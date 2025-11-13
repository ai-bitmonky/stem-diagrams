"""
OpenIE Extractor - Open Information Extraction
Phase 6A of Advanced NLP Roadmap

Extracts (subject, relation, object) triples from text without
predefined schemas. Useful for discovering new relationships
in scientific text.

Supports multiple backends:
- AllenNLP OpenIE (lightweight, Python-native)
- Stanford CoreNLP OpenIE (more accurate, requires Java)
- Fallback pattern-based extraction

Installation:
    pip install allennlp allennlp-models  # For AllenNLP backend
    # OR download Stanford CoreNLP for Java backend
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
import re
import logging

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType

# AllenNLP OpenIE (optional)
try:
    from allennlp.predictors import Predictor
    ALLENNLP_AVAILABLE = True
except ImportError:
    ALLENNLP_AVAILABLE = False
    Predictor = None


@dataclass
class Triple:
    """
    (Subject, Relation, Object) triple

    Example: ("force", "acts on", "mass")
    """
    subject: str
    relation: str
    object: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'subject': self.subject,
            'relation': self.relation,
            'object': self.object,
            'confidence': self.confidence,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"({self.subject}) --[{self.relation}]-> ({self.object})"


@dataclass
class OpenIEResult:
    """Result from OpenIE extraction"""
    text: str
    triples: List[Triple] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'triples': [t.to_dict() for t in self.triples],
            'triple_count': len(self.triples),
            'metadata': self.metadata
        }


class OpenIEExtractor:
    """
    Open Information Extraction for discovering relationships

    Uses pattern matching and optional AllenNLP backend for
    extracting (subject, relation, object) triples from text.
    """

    def __init__(self,
                 backend: str = 'allennlp',
                 verbose: bool = False):
        """
        Initialize OpenIE extractor

        Args:
            backend: Backend to use ('allennlp', 'stanford', 'pattern')
            verbose: Enable verbose logging
        """
        self.backend = backend
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        self.predictor = None

        if backend == 'allennlp' and ALLENNLP_AVAILABLE:
            try:
                if self.verbose:
                    self.logger.info("Loading AllenNLP OpenIE model...")

                # Load pre-trained OpenIE model
                model_url = "https://storage.googleapis.com/allennlp-public-models/openie-model.2020.03.26.tar.gz"
                self.predictor = Predictor.from_path(model_url)

                if self.verbose:
                    self.logger.info("AllenNLP OpenIE loaded successfully")

            except Exception as e:
                self.logger.warning(f"Failed to load AllenNLP OpenIE: {e}")
                self.logger.warning("Falling back to pattern-based extraction")
                self.backend = 'pattern'

        elif backend == 'stanford':
            self.logger.warning("Stanford CoreNLP backend not implemented. Using pattern-based extraction.")
            self.backend = 'pattern'

        elif backend == 'pattern':
            if self.verbose:
                self.logger.info("Using pattern-based OpenIE extraction")

    # ========== Triple Extraction ==========

    def extract(self, text: str) -> OpenIEResult:
        """
        Extract triples from text

        Args:
            text: Input text

        Returns:
            OpenIEResult with extracted triples

        Example:
            >>> extractor = OpenIEExtractor()
            >>> result = extractor.extract("The force acts on the mass.")
            >>> for triple in result.triples:
            ...     print(triple)
            (force) --[acts on]-> (mass)
        """
        if self.backend == 'allennlp' and self.predictor:
            return self._extract_allennlp(text)
        elif self.backend == 'stanford':
            return self._extract_stanford(text)
        else:
            return self._extract_pattern(text)

    def _extract_allennlp(self, text: str) -> OpenIEResult:
        """Extract using AllenNLP OpenIE"""
        try:
            prediction = self.predictor.predict(sentence=text)

            triples = []
            for extraction in prediction.get('verbs', []):
                # AllenNLP returns verb-based extractions
                description = extraction.get('description', '')

                # Parse description (format: "subject: X; relation: Y; object: Z")
                triple = self._parse_allennlp_description(description, text)
                if triple:
                    triples.append(triple)

            return OpenIEResult(
                text=text,
                triples=triples,
                metadata={'backend': 'allennlp', 'extraction_count': len(triples)}
            )

        except Exception as e:
            self.logger.error(f"AllenNLP extraction failed: {e}")
            return self._extract_pattern(text)

    def _parse_allennlp_description(self, description: str, text: str) -> Optional[Triple]:
        """Parse AllenNLP extraction description"""
        # Try to extract ARG0 (subject), V (verb), ARG1 (object)
        # This is a simplified parser
        parts = description.split()

        subject = None
        relation = None
        obj = None

        i = 0
        while i < len(parts):
            part = parts[i]

            if part.startswith('[ARG0:'):
                # Extract subject
                subject_parts = []
                while i < len(parts) and not parts[i].endswith(']'):
                    if parts[i].startswith('[ARG0:'):
                        subject_parts.append(parts[i][6:])
                    else:
                        subject_parts.append(parts[i])
                    i += 1
                if i < len(parts):
                    last = parts[i].rstrip(']')
                    subject_parts.append(last)
                subject = ' '.join(subject_parts)

            elif part.startswith('[V:'):
                # Extract verb/relation
                relation_parts = []
                while i < len(parts) and not parts[i].endswith(']'):
                    if parts[i].startswith('[V:'):
                        relation_parts.append(parts[i][3:])
                    else:
                        relation_parts.append(parts[i])
                    i += 1
                if i < len(parts):
                    last = parts[i].rstrip(']')
                    relation_parts.append(last)
                relation = ' '.join(relation_parts)

            elif part.startswith('[ARG1:'):
                # Extract object
                obj_parts = []
                while i < len(parts) and not parts[i].endswith(']'):
                    if parts[i].startswith('[ARG1:'):
                        obj_parts.append(parts[i][6:])
                    else:
                        obj_parts.append(parts[i])
                    i += 1
                if i < len(parts):
                    last = parts[i].rstrip(']')
                    obj_parts.append(last)
                obj = ' '.join(obj_parts)

            i += 1

        if subject and relation and obj:
            return Triple(
                subject=subject.strip(),
                relation=relation.strip(),
                object=obj.strip(),
                confidence=0.9
            )

        return None

    def _extract_stanford(self, text: str) -> OpenIEResult:
        """Extract using Stanford CoreNLP OpenIE (not implemented)"""
        # Placeholder for Stanford CoreNLP integration
        return self._extract_pattern(text)

    def _extract_pattern(self, text: str) -> OpenIEResult:
        """Extract using pattern matching"""
        triples = []

        # Pattern 1: Subject + Verb + Object
        # Example: "Force acts on mass"
        pattern1 = r'(\w+(?:\s+\w+)?)\s+(\w+(?:\s+\w+)?)\s+(?:on|to|with|at|in)\s+(\w+(?:\s+\w+)?)'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)

        for match in matches1:
            subject, verb, obj = match
            relation = f"{verb} on"  # Include preposition

            triple = Triple(
                subject=subject.strip(),
                relation=relation.strip(),
                object=obj.strip(),
                confidence=0.7  # Lower confidence for pattern matching
            )
            triples.append(triple)

        # Pattern 2: Subject + "is" + Description
        # Example: "Force is applied to the body"
        pattern2 = r'(\w+(?:\s+\w+)?)\s+is\s+(\w+(?:\s+\w+)?)\s+(?:to|on)\s+(\w+(?:\s+\w+)?)'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)

        for match in matches2:
            subject, action, obj = match
            relation = f"is {action}"

            triple = Triple(
                subject=subject.strip(),
                relation=relation.strip(),
                object=obj.strip(),
                confidence=0.7
            )
            triples.append(triple)

        # Pattern 3: Subject + Action + Object (direct)
        # Example: "Battery powers circuit"
        pattern3 = r'(\w+(?:\s+\w+)?)\s+(\w+s)\s+(\w+(?:\s+\w+)?)'
        matches3 = re.findall(pattern3, text, re.IGNORECASE)

        for match in matches3:
            subject, verb, obj = match

            # Skip if already found
            if any(t.subject.lower() == subject.lower() and
                   t.object.lower() == obj.lower()
                   for t in triples):
                continue

            triple = Triple(
                subject=subject.strip(),
                relation=verb.strip(),
                object=obj.strip(),
                confidence=0.6
            )
            triples.append(triple)

        return OpenIEResult(
            text=text,
            triples=triples,
            metadata={'backend': 'pattern', 'pattern_count': 3}
        )

    # ========== Batch Processing ==========

    def extract_batch(self, texts: List[str]) -> List[OpenIEResult]:
        """
        Extract triples from multiple texts

        Args:
            texts: List of input texts

        Returns:
            List of OpenIEResult objects
        """
        return [self.extract(text) for text in texts]

    # ========== Property Graph Integration ==========

    def to_property_graph(self, result: OpenIEResult) -> PropertyGraph:
        """
        Convert OpenIE result to PropertyGraph

        Args:
            result: OpenIEResult from extraction

        Returns:
            PropertyGraph with subjects and objects as nodes, relations as edges

        Example:
            >>> result = extractor.extract(text)
            >>> graph = extractor.to_property_graph(result)
        """
        graph = PropertyGraph()

        # Track unique entities
        entities: Dict[str, str] = {}  # text -> node_id

        # Add triples to graph
        for triple in result.triples:
            # Add subject node
            if triple.subject.lower() not in entities:
                subject_id = f"entity_{len(entities)}"
                subject_node = GraphNode(
                    id=subject_id,
                    type=NodeType.OBJECT,
                    label=triple.subject,
                    properties={'confidence': triple.confidence}
                )
                graph.add_node(subject_node)
                entities[triple.subject.lower()] = subject_id
            else:
                subject_id = entities[triple.subject.lower()]

            # Add object node
            if triple.object.lower() not in entities:
                object_id = f"entity_{len(entities)}"
                object_node = GraphNode(
                    id=object_id,
                    type=NodeType.OBJECT,
                    label=triple.object,
                    properties={'confidence': triple.confidence}
                )
                graph.add_node(object_node)
                entities[triple.object.lower()] = object_id
            else:
                object_id = entities[triple.object.lower()]

            # Add relation edge
            edge = GraphEdge(
                source=subject_id,
                target=object_id,
                type=self._infer_edge_type(triple.relation),
                label=triple.relation,
                confidence=triple.confidence,
                metadata={'source': 'openie'}
            )

            graph.add_edge(edge)

        return graph

    def _infer_edge_type(self, relation: str) -> EdgeType:
        """Infer EdgeType from relation text"""
        relation_lower = relation.lower()

        if 'act' in relation_lower:
            return EdgeType.ACTS_ON
        elif 'connect' in relation_lower or 'link' in relation_lower:
            return EdgeType.CONNECTED_TO
        elif 'contain' in relation_lower:
            return EdgeType.CONTAINS
        elif 'cause' in relation_lower:
            return EdgeType.CAUSES
        elif 'locate' in relation_lower or 'at' in relation_lower:
            return EdgeType.LOCATED_AT
        elif 'part' in relation_lower:
            return EdgeType.PART_OF
        else:
            return EdgeType.RELATED_TO

    # ========== Triple Filtering and Merging ==========

    def filter_triples(self,
                      triples: List[Triple],
                      min_confidence: float = 0.5,
                      remove_duplicates: bool = True) -> List[Triple]:
        """
        Filter triples by confidence and remove duplicates

        Args:
            triples: List of triples
            min_confidence: Minimum confidence threshold
            remove_duplicates: Remove duplicate triples

        Returns:
            Filtered list of triples
        """
        # Filter by confidence
        filtered = [t for t in triples if t.confidence >= min_confidence]

        # Remove duplicates
        if remove_duplicates:
            unique = []
            seen: Set[Tuple[str, str, str]] = set()

            for triple in filtered:
                key = (triple.subject.lower(), triple.relation.lower(), triple.object.lower())
                if key not in seen:
                    unique.append(triple)
                    seen.add(key)

            return unique

        return filtered

    def merge_results(self, results: List[OpenIEResult]) -> OpenIEResult:
        """
        Merge multiple OpenIE results

        Args:
            results: List of OpenIEResult objects

        Returns:
            Merged OpenIEResult
        """
        all_triples = []
        for result in results:
            all_triples.extend(result.triples)

        # Remove duplicates
        filtered_triples = self.filter_triples(all_triples, min_confidence=0.5)

        return OpenIEResult(
            text=' '.join(r.text for r in results),
            triples=filtered_triples,
            metadata={'merged_from': len(results)}
        )

    # ========== Utility Methods ==========

    def is_available(self) -> bool:
        """Check if OpenIE backend is available"""
        return self.backend in ['pattern', 'allennlp', 'stanford']

    def get_relation_types(self, result: OpenIEResult) -> Dict[str, int]:
        """Get count of relations by type"""
        type_counts: Dict[str, int] = {}
        for triple in result.triples:
            type_counts[triple.relation] = type_counts.get(triple.relation, 0) + 1
        return type_counts

    def __repr__(self) -> str:
        """String representation"""
        return f"OpenIEExtractor(backend='{self.backend}', available={self.is_available()})"


# ========== Standalone Functions ==========

def check_openie_availability() -> bool:
    """Check if OpenIE is available"""
    return True  # Pattern-based extraction always available


def extract_triples(text: str) -> List[Tuple[str, str, str]]:
    """
    Simple triple extraction

    Args:
        text: Input text

    Returns:
        List of (subject, relation, object) tuples

    Example:
        >>> triples = extract_triples("Force acts on mass.")
        >>> for s, r, o in triples:
        ...     print(f"{s} --{r}-> {o}")
    """
    extractor = OpenIEExtractor(backend='pattern', verbose=False)
    result = extractor.extract(text)

    return [(t.subject, t.relation, t.object) for t in result.triples]


def build_knowledge_graph_from_triples(texts: List[str]) -> PropertyGraph:
    """
    Build knowledge graph from multiple texts using OpenIE

    Args:
        texts: List of input texts

    Returns:
        PropertyGraph with extracted knowledge

    Example:
        >>> graph = build_knowledge_graph_from_triples([
        ...     "Force acts on mass.",
        ...     "Mass has inertia.",
        ...     "Inertia resists acceleration."
        ... ])
        >>> print(graph.summary())
    """
    extractor = OpenIEExtractor(verbose=False)
    results = extractor.extract_batch(texts)

    # Merge all results
    merged = extractor.merge_results(results)

    # Convert to graph
    return extractor.to_property_graph(merged)
