"""
Property Graph - Graph-Based Knowledge Representation
Phase 1A of Advanced NLP Roadmap

Provides graph-based knowledge representation for STEM problems using NetworkX.
Enables relationship extraction, property propagation, and semantic queries.

Architecture:
- Nodes: Entities (objects, quantities, concepts)
- Edges: Relationships between entities
- Properties: Attributes attached to nodes and edges
- Queries: Pattern matching and traversal
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json




class NodeType(Enum):
    """Types of nodes in the property graph"""
    # Physical objects
    OBJECT = "object"
    COMPONENT = "component"
    BODY = "body"

    # Quantities and measurements
    QUANTITY = "quantity"
    MEASUREMENT = "measurement"
    PARAMETER = "parameter"

    # Concepts and abstractions
    CONCEPT = "concept"
    LAW = "law"
    PROCESS = "process"
    EVENT = "event"

    # Spatial and geometric
    LOCATION = "location"
    GEOMETRY = "geometry"
    COORDINATE = "coordinate"

    # Forces and fields
    FORCE = "force"
    FIELD = "field"

    # Other
    UNKNOWN = "unknown"


class EdgeType(Enum):
    """Types of edges (relationships) in the property graph"""
    # Structural relationships
    CONNECTED_TO = "connected_to"
    CONTAINS = "contains"
    PART_OF = "part_of"

    # Spatial relationships
    LOCATED_AT = "located_at"
    ADJACENT_TO = "adjacent_to"
    BETWEEN = "between"
    ABOVE = "above"
    BELOW = "below"
    LEFT_OF = "left_of"
    RIGHT_OF = "right_of"

    # Physical relationships
    ACTS_ON = "acts_on"
    APPLIED_TO = "applied_to"
    EXERTED_BY = "exerted_by"

    # Measurement relationships
    HAS_VALUE = "has_value"
    HAS_UNIT = "has_unit"
    MEASURED_AT = "measured_at"

    # Causal relationships
    CAUSES = "causes"
    RESULTS_IN = "results_in"
    DEPENDS_ON = "depends_on"

    # Conceptual relationships
    IS_A = "is_a"
    INSTANCE_OF = "instance_of"
    GOVERNED_BY = "governed_by"

    # Generic
    RELATED_TO = "related_to"
    UNKNOWN = "unknown"


@dataclass
class GraphNode:
    """
    Node in the property graph representing an entity
    """
    id: str
    type: NodeType
    label: str  # Human-readable name
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value if isinstance(self.type, NodeType) else self.type,
            'label': self.label,
            'properties': self.properties,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphNode':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            type=NodeType(data['type']) if data['type'] in [t.value for t in NodeType] else NodeType.UNKNOWN,
            label=data['label'],
            properties=data.get('properties', {}),
            metadata=data.get('metadata', {})
        )


@dataclass
class GraphEdge:
    """
    Edge in the property graph representing a relationship
    """
    source: str  # Source node ID
    target: str  # Target node ID
    type: EdgeType
    label: str  # Human-readable relationship name
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # Confidence in this relationship (0-1)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type.value if isinstance(self.type, EdgeType) else self.type,
            'label': self.label,
            'properties': self.properties,
            'metadata': self.metadata,
            'confidence': self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphEdge':
        """Create from dictionary"""
        return cls(
            source=data['source'],
            target=data['target'],
            type=EdgeType(data['type']) if data['type'] in [t.value for t in EdgeType] else EdgeType.UNKNOWN,
            label=data['label'],
            properties=data.get('properties', {}),
            metadata=data.get('metadata', {}),
            confidence=data.get('confidence', 1.0)
        )


class PropertyGraph:
    """
    Property graph for knowledge representation using NetworkX

    Features:
    - Add/remove nodes and edges
    - Query by pattern matching
    - Property propagation
    - Graph traversal
    - Conversion to/from CanonicalProblemSpec
    """

    def __init__(self):
        """Initialize empty property graph"""
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        self._node_index: Dict[str, GraphNode] = {}  # Fast node lookup
        self._edge_index: Dict[str, List[GraphEdge]] = {}  # Fast edge lookup by source

    # ========== Node Operations ==========

    def add_node(self, node: GraphNode) -> None:
        """
        Add a node to the graph

        Args:
            node: GraphNode to add
        """
        self.graph.add_node(
            node.id,
            type=node.type,
            label=node.label,
            properties=node.properties,
            metadata=node.metadata
        )
        self._node_index[node.id] = node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """
        Get a node by ID

        Args:
            node_id: ID of the node

        Returns:
            GraphNode if found, None otherwise
        """
        return self._node_index.get(node_id)

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node and all its edges

        Args:
            node_id: ID of the node to remove
        """
        if node_id in self.graph:
            self.graph.remove_node(node_id)
            del self._node_index[node_id]
            # Clean up edge index
            if node_id in self._edge_index:
                del self._edge_index[node_id]

    def has_node(self, node_id: str) -> bool:
        """Check if node exists"""
        return node_id in self._node_index

    def get_all_nodes(self, node_type: Optional[NodeType] = None) -> List[GraphNode]:
        """
        Get all nodes, optionally filtered by type

        Args:
            node_type: Optional NodeType to filter by

        Returns:
            List of GraphNode objects
        """
        if node_type is None:
            return list(self._node_index.values())
        else:
            return [n for n in self._node_index.values() if n.type == node_type]

    def merge_node_properties(self, node_id: str, properties: Dict[str, Any]) -> None:
        """Merge additional properties into a node"""
        if not properties:
            return
        node = self._node_index.get(node_id)
        if not node:
            raise KeyError(f"Node {node_id} not found")
        node.properties = self._merge_dict_values(node.properties, properties)
        if node_id in self.graph.nodes:
            self.graph.nodes[node_id]['properties'] = node.properties

    def merge_node_metadata(self, node_id: str, metadata: Dict[str, Any]) -> None:
        """Merge metadata payload into a node"""
        if not metadata:
            return
        node = self._node_index.get(node_id)
        if not node:
            raise KeyError(f"Node {node_id} not found")
        node.metadata = self._merge_dict_values(node.metadata, metadata)
        if node_id in self.graph.nodes:
            self.graph.nodes[node_id]['metadata'] = node.metadata

    def find_nodes_missing_property(self,
                                    property_name: str,
                                    node_type: Optional[NodeType] = None,
                                    label_contains: Optional[str] = None) -> List[GraphNode]:
        """Return nodes that lack a given property (case-insensitive)"""
        if not property_name:
            return []
        property_name = property_name.lower()
        label_filter = label_contains.lower() if label_contains else None
        matches: List[GraphNode] = []
        for node in self.get_all_nodes(node_type):
            if label_filter and label_filter not in node.label.lower():
                continue
            properties = node.properties or {}
            value = None
            for key, val in properties.items():
                if key.lower() == property_name:
                    value = val
                    break
            if value in (None, '', [], {}):
                matches.append(node)
        return matches

    def find_nodes_by_metadata(self, key: str, value: Optional[Any] = None) -> List[GraphNode]:
        """Return nodes whose metadata contain the provided key/value"""
        if not key:
            return []
        key_lower = key.lower()
        matches: List[GraphNode] = []
        for node in self.get_all_nodes():
            metadata = node.metadata or {}
            for meta_key, meta_value in metadata.items():
                if meta_key.lower() != key_lower:
                    continue
                if value is None or meta_value == value:
                    matches.append(node)
                    break
        return matches

    # ========== Edge Operations ==========

    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add an edge to the graph

        Args:
            edge: GraphEdge to add
        """
        # Verify nodes exist
        if not self.has_node(edge.source):
            raise ValueError(f"Source node {edge.source} does not exist")
        if not self.has_node(edge.target):
            raise ValueError(f"Target node {edge.target} does not exist")

        self.graph.add_edge(
            edge.source,
            edge.target,
            type=edge.type,
            label=edge.label,
            properties=edge.properties,
            metadata=edge.metadata,
            confidence=edge.confidence
        )

        # Update edge index
        if edge.source not in self._edge_index:
            self._edge_index[edge.source] = []
        self._edge_index[edge.source].append(edge)

    def get_edges(self, source: Optional[str] = None, target: Optional[str] = None,
                  edge_type: Optional[EdgeType] = None) -> List[GraphEdge]:
        """
        Get edges, optionally filtered by source, target, and/or type

        Args:
            source: Optional source node ID
            target: Optional target node ID
            edge_type: Optional EdgeType to filter by

        Returns:
            List of GraphEdge objects
        """
        edges = []

        # Get all edges from graph
        for src, tgt, data in self.graph.edges(data=True):
            if source and src != source:
                continue
            if target and tgt != target:
                continue
            if edge_type and data.get('type') != edge_type:
                continue

            edges.append(GraphEdge(
                source=src,
                target=tgt,
                type=data.get('type', EdgeType.UNKNOWN),
                label=data.get('label', ''),
                properties=data.get('properties', {}),
                metadata=data.get('metadata', {}),
                confidence=data.get('confidence', 1.0)
            ))

        return edges

    def get_outgoing_edges(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphEdge]:
        """Get all edges going out from a node"""
        return self.get_edges(source=node_id, edge_type=edge_type)

    def get_incoming_edges(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphEdge]:
        """Get all edges coming into a node"""
        return self.get_edges(target=node_id, edge_type=edge_type)

    def get_neighbors(self, node_id: str, direction: str = 'both') -> List[str]:
        """
        Get neighbor node IDs

        Args:
            node_id: ID of the node
            direction: 'out', 'in', or 'both'

        Returns:
            List of neighbor node IDs
        """
        if direction == 'out':
            return list(self.graph.successors(node_id))
        elif direction == 'in':
            return list(self.graph.predecessors(node_id))
        else:  # both
            return list(set(self.graph.successors(node_id)) | set(self.graph.predecessors(node_id)))

    # ========== Graph Queries ==========

    def query_pattern(self, pattern: Dict) -> List[Dict]:
        """
        Query graph by pattern matching

        Pattern format:
        {
            'nodes': [
                {'id': 'n1', 'type': NodeType.OBJECT, 'properties': {...}},
                {'id': 'n2', 'type': NodeType.FORCE}
            ],
            'edges': [
                {'source': 'n1', 'target': 'n2', 'type': EdgeType.ACTS_ON}
            ]
        }

        Returns list of matches (each match is a dict mapping pattern IDs to actual IDs)
        """
        matches = []

        # Get candidate nodes for each pattern node
        candidates: Dict[str, List[str]] = {}
        for node_pattern in pattern.get('nodes', []):
            pattern_id = node_pattern['id']
            node_type = node_pattern.get('type')
            props = node_pattern.get('properties', {})

            # Find matching nodes
            matching_nodes = []
            for node in self.get_all_nodes(node_type):
                # Check if properties match
                if all(node.properties.get(k) == v for k, v in props.items()):
                    matching_nodes.append(node.id)

            candidates[pattern_id] = matching_nodes

        # Generate all combinations and check edge constraints
        def check_match(assignment: Dict[str, str]) -> bool:
            """Check if node assignment satisfies edge constraints"""
            for edge_pattern in pattern.get('edges', []):
                src = assignment[edge_pattern['source']]
                tgt = assignment[edge_pattern['target']]
                edge_type = edge_pattern.get('type')

                # Check if edge exists
                edges = self.get_edges(source=src, target=tgt, edge_type=edge_type)
                if not edges:
                    return False

            return True

        # Simple implementation - for complex patterns, use graph isomorphism
        # For now, just return nodes matching the first pattern
        if pattern.get('nodes'):
            first_pattern = pattern['nodes'][0]
            for node_id in candidates.get(first_pattern['id'], []):
                matches.append({first_pattern['id']: node_id})

        return matches

    def find_paths(self, start: str, end: str, max_length: int = 5) -> List[List[str]]:
        """
        Find all paths between two nodes

        Args:
            start: Start node ID
            end: End node ID
            max_length: Maximum path length

        Returns:
            List of paths (each path is a list of node IDs)
        """
        try:
            # Use NetworkX's all_simple_paths
            paths = nx.all_simple_paths(self.graph, start, end, cutoff=max_length)
            return list(paths)
        except nx.NetworkXNoPath:
            return []

    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between two nodes"""
        try:
            return nx.shortest_path(self.graph, start, end)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    # ========== Graph Analysis ==========

    def get_subgraph(self, node_ids: List[str]) -> 'PropertyGraph':
        """
        Extract a subgraph containing only the specified nodes

        Args:
            node_ids: List of node IDs to include

        Returns:
            New PropertyGraph containing only the specified nodes and edges between them
        """
        subgraph = PropertyGraph()

        # Add nodes
        for node_id in node_ids:
            if node_id in self._node_index:
                subgraph.add_node(self._node_index[node_id])

        # Add edges
        for edge in self.get_edges():
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge)

        return subgraph

    def get_connected_components(self) -> List[Set[str]]:
        """
        Get connected components (treating graph as undirected)

        Returns:
            List of sets of node IDs, each set is a connected component
        """
        undirected = self.graph.to_undirected()
        return list(nx.connected_components(undirected))

    def get_node_degree(self, node_id: str) -> Dict[str, int]:
        """
        Get degree statistics for a node

        Returns:
            Dict with 'in', 'out', and 'total' degree counts
        """
        return {
            'in': self.graph.in_degree(node_id),
            'out': self.graph.out_degree(node_id),
            'total': self.graph.degree(node_id)
        }

    # ========== Conversion Methods ==========

    def to_canonical_spec(self) -> Dict:
        """
        Convert property graph to CanonicalProblemSpec format

        Returns:
            Dictionary representation compatible with CanonicalProblemSpec
        """
        from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain

        # Extract objects from nodes
        objects = []
        for node in self.get_all_nodes():
            objects.append({
                'id': node.id,
                'type': node.type.value,
                'label': node.label,
                **node.properties
            })

        # Extract relationships from edges
        relationships = []
        for edge in self.get_edges():
            relationships.append({
                'type': edge.type.value,
                'subject': edge.source,
                'target': edge.target,
                'label': edge.label,
                **edge.properties
            })

        # Build spec
        return {
            'objects': objects,
            'relationships': relationships,
            'graph_metadata': {
                'node_count': len(self._node_index),
                'edge_count': len(list(self.graph.edges())),
                'connected_components': len(self.get_connected_components())
            }
        }

    @classmethod
    def from_canonical_spec(cls, spec: Dict) -> 'PropertyGraph':
        """
        Create property graph from CanonicalProblemSpec

        Args:
            spec: CanonicalProblemSpec dictionary or object

        Returns:
            PropertyGraph instance
        """
        graph = cls()

        # Handle both dict and object
        if hasattr(spec, 'to_dict'):
            spec = spec.to_dict()

        # Add nodes from objects
        for obj in spec.get('objects', []):
            node_type = NodeType.UNKNOWN

            # Infer node type from object type
            obj_type = obj.get('type', '').lower()
            if 'force' in obj_type:
                node_type = NodeType.FORCE
            elif 'body' in obj_type or 'mass' in obj_type or 'block' in obj_type:
                node_type = NodeType.BODY
            elif any(x in obj_type for x in ['component', 'resistor', 'capacitor', 'battery']):
                node_type = NodeType.COMPONENT
            elif any(x in obj_type for x in ['quantity', 'value', 'measurement']):
                node_type = NodeType.QUANTITY
            else:
                node_type = NodeType.OBJECT

            node = GraphNode(
                id=obj.get('id', f"node_{len(graph._node_index)}"),
                type=node_type,
                label=obj.get('label', obj.get('name', obj.get('type', 'unknown'))),
                properties={k: v for k, v in obj.items() if k not in ['id', 'type', 'label']}
            )
            graph.add_node(node)

        # Add edges from relationships
        for rel in spec.get('relationships', []):
            edge_type = EdgeType.RELATED_TO

            # Infer edge type from relationship type
            rel_type = rel.get('type', '').lower()
            if 'acts' in rel_type or 'act' in rel_type:
                edge_type = EdgeType.ACTS_ON
            elif 'connect' in rel_type:
                edge_type = EdgeType.CONNECTED_TO
            elif 'contain' in rel_type:
                edge_type = EdgeType.CONTAINS
            elif 'cause' in rel_type:
                edge_type = EdgeType.CAUSES

            # Get source and target
            source = rel.get('subject', rel.get('source'))
            target = rel.get('target', rel.get('object'))

            if source and target:
                edge = GraphEdge(
                    source=source,
                    target=target,
                    type=edge_type,
                    label=rel.get('label', rel.get('type', 'related')),
                    properties={k: v for k, v in rel.items() if k not in ['source', 'target', 'subject', 'type', 'label']}
                )

                # Only add edge if both nodes exist
                if graph.has_node(source) and graph.has_node(target):
                    graph.add_edge(edge)

        return graph

    # ========== Serialization ==========

    def to_dict(self) -> Dict:
        """Export graph to dictionary"""
        return {
            'nodes': [node.to_dict() for node in self._node_index.values()],
            'edges': [edge.to_dict() for edge in self.get_edges()],
            'metadata': {
                'node_count': len(self._node_index),
                'edge_count': len(list(self.graph.edges()))
            }
        }

    def to_json(self, filepath: str) -> None:
        """Export graph to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PropertyGraph':
        """Create graph from dictionary"""
        graph = cls()

        # Add nodes
        for node_data in data.get('nodes', []):
            graph.add_node(GraphNode.from_dict(node_data))

        # Add edges
        for edge_data in data.get('edges', []):
            edge = GraphEdge.from_dict(edge_data)
            if graph.has_node(edge.source) and graph.has_node(edge.target):
                graph.add_edge(edge)

        return graph

    @classmethod
    def from_json(cls, filepath: str) -> 'PropertyGraph':
        """Load graph from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    # ========== Utility Methods ==========

    def __len__(self) -> int:
        """Return number of nodes"""
        return len(self._node_index)

    def __repr__(self) -> str:
        """String representation"""
        return f"PropertyGraph(nodes={len(self._node_index)}, edges={len(list(self.graph.edges()))})"

    def summary(self) -> str:
        """Get a summary of the graph"""
        summary = [
            f"PropertyGraph Summary:",
            f"  Nodes: {len(self._node_index)}",
            f"  Edges: {len(list(self.graph.edges()))}",
            f"  Connected Components: {len(self.get_connected_components())}",
            f"\nNode Types:"
        ]

        # Count node types
        type_counts: Dict[NodeType, int] = {}
        for node in self._node_index.values():
            type_counts[node.type] = type_counts.get(node.type, 0) + 1

        for node_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"    {node_type.value}: {count}")

        return '\n'.join(summary)

    @staticmethod
    def _merge_dict_values(original: Optional[Dict[str, Any]],
                           updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge helper preserving nested structures"""
        result = dict(original) if original else {}
        for key, value in updates.items():
            if key not in result:
                result[key] = value
                continue

            existing = result[key]
            if isinstance(existing, list) and isinstance(value, list):
                for item in value:
                    if item not in existing:
                        existing.append(item)
            elif isinstance(existing, dict) and isinstance(value, dict):
                result[key] = PropertyGraph._merge_dict_values(existing, value)
            else:
                result[key] = value
        return result
