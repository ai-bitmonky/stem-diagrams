"""Registry for pluggable domain modules."""

from __future__ import annotations

from typing import Any, List, Optional

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import PrimitiveLibrary


class DomainModuleRegistry:
    """Keeps track of available domain modules and builds artifacts per domain."""

    def __init__(self, primitive_library: Optional[PrimitiveLibrary] = None, auto_register: bool = True):
        self._modules: List[DomainModule] = []
        self.primitive_library = primitive_library
        if auto_register:
            self._load_default_modules()

    def _load_default_modules(self) -> None:
        try:
            from core.domain_modules.electronics import ElectronicsSchemDrawModule
            self.register(ElectronicsSchemDrawModule())
        except Exception as exc:
            print(f"⚠️  Electronics module unavailable: {exc}")

        try:
            from core.domain_modules.mechanics import MechanicsPySketcherModule
            self.register(MechanicsPySketcherModule())
        except Exception as exc:
            print(f"⚠️  Mechanics module unavailable: {exc}")

        try:
            from core.domain_modules.chemistry import ChemistryRDKitModule
            self.register(ChemistryRDKitModule())
        except Exception as exc:
            print(f"⚠️  Chemistry module unavailable: {exc}")

        try:
            from core.domain_modules.biology import BiologyCytoscapeModule
            self.register(BiologyCytoscapeModule())
        except Exception as exc:
            print(f"⚠️  Biology module unavailable: {exc}")

        try:
            from core.domain_modules.computer_science import ComputerScienceDiagramModule
            self.register(ComputerScienceDiagramModule())
        except Exception as exc:
            print(f"⚠️  CS module unavailable: {exc}")

    def register(self, module: DomainModule) -> None:
        if self.primitive_library:
            module.set_primitive_library(self.primitive_library)
        self._modules.append(module)
        self._modules.sort(key=lambda m: m.priority, reverse=True)
        print(f"✓ Domain module registered: {module.display_name} (priority {module.priority})")

    def list_modules(self) -> List[str]:
        return [f"{module.module_id} ({module.display_name})" for module in self._modules]

    def build_artifacts(
        self,
        domain: Optional[str],
        diagram_plan: Any,
        spec: Any = None,
        property_graph: Any = None,
        scene: Any = None,
    ) -> List[DomainModuleArtifact]:
        if not domain or not diagram_plan:
            return []
        artifacts: List[DomainModuleArtifact] = []
        for module in self._modules:
            if not module.supports_domain(domain):
                continue
            artifact = module.build_artifact(
                domain=domain,
                diagram_plan=diagram_plan,
                spec=spec,
                property_graph=property_graph,
                scene=scene,
            )
            if artifact:
                artifacts.append(artifact)
        return artifacts
