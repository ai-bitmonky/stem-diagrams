"""
Specialized Domain Renderers
============================

High-quality domain-specific rendering using specialized libraries:

Physics:
- PySketcher: Python-based sketching for mechanics diagrams
- Manim: Mathematical animation engine (for advanced visualizations)
- PyBullet: Physics simulation (for dynamic diagrams)

Electronics/Circuits:
- SchemDraw: Professional circuit diagram generation
- CircuitikZ: LaTeX-based circuit diagrams (via TikZ)

Chemistry:
- RDKit: Molecular structure visualization
- ChemFig: LaTeX-based chemical structures

Mathematics:
- TikZ: Professional mathematical diagrams
- GeoGebra: Interactive geometry (API-based)

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class RendererDomain(Enum):
    """Domain categories for specialized renderers"""
    PHYSICS = "physics"
    ELECTRONICS = "electronics"
    CHEMISTRY = "chemistry"
    MATHEMATICS = "mathematics"
    GEOMETRY = "geometry"


@dataclass
class RendererCapabilities:
    """Capabilities of a specialized renderer"""
    name: str
    domain: RendererDomain
    library: str
    output_formats: List[str]  # e.g., ['svg', 'png', 'tikz', 'pdf']
    supported_diagram_types: List[str]
    requires_install: bool
    install_command: str
    description: str


class BaseSpecializedRenderer:
    """Base class for specialized domain renderers"""

    def __init__(self):
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if the required library is installed"""
        raise NotImplementedError

    def get_capabilities(self) -> RendererCapabilities:
        """Get renderer capabilities"""
        raise NotImplementedError

    def can_render(self, diagram_type: str, domain: str) -> bool:
        """Check if this renderer can handle the given diagram type"""
        raise NotImplementedError

    def render(
        self,
        scene_data: Dict[str, Any],
        output_format: str = 'svg'
    ) -> Optional[str]:
        """
        Render diagram using specialized library

        Args:
            scene_data: Universal scene format data
            output_format: Desired output format

        Returns:
            Rendered output (SVG string, file path, or None if failed)
        """
        raise NotImplementedError


# Module-level availability tracking
_available_renderers: Dict[str, BaseSpecializedRenderer] = {}


def register_renderer(name: str, renderer: BaseSpecializedRenderer):
    """Register a specialized renderer"""
    global _available_renderers
    if renderer.available:
        _available_renderers[name] = renderer
        print(f"✅ Registered specialized renderer: {name}")
    else:
        print(f"⚠️  Specialized renderer '{name}' not available (library not installed)")


def get_available_renderers() -> Dict[str, BaseSpecializedRenderer]:
    """Get all available specialized renderers"""
    return _available_renderers.copy()


def get_renderer_for_diagram(diagram_type: str, domain: str) -> Optional[BaseSpecializedRenderer]:
    """Find the best renderer for a given diagram type and domain"""
    for renderer in _available_renderers.values():
        if renderer.can_render(diagram_type, domain):
            return renderer
    return None
