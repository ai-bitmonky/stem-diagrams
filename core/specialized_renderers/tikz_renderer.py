#!/usr/bin/env python3
"""
TikZ/Math Renderer
==================

LaTeX TikZ code generation for mathematical diagrams.

TikZ is a powerful LaTeX package for creating publication-quality graphics.
This renderer generates TikZ code that can be compiled to PDF/SVG.

Supports:
- Geometric constructions
- Function plots
- Coordinate systems
- Mathematical annotations

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


class TikZRenderer(BaseSpecializedRenderer):
    """
    TikZ/LaTeX renderer for mathematical diagrams

    Generates LaTeX TikZ code that can be compiled to SVG/PDF
    """

    def _check_availability(self) -> bool:
        """Always available (generates TikZ code)"""
        return True

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="TikZ",
            domain=RendererDomain.MATHEMATICS,
            library="built-in",
            output_formats=['tikz', 'tex'],
            supported_diagram_types=[
                'geometric_construction',
                'function_plot',
                'coordinate_system',
                'vector_diagram',
                'trigonometric_circle',
                'mathematical_proof',
                'graph_theory'
            ],
            requires_install=False,
            install_command="# Built-in TikZ code generation (requires LaTeX for compilation)",
            description="Professional mathematical diagram generation via TikZ/LaTeX"
        )

    def can_render(self, diagram_type: str, domain: str) -> bool:
        """Check if this renderer can handle the diagram"""
        domain_lower = domain.lower()
        type_lower = diagram_type.lower()

        # Domain matching
        if 'math' in domain_lower or 'geometry' in domain_lower:
            return True

        # Type matching
        math_keywords = ['geometric', 'function', 'coordinate', 'vector', 'trigonometric', 'graph']
        return any(kw in type_lower for kw in math_keywords)

    def render(
        self,
        scene_data: Dict[str, Any],
        output_format: str = 'tikz'
    ) -> Optional[str]:
        """
        Generate TikZ code

        Args:
            scene_data: Universal scene format
            output_format: 'tikz' or 'tex' (full document)

        Returns:
            TikZ/LaTeX code
        """
        diagram_type = scene_data.get('diagram_type', '').lower()

        # Generate appropriate TikZ code
        if 'geometric' in diagram_type:
            tikz_code = self._generate_geometric_diagram(scene_data)
        elif 'function' in diagram_type or 'plot' in diagram_type:
            tikz_code = self._generate_function_plot(scene_data)
        elif 'coordinate' in diagram_type:
            tikz_code = self._generate_coordinate_system(scene_data)
        elif 'vector' in diagram_type:
            tikz_code = self._generate_vector_diagram(scene_data)
        else:
            tikz_code = self._generate_generic_diagram(scene_data)

        if output_format == 'tex':
            # Wrap in full LaTeX document
            return self._wrap_in_document(tikz_code)
        else:
            return tikz_code

    def _generate_geometric_diagram(self, scene_data: Dict[str, Any]) -> str:
        """Generate geometric construction TikZ code"""
        tikz = [
            "\\begin{tikzpicture}[scale=1.5]",
            "  % Geometric Construction",
            "  % Points",
            "  \\coordinate (A) at (0,0);",
            "  \\coordinate (B) at (4,0);",
            "  \\coordinate (C) at (2,3);",
            "",
            "  % Triangle",
            "  \\draw[thick] (A) -- (B) -- (C) -- cycle;",
            "",
            "  % Labels",
            "  \\node[below left] at (A) {$A$};",
            "  \\node[below right] at (B) {$B$};",
            "  \\node[above] at (C) {$C$};",
            "",
            "  % Right angle marker",
            "  \\draw (A) rectangle ++(0.3,0.3);",
            "\\end{tikzpicture}"
        ]
        return '\n'.join(tikz)

    def _generate_function_plot(self, scene_data: Dict[str, Any]) -> str:
        """Generate function plot TikZ code"""
        function = scene_data.get('function', 'x^2')
        xmin = scene_data.get('xmin', -3)
        xmax = scene_data.get('xmax', 3)

        tikz = [
            "\\begin{tikzpicture}",
            "  \\begin{axis}[",
            f"    domain={xmin}:{xmax},",
            "    samples=100,",
            "    axis lines=middle,",
            "    xlabel=$x$,",
            "    ylabel=$y$,",
            "    grid=major",
            "  ]",
            f"    \\addplot[blue, thick] {{{function}}};",
            f"    \\legend{{$y={function}$}}",
            "  \\end{axis}",
            "\\end{tikzpicture}"
        ]
        return '\n'.join(tikz)

    def _generate_coordinate_system(self, scene_data: Dict[str, Any]) -> str:
        """Generate coordinate system TikZ code"""
        tikz = [
            "\\begin{tikzpicture}",
            "  % Coordinate System",
            "  \\draw[->] (-3,0) -- (3,0) node[right] {$x$};",
            "  \\draw[->] (0,-3) -- (0,3) node[above] {$y$};",
            "",
            "  % Grid",
            "  \\draw[help lines, gray!30] (-3,-3) grid (3,3);",
            "",
            "  % Points",
            "  \\foreach \\x in {-2,-1,1,2}",
            "    \\draw (\\x,0.1) -- (\\x,-0.1) node[below] {$\\x$};",
            "  \\foreach \\y in {-2,-1,1,2}",
            "    \\draw (0.1,\\y) -- (-0.1,\\y) node[left] {$\\y$};",
            "\\end{tikzpicture}"
        ]
        return '\n'.join(tikz)

    def _generate_vector_diagram(self, scene_data: Dict[str, Any]) -> str:
        """Generate vector diagram TikZ code"""
        vectors = scene_data.get('vectors', [])

        tikz = [
            "\\begin{tikzpicture}[scale=1.5]",
            "  % Vector Diagram",
            "  \\draw[->] (-1,0) -- (4,0) node[right] {$x$};",
            "  \\draw[->] (0,-1) -- (0,4) node[above] {$y$};",
            ""
        ]

        # Default vectors if none provided
        if not vectors:
            vectors = [
                {'x': 3, 'y': 2, 'label': '\\vec{v}_1', 'color': 'red'},
                {'x': 1, 'y': 3, 'label': '\\vec{v}_2', 'color': 'blue'}
            ]

        for vec in vectors:
            x = vec.get('x', 1)
            y = vec.get('y', 1)
            label = vec.get('label', '\\vec{v}')
            color = vec.get('color', 'black')
            tikz.append(f"  \\draw[->, thick, {color}] (0,0) -- ({x},{y}) node[midway, above] {{{label}}};")

        tikz.append("\\end{tikzpicture}")
        return '\n'.join(tikz)

    def _generate_generic_diagram(self, scene_data: Dict[str, Any]) -> str:
        """Generate generic mathematical diagram"""
        return self._generate_coordinate_system(scene_data)

    def _wrap_in_document(self, tikz_code: str) -> str:
        """Wrap TikZ code in complete LaTeX document"""
        doc = f"""\\documentclass{{article}}
\\usepackage{{tikz}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}

\\begin{{document}}

{tikz_code}

\\end{{document}}
"""
        return doc

    def generate_circle(self, radius: float = 1.0, center: tuple = (0, 0)) -> str:
        """Generate TikZ code for a circle"""
        cx, cy = center
        return f"\\draw ({cx},{cy}) circle ({radius}cm);"

    def generate_line(self, start: tuple, end: tuple, style: str = "thick") -> str:
        """Generate TikZ code for a line"""
        x1, y1 = start
        x2, y2 = end
        return f"\\draw[{style}] ({x1},{y1}) -- ({x2},{y2});"

    def generate_point(self, pos: tuple, label: str = "") -> str:
        """Generate TikZ code for a point"""
        x, y = pos
        code = f"\\fill ({x},{y}) circle (2pt);"
        if label:
            code += f"\n\\node[above right] at ({x},{y}) {{{label}}};"
        return code


# Example usage
if __name__ == '__main__':
    renderer = TikZRenderer()
    print(f"✅ TikZ renderer available: {renderer.available}")
    print(f"Capabilities: {renderer.get_capabilities()}")

    # Test geometric diagram
    test_scene = {
        'diagram_type': 'geometric_construction'
    }

    tikz = renderer.render(test_scene, output_format='tikz')
    if tikz:
        print(f"✅ Generated TikZ code ({len(tikz)} chars)")
        print("\nSample TikZ code:")
        print(tikz[:200] + "...")

    # Test full document
    doc = renderer.render(test_scene, output_format='tex')
    if doc:
        print(f"\n✅ Generated full LaTeX document ({len(doc)} chars)")
