"""
SciBERT Embedder - Scientific Domain Embeddings
Phase 4A of Advanced NLP Roadmap

Integrates AllenAI's SciBERT for:
- Scientific domain text embeddings
- Entity similarity and disambiguation
- Domain-aware semantic search
- Improved entity classification

Installation:
    pip install transformers torch

Model: allenai/scibert_scivocab_uncased (110M parameters)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging
import numpy as np

# Transformers and torch are optional
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None
    AutoTokenizer = AutoModel = None


@dataclass
class EntityEmbedding:
    """Entity with SciBERT embedding"""
    text: str
    embedding: Optional[np.ndarray] = None
    entity_type: Optional[str] = None
    confidence: float = 0.0

    def similarity_to(self, other: 'EntityEmbedding') -> float:
        """Calculate cosine similarity to another entity"""
        if self.embedding is None or other.embedding is None:
            return 0.0

        # Cosine similarity
        dot_product = np.dot(self.embedding, other.embedding)
        norm_product = np.linalg.norm(self.embedding) * np.linalg.norm(other.embedding)

        if norm_product == 0:
            return 0.0

        return float(dot_product / norm_product)


@dataclass
class DisambiguationResult:
    """Result of entity disambiguation"""
    original_text: str
    candidates: List[EntityEmbedding] = field(default_factory=list)
    best_match: Optional[EntityEmbedding] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'original_text': self.original_text,
            'best_match': self.best_match.text if self.best_match else None,
            'confidence': self.confidence,
            'candidate_count': len(self.candidates)
        }


class SciBERTEmbedder:
    """
    SciBERT-based embedder for scientific text

    Uses AllenAI's SciBERT model trained on scientific papers
    for better understanding of scientific terminology.
    """

    def __init__(self,
                 model_name: str = 'allenai/scibert_scivocab_uncased',
                 device: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize SciBERT embedder

        Args:
            model_name: Model name from Hugging Face
            device: Device to use ('cuda', 'cpu', or None for auto)
            verbose: Enable verbose logging

        Raises:
            ImportError: If transformers or torch not installed
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers not installed. Install with: pip install transformers torch"
            )

        self.model_name = model_name
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Determine device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device

        if self.verbose:
            self.logger.info(f"Loading SciBERT model: {model_name}")
            self.logger.info(f"Using device: {self.device}")

        # Load tokenizer and model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode

            if self.verbose:
                self.logger.info("SciBERT model loaded successfully")

        except Exception as e:
            raise RuntimeError(f"Failed to load SciBERT model: {e}")

        # Cache for embeddings
        self._embedding_cache: Dict[str, np.ndarray] = {}

    # ========== Embedding Generation ==========

    def embed(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Generate SciBERT embedding for text

        Args:
            text: Input text
            use_cache: Use cached embeddings if available

        Returns:
            numpy array of embedding (768 dimensions)

        Example:
            >>> embedder = SciBERTEmbedder()
            >>> embedding = embedder.embed("ionic bond")
            >>> print(embedding.shape)  # (768,)
        """
        # Check cache
        if use_cache and text in self._embedding_cache:
            return self._embedding_cache[text]

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use [CLS] token embedding (first token)
        cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

        # Cache
        if use_cache:
            self._embedding_cache[text] = cls_embedding

        return cls_embedding

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts
            batch_size: Batch size for processing

        Returns:
            List of embeddings

        Example:
            >>> texts = ["force", "mass", "acceleration"]
            >>> embeddings = embedder.embed_batch(texts)
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Tokenize batch
            inputs = self.tokenizer(
                batch_texts,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=512
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Extract [CLS] embeddings
            batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            embeddings.extend(batch_embeddings)

        return embeddings

    # ========== Similarity and Comparison ==========

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1, where 1 is identical)

        Example:
            >>> sim = embedder.similarity("ionic bond", "covalent bond")
            >>> print(f"Similarity: {sim:.3f}")
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)

        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

        return float(similarity)

    def find_most_similar(self,
                         query: str,
                         candidates: List[str],
                         top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find most similar texts to query

        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return

        Returns:
            List of (text, similarity_score) tuples, sorted by similarity

        Example:
            >>> candidates = ["force", "mass", "energy", "power"]
            >>> results = embedder.find_most_similar("newton", candidates)
            >>> for text, score in results:
            ...     print(f"{text}: {score:.3f}")
        """
        query_emb = self.embed(query)
        candidate_embs = self.embed_batch(candidates)

        # Calculate similarities
        similarities = []
        for candidate, candidate_emb in zip(candidates, candidate_embs):
            sim = np.dot(query_emb, candidate_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(candidate_emb)
            )
            similarities.append((candidate, float(sim)))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    # ========== Entity Disambiguation ==========

    def disambiguate_entity(self,
                           entity_text: str,
                           knowledge_base: Dict[str, str],
                           threshold: float = 0.7) -> DisambiguationResult:
        """
        Disambiguate an entity against a knowledge base

        Args:
            entity_text: Entity text to disambiguate
            knowledge_base: Dict mapping entity IDs to descriptions
            threshold: Minimum similarity threshold

        Returns:
            DisambiguationResult with best match

        Example:
            >>> kb = {
            ...     "F1": "electrostatic force between charged particles",
            ...     "F2": "gravitational force due to mass",
            ...     "F3": "normal force from surface contact"
            ... }
            >>> result = embedder.disambiguate_entity("force from table", kb)
            >>> print(result.best_match.text)  # "F3"
        """
        entity_emb = self.embed(entity_text)

        # Create candidates
        candidates = []
        for entity_id, description in knowledge_base.items():
            desc_emb = self.embed(description)

            # Calculate similarity
            sim = np.dot(entity_emb, desc_emb) / (
                np.linalg.norm(entity_emb) * np.linalg.norm(desc_emb)
            )

            candidate = EntityEmbedding(
                text=entity_id,
                embedding=desc_emb,
                entity_type=knowledge_base.get('type'),
                confidence=float(sim)
            )
            candidates.append(candidate)

        # Sort by confidence
        candidates.sort(key=lambda c: c.confidence, reverse=True)

        # Get best match
        best_match = None
        confidence = 0.0

        if candidates and candidates[0].confidence >= threshold:
            best_match = candidates[0]
            confidence = candidates[0].confidence

        return DisambiguationResult(
            original_text=entity_text,
            candidates=candidates,
            best_match=best_match,
            confidence=confidence
        )

    # ========== Domain Classification ==========

    def classify_domain(self,
                       text: str,
                       domain_descriptions: Dict[str, str]) -> Tuple[str, float]:
        """
        Classify text into one of several domains

        Args:
            text: Text to classify
            domain_descriptions: Dict mapping domain names to descriptions

        Returns:
            (domain_name, confidence) tuple

        Example:
            >>> domains = {
            ...     "mechanics": "forces, motion, Newton's laws",
            ...     "thermodynamics": "heat, temperature, entropy",
            ...     "electromagnetism": "electric fields, magnetic fields"
            ... }
            >>> domain, conf = embedder.classify_domain(
            ...     "A force acts on a mass",
            ...     domains
            ... )
            >>> print(f"Domain: {domain} ({conf:.2f})")
        """
        text_emb = self.embed(text)

        best_domain = None
        best_similarity = 0.0

        for domain, description in domain_descriptions.items():
            domain_emb = self.embed(description)

            # Calculate similarity
            sim = np.dot(text_emb, domain_emb) / (
                np.linalg.norm(text_emb) * np.linalg.norm(domain_emb)
            )

            if sim > best_similarity:
                best_similarity = sim
                best_domain = domain

        return (best_domain, float(best_similarity)) if best_domain else ("unknown", 0.0)

    # ========== Property Graph Integration ==========

    def enrich_nodes_with_embeddings(self, nodes: List[Dict]) -> List[Dict]:
        """
        Add SciBERT embeddings to graph nodes

        Args:
            nodes: List of node dicts with 'label' or 'text' fields

        Returns:
            List of nodes with added 'embedding' field

        Example:
            >>> nodes = [
            ...     {'id': 'node1', 'label': 'force'},
            ...     {'id': 'node2', 'label': 'mass'}
            ... ]
            >>> enriched = embedder.enrich_nodes_with_embeddings(nodes)
        """
        for node in nodes:
            text = node.get('label') or node.get('text') or node.get('name', '')
            if text:
                node['embedding'] = self.embed(text).tolist()

        return nodes

    def find_similar_nodes(self,
                          query_node: Dict,
                          candidate_nodes: List[Dict],
                          top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Find nodes similar to a query node based on embeddings

        Args:
            query_node: Node dict with 'embedding' field
            candidate_nodes: List of candidate node dicts with 'embedding'
            top_k: Number of top results

        Returns:
            List of (node, similarity) tuples
        """
        if 'embedding' not in query_node:
            return []

        query_emb = np.array(query_node['embedding'])

        similarities = []
        for node in candidate_nodes:
            if 'embedding' in node:
                node_emb = np.array(node['embedding'])

                sim = np.dot(query_emb, node_emb) / (
                    np.linalg.norm(query_emb) * np.linalg.norm(node_emb)
                )

                similarities.append((node, float(sim)))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    # ========== Utility Methods ==========

    def clear_cache(self) -> None:
        """Clear embedding cache"""
        self._embedding_cache.clear()

    def cache_size(self) -> int:
        """Get number of cached embeddings"""
        return len(self._embedding_cache)

    def is_available(self) -> bool:
        """Check if transformers is available"""
        return TRANSFORMERS_AVAILABLE

    def __repr__(self) -> str:
        """String representation"""
        return f"SciBERTEmbedder(model='{self.model_name}', device='{self.device}', cached={self.cache_size()})"


# ========== Standalone Functions ==========

def check_transformers_availability() -> bool:
    """Check if transformers and torch are available"""
    return TRANSFORMERS_AVAILABLE


def simple_similarity(text1: str, text2: str) -> float:
    """
    Simple similarity check using SciBERT

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score (0-1)

    Example:
        >>> sim = simple_similarity("ionic bond", "covalent bond")
        >>> print(f"Similarity: {sim:.3f}")
    """
    if not TRANSFORMERS_AVAILABLE:
        # Fallback to basic string similarity
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    try:
        embedder = SciBERTEmbedder(verbose=False)
        return embedder.similarity(text1, text2)
    except Exception:
        return 0.0


def find_best_match(query: str, candidates: List[str]) -> Tuple[str, float]:
    """
    Find best matching candidate for query

    Args:
        query: Query text
        candidates: List of candidate texts

    Returns:
        (best_match, similarity_score) tuple

    Example:
        >>> best, score = find_best_match(
        ...     "force from surface",
        ...     ["gravity", "friction", "tension"]
        ... )
        >>> print(f"Best match: {best} ({score:.2f})")
    """
    if not TRANSFORMERS_AVAILABLE or not candidates:
        return ("", 0.0)

    try:
        embedder = SciBERTEmbedder(verbose=False)
        results = embedder.find_most_similar(query, candidates, top_k=1)

        if results:
            return results[0]
        else:
            return ("", 0.0)

    except Exception:
        return ("", 0.0)
