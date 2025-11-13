"""
Domain Module Framework
=======================

Defines pluggable domain-specific builders that can attach external
rendering libraries (SchemDraw, PySketcher, RDKit, etc.) without touching
core pipeline logic. Each module produces a lightweight artifact that can be
rendered by downstream tooling or exposed in the UI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.primitive_library import PrimitiveLibrary, PrimitiveCategory


@dataclass
class DomainModuleArtifact:
    """Output produced by a domain module."""

    module_id: str
    title: str
    format: str  # e.g., 'schemdraw_python', 'latex', 'mermaid'
    content: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'module_id': self.module_id,
            'title': self.title,
            'format': self.format,
            'content': self.content,
            'description': self.description,
            'metadata': self.metadata,
        }


class DomainModule(ABC):
    """Base class for all pluggable domain modules."""

    module_id: str = "generic"
    display_name: str = "Generic Module"
    supported_domains: List[str] = []
    priority: int = 10  # Higher priority modules run first

    def __init__(self) -> None:
        self._available = True
        self.primitive_library: Optional[PrimitiveLibrary] = None

    @property
    def available(self) -> bool:
        return self._available

    @available.setter
    def available(self, value: bool) -> None:
        self._available = value

    def supports_domain(self, domain: Optional[str]) -> bool:
        if not domain:
            return False
        domain_lower = domain.lower()
        return any(domain_lower == d or domain_lower.startswith(d)
                   for d in self.supported_domains)

    def set_primitive_library(self, primitive_library: PrimitiveLibrary) -> None:
        self.primitive_library = primitive_library

    def query_primitives(
        self,
        text: str,
        domain: Optional[str],
        top_k: int = 3,
        min_score: float = 0.2
    ) -> List[Any]:
        if not self.primitive_library or not text:
            return []
        category = self._domain_to_category(domain)
        return self.primitive_library.query(
            text=text,
            top_k=top_k,
            category=category,
            min_score=min_score
        )

    def _domain_to_category(self, domain: Optional[str]) -> Optional[PrimitiveCategory]:
        if not domain:
            return None
        domain = domain.lower()
        if 'elect' in domain:
            return PrimitiveCategory.ELECTRONICS
        if 'mech' in domain or 'phys' in domain:
            return PrimitiveCategory.MECHANICS
        if 'chem' in domain:
            return PrimitiveCategory.CHEMISTRY
        if 'bio' in domain:
            return PrimitiveCategory.BIOLOGY
        if 'cs' in domain or 'computer' in domain:
            return PrimitiveCategory.COMPUTER_SCIENCE
        return None

    def normalize_entities(self, diagram_plan: Any) -> List[Dict[str, Any]]:
        entities = getattr(diagram_plan, 'extracted_entities', None)
        if not entities:
            entities = getattr(diagram_plan, 'entities', None)
        return list(entities or [])

    def normalize_relations(self, diagram_plan: Any) -> List[Dict[str, Any]]:
        relations = getattr(diagram_plan, 'extracted_relations', None)
        if not relations:
            relations = getattr(diagram_plan, 'relationships', None)
        return list(relations or [])

    @abstractmethod
    def build_artifact(
        self,
        domain: str,
        diagram_plan: Any,
        spec: Optional[Any] = None,
        property_graph: Optional[Any] = None,
        scene: Optional[Any] = None,
    ) -> Optional[DomainModuleArtifact]:
        """Generate a domain-specific artifact."""
        raise NotImplementedError
