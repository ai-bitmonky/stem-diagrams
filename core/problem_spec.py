"""
Canonical Problem Specification - Shared Data Structures

This module contains the core data structures used across analyzers
to avoid circular dependencies between local_ai_analyzer and universal_ai_analyzer.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class PhysicsDomain(Enum):
    """Physics domain classification"""
    ELECTROSTATICS = "electrostatics"
    CURRENT_ELECTRICITY = "current_electricity"
    MECHANICS = "mechanics"
    THERMODYNAMICS = "thermodynamics"
    OPTICS = "optics"
    MAGNETISM = "magnetism"
    WAVES = "waves"
    MODERN_PHYSICS = "modern_physics"
    UNKNOWN = "unknown"


@dataclass
class CanonicalProblemSpec:
    """
    Universal problem specification format - domain-agnostic
    This is the ONLY spec format used throughout the pipeline
    """
    # Metadata
    domain: PhysicsDomain
    problem_type: str
    problem_text: str
    complexity_score: float = 0.0

    # Core entities (domain-agnostic)
    objects: List[Dict] = field(default_factory=list)
    relationships: List[Dict] = field(default_factory=list)
    environment: Dict = field(default_factory=dict)

    # Physics context
    physics_context: Dict = field(default_factory=dict)
    applicable_laws: List[str] = field(default_factory=list)

    # Constraints
    constraints: List[Dict] = field(default_factory=list)

    # Geometry
    geometry: Dict = field(default_factory=dict)
    coordinate_system: str = "cartesian"

    # Subproblems (for complex problems)
    subproblems: List['CanonicalProblemSpec'] = field(default_factory=list)

    # Validation
    is_complete: bool = True
    missing_information: List[str] = field(default_factory=list)
    confidence: float = 0.0

    # AI reasoning trace
    reasoning_trace: List[Dict] = field(default_factory=list)
    attribute_provenance: Dict[str, str] = field(default_factory=dict)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    diagram_plan: Optional[Any] = None  # Reference to DiagramPlan for downstream modules
    diagram_plan_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'domain': self.domain.value if isinstance(self.domain, PhysicsDomain) else self.domain,
            'problem_type': self.problem_type,
            'problem_text': self.problem_text,
            'complexity_score': self.complexity_score,
            'objects': self.objects,
            'relationships': self.relationships,
            'environment': self.environment,
            'physics_context': self.physics_context,
            'applicable_laws': self.applicable_laws,
            'constraints': self.constraints,
            'geometry': self.geometry,
            'coordinate_system': self.coordinate_system,
            'subproblems': [sp.to_dict() if hasattr(sp, 'to_dict') else sp for sp in self.subproblems],
            'is_complete': self.is_complete,
            'missing_information': self.missing_information,
            'confidence': self.confidence,
            'reasoning_trace': self.reasoning_trace,
            'attribute_provenance': self.attribute_provenance,
            'analysis_metadata': self.analysis_metadata,
            'diagram_plan_metadata': self.diagram_plan_metadata
        }


class IncompleteSpecsError(Exception):
    """Raised when specifications are incomplete and cannot be fixed"""
    def __init__(self, missing: List[str]):
        self.missing = missing
        super().__init__(f"Incomplete specifications. Missing: {', '.join(missing)}")
