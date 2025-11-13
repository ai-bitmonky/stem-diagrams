"""
Diagram Plan Data Structures
Phase 1B of Planning & Reasoning Roadmap

Defines the data structures for diagram planning:
- DiagramPlan: The main planning output
- PlanningStrategy: Different strategies for diagram generation
- LayoutConstraint: Constraints for diagram layout
- Subproblem: Decomposed problem components
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain


class PlanningStrategy(Enum):
    """Strategies for diagram planning"""
    # Simple strategies
    HEURISTIC = "heuristic"  # Fast heuristic-based placement
    TEMPLATE = "template"  # Use predefined templates

    # Constraint-based strategies
    CONSTRAINT_BASED = "constraint_based"  # Use constraint solver (Z3)
    OPTIMIZATION = "optimization"  # Optimize for specific objectives

    # Symbolic strategies
    SYMBOLIC_PHYSICS = "symbolic_physics"  # Use symbolic physics engine
    GEOMETRIC = "geometric"  # Use computational geometry

    # Hybrid strategies
    HYBRID = "hybrid"  # Combine multiple approaches
    ADAPTIVE = "adaptive"  # Select strategy dynamically


class LayoutObjective(Enum):
    """Optimization objectives for layout"""
    MINIMIZE_OVERLAP = "minimize_overlap"
    MAXIMIZE_CLARITY = "maximize_clarity"
    MINIMIZE_AREA = "minimize_area"
    MAXIMIZE_SYMMETRY = "maximize_symmetry"
    BALANCE_COMPOSITION = "balance_composition"


class ConstraintPriority(Enum):
    """Priority levels for constraints"""
    REQUIRED = "required"  # Must be satisfied
    HIGH = "high"  # Should be satisfied
    MEDIUM = "medium"  # Nice to have
    LOW = "low"  # Optional


@dataclass
class LayoutConstraint:
    """
    A constraint for diagram layout

    Examples:
    - No overlap between objects
    - Minimum distance between components
    - Alignment constraints
    - Symmetry constraints
    """
    type: str  # Constraint type (e.g., "no_overlap", "distance", "alignment")
    objects: List[str]  # Object IDs involved in constraint
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: ConstraintPriority = ConstraintPriority.MEDIUM
    tolerance: float = 1e-3  # Tolerance for numerical constraints

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'objects': self.objects,
            'parameters': self.parameters,
            'priority': self.priority.value if isinstance(self.priority, ConstraintPriority) else self.priority,
            'tolerance': self.tolerance
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'LayoutConstraint':
        """Create from dictionary"""
        return cls(
            type=data['type'],
            objects=data['objects'],
            parameters=data.get('parameters', {}),
            priority=ConstraintPriority(data.get('priority', 'medium')),
            tolerance=data.get('tolerance', 1e-3)
        )


@dataclass
class Subproblem:
    """
    A decomposed subproblem

    For complex problems, we decompose into simpler subproblems
    that can be solved independently and then combined.
    """
    id: str
    description: str
    specs: CanonicalProblemSpec
    dependencies: List[str] = field(default_factory=list)  # IDs of subproblems this depends on
    constraints: List[LayoutConstraint] = field(default_factory=list)
    complexity: float = 0.0  # Estimated complexity (0-1)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'specs': self.specs.to_dict() if hasattr(self.specs, 'to_dict') else self.specs,
            'dependencies': self.dependencies,
            'constraints': [c.to_dict() for c in self.constraints],
            'complexity': self.complexity,
            'metadata': self.metadata
        }


@dataclass
class DiagramPlan:
    """
    Complete diagram plan

    This is the output of the DiagramPlanner and serves as input to the
    constraint solver and scene builder.
    """
    # Original specification
    original_spec: CanonicalProblemSpec

    # Planning metadata
    complexity_score: float  # Overall complexity (0-1)
    strategy: PlanningStrategy  # Chosen planning strategy
    objectives: List[LayoutObjective] = field(default_factory=list)

    # Decomposition
    subproblems: List[Subproblem] = field(default_factory=list)
    is_decomposed: bool = False

    # Constraints
    global_constraints: List[LayoutConstraint] = field(default_factory=list)
    local_constraints: Dict[str, List[LayoutConstraint]] = field(default_factory=dict)

    # Canvas and coordinate system
    canvas_width: int = 1200
    canvas_height: int = 800
    margins: List[int] = field(default_factory=lambda: [40, 40, 40, 40])  # top, right, bottom, left
    coordinate_system: str = "cartesian"
    origin: List[int] = field(default_factory=lambda: [600, 400])  # center of canvas
    scale: float = 100.0  # pixels per unit

    # Layout hints
    layout_hints: Dict[str, Any] = field(default_factory=dict)
    style_hints: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Extracted data from property graph pipeline
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    extracted_relations: List[Dict[str, Any]] = field(default_factory=list)

    # Planning trace (for debugging)
    planning_trace: List[Dict] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'original_spec': self.original_spec.to_dict() if hasattr(self.original_spec, 'to_dict') else self.original_spec,
            'complexity_score': self.complexity_score,
            'strategy': self.strategy.value if isinstance(self.strategy, PlanningStrategy) else self.strategy,
            'objectives': [obj.value if isinstance(obj, LayoutObjective) else obj for obj in self.objectives],
            'subproblems': [sp.to_dict() for sp in self.subproblems],
            'is_decomposed': self.is_decomposed,
            'global_constraints': [c.to_dict() for c in self.global_constraints],
            'local_constraints': {k: [c.to_dict() for c in v] for k, v in self.local_constraints.items()},
            'canvas_width': self.canvas_width,
            'canvas_height': self.canvas_height,
            'margins': self.margins,
            'coordinate_system': self.coordinate_system,
            'origin': self.origin,
            'scale': self.scale,
            'layout_hints': self.layout_hints,
            'style_hints': self.style_hints,
            'extracted_entities': self.extracted_entities,
            'extracted_relations': self.extracted_relations,
            'planning_trace': self.planning_trace,
            'metadata': self.metadata
        }

    def add_global_constraint(self, constraint: LayoutConstraint) -> None:
        """Add a global constraint"""
        self.global_constraints.append(constraint)

    def add_local_constraint(self, object_id: str, constraint: LayoutConstraint) -> None:
        """Add a constraint specific to an object"""
        if object_id not in self.local_constraints:
            self.local_constraints[object_id] = []
        self.local_constraints[object_id].append(constraint)

    def add_subproblem(self, subproblem: Subproblem) -> None:
        """Add a subproblem"""
        self.subproblems.append(subproblem)
        self.is_decomposed = len(self.subproblems) > 1

    def get_all_constraints(self) -> List[LayoutConstraint]:
        """Get all constraints (global + local)"""
        all_constraints = list(self.global_constraints)
        for constraints in self.local_constraints.values():
            all_constraints.extend(constraints)
        return all_constraints

    def get_constraint_count(self) -> Dict[str, int]:
        """Get count of constraints by priority"""
        counts = {
            'required': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for constraint in self.get_all_constraints():
            priority = constraint.priority.value if isinstance(constraint.priority, ConstraintPriority) else constraint.priority
            if priority in counts:
                counts[priority] += 1

        return counts

    def log_planning_step(self, step: str, details: Dict[str, Any]) -> None:
        """Log a planning step for debugging"""
        self.planning_trace.append({
            'step': step,
            'timestamp': len(self.planning_trace),
            'details': details
        })

    def summary(self) -> str:
        """Get a summary of the plan"""
        lines = [
            "Diagram Plan Summary:",
            f"  Complexity: {self.complexity_score:.2f}",
            f"  Strategy: {self.strategy.value if isinstance(self.strategy, PlanningStrategy) else self.strategy}",
            f"  Decomposed: {self.is_decomposed}",
            f"  Subproblems: {len(self.subproblems)}",
            f"  Global Constraints: {len(self.global_constraints)}",
            f"  Total Constraints: {len(self.get_all_constraints())}",
            ""
        ]

        # Constraint breakdown
        constraint_counts = self.get_constraint_count()
        lines.append("Constraints by Priority:")
        for priority, count in constraint_counts.items():
            if count > 0:
                lines.append(f"    {priority}: {count}")

        # Objectives
        if self.objectives:
            lines.append("\nOptimization Objectives:")
            for obj in self.objectives:
                obj_str = obj.value if isinstance(obj, LayoutObjective) else str(obj)
                lines.append(f"    - {obj_str}")

        # Subproblems
        if self.subproblems:
            lines.append("\nSubproblems:")
            for sp in self.subproblems:
                lines.append(f"    - {sp.id}: {sp.description} (complexity: {sp.complexity:.2f})")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        """String representation"""
        return f"DiagramPlan(complexity={self.complexity_score:.2f}, strategy={self.strategy}, subproblems={len(self.subproblems)})"


# ========== Common Constraint Builders ==========

def create_no_overlap_constraint(object_ids: List[str], margin: float = 5.0, priority: ConstraintPriority = ConstraintPriority.REQUIRED) -> LayoutConstraint:
    """Create a no-overlap constraint for multiple objects"""
    return LayoutConstraint(
        type="no_overlap",
        objects=object_ids,
        parameters={'margin': margin},
        priority=priority
    )


def create_distance_constraint(obj1: str, obj2: str, distance: float, priority: ConstraintPriority = ConstraintPriority.HIGH) -> LayoutConstraint:
    """Create a distance constraint between two objects"""
    return LayoutConstraint(
        type="distance",
        objects=[obj1, obj2],
        parameters={'distance': distance},
        priority=priority
    )


def create_alignment_constraint(object_ids: List[str], axis: str = 'horizontal', priority: ConstraintPriority = ConstraintPriority.MEDIUM) -> LayoutConstraint:
    """Create an alignment constraint"""
    return LayoutConstraint(
        type=f"alignment_{axis}",
        objects=object_ids,
        parameters={'axis': axis},
        priority=priority
    )


def create_symmetry_constraint(object_ids: List[str], axis: str = 'vertical', priority: ConstraintPriority = ConstraintPriority.LOW) -> LayoutConstraint:
    """Create a symmetry constraint"""
    return LayoutConstraint(
        type="symmetry",
        objects=object_ids,
        parameters={'axis': axis},
        priority=priority
    )


def create_bounds_constraint(object_id: str, min_x: float, max_x: float, min_y: float, max_y: float, priority: ConstraintPriority = ConstraintPriority.REQUIRED) -> LayoutConstraint:
    """Create a bounds constraint (object must stay within bounds)"""
    return LayoutConstraint(
        type="bounds",
        objects=[object_id],
        parameters={
            'min_x': min_x,
            'max_x': max_x,
            'min_y': min_y,
            'max_y': max_y
        },
        priority=priority
    )
