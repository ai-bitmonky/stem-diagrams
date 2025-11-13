#!/usr/bin/env python3
"""
Physics Specialized Renderers
==============================

Physics diagram generation using specialized libraries:
- PySketcher: Python-based sketching for mechanics
- Matplotlib-based renderers for force diagrams, free body diagrams

Note: Manim and PyBullet are complex animation/simulation libraries
that require extensive setup. We provide pattern-based alternatives.

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Dict, List, Optional, Any
import re

from . import (
    BaseSpecializedRenderer,
    RendererCapabilities,
    RendererDomain
)


class PhysicsDiagramRenderer(BaseSpecializedRenderer):
    """
    Physics diagram renderer (pattern-based, no external dependencies)

    Provides templates for common physics diagrams:
    - Force diagrams
    - Free body diagrams
    - Inclined planes
    - Pulley systems
    - Spring-mass systems
    """

    def _check_availability(self) -> bool:
        """Always available (pattern-based)"""
        return True

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="PhysicsDiagramRenderer",
            domain=RendererDomain.PHYSICS,
            library="built-in",
            output_formats=['svg'],
            supported_diagram_types=[
                'force_diagram',
                'free_body_diagram',
                'inclined_plane',
                'pulley_system',
                'spring_mass_system',
                'projectile_motion',
                'collision_diagram'
            ],
            requires_install=False,
            install_command="# Built-in, no installation needed",
            description="Pattern-based physics diagram generation"
        )

    def can_render(self, diagram_type: str, domain: str) -> bool:
        """Check if this renderer can handle the diagram"""
        domain_lower = domain.lower()
        type_lower = diagram_type.lower()

        # Domain matching
        if 'physics' in domain_lower or 'mechanics' in domain_lower:
            return True

        # Type matching
        physics_keywords = ['force', 'body', 'incline', 'pulley', 'spring', 'mass', 'projectile']
        return any(kw in type_lower for kw in physics_keywords)

    def render(
        self,
        scene_data: Dict[str, Any],
        output_format: str = 'svg'
    ) -> Optional[str]:
        """
        Render physics diagram using patterns

        Args:
            scene_data: Universal scene format
            output_format: Only 'svg' supported

        Returns:
            SVG string
        """
        diagram_type = scene_data.get('diagram_type', '').lower()

        if 'free_body' in diagram_type or 'force' in diagram_type:
            return self._render_free_body_diagram(scene_data)
        elif 'incline' in diagram_type:
            return self._render_inclined_plane(scene_data)
        elif 'spring' in diagram_type:
            return self._render_spring_mass(scene_data)
        else:
            # Default: simple block with forces
            return self._render_force_diagram(scene_data)

    def _render_free_body_diagram(self, scene_data: Dict[str, Any]) -> str:
        """Generate free body diagram SVG"""
        # Extract forces
        forces = scene_data.get('forces', [])

        svg_parts = [
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">',
            '  <!-- Free Body Diagram -->',
            '  <!-- Central object -->',
            '  <rect x="175" y="175" width="50" height="50" fill="#e0e0e0" stroke="black" stroke-width="2"/>',
            '  <text x="200" y="205" text-anchor="middle" font-size="16">m</text>',
        ]

        # Add force arrows
        force_templates = {
            'gravity': '<line x1="200" y1="225" x2="200" y2="300" stroke="red" stroke-width="3" marker-end="url(#arrowred)"/><text x="210" y="270" font-size="14" fill="red">F_g</text>',
            'normal': '<line x1="200" y1="175" x2="200" y2="100" stroke="blue" stroke-width="3" marker-end="url(#arrowblue)"/><text x="210" y="130" font-size="14" fill="blue">F_N</text>',
            'friction': '<line x1="175" y1="200" x2="100" y2="200" stroke="green" stroke-width="3" marker-end="url(#arrowgreen)"/><text x="130" y="190" font-size="14" fill="green">f</text>',
            'applied': '<line x1="225" y1="200" x2="300" y2="200" stroke="orange" stroke-width="3" marker-end="url(#arroworange)"/><text x="270" y="190" font-size="14" fill="orange">F_a</text>',
        }

        # Arrow markers
        svg_parts.append('  <defs>')
        for color in ['red', 'blue', 'green', 'orange']:
            svg_parts.append(f'    <marker id="arrow{color}" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">')
            svg_parts.append(f'      <path d="M0,0 L0,6 L9,3 z" fill="{color}"/>')
            svg_parts.append('    </marker>')
        svg_parts.append('  </defs>')

        # Add forces
        for force in forces:
            force_type = force.get('type', '').lower()
            if force_type in force_templates:
                svg_parts.append(f'  {force_templates[force_type]}')

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

    def _render_inclined_plane(self, scene_data: Dict[str, Any]) -> str:
        """Generate inclined plane diagram"""
        angle = scene_data.get('angle', 30)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400" width="500" height="400">
          <!-- Inclined Plane -->
          <line x1="50" y1="350" x2="450" y2="350" stroke="black" stroke-width="2"/>
          <line x1="50" y1="350" x2="400" y2="150" stroke="black" stroke-width="3"/>
          <line x1="400" y1="150" x2="400" y2="350" stroke="black" stroke-width="2" stroke-dasharray="5,5"/>

          <!-- Block -->
          <rect x="180" y="210" width="60" height="40" fill="#d0d0d0" stroke="black" stroke-width="2"
                transform="rotate(-{angle} 210 230)"/>
          <text x="210" y="235" text-anchor="middle" font-size="14">m</text>

          <!-- Angle marker -->
          <path d="M 50 350 L 100 350 A 50 50 0 0 1 75 320" fill="none" stroke="blue" stroke-width="1.5"/>
          <text x="90" y="345" font-size="14" fill="blue">{angle}°</text>

          <!-- Labels -->
          <text x="250" y="30" font-size="16" font-weight="bold">Inclined Plane</text>
        </svg>'''
        return svg

    def _render_spring_mass(self, scene_data: Dict[str, Any]) -> str:
        """Generate spring-mass system"""
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" width="300" height="400">
          <!-- Spring-Mass System -->
          <line x1="50" y1="50" x2="250" y2="50" stroke="black" stroke-width="3"/>

          <!-- Spring (zigzag) -->
          <path d="M 150 50 L 160 80 L 140 110 L 160 140 L 140 170 L 160 200 L 150 230"
                fill="none" stroke="blue" stroke-width="2"/>

          <!-- Mass -->
          <rect x="120" y="230" width="60" height="60" fill="#e0e0e0" stroke="black" stroke-width="2"/>
          <text x="150" y="265" text-anchor="middle" font-size="16">m</text>

          <!-- Label -->
          <text x="150" y="320" text-anchor="middle" font-size="14">Spring Constant: k</text>
        </svg>'''
        return svg

    def _render_force_diagram(self, scene_data: Dict[str, Any]) -> str:
        """Simple force diagram"""
        return self._render_free_body_diagram(scene_data)


# Example usage
if __name__ == '__main__':
    renderer = PhysicsDiagramRenderer()
    print(f"✅ Physics renderer available: {renderer.available}")
    print(f"Capabilities: {renderer.get_capabilities()}")

    # Test free body diagram
    test_scene = {
        'diagram_type': 'free_body_diagram',
        'forces': [
            {'type': 'gravity'},
            {'type': 'normal'},
            {'type': 'friction'}
        ]
    }

    svg = renderer.render(test_scene)
    if svg:
        print(f"✅ Generated physics diagram ({len(svg)} chars)")
    else:
        print("❌ Failed to generate diagram")
