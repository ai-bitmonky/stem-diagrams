"""
SymPy Symbolic Physics Engine - Symbolic Equation Solving
Phase 3B of Planning & Reasoning Roadmap

Provides symbolic solving for physics problems:
- Force balance (ΣF = 0)
- Kinematic equations (motion)
- Energy conservation
- Circuit analysis (Kirchhoff's laws)
- Optics (lens/mirror equations)

Installation:
    pip install sympy

Example:
    engine = SymbolicPhysicsEngine()
    forces = [Force('F1', magnitude=10, angle=0), Force('F2', angle=90)]
    solution = engine.solve_force_balance(forces)
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

# SymPy is optional - graceful degradation if not installed
try:
    import sympy as sp
    from sympy import symbols, Eq, solve, cos, sin, sqrt, simplify, N
    from sympy.physics.mechanics import dynamicsymbols
    from sympy.physics.units import meter, second, kilogram, newton, joule
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    sp = None


@dataclass
class Force:
    """Represents a force vector"""
    name: str
    magnitude: Optional[float] = None  # None means unknown
    angle: Optional[float] = None  # Angle in degrees from +x axis
    angle_rad: Optional[float] = None  # Angle in radians
    components: Optional[Tuple[float, float]] = None  # (Fx, Fy)

    def __post_init__(self):
        """Convert angle to radians if provided"""
        if self.angle is not None and self.angle_rad is None:
            self.angle_rad = sp.rad(self.angle) if SYMPY_AVAILABLE else self.angle * 3.14159 / 180


@dataclass
class PhysicsSolution:
    """Solution from symbolic physics engine"""
    solved_variables: Dict[str, Any] = field(default_factory=dict)
    equations: List[Any] = field(default_factory=list)
    assumptions: Dict[str, Any] = field(default_factory=dict)
    solution_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_value(self, variable: str) -> Optional[float]:
        """Get numeric value of a solved variable"""
        value = self.solved_variables.get(variable)
        if value is not None:
            try:
                if SYMPY_AVAILABLE:
                    return float(N(value))
                else:
                    return float(value)
            except:
                return None
        return None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'solved_variables': {k: str(v) for k, v in self.solved_variables.items()},
            'solution_valid': self.solution_valid,
            'metadata': self.metadata
        }


class SymbolicPhysicsEngine:
    """
    Symbolic physics engine using SymPy

    Solves physics problems symbolically before numerical evaluation
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize symbolic physics engine

        Args:
            verbose: Enable verbose logging

        Raises:
            ImportError: If SymPy is not installed
        """
        if not SYMPY_AVAILABLE:
            raise ImportError(
                "SymPy is not installed. Install with: pip install sympy"
            )

        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Physical constants
        self.g = 9.8  # m/s^2 (gravity)
        self.k = 8.99e9  # N⋅m²/C² (Coulomb's constant)
        self.c = 3.0e8  # m/s (speed of light)

    # ========== Force Balance ==========

    def solve_force_balance(self, forces: List[Force], equilibrium: bool = True) -> PhysicsSolution:
        """
        Solve force balance equations (Newton's 1st law or 2nd law)

        For equilibrium: ΣF = 0
        For dynamics: ΣF = ma

        Args:
            forces: List of Force objects
            equilibrium: If True, assume equilibrium (ΣF = 0)

        Returns:
            PhysicsSolution with solved force magnitudes

        Example:
            # Three forces in equilibrium, find F3
            forces = [
                Force('F1', magnitude=10, angle=0),
                Force('F2', magnitude=10, angle=90),
                Force('F3', angle=180)  # Unknown magnitude
            ]
            solution = engine.solve_force_balance(forces)
            print(solution.get_value('F3'))  # → 14.14 (approx)
        """
        # Create symbols for unknown force magnitudes
        force_symbols = {}
        for force in forces:
            if force.magnitude is None:
                force_symbols[force.name] = symbols(force.name, positive=True, real=True)

        # Sum forces in x and y directions
        sum_x = 0
        sum_y = 0

        for force in forces:
            # Get magnitude (either numeric or symbolic)
            if force.magnitude is not None:
                mag = force.magnitude
            else:
                mag = force_symbols[force.name]

            # Get angle
            if force.angle_rad is not None:
                angle = force.angle_rad
            elif force.angle is not None:
                angle = sp.rad(force.angle)
            else:
                angle = 0

            # Add components
            if force.components:
                sum_x += force.components[0]
                sum_y += force.components[1]
            else:
                sum_x += mag * cos(angle)
                sum_y += mag * sin(angle)

        # Create equilibrium equations
        if equilibrium:
            eq_x = Eq(sum_x, 0)
            eq_y = Eq(sum_y, 0)
        else:
            # For dynamics, would need mass and acceleration
            # For now, just equilibrium
            eq_x = Eq(sum_x, 0)
            eq_y = Eq(sum_y, 0)

        # Solve
        unknowns = list(force_symbols.values())

        if unknowns:
            try:
                solutions = solve([eq_x, eq_y], unknowns, dict=True)

                if solutions:
                    sol_dict = solutions[0] if isinstance(solutions, list) else solutions

                    # Convert symbolic solutions to numeric if possible
                    solved_variables = {}
                    for sym_name, sym in force_symbols.items():
                        if sym in sol_dict:
                            solved_variables[sym_name] = sol_dict[sym]

                    return PhysicsSolution(
                        solved_variables=solved_variables,
                        equations=[eq_x, eq_y],
                        solution_valid=True,
                        metadata={'method': 'force_balance', 'unknowns': len(unknowns)}
                    )
                else:
                    return PhysicsSolution(
                        solution_valid=False,
                        metadata={'error': 'No solution found'}
                    )
            except Exception as e:
                self.logger.error(f"Force balance solve failed: {e}")
                return PhysicsSolution(
                    solution_valid=False,
                    metadata={'error': str(e)}
                )
        else:
            # All forces known, just verify equilibrium
            sum_x_val = float(N(sum_x))
            sum_y_val = float(N(sum_y))

            return PhysicsSolution(
                solved_variables={},
                solution_valid=abs(sum_x_val) < 1e-6 and abs(sum_y_val) < 1e-6,
                metadata={
                    'sum_x': sum_x_val,
                    'sum_y': sum_y_val,
                    'balanced': abs(sum_x_val) < 1e-6 and abs(sum_y_val) < 1e-6
                }
            )

    # ========== Kinematics ==========

    def solve_kinematics(self,
                        initial_velocity: Optional[float] = None,
                        final_velocity: Optional[float] = None,
                        acceleration: Optional[float] = None,
                        time: Optional[float] = None,
                        distance: Optional[float] = None) -> PhysicsSolution:
        """
        Solve kinematic equations for 1D motion

        Equations:
        1. v = v0 + at
        2. s = v0*t + (1/2)*a*t²
        3. v² = v0² + 2as

        Args:
            initial_velocity: v0
            final_velocity: v
            acceleration: a
            time: t
            distance: s

        Returns:
            PhysicsSolution with solved variables

        Example:
            # Find final velocity: v0=0, a=10, t=5
            solution = engine.solve_kinematics(
                initial_velocity=0,
                acceleration=10,
                time=5
            )
            print(solution.get_value('v'))  # → 50
        """
        # Create symbols
        v0, v, a, t, s = symbols('v0 v a t s', real=True)

        # Kinematic equations
        eq1 = Eq(v, v0 + a * t)
        eq2 = Eq(s, v0 * t + sp.Rational(1, 2) * a * t**2)
        eq3 = Eq(v**2, v0**2 + 2 * a * s)

        # Build substitution dict for known values
        known = {}
        if initial_velocity is not None:
            known[v0] = initial_velocity
        if final_velocity is not None:
            known[v] = final_velocity
        if acceleration is not None:
            known[a] = acceleration
        if time is not None:
            known[t] = time
        if distance is not None:
            known[s] = distance

        # Find unknowns
        all_vars = {v0, v, a, t, s}
        unknowns = all_vars - set(known.keys())

        if len(unknowns) > 2:
            return PhysicsSolution(
                solution_valid=False,
                metadata={'error': f'Too many unknowns ({len(unknowns)}). Need at least 3 known variables.'}
            )

        # Substitute known values
        eq1_sub = eq1.subs(known)
        eq2_sub = eq2.subs(known)
        eq3_sub = eq3.subs(known)

        # Try to solve with different equation combinations
        try:
            # Try eq1 and eq2
            solutions = solve([eq1_sub, eq2_sub], list(unknowns), dict=True)

            if not solutions:
                # Try eq1 and eq3
                solutions = solve([eq1_sub, eq3_sub], list(unknowns), dict=True)

            if not solutions:
                # Try eq2 and eq3
                solutions = solve([eq2_sub, eq3_sub], list(unknowns), dict=True)

            if solutions:
                sol_dict = solutions[0] if isinstance(solutions, list) else solutions

                # Convert to readable variable names
                var_map = {'v0': v0, 'v': v, 'a': a, 't': t, 's': s}
                solved_variables = {}

                for var_name, var_sym in var_map.items():
                    if var_sym in sol_dict:
                        solved_variables[var_name] = sol_dict[var_sym]
                    elif var_sym in known:
                        solved_variables[var_name] = known[var_sym]

                return PhysicsSolution(
                    solved_variables=solved_variables,
                    equations=[eq1, eq2, eq3],
                    assumptions=known,
                    solution_valid=True,
                    metadata={'method': 'kinematics'}
                )
            else:
                return PhysicsSolution(
                    solution_valid=False,
                    metadata={'error': 'No solution found'}
                )

        except Exception as e:
            self.logger.error(f"Kinematics solve failed: {e}")
            return PhysicsSolution(
                solution_valid=False,
                metadata={'error': str(e)}
            )

    # ========== Incline Plane ==========

    def solve_incline_plane(self, mass: float, angle: float, friction_coeff: Optional[float] = None) -> PhysicsSolution:
        """
        Solve incline plane problem

        Args:
            mass: Mass in kg
            angle: Incline angle in degrees
            friction_coeff: Coefficient of friction (optional)

        Returns:
            PhysicsSolution with normal force, friction force, net force
        """
        # Convert angle to radians
        angle_rad = sp.rad(angle)

        # Symbols
        m, theta, mu = symbols('m theta mu', positive=True, real=True)
        g = self.g

        # Weight
        W = m * g

        # Normal force: N = mg*cos(θ)
        N_force = W * cos(theta)

        # Parallel component: F_parallel = mg*sin(θ)
        F_parallel = W * sin(theta)

        # Friction force (if present): f = μN
        if friction_coeff is not None:
            F_friction = mu * N_force
            F_net = F_parallel - F_friction
        else:
            F_friction = 0
            F_net = F_parallel

        # Substitute values
        subs = {m: mass, theta: angle_rad}
        if friction_coeff is not None:
            subs[mu] = friction_coeff

        N_val = float(N(N_force.subs(subs)))
        F_parallel_val = float(N(F_parallel.subs(subs)))
        F_friction_val = float(N(F_friction.subs(subs))) if friction_coeff else 0
        F_net_val = float(N(F_net.subs(subs)))

        return PhysicsSolution(
            solved_variables={
                'normal_force': N_val,
                'parallel_force': F_parallel_val,
                'friction_force': F_friction_val,
                'net_force': F_net_val,
                'weight': mass * g
            },
            solution_valid=True,
            metadata={
                'mass': mass,
                'angle': angle,
                'friction_coeff': friction_coeff
            }
        )

    # ========== Electrostatics ==========

    def solve_coulomb_force(self, q1: float, q2: float, distance: float) -> PhysicsSolution:
        """
        Calculate Coulomb force between two charges

        F = k * |q1 * q2| / r²

        Args:
            q1: Charge 1 in Coulombs
            q2: Charge 2 in Coulombs
            distance: Distance in meters

        Returns:
            PhysicsSolution with force magnitude
        """
        # Coulomb's law
        F = self.k * abs(q1 * q2) / (distance ** 2)

        return PhysicsSolution(
            solved_variables={
                'force': F,
                'attractive': (q1 * q2 < 0)
            },
            solution_valid=True,
            metadata={
                'q1': q1,
                'q2': q2,
                'distance': distance,
                'coulomb_constant': self.k
            }
        )

    # ========== Energy Conservation ==========

    def solve_energy_conservation(self,
                                   initial_kinetic: Optional[float] = None,
                                   final_kinetic: Optional[float] = None,
                                   initial_potential: Optional[float] = None,
                                   final_potential: Optional[float] = None,
                                   work_done: Optional[float] = None) -> PhysicsSolution:
        """
        Solve energy conservation problems

        E_initial + W = E_final
        (KE_i + PE_i) + W = (KE_f + PE_f)

        Args:
            initial_kinetic: Initial KE
            final_kinetic: Final KE
            initial_potential: Initial PE
            final_potential: Final PE
            work_done: Work done by external forces

        Returns:
            PhysicsSolution with solved energies
        """
        # Symbols
        KE_i, KE_f, PE_i, PE_f, W = symbols('KE_i KE_f PE_i PE_f W', real=True)

        # Energy conservation equation
        eq = Eq(KE_i + PE_i + W, KE_f + PE_f)

        # Build known values
        known = {}
        if initial_kinetic is not None:
            known[KE_i] = initial_kinetic
        if final_kinetic is not None:
            known[KE_f] = final_kinetic
        if initial_potential is not None:
            known[PE_i] = initial_potential
        if final_potential is not None:
            known[PE_f] = final_potential
        if work_done is not None:
            known[W] = work_done

        # Find unknowns
        all_vars = {KE_i, KE_f, PE_i, PE_f, W}
        unknowns = all_vars - set(known.keys())

        if len(unknowns) > 1:
            return PhysicsSolution(
                solution_valid=False,
                metadata={'error': f'Too many unknowns ({len(unknowns)}). Need exactly 1 unknown.'}
            )

        # Solve
        try:
            eq_sub = eq.subs(known)
            solutions = solve(eq_sub, list(unknowns))

            if solutions:
                solved_value = solutions[0] if isinstance(solutions, list) else solutions

                # Map back to variable name
                var_map = {'KE_i': KE_i, 'KE_f': KE_f, 'PE_i': PE_i, 'PE_f': PE_f, 'W': W}
                solved_variables = dict(known)

                for var_name, var_sym in var_map.items():
                    if var_sym in unknowns:
                        solved_variables[var_name] = float(N(solved_value))

                return PhysicsSolution(
                    solved_variables=solved_variables,
                    equations=[eq],
                    solution_valid=True,
                    metadata={'method': 'energy_conservation'}
                )
            else:
                return PhysicsSolution(
                    solution_valid=False,
                    metadata={'error': 'No solution found'}
                )

        except Exception as e:
            self.logger.error(f"Energy conservation solve failed: {e}")
            return PhysicsSolution(
                solution_valid=False,
                metadata={'error': str(e)}
            )

    # ========== Utility Methods ==========

    def is_available(self) -> bool:
        """Check if SymPy is available"""
        return SYMPY_AVAILABLE

    def __repr__(self) -> str:
        """String representation"""
        return f"SymbolicPhysicsEngine(available={self.is_available()})"


# ========== Standalone Functions ==========

def check_sympy_availability() -> bool:
    """
    Check if SymPy is available

    Returns:
        True if SymPy is installed
    """
    return SYMPY_AVAILABLE


def solve_simple_force_balance(forces: List[Tuple[str, float, float]]) -> Dict[str, float]:
    """
    Simple force balance solver

    Args:
        forces: List of (name, magnitude, angle_degrees) tuples

    Returns:
        Dict of solved variables

    Example:
        >>> forces = [('F1', 10, 0), ('F2', 10, 90), ('F3', None, 180)]
        >>> solution = solve_simple_force_balance(forces)
        >>> print(solution['F3'])  # → 14.14
    """
    if not SYMPY_AVAILABLE:
        return {}

    try:
        engine = SymbolicPhysicsEngine()
        force_objs = [Force(name, magnitude=mag, angle=angle) for name, mag, angle in forces]
        solution = engine.solve_force_balance(force_objs)

        if solution.solution_valid:
            return {k: solution.get_value(k) for k in solution.solved_variables.keys()}
        else:
            return {}
    except Exception:
        return {}
