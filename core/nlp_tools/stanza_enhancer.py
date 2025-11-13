"""
Stanza NLP Enhancer - Dependency Parsing and POS Tagging
Phase 2A of Advanced NLP Roadmap

Integrates Stanford Stanza for:
- Dependency parsing
- POS (Part-of-Speech) tagging
- Lemmatization
- Relationship extraction from grammatical structure

Installation:
    pip install stanza
    python -c "import stanza; stanza.download('en')"
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType

# Stanza is optional - graceful degradation if not installed
try:
    import stanza
    STANZA_AVAILABLE = True
except ImportError:
    STANZA_AVAILABLE = False
    stanza = None


@dataclass
class DependencyRelation:
    """
    A dependency relation extracted from text

    Example: "Force acts on block"
    - head: "acts"
    - dependent: "Force"
    - relation: "nsubj" (nominal subject)
    """
    head: str  # Head word
    head_pos: str  # POS tag of head
    dependent: str  # Dependent word
    dependent_pos: str  # POS tag of dependent
    relation: str  # Dependency relation type
    confidence: float = 1.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'head': self.head,
            'head_pos': self.head_pos,
            'dependent': self.dependent,
            'dependent_pos': self.dependent_pos,
            'relation': self.relation,
            'confidence': self.confidence
        }


@dataclass
class EntityMention:
    """An entity mentioned in text with POS information"""
    text: str
    lemma: str  # Lemmatized form
    pos: str  # Part-of-speech tag
    start_char: int
    end_char: int
    dependencies: List[DependencyRelation] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'lemma': self.lemma,
            'pos': self.pos,
            'start_char': self.start_char,
            'end_char': self.end_char,
            'dependencies': [d.to_dict() for d in self.dependencies]
        }


class StanzaEnhancer:
    """
    Stanza-based NLP enhancement for STEM text

    Provides:
    - Dependency parsing to extract relationships
    - POS tagging for entity classification
    - Lemmatization for normalization
    - Grammatical structure analysis
    """

    def __init__(self, language: str = 'en', verbose: bool = False):
        """
        Initialize Stanza enhancer

        Args:
            language: Language code (default: 'en')
            verbose: Enable verbose logging

        Raises:
            ImportError: If Stanza is not installed
        """
        if not STANZA_AVAILABLE:
            raise ImportError(
                "Stanza is not installed. Install with: pip install stanza && "
                "python -c 'import stanza; stanza.download(\"en\")'"
            )

        self.language = language
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Initialize Stanza pipeline
        # Processors: tokenize, pos, lemma, depparse
        try:
            self.nlp = stanza.Pipeline(
                language,
                processors='tokenize,pos,lemma,depparse',
                verbose=verbose,
                download_method=None  # Don't auto-download
            )
            if verbose:
                self.logger.info("Stanza pipeline initialized successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Stanza pipeline: {e}. "
                f"Make sure you've downloaded the model: python -c 'import stanza; stanza.download(\"{language}\")'"
            )

    # ========== Text Analysis ==========

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text with Stanza

        Args:
            text: Input text

        Returns:
            Dict with analysis results including dependencies, POS tags, lemmas
        """
        try:
            doc = self.nlp(text)

            result = {
                'text': text,
                'sentences': [],
                'dependencies': [],
                'entities': [],
                'triples': []
            }

            for sentence in doc.sentences:
                sent_data = {
                    'text': sentence.text,
                    'tokens': [],
                    'dependencies': []
                }

                # Extract tokens and POS tags
                for word in sentence.words:
                    sent_data['tokens'].append({
                        'text': word.text,
                        'lemma': word.lemma,
                        'pos': word.pos,
                        'xpos': word.xpos,
                        'feats': word.feats
                    })

                # Extract dependencies
                for word in sentence.words:
                    if word.head > 0:  # Skip root
                        head_word = sentence.words[word.head - 1]

                        dep = DependencyRelation(
                            head=head_word.text,
                            head_pos=head_word.pos,
                            dependent=word.text,
                            dependent_pos=word.pos,
                            relation=word.deprel
                        )

                        sent_data['dependencies'].append(dep.to_dict())
                        result['dependencies'].append(dep.to_dict())

                result['sentences'].append(sent_data)

            # Extract entity mentions (nouns and noun phrases)
            result['entities'] = self._extract_entities(doc)

            # Extract subject-verb-object triples
            result['triples'] = self._extract_triples(doc)

            return result

        except Exception as e:
            self.logger.error(f"Stanza analysis failed: {e}")
            return {'text': text, 'error': str(e)}

    def _extract_entities(self, doc) -> List[Dict]:
        """Extract entity mentions from document"""
        entities = []

        for sentence in doc.sentences:
            for word in sentence.words:
                # Extract nouns and proper nouns as entities
                if word.pos in ['NOUN', 'PROPN']:
                    entities.append({
                        'text': word.text,
                        'lemma': word.lemma,
                        'pos': word.pos,
                        'sentence': sentence.text
                    })

        return entities

    def _extract_triples(self, doc) -> List[Dict]:
        """
        Extract (subject, verb, object) triples

        Example: "Force acts on block" → (Force, acts, block)
        """
        triples = []

        for sentence in doc.sentences:
            # Build word index
            words = sentence.words

            # Find verbs (potential relations)
            for word in words:
                if word.pos in ['VERB']:
                    verb = word.text
                    subject = None
                    obj = None

                    # Find subject (nsubj) and object (obj, dobj)
                    for other_word in words:
                        if other_word.head == word.id:
                            if other_word.deprel in ['nsubj', 'nsubj:pass']:
                                subject = other_word.text
                            elif other_word.deprel in ['obj', 'dobj', 'obl']:
                                obj = other_word.text

                    if subject and obj:
                        triples.append({
                            'subject': subject,
                            'relation': verb,
                            'object': obj,
                            'sentence': sentence.text
                        })

        return triples

    # ========== Relationship Extraction ==========

    def extract_relationships(self, text: str) -> List[Dict]:
        """
        Extract relationships from text using dependency parsing

        Args:
            text: Input text

        Returns:
            List of relationship dicts with subject, relation, target

        Example:
            "A 10N force acts on a 5kg block"
            →  [{'subject': 'force', 'relation': 'acts_on', 'target': 'block'}]
        """
        analysis = self.analyze(text)
        relationships = []

        # Use triples as base relationships
        for triple in analysis.get('triples', []):
            relationships.append({
                'subject': triple['subject'],
                'type': triple['relation'],
                'target': triple['object'],
                'source': 'stanza_dependency',
                'confidence': 0.8
            })

        # Extract additional relationships from dependencies
        for dep in analysis.get('dependencies', []):
            # Map dependency relations to semantic relationships
            relation_type = self._map_dependency_to_relation(dep['relation'])

            if relation_type:
                relationships.append({
                    'subject': dep['dependent'],
                    'type': relation_type,
                    'target': dep['head'],
                    'source': 'stanza_dependency',
                    'confidence': 0.6
                })

        return relationships

    def _map_dependency_to_relation(self, deprel: str) -> Optional[str]:
        """Map Stanza dependency relation to semantic relation type"""
        # Map dependency relations to semantic relations
        mapping = {
            'nsubj': 'subject_of',
            'obj': 'object_of',
            'dobj': 'object_of',
            'nmod': 'modifier_of',
            'amod': 'modifies',
            'compound': 'part_of',
            'conj': 'related_to',
            'obl': 'oblique_of',
            'case': 'has_case',
            'det': 'determined_by'
        }

        return mapping.get(deprel)

    # ========== Property Graph Integration ==========

    def enrich_property_graph(self, text: str, graph: PropertyGraph) -> PropertyGraph:
        """
        Enrich a property graph with relationships extracted from text

        Args:
            text: Problem text
            graph: Existing PropertyGraph to enrich

        Returns:
            Enriched PropertyGraph
        """
        # Extract relationships
        relationships = self.extract_relationships(text)

        # Add relationships to graph
        for rel in relationships:
            subject = rel['subject']
            target = rel['target']
            rel_type = rel['type']

            # Try to find matching nodes in graph
            subject_node = self._find_node_by_text(graph, subject)
            target_node = self._find_node_by_text(graph, target)

            # If both nodes exist, add edge
            if subject_node and target_node:
                # Map relation type to EdgeType
                edge_type = self._map_relation_to_edge_type(rel_type)

                edge = GraphEdge(
                    source=subject_node.id,
                    target=target_node.id,
                    type=edge_type,
                    label=rel_type,
                    confidence=rel.get('confidence', 0.7),
                    metadata={'source': 'stanza'}
                )

                try:
                    graph.add_edge(edge)
                except ValueError:
                    # Edge already exists or nodes don't exist
                    pass

        return graph

    def _find_node_by_text(self, graph: PropertyGraph, text: str) -> Optional[GraphNode]:
        """Find a node in graph by matching text"""
        text_lower = text.lower()

        for node in graph.get_all_nodes():
            if text_lower in node.label.lower() or text_lower in node.id.lower():
                return node

            # Check properties
            for prop_value in node.properties.values():
                if isinstance(prop_value, str) and text_lower in prop_value.lower():
                    return node

        return None

    def _map_relation_to_edge_type(self, relation: str) -> EdgeType:
        """Map textual relation to EdgeType"""
        relation_lower = relation.lower()

        # Map common relations
        if 'act' in relation_lower:
            return EdgeType.ACTS_ON
        elif 'connect' in relation_lower:
            return EdgeType.CONNECTED_TO
        elif 'contain' in relation_lower:
            return EdgeType.CONTAINS
        elif 'locate' in relation_lower or 'at' in relation_lower:
            return EdgeType.LOCATED_AT
        elif 'cause' in relation_lower:
            return EdgeType.CAUSES
        elif 'part' in relation_lower:
            return EdgeType.PART_OF
        else:
            return EdgeType.RELATED_TO

    # ========== Utility Methods ==========

    def get_pos_tags(self, text: str) -> List[Tuple[str, str]]:
        """
        Get POS tags for text

        Args:
            text: Input text

        Returns:
            List of (word, pos_tag) tuples
        """
        analysis = self.analyze(text)
        tags = []

        for sentence in analysis.get('sentences', []):
            for token in sentence.get('tokens', []):
                tags.append((token['text'], token['pos']))

        return tags

    def get_lemmas(self, text: str) -> Dict[str, str]:
        """
        Get lemmatized forms of words

        Args:
            text: Input text

        Returns:
            Dict mapping words to their lemmas
        """
        analysis = self.analyze(text)
        lemmas = {}

        for sentence in analysis.get('sentences', []):
            for token in sentence.get('tokens', []):
                lemmas[token['text']] = token['lemma']

        return lemmas

    def is_available(self) -> bool:
        """Check if Stanza is available"""
        return STANZA_AVAILABLE and self.nlp is not None

    def __repr__(self) -> str:
        """String representation"""
        return f"StanzaEnhancer(language='{self.language}', available={self.is_available()})"


# ========== Standalone Functions ==========

def check_stanza_availability() -> bool:
    """
    Check if Stanza is available

    Returns:
        True if Stanza is installed and models are downloaded
    """
    if not STANZA_AVAILABLE:
        return False

    try:
        # Try to create a minimal pipeline
        nlp = stanza.Pipeline('en', processors='tokenize', verbose=False, download_method=None)
        return True
    except:
        return False


def extract_relationships_simple(text: str) -> List[Dict]:
    """
    Simple relationship extraction using Stanza

    Args:
        text: Input text

    Returns:
        List of relationships

    Example:
        >>> extract_relationships_simple("Force acts on block")
        [{'subject': 'Force', 'relation': 'acts', 'object': 'block'}]
    """
    if not STANZA_AVAILABLE:
        return []

    try:
        enhancer = StanzaEnhancer(verbose=False)
        return enhancer.extract_relationships(text)
    except Exception:
        return []
