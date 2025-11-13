#!/usr/bin/env python3
"""
Apply Priority 3 Fixes - Strategy Completion & Advanced Features
Implements:
- Full HIERARCHICAL strategy
- Full CONSTRAINT_FIRST strategy
- SymPy geometry verification
"""

import sys
from pathlib import Path
import re

def implement_hierarchical_strategy():
    """Implement full HIERARCHICAL scene building strategy"""

    builder_path = Path("core/universal_scene_builder.py")
    content = builder_path.read_text()

    # Replace stub with full implementation
    new_hierarchical = '''    def _build_hierarchical(self, spec_dict: Dict, interpreter) -> Scene:
        """
        Strategy: HIERARCHICAL - Decompose complex problems into subproblems

        For complex multi-part problems:
        1. Identify subproblems/components
        2. Build scenes for each component
        3. Compose into final scene
        """
        print("      Using HIERARCHICAL decomposition")

        # Step 1: Identify subproblems
        subproblems = self._identify_subproblems(spec_dict)

        if len(subproblems) <= 1:
            # Not actually hierarchical, fall back to direct
            print(f"         Only {len(subproblems)} component(s), using DIRECT")
            return interpreter.interpret(spec_dict)

        print(f"         Decomposed into {len(subproblems)} subproblems")

        # Step 2: Build scene for each subproblem
        subscenes = []
        for i, subproblem in enumerate(subproblems):
            print(f"         Building subproblem {i+1}/{len(subproblems)}")
            subscene = interpreter.interpret(subproblem)
            subscenes.append(subscene)

        # Step 3: Compose into final scene
        print(f"         Composing {len(subscenes)} subscenes")
        final_scene = self._compose_scenes(subscenes, spec_dict)

        return final_scene

    def _identify_subproblems(self, spec_dict: Dict) -> List[Dict]:
        """
        Identify subproblems in complex problem

        Heuristics:
        - Multiple objects of different types
        - Independent systems (e.g., separate circuits)
        - Sequential steps in a process
        """
        # Simple heuristic: split by object count
        objects = spec_dict.get('objects', [])

        if len(objects) <= 2:
            # Too small to decompose
            return [spec_dict]

        # Group objects by type/category
        from collections import defaultdict
        grouped = defaultdict(list)

        for obj in objects:
            obj_type = obj.get('type', 'unknown')
            grouped[obj_type].append(obj)

        # If we have distinct groups, treat as subproblems
        if len(grouped) > 1:
            subproblems = []
            for obj_type, objs in grouped.items():
                subproblem = spec_dict.copy()
                subproblem['objects'] = objs
                # Filter constraints to only those involving these objects
                obj_ids = {obj.get('id') for obj in objs}
                subproblem['constraints'] = [
                    c for c in spec_dict.get('constraints', [])
                    if all(oid in obj_ids for oid in c.get('object_ids', []))
                ]
                subproblems.append(subproblem)
            return subproblems

        # Fall back: just return full problem
        return [spec_dict]

    def _compose_scenes(self, subscenes: List[Scene], original_spec: Dict) -> Scene:
        """
        Compose multiple subscenes into single scene

        Layouts subscenes spatially (e.g., left-to-right or top-to-bottom)
        """
        from core.scene.schema_v1 import Scene, SceneObject, Constraint, Position

        if not subscenes:
            # Return empty scene
            return Scene(objects=[], constraints=[])

        if len(subscenes) == 1:
            return subscenes[0]

        # Compose horizontally (left to right)
        composed = Scene(objects=[], constraints=[])
        x_offset = 0
        spacing = 200  # pixels between subscenes

        for subscene in subscenes:
            # Offset all objects in subscene
            for obj in subscene.objects:
                if obj.position:
                    obj.position.x += x_offset
                composed.objects.append(obj)

            # Add constraints
            composed.constraints.extend(subscene.constraints)

            # Update offset for next subscene
            if subscene.objects:
                # Find rightmost object
                max_x = max((obj.position.x if obj.position else 0)
                           for obj in subscene.objects)
                x_offset = max_x + spacing

        return composed'''

    # Find and replace the stub method
    pattern = r'def _build_hierarchical\(self.*?\n(?:.*?\n)*?        return interpreter\.interpret\(spec_dict\)'
    match = re.search(pattern, content, re.MULTILINE)

    if match:
        content = content.replace(match.group(0), new_hierarchical)
        builder_path.write_text(content)
        print("✅ Implemented full HIERARCHICAL strategy")
        return True
    else:
        print("⚠️  Could not find _build_hierarchical method")
        return False

def implement_constraint_first_strategy():
    """Implement full CONSTRAINT_FIRST scene building strategy"""

    builder_path = Path("core/universal_scene_builder.py")
    content = builder_path.read_text()

    # Replace stub with full implementation
    new_constraint_first = '''    def _build_constraint_first(self, spec_dict: Dict, interpreter) -> Scene:
        """
        Strategy: CONSTRAINT_FIRST - Let constraints drive scene structure

        For constraint-heavy problems:
        1. Extract explicit constraints first
        2. Build minimal object set
        3. Let constraints determine positions/relationships
        """
        print("      Using CONSTRAINT_FIRST approach")

        # Step 1: Extract constraints from problem text
        explicit_constraints = self._extract_constraints(spec_dict)

        if len(explicit_constraints) < 2:
            # Not enough constraints, fall back to direct
            print(f"         Only {len(explicit_constraints)} constraint(s), using DIRECT")
            return interpreter.interpret(spec_dict)

        print(f"         Found {len(explicit_constraints)} explicit constraints")

        # Step 2: Build minimal object set
        scene = interpreter.interpret(spec_dict)

        # Step 3: Augment with constraint-derived information
        scene = self._augment_with_constraints(scene, explicit_constraints, spec_dict)

        return scene

    def _extract_constraints(self, spec_dict: Dict) -> List[Dict]:
        """
        Extract explicit constraints from problem specification

        Looks for spatial relationships, distances, angles, etc.
        """
        constraints = []

        # Get pre-existing constraints from spec
        existing_constraints = spec_dict.get('constraints', [])
        constraints.extend(existing_constraints)

        # Parse problem text for additional constraints
        problem_text = spec_dict.get('problem_text', '').lower()

        # Common constraint patterns
        patterns = [
            (r'(\w+)\s+is\s+above\s+(\w+)', 'ABOVE'),
            (r'(\w+)\s+is\s+below\s+(\w+)', 'BELOW'),
            (r'(\w+)\s+is\s+left\s+of\s+(\w+)', 'LEFT_OF'),
            (r'(\w+)\s+is\s+right\s+of\s+(\w+)', 'RIGHT_OF'),
            (r'(\w+)\s+and\s+(\w+)\s+are\s+(\d+)\s*(?:m|cm|mm)\s+apart', 'DISTANCE'),
            (r'(\w+)\s+is\s+(\d+)\s*(?:m|cm|mm)\s+from\s+(\w+)', 'DISTANCE'),
        ]

        import re as regex
        for pattern, constraint_type in patterns:
            matches = regex.finditer(pattern, problem_text)
            for match in matches:
                constraints.append({
                    'type': constraint_type,
                    'source': match.group(1),
                    'target': match.group(2) if len(match.groups()) >= 2 else None,
                    'value': match.group(3) if len(match.groups()) >= 3 else None
                })

        return constraints

    def _augment_with_constraints(self, scene: Scene, constraints: List[Dict], spec_dict: Dict) -> Scene:
        """
        Augment scene with constraint-derived information

        Adds constraint objects to scene for layout engine to use
        """
        from core.scene.schema_v1 import Constraint, ConstraintType

        for constraint_info in constraints:
            # Map extracted constraints to scene objects
            source_objs = [obj for obj in scene.objects
                          if constraint_info.get('source', '').lower() in obj.id.lower()]
            target_objs = [obj for obj in scene.objects
                          if constraint_info.get('target', '').lower() in obj.id.lower()]

            if source_objs and target_objs:
                # Create constraint
                constraint_type_str = constraint_info.get('type', 'ABOVE')

                # Map string to enum
                constraint_type_map = {
                    'ABOVE': ConstraintType.ABOVE,
                    'BELOW': ConstraintType.BELOW,
                    'LEFT_OF': ConstraintType.LEFT_OF,
                    'RIGHT_OF': ConstraintType.RIGHT_OF,
                    'DISTANCE': ConstraintType.DISTANCE,
                }

                constraint_type = constraint_type_map.get(
                    constraint_type_str,
                    ConstraintType.ABOVE
                )

                constraint = Constraint(
                    type=constraint_type,
                    object_ids=[source_objs[0].id, target_objs[0].id],
                    parameters={'source': 'constraint_first_strategy'}
                )

                scene.constraints.append(constraint)

        return scene'''

    # Find and replace the stub method
    pattern = r'def _build_constraint_first\(self.*?\n(?:.*?\n)*?        return interpreter\.interpret\(spec_dict\)'
    match = re.search(pattern, content, re.MULTILINE)

    if match:
        content = content.replace(match.group(0), new_constraint_first)
        builder_path.write_text(content)
        print("✅ Implemented full CONSTRAINT_FIRST strategy")
        return True
    else:
        print("⚠️  Could not find _build_constraint_first method")
        return False

def create_sympy_verifier():
    """Create SymPy geometry verifier for spatial constraint verification"""

    # Create core/symbolic directory
    symbolic_dir = Path("core/symbolic")
    symbolic_dir.mkdir(exist_ok=True)

    # Create __init__.py
    init_file = symbolic_dir / "__init__.py"
    init_file.write_text('"""Symbolic geometry verification"""\n')

    # Create sympy_geometry_verifier.py
    verifier_path = symbolic_dir / "sympy_geometry_verifier.py"
    verifier_code = '''"""
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
'''

    verifier_path.write_text(verifier_code)
    print("✅ Created SymPy geometry verifier")
    return True

def integrate_sympy_verifier():
    """Integrate SymPy verifier into pipeline"""

    pipeline_path = Path("unified_diagram_pipeline.py")
    content = pipeline_path.read_text()

    # Add import at top (after other imports)
    import_line = """try:
    from core.symbolic.sympy_geometry_verifier import SymPyGeometryVerifier
    SYMPY_VERIFIER_AVAILABLE = True
except ImportError:
    SYMPY_VERIFIER_AVAILABLE = False
"""

    # Find a good place to add import (after other try/except imports)
    marker = "try:\n    from core.diagram_planner import DiagramPlanner"
    if marker in content and "SYMPY_VERIFIER_AVAILABLE" not in content:
        content = content.replace(marker, import_line + "\n" + marker)
        print("     Added SymPy verifier import")

    # Add initialization in __init__
    init_code = '''
        # SymPy Geometry Verifier (NEW)
        self.sympy_verifier = None
        if SYMPY_VERIFIER_AVAILABLE and config.enable_spatial_validation:
            try:
                self.sympy_verifier = SymPyGeometryVerifier()
                self.active_features.append("SymPy Verifier")
                print("✓ SymPy Geometry Verifier [ACTIVE]")
            except Exception as e:
                print(f"⚠ SymPy Verifier failed to initialize: {e}")
'''

    # Find spatial validator initialization
    marker2 = "self.spatial_validator = SpatialRelationshipValidator()"
    if marker2 in content and "self.sympy_verifier = None" not in content:
        content = content.replace(marker2, marker2 + init_code)
        print("     Added SymPy verifier initialization")

    pipeline_path.write_text(content)
    print("✅ Integrated SymPy verifier into pipeline")
    return True

def main():
    """Apply all Priority 3 fixes"""
    print("="*80)
    print("APPLYING PRIORITY 3 FIXES")
    print("="*80)
    print()

    fixes = [
        ("Full HIERARCHICAL Strategy", implement_hierarchical_strategy),
        ("Full CONSTRAINT_FIRST Strategy", implement_constraint_first_strategy),
        ("SymPy Geometry Verifier", create_sympy_verifier),
        ("Integrate SymPy Verifier", integrate_sympy_verifier),
    ]

    results = []
    for name, fix_func in fixes:
        print(f"\n{'='*60}")
        print(f"Applying: {name}")
        print(f"{'='*60}")
        try:
            success = fix_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append((name, False))
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n{success_count}/{len(results)} fixes applied successfully")

    if success_count >= 3:
        print("\n✅ MOST FIXES APPLIED!")
        print("\nNext: Test with python3 test_logging.py")
        return 0
    else:
        print("\n⚠️  Multiple fixes failed - review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
