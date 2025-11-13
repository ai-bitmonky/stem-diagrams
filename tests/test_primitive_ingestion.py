from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

from core.primitive_ingestion import PrimitiveExtractor
from core.primitive_library import PrimitiveLibrary, PrimitiveCategory


def _build_test_image(tmp_path: Path) -> Path:
    image = Image.new("RGB", (80, 80), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([5, 5, 35, 35], outline="black", width=3)
    draw.line([45, 10, 75, 10], fill="black", width=3)
    draw.line([45, 20, 75, 20], fill="black", width=3)
    draw.line([45, 30, 75, 30], fill="black", width=3)
    image_path = tmp_path / "diagram.png"
    image.save(image_path)
    return image_path


def test_ingest_reference_diagram_populates_library(tmp_path):
    image_path = _build_test_image(tmp_path)

    with patch("core.primitive_library.PrimitiveLibrary._get_embedder", return_value=None):
        library = PrimitiveLibrary(backend="memory")
    initial_count = len(library.memory_store)

    extractor = PrimitiveExtractor(prefer_stub=True)
    summary = library.ingest_reference_diagram(
        str(image_path),
        category_hint=PrimitiveCategory.ELECTRONICS,
        tags=["test"],
        extractor=extractor,
    )

    assert summary["ingested"] >= 1
    assert len(library.memory_store) > initial_count
    assert summary["detections"], "detections should include at least one entry"
