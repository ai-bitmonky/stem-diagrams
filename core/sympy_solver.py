"""
SymPy Constraint Solver
=======================

Symbolic mathematics solver for physics-based layout constraints.
Complements Z3 by handling symbolic physics expressions.

Author: Universal STEM Diagram Generator
Date: November 12, 2025
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

try:
    import sympy as sp
    from sympy import symbols, Eq, solve
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    sp = None


@dataclass
class SymPySolution:
    """Solution from SymPy solver"""
    satisfiable: bool
    variables: Dict[str, float]
    equations_solved: List[str]
    metadata: Dict[str, Any]


class SymPyLayoutSolver:
    """
    SymPy-based symbolic solver for physics layout problems

    Use cases:
    - Symbolic physics relationships (F=ma, E=mc^2)
    - Geometric constraints with symbolic parameters
    - Problems requiring algebraic manipulation
    """

    def __init__(self):
        """Initialize SymPy solver"""
        if not SYMPY_AVAILABLE:
            raise ImportError("SymPy not installed. Install with: pip install sympy")

        self.logger = logging.getLogger(__name__)

    def solve_physics_layout(
        self,
        physics_equations: List[str],
        variables: List[str],
        known_values: Optional[Dict[str, float]] = None
    ) -> SymPySolution:
        """
        Solve physics-based layout using symbolic math

        Args:
            physics_equations: List of equations as strings (e.g., "F - m*a")
            variables: List of variable names to solve for
            known_values: Dictionary of known variable values

        Returns:
            SymPySolution with solved values

        Example:
            >>> solver = SymPyLayoutSolver()
            >>> result = solver.solve_physics_layout(
            ...     physics_equations=["F - m*a", "a - 10"],  # F=ma, a=10
            ...     variables=['F', 'm', 'a'],
            ...     known_values={'m': 2.0}
            ... )
            >>> print(result.variables)  # {'F': 20.0, 'm': 2.0, 'a': 10.0}
        """
        try:
            # Create symbolic variables
            sym_vars = {var: symbols(var, real=True) for var in variables}

            # Parse equations
            equations = []
            for eq_str in physics_equations:
                try:
                    # Parse equation (supports "F - m*a" format)
                    expr = sp.sympify(eq_str, locals=sym_vars)
                    equations.append(Eq(expr, 0))
                except Exception as e:
                    self.logger.warning(f"Failed to parse equation '{eq_str}': {e}")

            # Apply known values
            substitutions = {}
            if known_values:
                for var, val in known_values.items():
                    if var in sym_vars:
                        substitutions[sym_vars[var]] = val

            # Solve system
            unknowns = [sym_vars[v] for v in variables if v not in (known_values or {})]

            if unknowns:
                solutions = solve(equations, unknowns, dict=True)

                if solutions:
                    # Take first solution
                    solution = solutions[0]

                    # Convert to float values
                    result_vars = known_values.copy() if known_values else {}
                    for sym, val in solution.items():
                        var_name = str(sym)
                        try:
                            # Try to evaluate to float
                            evalf_result = val.evalf()
                            # Check if result is numeric
                            if evalf_result.is_number:
                                result_vars[var_name] = float(evalf_result)
                            else:
                                # Still symbolic, skip it
                                self.logger.warning(f"Variable {var_name} could not be evaluated to float: {evalf_result}")
                        except (TypeError, ValueError, AttributeError) as e:
                            # Cannot convert to float, skip this variable
                            self.logger.warning(f"Cannot convert {var_name} to float: {e}")

                    return SymPySolution(
                        satisfiable=True,
                        variables=result_vars,
                        equations_solved=[str(eq) for eq in equations],
                        metadata={
                            'solver': 'sympy',
                            'solution_count': len(solutions)
                        }
                    )

            # No solution found
            return SymPySolution(
                satisfiable=False,
                variables=known_values or {},
                equations_solved=[],
                metadata={'solver': 'sympy', 'error': 'No solution found'}
            )

        except Exception as e:
            self.logger.error(f"SymPy solve error: {e}")
            return SymPySolution(
                satisfiable=False,
                variables=known_values or {},
                equations_solved=[],
                metadata={'solver': 'sympy', 'error': str(e)}
            )

    def solve_geometric_constraints(
        self,
        constraints: List[Dict[str, Any]],
        object_ids: List[str]
    ) -> SymPySolution:
        """
        Solve geometric layout constraints symbolically

        Args:
            constraints: List of constraint dicts with type and parameters
            object_ids: List of object IDs to position

        Returns:
            SymPySolution with object positions
        """
        # Create position variables for each object
        variables = []
        for obj_id in object_ids:
            variables.extend([f"{obj_id}_x", f"{obj_id}_y"])

        # Convert constraints to equations
        equations = []
        known_values = {}

        for constraint in constraints:
            c_type = constraint.get('type', '')

            if c_type == 'DISTANCE':
                # Distance between two objects
                obj1 = constraint.get('object1')
                obj2 = constraint.get('object2')
                distance = constraint.get('distance', 100)

                if obj1 in object_ids and obj2 in object_ids:
                    # (x2-x1)^2 + (y2-y1)^2 = d^2
                    eq = f"({obj2}_x - {obj1}_x)**2 + ({obj2}_y - {obj1}_y)**2 - {distance**2}"
                    equations.append(eq)

            elif c_type == 'ALIGN_HORIZONTAL':
                # Same y-coordinate
                obj1 = constraint.get('object1')
                obj2 = constraint.get('object2')

                if obj1 in object_ids and obj2 in object_ids:
                    eq = f"{obj1}_y - {obj2}_y"
                    equations.append(eq)

            elif c_type == 'ALIGN_VERTICAL':
                obj1 = constraint.get('object1')
                obj2 = constraint.get('object2')
                if obj1 in object_ids and obj2 in object_ids:
                    eq = f"{obj1}_x - {obj2}_x"
                    equations.append(eq)

            elif c_type == 'FIXED_POSITION':
                # Fixed x, y
                obj = constraint.get('object')
                x = constraint.get('x')
                y = constraint.get('y')

                if obj in object_ids:
                    if x is not None:
                        known_values[f"{obj}_x"] = x
                    if y is not None:
                        known_values[f"{obj}_y"] = y

        # Solve
        return self.solve_physics_layout(equations, variables, known_values)


    def solve_layout(self, entities: list, constraints: list) -> 'SymPySolution':
        """
        Solve layout from entities and constraints (DiagramPlanner interface)

        Args:
            entities: List of entity dicts with 'id' keys
            constraints: List of LayoutConstraint objects

        Returns:
            SymPySolution with positions dict
        """
        # Extract object IDs
        object_ids = [e['id'] for e in entities]

        # Convert LayoutConstraints to constraint dicts
        constraint_dicts = []
        for c in constraints:
            constraint_dicts.append({
                'type': c.type,
                'objects': c.objects,
                **c.parameters
            })

        # Use existing solve_geometric_layout
        return self.solve_geometric_layout(constraint_dicts, object_ids)

    def solve_geometric_layout(self, entities: list, constraints: list) -> 'SymPySolution':
        """
        Solve geometric layout (alternative interface for DiagramPlanner)

        Args:
            entities: List of entity dicts
            constraints: List of constraints

        Returns:
            SymPySolution with positions
        """
        # Extract IDs if entities are dicts
        if entities and isinstance(entities[0], dict):
            object_ids = [e['id'] for e in entities]
        else:
            # Already a list of IDs or LayoutConstraint objects
            object_ids = [str(e) for e in entities] if entities else []

        # Use existing solve_geometric_layout logic
        return self.solve_geometric_constraints(constraints, object_ids)


def is_sympy_available() -> bool:
    """Check if SymPy is available"""
    return SYMPY_AVAILABLE
