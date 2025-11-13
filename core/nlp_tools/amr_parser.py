#!/usr/bin/env python3
"""
AMR (Abstract Meaning Representation) Parser

Provides semantic representation of sentences as directed acyclic graphs.
Extracts:
- Semantic roles (agent, patient, theme, etc.)
- Conceptual relationships
- Events and their participants
- Modality and negation
- Temporal and causal relationships
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
import re
from enum import Enum


class AMRNodeType(Enum):
    """Types of AMR nodes"""
    CONCEPT = "concept"
    ENTITY = "entity"
    EVENT = "event"
    STATE = "state"
    PROPERTY = "property"
    QUANTITY = "quantity"
    OPERATOR = "operator"


class AMREdgeType(Enum):
    """Types of AMR edges (semantic roles)"""
    ARG0 = "ARG0"  # Agent (typically subject)
    ARG1 = "ARG1"  # Patient (typically object)
    ARG2 = "ARG2"  # Instrument, beneficiary, attribute
    ARG3 = "ARG3"  # Starting point, beneficiary
    ARG4 = "ARG4"  # Ending point
    LOCATION = "location"
    TIME = "time"
    MANNER = "manner"
    PURPOSE = "purpose"
    CAUSE = "cause"
    CONDITION = "condition"
    INSTRUMENT = "instrument"
    BENEFICIARY = "beneficiary"
    ACCOMPANIER = "accompanier"
    TOPIC = "topic"
    DOMAIN = "domain"
    POSS = "poss"  # Possessor
    PART = "part-of"
    CONSIST = "consist-of"
    MOD = "mod"  # Modifier
    DEGREE = "degree"
    POLARITY = "polarity"
    QUANT = "quant"  # Quantifier


@dataclass
class AMRNode:
    """Represents a node in the AMR graph"""
    id: str
    concept: str
    type: AMRNodeType
    text: Optional[str] = None
    properties: Dict[str, any] = field(default_factory=dict)


@dataclass
class AMREdge:
    """Represents an edge in the AMR graph"""
    source: str  # Source node ID
    target: str  # Target node ID
    role: AMREdgeType
    label: Optional[str] = None


@dataclass
class AMRGraph:
    """Represents an Abstract Meaning Representation graph"""
    nodes: List[AMRNode]
    edges: List[AMREdge]
    root: Optional[str] = None  # Root node ID
    text: str = ""


@dataclass
class AMRParseResult:
    """Result from AMR parsing"""
    graphs: List[AMRGraph]  # One graph per sentence
    concepts: Set[str]
    entities: Dict[str, str]  # Entity name -> concept
    events: List[str]
    relations: List[Tuple[str, str, str]]  # (source, relation, target)
    raw_text: str


class AMRParser:
    """
    Lightweight AMR parser using rule-based and pattern-based approaches.

    This provides basic AMR functionality. For production use with complex
    sentences, consider using amrlib or transition-amr-parser with trained models.
    """

    def __init__(self):
        """Initialize the AMR parser"""
        # Verb-based event concepts
        self.event_verbs = {
            'place', 'put', 'set', 'move', 'apply', 'connect', 'attach',
            'charge', 'discharge', 'flow', 'transfer', 'conduct', 'insulate',
            'heat', 'cool', 'compress', 'expand', 'react', 'dissolve',
            'calculate', 'measure', 'determine', 'find', 'solve'
        }

        # Physical object concepts
        self.physical_objects = {
            'block', 'sphere', 'cylinder', 'plate', 'wire', 'rod', 'container',
            'capacitor', 'resistor', 'inductor', 'battery', 'circuit',
            'particle', 'molecule', 'atom', 'electron', 'proton'
        }

        # Property concepts
        self.properties = {
            'mass', 'weight', 'density', 'volume', 'area', 'length',
            'charge', 'current', 'voltage', 'resistance', 'capacitance',
            'temperature', 'pressure', 'velocity', 'acceleration', 'force',
            'energy', 'power', 'frequency', 'amplitude'
        }

        # Relationship verbs
        self.relationship_verbs = {
            'is', 'has', 'contains', 'consists', 'connects', 'touches',
            'rests', 'supports', 'holds', 'carries'
        }

        # Prepositions indicating spatial relations
        self.spatial_preps = {
            'on', 'in', 'at', 'above', 'below', 'between', 'inside',
            'outside', 'near', 'far', 'next to', 'adjacent to'
        }

        # Sentence splitter pattern
        self.sentence_pattern = re.compile(r'[.!?]+')

    def parse(self, text: str) -> AMRParseResult:
        """
        Parse text into AMR representation.

        Args:
            text: Input text to parse

        Returns:
            AMRParseResult with semantic graphs
        """
        # Split into sentences
        sentences = self._split_sentences(text)

        # Parse each sentence
        graphs = []
        all_concepts = set()
        all_entities = {}
        all_events = []
        all_relations = []

        for sentence in sentences:
            graph = self._parse_sentence(sentence)
            graphs.append(graph)

            # Collect concepts, entities, events
            for node in graph.nodes:
                all_concepts.add(node.concept)
                if node.type == AMRNodeType.ENTITY:
                    all_entities[node.text or node.concept] = node.concept
                elif node.type == AMRNodeType.EVENT:
                    all_events.append(node.concept)

            # Collect relations
            for edge in graph.edges:
                source_node = next((n for n in graph.nodes if n.id == edge.source), None)
                target_node = next((n for n in graph.nodes if n.id == edge.target), None)
                if source_node and target_node:
                    all_relations.append((
                        source_node.concept,
                        edge.role.value,
                        target_node.concept
                    ))

        return AMRParseResult(
            graphs=graphs,
            concepts=all_concepts,
            entities=all_entities,
            events=all_events,
            relations=all_relations,
            raw_text=text
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = self.sentence_pattern.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def _parse_sentence(self, sentence: str) -> AMRGraph:
        """Parse a single sentence into an AMR graph"""
        nodes = []
        edges = []
        node_counter = [0]  # Use list for mutable counter

        def new_node_id():
            node_counter[0] += 1
            return f"n{node_counter[0]}"

        # Tokenize
        words = sentence.lower().split()

        # Extract main event/predicate
        main_event = None
        main_event_id = None

        for word in words:
            if word in self.event_verbs:
                main_event_id = new_node_id()
                main_event = AMRNode(
                    id=main_event_id,
                    concept=word,
                    type=AMRNodeType.EVENT,
                    text=word
                )
                nodes.append(main_event)
                break

        # If no event verb found, look for relationship verb
        if not main_event:
            for word in words:
                if word in self.relationship_verbs:
                    main_event_id = new_node_id()
                    main_event = AMRNode(
                        id=main_event_id,
                        concept=word,
                        type=AMRNodeType.STATE,
                        text=word
                    )
                    nodes.append(main_event)
                    break

        # Extract entities (physical objects)
        entities = []
        for word in words:
            if word in self.physical_objects:
                entity_id = new_node_id()
                entity = AMRNode(
                    id=entity_id,
                    concept=word,
                    type=AMRNodeType.ENTITY,
                    text=word
                )
                nodes.append(entity)
                entities.append(entity)

                # Connect to main event if exists
                if main_event:
                    # First entity is typically ARG0 (agent), second is ARG1 (patient)
                    role = AMREdgeType.ARG0 if len(entities) == 1 else AMREdgeType.ARG1
                    edge = AMREdge(
                        source=main_event_id,
                        target=entity_id,
                        role=role
                    )
                    edges.append(edge)

        # Extract properties
        for word in words:
            if word in self.properties:
                prop_id = new_node_id()
                prop_node = AMRNode(
                    id=prop_id,
                    concept=word,
                    type=AMRNodeType.PROPERTY,
                    text=word
                )
                nodes.append(prop_node)

                # Connect property to last entity
                if entities:
                    edge = AMREdge(
                        source=entities[-1].id,
                        target=prop_id,
                        role=AMREdgeType.POSS
                    )
                    edges.append(edge)

        # Extract quantities (numbers with units)
        quantity_pattern = re.compile(r'(\d+\.?\d*)\s*([a-zA-Z]+)')
        for match in quantity_pattern.finditer(sentence):
            value = match.group(1)
            unit = match.group(2)

            quant_id = new_node_id()
            quant_node = AMRNode(
                id=quant_id,
                concept='quantity',
                type=AMRNodeType.QUANTITY,
                properties={'value': float(value), 'unit': unit}
            )
            nodes.append(quant_node)

            # Connect to last property or entity
            if nodes:
                target = nodes[-2] if len(nodes) > 1 else nodes[-1]
                edge = AMREdge(
                    source=target.id,
                    target=quant_id,
                    role=AMREdgeType.QUANT
                )
                edges.append(edge)

        # Extract spatial relations
        for prep in self.spatial_preps:
            if prep in sentence.lower():
                # Create location modifier
                loc_id = new_node_id()
                loc_node = AMRNode(
                    id=loc_id,
                    concept=prep,
                    type=AMRNodeType.PROPERTY
                )
                nodes.append(loc_node)

                # Connect to entities
                if len(entities) >= 2:
                    edge = AMREdge(
                        source=entities[0].id,
                        target=loc_id,
                        role=AMREdgeType.LOCATION
                    )
                    edges.append(edge)

                    edge2 = AMREdge(
                        source=loc_id,
                        target=entities[1].id,
                        role=AMREdgeType.ARG1
                    )
                    edges.append(edge2)

        # Build graph
        graph = AMRGraph(
            nodes=nodes,
            edges=edges,
            root=main_event_id if main_event else (nodes[0].id if nodes else None),
            text=sentence
        )

        return graph

    def graph_to_penman(self, graph: AMRGraph) -> str:
        """
        Convert AMR graph to PENMAN notation (standard AMR format).

        Args:
            graph: AMR graph

        Returns:
            PENMAN notation string
        """
        if not graph.root:
            return "()"

        def format_node(node_id: str, visited: Set[str], indent: int = 0) -> str:
            if node_id in visited:
                return node_id

            visited.add(node_id)
            node = next((n for n in graph.nodes if n.id == node_id), None)
            if not node:
                return node_id

            # Start with concept
            result = f"({node_id} / {node.concept}"

            # Add outgoing edges
            outgoing = [e for e in graph.edges if e.source == node_id]
            for edge in outgoing:
                result += f"\n{'  ' * (indent + 1)}:{edge.role.value.lower()} "
                result += format_node(edge.target, visited, indent + 1)

            result += ")"
            return result

        visited = set()
        return format_node(graph.root, visited)


# Convenience function
def parse_amr(text: str) -> AMRParseResult:
    """
    Convenience function to parse text into AMR.

    Args:
        text: Input text

    Returns:
        AMRParseResult with semantic graphs
    """
    parser = AMRParser()
    return parser.parse(text)


if __name__ == '__main__':
    # Test the parser
    test_text = """
    A block of mass 5 kg is placed on an inclined plane.
    The plane has an angle of 30 degrees.
    Calculate the force acting on the block.
    """

    parser = AMRParser()
    result = parser.parse(test_text)

    print("=" * 60)
    print("AMR Parser Test")
    print("=" * 60)

    print(f"\nConcepts found: {result.concepts}")
    print(f"\nEntities: {result.entities}")
    print(f"\nEvents: {result.events}")

    print(f"\nRelations found: {len(result.relations)}")
    for relation in result.relations[:10]:
        print(f"  {relation[0]} --[{relation[1]}]--> {relation[2]}")

    print(f"\nAMR Graphs: {len(result.graphs)}")
    for i, graph in enumerate(result.graphs):
        print(f"\nGraph {i+1}: {graph.text}")
        print(f"  Nodes: {len(graph.nodes)}")
        print(f"  Edges: {len(graph.edges)}")

        # Show PENMAN notation
        penman = parser.graph_to_penman(graph)
        print(f"  PENMAN:\n{penman}")

    print("=" * 60)
