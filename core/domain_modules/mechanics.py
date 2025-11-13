"""Mechanics domain module using PySketcher / pyfreebody templates."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import DiagramPrimitive


class MechanicsPySketcherModule(DomainModule):
    module_id = "mechanics_pysketcher"
    display_name = "PySketcher / pyfreebody"
    supported_domains = ["mechanics", "physics"]
    priority = 40

    def __init__(self) -> None:
        super().__init__()
        try:
            import pysketcher  # type: ignore
            self.available = True
        except Exception:
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
        if not entities:
            return None

        svg_payload = self._build_svg_from_primitives(entities)
        if svg_payload:
            svg_content, match_count = svg_payload
            metadata = {
                'primitive_matches': match_count,
                'available': True,
                'object_count': len(entities)
            }
            return DomainModuleArtifact(
                module_id=f"{self.module_id}_svg",
                title="Mechanics primitives (SVG)",
                format="svg",
                content=svg_content,
                description="SVG layout composed from mass/spring/force primitives.",
                metadata=metadata,
            )

        script = self._generate_pysketcher_script(entities)
        metadata: Dict[str, Any] = {
            'available': self.available,
            'object_count': len(entities),
            'primitive_matches': 0,
        }
        if not self.available:
            metadata['warning'] = 'pysketcher not installed - script not executed'

        return DomainModuleArtifact(
            module_id=self.module_id,
            title="Mechanics diagram template",
            format="python",
            content=script,
            description="PySketcher/pyfreebody script scaffold for block/pulley/spring diagrams.",
            metadata=metadata,
        )

    def _generate_pysketcher_script(self, entities: List[Dict[str, Any]]) -> str:
        blocks = [e for e in entities if 'block' in e.get('type', '').lower() or 'mass' in e.get('type', '').lower()]
        springs = [e for e in entities if 'spring' in e.get('type', '').lower()]
        forces = [e for e in entities if 'force' in e.get('type', '').lower()]

        lines = [
            "from pysketcher import *",
            "drawing_tool.set_coordinate_system(xmin=0, xmax=12, ymin=0, ymax=6, axis=False)",
            "scene = Composition()",
        ]

        for idx, block in enumerate(blocks or [{'label': 'Block'}]):
            label = block.get('label', f'Block {idx+1}')
            lines.append(
                f"block_{idx+1} = Rectangle((2*{idx}+1, 1), 2, 1).set_filled_curves('lightgray').set_line_color('black')"
            )
            lines.append(f"block_{idx+1}.add_text('{label}', position='center')")
            lines.append(f"scene += block_{idx+1}")

        for idx, spring in enumerate(springs):
            lines.append(
                f"spring_{idx+1} = Spring((0.5, {idx+1}+1), (1.5, {idx+1}+1), coils=6)")
            lines.append(f"scene += spring_{idx+1}")

        for idx, force in enumerate(forces or [{'label': 'F'}]):
            label = force.get('label', f'F_{idx+1}')
            lines.append(
                f"force_{idx+1} = Force((4, {idx+1}+1.5), (6, {idx+1}+1.5)).add_text('{label}')"
            )
            lines.append(f"scene += force_{idx+1}")

        lines.append("scene.draw()"); lines.append("drawing_tool.display()")
        return "\n".join(lines)

    def _build_svg_from_primitives(self, entities: List[Dict[str, Any]]) -> Optional[tuple[str, int]]:
        matches: List[tuple[Dict[str, Any], DiagramPrimitive]] = []
        for entity in entities:
            primitive = self._fetch_primitive(entity)
            if primitive:
                matches.append((entity, primitive))

        if not matches:
            return None

        spacing = 160
        width = max(spacing * len(matches), 200)
        height = 160
        fragments: List[str] = []

        for idx, (entity, primitive) in enumerate(matches):
            transform = self._transform_for_entity(entity, idx * spacing)
            fragments.append(f'<g transform="{transform}">{primitive.svg_content}</g>')
            label = escape(entity.get('label', entity.get('id', '')))
            if label:
                fragments.append(f'<text x="{idx * spacing + 20}" y="{height - 15}" font-size="14">{label}</text>')

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(fragments)}</svg>'
        return svg, len(matches)

    def _fetch_primitive(self, entity: Dict[str, Any]) -> Optional[DiagramPrimitive]:
        queries = [entity.get('label'), entity.get('type'), entity.get('id')]
        for query in filter(None, queries):
            primitives = self.query_primitives(query, "mechanics", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        fallback_keywords = ['block', 'mass', 'spring', 'pulley', 'force']
        for keyword in fallback_keywords:
            primitives = self.query_primitives(keyword, "mechanics", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        return None

    def _transform_for_entity(self, entity: Dict[str, Any], x_offset: float) -> str:
        props = entity.get('properties', {}) or {}
        scale = props.get('scale', 1.0)
        rotation = props.get('rotation', 0.0)
        return f"translate({x_offset + 40},60) scale({scale}) rotate({rotation})"
