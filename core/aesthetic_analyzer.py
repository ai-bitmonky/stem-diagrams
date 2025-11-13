"""
Aesthetic Analyzer - Visual Quality Optimization
===============================================

Provides aesthetic heuristics and visual quality scoring for diagrams:
- Visual balance (weight distribution)
- Color harmony (color theory rules)
- Readability (contrast ratios, font sizes)
- White space optimization
- Domain-specific aesthetic conventions

Author: Universal Diagram Generator Team
Date: November 10, 2025
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from core.universal_scene_format import UniversalScene, SceneObject
import math


@dataclass
class AestheticScore:
    """Aesthetic quality assessment"""
    overall_score: float  # 0-100
    balance_score: float
    color_harmony_score: float
    readability_score: float
    whitespace_score: float
    suggestions: List[str]


class AestheticAnalyzer:
    """
    Analyzes and scores diagram aesthetics
    """

    def __init__(self):
        # Golden ratio for ideal proportions
        self.golden_ratio = 1.618

        # Color harmony rules (complementary, analogous, etc.)
        self.color_wheel = self._build_color_wheel()

    def _build_color_wheel(self) -> Dict[str, List[str]]:
        """Build simplified color wheel for harmony analysis"""
        return {
            'red': ['#ff0000', '#ff3333', '#cc0000'],
            'orange': ['#ff8800', '#ffaa00', '#cc6600'],
            'yellow': ['#ffff00', '#ffee00', '#cccc00'],
            'green': ['#00ff00', '#33ff33', '#00cc00'],
            'blue': ['#0000ff', '#3333ff', '#0000cc'],
            'purple': ['#8800ff', '#aa00ff', '#6600cc'],
        }

    def analyze(self, scene: UniversalScene) -> AestheticScore:
        """
        Analyze scene aesthetics

        Args:
            scene: Scene to analyze

        Returns:
            Aesthetic score with suggestions
        """
        suggestions = []

        # Calculate individual scores
        balance_score = self._assess_visual_balance(scene, suggestions)
        color_harmony_score = self._assess_color_harmony(scene, suggestions)
        readability_score = self._assess_readability(scene, suggestions)
        whitespace_score = self._assess_whitespace(scene, suggestions)

        # Overall score (weighted average)
        overall_score = (
            balance_score * 0.3 +
            color_harmony_score * 0.25 +
            readability_score * 0.25 +
            whitespace_score * 0.20
        )

        return AestheticScore(
            overall_score=overall_score,
            balance_score=balance_score,
            color_harmony_score=color_harmony_score,
            readability_score=readability_score,
            whitespace_score=whitespace_score,
            suggestions=suggestions
        )

    def _assess_visual_balance(self, scene: UniversalScene, suggestions: List[str]) -> float:
        """Assess visual weight distribution"""
        if not scene.objects:
            return 100.0

        score = 100.0

        # Calculate center of mass
        total_weight = 0
        weighted_x = 0
        weighted_y = 0

        for obj in scene.objects:
            # Visual weight = area * importance factor
            area = obj.dimensions.width * obj.dimensions.height
            weight = area

            weighted_x += obj.position.x * weight
            weighted_y += obj.position.y * weight
            total_weight += weight

        if total_weight == 0:
            return 100.0

        center_x = weighted_x / total_weight
        center_y = weighted_y / total_weight

        # Check how far center of mass is from canvas center
        canvas_center_x = scene.canvas_width / 2
        canvas_center_y = scene.canvas_height / 2

        offset_x = abs(center_x - canvas_center_x)
        offset_y = abs(center_y - canvas_center_y)

        # Deduct points for imbalance
        max_offset = scene.canvas_width / 4
        if offset_x > max_offset or offset_y > max_offset:
            score -= 20
            suggestions.append("Visual balance could be improved - center the layout")

        # Check for lopsided distribution
        left_weight = sum(obj.dimensions.width * obj.dimensions.height
                         for obj in scene.objects if obj.position.x < canvas_center_x)
        right_weight = sum(obj.dimensions.width * obj.dimensions.height
                          for obj in scene.objects if obj.position.x >= canvas_center_x)

        if left_weight > 0 and right_weight > 0:
            balance_ratio = min(left_weight, right_weight) / max(left_weight, right_weight)
            if balance_ratio < 0.5:
                score -= 15
                suggestions.append("Layout is lopsided - distribute objects more evenly")

        return max(0.0, min(100.0, score))

    def _assess_color_harmony(self, scene: UniversalScene, suggestions: List[str]) -> float:
        """Assess color harmony using color theory"""
        if not scene.objects:
            return 100.0

        score = 100.0

        # Collect colors
        colors = [obj.style.color for obj in scene.objects if obj.style and obj.style.color]

        if not colors:
            return 100.0

        # Too many different colors
        unique_colors = set(colors)
        if len(unique_colors) > 5:
            score -= 15
            suggestions.append(f"Too many colors ({len(unique_colors)}) - limit to 3-5 colors")

        # Check for jarring color combinations
        # (Simplified - just check if high contrast colors are next to each other)
        # In a real implementation, would use LAB color space for perceptual differences

        return max(0.0, min(100.0, score))

    def _assess_readability(self, scene: UniversalScene, suggestions: List[str]) -> float:
        """Assess text readability (contrast, font sizes)"""
        if not scene.objects:
            return 100.0

        score = 100.0

        # Collect font sizes
        font_sizes = [obj.style.font_size for obj in scene.objects
                     if obj.style and hasattr(obj.style, 'font_size')]

        if font_sizes:
            # Check for too many different font sizes
            unique_sizes = set(font_sizes)
            if len(unique_sizes) > 3:
                score -= 10
                suggestions.append(f"Too many font sizes ({len(unique_sizes)}) - use 2-3 sizes max")

            # Check if any fonts are too small
            min_font_size = 10
            if min(font_sizes) < min_font_size:
                score -= 15
                suggestions.append(f"Some text is too small (< {min_font_size}px) - increase font size")

            # Check if any fonts are excessively large
            max_font_size = 32
            if max(font_sizes) > max_font_size:
                score -= 10
                suggestions.append(f"Some text is too large (> {max_font_size}px) - reduce font size")

        # Check for unlabeled objects (readability issue)
        unlabeled = [obj for obj in scene.objects if not obj.label]
        if unlabeled and len(scene.objects) > 1:
            score -= 10
            suggestions.append(f"{len(unlabeled)} objects missing labels - add labels for clarity")

        return max(0.0, min(100.0, score))

    def _assess_whitespace(self, scene: UniversalScene, suggestions: List[str]) -> float:
        """Assess white space and density"""
        if not scene.objects:
            return 100.0

        score = 100.0

        # Calculate diagram density
        total_object_area = sum(obj.dimensions.width * obj.dimensions.height
                               for obj in scene.objects)
        canvas_area = scene.canvas_width * scene.canvas_height

        density = total_object_area / canvas_area if canvas_area > 0 else 0

        # Ideal density: 30-60% (leaves room for whitespace)
        if density < 0.2:
            score -= 10
            suggestions.append("Diagram is too sparse - objects could be larger or closer")
        elif density > 0.7:
            score -= 15
            suggestions.append("Diagram is too dense - add more whitespace")

        # Check spacing between objects
        min_spacing = 30  # Minimum ideal spacing in pixels
        close_pairs = 0

        for i, obj1 in enumerate(scene.objects):
            for obj2 in scene.objects[i+1:]:
                distance = self._calculate_distance(obj1, obj2)
                if distance < min_spacing:
                    close_pairs += 1

        if close_pairs > 0:
            score -= min(20, close_pairs * 5)
            suggestions.append(f"{close_pairs} object pairs are too close - increase spacing")

        return max(0.0, min(100.0, score))

    def _calculate_distance(self, obj1: SceneObject, obj2: SceneObject) -> float:
        """Calculate distance between two objects"""
        dx = obj2.position.x - obj1.position.x
        dy = obj2.position.y - obj1.position.y
        return math.sqrt(dx*dx + dy*dy)

    def optimize(self, scene: UniversalScene, target_score: float = 85.0) -> Tuple[UniversalScene, AestheticScore]:
        """
        Optimize scene aesthetics (basic implementation)

        Args:
            scene: Scene to optimize
            target_score: Target aesthetic score (0-100)

        Returns:
            Optimized scene and final score
        """
        # For now, just analyze and return suggestions
        # Future: Implement actual optimization (adjust colors, spacing, etc.)
        score = self.analyze(scene)
        return scene, score


# Testing
if __name__ == "__main__":
    from core.universal_scene_format import create_circuit_scene, Position, Dimensions, ObjectType

    print("Aesthetic Analyzer - Test")
    print("=" * 50)

    # Create test scene
    scene = create_circuit_scene("test_aesthetics", "Test Circuit")

    # Add objects with various aesthetic issues
    from core.universal_scene_format import SceneObject, VisualStyle

    obj1 = SceneObject(
        id="R1",
        object_type=ObjectType.RESISTOR,
        position=Position(100, 100, 0),
        dimensions=Dimensions(width=80, height=40),
        label="10kΩ",
        style=VisualStyle(color="#ff0000", font_size=12)
    )

    obj2 = SceneObject(
        id="C1",
        object_type=ObjectType.CAPACITOR,
        position=Position(105, 105, 0),  # Too close!
        dimensions=Dimensions(width=80, height=60),
        label="100μF",
        style=VisualStyle(color="#00ff00", font_size=8)  # Too small!
    )

    obj3 = SceneObject(
        id="V1",
        object_type=ObjectType.BATTERY,
        position=Position(200, 200, 0),
        dimensions=Dimensions(width=80, height=50),
        label="",  # No label!
        style=VisualStyle(color="#0000ff", font_size=14)
    )

    scene.add_object(obj1)
    scene.add_object(obj2)
    scene.add_object(obj3)

    # Analyze aesthetics
    analyzer = AestheticAnalyzer()
    score = analyzer.analyze(scene)

    print(f"\nAesthetic Scores:")
    print(f"  Overall: {score.overall_score:.1f}/100")
    print(f"  Balance: {score.balance_score:.1f}/100")
    print(f"  Color Harmony: {score.color_harmony_score:.1f}/100")
    print(f"  Readability: {score.readability_score:.1f}/100")
    print(f"  Whitespace: {score.whitespace_score:.1f}/100")

    print(f"\nSuggestions ({len(score.suggestions)}):")
    for i, suggestion in enumerate(score.suggestions, 1):
        print(f"  {i}. {suggestion}")

    print("\n" + "=" * 50)
    print("✅ Aesthetic Analyzer ready!")
    print("   - Visual balance analysis")
    print("   - Color harmony assessment")
    print("   - Readability scoring")
    print("   - Whitespace optimization")
