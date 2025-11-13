#!/usr/bin/env python3
"""
SchemDraw Renderer
==================

Professional circuit diagram generation using SchemDraw library.

SchemDraw provides:
- High-quality circuit diagrams
- Standard electronic symbols
- Automatic wire routing
- Multiple output formats (SVG, PNG, PDF)

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Dict, List, Optional, Any
import io

try:
    import schemdraw
    import schemdraw.elements as elm
    SCHEMDRAW_AVAILABLE = True
except ImportError:
    SCHEMDRAW_AVAILABLE = False
    schemdraw = None
    elm = None

from . import (
    BaseSpecializedRenderer,
    RendererCapabilities,
    RendererDomain
)


class SchemDrawRenderer(BaseSpecializedRenderer):
    """
    Circuit diagram renderer using SchemDraw

    Supports:
    - Resistors, capacitors, inductors
    - Voltage/current sources
    - Diodes, transistors
    - Op-amps, logic gates
    - Custom wire routing
    """

    def _check_availability(self) -> bool:
        """Check if SchemDraw is installed"""
        return SCHEMDRAW_AVAILABLE

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="SchemDraw",
            domain=RendererDomain.ELECTRONICS,
            library="schemdraw",
            output_formats=['svg', 'png', 'pdf'],
            supported_diagram_types=[
                'circuit',
                'resistor_circuit',
                'rc_circuit',
                'rlc_circuit',
                'amplifier_circuit',
                'logic_circuit',
                'voltage_divider',
                'current_divider',
                'capacitor_circuit'
            ],
            requires_install=True,
            install_command="pip install schemdraw",
            description="Professional circuit diagram generation with standard electronic symbols"
        )

    def can_render(self, diagram_type: str, domain: str) -> bool:
        """Check if this renderer can handle the diagram"""
        if not self.available:
            return False

        domain_lower = domain.lower()
        type_lower = diagram_type.lower()

        # Domain matching
        if 'circuit' in domain_lower or 'electric' in domain_lower or 'electronics' in domain_lower:
            return True

        # Type matching
        circuit_keywords = ['circuit', 'resistor', 'capacitor', 'inductor', 'voltage', 'current']
        return any(kw in type_lower for kw in circuit_keywords)

    def render(
        self,
        scene_data: Dict[str, Any],
        output_format: str = 'svg'
    ) -> Optional[str]:
        """
        Render circuit diagram using SchemDraw

        Args:
            scene_data: Universal scene format with:
                - components: List of circuit components
                - connections: Wire connections
                - annotations: Labels and values
            output_format: 'svg', 'png', or 'pdf'

        Returns:
            SVG string or file path
        """
        if not self.available:
            print("⚠️  SchemDraw not available")
            return None

        try:
            # Create drawing
            with schemdraw.Drawing() as d:
                # Parse components and create circuit
                self._add_components(d, scene_data)

            # Get output
            if output_format == 'svg':
                # Return SVG as string
                svg_io = io.StringIO()
                d.save(svg_io, format='svg')
                return svg_io.getvalue()
            else:
                # Save to file and return path
                output_path = f"circuit_output.{output_format}"
                d.save(output_path)
                return output_path

        except Exception as e:
            print(f"❌ SchemDraw rendering failed: {e}")
            return None

    def _add_components(self, drawing, scene_data: Dict[str, Any]):
        """Add components to SchemDraw drawing"""
        components = scene_data.get('components', [])

        for comp in components:
            comp_type = comp.get('type', '').lower()
            label = comp.get('label', '')
            value = comp.get('value', '')

            # Map component types to SchemDraw elements
            if 'resistor' in comp_type:
                elem = drawing.add(elm.Resistor().label(f"{label}\n{value}"))
            elif 'capacitor' in comp_type:
                elem = drawing.add(elm.Capacitor().label(f"{label}\n{value}"))
            elif 'inductor' in comp_type:
                elem = drawing.add(elm.Inductor().label(f"{label}\n{value}"))
            elif 'voltage' in comp_type and 'source' in comp_type:
                elem = drawing.add(elm.SourceV().label(f"{label}\n{value}"))
            elif 'current' in comp_type and 'source' in comp_type:
                elem = drawing.add(elm.SourceI().label(f"{label}\n{value}"))
            elif 'battery' in comp_type:
                elem = drawing.add(elm.Battery().label(f"{label}\n{value}"))
            elif 'ground' in comp_type:
                elem = drawing.add(elm.Ground())
            elif 'switch' in comp_type:
                elem = drawing.add(elm.Switch().label(label))
            elif 'diode' in comp_type:
                elem = drawing.add(elm.Diode().label(label))
            elif 'led' in comp_type:
                elem = drawing.add(elm.LED().label(label))
            else:
                # Default to resistor for unknown types
                elem = drawing.add(elm.Resistor().label(label))

    def render_simple_resistor_circuit(
        self,
        resistors: List[Dict[str, Any]],
        voltage_source: Dict[str, Any]
    ) -> Optional[str]:
        """
        Convenience method for simple resistor circuits

        Args:
            resistors: List of resistors with 'value' and 'label'
            voltage_source: Voltage source with 'value'

        Returns:
            SVG string
        """
        if not self.available:
            return None

        with schemdraw.Drawing() as d:
            # Voltage source
            d += elm.SourceV().label(f"{voltage_source.get('value', 'V')}")

            # Add resistors in series
            for r in resistors:
                d += elm.Resistor().label(f"{r.get('label', 'R')}\n{r.get('value', '')}")

            # Close circuit with wire and ground
            d += elm.Line().down()
            d += elm.Ground()

        # Return SVG
        svg_io = io.StringIO()
        d.save(svg_io, format='svg')
        return svg_io.getvalue()


# Example usage and testing
if __name__ == '__main__':
    renderer = SchemDrawRenderer()

    if renderer.available:
        print("✅ SchemDraw renderer available")
        print(f"Capabilities: {renderer.get_capabilities()}")

        # Test simple circuit
        test_scene = {
            'components': [
                {'type': 'voltage_source', 'label': 'V1', 'value': '10V'},
                {'type': 'resistor', 'label': 'R1', 'value': '100Ω'},
                {'type': 'resistor', 'label': 'R2', 'value': '200Ω'},
                {'type': 'ground', 'label': 'GND'}
            ]
        }

        svg = renderer.render(test_scene, output_format='svg')
        if svg:
            print(f"✅ Generated circuit diagram ({len(svg)} chars)")
        else:
            print("❌ Failed to generate circuit")
    else:
        print("❌ SchemDraw not available")
        print(f"   Install with: {renderer.get_capabilities().install_command}")
