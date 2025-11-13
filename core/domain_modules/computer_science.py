"""Computer science domain module producing PlantUML/Mermaid diagrams."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import DiagramPrimitive


class ComputerScienceDiagramModule(DomainModule):
    module_id = "cs_plantuml"
    display_name = "PlantUML / Mermaid"
    supported_domains = ["computer_science", "cs", "programming"]
    priority = 25

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

        svg_payload = self._build_svg_from_primitives(entities, relations)
        if svg_payload:
            svg_content, match_count = svg_payload
            metadata = {
                'node_count': len(entities),
                'edge_count': len(relations),
                'primitive_matches': match_count
            }
            return DomainModuleArtifact(
                module_id=f"{self.module_id}_svg",
                title="CS primitives (SVG)",
                format="svg",
                content=svg_content,
                description="SVG diagram composed from database/server/cloud primitives.",
                metadata=metadata
            )

        plantuml = self._render_plantuml(entities, relations)
        mermaid = self._render_mermaid(entities, relations)
        content = """@startuml\n{plantuml}\n@enduml\n\n```mermaid\n{mermaid}\n```""".format(
            plantuml=plantuml,
            mermaid=mermaid
        )

        return DomainModuleArtifact(
            module_id=self.module_id,
            title="CS diagram templates",
            format="text",
            content=content,
            description="Automatically generated PlantUML and Mermaid templates for class/graph diagrams.",
            metadata={'node_count': len(entities), 'edge_count': len(relations), 'primitive_matches': 0}
        )

    def _render_plantuml(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> str:
        lines = []
        for entity in entities:
            name = entity.get('label', entity.get('id', 'Node'))
            lines.append(f"class {self._sanitize(name)}")
        for rel in relations:
            src = self._sanitize(rel.get('source_id') or rel.get('source') or 'A')
            tgt = self._sanitize(rel.get('target_id') or rel.get('target') or 'B')
            rel_type = rel.get('type', '--')
            connector = '-->' if 'flow' in rel_type.lower() else '--'
            lines.append(f"{src} {connector} {tgt} : {rel_type}")
        return "\n".join(lines)

    def _render_mermaid(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> str:
        lines = ["graph LR"]
        if not relations:
            for entity in entities:
                name = self._sanitize(entity.get('id', 'node'))
                label = entity.get('label', name)
                lines.append(f"    {name}[{label}]")
        else:
            for rel in relations:
                src = self._sanitize(rel.get('source_id') or rel.get('source') or 'A')
                tgt = self._sanitize(rel.get('target_id') or rel.get('target') or 'B')
                label = rel.get('type', '')
                lines.append(f"    {src}[{src}] -->|{label}| {tgt}[{tgt}]")
        return "\n".join(lines)

    def _sanitize(self, text: str) -> str:
        text = text.replace(' ', '_').replace('-', '_')
        return ''.join(ch for ch in text if ch.isalnum() or ch == '_') or 'Node'

    def _build_svg_from_primitives(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Optional[tuple[str, int]]:
        matches: List[tuple[Dict[str, Any], DiagramPrimitive]] = []
        for entity in entities:
            primitive = self._fetch_primitive(entity)
            if primitive:
                matches.append((entity, primitive))

        if not matches:
            return None

        spacing = 180
        width = spacing * len(matches)
        height = 160
        fragments: List[str] = []

        for idx, (entity, primitive) in enumerate(matches):
            transform = f"translate({idx * spacing + 20}, 30)"
            fragments.append(f'<g transform="{transform}">{primitive.svg_content}</g>')
            label = escape(entity.get('label', entity.get('id', '')))
            if label:
                fragments.append(f'<text x="{idx * spacing + 40}" y="{height - 20}" font-size="14">{label}</text>')

        for rel in relations:
            src_idx = self._entity_index(matches, rel.get('source_id') or rel.get('source'))
            tgt_idx = self._entity_index(matches, rel.get('target_id') or rel.get('target'))
            if src_idx is None or tgt_idx is None:
                continue
            x1 = src_idx * spacing + 80
            x2 = tgt_idx * spacing + 80
            y = height - 60
            fragments.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#7f8c8d" stroke-width="2" marker-end="url(#arrow)"/>')

        marker = '<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="#7f8c8d"/></marker></defs>'
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{marker}{"".join(fragments)}</svg>'
        return svg, len(matches)

    def _fetch_primitive(self, entity: Dict[str, Any]) -> Optional[DiagramPrimitive]:
        queries = [entity.get('label'), entity.get('type'), entity.get('id')]
        for query in filter(None, queries):
            primitives = self.query_primitives(query, "computer_science", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        fallback = ['database', 'server', 'cloud', 'process']
        for keyword in fallback:
            primitives = self.query_primitives(keyword, "computer_science", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        return None

    def _entity_index(self, matches: List[tuple[Dict[str, Any], DiagramPrimitive]], entity_id: Optional[str]) -> Optional[int]:
        if not entity_id:
            return None
        for idx, (entity, _) in enumerate(matches):
            if entity.get('id') == entity_id:
                return idx
        return None
