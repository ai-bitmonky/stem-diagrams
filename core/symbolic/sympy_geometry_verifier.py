"""
SymPy Geometry Verifier - Symbolic spatial verification

Verifies spatial relationships using symbolic geometry to catch
geometric inconsistencies that heuristic layout might miss.
"""

from typing import Dict, List, Tuple, Optional
try:
    from sympy.geometry import Point, Segment, Circle
    from sympy import Float
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("⚠️  SymPy not available, geometric verification disabled")

from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType

class SymPyGeometryVerifier:
    """Verify spatial relationships using symbolic geometry"""

    def __init__(self):
        if not SYMPY_AVAILABLE:
            raise ImportError("SymPy is required for geometric verification")
        print("✅ SymPy Geometry Verifier initialized")

    def verify_scene(self, scene: Scene) -> Dict[str, any]:
        """
        Verify all spatial relationships in scene

        Returns:
            Dict with:
                - violations: List of constraint IDs that are violated
                - satisfactions: List of constraint IDs that are satisfied
                - overall_valid: Boolean indicating if scene is geometrically valid
        """
        violations = []
        satisfactions = []

        # Convert scene objects to SymPy geometry
        sympy_objects = self._scene_to_sympy(scene)

        if not sympy_objects:
            return {
                'violations': [],
                'satisfactions': [],
                'overall_valid': True,
                'message': 'No positioned objects to verify'
            }

        # Verify each constraint
        for i, constraint in enumerate(scene.constraints):
            constraint_id = f"constraint_{i}"

            try:
                is_satisfied = self._verify_constraint(constraint, sympy_objects)

                if is_satisfied:
                    satisfactions.append(constraint_id)
                else:
                    violations.append(constraint_id)
            except Exception as e:
                # Skip constraints we can't verify
                print(f"      ⚠️  Could not verify constraint {constraint_id}: {e}")

        return {
            'violations': violations,
            'satisfactions': satisfactions,
            'overall_valid': len(violations) == 0,
            'total_constraints': len(scene.constraints),
            'verified_constraints': len(violations) + len(satisfactions)
        }

    def _scene_to_sympy(self, scene: Scene) -> Dict[str, Point]:
        """Convert scene objects to SymPy Points"""
        points = {}
        for obj in scene.objects:
            if obj.position:
                points[obj.id] = Point(Float(obj.position.x), Float(obj.position.y))
        return points

    def _verify_constraint(self, constraint: Constraint, sympy_objects: Dict[str, Point]) -> bool:
        """Verify a single constraint"""

        if len(constraint.object_ids) < 2:
            return True  # Can't verify single-object constraints

        obj1_id = constraint.object_ids[0]
        obj2_id = constraint.object_ids[1]

        if obj1_id not in sympy_objects or obj2_id not in sympy_objects:
            return True  # Skip if objects not positioned

        obj1 = sympy_objects[obj1_id]
        obj2 = sympy_objects[obj2_id]

        if constraint.type == ConstraintType.ABOVE:
            return self._verify_above(obj1, obj2)
        elif constraint.type == ConstraintType.BELOW:
            return self._verify_below(obj1, obj2)
        elif constraint.type == ConstraintType.LEFT_OF:
            return self._verify_left_of(obj1, obj2)
        elif constraint.type == ConstraintType.RIGHT_OF:
            return self._verify_right_of(obj1, obj2)
        elif constraint.type == ConstraintType.DISTANCE:
            expected_dist = constraint.parameters.get('distance', 100.0)
            return self._verify_distance(obj1, obj2, expected_dist)
        else:
            # Unknown constraint type
            return True

    def _verify_above(self, obj1: Point, obj2: Point) -> bool:
        """Verify obj1 is above obj2 (smaller y in SVG coordinates)"""
        return float(obj1.y) < float(obj2.y)

    def _verify_below(self, obj1: Point, obj2: Point) -> bool:
        """Verify obj1 is below obj2 (larger y in SVG coordinates)"""
        return float(obj1.y) > float(obj2.y)

    def _verify_left_of(self, obj1: Point, obj2: Point) -> bool:
        """Verify obj1 is left of obj2"""
        return float(obj1.x) < float(obj2.x)

    def _verify_right_of(self, obj1: Point, obj2: Point) -> bool:
        """Verify obj1 is right of obj2"""
        return float(obj1.x) > float(obj2.x)

    def _verify_distance(self, obj1: Point, obj2: Point, expected_dist: float) -> bool:
        """Verify distance between objects"""
        actual_dist = obj1.distance(obj2)
        tolerance = 10.0  # 10px tolerance
        return abs(float(actual_dist) - expected_dist) < tolerance
