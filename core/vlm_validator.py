"""
VLM (Vision-Language Model) Validator
======================================

Priority 3 MEDIUM feature from roadmap.

Visual-semantic validation using Vision-Language Models to verify
that generated diagrams match the textual description.

Supported VLMs:
- BLIP-2 (Salesforce)
- LLaVA (Microsoft)
- OpenFlamingo
- GPT-4 Vision (API)

Dependencies (to install):
- pip install transformers pillow
- pip install salesforce-lavis  # For BLIP-2
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import base64
import os
import tempfile


class VLMProvider(Enum):
    """Supported VLM providers"""
    BLIP2 = "blip2"
    LLAVA = "llava"
    GPT4_VISION = "gpt4v"
    STUB = "stub"  # For testing without actual model


@dataclass
class VLMConfig:
    """Configuration for VLM"""
    provider: VLMProvider
    model_name: str
    device: str = "cuda"  # or "cpu"
    api_key: Optional[str] = None


@dataclass
class VisualValidationResult:
    """Result of visual validation"""
    is_valid: bool
    confidence: float
    description: str  # VLM's description of the image
    discrepancies: List[str]  # Differences from expected
    suggestions: List[str]  # Improvement suggestions
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def issues(self) -> List[str]:
        """Backward-compatible alias for discrepancies"""
        return self.discrepancies

class VLMValidator:
    """
    Vision-Language Model validator

    Validates generated diagrams by:
    1. Generating description from image using VLM
    2. Comparing VLM description to original text
    3. Identifying discrepancies
    4. Suggesting improvements
    """

    def __init__(self, config: Optional[VLMConfig] = None):
        """
        Initialize VLM validator

        Args:
            config: VLM configuration (default: BLIP-2 local)
        """
        self.config = config or self._get_default_config()
        self.model = self._initialize_model()

        print(f"✅ VLM Validator initialized")
        print(f"   Provider: {self.config.provider.value}")
        print(f"   Model: {self.config.model_name}")

    def _get_default_config(self) -> VLMConfig:
        """Get default configuration (BLIP-2 local)"""
        return VLMConfig(
            provider=VLMProvider.BLIP2,
            model_name="Salesforce/blip2-opt-2.7b",
            device="cpu"  # Use CPU by default for compatibility
        )

    def _initialize_model(self):
        """Initialize VLM based on provider"""
        if self.config.provider == VLMProvider.BLIP2:
            return self._init_blip2()
        elif self.config.provider == VLMProvider.LLAVA:
            return self._init_llava()
        elif self.config.provider == VLMProvider.GPT4_VISION:
            return self._init_gpt4v()
        elif self.config.provider == VLMProvider.STUB:
            return None  # Stub mode
        else:
            raise ValueError(f"Unsupported VLM provider: {self.config.provider}")

    def _init_blip2(self):
        """Initialize BLIP-2 model"""
        try:
            from transformers import Blip2Processor, Blip2ForConditionalGeneration
            import torch

            print("   Loading BLIP-2 model (this may take a while)...")
            processor = Blip2Processor.from_pretrained(self.config.model_name)
            model = Blip2ForConditionalGeneration.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16 if self.config.device == "cuda" else torch.float32
            )
            model.to(self.config.device)
            print("   ✅ BLIP-2 loaded successfully")

            return {"processor": processor, "model": model}

        except ImportError:
            print("❌ BLIP-2 dependencies not installed")
            print("   Run: pip install transformers pillow torch")
            return None
        except Exception as e:
            print(f"⚠️  BLIP-2 initialization failed: {e}")
            return None

    def _init_llava(self):
        """Initialize LLaVA model"""
        try:
            # TODO: Implement LLaVA initialization
            print("⚠️  LLaVA not yet implemented")
            return None
        except Exception as e:
            print(f"⚠️  LLaVA initialization failed: {e}")
            return None

    def _init_gpt4v(self):
        """Initialize GPT-4 Vision API"""
        try:
            import openai
            if not self.config.api_key:
                print("❌ GPT-4 Vision requires API key")
                return None

            openai.api_key = self.config.api_key
            return openai

        except ImportError:
            print("❌ OpenAI not installed. Run: pip install openai")
            return None

    def validate_diagram(
        self,
        diagram_input: str,
        expected_description: str,
        scene_data: Optional[Dict] = None
    ) -> VisualValidationResult:
        """
        Validate diagram image against expected description

        Args:
            image_path: Path to generated SVG/PNG diagram
            expected_description: Original problem text
            scene_data: Optional scene metadata for context

        Returns:
            VisualValidationResult with validation details
        """
        svg_temp_path = None
        try:
            if diagram_input.strip().startswith("<svg"):
                svg_temp_path = self._write_temp_svg(diagram_input)
                image_path = svg_temp_path
            else:
                image_path = diagram_input

            print(f"\n🔍 Visual validation of: {Path(image_path).name}")

            # Convert SVG to PNG if needed
            image_path = self._ensure_png(image_path)

            # Generate description from image
            vlm_description = self._describe_image(image_path)
        finally:
            if svg_temp_path and os.path.exists(svg_temp_path):
                os.remove(svg_temp_path)

        if not vlm_description:
            return VisualValidationResult(
                is_valid=False,
                confidence=0.0,
                description="Failed to generate description",
                discrepancies=["VLM failed to process image"],
                suggestions=["Check image format and VLM configuration"]
            )

        # Compare descriptions
        is_valid, confidence, discrepancies = self._compare_descriptions(
            vlm_description,
            expected_description,
            scene_data
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(discrepancies, scene_data)

        return VisualValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            description=vlm_description,
            discrepancies=discrepancies,
            suggestions=suggestions
        )

    def _ensure_png(self, image_path: str) -> str:
        """Convert SVG to PNG if needed"""
        path = Path(image_path)

        if path.suffix.lower() == '.svg':
            # Convert SVG to PNG
            png_path = path.with_suffix('.png')

            try:
                from cairosvg import svg2png
                svg2png(url=str(path), write_to=str(png_path))
                print(f"   ✅ Converted SVG to PNG: {png_path.name}")
                return str(png_path)
            except ImportError:
                print("⚠️  cairosvg not installed. Install: pip install cairosvg")
                print("   Attempting to use SVG directly (may not work)")
                return image_path
            except Exception as e:
                print(f"⚠️  SVG conversion failed: {e}")
                return image_path

        return image_path

    def _write_temp_svg(self, svg_content: str) -> str:
        """Persist inline SVG content to a temporary file"""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
        tmp.write(svg_content.encode("utf-8"))
        tmp.flush()
        tmp.close()
        return tmp.name

    def _describe_image(self, image_path: str) -> Optional[str]:
        """Generate description of image using VLM"""

        if self.model is None:
            # Stub mode
            return self._stub_describe_image(image_path)

        if self.config.provider == VLMProvider.BLIP2:
            return self._describe_with_blip2(image_path)
        elif self.config.provider == VLMProvider.GPT4_VISION:
            return self._describe_with_gpt4v(image_path)
        else:
            return None

    def _describe_with_blip2(self, image_path: str) -> Optional[str]:
        """Describe image using BLIP-2"""
        try:
            from PIL import Image
            import torch

            # Load image
            image = Image.open(image_path).convert('RGB')

            # Prepare inputs
            prompt = "Describe this diagram in detail, including all components, connections, and labels:"
            inputs = self.model["processor"](image, text=prompt, return_tensors="pt").to(self.config.device)

            # Generate description
            with torch.no_grad():
                outputs = self.model["model"].generate(**inputs, max_length=200)

            description = self.model["processor"].decode(outputs[0], skip_special_tokens=True)

            print(f"   📝 VLM description: {description[:100]}...")
            return description

        except Exception as e:
            print(f"❌ BLIP-2 description failed: {e}")
            return None

    def _describe_with_gpt4v(self, image_path: str) -> Optional[str]:
        """Describe image using GPT-4 Vision"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Call GPT-4 Vision
            response = self.model.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this scientific diagram in detail, including all components, connections, values, and labels."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=300
            )

            description = response.choices[0].message.content
            print(f"   📝 VLM description: {description[:100]}...")
            return description

        except Exception as e:
            print(f"❌ GPT-4V description failed: {e}")
            return None

    def _stub_describe_image(self, image_path: str) -> str:
        """Stub description for testing"""
        return "A circuit diagram showing capacitors and a battery connected in series. The diagram includes labels and connection lines."

    def _compare_descriptions(
        self,
        vlm_desc: str,
        expected_desc: str,
        scene_data: Optional[Dict]
    ) -> Tuple[bool, float, List[str]]:
        """
        Compare VLM description with expected description

        Returns: (is_valid, confidence, discrepancies)
        """
        discrepancies = []

        # Extract key elements from expected description
        expected_elements = self._extract_key_elements(expected_desc)

        # Check if VLM description mentions key elements
        vlm_lower = vlm_desc.lower()
        missing_elements = []

        for element in expected_elements:
            if element.lower() not in vlm_lower:
                missing_elements.append(element)

        if missing_elements:
            discrepancies.append(f"Missing elements: {', '.join(missing_elements)}")

        # Calculate confidence based on element coverage
        coverage = 1.0 - (len(missing_elements) / max(len(expected_elements), 1))
        confidence = coverage

        # Determine validity (>70% coverage = valid)
        is_valid = confidence >= 0.7

        return is_valid, confidence, discrepancies

    def _extract_key_elements(self, text: str) -> List[str]:
        """Extract key diagram elements from text"""
        import re

        elements = []

        # Extract component types
        components = re.findall(r'\b(capacitor|resistor|battery|inductor|diode|transistor)\b', text, re.IGNORECASE)
        elements.extend(components)

        # Extract quantities with units
        quantities = re.findall(r'\d+\.?\d*\s*[μmkM]?[FVAΩHz]\b', text)
        elements.extend(quantities)

        # Extract connection types
        connections = re.findall(r'\b(series|parallel|connected)\b', text, re.IGNORECASE)
        elements.extend(connections)

        return list(set(elements))  # Remove duplicates

    def _generate_suggestions(self, discrepancies: List[str], scene_data: Optional[Dict]) -> List[str]:
        """Generate improvement suggestions based on discrepancies"""
        suggestions = []

        if "Missing elements" in str(discrepancies):
            suggestions.append("Add missing components to diagram")
            suggestions.append("Ensure all labels are visible and clear")

        if len(discrepancies) > 2:
            suggestions.append("Consider using more detailed representation")
            suggestions.append("Check component positioning and layout")

        return suggestions


class VLMValidatorStub(VLMValidator):
    """Stub VLM validator for testing without actual model"""

    def __init__(self):
        self.config = VLMConfig(provider=VLMProvider.STUB, model_name="stub")
        self.model = None
        print("✅ VLM Validator (STUB) initialized")

    def validate_diagram(self, image_path: str, expected_description: str, scene_data: Optional[Dict] = None) -> VisualValidationResult:
        """Stub validation always returns success"""
        return VisualValidationResult(
            is_valid=True,
            confidence=0.85,
            description="Stub validation - diagram appears correct",
            discrepancies=[],
            suggestions=[]
        )


if __name__ == "__main__":
    # Test VLM validator
    print("=" * 80)
    print("VLM VALIDATOR TEST")
    print("=" * 80)

    # Use stub for testing
    validator = VLMValidatorStub()

    # Test with dummy image
    test_image = "output/batch2_html_enhanced/q7_question_7.svg"
    test_desc = "A circuit with two capacitors in series"

    result = validator.validate_diagram(test_image, test_desc)

    print(f"\n📊 Validation Result:")
    print(f"   Valid: {result.is_valid}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Description: {result.description}")
    print(f"   Discrepancies: {result.discrepancies}")
    print(f"   Suggestions: {result.suggestions}")
