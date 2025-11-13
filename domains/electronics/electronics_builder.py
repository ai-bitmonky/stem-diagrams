"""
Electronics Domain Scene Builder
=================================

Specialized scene builder for electronics/circuit diagrams.
Migrated from AdvancedSceneBuilder with enhanced capabilities.
"""

from typing import Dict, List
from core.domain_registry import DomainSceneBuilder, DomainCapabilities, SupportedDomain
from core.advanced_scene_builder import AdvancedSceneBuilder
from core.universal_scene_format import UniversalScene


class ElectronicsSceneBuilder(DomainSceneBuilder):
    """
    Electronics/Circuit diagram builder

    Supports:
    - Capacitor circuits (series, parallel)
    - Resistor circuits
    - Battery/power sources
    - Detailed physical representations
    """

    def __init__(self):
        self.advanced_builder = AdvancedSceneBuilder()

    def get_capabilities(self) -> DomainCapabilities:
        return DomainCapabilities(
            domain=SupportedDomain.ELECTRONICS,
            name="Electronics & Circuits",
            description="Circuit diagrams, capacitors, resistors, batteries",
            supported_diagram_types=[
                "circuit_diagram",
                "capacitor_circuit",
                "resistor_network",
                "rc_circuit",
                "rlc_circuit"
            ],
            keywords=[
                "capacitor", "capacitance", "resistor", "resistance",
                "battery", "voltage", "current", "circuit", "series",
                "parallel", "charge", "electric field", "dielectric",
                "ohm", "ampere", "volt", "farad"
            ],
            dependencies=[],  # No external deps for basic circuits
            maturity="production",  # Fully implemented
            examples=[
                "Series capacitor circuit with 2.00 μF and 8.00 μF",
                "Parallel-plate capacitor with dielectric",
                "RC circuit with time constant"
            ]
        )

    def can_handle(self, nlp_results: Dict, problem_text: str) -> float:
        """
        Determine if this is an electronics problem

        Returns confidence score 0.0-1.0
        """
        text_lower = problem_text.lower()
        caps = self.get_capabilities()

        # Count keyword matches
        keyword_matches = sum(1 for kw in caps.keywords if kw in text_lower)

        # Check domain from NLP
        domain_match = nlp_results.get('domain', '').lower() in ['electronics', 'electrical', 'capacitance']

        # Calculate confidence
        keyword_confidence = min(keyword_matches / 5.0, 1.0)  # Max at 5 keywords
        domain_confidence = 1.0 if domain_match else 0.0

        # Weighted average
        confidence = 0.6 * keyword_confidence + 0.4 * domain_confidence

        return confidence

    def build_scene(self, nlp_results: Dict, problem_text: str) -> UniversalScene:
        """Build electronics scene using advanced builder"""
        # Delegate to existing AdvancedSceneBuilder which has full implementation
        return self.advanced_builder.build_capacitor_scene(nlp_results, problem_text)

    def validate_scene(self, scene: UniversalScene) -> List[str]:
        """Electronics-specific validation"""
        warnings = []

        # Check for power source
        has_battery = any(obj.object_type.value == 'battery' for obj in scene.objects)
        if not has_battery:
            warnings.append("Circuit missing power source (battery)")

        # Check for at least one component
        component_types = ['capacitor', 'resistor', 'inductor']
        has_component = any(
            any(comp_type in obj.id.lower() or comp_type in str(obj.object_type).lower()
                for comp_type in component_types)
            for obj in scene.objects
        )
        if not has_component:
            warnings.append("Circuit missing electronic components")

        # Check connections
        if len(scene.relationships) == 0:
            warnings.append("No connections between components")

        return warnings
