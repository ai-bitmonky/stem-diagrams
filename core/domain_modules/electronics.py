"""Electronics domain module built on SchemDraw/CircuitikZ."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import DiagramPrimitive


class ElectronicsSchemDrawModule(DomainModule):
    module_id = "electronics_schemdraw"
    display_name = "SchemDraw/CircuitikZ"
    supported_domains = ["electronics", "current_electricity", "electrostatics"]
    priority = 50

    def __init__(self) -> None:
        super().__init__()
        try:
            import schemdraw  # type: ignore
            from schemdraw import elements as elm  # type: ignore
            self._schemdraw = schemdraw
            self._schemdraw_elements = elm
            self.available = True
        except Exception:
            self._schemdraw = None
            self._schemdraw_elements = None
            self.available = False

    def build_artifact(
        self,
        domain: str,
        diagram_plan: Any,
        spec: Any = None,
        property_graph: Any = None,
        scene: Any = None,
    ) -> DomainModuleArtifact | None:
        entities = self.normalize_entities(diagram_plan)
        relations = self.normalize_relations(diagram_plan)
        if not entities:
            return None

        svg_payload = self._build_svg_from_primitives(entities)
        if svg_payload:
            svg_content, match_count = svg_payload
            metadata: Dict[str, Any] = {
                'primitive_matches': match_count,
                'available': True,
                'component_count': len(entities)
            }
            return DomainModuleArtifact(
                module_id=f"{self.module_id}_svg",
                title="Electronics primitives (SVG)",
                format="svg",
                content=svg_content,
                description="SVG assembled from primitive library components (battery, resistor, capacitor, etc.).",
                metadata=metadata,
            )

        script = self._generate_schemdraw_script(entities, relations)
        latex = self._generate_circuitikz_snippet(entities, relations)
        content = (
            "# SchemDraw Python template\n" + script + "\n\n% CircuitikZ LaTeX template\n" + latex
        )

        metadata: Dict[str, Any] = {
            'available': self.available,
            'component_count': len(entities),
            'primitive_matches': 0,
        }
        if not self.available:
            metadata['warning'] = 'schemdraw not installed - generated template only'

        return DomainModuleArtifact(
            module_id=self.module_id,
            title="Electronics schematic templates",
            format="text",
            content=content,
            description="Templates for SchemDraw (Python) and CircuitikZ (LaTeX) generated from the property-graph plan.",
            metadata=metadata,
        )

    def _generate_schemdraw_script(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> str:
        lines = [
            "import schemdraw",
            "from schemdraw import elements as elm",
            "",
            "d = schemdraw.Drawing(file='schematic.svg')",
        ]

        # Simple left-to-right placement
        for index, ent in enumerate(entities):
            label = ent.get('label', ent.get('id', f'comp{index+1}'))
            comp_type = ent.get('type', 'component').lower()
            element = self._schemdraw_element_name(comp_type)
            lines.append(f"d += elm.{element}().label('{label}')")
            if index < len(entities) - 1:
                lines.append("d += elm.Line().right()")

        lines.append("d.draw()")
        return "\n".join(lines)

    def _schemdraw_element_name(self, comp_type: str) -> str:
        if 'res' in comp_type:
            return 'Resistor'
        if 'cap' in comp_type:
            return 'Capacitor'
        if 'ind' in comp_type:
            return 'Inductor'
        if 'battery' in comp_type or 'source' in comp_type:
            return 'SourceV'
        return 'Box'

    def _generate_circuitikz_snippet(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> str:
        latex_lines = [
            "\\begin{circuitikz}",
            "  \\draw",
        ]
        for index, ent in enumerate(entities):
            label = ent.get('label', ent.get('id', f'comp{index+1}'))
            comp_type = ent.get('type', 'component').lower()
            latex_component = self._circuitikz_component(comp_type, label)
            if index == 0:
                latex_lines.append(f"    (0,0) to {latex_component}")
            else:
                latex_lines.append(f"    to {latex_component}")
        latex_lines.append("    ;")
        latex_lines.append("\\end{circuitikz}")
        return "\n".join(latex_lines)

    def _circuitikz_component(self, comp_type: str, label: str) -> str:
        if 'res' in comp_type:
            return f"[R,l={{{label}}}]"
        if 'cap' in comp_type:
            return f"[C,l={{{label}}}]"
        if 'ind' in comp_type:
            return f"[L,l={{{label}}}]"
        if 'battery' in comp_type or 'source' in comp_type:
            return f"[american voltage source,l={{{label}}}]"
        return f"[generic,l={{{label}}}]"

    # Primitive helpers -----------------------------------------------------

    def _build_svg_from_primitives(self, entities: List[Dict[str, Any]]) -> Optional[tuple[str, int]]:
        matches: List[tuple[Dict[str, Any], DiagramPrimitive]] = []
        for entity in entities:
            primitive = self._fetch_primitive(entity)
            if primitive:
                matches.append((entity, primitive))

        if not matches:
            return None

        spacing = 140
        width = max(spacing * len(matches), 200)
        height = 140
        fragments: List[str] = []

        for idx, (entity, primitive) in enumerate(matches):
            transform = self._transform_for_entity(entity, idx * spacing)
            fragments.append(f'<g transform="{transform}">{primitive.svg_content}</g>')
            label = escape(entity.get('label', entity.get('id', '')))
            if label:
                fragments.append(f'<text x="{idx * spacing + 10}" y="{height - 10}" font-size="14" fill="#2c3e50">{label}</text>')

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(fragments)}</svg>'
        return svg, len(matches)

    def _fetch_primitive(self, entity: Dict[str, Any]) -> Optional[DiagramPrimitive]:
        queries = [entity.get('label'), entity.get('type'), entity.get('id')]
        for query in filter(None, queries):
            primitives = self.query_primitives(query, "electronics", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        # Try default type keywords
        default_keywords = {
            'battery': 'battery',
            'resistor': 'resistor',
            'capacitor': 'capacitor',
            'switch': 'switch'
        }
        for keyword in default_keywords.values():
            primitives = self.query_primitives(keyword, "electronics", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        return None

    def _transform_for_entity(self, entity: Dict[str, Any], x_offset: float) -> str:
        props = entity.get('properties', {}) or {}
        scale = props.get('scale', 1.0)
        rotation = props.get('rotation', 0.0)
        return f"translate({x_offset + 20},40) scale({scale}) rotate({rotation})"
