"""
Z3 Layout Solver - SMT-Based Constraint Satisfaction for Diagram Layout
Phase 2B of Planning & Reasoning Roadmap

Uses Z3 SMT solver to find optimal diagram layouts that satisfy constraints:
- Canvas bounds
- No overlap
- Distance constraints
- Alignment constraints
- Symmetry constraints

Installation:
    pip install z3-solver

Example:
    solver = Z3LayoutSolver()
    solution = solver.solve_layout(plan)
    if solution.satisfiable:
        positions = solution.positions
"""

from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from core.diagram_plan import DiagramPlan, LayoutConstraint, ConstraintPriority

# Z3 is optional - graceful degradation if not installed
try:
    from z3 import *
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    Z3 = None
    # Define placeholder types when z3 is not available
    Solver = Any  # type: ignore


@dataclass
class LayoutSolution:
    """
    Solution from Z3 layout solver

    Contains:
    - positions: Dict mapping object ID to (x, y) position
    - satisfiable: Whether constraints were satisfiable
    - solve_time: Time taken to solve (seconds)
    - model: Z3 model (if satisfiable)
    """
    positions: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    satisfiable: bool = False
    solve_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    z3_model: Any = None  # Z3 model object

    def get_position(self, object_id: str) -> Optional[Tuple[float, float]]:
        """Get position of an object"""
        return self.positions.get(object_id)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'positions': {k: list(v) for k, v in self.positions.items()},
            'satisfiable': self.satisfiable,
            'solve_time': self.solve_time,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"LayoutSolution(satisfiable={self.satisfiable}, objects={len(self.positions)}, time={self.solve_time:.3f}s)"


class Z3LayoutSolver:
    """
    Z3-based layout solver for diagram generation

    Uses SMT (Satisfiability Modulo Theories) solving to find optimal
    object placements that satisfy all constraints.
    """

    def __init__(self, timeout: int = 30000, verbose: bool = False):
        """
        Initialize Z3 layout solver

        Args:
            timeout: Solver timeout in milliseconds (default: 30000 = 30 seconds)
            verbose: Enable verbose logging

        Raises:
            ImportError: If Z3 is not installed
        """
        if not Z3_AVAILABLE:
            raise ImportError(
                "Z3 is not installed. Install with: pip install z3-solver"
            )

        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

    # ========== Main Solve Method ==========

    def solve_layout(self, plan: DiagramPlan, object_dimensions: Optional[Dict[str, Tuple[float, float]]] = None) -> LayoutSolution:
        """
        Solve layout constraints to find optimal positions

        Args:
            plan: DiagramPlan with constraints
            object_dimensions: Optional dict mapping object ID to (width, height)

        Returns:
            LayoutSolution with positions if satisfiable
        """
        start_time = time.time()

        # Extract object IDs from plan
        object_ids = self._extract_object_ids(plan)

        if not object_ids:
            return LayoutSolution(
                satisfiable=False,
                solve_time=time.time() - start_time,
                metadata={'error': 'No objects to layout'}
            )

        # Use default dimensions if not provided
        if object_dimensions is None:
            object_dimensions = {obj_id: (50.0, 50.0) for obj_id in object_ids}

        # Create solver
        solver = Solver()
        solver.set("timeout", self.timeout)

        # Create variables
        vars = self._create_variables(object_ids, object_dimensions)

        # Add constraints
        constraint_count = 0

        # 1. Canvas bounds constraints
        bounds_constraints = self._add_bounds_constraints(solver, vars, plan)
        constraint_count += bounds_constraints

        # 2. Non-overlap constraints
        overlap_constraints = self._add_overlap_constraints(solver, vars, object_dimensions)
        constraint_count += overlap_constraints

        # 3. Plan-specific constraints
        plan_constraints = self._add_plan_constraints(solver, vars, plan, object_dimensions)
        constraint_count += plan_constraints

        if self.verbose:
            self.logger.info(f"Added {constraint_count} constraints to Z3 solver")

        # Solve
        if self.verbose:
            self.logger.info("Solving constraints with Z3...")

        check_result = solver.check()
        solve_time = time.time() - start_time

        # Process result
        if check_result == sat:
            model = solver.model()
            positions = self._extract_positions(model, vars)

            if self.verbose:
                self.logger.info(f"Solution found in {solve_time:.3f}s")

            return LayoutSolution(
                positions=positions,
                satisfiable=True,
                solve_time=solve_time,
                z3_model=model,
                metadata={
                    'constraint_count': constraint_count,
                    'object_count': len(object_ids)
                }
            )
        elif check_result == unsat:
            if self.verbose:
                self.logger.warning(f"Constraints are unsatisfiable (time: {solve_time:.3f}s)")

            return LayoutSolution(
                satisfiable=False,
                solve_time=solve_time,
                metadata={'reason': 'unsatisfiable', 'constraint_count': constraint_count}
            )
        else:  # unknown
            if self.verbose:
                self.logger.warning(f"Solver timeout or unknown result (time: {solve_time:.3f}s)")

            return LayoutSolution(
                satisfiable=False,
                solve_time=solve_time,
                metadata={'reason': 'timeout', 'constraint_count': constraint_count}
            )

    # ========== Variable Creation ==========

    def _create_variables(self, object_ids: List[str], dimensions: Dict[str, Tuple[float, float]]) -> Dict[str, Dict[str, Any]]:
        """
        Create Z3 variables for each object

        Args:
            object_ids: List of object IDs
            dimensions: Dict mapping object ID to (width, height)

        Returns:
            Dict mapping object ID to variable dict with 'x', 'y', 'width', 'height'
        """
        vars = {}

        for obj_id in object_ids:
            width, height = dimensions.get(obj_id, (50.0, 50.0))

            vars[obj_id] = {
                'x': Real(f'{obj_id}_x'),
                'y': Real(f'{obj_id}_y'),
                'width': width,
                'height': height
            }

        return vars

    # ========== Constraint Addition ==========

    def _add_bounds_constraints(self, solver: Solver, vars: Dict, plan: DiagramPlan) -> int:
        """Add canvas bounds constraints"""
        count = 0

        canvas_width = plan.canvas_width
        canvas_height = plan.canvas_height
        margins = plan.margins  # [top, right, bottom, left]

        min_x = margins[3]  # left margin
        max_x = canvas_width - margins[1]  # right margin
        min_y = margins[0]  # top margin
        max_y = canvas_height - margins[2]  # bottom margin

        for obj_id, obj_vars in vars.items():
            x = obj_vars['x']
            y = obj_vars['y']
            width = obj_vars['width']
            height = obj_vars['height']

            # Object must be fully within canvas bounds
            solver.add(x >= min_x)
            solver.add(x + width <= max_x)
            solver.add(y >= min_y)
            solver.add(y + height <= max_y)

            count += 4

        return count

    def _add_overlap_constraints(self, solver: Solver, vars: Dict, dimensions: Dict[str, Tuple[float, float]]) -> int:
        """Add non-overlap constraints between all objects"""
        count = 0
        object_ids = list(vars.keys())

        for i, obj1_id in enumerate(object_ids):
            for obj2_id in object_ids[i + 1:]:
                v1 = vars[obj1_id]
                v2 = vars[obj2_id]

                # Two rectangles don't overlap if one is completely to the left/right/above/below the other
                # Constraint: OR(
                #   obj1.right <= obj2.left,  # obj1 left of obj2
                #   obj2.right <= obj1.left,  # obj2 left of obj1
                #   obj1.bottom <= obj2.top,  # obj1 above obj2
                #   obj2.bottom <= obj1.top   # obj2 above obj1
                # )

                solver.add(Or(
                    v1['x'] + v1['width'] <= v2['x'],  # obj1 left of obj2
                    v2['x'] + v2['width'] <= v1['x'],  # obj2 left of obj1
                    v1['y'] + v1['height'] <= v2['y'],  # obj1 above obj2
                    v2['y'] + v2['height'] <= v1['y']   # obj2 above obj1
                ))

                count += 1

        return count

    def _add_plan_constraints(self, solver: Solver, vars: Dict, plan: DiagramPlan, dimensions: Dict) -> int:
        """Add constraints from diagram plan"""
        count = 0

        all_constraints = plan.get_all_constraints()

        for constraint in all_constraints:
            # Skip low-priority constraints if there are too many
            if constraint.priority == ConstraintPriority.LOW and len(all_constraints) > 20:
                continue

            constraint_type = constraint.type
            objects = constraint.objects
            params = constraint.parameters

            # Skip if objects not in vars
            if not all(obj_id in vars for obj_id in objects):
                continue

            # Add constraint based on type
            if constraint_type == 'distance':
                added = self._add_distance_constraint(solver, vars, objects, params)
                count += added

            elif constraint_type in ['alignment_horizontal', 'alignment_h']:
                added = self._add_horizontal_alignment_constraint(solver, vars, objects)
                count += added

            elif constraint_type in ['alignment_vertical', 'alignment_v']:
                added = self._add_vertical_alignment_constraint(solver, vars, objects)
                count += added

            elif constraint_type == 'symmetry':
                added = self._add_symmetry_constraint(solver, vars, objects, params, plan)
                count += added

            elif constraint_type == 'centered':
                added = self._add_centered_constraint(solver, vars, objects, plan)
                count += added

        return count

    def _add_distance_constraint(self, solver: Solver, vars: Dict, objects: List[str], params: Dict) -> int:
        """Add distance constraint between two objects"""
        if len(objects) < 2:
            return 0

        obj1_id = objects[0]
        obj2_id = objects[1]
        target_distance = params.get('distance', 100.0)

        v1 = vars[obj1_id]
        v2 = vars[obj2_id]

        # Distance between centers
        center1_x = v1['x'] + v1['width'] / 2
        center1_y = v1['y'] + v1['height'] / 2
        center2_x = v2['x'] + v2['width'] / 2
        center2_y = v2['y'] + v2['height'] / 2

        # Euclidean distance
        dist_x = center2_x - center1_x
        dist_y = center2_y - center1_y

        # Approximate distance constraint (Z3 doesn't handle sqrt well, so use Manhattan or squared distance)
        # Using squared distance: dist^2 = target^2
        target_sq = target_distance ** 2
        tolerance = params.get('tolerance', 0.1) * target_sq

        solver.add(And(
            dist_x * dist_x + dist_y * dist_y >= target_sq - tolerance,
            dist_x * dist_x + dist_y * dist_y <= target_sq + tolerance
        ))

        return 1

    def _add_horizontal_alignment_constraint(self, solver: Solver, vars: Dict, objects: List[str]) -> int:
        """Align objects horizontally (same y coordinate)"""
        if len(objects) < 2:
            return 0

        # All objects should have the same y coordinate (aligned along horizontal axis)
        first_obj = vars[objects[0]]
        count = 0

        for obj_id in objects[1:]:
            obj_vars = vars[obj_id]
            solver.add(obj_vars['y'] == first_obj['y'])
            count += 1

        return count

    def _add_vertical_alignment_constraint(self, solver: Solver, vars: Dict, objects: List[str]) -> int:
        """Align objects vertically (same x coordinate)"""
        if len(objects) < 2:
            return 0

        # All objects should have the same x coordinate (aligned along vertical axis)
        first_obj = vars[objects[0]]
        count = 0

        for obj_id in objects[1:]:
            obj_vars = vars[obj_id]
            solver.add(obj_vars['x'] == first_obj['x'])
            count += 1

        return count

    def _add_symmetry_constraint(self, solver: Solver, vars: Dict, objects: List[str], params: Dict, plan: DiagramPlan) -> int:
        """Add symmetry constraint"""
        if len(objects) < 2:
            return 0

        axis = params.get('axis', 'vertical')
        count = 0

        if axis == 'vertical':
            # Objects should be symmetric about vertical center line
            center_x = plan.canvas_width / 2

            for i in range(len(objects) // 2):
                obj1 = vars[objects[i]]
                obj2 = vars[objects[len(objects) - 1 - i]]

                # Distance from center should be equal but opposite
                center1_x = obj1['x'] + obj1['width'] / 2
                center2_x = obj2['x'] + obj2['width'] / 2

                solver.add(center1_x + center2_x == 2 * center_x)
                count += 1

        elif axis == 'horizontal':
            # Objects should be symmetric about horizontal center line
            center_y = plan.canvas_height / 2

            for i in range(len(objects) // 2):
                obj1 = vars[objects[i]]
                obj2 = vars[objects[len(objects) - 1 - i]]

                center1_y = obj1['y'] + obj1['height'] / 2
                center2_y = obj2['y'] + obj2['height'] / 2

                solver.add(center1_y + center2_y == 2 * center_y)
                count += 1

        return count

    def _add_centered_constraint(self, solver: Solver, vars: Dict, objects: List[str], plan: DiagramPlan) -> int:
        """Center objects on canvas"""
        if len(objects) == 0:
            return 0

        center_x = plan.canvas_width / 2
        center_y = plan.canvas_height / 2
        count = 0

        for obj_id in objects:
            obj_vars = vars[obj_id]

            # Object center should be at canvas center
            obj_center_x = obj_vars['x'] + obj_vars['width'] / 2
            obj_center_y = obj_vars['y'] + obj_vars['height'] / 2

            solver.add(obj_center_x == center_x)
            solver.add(obj_center_y == center_y)
            count += 2

        return count

    # ========== Solution Extraction ==========

    def _extract_positions(self, model, vars: Dict) -> Dict[str, Tuple[float, float]]:
        """Extract positions from Z3 model"""
        positions = {}

        for obj_id, obj_vars in vars.items():
            x_val = model[obj_vars['x']]
            y_val = model[obj_vars['y']]

            # Convert Z3 values to Python floats
            if x_val is not None and y_val is not None:
                try:
                    # Handle both rational and real values
                    if hasattr(x_val, 'as_decimal'):
                        x = float(x_val.as_decimal(10).rstrip('?'))
                    else:
                        x = float(x_val.as_long() if hasattr(x_val, 'as_long') else x_val)

                    if hasattr(y_val, 'as_decimal'):
                        y = float(y_val.as_decimal(10).rstrip('?'))
                    else:
                        y = float(y_val.as_long() if hasattr(y_val, 'as_long') else y_val)

                    positions[obj_id] = (x, y)
                except Exception as e:
                    self.logger.warning(f"Failed to extract position for {obj_id}: {e}")

        return positions

    # ========== Utility Methods ==========

    def _extract_object_ids(self, plan: DiagramPlan) -> List[str]:
        """Extract object IDs from plan"""
        object_ids = set()

        # Safety check for None plan
        if not plan:
            return []

        # From original spec
        if plan.original_spec and hasattr(plan.original_spec, 'objects') and plan.original_spec.objects:
            for obj in plan.original_spec.objects:
                obj_id = obj.get('id', '') if isinstance(obj, dict) else getattr(obj, 'id', '')
                if obj_id:
                    object_ids.add(obj_id)

        # From subproblems
        if hasattr(plan, 'subproblems') and plan.subproblems:
            for subproblem in plan.subproblems:
                if hasattr(subproblem, 'specs') and subproblem.specs and hasattr(subproblem.specs, 'objects'):
                    for obj in subproblem.specs.objects:
                        obj_id = obj.get('id', '') if isinstance(obj, dict) else getattr(obj, 'id', '')
                        if obj_id:
                            object_ids.add(obj_id)

        return list(object_ids)

    def is_available(self) -> bool:
        """Check if Z3 is available"""
        return Z3_AVAILABLE

    def __repr__(self) -> str:
        """String representation"""
        return f"Z3LayoutSolver(timeout={self.timeout}ms, available={self.is_available()})"


# ========== Standalone Functions ==========

def check_z3_availability() -> bool:
    """
    Check if Z3 is available

    Returns:
        True if Z3 is installed
    """
    return Z3_AVAILABLE


def solve_simple_layout(object_ids: List[str],
                        canvas_size: Tuple[int, int] = (800, 600),
                        object_size: Tuple[float, float] = (50.0, 50.0)) -> LayoutSolution:
    """
    Simple layout solver for quick testing

    Args:
        object_ids: List of object IDs
        canvas_size: Canvas (width, height)
        object_size: Default object (width, height)

    Returns:
        LayoutSolution with positions

    Example:
        >>> solution = solve_simple_layout(['obj1', 'obj2', 'obj3'])
        >>> if solution.satisfiable:
        ...     print(solution.positions)
    """
    if not Z3_AVAILABLE:
        return LayoutSolution(satisfiable=False, metadata={'error': 'Z3 not available'})

    # Create minimal plan
    from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.UNKNOWN,
        problem_type='test',
        problem_text='Test layout',
        objects=[{'id': obj_id} for obj_id in object_ids]
    )

    plan = DiagramPlan(
        original_spec=spec,
        complexity_score=0.3,
        strategy='heuristic',
        canvas_width=canvas_size[0],
        canvas_height=canvas_size[1]
    )

    # Add no-overlap constraint
    from core.diagram_plan import create_no_overlap_constraint
    plan.add_global_constraint(create_no_overlap_constraint(object_ids))

    # Solve
    solver = Z3LayoutSolver(verbose=False)
    dimensions = {obj_id: object_size for obj_id in object_ids}
    return solver.solve_layout(plan, dimensions)
