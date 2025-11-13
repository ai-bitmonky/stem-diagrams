"""
Domain Registry - Multi-Domain Support Framework
=================================================

Pluggable domain system for Universal STEM Diagram Generator.
Supports: Electronics, Physics, Chemistry, Mathematics, Biology, CS, Mechanical

Priority 1 CRITICAL feature from roadmap alignment analysis.
"""

from typing import Dict, Type, Optional, List
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod

from core.universal_scene_format import UniversalScene


class SupportedDomain(Enum):
    """Supported STEM domains"""
    ELECTRONICS = "electronics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    MATHEMATICS = "mathematics"
    BIOLOGY = "biology"
    COMPUTER_SCIENCE = "computer_science"
    MECHANICAL = "mechanical"


@dataclass
class DomainCapabilities:
    """Capabilities and metadata for a domain"""
    domain: SupportedDomain
    name: str
    description: str
    supported_diagram_types: List[str]
    keywords: List[str]
    dependencies: List[str]  # External libraries required
    maturity: str  # 'production', 'beta', 'alpha', 'stub'
    examples: List[str]


class DomainSceneBuilder(ABC):
    """
    Abstract base class for domain-specific scene builders

    Each domain implements this interface to provide specialized
    scene building logic for that domain's diagrams.
    """

    @abstractmethod
    def get_capabilities(self) -> DomainCapabilities:
        """Return domain capabilities and metadata"""
        pass

    @abstractmethod
    def can_handle(self, nlp_results: Dict, problem_text: str) -> float:
        """
        Determine if this builder can handle the problem

        Returns:
            Confidence score 0.0-1.0
        """
        pass

    @abstractmethod
    def build_scene(self, nlp_results: Dict, problem_text: str) -> UniversalScene:
        """Build scene for this domain"""
        pass

    @abstractmethod
    def validate_scene(self, scene: UniversalScene) -> List[str]:
        """Domain-specific validation, returns list of warnings/errors"""
        pass


class DomainRegistry:
    """
    Central registry for all domain-specific scene builders

    Usage:
        registry = DomainRegistry()
        registry.register(ElectronicsSceneBuilder())
        registry.register(PhysicsSceneBuilder())

        builder = registry.get_builder_for_problem(nlp_results, text)
        scene = builder.build_scene(nlp_results, text)
    """

    def __init__(self):
        self._builders: Dict[SupportedDomain, DomainSceneBuilder] = {}
        self._load_default_builders()

    def _load_default_builders(self):
        """Load all available domain builders"""
        # Import and register domain builders
        try:
            from domains.electronics.electronics_builder import ElectronicsSceneBuilder
            self.register(ElectronicsSceneBuilder())
        except ImportError:
            print("⚠️  Electronics domain builder not available")

        try:
            from domains.physics.physics_builder import PhysicsSceneBuilder
            self.register(PhysicsSceneBuilder())
        except ImportError:
            print("⚠️  Physics domain builder not available (stub)")

        try:
            from domains.chemistry.chemistry_builder import ChemistrySceneBuilder
            self.register(ChemistrySceneBuilder())
        except ImportError:
            print("⚠️  Chemistry domain builder not available (stub)")

        try:
            from domains.mathematics.math_builder import MathematicsSceneBuilder
            self.register(MathematicsSceneBuilder())
        except ImportError:
            print("⚠️  Mathematics domain builder not available (stub)")

    def register(self, builder: DomainSceneBuilder):
        """Register a domain builder"""
        caps = builder.get_capabilities()
        self._builders[caps.domain] = builder
        print(f"✅ Registered domain: {caps.name} ({caps.maturity})")

    def get_builder(self, domain: SupportedDomain) -> Optional[DomainSceneBuilder]:
        """Get builder for specific domain"""
        return self._builders.get(domain)

    def get_builder_for_problem(self, nlp_results: Dict, problem_text: str) -> DomainSceneBuilder:
        """
        Automatically select best builder for the problem

        Returns the builder with highest confidence score
        """
        best_builder = None
        best_score = 0.0

        for domain, builder in self._builders.items():
            score = builder.can_handle(nlp_results, problem_text)
            if score > best_score:
                best_score = score
                best_builder = builder

        if best_builder is None:
            raise ValueError("No suitable domain builder found for problem")

        caps = best_builder.get_capabilities()
        print(f"🎯 Selected domain: {caps.name} (confidence: {best_score:.2f})")

        return best_builder

    def list_domains(self) -> List[DomainCapabilities]:
        """List all registered domains"""
        return [builder.get_capabilities() for builder in self._builders.values()]

    def get_domain_status(self) -> Dict[str, str]:
        """Get maturity status of all domains"""
        return {
            caps.name: caps.maturity
            for caps in self.list_domains()
        }


# Global registry instance
_global_registry = None


def get_domain_registry() -> DomainRegistry:
    """Get global domain registry singleton"""
    global _global_registry
    if _global_registry is None:
        _global_registry = DomainRegistry()
    return _global_registry


if __name__ == "__main__":
    # Test domain registry
    print("=" * 80)
    print("DOMAIN REGISTRY TEST")
    print("=" * 80)

    registry = get_domain_registry()

    print("\n📋 Registered domains:")
    for caps in registry.list_domains():
        print(f"  • {caps.name}: {caps.maturity}")
        print(f"    Keywords: {', '.join(caps.keywords[:5])}")
        print(f"    Types: {', '.join(caps.supported_diagram_types)}")
        print()

    print("🎯 Domain status:")
    for domain, status in registry.get_domain_status().items():
        print(f"  • {domain}: {status}")
