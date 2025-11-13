#!/usr/bin/env python3
"""
Specialized Renderer Registry
==============================

Central registry for all specialized domain renderers.

Automatically discovers and registers available renderers,
providing a unified interface for accessing domain-specific
rendering capabilities.

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from . import BaseSpecializedRenderer, RendererDomain, get_available_renderers, register_renderer


@dataclass
class RendererInfo:
    """Information about a registered renderer"""
    name: str
    domain: RendererDomain
    available: bool
    requires_install: bool
    install_command: str
    supported_diagram_types: List[str]


class SpecializedRendererRegistry:
    """
    Central registry for specialized renderers

    Usage:
        registry = SpecializedRendererRegistry()
        registry.initialize()  # Discovers and registers all renderers

        # Get renderer for a specific diagram
        renderer = registry.get_renderer_for_diagram('circuit', 'electronics')

        # List all available renderers
        available = registry.list_available_renderers()
    """

    def __init__(self):
        self._renderers: Dict[str, BaseSpecializedRenderer] = {}
        self._initialized = False

    def initialize(self):
        """
        Initialize and register all available renderers

        This imports and registers:
        - SchemDrawRenderer (electronics)
        - RDKitRenderer (chemistry)
        - PhysicsDiagramRenderer (physics)
        - TikZRenderer (mathematics)
        """
        if self._initialized:
            return

        print("Initializing specialized renderers...")

        # Import and register SchemDraw
        try:
            from .schemdraw_renderer import SchemDrawRenderer
            renderer = SchemDrawRenderer()
            self._register(renderer, 'schemdraw')
        except Exception as e:
            print(f"  ⚠️  SchemDraw: {e}")

        # Import and register RDKit
        try:
            from .rdkit_renderer import RDKitRenderer
            renderer = RDKitRenderer()
            self._register(renderer, 'rdkit')
        except Exception as e:
            print(f"  ⚠️  RDKit: {e}")

        # Import and register Physics
        try:
            from .physics_renderers import PhysicsDiagramRenderer
            renderer = PhysicsDiagramRenderer()
            self._register(renderer, 'physics')
        except Exception as e:
            print(f"  ⚠️  Physics: {e}")

        # Import and register TikZ
        try:
            from .tikz_renderer import TikZRenderer
            renderer = TikZRenderer()
            self._register(renderer, 'tikz')
        except Exception as e:
            print(f"  ⚠️  TikZ: {e}")

        self._initialized = True
        print(f"✅ Specialized renderers initialized: {len(self._renderers)} available")

    def _register(self, renderer: BaseSpecializedRenderer, name: str):
        """Register a renderer"""
        if renderer.available:
            self._renderers[name] = renderer
            caps = renderer.get_capabilities()
            print(f"  ✅ {caps.name}: {len(caps.supported_diagram_types)} diagram types")
        else:
            caps = renderer.get_capabilities()
            print(f"  ⚠️  {caps.name}: Not available (install: {caps.install_command})")

    def get_renderer_for_diagram(
        self,
        diagram_type: str,
        domain: str
    ) -> Optional[BaseSpecializedRenderer]:
        """
        Find the best renderer for a diagram type and domain

        Args:
            diagram_type: Type of diagram (e.g., 'circuit', 'molecule')
            domain: Domain (e.g., 'electronics', 'chemistry')

        Returns:
            Specialized renderer or None if not available
        """
        if not self._initialized:
            self.initialize()

        for renderer in self._renderers.values():
            if renderer.can_render(diagram_type, domain):
                return renderer

        return None

    def get_renderer_by_name(self, name: str) -> Optional[BaseSpecializedRenderer]:
        """Get a specific renderer by name"""
        if not self._initialized:
            self.initialize()

        return self._renderers.get(name.lower())

    def list_available_renderers(self) -> List[RendererInfo]:
        """List all available renderers"""
        if not self._initialized:
            self.initialize()

        result = []
        for name, renderer in self._renderers.items():
            caps = renderer.get_capabilities()
            result.append(RendererInfo(
                name=caps.name,
                domain=caps.domain,
                available=renderer.available,
                requires_install=caps.requires_install,
                install_command=caps.install_command,
                supported_diagram_types=caps.supported_diagram_types
            ))

        return result

    def get_supported_diagram_types(self, domain: Optional[str] = None) -> List[str]:
        """
        Get all supported diagram types, optionally filtered by domain

        Args:
            domain: Optional domain filter

        Returns:
            List of supported diagram types
        """
        if not self._initialized:
            self.initialize()

        types = set()
        for renderer in self._renderers.values():
            caps = renderer.get_capabilities()
            if domain is None or caps.domain.value == domain.lower():
                types.update(caps.supported_diagram_types)

        return sorted(list(types))

    def render_diagram(
        self,
        scene_data: Dict[str, Any],
        diagram_type: str,
        domain: str,
        output_format: str = 'svg'
    ) -> Optional[str]:
        """
        Render a diagram using the appropriate specialized renderer

        Args:
            scene_data: Universal scene format data
            diagram_type: Type of diagram
            domain: Domain
            output_format: Desired output format

        Returns:
            Rendered diagram or None if failed
        """
        renderer = self.get_renderer_for_diagram(diagram_type, domain)
        if renderer:
            try:
                return renderer.render(scene_data, output_format)
            except Exception as e:
                print(f"❌ Rendering failed with {renderer.get_capabilities().name}: {e}")
                return None
        else:
            print(f"⚠️  No specialized renderer available for {diagram_type} ({domain})")
            return None


# Global registry instance
_global_registry = None


def get_registry() -> SpecializedRendererRegistry:
    """Get the global renderer registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = SpecializedRendererRegistry()
        _global_registry.initialize()
    return _global_registry


# Example usage and testing
if __name__ == '__main__':
    print("="*80)
    print("Specialized Renderer Registry Test")
    print("="*80)

    # Initialize registry
    registry = SpecializedRendererRegistry()
    registry.initialize()

    print(f"\n{'='*80}")
    print("Available Renderers")
    print("="*80)

    # List available renderers
    for info in registry.list_available_renderers():
        status = "✅ Available" if info.available else "❌ Not installed"
        print(f"\n{info.name} ({info.domain.value}): {status}")
        print(f"  Diagram types: {', '.join(info.supported_diagram_types[:5])}")
        if len(info.supported_diagram_types) > 5:
            print(f"                 ... and {len(info.supported_diagram_types) - 5} more")
        if not info.available:
            print(f"  Install: {info.install_command}")

    print(f"\n{'='*80}")
    print("Supported Diagram Types by Domain")
    print("="*80)

    for domain in ['electronics', 'chemistry', 'physics', 'mathematics']:
        types = registry.get_supported_diagram_types(domain)
        if types:
            print(f"\n{domain.title()}: {len(types)} types")
            print(f"  {', '.join(types[:10])}")
            if len(types) > 10:
                print(f"  ... and {len(types) - 10} more")

    print(f"\n{'='*80}")
    print("Test Rendering")
    print("="*80)

    # Test physics diagram (always available)
    print("\n Testing physics free body diagram...")
    test_scene = {
        'diagram_type': 'free_body_diagram',
        'forces': [{'type': 'gravity'}, {'type': 'normal'}]
    }
    svg = registry.render_diagram(test_scene, 'free_body_diagram', 'physics')
    if svg:
        print(f"✅ Generated diagram ({len(svg)} chars)")
    else:
        print("❌ Failed to generate diagram")

    print(f"\n{'='*80}")
    print("✅ Registry test complete")
    print("="*80)
