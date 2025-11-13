"""
Multimodal Primitive Extraction
-------------------------------

This module wires up DETR (object detection), SAM (segmentation), Donut (OCR-free
scene description), and TrOCR (text extraction) to ingest reference diagrams and
hydrate the primitive library automatically.

The heavy ML dependencies are optional. When a model is missing, the extractor
falls back to lightweight heuristics so that tests and offline environments still
function. When the dependencies are installed, the same workflow seamlessly
switches to the full multimodal stack.
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    TRANSFORMERS_AVAILABLE = False
    pipeline = None  # type: ignore

try:
    from segment_anything import SamPredictor, sam_model_registry

    SAM_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SAM_AVAILABLE = False
    SamPredictor = None  # type: ignore
    sam_model_registry = {}  # type: ignore


CategoryStr = str


@dataclass
class PrimitiveExtractionResult:
    """Lightweight payload describing an extracted primitive."""

    primitive_id: str
    name: str
    category: CategoryStr
    svg_content: str
    tags: List[str]
    metadata: Dict[str, Any]
    bbox: Tuple[int, int, int, int]
    confidence: float = 0.0


class PrimitiveExtractor:
    """
    Multimodal primitive extractor orchestrating DETR, SAM, Donut, and TrOCR.

    The extractor gracefully degrades to heuristic detections whenever a model
    is unavailable or the environment lacks GPU resources.
    """

    DETR_MODEL_ID = "facebook/detr-resnet-50"
    DONUT_MODEL_ID = "naver-clova-ix/donut-base-finetuned-cord-v2"
    TROCR_MODEL_ID = "microsoft/trocr-base-printed"

    CATEGORY_KEYWORDS: Dict[str, Sequence[str]] = {
        "electronics": ["battery", "resistor", "capacitor", "wire", "switch", "diode", "inductor"],
        "mechanics": ["mass", "block", "pulley", "force", "spring", "lever"],
        "chemistry": ["atom", "bond", "molecule", "reaction"],
        "biology": ["cell", "dna", "protein", "organ"],
        "geometry": ["triangle", "circle", "polygon", "angle"],
        "computer_science": ["server", "database", "node", "network", "cloud"],
        "math": ["graph", "function", "axis", "vector"],
    }

    def __init__(
        self,
        *,
        enable_detr: bool = True,
        enable_sam: bool = True,
        enable_donut: bool = True,
        enable_trocr: bool = True,
        prefer_stub: bool = False,
        detection_threshold: float = 0.4,
        max_regions: int = 12,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.prefer_stub = prefer_stub
        self.detection_threshold = detection_threshold
        self.max_regions = max_regions
        self.warnings: List[str] = []

        # Lazy-loaded models
        self._detr_pipeline = None
        self._donut_pipeline = None
        self._trocr_pipeline = None
        self._sam_predictor: Optional[SamPredictor] = None  # type: ignore[assignment]
        self._sam_image_signature: Optional[Tuple[int, int, int]] = None

        if enable_detr and not prefer_stub:
            self._detr_pipeline = self._init_detr()
        if enable_donut and not prefer_stub:
            self._donut_pipeline = self._init_donut()
        if enable_trocr and not prefer_stub:
            self._trocr_pipeline = self._init_trocr()
        if enable_sam and not prefer_stub:
            self._sam_predictor = self._init_sam()

    # ------------------------------------------------------------------ public API
    def extract_from_image(
        self,
        image_path: str,
        *,
        category_hint: Optional[str] = None,
        extra_tags: Optional[Sequence[str]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[PrimitiveExtractionResult]:
        """
        Extract primitives from a reference diagram.

        Args:
            image_path: Path to an input diagram (PNG/SVG converted to raster).
            category_hint: Optional category bias (e.g., "electronics").
            extra_tags: Additional tags to add to each primitive.
            extra_metadata: Metadata merged into each primitive payload.
        """
        image_file = Path(image_path)
        if not image_file.exists():
            raise FileNotFoundError(f"Diagram not found: {image_path}")

        image = Image.open(image_file).convert("RGB")
        image_bytes = image_file.read_bytes()
        image_hash = hashlib.sha1(image_bytes).hexdigest()

        diagram_caption = self._describe_with_donut(image)
        detections = self._detect_objects(image)
        if not detections:
            detections = self._fallback_detect(image)

        results: List[PrimitiveExtractionResult] = []
        for idx, det in enumerate(detections[: self.max_regions]):
            bbox = self._sanitize_bbox(det["bbox"], image.size)
            if bbox is None:
                continue

            crop = image.crop(bbox)
            ocr_text = self._extract_text_with_trocr(crop)
            region_caption = self._describe_with_donut(crop) or diagram_caption
            mask_bbox = self._segment_region(image, bbox, image_hash)

            primitive_id = f"vision_{image_hash[:8]}_{idx:03d}"
            name = ocr_text or region_caption or det["label"] or f"primitive_{idx}"
            category = self._infer_category(det["label"], category_hint)

            tags = self._build_tags(det["label"], ocr_text, region_caption, extra_tags)
            svg_content = self._encode_crop_as_svg(crop)

            metadata = {
                "source": "multimodal_ingestion",
                "label": det["label"],
                "confidence": det.get("score"),
                "bbox": bbox,
                "mask_bbox": mask_bbox,
                "ocr_text": ocr_text,
                "donut_summary": region_caption,
                "image_hash": image_hash,
            }
            if extra_metadata:
                metadata.update(extra_metadata)

            primitive_payload = PrimitiveExtractionResult(
                primitive_id=primitive_id,
                name=name.strip() if isinstance(name, str) else name,
                category=category,
                svg_content=svg_content,
                tags=tags,
                metadata=metadata,
                bbox=bbox,
                confidence=det.get("score", 0.0),
            )
            results.append(primitive_payload)

        return results

    # ------------------------------------------------------------------ model loaders
    def _init_detr(self):
        if not TRANSFORMERS_AVAILABLE:
            self._warn_once("transformers not installed – DETR disabled")
            return None
        try:
            return pipeline("object-detection", model=self.DETR_MODEL_ID)
        except Exception as exc:  # pragma: no cover - requires external model
            self._warn_once(f"Failed to load DETR: {exc}")
            return None

    def _init_donut(self):
        if not TRANSFORMERS_AVAILABLE:
            return None
        try:
            return pipeline("image-to-text", model=self.DONUT_MODEL_ID)
        except Exception as exc:  # pragma: no cover
            self._warn_once(f"Failed to load Donut model: {exc}")
            return None

    def _init_trocr(self):
        if not TRANSFORMERS_AVAILABLE:
            return None
        try:
            return pipeline("image-to-text", model=self.TROCR_MODEL_ID)
        except Exception as exc:  # pragma: no cover
            self._warn_once(f"Failed to load TrOCR model: {exc}")
            return None

    def _init_sam(self):
        if not SAM_AVAILABLE:
            self._warn_once("segment-anything not installed – SAM disabled")
            return None
        checkpoint = os.environ.get("SAM_CHECKPOINT_PATH")
        model_type = os.environ.get("SAM_MODEL_TYPE", "vit_b")
        if not checkpoint or not Path(checkpoint).exists():
            self._warn_once("SAM checkpoint missing – set SAM_CHECKPOINT_PATH to enable segmentation")
            return None
        try:  # pragma: no cover - depends on optional weights
            sam_model = sam_model_registry[model_type](checkpoint=checkpoint)
            return SamPredictor(sam_model)
        except Exception as exc:
            self._warn_once(f"Failed to initialize SAM ({exc})")
            return None

    # ------------------------------------------------------------------ helpers
    def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        if self._detr_pipeline is None:
            return []
        try:
            raw = self._detr_pipeline(image)
        except Exception as exc:  # pragma: no cover - external inference
            self._warn_once(f"DETR inference failed: {exc}")
            return []

        detections: List[Dict[str, Any]] = []
        for item in raw:
            score = float(item.get("score", 0.0))
            if score < self.detection_threshold:
                continue
            box = item.get("box", {})
            bbox = (
                int(box.get("xmin", 0)),
                int(box.get("ymin", 0)),
                int(box.get("xmax", 0)),
                int(box.get("ymax", 0)),
            )
            detections.append({"label": item.get("label", "component"), "score": score, "bbox": bbox})
        return detections

    def _fallback_detect(self, image: Image.Image) -> List[Dict[str, Any]]:
        width, height = image.size
        # Simple heuristic: return the whole canvas and a 2x2 grid if the image is large enough
        detections = [
            {"label": "diagram_component", "score": 0.5, "bbox": (0, 0, width, height)}
        ]
        if width >= 64 and height >= 64:
            half_w, half_h = width // 2, height // 2
            steps = [
                (0, 0, half_w, half_h),
                (half_w, 0, width, half_h),
                (0, half_h, half_w, height),
                (half_w, half_h, width, height),
            ]
            for bbox in steps:
                detections.append({"label": "diagram_component", "score": 0.35, "bbox": bbox})
        return detections

    def _segment_region(
        self,
        image: Image.Image,
        bbox: Tuple[int, int, int, int],
        image_hash: str,
    ) -> Optional[Tuple[int, int, int, int]]:
        if self._sam_predictor is None:
            return None
        try:  # pragma: no cover - requires optional dependency
            np_image = np.asarray(image)
            signature = np_image.shape
            if self._sam_image_signature != signature:
                self._sam_predictor.set_image(np_image)
                self._sam_image_signature = signature

            box_arr = np.array([[bbox[0], bbox[1], bbox[2], bbox[3]]], dtype=np.float32)
            masks, _, _ = self._sam_predictor.predict(
                point_coords=None,
                point_labels=None,
                box=box_arr,
                multimask_output=False,
            )
            if masks is None or len(masks) == 0:
                return None
            mask = masks[0]
            ys, xs = np.where(mask)
            if ys.size == 0 or xs.size == 0:
                return None
            return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        except Exception as exc:
            self.logger.debug("SAM segmentation skipped for %s: %s", image_hash, exc)
            return None

    def _extract_text_with_trocr(self, image: Image.Image) -> Optional[str]:
        if self._trocr_pipeline is None:
            return None
        try:  # pragma: no cover - heavy inference
            result = self._trocr_pipeline(image)
            if result and "generated_text" in result[0]:
                return result[0]["generated_text"].strip()
        except Exception as exc:
            self.logger.debug("TrOCR failed: %s", exc)
        return None

    def _describe_with_donut(self, image: Image.Image) -> Optional[str]:
        if self._donut_pipeline is None:
            return None
        try:  # pragma: no cover - heavy inference
            result = self._donut_pipeline(image)
            if result:
                text = result[0].get("generated_text") or result[0].get("text")
                if text:
                    return text.strip()
        except Exception as exc:
            self.logger.debug("Donut captioning failed: %s", exc)
        return None

    def _encode_crop_as_svg(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        width, height = image.size
        return (
            f'<image width="{width}" height="{height}" '
            f'href="data:image/png;base64,{encoded}" preserveAspectRatio="none" />'
        )

    def _infer_category(self, label: Optional[str], category_hint: Optional[str]) -> str:
        if category_hint:
            return category_hint.lower()
        label = (label or "").lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in label for keyword in keywords):
                return category
        return "geometry"

    def _build_tags(
        self,
        label: Optional[str],
        ocr_text: Optional[str],
        caption: Optional[str],
        extra_tags: Optional[Sequence[str]],
    ) -> List[str]:
        tags: List[str] = []
        if label:
            tags.append(label.lower())
        if ocr_text:
            tags.extend(word.lower() for word in ocr_text.split())
        if caption:
            tags.extend(word.lower() for word in caption.split()[:6])
        if extra_tags:
            tags.extend(tag.lower() for tag in extra_tags if tag)
        # Deduplicate while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                unique_tags.append(tag)
                seen.add(tag)
        return unique_tags

    def _sanitize_bbox(
        self,
        bbox: Tuple[int, int, int, int],
        image_size: Tuple[int, int],
    ) -> Optional[Tuple[int, int, int, int]]:
        x_min, y_min, x_max, y_max = bbox
        width, height = image_size
        x_min = max(0, min(width, x_min))
        y_min = max(0, min(height, y_min))
        x_max = max(0, min(width, x_max))
        y_max = max(0, min(height, y_max))
        if x_max - x_min <= 0 or y_max - y_min <= 0:
            return None
        return (x_min, y_min, x_max, y_max)

    def _warn_once(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)
            self.logger.warning(message)


__all__ = ["PrimitiveExtractor", "PrimitiveExtractionResult"]
