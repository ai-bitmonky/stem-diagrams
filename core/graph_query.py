"""
Graph Query Language - Advanced Query Interface for Property Graphs
Phase 1A of Advanced NLP Roadmap

Provides Cypher-like query capabilities for property graphs:
- Pattern matching
- Path finding
- Aggregation
- Filtering and sorting

Example queries:
- MATCH (n:OBJECT {type: 'force'}) RETURN n
- MATCH (a)-[r:ACTS_ON]->(b) RETURN a, r, b
- MATCH path=(start)-[*1..3]->(end) RETURN path
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType


class QueryOperator(Enum):
    """Query operators for filtering"""
    EQ = "="  # Equal
    NE = "!="  # Not equal
    LT = "<"  # Less than
    LE = "<="  # Less than or equal
    GT = ">"  # Greater than
    GE = ">="  # Greater than or equal
    IN = "IN"  # In list
    CONTAINS = "CONTAINS"  # String contains
    STARTS_WITH = "STARTS_WITH"  # String starts with
    ENDS_WITH = "ENDS_WITH"  # String ends with


@dataclass
class QueryFilter:
    """Filter condition for queries"""
    property_name: str
    operator: QueryOperator
    value: Any

    def evaluate(self, properties: Dict[str, Any]) -> bool:
        """Evaluate filter against properties"""
        prop_value = properties.get(self.property_name)

        if prop_value is None:
            return False

        if self.operator == QueryOperator.EQ:
            return prop_value == self.value
        elif self.operator == QueryOperator.NE:
            return prop_value != self.value
        elif self.operator == QueryOperator.LT:
            return prop_value < self.value
        elif self.operator == QueryOperator.LE:
            return prop_value <= self.value
        elif self.operator == QueryOperator.GT:
            return prop_value > self.value
        elif self.operator == QueryOperator.GE:
            return prop_value >= self.value
        elif self.operator == QueryOperator.IN:
            return prop_value in self.value
        elif self.operator == QueryOperator.CONTAINS:
            return str(self.value) in str(prop_value)
        elif self.operator == QueryOperator.STARTS_WITH:
            return str(prop_value).startswith(str(self.value))
        elif self.operator == QueryOperator.ENDS_WITH:
            return str(prop_value).endswith(str(self.value))

        return False


@dataclass
class QueryResult:
    """Result of a graph query"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    paths: List[List[str]]  # List of paths (node ID lists)
    aggregations: Dict[str, Any]
    metadata: Dict[str, Any]

    def __len__(self) -> int:
        """Number of results"""
        return len(self.nodes) + len(self.edges) + len(self.paths)

    def __repr__(self) -> str:
        return f"QueryResult(nodes={len(self.nodes)}, edges={len(self.edges)}, paths={len(self.paths)})"


class GraphQueryEngine:
    """
    Query engine for property graphs

    Provides high-level query interface similar to Cypher/SPARQL
    """

    def __init__(self, graph: PropertyGraph):
        """
        Initialize query engine

        Args:
            graph: PropertyGraph to query
        """
        self.graph = graph

    # ========== Basic Queries ==========

    def match_nodes(self,
                    node_type: Optional[NodeType] = None,
                    filters: Optional[List[QueryFilter]] = None,
                    limit: Optional[int] = None) -> List[GraphNode]:
        """
        Match nodes by type and filters

        Args:
            node_type: Optional node type filter
            filters: Optional list of property filters
            limit: Optional result limit

        Returns:
            List of matching GraphNode objects

        Example:
            # Find all force nodes
            forces = engine.match_nodes(node_type=NodeType.FORCE)

            # Find forces with magnitude > 10
            filters = [QueryFilter('magnitude', QueryOperator.GT, 10)]
            strong_forces = engine.match_nodes(node_type=NodeType.FORCE, filters=filters)
        """
        # Get nodes by type
        nodes = self.graph.get_all_nodes(node_type)

        # Apply filters
        if filters:
            filtered_nodes = []
            for node in nodes:
                if all(f.evaluate(node.properties) for f in filters):
                    filtered_nodes.append(node)
            nodes = filtered_nodes

        # Apply limit
        if limit:
            nodes = nodes[:limit]

        return nodes

    def match_edges(self,
                    edge_type: Optional[EdgeType] = None,
                    source: Optional[str] = None,
                    target: Optional[str] = None,
                    filters: Optional[List[QueryFilter]] = None,
                    limit: Optional[int] = None) -> List[GraphEdge]:
        """
        Match edges by type, source, target, and filters

        Args:
            edge_type: Optional edge type filter
            source: Optional source node ID
            target: Optional target node ID
            filters: Optional list of property filters
            limit: Optional result limit

        Returns:
            List of matching GraphEdge objects

        Example:
            # Find all ACTS_ON relationships
            acts_on = engine.match_edges(edge_type=EdgeType.ACTS_ON)

            # Find edges from specific node
            edges_from_n1 = engine.match_edges(source='node_1')
        """
        # Get edges
        edges = self.graph.get_edges(source=source, target=target, edge_type=edge_type)

        # Apply filters
        if filters:
            filtered_edges = []
            for edge in edges:
                if all(f.evaluate(edge.properties) for f in filters):
                    filtered_edges.append(edge)
            edges = filtered_edges

        # Apply limit
        if limit:
            edges = edges[:limit]

        return edges

    # ========== Pattern Matching ==========

    def match_pattern(self,
                      source_type: Optional[NodeType] = None,
                      edge_type: Optional[EdgeType] = None,
                      target_type: Optional[NodeType] = None,
                      source_filters: Optional[List[QueryFilter]] = None,
                      edge_filters: Optional[List[QueryFilter]] = None,
                      target_filters: Optional[List[QueryFilter]] = None) -> List[Dict[str, Any]]:
        """
        Match graph pattern: (source)-[edge]->(target)

        Args:
            source_type: Optional source node type
            edge_type: Optional edge type
            target_type: Optional target node type
            source_filters: Optional filters for source node
            edge_filters: Optional filters for edge
            target_filters: Optional filters for target node

        Returns:
            List of matches, each match is a dict with 'source', 'edge', 'target' keys

        Example:
            # Find all forces acting on bodies
            matches = engine.match_pattern(
                source_type=NodeType.FORCE,
                edge_type=EdgeType.ACTS_ON,
                target_type=NodeType.BODY
            )
        """
        matches = []

        # Get candidate source nodes
        source_nodes = self.match_nodes(node_type=source_type, filters=source_filters)

        for source_node in source_nodes:
            # Get outgoing edges from source
            edges = self.match_edges(edge_type=edge_type, source=source_node.id, filters=edge_filters)

            for edge in edges:
                # Get target node
                target_node = self.graph.get_node(edge.target)

                if target_node:
                    # Check target type and filters
                    if target_type and target_node.type != target_type:
                        continue

                    if target_filters:
                        if not all(f.evaluate(target_node.properties) for f in target_filters):
                            continue

                    # Match found
                    matches.append({
                        'source': source_node,
                        'edge': edge,
                        'target': target_node
                    })

        return matches

    # ========== Path Queries ==========

    def find_all_paths(self,
                       start: str,
                       end: str,
                       min_length: int = 1,
                       max_length: int = 5,
                       edge_type: Optional[EdgeType] = None) -> List[List[str]]:
        """
        Find all paths between two nodes

        Args:
            start: Start node ID
            end: End node ID
            min_length: Minimum path length (number of edges)
            max_length: Maximum path length
            edge_type: Optional edge type filter

        Returns:
            List of paths (each path is a list of node IDs)

        Example:
            # Find all paths from node_1 to node_5
            paths = engine.find_all_paths('node_1', 'node_5', max_length=3)
        """
        all_paths = self.graph.find_paths(start, end, max_length)

        # Filter by length
        filtered_paths = [p for p in all_paths if min_length <= len(p) - 1 <= max_length]

        # Filter by edge type if specified
        if edge_type:
            filtered_by_type = []
            for path in filtered_paths:
                # Check all edges in path
                valid = True
                for i in range(len(path) - 1):
                    edges = self.graph.get_edges(source=path[i], target=path[i + 1], edge_type=edge_type)
                    if not edges:
                        valid = False
                        break
                if valid:
                    filtered_by_type.append(path)
            filtered_paths = filtered_by_type

        return filtered_paths

    def find_shortest_paths(self,
                           start: str,
                           targets: Optional[List[str]] = None,
                           max_length: Optional[int] = None) -> Dict[str, List[str]]:
        """
        Find shortest paths from start to multiple targets

        Args:
            start: Start node ID
            targets: List of target node IDs (if None, finds to all nodes)
            max_length: Optional maximum path length

        Returns:
            Dict mapping target node ID to shortest path

        Example:
            # Find shortest paths from node_1 to all other nodes
            paths = engine.find_shortest_paths('node_1')
        """
        if targets is None:
            targets = [n.id for n in self.graph.get_all_nodes() if n.id != start]

        result = {}
        for target in targets:
            path = self.graph.find_shortest_path(start, target)
            if path and (max_length is None or len(path) - 1 <= max_length):
                result[target] = path

        return result

    def find_neighbors(self,
                       node_id: str,
                       depth: int = 1,
                       node_type: Optional[NodeType] = None) -> List[GraphNode]:
        """
        Find all neighbors within a certain depth

        Args:
            node_id: Starting node ID
            depth: Search depth (1 = direct neighbors, 2 = neighbors of neighbors, etc.)
            node_type: Optional node type filter

        Returns:
            List of neighbor GraphNode objects

        Example:
            # Find all direct neighbors
            neighbors = engine.find_neighbors('node_1', depth=1)

            # Find all force nodes within 2 hops
            force_neighbors = engine.find_neighbors('node_1', depth=2, node_type=NodeType.FORCE)
        """
        visited = {node_id}
        current_level = {node_id}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                neighbors = self.graph.get_neighbors(node)
                next_level.update(n for n in neighbors if n not in visited)
            visited.update(next_level)
            current_level = next_level

        # Get node objects
        neighbor_nodes = []
        for nid in visited:
            if nid != node_id:
                node = self.graph.get_node(nid)
                if node and (node_type is None or node.type == node_type):
                    neighbor_nodes.append(node)

        return neighbor_nodes

    # ========== Aggregation Queries ==========

    def count_nodes(self, node_type: Optional[NodeType] = None,
                    filters: Optional[List[QueryFilter]] = None) -> int:
        """Count nodes matching criteria"""
        return len(self.match_nodes(node_type=node_type, filters=filters))

    def count_edges(self, edge_type: Optional[EdgeType] = None,
                    filters: Optional[List[QueryFilter]] = None) -> int:
        """Count edges matching criteria"""
        return len(self.match_edges(edge_type=edge_type, filters=filters))

    def aggregate_property(self,
                          node_type: Optional[NodeType] = None,
                          property_name: str = '',
                          aggregation: str = 'sum',
                          filters: Optional[List[QueryFilter]] = None) -> Any:
        """
        Aggregate a numeric property across nodes

        Args:
            node_type: Optional node type filter
            property_name: Name of property to aggregate
            aggregation: Aggregation function ('sum', 'avg', 'min', 'max', 'count')
            filters: Optional property filters

        Returns:
            Aggregated value

        Example:
            # Sum of all force magnitudes
            total_force = engine.aggregate_property(
                node_type=NodeType.FORCE,
                property_name='magnitude',
                aggregation='sum'
            )
        """
        nodes = self.match_nodes(node_type=node_type, filters=filters)

        values = []
        for node in nodes:
            value = node.properties.get(property_name)
            if value is not None:
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass

        if not values:
            return 0 if aggregation in ['sum', 'count'] else None

        if aggregation == 'sum':
            return sum(values)
        elif aggregation == 'avg':
            return sum(values) / len(values)
        elif aggregation == 'min':
            return min(values)
        elif aggregation == 'max':
            return max(values)
        elif aggregation == 'count':
            return len(values)
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")

    def group_by(self,
                 node_type: Optional[NodeType] = None,
                 group_property: str = '',
                 filters: Optional[List[QueryFilter]] = None) -> Dict[Any, List[GraphNode]]:
        """
        Group nodes by a property value

        Args:
            node_type: Optional node type filter
            group_property: Property to group by
            filters: Optional property filters

        Returns:
            Dict mapping property value to list of nodes

        Example:
            # Group forces by direction
            by_direction = engine.group_by(
                node_type=NodeType.FORCE,
                group_property='direction'
            )
        """
        nodes = self.match_nodes(node_type=node_type, filters=filters)

        groups: Dict[Any, List[GraphNode]] = {}
        for node in nodes:
            group_value = node.properties.get(group_property, 'unknown')
            if group_value not in groups:
                groups[group_value] = []
            groups[group_value].append(node)

        return groups

    # ========== Complex Queries ==========

    def query(self,
              select: Optional[List[str]] = None,
              match_nodes: Optional[Dict] = None,
              match_edges: Optional[Dict] = None,
              where: Optional[List[QueryFilter]] = None,
              order_by: Optional[str] = None,
              limit: Optional[int] = None) -> QueryResult:
        """
        Execute complex query with multiple clauses

        Args:
            select: List of what to return ('nodes', 'edges', 'paths')
            match_nodes: Node matching criteria
            match_edges: Edge matching criteria
            where: Additional filters
            order_by: Property to sort by
            limit: Result limit

        Returns:
            QueryResult object

        Example:
            result = engine.query(
                select=['nodes', 'edges'],
                match_nodes={'type': NodeType.FORCE},
                where=[QueryFilter('magnitude', QueryOperator.GT, 5)],
                order_by='magnitude',
                limit=10
            )
        """
        nodes = []
        edges = []
        paths = []

        # Match nodes
        if match_nodes or 'nodes' in (select or []):
            node_type = match_nodes.get('type') if match_nodes else None
            node_filters = match_nodes.get('filters', []) if match_nodes else []
            if where:
                node_filters.extend(where)
            nodes = self.match_nodes(node_type=node_type, filters=node_filters if node_filters else None)

        # Match edges
        if match_edges or 'edges' in (select or []):
            edge_type = match_edges.get('type') if match_edges else None
            edge_filters = match_edges.get('filters', []) if match_edges else []
            edges = self.match_edges(edge_type=edge_type, filters=edge_filters if edge_filters else None)

        # Sort
        if order_by and nodes:
            nodes = sorted(nodes, key=lambda n: n.properties.get(order_by, 0))

        # Limit
        if limit:
            nodes = nodes[:limit]
            edges = edges[:limit]
            paths = paths[:limit]

        return QueryResult(
            nodes=nodes,
            edges=edges,
            paths=paths,
            aggregations={},
            metadata={'query': {
                'select': select,
                'match_nodes': match_nodes,
                'match_edges': match_edges,
                'where': where,
                'order_by': order_by,
                'limit': limit
            }}
        )

    # ========== Utility Methods ==========

    def explain(self, query_result: QueryResult) -> str:
        """
        Explain a query result

        Args:
            query_result: Result to explain

        Returns:
            Human-readable explanation
        """
        lines = [
            "Query Result Explanation:",
            f"  Nodes returned: {len(query_result.nodes)}",
            f"  Edges returned: {len(query_result.edges)}",
            f"  Paths returned: {len(query_result.paths)}",
            ""
        ]

        if query_result.nodes:
            lines.append("Nodes:")
            for node in query_result.nodes[:5]:  # Show first 5
                lines.append(f"    - {node.id} ({node.type.value}): {node.label}")
            if len(query_result.nodes) > 5:
                lines.append(f"    ... and {len(query_result.nodes) - 5} more")

        if query_result.edges:
            lines.append("\nEdges:")
            for edge in query_result.edges[:5]:
                lines.append(f"    - {edge.source} --[{edge.type.value}]--> {edge.target}")
            if len(query_result.edges) > 5:
                lines.append(f"    ... and {len(query_result.edges) - 5} more")

        return '\n'.join(lines)


# ========== Query Builder ==========

class QueryBuilder:
    """
    Fluent interface for building queries

    Example:
        result = QueryBuilder(graph) \\
            .match_nodes(NodeType.FORCE) \\
            .where('magnitude', QueryOperator.GT, 10) \\
            .limit(5) \\
            .execute()
    """

    def __init__(self, graph: PropertyGraph):
        self.engine = GraphQueryEngine(graph)
        self._node_type: Optional[NodeType] = None
        self._edge_type: Optional[EdgeType] = None
        self._filters: List[QueryFilter] = []
        self._limit: Optional[int] = None
        self._order_by: Optional[str] = None

    def match_nodes(self, node_type: NodeType) -> 'QueryBuilder':
        """Match nodes of type"""
        self._node_type = node_type
        return self

    def match_edges(self, edge_type: EdgeType) -> 'QueryBuilder':
        """Match edges of type"""
        self._edge_type = edge_type
        return self

    def where(self, property_name: str, operator: QueryOperator, value: Any) -> 'QueryBuilder':
        """Add filter condition"""
        self._filters.append(QueryFilter(property_name, operator, value))
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        """Limit results"""
        self._limit = n
        return self

    def order_by(self, property_name: str) -> 'QueryBuilder':
        """Order by property"""
        self._order_by = property_name
        return self

    def execute(self) -> QueryResult:
        """Execute query"""
        return self.engine.query(
            match_nodes={'type': self._node_type} if self._node_type else None,
            match_edges={'type': self._edge_type} if self._edge_type else None,
            where=self._filters if self._filters else None,
            order_by=self._order_by,
            limit=self._limit
        )
