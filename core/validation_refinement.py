"""
Validation and Refinement Layer
================================

This module provides validation and automatic refinement for diagrams:
- Visual diagram validation
- Automatic refinement suggestions
- Quality scoring (0-100)
- Error detection and correction
- Best practices enforcement

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Position,
    ObjectType, RelationType
)
import math


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # "error", "warning", "info"
    category: str  # "layout", "connectivity", "style", "physics"
    message: str
    affected_objects: List[str]
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class QualityScore:
    """Quality assessment of a diagram"""
    overall_score: float  # 0-100
    layout_score: float
    connectivity_score: float
    style_score: float
    physics_score: float
    issues: List[ValidationIssue]


class DiagramValidator:
    """
    Validates diagrams and provides quality assessments
    """

    def __init__(self):
        self.min_spacing = 50
        self.max_component_distance = 500
        self.ideal_component_distance = 150

    # ========== Safe Accessor Methods (handle both dict and Position object) ==========

    def _get_x(self, pos) -> float:
        """Safely get x coordinate from position (dict or Position object)"""
        if isinstance(pos, dict):
            return pos.get('x', 0.0)
        return getattr(pos, 'x', 0.0)

    def _get_y(self, pos) -> float:
        """Safely get y coordinate from position (dict or Position object)"""
        if isinstance(pos, dict):
            return pos.get('y', 0.0)
        return getattr(pos, 'y', 0.0)

    def _get_width(self, dims) -> float:
        """Safely get width from dimensions (dict or object)"""
        if dims is None:
            return 100.0
        if isinstance(dims, dict):
            return dims.get('width', 100.0)
        return getattr(dims, 'width', 100.0)

    def _get_height(self, dims) -> float:
        """Safely get height from dimensions (dict or object)"""
        if dims is None:
            return 100.0
        if isinstance(dims, dict):
            return dims.get('height', 100.0)
        return getattr(dims, 'height', 100.0)

    def _set_x(self, pos, value: float):
        """Safely set x coordinate (dict or Position object)"""
        if isinstance(pos, dict):
            pos['x'] = value
        else:
            pos.x = value

    def _set_y(self, pos, value: float):
        """Safely set y coordinate (dict or Position object)"""
        if isinstance(pos, dict):
            pos['y'] = value
        else:
            pos.y = value

    # ========== Validation Methods ==========

    def validate(self, scene: UniversalScene) -> QualityScore:
        """
        Validate scene and return quality score

        Args:
            scene: Scene to validate

        Returns:
            Quality score with issues list
        """
        print("  🔍 Validating diagram...")

        issues = []

        # Run validation checks
        issues.extend(self._validate_layout(scene))
        issues.extend(self._validate_connectivity(scene))
        issues.extend(self._validate_style(scene))
        issues.extend(self._validate_physics(scene))

        # Calculate scores
        layout_score = self._calculate_layout_score(scene, issues)
        connectivity_score = self._calculate_connectivity_score(scene, issues)
        style_score = self._calculate_style_score(scene, issues)
        physics_score = self._calculate_physics_score(scene, issues)

        # Overall score (weighted average)
        overall_score = (
            layout_score * 0.3 +
            connectivity_score * 0.3 +
            style_score * 0.2 +
            physics_score * 0.2
        )

        quality = QualityScore(
            overall_score=overall_score,
            layout_score=layout_score,
            connectivity_score=connectivity_score,
            style_score=style_score,
            physics_score=physics_score,
            issues=issues
        )

        print(f"  ✅ Validation complete: Score = {overall_score:.1f}/100")
        return quality

    def _validate_layout(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate layout quality"""
        issues = []

        if not scene.objects:
            return issues

        # Check for overlapping components
        for i, obj1 in enumerate(scene.objects):
            for obj2 in scene.objects[i+1:]:
                if self._objects_overlap(obj1, obj2):
                    issues.append(ValidationIssue(
                        severity="error",
                        category="layout",
                        message=f"Objects {obj1.id} and {obj2.id} are overlapping",
                        affected_objects=[obj1.id, obj2.id],
                        fix_suggestion="Increase spacing between components",
                        auto_fixable=True
                    ))

        # Check component spacing
        for i, obj1 in enumerate(scene.objects):
            for obj2 in scene.objects[i+1:]:
                distance = self._calculate_distance(obj1.position, obj2.position)
                if distance < self.min_spacing:
                    issues.append(ValidationIssue(
                        severity="warning",
                        category="layout",
                        message=f"Components {obj1.id} and {obj2.id} are too close",
                        affected_objects=[obj1.id, obj2.id],
                        fix_suggestion=f"Maintain minimum spacing of {self.min_spacing}px",
                        auto_fixable=True
                    ))

        # Check alignment
        y_positions = [self._get_y(obj.position) for obj in scene.objects]
        if len(set([round(y/20) for y in y_positions])) == len(scene.objects):
            issues.append(ValidationIssue(
                severity="info",
                category="layout",
                message="Components could be better aligned",
                affected_objects=[obj.id for obj in scene.objects],
                fix_suggestion="Align components horizontally or vertically",
                auto_fixable=True
            ))

        # Check if layout is centered
        if scene.objects:
            avg_x = sum(self._get_x(obj.position) for obj in scene.objects) / len(scene.objects)
            avg_y = sum(self._get_y(obj.position) for obj in scene.objects) / len(scene.objects)
            center_x = scene.coord_system.get('extent', [1200, 800])[0] / 2
            center_y = scene.coord_system.get('extent', [1200, 800])[1] / 2

            if abs(avg_x - center_x) > 100 or abs(avg_y - center_y) > 100:
                issues.append(ValidationIssue(
                    severity="info",
                    category="layout",
                    message="Layout is not centered in canvas",
                    affected_objects=[],
                    fix_suggestion="Center the layout",
                    auto_fixable=True
                ))

        return issues

    def _validate_connectivity(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate connectivity and relationships"""
        issues = []

        # Scene may not have relationships attribute (uses constraints instead)
        relationships = getattr(scene, 'relationships', [])

        if not relationships:
            if len(scene.objects) > 1:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="connectivity",
                    message="Multiple objects present but no connections defined",
                    affected_objects=[obj.id for obj in scene.objects],
                    fix_suggestion="Add connections between related components",
                    auto_fixable=False
                ))
            return issues

        # Check for dangling connections
        object_ids = {obj.id for obj in scene.objects}
        for rel in relationships:
            if rel.source_id not in object_ids:
                issues.append(ValidationIssue(
                    severity="error",
                    category="connectivity",
                    message=f"Connection references non-existent object: {rel.source_id}",
                    affected_objects=[rel.id],
                    fix_suggestion="Remove invalid connection",
                    auto_fixable=True
                ))
            if rel.target_id not in object_ids:
                issues.append(ValidationIssue(
                    severity="error",
                    category="connectivity",
                    message=f"Connection references non-existent object: {rel.target_id}",
                    affected_objects=[rel.id],
                    fix_suggestion="Remove invalid connection",
                    auto_fixable=True
                ))

        # Check for disconnected components (for circuits)
        domain = getattr(scene, 'domain', None)
        if domain and hasattr(domain, 'value') and domain.value == "electronics":
            obj_dict = {obj.id: obj for obj in scene.objects}
            connected_objs = set()
            for rel in relationships:
                connected_objs.add(rel.source_id)
                connected_objs.add(rel.target_id)

            disconnected = object_ids - connected_objs
            if disconnected and len(scene.objects) > 1:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="connectivity",
                    message=f"Disconnected components: {', '.join(disconnected)}",
                    affected_objects=list(disconnected),
                    fix_suggestion="Connect all circuit components",
                    auto_fixable=False
                ))

        # Check connection distances
        obj_dict = {obj.id: obj for obj in scene.objects}
        for rel in relationships:
            if rel.source_id in obj_dict and rel.target_id in obj_dict:
                source = obj_dict[rel.source_id]
                target = obj_dict[rel.target_id]
                distance = self._calculate_distance(source.position, target.position)

                if distance > self.max_component_distance:
                    issues.append(ValidationIssue(
                        severity="warning",
                        category="connectivity",
                        message=f"Very long connection between {rel.source_id} and {rel.target_id}",
                        affected_objects=[rel.source_id, rel.target_id],
                        fix_suggestion="Bring connected components closer",
                        auto_fixable=True
                    ))

        return issues

    def _validate_style(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate visual style consistency"""
        issues = []

        # Check for labels
        unlabeled = [obj for obj in scene.objects if not (obj.properties and obj.properties.get('label'))]
        if unlabeled and len(scene.objects) > 1:
            issues.append(ValidationIssue(
                severity="info",
                category="style",
                message=f"{len(unlabeled)} objects without labels",
                affected_objects=[obj.id for obj in unlabeled],
                fix_suggestion="Add labels to all components",
                auto_fixable=False
            ))

        # Check color consistency
        colors = [obj.style.get('color') for obj in scene.objects if obj.style and isinstance(obj.style, dict) and obj.style.get('color')]
        if len(set(colors)) > 5:
            issues.append(ValidationIssue(
                severity="info",
                category="style",
                message="Too many different colors used",
                affected_objects=[],
                fix_suggestion="Use consistent color scheme",
                auto_fixable=True
            ))

        # Check font consistency
        font_sizes = [obj.style.get('font_size') for obj in scene.objects if obj.style and isinstance(obj.style, dict) and obj.style.get('font_size')]
        if len(set(font_sizes)) > 3:
            issues.append(ValidationIssue(
                severity="info",
                category="style",
                message="Inconsistent font sizes",
                affected_objects=[],
                fix_suggestion="Use 2-3 font sizes maximum",
                auto_fixable=True
            ))

        return issues

    def _validate_physics(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate physical correctness"""
        issues = []

        # Domain-specific validation
        domain = getattr(scene, 'domain', None)
        if domain and hasattr(domain, 'value'):
            if domain.value == "electronics":
                issues.extend(self._validate_circuit_physics(scene))
            elif domain.value == "chemistry":
                issues.extend(self._validate_chemistry_physics(scene))

        return issues

    def _validate_circuit_physics(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate circuit physics"""
        issues = []

        # Check for power source
        power_sources = [obj for obj in scene.objects
                        if obj.object_type == ObjectType.BATTERY]

        if not power_sources and len(scene.objects) > 1:
            issues.append(ValidationIssue(
                severity="warning",
                category="physics",
                message="Circuit has no power source",
                affected_objects=[],
                fix_suggestion="Add a battery or power source",
                auto_fixable=False
            ))

        # Check for closed circuit
        if relationships:
            # Simple check: all components should be in a connected graph
            obj_dict = {obj.id: obj for obj in scene.objects}
            visited = set()

            def dfs(obj_id):
                if obj_id in visited:
                    return
                visited.add(obj_id)
                for rel in relationships:
                    if rel.source_id == obj_id:
                        dfs(rel.target_id)
                    elif rel.target_id == obj_id:
                        dfs(rel.source_id)

            if scene.objects:
                dfs(scene.objects[0].id)

                if len(visited) < len(scene.objects):
                    issues.append(ValidationIssue(
                        severity="warning",
                        category="physics",
                        message="Circuit may not be closed (not all components connected)",
                        affected_objects=[],
                        fix_suggestion="Ensure circuit forms closed loop",
                        auto_fixable=False
                    ))

        return issues

    def _validate_chemistry_physics(self, scene: UniversalScene) -> List[ValidationIssue]:
        """Validate chemistry physics"""
        issues = []

        # Scene may not have relationships attribute
        relationships = getattr(scene, 'relationships', [])

        # Check bond valences (simplified)
        atoms = [obj for obj in scene.objects if obj.object_type == ObjectType.ATOM]

        for atom in atoms:
            # Count bonds
            bonds = [rel for rel in relationships
                    if (rel.source_id == atom.id or rel.target_id == atom.id)]

            # Simple valence check (this is very simplified)
            if len(bonds) > 4:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="physics",
                    message=f"Atom {atom.id} has unusual number of bonds: {len(bonds)}",
                    affected_objects=[atom.id],
                    fix_suggestion="Check chemical valence rules",
                    auto_fixable=False
                ))

        return issues

    def _calculate_layout_score(self, scene: UniversalScene,
                                issues: List[ValidationIssue]) -> float:
        """Calculate layout quality score"""
        score = 100.0

        # Deduct for issues
        for issue in issues:
            if issue.category == "layout":
                if issue.severity == "error":
                    score -= 20
                elif issue.severity == "warning":
                    score -= 10
                elif issue.severity == "info":
                    score -= 5

        return max(0.0, min(100.0, score))

    def _calculate_connectivity_score(self, scene: UniversalScene,
                                      issues: List[ValidationIssue]) -> float:
        """Calculate connectivity quality score"""
        score = 100.0

        for issue in issues:
            if issue.category == "connectivity":
                if issue.severity == "error":
                    score -= 25
                elif issue.severity == "warning":
                    score -= 15
                elif issue.severity == "info":
                    score -= 5

        return max(0.0, min(100.0, score))

    def _calculate_style_score(self, scene: UniversalScene,
                               issues: List[ValidationIssue]) -> float:
        """Calculate style quality score"""
        score = 100.0

        for issue in issues:
            if issue.category == "style":
                if issue.severity == "error":
                    score -= 15
                elif issue.severity == "warning":
                    score -= 10
                elif issue.severity == "info":
                    score -= 5

        return max(0.0, min(100.0, score))

    def _calculate_physics_score(self, scene: UniversalScene,
                                 issues: List[ValidationIssue]) -> float:
        """Calculate physics correctness score"""
        score = 100.0

        for issue in issues:
            if issue.category == "physics":
                if issue.severity == "error":
                    score -= 30
                elif issue.severity == "warning":
                    score -= 15
                elif issue.severity == "info":
                    score -= 5

        return max(0.0, min(100.0, score))

    def _objects_overlap(self, obj1: SceneObject, obj2: SceneObject) -> bool:
        """Check if two objects overlap"""
        # Simple rectangular overlap check
        x1 = self._get_x(obj1.position)
        y1 = self._get_y(obj1.position)
        w1 = self._get_width(getattr(obj1, 'dimensions', None))
        h1 = self._get_height(getattr(obj1, 'dimensions', None))

        x2 = self._get_x(obj2.position)
        y2 = self._get_y(obj2.position)
        w2 = self._get_width(getattr(obj2, 'dimensions', None))
        h2 = self._get_height(getattr(obj2, 'dimensions', None))

        x1_min = x1 - w1 / 2
        x1_max = x1 + w1 / 2
        y1_min = y1 - h1 / 2
        y1_max = y1 + h1 / 2

        x2_min = x2 - w2 / 2
        x2_max = x2 + w2 / 2
        y2_min = y2 - h2 / 2
        y2_max = y2 + h2 / 2

        return not (x1_max < x2_min or x2_max < x1_min or
                   y1_max < y2_min or y2_max < y1_min)

    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """Calculate distance between two positions"""
        x1 = self._get_x(pos1)
        y1 = self._get_y(pos1)
        x2 = self._get_x(pos2)
        y2 = self._get_y(pos2)
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


class DiagramRefiner:
    """
    Automatically refines diagrams based on validation issues
    """

    def __init__(self):
        self.validator = DiagramValidator()

    def refine(self, scene: UniversalScene, max_iterations: int = 3) -> Tuple[UniversalScene, QualityScore]:
        """
        Automatically refine diagram to improve quality

        Args:
            scene: Scene to refine
            max_iterations: Maximum refinement iterations

        Returns:
            Refined scene and final quality score
        """
        print("  🔧 Refining diagram...")

        for iteration in range(max_iterations):
            # Validate
            quality = self.validator.validate(scene)

            # If score is good enough, stop
            if quality.overall_score >= 90:
                break

            # Apply auto-fixes for fixable issues
            auto_fixed = 0
            for issue in quality.issues:
                if issue.auto_fixable:
                    if self._apply_auto_fix(scene, issue):
                        auto_fixed += 1

            print(f"    - Iteration {iteration + 1}: Score = {quality.overall_score:.1f}, Fixed {auto_fixed} issues")

            if auto_fixed == 0:
                break  # No more auto-fixes possible

        final_quality = self.validator.validate(scene)
        print(f"  ✅ Refinement complete: Final score = {final_quality.overall_score:.1f}/100")

        return scene, final_quality

    def _apply_auto_fix(self, scene: UniversalScene, issue: ValidationIssue) -> bool:
        """Apply automatic fix for an issue"""
        # Scene may not have relationships attribute
        relationships = getattr(scene, 'relationships', [])

        if issue.category == "layout":
            if "overlapping" in issue.message or "too close" in issue.message:
                # Increase spacing between affected objects
                if len(issue.affected_objects) >= 2:
                    obj1_id, obj2_id = issue.affected_objects[:2]
                    obj1 = next((obj for obj in scene.objects if obj.id == obj1_id), None)
                    obj2 = next((obj for obj in scene.objects if obj.id == obj2_id), None)

                    if obj1 and obj2:
                        # Move them apart
                        x1 = self.validator._get_x(obj1.position)
                        y1 = self.validator._get_y(obj1.position)
                        x2 = self.validator._get_x(obj2.position)
                        y2 = self.validator._get_y(obj2.position)

                        dx = x2 - x1
                        dy = y2 - y1
                        distance = math.sqrt(dx**2 + dy**2) + 1

                        move_distance = 30
                        new_x2 = x2 + (dx / distance) * move_distance
                        new_y2 = y2 + (dy / distance) * move_distance

                        self.validator._set_x(obj2.position, new_x2)
                        self.validator._set_y(obj2.position, new_y2)
                        return True

            elif "not centered" in issue.message:
                # Center layout
                if scene.objects:
                    avg_x = sum(self.validator._get_x(obj.position) for obj in scene.objects) / len(scene.objects)
                    avg_y = sum(self.validator._get_y(obj.position) for obj in scene.objects) / len(scene.objects)
                    center_x = scene.coord_system.get('extent', [1200, 800])[0] / 2
                    center_y = scene.coord_system.get('extent', [1200, 800])[1] / 2

                    offset_x = center_x - avg_x
                    offset_y = center_y - avg_y

                    for obj in scene.objects:
                        current_x = self.validator._get_x(obj.position)
                        current_y = self.validator._get_y(obj.position)
                        self.validator._set_x(obj.position, current_x + offset_x)
                        self.validator._set_y(obj.position, current_y + offset_y)
                    return True

        elif issue.category == "connectivity":
            if "dangling" in issue.message or "non-existent" in issue.message:
                # Remove invalid relationships
                relationships = [rel for rel in relationships
                                      if rel.id not in issue.affected_objects]
                return True

        return False


# Testing
if __name__ == "__main__":
    from core.universal_scene_format import create_circuit_scene, Dimensions

    print("Validation and Refinement Layer - Test")
    print("=" * 50)

    # Create test scene
    scene = create_circuit_scene("test_validation", "Test Circuit")

    # Add objects (some with issues)
    obj1 = SceneObject(
        id="R1",
        object_type=ObjectType.RESISTOR,
        position=Position(200, 200, 0),
        dimensions=Dimensions(width=80, height=40),
        label="10kΩ"
    )

    obj2 = SceneObject(
        id="C1",
        object_type=ObjectType.CAPACITOR,
        position=Position(210, 205, 0),  # Too close!
        dimensions=Dimensions(width=80, height=60),
        label="100μF"
    )

    obj3 = SceneObject(
        id="V1",
        object_type=ObjectType.BATTERY,
        position=Position(100, 200, 0),
        dimensions=Dimensions(width=80, height=50),
        label="9V"
    )

    scene.add_object(obj1)
    scene.add_object(obj2)
    scene.add_object(obj3)

    # Add relationship
    from core.universal_scene_format import Relationship, RelationType
    rel = Relationship(
        id="wire1",
        relation_type=RelationType.CONNECTED_TO,
        source_id="V1",
        target_id="R1"
    )
    scene.add_relationship(rel)

    print("\nValidating scene...")
    validator = DiagramValidator()
    quality = validator.validate(scene)

    print(f"\nQuality Scores:")
    print(f"  Overall: {quality.overall_score:.1f}/100")
    print(f"  Layout: {quality.layout_score:.1f}/100")
    print(f"  Connectivity: {quality.connectivity_score:.1f}/100")
    print(f"  Style: {quality.style_score:.1f}/100")
    print(f"  Physics: {quality.physics_score:.1f}/100")

    print(f"\nIssues found: {len(quality.issues)}")
    for issue in quality.issues:
        print(f"  [{issue.severity.upper()}] {issue.category}: {issue.message}")
        if issue.auto_fixable:
            print(f"    → Auto-fix available")

    # Test refinement
    print("\n" + "=" * 50)
    print("Testing automatic refinement...")
    refiner = DiagramRefiner()
    refined_scene, final_quality = refiner.refine(scene)

    print("\n" + "=" * 50)
    print("✅ Validation and Refinement Layer ready!")
    print("   - Comprehensive validation")
    print("   - Quality scoring (0-100)")
    print("   - Automatic issue detection")
    print("   - Auto-fix capabilities")
    print("   - Physics validation")
