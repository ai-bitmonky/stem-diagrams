"""
Intelligent Label Placement
============================

Automatic label placement with overlap avoidance.

Places labels near their associated objects while avoiding:
- Other labels
- Geometric shapes
- Canvas edges

Author: STEM-AI Pipeline Team
Date: November 11, 2025
"""

from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
import math
from core.scene.schema_v1 import Scene, SceneObject, PrimitiveType, Position, RenderLayer


@dataclass
class LabelPlacementCandidate:
    """Candidate position for label placement"""
    position: Dict[str, float]
    score: float
    direction: str  # "above", "below", "left", "right", etc.


class IntelligentLabelPlacer:
    """
    Automatic label placement with overlap avoidance

    Places labels near their associated objects while avoiding collisions.

    Usage:
        placer = IntelligentLabelPlacer()
        scene_with_labels = placer.place_labels(scene)
    """

    def __init__(self, canvas_width: int = 1200, canvas_height: int = 800, margin: int = 20):
        """
        Initialize label placer

        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            margin: Safety margin from canvas edges
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.margin = margin

        # Preferred directions (higher score = more preferred)
        self.direction_preferences = {
            "above": 10,
            "right": 8,
            "above_right": 6,
            "below": 4,
            "left": 3,
            "below_right": 2,
            "above_left": 1,
            "below_left": 0
        }

    def place_labels(self, scene: Scene) -> Scene:
        """
        Place all labels intelligently

        Args:
            scene: Scene with positioned shapes and unpositioned/poorly-positioned labels

        Returns:
            Scene with optimally positioned labels
        """
        # Separate labels from shapes
        shapes = [obj for obj in scene.objects if obj.type != PrimitiveType.TEXT]
        labels = [obj for obj in scene.objects if obj.type == PrimitiveType.TEXT]

        print(f"  📍 IntelligentLabelPlacer: Positioning {len(labels)} labels")

        # Process each label
        placed_labels = []
        for label in labels:
            # Get target object (if specified)
            target_obj_id = label.properties.get("target_object")
            target_obj = None

            if target_obj_id:
                target_obj = next((obj for obj in shapes if obj.id == target_obj_id), None)

            if target_obj and target_obj.position:
                # Find best position near target
                best_pos = self._find_best_label_position(
                    label, target_obj, shapes, placed_labels
                )
                label.position = best_pos
                print(f"     ✓ Placed '{label.id}' near '{target_obj.id}'")
            elif label.position is None:
                # No target specified and no position - place in safe area
                label.position = self._get_safe_default_position(label, shapes, placed_labels)
                print(f"     ⚠️  Placed '{label.id}' in default position (no target specified)")

            placed_labels.append(label)

        return scene

    def _find_best_label_position(
        self,
        label: SceneObject,
        target: SceneObject,
        shapes: List[SceneObject],
        other_labels: List[SceneObject]
    ) -> Dict[str, float]:
        """
        Find best position for label near target object

        Args:
            label: Label to place
            target: Target object to place label near
            shapes: All shape objects to avoid
            other_labels: Already-placed labels to avoid

        Returns:
            Position dictionary with x, y, anchor
        """
        # Get target bounds
        target_bounds = self._get_bounds(target)
        if target_bounds is None:
            return {"x": target.position["x"], "y": target.position["y"], "anchor": "center"}

        tx1, ty1, tx2, ty2 = target_bounds
        target_center_x = (tx1 + tx2) / 2
        target_center_y = (ty1 + ty2) / 2
        target_width = tx2 - tx1
        target_height = ty2 - ty1

        # Get label dimensions
        label_width, label_height = self._estimate_label_size(label)

        # Define offset distance from target
        offset = 15

        # Generate candidate positions
        candidates = [
            # Above
            LabelPlacementCandidate(
                position={"x": target_center_x, "y": ty1 - offset, "anchor": "bottom"},
                score=100.0,
                direction="above"
            ),
            # Below
            LabelPlacementCandidate(
                position={"x": target_center_x, "y": ty2 + offset, "anchor": "top"},
                score=100.0,
                direction="below"
            ),
            # Right
            LabelPlacementCandidate(
                position={"x": tx2 + offset, "y": target_center_y, "anchor": "left"},
                score=100.0,
                direction="right"
            ),
            # Left
            LabelPlacementCandidate(
                position={"x": tx1 - offset, "y": target_center_y, "anchor": "right"},
                score=100.0,
                direction="left"
            ),
            # Above-right (diagonal)
            LabelPlacementCandidate(
                position={"x": tx2 + offset, "y": ty1 - offset, "anchor": "bottom-left"},
                score=100.0,
                direction="above_right"
            ),
            # Above-left
            LabelPlacementCandidate(
                position={"x": tx1 - offset, "y": ty1 - offset, "anchor": "bottom-right"},
                score=100.0,
                direction="above_left"
            ),
            # Below-right
            LabelPlacementCandidate(
                position={"x": tx2 + offset, "y": ty2 + offset, "anchor": "top-left"},
                score=100.0,
                direction="below_right"
            ),
            # Below-left
            LabelPlacementCandidate(
                position={"x": tx1 - offset, "y": ty2 + offset, "anchor": "top-right"},
                score=100.0,
                direction="below_left"
            ),
        ]

        # Score each candidate
        best_candidate = None
        best_score = -float('inf')

        for candidate in candidates:
            score = self._score_label_position(
                label, candidate.position, label_width, label_height,
                shapes, other_labels, target
            )

            # Add direction preference
            score += self.direction_preferences.get(candidate.direction, 0)

            if score > best_score:
                best_score = score
                best_candidate = candidate

        if best_candidate:
            return best_candidate.position
        else:
            # Fallback: just above target
            return {"x": target_center_x, "y": ty1 - offset, "anchor": "bottom"}

    def _score_label_position(
        self,
        label: SceneObject,
        position: Dict[str, float],
        label_width: float,
        label_height: float,
        shapes: List[SceneObject],
        other_labels: List[SceneObject],
        target: SceneObject
    ) -> float:
        """
        Score a label position (higher is better)

        Args:
            label: Label being placed
            position: Candidate position
            label_width: Estimated label width
            label_height: Estimated label height
            shapes: All shapes to avoid
            other_labels: Already-placed labels to avoid
            target: Target object

        Returns:
            Score (higher = better)
        """
        score = 100.0

        # Create temporary label bounds for this position
        label_bounds = self._get_label_bounds_at_position(
            position, label_width, label_height
        )

        # Penalty for overlapping shapes (except target)
        for shape in shapes:
            if shape.id == target.id:
                continue  # Allow overlap with target object

            shape_bounds = self._get_bounds(shape)
            if shape_bounds and self._bounds_overlap(label_bounds, shape_bounds):
                score -= 50  # Major penalty

        # Penalty for overlapping other labels
        for other_label in other_labels:
            if other_label.id == label.id or not other_label.position:
                continue

            other_label_w, other_label_h = self._estimate_label_size(other_label)
            other_bounds = self._get_label_bounds_at_position(
                other_label.position, other_label_w, other_label_h
            )

            if self._bounds_overlap(label_bounds, other_bounds):
                score -= 30  # Significant penalty

        # Penalty for being near canvas edge
        if self._near_edge(label_bounds):
            score -= 20

        # Small bonus for being close to target (not too far)
        distance_to_target = self._distance_to_target(position, target)
        if distance_to_target < 50:
            score += 5

        return score

    def _get_bounds(self, obj: SceneObject) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding box (x1, y1, x2, y2) for an object"""
        if obj.position is None:
            return None

        pos = obj.position
        x = pos.get("x", 0)
        y = pos.get("y", 0)

        if obj.type in [PrimitiveType.RECTANGLE, PrimitiveType.CAPACITOR_PLATE]:
            width = obj.properties.get("width", 0)
            height = obj.properties.get("height", 0)

            anchor = pos.get("anchor", "top-left")
            if anchor == "top-left":
                return (x, y, x + width, y + height)
            elif anchor == "center":
                return (x - width/2, y - height/2, x + width/2, y + height/2)
            elif anchor == "bottom-left":
                return (x, y - height, x + width, y)
            else:
                return (x, y, x + width, y + height)

        elif obj.type == PrimitiveType.CIRCLE:
            radius = obj.properties.get("radius", 0)
            return (x - radius, y - radius, x + radius, y + radius)

        return None

    def _estimate_label_size(self, label: SceneObject) -> Tuple[float, float]:
        """Estimate label dimensions"""
        font_size = label.properties.get("font_size", 14)
        text = label.properties.get("text", "")

        # Rough approximation: 0.6 * font_size per character
        width = len(text) * font_size * 0.6
        height = font_size * 1.2

        return (width, height)

    def _get_label_bounds_at_position(
        self,
        position: Dict[str, float],
        width: float,
        height: float
    ) -> Tuple[float, float, float, float]:
        """Get label bounds at given position"""
        x = position["x"]
        y = position["y"]
        anchor = position.get("anchor", "center")

        if anchor == "top-left" or anchor == "left":
            return (x, y, x + width, y + height)
        elif anchor == "bottom-left":
            return (x, y - height, x + width, y)
        elif anchor == "top-right" or anchor == "right":
            return (x - width, y, x, y + height)
        elif anchor == "bottom-right":
            return (x - width, y - height, x, y)
        elif anchor == "top":
            return (x - width/2, y, x + width/2, y + height)
        elif anchor == "bottom":
            return (x - width/2, y - height, x + width/2, y)
        else:  # center
            return (x - width/2, y - height/2, x + width/2, y + height/2)

    def _bounds_overlap(
        self,
        bounds1: Tuple[float, float, float, float],
        bounds2: Tuple[float, float, float, float]
    ) -> bool:
        """Check if two bounding boxes overlap"""
        x1_1, y1_1, x2_1, y2_1 = bounds1
        x1_2, y1_2, x2_2, y2_2 = bounds2

        return not (x2_1 < x1_2 or x1_1 > x2_2 or y2_1 < y1_2 or y1_1 > y2_2)

    def _near_edge(self, bounds: Tuple[float, float, float, float]) -> bool:
        """Check if bounds are near canvas edge"""
        x1, y1, x2, y2 = bounds

        return (x1 < self.margin or
                x2 > self.canvas_width - self.margin or
                y1 < self.margin or
                y2 > self.canvas_height - self.margin)

    def _distance_to_target(self, position: Dict[str, float], target: SceneObject) -> float:
        """Calculate distance from position to target center"""
        if target.position is None:
            return float('inf')

        target_x = target.position.get("x", 0)
        target_y = target.position.get("y", 0)
        label_x = position["x"]
        label_y = position["y"]

        return math.sqrt((label_x - target_x)**2 + (label_y - target_y)**2)

    def _get_safe_default_position(
        self,
        label: SceneObject,
        shapes: List[SceneObject],
        other_labels: List[SceneObject]
    ) -> Dict[str, float]:
        """Get safe default position for label without target"""
        # Try to place in top-right corner
        label_w, label_h = self._estimate_label_size(label)

        candidates = [
            {"x": self.canvas_width - 100, "y": 50, "anchor": "top-right"},
            {"x": 100, "y": 50, "anchor": "top-left"},
            {"x": self.canvas_width - 100, "y": self.canvas_height - 50, "anchor": "bottom-right"},
            {"x": 100, "y": self.canvas_height - 50, "anchor": "bottom-left"},
        ]

        best_pos = candidates[0]
        best_score = -float('inf')

        for pos in candidates:
            score = self._score_label_position(
                label, pos, label_w, label_h,
                shapes, other_labels, SceneObject("dummy", PrimitiveType.TEXT, position=pos)
            )
            if score > best_score:
                best_score = score
                best_pos = pos

        return best_pos


# Example usage
if __name__ == '__main__':
    print("="*80)
    print("Intelligent Label Placer Test")
    print("="*80)

    from core.scene.schema_v1 import Scene, SceneObject, PrimitiveType, RenderLayer

    # Create test scene
    scene = Scene()

    # Add a shape
    scene.objects.append(SceneObject(
        id="rect1",
        type=PrimitiveType.RECTANGLE,
        position={"x": 400, "y": 300, "anchor": "center"},
        properties={"width": 200, "height": 100},
        layer=RenderLayer.SHAPES
    ))

    # Add label for rect1 (without position)
    scene.objects.append(SceneObject(
        id="label1",
        type=PrimitiveType.TEXT,
        position=None,  # Will be placed automatically
        properties={"text": "κ₁ = 21.0", "font_size": 18, "target_object": "rect1"},
        layer=RenderLayer.LABELS
    ))

    # Place labels
    placer = IntelligentLabelPlacer()
    scene = placer.place_labels(scene)

    # Check result
    label = next(obj for obj in scene.objects if obj.id == "label1")
    if label.position:
        print(f"\n✅ Label placed at: x={label.position['x']:.1f}, y={label.position['y']:.1f}, anchor={label.position.get('anchor', 'center')}")
    else:
        print("\n❌ Label placement failed")

    print(f"\n{'='*80}")
    print("✅ Label placer test complete")
    print("="*80)
