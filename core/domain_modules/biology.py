"""Biology domain module using Cytoscape-style JSON."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import DiagramPrimitive


class BiologyCytoscapeModule(DomainModule):
    module_id = "biology_cytoscape"
    display_name = "Cytoscape Pathway Template"
    supported_domains = ["biology"]
    priority = 30

    def __init__(self) -> None:
        super().__init__()
        try:
            import py2cytoscape  # type: ignore
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
        relations = self.normalize_relations(diagram_plan)
        if not entities:
            return None

        svg_payload = self._build_svg_from_primitives(entities, relations)
        if svg_payload:
            svg_content, match_count = svg_payload
            metadata: Dict[str, Any] = {
                'available': True,
                'primitive_matches': match_count,
                'node_count': len(entities)
            }
            return DomainModuleArtifact(
                module_id=f"{self.module_id}_svg",
                title="Biology primitives (SVG)",
                format="svg",
                content=svg_content,
                description="SVG graph assembled from biology primitives (DNA, cells).",
                metadata=metadata,
            )

        network = self._build_cytoscape_network(entities, relations)
        metadata: Dict[str, Any] = {
            'available': self.available,
            'node_count': len(network['elements']['nodes']),
            'edge_count': len(network['elements']['edges']),
            'primitive_matches': 0,
        }
        if not self.available:
            metadata['warning'] = 'py2cytoscape not installed - JSON provided for Cytoscape import'

        return DomainModuleArtifact(
            module_id=self.module_id,
            title="Cytoscape pathway JSON",
            format="json",
            content=json.dumps(network, indent=2),
            description="Cytoscape-compatible JSON graph representing the biological interactions detected in the plan.",
            metadata=metadata,
        )

    def _build_cytoscape_network(self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes = []
        for entity in entities:
            nodes.append({
                'data': {
                    'id': entity.get('id'),
                    'name': entity.get('label', entity.get('id')),
                    'type': entity.get('type', 'entity')
                }
            })

        edges = []
        for relation in relations:
            src = relation.get('source_id') or relation.get('source')
            tgt = relation.get('target_id') or relation.get('target')
            if not (src and tgt):
                continue
            edges.append({
                'data': {
                    'id': f"{src}-{tgt}",
                    'source': src,
                    'target': tgt,
                    'interaction': relation.get('type', 'interaction')
                }
            })

        style = [
            {
                'selector': 'node',
                'style': {
                    'label': 'data(name)',
                    'background-color': '#6fb1fc',
                    'width': 'mapData(weight, 0, 10, 20, 60)',
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'line-color': '#d0d0d0',
                    'target-arrow-color': '#d0d0d0'
                }
            }
        ]

        return {
            'elements': {
                'nodes': nodes,
                'edges': edges,
            },
            'style': style,
        }

    def _build_svg_from_primitives(self,
                                   entities: List[Dict[str, Any]],
                                   relations: List[Dict[str, Any]]) -> Optional[tuple[str, int]]:
        matches: List[tuple[Dict[str, Any], DiagramPrimitive]] = []
        for entity in entities:
            primitive = self._fetch_primitive(entity)
            if primitive:
                matches.append((entity, primitive))

        if not matches:
            return None

        spacing = 160
        columns = 3
        width = spacing * min(len(matches), columns)
        height = spacing * ((len(matches) - 1) // columns + 1)
        fragments: List[str] = []

        for idx, (entity, primitive) in enumerate(matches):
            col = idx % columns
            row = idx // columns
            transform = f"translate({col * spacing + 30}, {row * spacing + 30})"
            fragments.append(f'<g transform="{transform}">{primitive.svg_content}</g>')
            label = escape(entity.get('label', entity.get('id', '')))
            if label:
                fragments.append(f'<text x="{col * spacing + 10}" y="{row * spacing + 120}" font-size="14">{label}</text>')

        # Draw simple relation lines
        for relation in relations:
            src_idx = self._entity_index(matches, relation.get('source_id') or relation.get('source'))
            tgt_idx = self._entity_index(matches, relation.get('target_id') or relation.get('target'))
            if src_idx is None or tgt_idx is None:
                continue
            src_col, src_row = src_idx % columns, src_idx // columns
            tgt_col, tgt_row = tgt_idx % columns, tgt_idx // columns
            x1 = src_col * spacing + 40
            y1 = src_row * spacing + 40
            x2 = tgt_col * spacing + 40
            y2 = tgt_row * spacing + 40
            fragments.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#7f8c8d" stroke-width="2" marker-end="url(#arrow)"/>')

        marker = '<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="#7f8c8d"/></marker></defs>'
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{marker}{"".join(fragments)}</svg>'
        return svg, len(matches)

    def _fetch_primitive(self, entity: Dict[str, Any]) -> Optional[DiagramPrimitive]:
        queries = [entity.get('label'), entity.get('type'), entity.get('id')]
        for query in filter(None, queries):
            primitives = self.query_primitives(query, "biology", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        fallback_keywords = ['dna', 'cell', 'protein', 'enzyme']
        for keyword in fallback_keywords:
            primitives = self.query_primitives(keyword, "biology", top_k=1, min_score=0.2)
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
