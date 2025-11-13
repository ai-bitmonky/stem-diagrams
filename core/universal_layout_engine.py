"""
Universal Layout Engine - Single Robust Pipeline Phase 4
Merges LP solver + Scene solver + PhysicsPositionCalculator + aesthetic optimization
Single deterministic layout algorithm
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType, PrimitiveType
from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain

try:
    from core.solvers.z3_layout_solver import Z3LayoutSolver
    Z3_LAYOUT_AVAILABLE = True
except Exception:
    Z3_LAYOUT_AVAILABLE = False
    Z3LayoutSolver = None

try:
    from core.sympy_solver import SymPyLayoutSolver
    SYMPY_LAYOUT_AVAILABLE = True
except Exception:
    SYMPY_LAYOUT_AVAILABLE = False
    SymPyLayoutSolver = None

try:
    from cassowary import SimplexSolver, Variable  # type: ignore
    CASSOWARY_AVAILABLE = True
except Exception:
    CASSOWARY_AVAILABLE = False
    SimplexSolver = None
    Variable = None

try:
    from core.label_placer import IntelligentLabelPlacer
    LABEL_PLACER_AVAILABLE = True
except Exception:
    LABEL_PLACER_AVAILABLE = False
    IntelligentLabelPlacer = None


class UniversalLayoutEngine:
    """
    Universal Layout Engine - Single robust implementation

    Merges:
    - constraint_solver.py (LP-based solver)
    - core/solver/constraint_solver.py (Scene-based iterative solver)
    - PhysicsPositionCalculator (physics-space positioning)

    Single deterministic algorithm that:
    1. Initializes smart positions based on domain
    2. Applies constraint satisfaction
    3. Optimizes for aesthetics
    4. Places labels intelligently
    """

    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize Universal Layout Engine

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        self.margin = 40

        print(f"✅ UniversalLayoutEngine initialized")
        print(f"   Canvas: {width}x{height}")
        print(f"   Center: {self.center}")

        self.z3_solver = Z3LayoutSolver() if Z3_LAYOUT_AVAILABLE else None
        self.sympy_solver = SymPyLayoutSolver() if SYMPY_LAYOUT_AVAILABLE else None
        self.cassowary_solver_cls = SimplexSolver if CASSOWARY_AVAILABLE else None
        self.label_placer = IntelligentLabelPlacer(canvas_width=width, canvas_height=height) if LABEL_PLACER_AVAILABLE else None
        self._solver_warning_cache: Dict[str, str] = {}

    def _get_position_coords(self, obj: SceneObject) -> Tuple[float, float]:
        """Get (x, y) coordinates from position regardless of format (dict or Position object)"""
        if not obj or not obj.position:
            return 0, 0
        if isinstance(obj.position, dict):
            x = obj.position.get('x') or 0
            y = obj.position.get('y') or 0
            return x, y
        elif hasattr(obj.position, 'x') and hasattr(obj.position, 'y'):
            x = obj.position.x if obj.position.x is not None else 0
            y = obj.position.y if obj.position.y is not None else 0
            return x, y
        else:
            return 0, 0

    def _set_position_coords(self, obj: SceneObject, x: float = None, y: float = None):
        """Set (x, y) coordinates on position regardless of format"""
        if not obj or not obj.position:
            return
        if isinstance(obj.position, dict):
            if x is not None:
                obj.position['x'] = x
            if y is not None:
                obj.position['y'] = y
        elif hasattr(obj.position, 'x') and hasattr(obj.position, 'y'):
            if x is not None:
                obj.position.x = x
            if y is not None:
                obj.position.y = y

    def _safe_coord(self, obj: SceneObject, key: str, fallback: float) -> float:
        """Safely get coordinate from position (x or y)"""
        if not obj or not obj.position:
            return fallback
        if isinstance(obj.position, dict):
            value = obj.position.get(key, fallback)
        elif hasattr(obj.position, key):
            value = getattr(obj.position, key, fallback)
        else:
            return fallback

        if value in (None, "", []):
            return fallback
        return float(value)

    def _safe_dimension(self, obj: SceneObject, key: str, fallback: float) -> float:
        """Safely get dimension from properties (width or height)"""
        if not obj or not obj.properties:
            return fallback
        value = obj.properties.get(key, fallback)
        if value in (None, "", []):
            return fallback
        try:
            return float(value)
        except (ValueError, TypeError):
            return fallback

    def solve(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """
        Solve layout for scene

        Pipeline:
        1. Domain-aware initial placement
        2. Iterative constraint satisfaction (max 50 iterations)
        3. Aesthetic optimization (spacing, alignment)
        4. Intelligent label placement
        5. Final validation

        Args:
            scene: Scene with objects and constraints (positions may be None)
            spec: Problem specification for domain context

        Returns:
            Scene with all positions determined
        """
        print(f"\n{'='*80}")
        print(f"📐 UNIVERSAL LAYOUT ENGINE - Phase 4")
        print(f"{'='*80}\n")

        # Step 1: Domain-aware initial placement (only for objects without positions)
        print("Step 1/6: Domain-Aware Initial Placement")
        self._initial_placement(scene, spec)
        print(f"   ✅ Positioned {len(scene.objects)} objects")

        # Step 2: Advanced constraint solvers
        print("\nStep 2/6: Advanced Constraint Solvers (Z3/SymPy/Cassowary)")
        solver_report = self._apply_advanced_constraint_solvers(scene, spec)
        if solver_report:
            print(f"   ⚙️  Applied solvers: {', '.join(solver_report)}")
        else:
            print("   ℹ️  No advanced solver applied")

        # Step 3: Iterative constraint satisfaction
        print("\nStep 3/6: Iterative Constraint Satisfaction")
        iterations = self._solve_constraints(scene)
        print(f"   ✅ Converged in {iterations} iterations")

        # Step 4: Aesthetic optimization
        print("\nStep 4/6: Aesthetic Optimization")
        self._optimize_aesthetics(scene, spec)
        print(f"   ✅ Optimized spacing and alignment")

        # Step 5: Intelligent label placement
        print("\nStep 5/6: Intelligent Label Placement")
        self._place_labels(scene)
        print(f"   ✅ Placed labels with overlap avoidance")

        # Step 6: Final validation
        print("\nStep 6/6: Layout Validation")
        valid, issues = self._validate_layout(scene)
        if valid:
            print(f"   ✅ Layout is valid")
        else:
            print(f"   ⚠️  Layout issues: {', '.join(issues)}")

        print(f"\n{'='*80}")
        print(f"✅ UNIVERSAL LAYOUT ENGINE COMPLETE")
        print(f"{'='*80}\n")

        return scene

    def _initial_placement(self, scene: Scene, spec: CanonicalProblemSpec):
        """Step 1: Smart initial positioning based on domain"""

        domain = spec.domain

        if domain == PhysicsDomain.ELECTROSTATICS:
            self._place_electrostatics(scene, spec)

        elif domain == PhysicsDomain.CURRENT_ELECTRICITY:
            self._place_circuit(scene, spec)

        elif domain == PhysicsDomain.MECHANICS:
            self._place_mechanics(scene, spec)

        elif domain == PhysicsDomain.THERMODYNAMICS:
            self._place_thermodynamics(scene, spec)

        elif domain == PhysicsDomain.OPTICS:
            self._place_optics(scene, spec)

        else:
            # Generic grid layout
            self._place_generic_grid(scene)

    def _place_electrostatics(self, scene: Scene, spec: CanonicalProblemSpec):
        """
        Place electrostatics objects from constraints (GENERIC SOLUTION)

        Uses PARALLEL + DISTANCE constraints to position objects correctly.
        For parallel-plate capacitors:
        - PARALLEL constraint → plates face each other (vertical stacking)
        - DISTANCE constraint → gap between plates
        """

        # Check if this is a capacitor problem (plates present)
        plates = [obj for obj in scene.objects if 'plate' in obj.id.lower()]
        charges = [obj for obj in scene.objects if 'charge' in obj.type.value.lower()]
        field_lines = [obj for obj in scene.objects if 'field' in obj.id.lower() or 'field' in obj.type.value.lower()]
        dielectrics = [obj for obj in scene.objects if 'dielectric' in obj.id.lower()]

        if plates:
            # GENERIC CONSTRAINT-BASED POSITIONING
            # Extract plate dimensions from properties
            plate_width = plates[0].properties.get('width', 400)
            plate_height = plates[0].properties.get('height', 12)

            # Find DISTANCE constraint for plate separation
            plate_separation = 180  # Default
            for constraint in scene.constraints:
                if constraint.type == ConstraintType.DISTANCE and 'plate' in str(constraint.objects):
                    if constraint.value:
                        plate_separation = constraint.value
                        print(f"   📏 Using DISTANCE constraint: {plate_separation}px separation")
                        break

            if len(plates) == 2:
                # GENERIC SOLUTION: Parallel plates in physics → vertical stacking
                # Top plate above center, bottom plate below center
                plate1_y = self.center[1] - plate_separation / 2 - plate_height
                plate2_y = self.center[1] + plate_separation / 2

                # Use properties for dimensions, not hard-coded
                plates[0].position = {
                    'x': self.center[0] - plate_width / 2,  # Centered horizontally
                    'y': plate1_y,                           # Above center
                    'anchor': 'top-left'
                }
                plates[1].position = {
                    'x': self.center[0] - plate_width / 2,  # Centered horizontally
                    'y': plate2_y,                           # Below center
                    'anchor': 'top-left'
                }

                print(f"   📍 Positioned plates VERTICALLY:")
                print(f"      {plates[0].id}: y={plate1_y:.1f} (top)")
                print(f"      {plates[1].id}: y={plate2_y:.1f} (bottom)")
                print(f"      Separation: {plate_separation}px")

            # GENERIC SOLUTION: Apply BETWEEN constraints during initial placement
            # This gives dielectrics initial positions so ADJACENT and STACKED_V can refine them
            print(f"   📐 Applying BETWEEN constraints for dielectric positioning...")

            # Apply BETWEEN constraints to position dielectrics between plates
            for constraint in scene.constraints:
                if constraint.type == ConstraintType.BETWEEN and any('dielectric' in obj_id for obj_id in constraint.objects):
                    self._apply_between_constraint(scene, constraint)

            # Place field lines between plates (vertical arrows pointing down)
            if field_lines:
                num_lines = len(field_lines)
                for i, field_line in enumerate(field_lines):
                    # Distribute evenly between plates
                    x_pos = self.center[0] - plate_separation/3 + (i * plate_separation * 0.66 / max(num_lines-1, 1))
                    field_line.position = {
                        'x': x_pos,
                        'y': self.center[1],
                        'length': 60,
                        'angle': 90  # Pointing downward
                    }

        else:
            # Standard charge layout
            # Arrange charges in optimal pattern
            if len(charges) == 1:
                # Single charge at center
                charges[0].position = {'x': self.center[0], 'y': self.center[1]}

            elif len(charges) == 2:
                # Two charges: horizontal line
                spacing = min(self.width, self.height) * 0.4
                charges[0].position = {'x': self.center[0] - spacing/2, 'y': self.center[1]}
                charges[1].position = {'x': self.center[0] + spacing/2, 'y': self.center[1]}

            else:
                # Multiple charges: circle arrangement
                radius = min(self.width, self.height) * 0.3
                for i, charge in enumerate(charges):
                    angle = 2 * math.pi * i / len(charges)
                    charge.position = {
                        'x': self.center[0] + radius * math.cos(angle),
                        'y': self.center[1] + radius * math.sin(angle)
                    }

        # Place remaining objects at center
        placed_ids = {obj.id for obj in plates + charges + field_lines + dielectrics}
        for obj in scene.objects:
            if obj.id not in placed_ids and not obj.position:
                obj.position = {'x': self.center[0], 'y': self.center[1]}

    def _place_circuit(self, scene: Scene, spec: CanonicalProblemSpec):
        """Place circuit objects (battery, resistors, capacitors, wires)"""

        components = [obj for obj in scene.objects if obj.type in [PrimitiveType.BATTERY_SYMBOL, PrimitiveType.RESISTOR_SYMBOL, PrimitiveType.CAPACITOR_SYMBOL]]
        
        # Simple rectangular layout
        if not components: return

        x = self.center[0] - 200
        y = self.center[1] - 150
        width = 400
        height = 300

        # Place components along the rectangle
        if len(components) == 1:
            components[0].position = {'x': self.center[0], 'y': y}
        elif len(components) == 2:
            components[0].position = {'x': x, 'y': self.center[1]}
            components[1].position = {'x': x + width, 'y': self.center[1]}
        elif len(components) == 3:
            components[0].position = {'x': self.center[0], 'y': y}
            components[1].position = {'x': x, 'y': self.center[1]}
            components[2].position = {'x': x + width, 'y': self.center[1]}
        else:
            # Distribute components along the 4 sides
            side_len = len(components) // 4
            for i, comp in enumerate(components):
                if i < side_len: # Top
                    comp.position = {'x': x + (i + 1) * width / (side_len + 1), 'y': y}
                elif i < 2 * side_len: # Right
                    comp.position = {'x': x + width, 'y': y + (i - side_len + 1) * height / (side_len + 1)}
                elif i < 3 * side_len: # Bottom
                    comp.position = {'x': x + width - (i - 2 * side_len + 1) * width / (side_len + 1), 'y': y + height}
                else: # Left
                    comp.position = {'x': x, 'y': y + height - (i - 3 * side_len + 1) * height / (side_len + 1)}

    def _place_mechanics(self, scene: Scene, spec: CanonicalProblemSpec):
        """Place mechanics objects (masses, forces, surfaces)"""

        surfaces = [obj for obj in scene.objects if obj.type == PrimitiveType.LINE and 'surface' in obj.id]
        masses = [obj for obj in scene.objects if obj.type == PrimitiveType.MASS]

        # Place surfaces first
        for i, surface in enumerate(surfaces):
            if not surface.position:
                surface.position = {
                    'x': self.margin,
                    'y': self.height - self.margin - 50 * (i + 1),
                    'width': self.width - 2 * self.margin,
                    'height': 5
                }

        # Place masses on surfaces
        for mass in masses:
            if not mass.position:
                # Find the surface this mass is on
                surface = next((s for s in surfaces if any(r.get('subject') == mass.id and r.get('target') == s.id for r in spec.relationships)), None)
                if surface and surface.position:
                    surface_y = surface.position.get('y') or self.center[1]
                    mass.position = {
                        'x': self.center[0],
                        'y': surface_y - mass.properties.get('height', 50) / 2
                    }
                else:
                    # Default placement if no surface
                    mass.position = {'x': self.center[0], 'y': self.center[1]}

    def _place_thermodynamics(self, scene: Scene, spec: CanonicalProblemSpec):
        """Place thermodynamics objects (PV diagrams, gas states)"""

        # For PV diagrams, use centered layout
        for i, obj in enumerate(scene.objects):
            if not obj.position:
                obj.position = {
                    'x': self.center[0],
                    'y': self.center[1] + i * 50 - (len(scene.objects)-1) * 25
                }

    def _place_optics(self, scene: Scene, spec: CanonicalProblemSpec):
        """Place optics objects (lenses, mirrors, rays)"""

        # Add principal axis if it doesn't exist
        if not any(obj.type == PrimitiveType.LINE and obj.id == 'principal_axis' for obj in scene.objects):
            scene.objects.append(SceneObject(
                id='principal_axis',
                type=PrimitiveType.LINE,
                properties={
                    'start': {'x': self.margin, 'y': self.center[1]},
                    'end': {'x': self.width - self.margin, 'y': self.center[1]}
                }
            ))

        # Place lens/mirror at the center
        lens_or_mirror = next((obj for obj in scene.objects if obj.type in [PrimitiveType.LENS]), None)
        if lens_or_mirror and not lens_or_mirror.position:
            lens_or_mirror.position = {'x': self.center[0], 'y': self.center[1]}

        # Place other objects relative to the lens/mirror
        for obj in scene.objects:
            if obj.position:
                continue

            if obj.type == PrimitiveType.FOCAL_POINT:
                parent = self._get_obj(scene, obj.properties.get('parent'))
                if parent and parent.position:
                    distance = obj.properties.get('distance', 0)
                    parent_x = parent.position.get('x') or self.center[0]
                    parent_y = parent.position.get('y') or self.center[1]
                    obj.position = {'x': parent_x + distance, 'y': parent_y}
            elif obj.properties.get('is_object'):
                # Place object to the left of the lens
                obj.position = {'x': self.center[0] - 200, 'y': self.center[1] - 50}
            elif obj.properties.get('is_image'):
                # Place image to the right of the lens
                obj.position = {'x': self.center[0] + 200, 'y': self.center[1] + 50}
            else:
                # Generic placement for other objects
                obj.position = {'x': self.center[0], 'y': self.center[1]}

    def _place_generic_grid(self, scene: Scene):
        """Generic grid layout for unknown domains"""

        n = len(scene.objects)
        cols = math.ceil(math.sqrt(n))

        for i, obj in enumerate(scene.objects):
            if not obj.position:
                row = i // cols
                col = i % cols
                spacing_x = (self.width - 2 * self.margin) / (cols + 1)
                spacing_y = (self.height - 2 * self.margin) / (cols + 1)

                obj.position = {
                    'x': self.margin + spacing_x * (col + 1),
                    'y': self.margin + spacing_y * (row + 1)
                }

    def _solve_constraints(self, scene: Scene) -> int:
        """Step 2: Iterative constraint satisfaction"""

        max_iterations = 50
        tolerance = 1e-3

        for iteration in range(max_iterations):
            converged = True

            for constraint in scene.constraints:
                moved = self._apply_constraint(scene, constraint)
                if moved > tolerance:
                    converged = False

            if converged:
                return iteration + 1

        return max_iterations

    def _apply_advanced_constraint_solvers(self, scene: Scene, spec: CanonicalProblemSpec) -> List[str]:
        """Apply Z3, SymPy, Cassowary passes if available"""
        applied: List[str] = []
        plan = getattr(spec, 'diagram_plan', None)
        plan_constraints = getattr(plan, 'global_constraints', None) or []
        sympy_constraints = self._collect_sympy_constraints(scene, plan)
        cassowary_required = any(
            constraint.type in (
                ConstraintType.ALIGNED_H,
                ConstraintType.ALIGNED_V,
                ConstraintType.LEFT_OF,
                ConstraintType.RIGHT_OF,
                ConstraintType.ABOVE,
                ConstraintType.BELOW,
                ConstraintType.STACKED_H,
                ConstraintType.STACKED_V
            ) and len(constraint.objects or []) >= 2
            for constraint in scene.constraints
        )

        # Z3 via diagram plan constraints
        if plan_constraints:
            if self.z3_solver:
                try:
                    object_dims = self._estimate_object_dimensions(scene)
                    solution = self.z3_solver.solve_layout(plan, object_dims)
                    if solution and getattr(solution, 'satisfiable', False):
                        self._apply_positions_dict(scene, solution.positions)
                        applied.append('z3')
                except Exception as exc:
                    print(f"   ⚠️  Z3 solver error: {exc}")
            else:
                self._warn_solver_unavailable('Z3', 'install z3-solver to enforce formal constraints')

        # SymPy solver for geometric constraints
        if sympy_constraints:
            if self.sympy_solver:
                try:
                    object_ids = [obj.id for obj in scene.objects]
                    solution = self.sympy_solver.solve_geometric_constraints(sympy_constraints, object_ids)
                    if solution and getattr(solution, 'satisfiable', False):
                        positions = self._sympy_solution_to_positions(solution)
                        if positions:
                            self._apply_positions_dict(scene, positions)
                            applied.append('sympy')
                except Exception as exc:
                    print(f"   ⚠️  SymPy solver error: {exc}")
            else:
                self._warn_solver_unavailable('SymPy', 'install sympy for geometric solving')

        # Cassowary/kiwi pass for alignment/relative constraints
        if self.cassowary_solver_cls:
            try:
                if self._run_cassowary_solver(scene):
                    applied.append('cassowary')
            except Exception as exc:
                print(f"   ⚠️  Cassowary solver error: {exc}")
        elif cassowary_required:
            self._warn_solver_unavailable('Cassowary', 'install cassowary to honor alignment constraints')

        return applied

    def _warn_solver_unavailable(self, solver_name: str, hint: str) -> None:
        """Print a single warning per solver when dependency is missing"""
        if solver_name in self._solver_warning_cache:
            return
        self._solver_warning_cache[solver_name] = hint
        print(f"   ⚠️  {solver_name} solver unavailable – {hint}")

    def _apply_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """Apply single constraint, return max displacement"""

        max_displacement = 0.0

        if constraint.type == ConstraintType.ALIGNED_H:
            # SKIP if there's a DISTANCE constraint between any pair of these objects
            # (DISTANCE takes precedence - objects should maintain separation)
            has_distance_constraint = False
            for other_constraint in scene.constraints:
                if other_constraint.type == ConstraintType.DISTANCE:
                    # Check if any two objects from ALIGNED_H are in the DISTANCE constraint
                    distance_objs = set(other_constraint.objects)
                    aligned_objs = set(constraint.objects)
                    if len(distance_objs & aligned_objs) >= 2:
                        has_distance_constraint = True
                        break

            if has_distance_constraint:
                print(f"      ⏭️  Skipping ALIGNED_H constraint (conflicts with DISTANCE constraint)")
                return 0.0

            # Guard against missing objects
            objects = self._get_objects(scene, constraint.objects)
            if not objects: return 0.0

            # Align horizontally (same y)
            if constraint.objects:
                positions = [obj.position for obj in objects if obj.position]
                if not positions: return 0.0
                avg_y = sum(p.get('y', 0) for p in positions) / len(positions)

                for oid in constraint.objects:
                    obj = self._get_obj(scene, oid)
                    if not obj or not obj.position:
                        continue
                    old_y = obj.position.get('y', 0) if isinstance(obj.position, dict) else getattr(obj.position, 'y', 0)
                    if isinstance(obj.position, dict):
                        obj.position['y'] = avg_y
                    else:
                        obj.position.y = avg_y
                    max_displacement = max(max_displacement, abs(avg_y - old_y))

        elif constraint.type == ConstraintType.ALIGNED_V:
            # Guard against missing objects
            objects = self._get_objects(scene, constraint.objects)
            if not objects: return 0.0

            # Align vertically (same x)
            if constraint.objects:
                positions = [obj.position for obj in objects if obj.position]
                if not positions: return 0.0
                avg_x = sum(p.get('x', 0) for p in positions) / len(positions)

                for oid in constraint.objects:
                    obj = self._get_obj(scene, oid)
                    if not obj or not obj.position:
                        continue
                    old_x = obj.position.get('x', 0) if isinstance(obj.position, dict) else getattr(obj.position, 'x', 0)
                    if isinstance(obj.position, dict):
                        obj.position['x'] = avg_x
                    else:
                        obj.position.x = avg_x
                    max_displacement = max(max_displacement, abs(avg_x - old_x))

        elif constraint.type == ConstraintType.COINCIDENT:
            # Make object centers coincide
            objects = self._get_objects(scene, constraint.objects)
            if not objects: return 0.0

            positions = [obj.position for obj in objects if obj.position]
            if not positions: return 0.0
            avg_x = sum(p.get('x', 0) for p in positions) / len(positions)
            avg_y = sum(p.get('y', 0) for p in positions) / len(positions)

            for obj in objects:
                if obj.position:
                    obj.position['x'] = avg_x
                    obj.position['y'] = avg_y

        elif constraint.type == ConstraintType.DISTANCE:
            # SKIP: Distance constraints already handled in Step 1 (domain-aware placement)
            # Applying them here causes double-scaling issues (constraint value * scene scale)
            print(f"      ⏭️  Skipping DISTANCE constraint (already applied in initial placement)")
            return 0.0

        # FIX: Implement missing constraints
        elif constraint.type == ConstraintType.COLLINEAR:
            objects = self._get_objects(scene, constraint.objects)
            if len(objects) < 2: return 0.0
            
            # Simple horizontal or vertical alignment for now
            positions = [obj.position for obj in objects if obj.position]
            if not positions: return 0.0
            
            avg_y = sum(p.get('y', 0) for p in positions) / len(positions)
            for obj in objects:
                if obj.position:
                    old_y = obj.position.get('y', 0)
                    obj.position['y'] = avg_y
                    max_displacement = max(max_displacement, abs(avg_y - old_y))

        elif constraint.type == ConstraintType.PARALLEL:
            # Make two objects parallel (same orientation, NOT same position)
            # FIX: For capacitor plates, PARALLEL means they face each other (same X, same width)
            # but maintain DIFFERENT Y positions (separation maintained by DISTANCE constraint)
            if len(constraint.objects) >= 2:
                objects = self._get_objects(scene, constraint.objects)
                if len(objects) < 2: return 0.0

                # For rectangles/plates: align horizontally (same X) but keep Y separation
                positions = [obj.position for obj in objects if obj.position]
                if not positions: return 0.0

                # Align X positions (horizontal alignment)
                avg_x = sum(p.get('x', 0) for p in positions) / len(positions)

                for obj in objects:
                    if obj.position:
                        old_x = obj.position.get('x', 0)
                        obj.position['x'] = avg_x
                        max_displacement = max(max_displacement, abs(avg_x - old_x))
                        # DO NOT modify Y position - that's maintained by DISTANCE constraint

        elif constraint.type == ConstraintType.PERPENDICULAR:
            # Make two objects perpendicular to each other
            if len(constraint.objects) == 2:
                objects = self._get_objects(scene, constraint.objects)
                if len(objects) != 2: return 0.0
                obj1, obj2 = objects
                if not obj1.position or not obj2.position: return 0.0

                # Simple implementation for perpendicular:
                # If obj1 is horizontal (width > height), make obj2 vertical (center alignment)
                # If obj1 is vertical, make obj2 horizontal

                # For most physics diagrams: principal axis is horizontal, lens/mirror is vertical
                # Ensure obj2 is centered on obj1's position
                obj1_x, obj1_y = self._get_position_coords(obj1)
                obj2_x, obj2_y = self._get_position_coords(obj2)
                if obj1_x and obj2_x:
                    self._set_position_coords(obj2, x=obj1_x, y=obj1_y)
                    max_displacement = max(max_displacement, abs(obj1_x - obj2_x), abs(obj1_y - obj2_y))

        elif constraint.type == ConstraintType.SYMMETRIC:
            if len(constraint.objects) == 2 and constraint.value:
                obj1, obj2 = self._get_objects(scene, constraint.objects)
                center_obj = self._get_obj(scene, str(constraint.value))

                if not all([obj1, obj2, center_obj]) or not all([obj1.position, obj2.position, center_obj.position]):
                    return 0.0

                center_x, _ = self._get_position_coords(center_obj)
                if center_x == 0:
                    center_x = self.center[0]

                # Make obj1 and obj2 equidistant from the center object's x-position
                obj1_x, _ = self._get_position_coords(obj1)
                obj2_x, _ = self._get_position_coords(obj2)
                dist1 = center_x - obj1_x
                dist2 = obj2_x - center_x
                avg_dist = (dist1 + dist2) / 2

                self._set_position_coords(obj1, x=center_x - avg_dist)
                self._set_position_coords(obj2, x=center_x + avg_dist)

        elif constraint.type == ConstraintType.NO_OVERLAP:
            # Resolve overlaps by pushing apart
            for i, oid1 in enumerate(constraint.objects):
                for oid2 in constraint.objects[i+1:]:
                    obj1 = self._get_obj(scene, oid1)
                    obj2 = self._get_obj(scene, oid2)

                    if self._check_overlap(obj1, obj2):
                        # Push apart along shortest axis
                        dx, dy = self._resolve_overlap(obj1, obj2)
                        # Handle both dict and Position object formats
                        try:
                            if isinstance(obj2.position, dict):
                                if 'x' in obj2.position and 'y' in obj2.position:
                                    # Handle None values
                                    obj2.position['x'] = (obj2.position.get('x') or 0) + dx
                                    obj2.position['y'] = (obj2.position.get('y') or 0) + dy
                            elif hasattr(obj2.position, 'x') and hasattr(obj2.position, 'y'):
                                obj2.position.x = (obj2.position.x if obj2.position.x is not None else 0) + dx
                                obj2.position.y = (obj2.position.y if obj2.position.y is not None else 0) + dy
                            max_displacement = max(max_displacement, abs(dx), abs(dy))
                        except (KeyError, AttributeError) as e:
                            # Skip if position format is incompatible
                            pass

        elif constraint.type == ConstraintType.CONNECTED:
            # Simple connection: pull objects closer.
            # A full implementation would use graph-based layout for circuits.
            if len(constraint.objects) == 2:
                obj1, obj2 = self._get_objects(scene, constraint.objects)
                if not all([obj1, obj2]) or not all([obj1.position, obj2.position]):
                    return 0.0

                # For now, just reduce distance between them slightly if they are far apart
                dist = self._distance(obj1, obj2)
                target_dist = 50 # Target pixel distance for connected objects
                if dist > target_dist:
                    # Move obj2 towards obj1
                    obj1_x, obj1_y = self._get_position_coords(obj1)
                    obj2_x, obj2_y = self._get_position_coords(obj2)
                    vec = (obj1_x - obj2_x, obj1_y - obj2_y)
                    self._set_position_coords(obj2, x=obj2_x + vec[0] * 0.1, y=obj2_y + vec[1] * 0.1)

        # GENERIC SPATIAL CONSTRAINTS (for universal positioning)
        elif constraint.type == ConstraintType.BETWEEN:
            # SKIP: BETWEEN constraints already applied in Step 1 (initial placement)
            print(f"      ⏭️  Skipping BETWEEN constraint (already applied in initial placement)")
            return 0.0

        elif constraint.type == ConstraintType.ADJACENT:
            # obj1 and obj2 touch with no gap
            return self._apply_adjacent_constraint(scene, constraint)

        elif constraint.type == ConstraintType.ABOVE:
            # obj1 is above obj2
            return self._apply_above_constraint(scene, constraint)

        elif constraint.type == ConstraintType.BELOW:
            # obj1 is below obj2
            return self._apply_below_constraint(scene, constraint)

        elif constraint.type == ConstraintType.LEFT_OF:
            # obj1 is left of obj2
            return self._apply_left_of_constraint(scene, constraint)

        elif constraint.type == ConstraintType.RIGHT_OF:
            # obj1 is right of obj2
            return self._apply_right_of_constraint(scene, constraint)

        elif constraint.type == ConstraintType.STACKED_V:
            # Stack objects vertically (top to bottom)
            return self._apply_stacked_v_constraint(scene, constraint)

        elif constraint.type == ConstraintType.STACKED_H:
            # Stack objects horizontally (left to right)
            return self._apply_stacked_h_constraint(scene, constraint)

        return max_displacement

    def _optimize_aesthetics(self, scene: Scene, spec: CanonicalProblemSpec):
        """Step 3: Optimize for visual appeal"""

        # Snap to grid for clean appearance
        grid_size = 10
        for obj in scene.objects:
            if obj.position and 'x' in obj.position and 'y' in obj.position:
                # Handle None values
                x = obj.position.get('x') or 0
                y = obj.position.get('y') or 0
                obj.position['x'] = round(x / grid_size) * grid_size
                obj.position['y'] = round(y / grid_size) * grid_size

        # DISABLED: Minimum spacing enforcement breaks constraint-based layouts
        # For capacitors and other physics diagrams, objects are intentionally close
        # The constraint solver already handles spacing through ADJACENT, DISTANCE, etc.
        # Forcing additional spacing here destroys carefully constructed layouts

        # # Ensure minimum spacing
        # min_spacing = 30
        # for i, obj1 in enumerate(scene.objects):
        #     for obj2 in scene.objects[i+1:]:
        #         dist = self._distance(obj1, obj2)
        #         if dist < min_spacing:
        #             # Push apart slightly
        #             x1, y1 = obj1.position.get('x', 0), obj1.position.get('y', 0)
        #             x2, y2 = obj2.position.get('x', 0), obj2.position.get('y', 0)
        #
        #             if x1 != x2 or y1 != y2:
        #                 angle = math.atan2(y2 - y1, x2 - x1)
        #                 push = (min_spacing - dist) / 2
        #                 obj2.position['x'] += push * math.cos(angle)
        #                 obj2.position['y'] += push * math.sin(angle)

    def _place_labels(self, scene: Scene):
        """Step 4: Intelligent label placement"""

        if self.label_placer:
            try:
                self.label_placer.place_labels(scene)
                return
            except Exception as exc:
                print(f"   ⚠️  IntelligentLabelPlacer failed: {exc}")

        # For each object with a label, find best position (N, NE, E, SE, S, SW, W, NW)
        for obj in scene.objects:
            label = obj.properties.get('label')
            if label and obj.position:
                # Try 8 candidate positions
                candidates = [
                    ('N', 0, -30),
                    ('NE', 20, -20),
                    ('E', 30, 0),
                    ('SE', 20, 20),
                    ('S', 0, 30),
                    ('SW', -20, 20),
                    ('W', -30, 0),
                    ('NW', -20, -20)
                ]

                # Find position with least overlap
                best_pos = candidates[0]
                min_overlap = float('inf')

                for direction, dx, dy in candidates:
                    obj_x, obj_y = self._get_position_coords(obj)
                    label_x = obj_x + dx
                    label_y = obj_y + dy

                    # Check overlap with other objects
                    overlap = self._count_label_overlaps(label_x, label_y, scene.objects, obj)

                    if overlap < min_overlap:
                        min_overlap = overlap
                        best_pos = (direction, dx, dy)

                # Store label position
                _, dx, dy = best_pos
                obj_x, obj_y = self._get_position_coords(obj)
                obj.properties['label_position'] = {
                    'x': obj_x + dx,
                    'y': obj_y + dy
                }

    def _validate_layout(self, scene: Scene) -> Tuple[bool, List[str]]:
        """Step 5: Validate final layout"""

        issues = []

        # Check all objects have positions
        for obj in scene.objects:
            if not obj.position or 'x' not in obj.position or 'y' not in obj.position:
                issues.append(f"Object {obj.id} missing position")

        # Check within bounds
        for obj in scene.objects:
            if obj.position:
                x = obj.position.get('x', 0)
                y = obj.position.get('y', 0)

                if x < self.margin or x > self.width - self.margin:
                    issues.append(f"Object {obj.id} outside horizontal bounds")
                if y < self.margin or y > self.height - self.margin:
                    issues.append(f"Object {obj.id} outside vertical bounds")

        return len(issues) == 0, issues

    def _estimate_object_dimensions(self, scene: Scene) -> Dict[str, Tuple[float, float]]:
        dimensions: Dict[str, Tuple[float, float]] = {}
        for obj in scene.objects:
            width = obj.properties.get('width')
            height = obj.properties.get('height')
            if width is None or height is None:
                prim_type = getattr(obj, 'type', None)
                if prim_type == PrimitiveType.CIRCLE or (isinstance(prim_type, str) and 'circle' in prim_type.lower()):
                    radius = obj.properties.get('radius', 40)
                    width = height = radius * 2
                elif prim_type == PrimitiveType.RECTANGLE or (isinstance(prim_type, str) and 'rect' in prim_type.lower()):
                    width = obj.properties.get('width', 120)
                    height = obj.properties.get('height', 60)
                else:
                    width = width or 100
                    height = height or 80
            dimensions[obj.id] = (float(width), float(height))
        return dimensions

    def _apply_positions_dict(self, scene: Scene, positions: Dict[str, Tuple[float, float]]):
        if not positions:
            return
        for obj in scene.objects:
            coords = positions.get(obj.id)
            if not coords:
                continue
            x, y = coords
            if obj.position is None:
                obj.position = {'x': float(x), 'y': float(y)}
            elif isinstance(obj.position, dict):
                obj.position['x'] = float(x)
                obj.position['y'] = float(y)
            else:
                obj.position.x = float(x)
                obj.position.y = float(y)

    def _collect_sympy_constraints(self, scene: Scene, plan: Any) -> List[Dict[str, Any]]:
        constraints: List[Dict[str, Any]] = []
        for constraint in scene.constraints:
            if constraint.type == ConstraintType.DISTANCE and len(constraint.objects) >= 2:
                constraints.append({
                    'type': 'DISTANCE',
                    'object1': constraint.objects[0],
                    'object2': constraint.objects[1],
                    'distance': constraint.value or 100
                })
            elif constraint.type == ConstraintType.ALIGNED_H and len(constraint.objects) >= 2:
                for i in range(len(constraint.objects) - 1):
                    constraints.append({
                        'type': 'ALIGN_HORIZONTAL',
                        'object1': constraint.objects[i],
                        'object2': constraint.objects[i + 1]
                    })
            elif constraint.type == ConstraintType.ALIGNED_V and len(constraint.objects) >= 2:
                for i in range(len(constraint.objects) - 1):
                    constraints.append({
                        'type': 'ALIGN_VERTICAL',
                        'object1': constraint.objects[i],
                        'object2': constraint.objects[i + 1]
                    })

        if plan and hasattr(plan, 'layout_hints'):
            hints = getattr(plan, 'layout_hints', {}) or {}
            for obj_id, coords in hints.get('positions', {}).items():
                if isinstance(coords, dict):
                    constraints.append({
                        'type': 'FIXED_POSITION',
                        'object': obj_id,
                        'x': coords.get('x'),
                        'y': coords.get('y')
                    })

        return constraints

    def _sympy_solution_to_positions(self, solution) -> Dict[str, Tuple[float, float]]:
        positions: Dict[str, List[Optional[float]]] = {}
        for var_name, value in getattr(solution, 'variables', {}).items():
            if not isinstance(var_name, str):
                continue
            if not isinstance(value, (int, float)):
                continue
            if var_name.endswith('_x'):
                obj_id = var_name[:-2]
                positions.setdefault(obj_id, [None, None])[0] = float(value)
            elif var_name.endswith('_y'):
                obj_id = var_name[:-2]
                positions.setdefault(obj_id, [None, None])[1] = float(value)
        finalized = {}
        for obj_id, (x, y) in positions.items():
            if x is not None and y is not None:
                finalized[obj_id] = (x, y)
        return finalized

    def _run_cassowary_solver(self, scene: Scene) -> bool:
        if not self.cassowary_solver_cls or Variable is None:
            return False

        solver = self.cassowary_solver_cls()
        x_vars: Dict[str, Any] = {}
        y_vars: Dict[str, Any] = {}

        for obj in scene.objects:
            var_x = Variable(f"{obj.id}_x")
            var_y = Variable(f"{obj.id}_y")
            x_vars[obj.id] = var_x
            y_vars[obj.id] = var_y
            solver.add_stay(var_x)
            solver.add_stay(var_y)
            if obj.position:
                solver.add_edit_var(var_x)
                solver.add_edit_var(var_y)
                solver.suggest_value(var_x, obj.position.get('x', 0))
                solver.suggest_value(var_y, obj.position.get('y', 0))

        def _pairs(items: List[str]) -> List[Tuple[str, str]]:
            return [(items[i], items[i + 1]) for i in range(len(items) - 1)]

        added_constraint = False

        for constraint in scene.constraints:
            objs = constraint.objects or []
            if len(objs) < 2:
                continue

            if constraint.type == ConstraintType.ALIGNED_H:
                for a, b in _pairs(objs):
                    if a in y_vars and b in y_vars:
                        solver.add_constraint(y_vars[a] == y_vars[b])
                        added_constraint = True
            elif constraint.type == ConstraintType.ALIGNED_V:
                for a, b in _pairs(objs):
                    if a in x_vars and b in x_vars:
                        solver.add_constraint(x_vars[a] == x_vars[b])
                        added_constraint = True
            elif constraint.type == ConstraintType.LEFT_OF:
                obj_a, obj_b = objs[:2]
                if obj_a in x_vars and obj_b in x_vars:
                    solver.add_constraint(x_vars[obj_a] + 40 <= x_vars[obj_b])
                    added_constraint = True
            elif constraint.type == ConstraintType.RIGHT_OF:
                obj_a, obj_b = objs[:2]
                if obj_a in x_vars and obj_b in x_vars:
                    solver.add_constraint(x_vars[obj_a] >= x_vars[obj_b] + 40)
                    added_constraint = True
            elif constraint.type == ConstraintType.STACKED_V:
                for idx in range(len(objs) - 1):
                    upper = objs[idx]
                    lower = objs[idx + 1]
                    if upper in y_vars and lower in y_vars:
                        solver.add_constraint(y_vars[lower] >= y_vars[upper] + 60)
                        added_constraint = True
            elif constraint.type == ConstraintType.STACKED_H:
                for idx in range(len(objs) - 1):
                    left = objs[idx]
                    right = objs[idx + 1]
                    if left in x_vars and right in x_vars:
                        solver.add_constraint(x_vars[right] >= x_vars[left] + 80)
                        added_constraint = True

        if not added_constraint:
            return False

        solver.solve()

        for obj in scene.objects:
            if obj.id in x_vars and obj.id in y_vars:
                x_val = x_vars[obj.id].value
                y_val = y_vars[obj.id].value
                if obj.position is None:
                    obj.position = {'x': float(x_val), 'y': float(y_val)}
                else:
                    obj.position['x'] = float(x_val)
                    obj.position['y'] = float(y_val)

        return True

    # GENERIC SPATIAL CONSTRAINT SOLVERS

    def _apply_between_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """
        Position obj1 BETWEEN obj2 and obj3

        For capacitor dielectrics: dielectric fills space between top and bottom plates
        General case: obj1 is positioned vertically/horizontally between obj2 and obj3
        """
        if len(constraint.objects) != 3:
            return 0.0

        obj1_id, obj2_id, obj3_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)
        obj3 = self._get_obj(scene, obj3_id)

        if not all([obj1, obj2, obj3]) or not all([obj2.position, obj3.position]):
            return 0.0

        max_displacement = 0.0

        # Determine if this is vertical or horizontal stacking
        obj2_y = obj2.position.get('y', 0)
        obj3_y = obj3.position.get('y', 0)
        obj2_x = obj2.position.get('x', 0)
        obj3_x = obj3.position.get('x', 0)

        # Get object dimensions
        obj1_width = obj1.properties.get('width', 40)
        obj1_height = obj1.properties.get('height', 40)
        obj2_height = obj2.properties.get('height', 12)

        # Vertical stacking (most common for capacitors)
        if abs(obj2_y - obj3_y) > abs(obj2_x - obj3_x):
            # obj1 should start where obj2 ends and fill to where obj3 starts
            top_obj = obj2 if obj2_y < obj3_y else obj3
            bottom_obj = obj3 if obj2_y < obj3_y else obj2

            top_obj_y = top_obj.position.get('y') or self.center[1]
            target_y = top_obj_y + top_obj.properties.get('height', 12)

            # Preserve obj1's X position if it exists (for multi-region capacitors)
            # Otherwise use the plate's X position
            if obj1.position and obj1.position.get('x') is not None:
                target_x = obj1.position.get('x') or self.center[0]
            else:
                target_x = top_obj.position.get('x', self.center[0])

            if obj1.position:
                old_x = obj1.position.get('x', target_x)
                old_y = obj1.position.get('y', 0)
                max_displacement = max(abs(target_x - old_x), abs(target_y - old_y))

            obj1.position = {
                'x': target_x,
                'y': target_y,
                'anchor': 'top-left'
            }

            print(f"      🔗 BETWEEN constraint: {obj1_id} positioned between {obj2_id} and {obj3_id}")
            print(f"         Position: x={target_x:.1f}, y={target_y:.1f}")

        # Horizontal stacking
        else:
            left_obj = obj2 if obj2_x < obj3_x else obj3
            right_obj = obj3 if obj2_x < obj3_x else obj2

            left_obj_x = left_obj.position.get('x') or self.center[0]
            target_x = left_obj_x + left_obj.properties.get('width', 40)
            target_y = left_obj.position.get('y') or self.center[1]

            if obj1.position:
                old_x = obj1.position.get('x', 0)
                old_y = obj1.position.get('y', 0)
                max_displacement = max(abs(target_x - old_x), abs(target_y - old_y))

            obj1.position = {
                'x': target_x,
                'y': target_y,
                'anchor': 'top-left'
            }

        return max_displacement

    def _apply_adjacent_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """
        Make obj1 and obj2 adjacent (touching with no gap)

        For capacitors: left and right dielectrics touch with no gap
        Determines direction based on object dimensions:
        - If heights are similar → horizontal adjacency (side by side)
        - If widths are similar → vertical adjacency (top/bottom)
        """
        if len(constraint.objects) != 2:
            return 0.0

        obj1_id, obj2_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)

        if not all([obj1, obj2]) or not all([obj1.position, obj2.position]):
            return 0.0

        # Get positions and dimensions
        def _safe_coord(position: Dict, key: str, fallback: float) -> float:
            value = position.get(key, fallback)
            if value in (None, "", []):
                return fallback
            return float(value)

        def _safe_dim(properties: Dict, key: str, fallback: float) -> float:
            value = properties.get(key, fallback)
            if value in (None, "", []):
                return fallback
            return float(value)

        obj1_x = _safe_coord(obj1.position, 'x', 0)
        obj1_y = _safe_coord(obj1.position, 'y', 0)
        obj1_width = _safe_dim(obj1.properties, 'width', 40)
        obj1_height = _safe_dim(obj1.properties, 'height', 40)

        obj2_x = _safe_coord(obj2.position, 'x', 0)
        obj2_y = _safe_coord(obj2.position, 'y', 0)
        obj2_width = _safe_dim(obj2.properties, 'width', 40)
        obj2_height = _safe_dim(obj2.properties, 'height', 40)

        max_displacement = 0.0

        # Determine adjacency direction based on current positions and dimensions
        # If at same Y position (or close) → horizontal adjacency (side by side)
        # If at same X position (or close) → vertical adjacency (top/bottom)

        y_diff = abs(obj1_y - obj2_y)
        x_diff = abs(obj1_x - obj2_x)

        # If at same Y position (within 20px tolerance) → horizontal adjacency
        # This is the case for capacitor dielectrics between plates
        if y_diff < 20 or x_diff > 50:  # Same Y level or far apart in X → horizontal
            # Position obj2 to the right of obj1
            target_x = obj1_x + obj1_width
            # DO NOT modify Y - let BETWEEN/STACKED_V constraints handle vertical positioning

            old_x = obj2.position['x']

            # Only move if significantly different (avoid oscillation)
            x_error = abs(target_x - old_x)

            if x_error > 1.0:
                obj2.position['x'] = target_x
                # DO NOT touch Y position - it's controlled by other constraints
                max_displacement = x_error
                print(f"      🔗 ADJACENT constraint: {obj2_id} adjacent to {obj1_id} (horizontal, X only)")
            else:
                max_displacement = 0.0  # Already satisfied

        # Vertical adjacency (stacked top/bottom at same X)
        else:
            target_y = obj1_y + obj1_height
            target_x = obj1_x  # Keep same X position

            old_y = obj2.position['y']
            old_x = obj2.position['x']

            # Only move if significantly different (avoid oscillation)
            y_error = abs(target_y - old_y)
            x_error = abs(target_x - old_x)

            if y_error > 1.0 or x_error > 1.0:
                obj2.position['y'] = target_y
                obj2.position['x'] = target_x
                max_displacement = max(y_error, x_error)
                print(f"      🔗 ADJACENT constraint: {obj2_id} adjacent to {obj1_id} (vertical, same X level)")
            else:
                max_displacement = 0.0  # Already satisfied

        return max_displacement

    def _apply_above_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """obj1 is above obj2"""
        if len(constraint.objects) != 2:
            return 0.0

        obj1_id, obj2_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)

        if not all([obj1, obj2]) or not obj2.position:
            return 0.0

        obj1_height = obj1.properties.get('height', 40)
        obj2_y = obj2.position.get('y', 0)

        # Position obj1 above obj2
        gap = constraint.value if constraint.value else 0  # Gap between objects
        target_y = obj2_y - obj1_height - gap
        target_x = obj2.position.get('x', self.center[0])

        max_displacement = 0.0
        if obj1.position:
            old_y = obj1.position.get('y', 0)
            max_displacement = abs(target_y - old_y)

        obj1.position = {
            'x': target_x,
            'y': target_y,
            'anchor': 'top-left'
        }

        return max_displacement

    def _apply_below_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """obj1 is below obj2"""
        if len(constraint.objects) != 2:
            return 0.0

        obj1_id, obj2_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)

        if not all([obj1, obj2]) or not obj2.position:
            return 0.0

        obj2_height = obj2.properties.get('height', 40)
        obj2_y = obj2.position.get('y', 0)

        # Position obj1 below obj2
        gap = constraint.value if constraint.value else 0
        target_y = obj2_y + obj2_height + gap
        target_x = obj2.position.get('x', self.center[0])

        max_displacement = 0.0
        if obj1.position:
            old_y = obj1.position.get('y', 0)
            max_displacement = abs(target_y - old_y)

        obj1.position = {
            'x': target_x,
            'y': target_y,
            'anchor': 'top-left'
        }

        return max_displacement

    def _apply_left_of_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """obj1 is left of obj2"""
        if len(constraint.objects) != 2:
            return 0.0

        obj1_id, obj2_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)

        if not all([obj1, obj2]) or not obj2.position:
            return 0.0

        obj1_width = obj1.properties.get('width', 40)
        obj2_x = obj2.position.get('x', 0)

        # Position obj1 left of obj2
        gap = constraint.value if constraint.value else 0
        target_x = obj2_x - obj1_width - gap
        target_y = obj2.position.get('y', self.center[1])

        max_displacement = 0.0
        if obj1.position:
            old_x = obj1.position.get('x', 0)
            max_displacement = abs(target_x - old_x)

        obj1.position = {
            'x': target_x,
            'y': target_y,
            'anchor': 'top-left'
        }

        return max_displacement

    def _apply_right_of_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """obj1 is right of obj2"""
        if len(constraint.objects) != 2:
            return 0.0

        obj1_id, obj2_id = constraint.objects
        obj1 = self._get_obj(scene, obj1_id)
        obj2 = self._get_obj(scene, obj2_id)

        if not all([obj1, obj2]) or not obj2.position:
            return 0.0

        obj2_width = obj2.properties.get('width', 40)
        obj2_x = obj2.position.get('x', 0)

        # Position obj1 right of obj2
        gap = constraint.value if constraint.value else 0
        target_x = obj2_x + obj2_width + gap
        target_y = obj2.position.get('y', self.center[1])

        max_displacement = 0.0
        if obj1.position:
            old_x = obj1.position.get('x', 0)
            max_displacement = abs(target_x - old_x)

        obj1.position = {
            'x': target_x,
            'y': target_y,
            'anchor': 'top-left'
        }

        return max_displacement

    def _apply_stacked_v_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """
        Stack objects vertically (top to bottom)
        Objects in constraint.objects list are stacked in order from top to bottom
        """
        if len(constraint.objects) < 2:
            return 0.0

        objects = self._get_objects(scene, constraint.objects)
        if not objects:
            return 0.0

        max_displacement = 0.0

        # First object stays in place (anchor)
        for i in range(1, len(objects)):
            prev_obj = objects[i - 1]
            curr_obj = objects[i]

            if not prev_obj.position:
                continue

            prev_height = self._safe_dimension(prev_obj, 'height', 40)
            prev_y = self._safe_coord(prev_obj, 'y', 0)
            prev_x = self._safe_coord(prev_obj, 'x', self.center[0])

            gap = constraint.value if constraint.value else 0  # Gap between stacked objects
            target_y = prev_y + prev_height + gap
            target_x = prev_x  # Aligned horizontally

            if not curr_obj.position:
                curr_obj.position = {}

            old_y = self._safe_coord(curr_obj, 'y', 0)
            old_x = self._safe_coord(curr_obj, 'x', 0)

            y_error = abs(target_y - old_y)
            x_error = abs(target_x - old_x)

            if y_error > 1.0 or x_error > 1.0:
                curr_obj.position['x'] = target_x
                curr_obj.position['y'] = target_y
                curr_obj.position['anchor'] = 'top-left'
                max_displacement = max(max_displacement, max(y_error, x_error))
                print(f"      📚 STACKED_V: {curr_obj.id} stacked below {prev_obj.id} at y={target_y:.1f}")

        return max_displacement

        return max_displacement

    def _apply_stacked_h_constraint(self, scene: Scene, constraint: Constraint) -> float:
        """
        Stack objects horizontally (left to right)
        Objects in constraint.objects list are stacked in order from left to right
        """
        if len(constraint.objects) < 2:
            return 0.0

        objects = self._get_objects(scene, constraint.objects)
        if not objects:
            return 0.0

        max_displacement = 0.0

        # First object stays in place (anchor)
        for i in range(1, len(objects)):
            prev_obj = objects[i-1]
            curr_obj = objects[i]

            if not prev_obj.position:
                continue

            prev_width = prev_obj.properties.get('width', 40)
            prev_x = prev_obj.position.get('x', 0)
            prev_y = prev_obj.position.get('y', self.center[1])

            gap = constraint.value if constraint.value else 0
            target_x = prev_x + prev_width + gap
            target_y = prev_y  # Aligned vertically

            if curr_obj.position:
                old_x = curr_obj.position.get('x', 0)
                max_displacement = max(max_displacement, abs(target_x - old_x))

            curr_obj.position = {
                'x': target_x,
                'y': target_y,
                'anchor': 'top-left'
            }

        return max_displacement

    # Helper methods

    def _get_obj(self, scene: Scene, obj_id: str) -> Optional[SceneObject]:
        """Get object by ID"""
        # FIX: Add guard for missing objects
        if not obj_id:
            return None
        for obj in scene.objects:
            if obj.id == obj_id:
                return obj
        return None

    def _get_objects(self, scene: Scene, object_ids: List[str]) -> List[SceneObject]:
        """Get multiple objects by a list of IDs, filtering out Nones."""
        return [obj for obj_id in object_ids if (obj := self._get_obj(scene, obj_id)) is not None]


    def _check_overlap(self, obj1: SceneObject, obj2: SceneObject) -> bool:
        """Check if two objects overlap"""
        if not obj1.position or not obj2.position:
            return False

        # Handle None values explicitly (can occur when positions are partially set)
        x1 = obj1.position.get('x') or 0
        y1 = obj1.position.get('y') or 0
        w1 = obj1.position.get('width') or 20
        h1 = obj1.position.get('height') or 20

        x2 = obj2.position.get('x') or 0
        y2 = obj2.position.get('y') or 0
        w2 = obj2.position.get('width') or 20
        h2 = obj2.position.get('height') or 20

        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def _resolve_overlap(self, obj1: SceneObject, obj2: SceneObject) -> Tuple[float, float]:
        """Calculate displacement to resolve overlap"""
        x1 = obj1.position.get('x') or 0
        y1 = obj1.position.get('y') or 0
        x2 = obj2.position.get('x') or 0
        y2 = obj2.position.get('y') or 0

        dx = x2 - x1
        dy = y2 - y1

        if abs(dx) > abs(dy):
            # Push horizontally
            return (20 if dx > 0 else -20, 0)
        else:
            # Push vertically
            return (0, 20 if dy > 0 else -20)

    def _distance(self, obj1: SceneObject, obj2: SceneObject) -> float:
        """Calculate distance between object centers"""
        if not obj1.position or not obj2.position:
            return float('inf')

        x1 = obj1.position.get('x') or 0
        y1 = obj1.position.get('y') or 0
        x2 = obj2.position.get('x') or 0
        y2 = obj2.position.get('y') or 0

        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _count_label_overlaps(self, label_x: float, label_y: float,
                             objects: List[SceneObject], exclude: SceneObject) -> int:
        """Count overlaps for label at given position"""
        overlap_count = 0
        label_size = 30  # Approximate label size

        for obj in objects:
            if obj == exclude or not obj.position:
                continue

            obj_x = obj.position.get('x', 0)
            obj_y = obj.position.get('y', 0)
            obj_w = obj.position.get('width', 20)
            obj_h = obj.position.get('height', 20)

            # Check overlap
            if not (label_x + label_size < obj_x or obj_x + obj_w < label_x or
                   label_y + 15 < obj_y or obj_y + obj_h < label_y):
                overlap_count += 1

        return overlap_count
