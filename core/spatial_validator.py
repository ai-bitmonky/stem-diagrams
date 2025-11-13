"""
Spatial Validation Layer
========================

Validates spatial properties of positioned scenes BEFORE rendering.

Catches errors early:
- Unintended overlaps between objects
- Labels overlapping shapes
- Elements outside canvas bounds
- Incorrect z-ordering

Author: STEM-AI Pipeline Team
Date: November 11, 2025
"""

from typing import List, Optional, Tuple, Set
from dataclasses import dataclass, field
from core.scene.schema_v1 import Scene, SceneObject, PrimitiveType, RenderLayer, Position, ConstraintType


@dataclass
class Overlap:
    """Represents an overlap between two objects"""
    obj1_id: str
    obj2_id: str
    is_intentional: bool = False
    overlap_area: float = 0.0


@dataclass
class LabelIssue:
    """Represents a label placement issue"""
    label_id: str
    issue_type: str  # "overlaps_shape", "overlaps_label", "out_of_bounds"
    overlapping_with: Optional[str] = None


@dataclass
class SpatialValidationReport:
    """Results of spatial validation"""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    overlaps: List[Overlap] = field(default_factory=list)
    label_issues: List[LabelIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0

    def is_valid(self) -> bool:
        """Check if validation passed (no errors)"""
        return not self.has_errors()

    def summary(self) -> str:
        """Generate summary report"""
        if self.is_valid():
            return f"✅ Spatial validation passed ({len(self.warnings)} warnings)"
        else:
            return f"❌ Spatial validation failed ({len(self.errors)} errors, {len(self.warnings)} warnings)"


class SpatialValidator:
    """
    Validates spatial properties of positioned scenes

    Usage:
        validator = SpatialValidator(canvas_width=1200, canvas_height=800)
        report = validator.validate(scene)
        if report.has_errors():
            print(report.summary())
            for error in report.errors:
                print(f"  - {error}")
    """

    def __init__(self, canvas_width: int = 1200, canvas_height: int = 800, margin: int = 20):
        """
        Initialize spatial validator

        Args:
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            margin: Safety margin from canvas edges
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.margin = margin

    def validate(self, scene: Scene) -> SpatialValidationReport:
        """
        Validate spatial properties of scene

        Args:
            scene: Positioned scene to validate

        Returns:
            Validation report with errors and warnings
        """
        report = SpatialValidationReport()

        # Check 1: Detect overlapping rectangles
        overlaps = self._check_overlaps(scene)
        for overlap in overlaps:
            if not overlap.is_intentional:
                report.errors.append(
                    f"Unintended overlap between '{overlap.obj1_id}' and '{overlap.obj2_id}' "
                    f"(area: {overlap.overlap_area:.1f} px²)"
                )
                report.overlaps.append(overlap)

        # Check 2: Label positioning
        label_issues = self._check_label_placement(scene)
        for issue in label_issues:
            if issue.issue_type == "overlaps_shape":
                report.warnings.append(
                    f"Label '{issue.label_id}' overlaps with shape '{issue.overlapping_with}'"
                )
            elif issue.issue_type == "overlaps_label":
                report.warnings.append(
                    f"Label '{issue.label_id}' overlaps with label '{issue.overlapping_with}'"
                )
            report.label_issues.append(issue)

        # Check 3: Canvas bounds
        out_of_bounds = self._check_bounds(scene)
        for obj_id, extent in out_of_bounds:
            report.errors.append(
                f"Object '{obj_id}' extends beyond canvas bounds "
                f"(extends {extent:.1f}px outside)"
            )

        # Check 4: Z-order correctness
        z_order_issues = self._check_z_order(scene)
        for obj_id, expected_layer, actual_layer in z_order_issues:
            report.warnings.append(
                f"Object '{obj_id}' has unexpected z-order: "
                f"expected {expected_layer.name}, got {actual_layer.name}"
            )

        # Check 5: Missing positions
        missing_positions = self._check_missing_positions(scene)
        for obj_id in missing_positions:
            report.errors.append(
                f"Object '{obj_id}' has no position assigned"
            )

        return report

    def _check_overlaps(self, scene: Scene) -> List[Overlap]:
        """Detect overlapping rectangles"""
        overlaps = []
        rectangles = [obj for obj in scene.objects
                     if obj.type in [PrimitiveType.RECTANGLE, PrimitiveType.CAPACITOR_PLATE]
                     and obj.position is not None]

        for i, rect1 in enumerate(rectangles):
            for rect2 in rectangles[i+1:]:
                overlap_area = self._calculate_overlap_area(rect1, rect2)
                if overlap_area > 0:
                    # Check if overlap is intentional (e.g., containment constraint)
                    is_intentional = self._is_intentional_overlap(
                        rect1, rect2, scene.constraints
                    )
                    overlaps.append(Overlap(
                        obj1_id=rect1.id,
                        obj2_id=rect2.id,
                        is_intentional=is_intentional,
                        overlap_area=overlap_area
                    ))

        return overlaps

    def _calculate_overlap_area(self, r1: SceneObject, r2: SceneObject) -> float:
        """Calculate overlap area between two rectangles"""
        if r1.position is None or r2.position is None:
            return 0.0

        # Get rectangle bounds
        r1_bounds = self._get_bounds(r1)
        r2_bounds = self._get_bounds(r2)

        if r1_bounds is None or r2_bounds is None:
            return 0.0

        r1_x1, r1_y1, r1_x2, r1_y2 = r1_bounds
        r2_x1, r2_y1, r2_x2, r2_y2 = r2_bounds

        # Calculate intersection
        inter_x1 = max(r1_x1, r2_x1)
        inter_y1 = max(r1_y1, r2_y1)
        inter_x2 = min(r1_x2, r2_x2)
        inter_y2 = min(r1_y2, r2_y2)

        # Check if there's an intersection
        if inter_x2 > inter_x1 and inter_y2 > inter_y1:
            return (inter_x2 - inter_x1) * (inter_y2 - inter_y1)

        return 0.0

    def _get_bounds(self, obj: SceneObject) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding box (x1, y1, x2, y2) for an object"""
        if obj.position is None:
            return None

        pos = obj.position
        x = pos.get("x", 0)
        y = pos.get("y", 0)

        # Get dimensions from properties
        if obj.type in [PrimitiveType.RECTANGLE, PrimitiveType.CAPACITOR_PLATE]:
            width = obj.properties.get("width", 0)
            height = obj.properties.get("height", 0)

            # Handle different anchor points
            anchor = pos.get("anchor", "top-left")
            if anchor == "top-left":
                return (x, y, x + width, y + height)
            elif anchor == "center":
                return (x - width/2, y - height/2, x + width/2, y + height/2)
            elif anchor == "bottom-left":
                return (x, y - height, x + width, y)
            else:
                # Default to top-left
                return (x, y, x + width, y + height)

        elif obj.type == PrimitiveType.CIRCLE:
            radius = obj.properties.get("radius", 0)
            return (x - radius, y - radius, x + radius, y + radius)

        elif obj.type == PrimitiveType.TEXT:
            # Approximate text bounds
            font_size = obj.properties.get("font_size", 14)
            text = obj.properties.get("text", "")
            # Rough approximation: 0.6 * font_size per character
            width = len(text) * font_size * 0.6
            height = font_size * 1.2
            return (x, y - height, x + width, y)

        return None

    def _is_intentional_overlap(
        self,
        obj1: SceneObject,
        obj2: SceneObject,
        constraints: List
    ) -> bool:
        """Check if overlap is intentional based on constraints"""
        # Check for CONTAINMENT constraint
        for constraint in constraints:
            if constraint.type == ConstraintType.CONTAINMENT:
                objs = constraint.objects
                if (obj1.id in objs and obj2.id in objs):
                    return True

            # Check for CONTAINS constraint
            if constraint.type == ConstraintType.CONTAINS:
                objs = constraint.objects
                if (obj1.id in objs and obj2.id in objs):
                    return True

        # Check by layer: if one is FILL and other is SHAPES, likely intentional
        if ((obj1.layer == RenderLayer.FILL and obj2.layer == RenderLayer.SHAPES) or
            (obj1.layer == RenderLayer.SHAPES and obj2.layer == RenderLayer.FILL)):
            return True

        return False

    def _check_label_placement(self, scene: Scene) -> List[LabelIssue]:
        """Check label positioning for overlaps"""
        issues = []
        labels = [obj for obj in scene.objects
                 if obj.type == PrimitiveType.TEXT and obj.position is not None]
        shapes = [obj for obj in scene.objects
                 if obj.type != PrimitiveType.TEXT and obj.position is not None]

        for label in labels:
            label_bounds = self._get_bounds(label)
            if label_bounds is None:
                continue

            # Check overlap with shapes
            for shape in shapes:
                shape_bounds = self._get_bounds(shape)
                if shape_bounds is None:
                    continue

                if self._bounds_overlap(label_bounds, shape_bounds):
                    issues.append(LabelIssue(
                        label_id=label.id,
                        issue_type="overlaps_shape",
                        overlapping_with=shape.id
                    ))

            # Check overlap with other labels
            for other_label in labels:
                if other_label.id == label.id:
                    continue

                other_bounds = self._get_bounds(other_label)
                if other_bounds is None:
                    continue

                if self._bounds_overlap(label_bounds, other_bounds):
                    issues.append(LabelIssue(
                        label_id=label.id,
                        issue_type="overlaps_label",
                        overlapping_with=other_label.id
                    ))

        return issues

    def _bounds_overlap(
        self,
        bounds1: Tuple[float, float, float, float],
        bounds2: Tuple[float, float, float, float]
    ) -> bool:
        """Check if two bounding boxes overlap"""
        x1_1, y1_1, x2_1, y2_1 = bounds1
        x1_2, y1_2, x2_2, y2_2 = bounds2

        return not (x2_1 < x1_2 or x1_1 > x2_2 or y2_1 < y1_2 or y1_1 > y2_2)

    def _check_bounds(self, scene: Scene) -> List[Tuple[str, float]]:
        """Check if objects are within canvas bounds"""
        out_of_bounds = []

        for obj in scene.objects:
            if obj.position is None:
                continue

            bounds = self._get_bounds(obj)
            if bounds is None:
                continue

            x1, y1, x2, y2 = bounds

            # Check how far outside canvas (if at all)
            extent = 0.0
            if x1 < self.margin:
                extent = max(extent, self.margin - x1)
            if x2 > self.canvas_width - self.margin:
                extent = max(extent, x2 - (self.canvas_width - self.margin))
            if y1 < self.margin:
                extent = max(extent, self.margin - y1)
            if y2 > self.canvas_height - self.margin:
                extent = max(extent, y2 - (self.canvas_height - self.margin))

            if extent > 0:
                out_of_bounds.append((obj.id, extent))

        return out_of_bounds

    def _check_z_order(self, scene: Scene) -> List[Tuple[str, RenderLayer, RenderLayer]]:
        """Check z-order correctness"""
        issues = []

        for obj in scene.objects:
            expected_layer = self._infer_expected_layer(obj)
            if expected_layer is not None and expected_layer != obj.layer:
                issues.append((obj.id, expected_layer, obj.layer))

        return issues

    def _infer_expected_layer(self, obj: SceneObject) -> Optional[RenderLayer]:
        """Infer expected layer based on object type"""
        type_to_layer = {
            PrimitiveType.TEXT: RenderLayer.LABELS,
            PrimitiveType.ARROW: RenderLayer.ARROWS,
            PrimitiveType.DIMENSION_ARROW: RenderLayer.ANNOTATIONS,
            PrimitiveType.FIELD_LINE: RenderLayer.LINES,
        }

        return type_to_layer.get(obj.type)

    def _check_missing_positions(self, scene: Scene) -> List[str]:
        """Check for objects without positions"""
        missing = []

        for obj in scene.objects:
            if obj.position is None:
                missing.append(obj.id)

        return missing


# Example usage and testing
if __name__ == '__main__':
    print("="*80)
    print("Spatial Validator Test")
    print("="*80)

    from core.scene.schema_v1 import Scene, SceneObject, Constraint, PrimitiveType, ConstraintType, RenderLayer

    # Create test scene with intentional issues
    scene = Scene()

    # Object 1: Rectangle within bounds
    scene.objects.append(SceneObject(
        id="rect1",
        type=PrimitiveType.RECTANGLE,
        position={"x": 100, "y": 100, "anchor": "top-left"},
        properties={"width": 200, "height": 100},
        layer=RenderLayer.SHAPES
    ))

    # Object 2: Rectangle that overlaps with rect1
    scene.objects.append(SceneObject(
        id="rect2",
        type=PrimitiveType.RECTANGLE,
        position={"x": 250, "y": 150, "anchor": "top-left"},
        properties={"width": 200, "height": 100},
        layer=RenderLayer.SHAPES
    ))

    # Object 3: Rectangle out of bounds
    scene.objects.append(SceneObject(
        id="rect3",
        type=PrimitiveType.RECTANGLE,
        position={"x": 1150, "y": 100, "anchor": "top-left"},
        properties={"width": 200, "height": 100},
        layer=RenderLayer.SHAPES
    ))

    # Object 4: Label overlapping rect1
    scene.objects.append(SceneObject(
        id="label1",
        type=PrimitiveType.TEXT,
        position={"x": 150, "y": 150, "anchor": "bottom-left"},
        properties={"text": "Test Label", "font_size": 16},
        layer=RenderLayer.LABELS
    ))

    # Object 5: Object without position
    scene.objects.append(SceneObject(
        id="rect4",
        type=PrimitiveType.RECTANGLE,
        position=None,
        properties={"width": 100, "height": 50},
        layer=RenderLayer.SHAPES
    ))

    # Run validation
    validator = SpatialValidator(canvas_width=1200, canvas_height=800)
    report = validator.validate(scene)

    # Print results
    print(f"\n{report.summary()}")
    print(f"\nErrors ({len(report.errors)}):")
    for error in report.errors:
        print(f"  ❌ {error}")

    print(f"\nWarnings ({len(report.warnings)}):")
    for warning in report.warnings:
        print(f"  ⚠️  {warning}")

    print(f"\n{'='*80}")
    print("✅ Spatial validator test complete")
    print("="*80)
