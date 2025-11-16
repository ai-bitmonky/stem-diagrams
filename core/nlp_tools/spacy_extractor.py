"""
spaCy NLP Extractor
Provides named entity recognition, dependency parsing, and linguistic analysis

Extracts:
- Named entities (PERSON, ORG, GPE, QUANTITY, etc.)
- Part-of-speech tags
- Dependency relations
- Noun chunks
- Lemmatization

Installation:
    pip install spacy
    python -m spacy download en_core_web_sm
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    Doc = None


@dataclass
class SpacyEntity:
    """Named entity extracted by spaCy"""
    text: str
    label: str
    start_char: int
    end_char: int

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'label': self.label,
            'start_char': self.start_char,
            'end_char': self.end_char
        }


@dataclass
class SpacyToken:
    """Token with linguistic annotations"""
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    is_stop: bool

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'lemma': self.lemma,
            'pos': self.pos,
            'tag': self.tag,
            'dep': self.dep,
            'is_stop': self.is_stop
        }


@dataclass
class SpacyResult:
    """Result from spaCy extraction"""
    text: str
    entities: List[SpacyEntity] = field(default_factory=list)
    tokens: List[SpacyToken] = field(default_factory=list)
    noun_chunks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'entities': [e.to_dict() for e in self.entities],
            'entity_count': len(self.entities),
            'tokens': [t.to_dict() for t in self.tokens],
            'token_count': len(self.tokens),
            'noun_chunks': self.noun_chunks,
            'noun_chunk_count': len(self.noun_chunks),
            'metadata': self.metadata
        }


class SpacyExtractor:
    """
    spaCy-based NLP extraction for entities, POS, and dependencies

    Provides comprehensive linguistic analysis using spaCy's
    pre-trained models.
    """

    _model_cache: Dict[str, "spacy.language.Language"] = {}

    def __init__(self, model_name: str = 'en_core_web_sm', verbose: bool = False):
        """
        Initialize spaCy extractor

        Args:
            model_name: spaCy model to use (default: en_core_web_sm)
            verbose: Enable verbose logging
        """
        self.model_name = model_name
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.nlp = None
        self._doc_cache: Dict[str, SpacyResult] = {}

        if not SPACY_AVAILABLE:
            raise ImportError(
                "spaCy not available. Install with: pip install spacy && "
                "python -m spacy download en_core_web_sm"
            )

        try:
            if model_name in SpacyExtractor._model_cache:
                self.nlp = SpacyExtractor._model_cache[model_name]
            else:
                if self.verbose:
                    self.logger.info(f"Loading spaCy model: {model_name}")

                # Disable multiprocessing to prevent semaphore leaks
                self.nlp = spacy.load(model_name, disable=[], exclude=[])
                # Disable parallelism in tokenizer to prevent resource leaks
                if hasattr(self.nlp.tokenizer, 'max_length'):
                    # Disable any internal multiprocessing
                    pass
                SpacyExtractor._model_cache[model_name] = self.nlp

            if self.verbose:
                self.logger.info(f"spaCy model {model_name} loaded successfully")

        except OSError as e:
            self.logger.error(
                f"spaCy model '{model_name}' not found. "
                f"Download with: python -m spacy download {model_name}"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to load spaCy model: {e}")
            raise

    def extract(self, text: str) -> SpacyResult:
        """
        Extract linguistic features from text

        Args:
            text: Input text

        Returns:
            SpacyResult with entities, tokens, and noun chunks
        """
        if not self.nlp:
            raise RuntimeError("spaCy model not initialized")

        if text in self._doc_cache:
            return self._doc_cache[text]

        # Process text
        doc = self.nlp(text)

        # Extract entities
        entities = [
            SpacyEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            )
            for ent in doc.ents
        ]

        # Extract tokens
        tokens = [
            SpacyToken(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_,
                is_stop=token.is_stop
            )
            for token in doc
        ]

        # Extract noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]

        # Build result
        result = SpacyResult(
            text=text,
            entities=entities,
            tokens=tokens,
            noun_chunks=noun_chunks,
            metadata={
                'model': self.model_name,
                'has_entities': len(entities) > 0,
                'has_noun_chunks': len(noun_chunks) > 0
            }
        )

        if self.verbose:
            self.logger.info(
                f"Extracted {len(entities)} entities, "
                f"{len(tokens)} tokens, "
                f"{len(noun_chunks)} noun chunks"
            )

        self._doc_cache[text] = result

        return result

    def extract_dict(self, text: str) -> Dict:
        """
        Extract and return as dictionary

        Args:
            text: Input text

        Returns:
            Dictionary with extraction results
        """
        result = self.extract(text)
        return result.to_dict()
