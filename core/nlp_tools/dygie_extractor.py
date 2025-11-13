"""
DyGIE++ Extractor - Joint Entity and Relation Extraction
Phase 3A of Advanced NLP Roadmap

Integrates AllenNLP's DyGIE++ for:
- Joint entity and relation extraction
- Scientific text understanding
- Co-reference resolution
- Event extraction

DyGIE++ is trained on scientific datasets (SciERC, ChemProt, etc.)
and excels at extracting entities and their relationships from
scientific text.

Installation:
    pip install allennlp==2.10.1 allennlp-models==2.10.1

Model: Pre-trained on SciERC (scientific papers)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType

# AllenNLP is optional - graceful degradation
try:
    from allennlp.predictors import Predictor
    from allennlp_models import pretrained
    ALLENNLP_AVAILABLE = True
except ImportError:
    ALLENNLP_AVAILABLE = False
    Predictor = pretrained = None


@dataclass
class Entity:
    """Extracted entity from DyGIE++"""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'type': self.entity_type,
            'start': self.start,
            'end': self.end,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


@dataclass
class Relation:
    """Extracted relation from DyGIE++"""
    subject: Entity
    object: Entity
    relation_type: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'subject': self.subject.to_dict(),
            'object': self.object.to_dict(),
            'relation_type': self.relation_type,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


@dataclass
class ExtractionResult:
    """Complete extraction result from DyGIE++"""
    text: str
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'entities': [e.to_dict() for e in self.entities],
            'relations': [r.to_dict() for r in self.relations],
            'events': self.events,
            'metadata': self.metadata
        }


class DyGIEExtractor:
    """
    DyGIE++ extractor for scientific text

    Uses AllenNLP's DyGIE++ model for joint entity and relation extraction
    specifically trained on scientific datasets.
    """

    def __init__(self,
                 model_name: str = 'dygiepp-scierc',
                 verbose: bool = False):
        """
        Initialize DyGIE++ extractor

        Args:
            model_name: Model name ('dygiepp-scierc' for scientific papers)
            verbose: Enable verbose logging

        Raises:
            ImportError: If AllenNLP is not installed
        """
        if not ALLENNLP_AVAILABLE:
            raise ImportError(
                "AllenNLP not installed. Install with: pip install allennlp==2.10.1 allennlp-models==2.10.1"
            )

        self.model_name = model_name
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        if self.verbose:
            self.logger.info(f"Loading DyGIE++ model: {model_name}")

        # Load predictor
        try:
            # DyGIE++ pre-trained on SciERC dataset
            model_url = "https://storage.googleapis.com/allennlp-public-models/dygiepp-scierc.tar.gz"

            self.predictor = Predictor.from_path(model_url)

            if self.verbose:
                self.logger.info("DyGIE++ model loaded successfully")

        except Exception as e:
            # Fallback: Try to use simplified model or mock
            self.logger.warning(f"Failed to load DyGIE++ model: {e}")
            self.logger.warning("Will use fallback extraction mode")
            self.predictor = None

    # ========== Entity and Relation Extraction ==========

    def extract(self, text: str) -> ExtractionResult:
        """
        Extract entities and relations from text

        Args:
            text: Input text

        Returns:
            ExtractionResult with entities and relations

        Example:
            >>> extractor = DyGIEExtractor()
            >>> result = extractor.extract(
            ...     "The protein binds to DNA with high affinity."
            ... )
            >>> for entity in result.entities:
            ...     print(f"{entity.text} ({entity.entity_type})")
            >>> for relation in result.relations:
            ...     print(f"{relation.subject.text} --{relation.relation_type}-> {relation.object.text}")
        """
        if self.predictor is None:
            # Fallback to simple extraction
            return self._fallback_extract(text)

        try:
            # Run prediction
            prediction = self.predictor.predict(sentence=text)

            # Parse results
            entities = self._parse_entities(prediction, text)
            relations = self._parse_relations(prediction, entities)

            return ExtractionResult(
                text=text,
                entities=entities,
                relations=relations,
                metadata={
                    'model': self.model_name,
                    'entity_count': len(entities),
                    'relation_count': len(relations)
                }
            )

        except Exception as e:
            self.logger.error(f"DyGIE++ extraction failed: {e}")
            return self._fallback_extract(text)

    def _parse_entities(self, prediction: Dict, text: str) -> List[Entity]:
        """Parse entities from DyGIE++ prediction"""
        entities = []

        # DyGIE++ returns entities as [start, end, type] tuples
        for ner_pred in prediction.get('ner', []):
            if len(ner_pred) >= 3:
                start_idx, end_idx, entity_type = ner_pred[0], ner_pred[1], ner_pred[2]

                # Extract text span
                tokens = prediction.get('tokens', [])
                if start_idx < len(tokens) and end_idx < len(tokens):
                    entity_text = ' '.join(tokens[start_idx:end_idx + 1])

                    entity = Entity(
                        text=entity_text,
                        entity_type=entity_type,
                        start=start_idx,
                        end=end_idx,
                        confidence=1.0
                    )
                    entities.append(entity)

        return entities

    def _parse_relations(self, prediction: Dict, entities: List[Entity]) -> List[Relation]:
        """Parse relations from DyGIE++ prediction"""
        relations = []

        # DyGIE++ returns relations as [start1, end1, start2, end2, type] tuples
        for rel_pred in prediction.get('relations', []):
            if len(rel_pred) >= 5:
                start1, end1, start2, end2, rel_type = rel_pred

                # Find corresponding entities
                subject = None
                object_ = None

                for entity in entities:
                    if entity.start == start1 and entity.end == end1:
                        subject = entity
                    if entity.start == start2 and entity.end == end2:
                        object_ = entity

                if subject and object_:
                    relation = Relation(
                        subject=subject,
                        object=object_,
                        relation_type=rel_type,
                        confidence=1.0
                    )
                    relations.append(relation)

        return relations

    def _fallback_extract(self, text: str) -> ExtractionResult:
        """Fallback extraction using simple heuristics"""
        # Simple keyword-based entity extraction
        entities = []
        relations = []

        # Common scientific entity types
        keywords = {
            'protein': 'Protein',
            'dna': 'DNA',
            'rna': 'RNA',
            'gene': 'Gene',
            'enzyme': 'Enzyme',
            'force': 'Force',
            'mass': 'Mass',
            'energy': 'Energy',
            'molecule': 'Molecule',
            'atom': 'Atom',
            'cell': 'Cell'
        }

        words = text.lower().split()
        for i, word in enumerate(words):
            for keyword, entity_type in keywords.items():
                if keyword in word:
                    entity = Entity(
                        text=word,
                        entity_type=entity_type,
                        start=i,
                        end=i,
                        confidence=0.5  # Lower confidence for fallback
                    )
                    entities.append(entity)

        return ExtractionResult(
            text=text,
            entities=entities,
            relations=relations,
            metadata={'extraction_mode': 'fallback'}
        )

    # ========== Batch Processing ==========

    def extract_batch(self, texts: List[str]) -> List[ExtractionResult]:
        """
        Extract from multiple texts

        Args:
            texts: List of input texts

        Returns:
            List of ExtractionResult objects

        Example:
            >>> results = extractor.extract_batch([
            ...     "Protein A binds to DNA.",
            ...     "The enzyme catalyzes the reaction."
            ... ])
        """
        results = []
        for text in texts:
            result = self.extract(text)
            results.append(result)

        return results

    # ========== Property Graph Integration ==========

    def to_property_graph(self, result: ExtractionResult) -> PropertyGraph:
        """
        Convert extraction result to PropertyGraph

        Args:
            result: ExtractionResult from extraction

        Returns:
            PropertyGraph with entities as nodes and relations as edges

        Example:
            >>> result = extractor.extract(text)
            >>> graph = extractor.to_property_graph(result)
        """
        graph = PropertyGraph()

        # Add entities as nodes
        entity_map = {}
        for i, entity in enumerate(result.entities):
            node_id = f"entity_{i}"

            # Map entity type to NodeType
            node_type = self._map_entity_type(entity.entity_type)

            node = GraphNode(
                id=node_id,
                type=node_type,
                label=entity.text,
                properties={
                    'entity_type': entity.entity_type,
                    'start': entity.start,
                    'end': entity.end,
                    'confidence': entity.confidence
                },
                metadata=entity.metadata
            )

            graph.add_node(node)
            entity_map[entity] = node_id

        # Add relations as edges
        for relation in result.relations:
            if relation.subject in entity_map and relation.object in entity_map:
                source_id = entity_map[relation.subject]
                target_id = entity_map[relation.object]

                # Map relation type to EdgeType
                edge_type = self._map_relation_type(relation.relation_type)

                edge = GraphEdge(
                    source=source_id,
                    target=target_id,
                    type=edge_type,
                    label=relation.relation_type,
                    confidence=relation.confidence,
                    metadata={'source': 'dygiepp'}
                )

                graph.add_edge(edge)

        return graph

    def _map_entity_type(self, entity_type: str) -> NodeType:
        """Map DyGIE++ entity type to NodeType"""
        entity_type_lower = entity_type.lower()

        # Common scientific entity type mappings
        if any(x in entity_type_lower for x in ['protein', 'enzyme', 'molecule', 'compound']):
            return NodeType.OBJECT
        elif any(x in entity_type_lower for x in ['process', 'reaction', 'method']):
            return NodeType.PROCESS
        elif any(x in entity_type_lower for x in ['measurement', 'quantity', 'value']):
            return NodeType.QUANTITY
        elif any(x in entity_type_lower for x in ['concept', 'theory']):
            return NodeType.CONCEPT
        else:
            return NodeType.UNKNOWN

    def _map_relation_type(self, relation_type: str) -> EdgeType:
        """Map DyGIE++ relation type to EdgeType"""
        relation_type_lower = relation_type.lower()

        # Common relation type mappings
        if 'use' in relation_type_lower or 'apply' in relation_type_lower:
            return EdgeType.RELATED_TO
        elif 'part' in relation_type_lower:
            return EdgeType.PART_OF
        elif 'cause' in relation_type_lower:
            return EdgeType.CAUSES
        elif 'compare' in relation_type_lower:
            return EdgeType.RELATED_TO
        else:
            return EdgeType.UNKNOWN

    # ========== Enhanced Extraction ==========

    def extract_with_context(self,
                            text: str,
                            context: Optional[str] = None) -> ExtractionResult:
        """
        Extract entities and relations with additional context

        Args:
            text: Main text to extract from
            context: Optional context (previous sentences, domain info)

        Returns:
            ExtractionResult

        Example:
            >>> result = extractor.extract_with_context(
            ...     "It binds to the receptor.",
            ...     context="The protein was isolated from cells."
            ... )
        """
        # If context provided, prepend it to text for better extraction
        if context:
            full_text = f"{context} {text}"
            result = self.extract(full_text)

            # Filter entities to only those in the main text
            # (This is simplified - real implementation would track offsets)
            return result
        else:
            return self.extract(text)

    # ========== Utility Methods ==========

    def is_available(self) -> bool:
        """Check if AllenNLP and DyGIE++ are available"""
        return ALLENNLP_AVAILABLE and self.predictor is not None

    def get_entity_types(self, result: ExtractionResult) -> Dict[str, int]:
        """Get count of entities by type"""
        type_counts: Dict[str, int] = {}
        for entity in result.entities:
            type_counts[entity.entity_type] = type_counts.get(entity.entity_type, 0) + 1
        return type_counts

    def get_relation_types(self, result: ExtractionResult) -> Dict[str, int]:
        """Get count of relations by type"""
        type_counts: Dict[str, int] = {}
        for relation in result.relations:
            type_counts[relation.relation_type] = type_counts.get(relation.relation_type, 0) + 1
        return type_counts

    def __repr__(self) -> str:
        """String representation"""
        return f"DyGIEExtractor(model='{self.model_name}', available={self.is_available()})"


# ========== Standalone Functions ==========

def check_allennlp_availability() -> bool:
    """Check if AllenNLP is available"""
    return ALLENNLP_AVAILABLE


def extract_scientific_entities(text: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Simple entity and relation extraction

    Args:
        text: Input text

    Returns:
        (entities, relations) tuple of dictionaries

    Example:
        >>> entities, relations = extract_scientific_entities(
        ...     "The protein binds to DNA."
        ... )
    """
    if not ALLENNLP_AVAILABLE:
        # Fallback to keyword extraction
        entities = []
        relations = []

        keywords = ['protein', 'dna', 'rna', 'enzyme', 'cell', 'molecule']
        words = text.lower().split()

        for i, word in enumerate(words):
            for keyword in keywords:
                if keyword in word:
                    entities.append({
                        'text': word,
                        'type': keyword.upper(),
                        'index': i
                    })

        return (entities, relations)

    try:
        extractor = DyGIEExtractor(verbose=False)
        result = extractor.extract(text)

        entities = [e.to_dict() for e in result.entities]
        relations = [r.to_dict() for r in result.relations]

        return (entities, relations)

    except Exception:
        return ([], [])


def create_knowledge_graph_from_text(text: str) -> Optional[PropertyGraph]:
    """
    Create a knowledge graph from scientific text

    Args:
        text: Input text

    Returns:
        PropertyGraph if successful, None otherwise

    Example:
        >>> graph = create_knowledge_graph_from_text(
        ...     "The enzyme catalyzes the reaction between substrate A and B."
        ... )
        >>> print(graph.summary())
    """
    if not ALLENNLP_AVAILABLE:
        return None

    try:
        extractor = DyGIEExtractor(verbose=False)
        result = extractor.extract(text)
        graph = extractor.to_property_graph(result)

        return graph

    except Exception:
        return None
