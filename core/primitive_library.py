"""
Primitive Diagram Library - FULL IMPLEMENTATION
================================================

Roadmap Layer 5: Query primitive library first, fallback to procedural generation.

Vector database-backed library with Milvus/Qdrant support for similarity search.
Includes in-memory fallback for environments without vector DB.

Author: Universal STEM Diagram Generator
Date: November 12, 2025
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path


class PrimitiveCategory(Enum):
    """Diagram primitive categories"""
    ELECTRONICS = "electronics"
    MECHANICS = "mechanics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    GEOMETRY = "geometry"
    MATH = "math"
    COMPUTER_SCIENCE = "computer_science"


@dataclass
class DiagramPrimitive:
    """Reusable diagram component"""
    id: str
    name: str
    category: PrimitiveCategory
    svg_content: str
    tags: List[str]
    similarity_score: float = 0.0  # Populated by search
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value if isinstance(self.category, PrimitiveCategory) else self.category,
            'svg_content': self.svg_content,
            'tags': self.tags,
            'similarity_score': self.similarity_score,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiagramPrimitive':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            category=PrimitiveCategory(data['category']),
            svg_content=data['svg_content'],
            tags=data.get('tags', []),
            similarity_score=data.get('similarity_score', 0.0),
            metadata=data.get('metadata', {})
        )


class PrimitiveLibrary:
    """
    Vector database-backed primitive library with multiple backend support

    Backends:
    - milvus: Milvus vector database (best for production)
    - qdrant: Qdrant vector database (alternative)
    - memory: In-memory fallback (for testing/development)
    - stub: Stub implementation (returns empty)
    """

    def __init__(self,
                 backend: str = "memory",
                 host: str = "localhost",
                 port: int = 19530,
                 collection_name: str = "primitives"):
        """
        Initialize primitive library

        Args:
            backend: Backend type ('milvus', 'qdrant', 'memory', 'stub')
            host: Vector DB host (for milvus/qdrant)
            port: Vector DB port
            collection_name: Collection/index name
        """
        self.backend = backend
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)

        # Backend-specific clients
        self.milvus_collection = None
        self.qdrant_client = None
        self.memory_store: List[Tuple[DiagramPrimitive, List[float]]] = []
        self.embedder = None

        # Initialize backend
        if backend == "milvus":
            self._init_milvus()
        elif backend == "qdrant":
            self._init_qdrant()
        elif backend == "memory":
            self._init_memory()
        elif backend == "stub":
            self.logger.info("Primitive library initialized in STUB mode")
        else:
            raise ValueError(f"Unknown backend: {backend}")

        self.logger.info(f"PrimitiveLibrary initialized with backend: {backend}")

    def _init_milvus(self):
        """Initialize Milvus connection"""
        try:
            from pymilvus import connections, Collection, utility

            connections.connect(host=self.host, port=str(self.port))

            # Check if collection exists
            if utility.has_collection(self.collection_name):
                self.milvus_collection = Collection(self.collection_name)
                self.logger.info(f"Connected to existing Milvus collection: {self.collection_name}")
            else:
                self.logger.warning(f"Milvus collection '{self.collection_name}' not found")
                self.logger.info("Falling back to memory backend")
                self.backend = "memory"
                self._init_memory()

        except ImportError:
            self.logger.warning("pymilvus not installed. Install with: pip install pymilvus")
            self.logger.info("Falling back to memory backend")
            self.backend = "memory"
            self._init_memory()
        except Exception as e:
            self.logger.warning(f"Failed to connect to Milvus: {e}")
            self.logger.info("Falling back to memory backend")
            self.backend = "memory"
            self._init_memory()

    def _init_qdrant(self):
        """Initialize Qdrant connection"""
        try:
            from qdrant_client import QdrantClient

            self.qdrant_client = QdrantClient(host=self.host, port=self.port)

            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                self.logger.info(f"Connected to existing Qdrant collection: {self.collection_name}")
            else:
                self.logger.warning(f"Qdrant collection '{self.collection_name}' not found")
                self.logger.info("Falling back to memory backend")
                self.backend = "memory"
                self._init_memory()

        except ImportError:
            self.logger.warning("qdrant-client not installed. Install with: pip install qdrant-client")
            self.logger.info("Falling back to memory backend")
            self.backend = "memory"
            self._init_memory()
        except Exception as e:
            self.logger.warning(f"Failed to connect to Qdrant: {e}")
            self.logger.info("Falling back to memory backend")
            self.backend = "memory"
            self._init_memory()

    def _init_memory(self):
        """Initialize in-memory backend with built-in primitives"""
        self.logger.info("Initializing in-memory primitive store with built-in components")

        # Load built-in primitives
        built_in = self._get_built_in_primitives()

        # Initialize embedder for similarity search
        try:
            self.embedder = self._get_embedder()
        except Exception as e:
            self.logger.warning(f"Failed to initialize embedder: {e}")
            self.embedder = None

        # Store primitives with embeddings
        for primitive in built_in:
            if self.embedder:
                # Generate embedding from name + tags
                text = f"{primitive.name} {' '.join(primitive.tags)}"
                embedding = self._embed_text(text)
                self.memory_store.append((primitive, embedding))
            else:
                # Store without embeddings (will use keyword matching)
                self.memory_store.append((primitive, []))

        self.logger.info(f"Loaded {len(self.memory_store)} built-in primitives")

    def _get_embedder(self):
        """Get text embedder (sentence-transformers)"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight model
            return model
        except ImportError:
            self.logger.warning("sentence-transformers not installed")
            return None

    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.embedder:
            embedding = self.embedder.encode(text)
            return embedding.tolist()
        else:
            return []

    def _get_built_in_primitives(self) -> List[DiagramPrimitive]:
        """Get built-in primitive library"""
        primitives = []

        # Electronics primitives
        primitives.extend([
            DiagramPrimitive(
                id="battery_symbol",
                name="Battery",
                category=PrimitiveCategory.ELECTRONICS,
                svg_content='<g><line x1="0" y1="0" x2="0" y2="20" stroke="black" stroke-width="2"/><line x1="-10" y1="20" x2="10" y2="20" stroke="black" stroke-width="3"/><line x1="-5" y1="30" x2="5" y2="30" stroke="black" stroke-width="1"/></g>',
                tags=['battery', 'power', 'voltage', 'source', 'dc', 'cell']
            ),
            DiagramPrimitive(
                id="resistor_zigzag",
                name="Resistor",
                category=PrimitiveCategory.ELECTRONICS,
                svg_content='<path d="M 0 0 L 10 0 L 15 -10 L 25 10 L 35 -10 L 45 10 L 55 -10 L 65 10 L 70 0 L 80 0" stroke="black" stroke-width="2" fill="none"/>',
                tags=['resistor', 'resistance', 'ohm', 'component', 'passive']
            ),
            DiagramPrimitive(
                id="capacitor_parallel",
                name="Capacitor",
                category=PrimitiveCategory.ELECTRONICS,
                svg_content='<g><line x1="0" y1="0" x2="30" y2="0" stroke="black" stroke-width="2"/><line x1="30" y1="-15" x2="30" y2="15" stroke="black" stroke-width="3"/><line x1="35" y1="-15" x2="35" y2="15" stroke="black" stroke-width="3"/><line x1="35" y1="0" x2="65" y2="0" stroke="black" stroke-width="2"/></g>',
                tags=['capacitor', 'capacitance', 'farad', 'component', 'passive', 'storage']
            ),
            DiagramPrimitive(
                id="switch_spst",
                name="Switch",
                category=PrimitiveCategory.ELECTRONICS,
                svg_content='<g><circle cx="0" cy="0" r="3" fill="black"/><line x1="3" y1="0" x2="40" y2="-15" stroke="black" stroke-width="2"/><circle cx="45" cy="0" r="3" fill="black"/></g>',
                tags=['switch', 'spst', 'control', 'open', 'close', 'toggle']
            ),
            DiagramPrimitive(
                id="led",
                name="LED",
                category=PrimitiveCategory.ELECTRONICS,
                svg_content='<g><path d="M 0 0 L 30 15 L 30 -15 Z" stroke="black" stroke-width="2" fill="none"/><line x1="30" y1="15" x2="30" y2="-15" stroke="black" stroke-width="2"/></g>',
                tags=['led', 'diode', 'light', 'indicator', 'semiconductor']
            ),
        ])

        # Mechanics primitives
        primitives.extend([
            DiagramPrimitive(
                id="mass_block",
                name="Mass/Block",
                category=PrimitiveCategory.MECHANICS,
                svg_content='<rect x="0" y="0" width="60" height="40" stroke="black" stroke-width="2" fill="lightgray"/>',
                tags=['mass', 'block', 'object', 'body', 'weight', 'kg']
            ),
            DiagramPrimitive(
                id="spring_coil",
                name="Spring",
                category=PrimitiveCategory.MECHANICS,
                svg_content='<path d="M 0 0 Q 10 -10 20 0 Q 30 10 40 0 Q 50 -10 60 0 Q 70 10 80 0" stroke="black" stroke-width="2" fill="none"/>',
                tags=['spring', 'elastic', 'coil', 'hooke', 'compression', 'extension']
            ),
            DiagramPrimitive(
                id="pulley_wheel",
                name="Pulley",
                category=PrimitiveCategory.MECHANICS,
                svg_content='<g><circle cx="30" cy="30" r="25" stroke="black" stroke-width="2" fill="white"/><circle cx="30" cy="30" r="5" stroke="black" stroke-width="2" fill="black"/></g>',
                tags=['pulley', 'wheel', 'rope', 'mechanical', 'advantage']
            ),
            DiagramPrimitive(
                id="force_arrow",
                name="Force Arrow",
                category=PrimitiveCategory.MECHANICS,
                svg_content='<g><line x1="0" y1="0" x2="80" y2="0" stroke="red" stroke-width="3"/><polygon points="80,0 70,-8 70,8" fill="red"/></g>',
                tags=['force', 'arrow', 'vector', 'newton', 'push', 'pull']
            ),
        ])

        # Chemistry primitives
        primitives.extend([
            DiagramPrimitive(
                id="atom_circle",
                name="Atom",
                category=PrimitiveCategory.CHEMISTRY,
                svg_content='<circle cx="20" cy="20" r="15" stroke="black" stroke-width="2" fill="lightblue"/>',
                tags=['atom', 'element', 'particle', 'nucleus', 'electron']
            ),
            DiagramPrimitive(
                id="bond_single",
                name="Single Bond",
                category=PrimitiveCategory.CHEMISTRY,
                svg_content='<line x1="0" y1="0" x2="50" y2="0" stroke="black" stroke-width="2"/>',
                tags=['bond', 'single', 'covalent', 'connection', 'chemical']
            ),
            DiagramPrimitive(
                id="bond_double",
                name="Double Bond",
                category=PrimitiveCategory.CHEMISTRY,
                svg_content='<g><line x1="0" y1="-3" x2="50" y2="-3" stroke="black" stroke-width="2"/><line x1="0" y1="3" x2="50" y2="3" stroke="black" stroke-width="2"/></g>',
                tags=['bond', 'double', 'covalent', 'connection', 'chemical']
            ),
        ])

        # Geometry primitives
        primitives.extend([
            DiagramPrimitive(
                id="triangle",
                name="Triangle",
                category=PrimitiveCategory.GEOMETRY,
                svg_content='<polygon points="30,10 10,50 50,50" stroke="black" stroke-width="2" fill="none"/>',
                tags=['triangle', 'shape', 'polygon', 'three', 'sides']
            ),
            DiagramPrimitive(
                id="circle_shape",
                name="Circle",
                category=PrimitiveCategory.GEOMETRY,
                svg_content='<circle cx="30" cy="30" r="25" stroke="black" stroke-width="2" fill="none"/>',
                tags=['circle', 'shape', 'round', 'radius', 'circumference']
            ),
            DiagramPrimitive(
                id="rectangle_shape",
                name="Rectangle",
                category=PrimitiveCategory.GEOMETRY,
                svg_content='<rect x="10" y="10" width="60" height="40" stroke="black" stroke-width="2" fill="none"/>',
                tags=['rectangle', 'shape', 'polygon', 'four', 'sides', 'quad']
            ),
        ])

        # Biology primitives
        primitives.extend([
            DiagramPrimitive(
                id="dna_double_helix",
                name="DNA Helix",
                category=PrimitiveCategory.BIOLOGY,
                svg_content='<g stroke="#7f8c8d" stroke-width="2" fill="none"><path d="M10,10 C40,40 40,80 10,110"/><path d="M60,10 C30,40 30,80 60,110"/><line x1="20" y1="30" x2="50" y2="30"/><line x1="20" y1="60" x2="50" y2="60"/><line x1="20" y1="90" x2="50" y2="90"/></g>',
                tags=['dna', 'helix', 'biology', 'genetics', 'molecule'],
                metadata={'tikz': '\\draw[thick] plot[smooth] coordinates {(0,0) (1,1) (1,2) (0,3)};'}
            ),
            DiagramPrimitive(
                id="cell_membrane",
                name="Cell Membrane",
                category=PrimitiveCategory.BIOLOGY,
                svg_content='<ellipse cx="40" cy="40" rx="38" ry="28" stroke="#16a085" stroke-width="3" fill="rgba(22,160,133,0.1)"/>',
                tags=['cell', 'biology', 'membrane', 'organelle'],
                metadata={'tikz': '\\draw[rounded corners=40pt] (-2,0) rectangle (2,3);'}
            ),
        ])

        # Computer Science primitives
        primitives.extend([
            DiagramPrimitive(
                id="database_cylinder",
                name="Database Cylinder",
                category=PrimitiveCategory.COMPUTER_SCIENCE,
                svg_content='<g><ellipse cx="40" cy="10" rx="30" ry="10" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/><rect x="10" y="10" width="60" height="40" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/><ellipse cx="40" cy="50" rx="30" ry="10" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/></g>',
                tags=['database', 'storage', 'table', 'sql', 'data'],
                metadata={'tikz': '\\node[database] (db) {DB};'}
            ),
            DiagramPrimitive(
                id="server_rack",
                name="Server Rack",
                category=PrimitiveCategory.COMPUTER_SCIENCE,
                svg_content='<g><rect x="10" y="5" width="60" height="90" fill="#bdc3c7" stroke="#34495e" stroke-width="2"/><rect x="15" y="15" width="50" height="15" fill="#2ecc71"/><rect x="15" y="40" width="50" height="15" fill="#3498db"/><rect x="15" y="65" width="50" height="15" fill="#e67e22"/></g>',
                tags=['server', 'rack', 'compute', 'node', 'network'],
            ),
            DiagramPrimitive(
                id="cloud_icon",
                name="Cloud",
                category=PrimitiveCategory.COMPUTER_SCIENCE,
                svg_content='<path d="M20 40 Q 20 20 40 20 Q 50 0 70 20 Q 90 20 90 40 Q 110 40 110 60 Q 110 80 90 80 L20 80 Q 0 80 0 60 Q 0 40 20 40" fill="#ecf0f1" stroke="#95a5a6" stroke-width="2"/>',
                tags=['cloud', 'network', 'internet', 'service'],
            ),
        ])

        return primitives

    def query(self,
             text: str,
             top_k: int = 5,
             category: Optional[PrimitiveCategory] = None,
             min_score: float = 0.0) -> List[DiagramPrimitive]:
        """
        Query primitive library for similar components

        Args:
            text: Query text (e.g., "battery", "resistor", "spring")
            top_k: Number of results to return
            category: Optional category filter
            min_score: Minimum similarity score threshold

        Returns:
            List of matching primitives sorted by similarity score
        """
        if self.backend == "stub":
            self.logger.warning("Primitive library is stub - no primitives available")
            return []

        if self.backend == "milvus":
            return self._query_milvus(text, top_k, category, min_score)
        elif self.backend == "qdrant":
            return self._query_qdrant(text, top_k, category, min_score)
        elif self.backend == "memory":
            return self._query_memory(text, top_k, category, min_score)
        else:
            return []

    def _query_memory(self,
                     text: str,
                     top_k: int,
                     category: Optional[PrimitiveCategory],
                     min_score: float) -> List[DiagramPrimitive]:
        """Query in-memory store"""
        if not self.memory_store:
            return []

        results = []
        text_lower = text.lower()

        if self.embedder:
            # Semantic search with embeddings
            query_embedding = self._embed_text(text)

            for primitive, embedding in self.memory_store:
                # Filter by category if specified
                if category and primitive.category != category:
                    continue

                # Calculate cosine similarity
                score = self._cosine_similarity(query_embedding, embedding)

                if score >= min_score:
                    prim_copy = DiagramPrimitive(
                        id=primitive.id,
                        name=primitive.name,
                        category=primitive.category,
                        svg_content=primitive.svg_content,
                        tags=primitive.tags,
                        similarity_score=score,
                        metadata=primitive.metadata
                    )
                    results.append(prim_copy)

        else:
            # Keyword matching fallback
            for primitive, _ in self.memory_store:
                # Filter by category
                if category and primitive.category != category:
                    continue

                # Simple keyword matching
                name_match = text_lower in primitive.name.lower()
                tags_match = any(text_lower in tag.lower() for tag in primitive.tags)

                if name_match or tags_match:
                    # Assign score based on match quality
                    score = 1.0 if name_match else 0.7
                    prim_copy = DiagramPrimitive(
                        id=primitive.id,
                        name=primitive.name,
                        category=primitive.category,
                        svg_content=primitive.svg_content,
                        tags=primitive.tags,
                        similarity_score=score,
                        metadata=primitive.metadata
                    )
                    results.append(prim_copy)

        # Sort by similarity score (descending) and take top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _query_milvus(self,
                     text: str,
                     top_k: int,
                     category: Optional[PrimitiveCategory],
                     min_score: float) -> List[DiagramPrimitive]:
        """Query Milvus vector database"""
        if not self.milvus_collection:
            return []

        try:
            # Generate query embedding
            query_embedding = self._embed_text(text)

            # Build filter expression
            filter_expr = None
            if category:
                filter_expr = f"category == '{category.value}'"

            # Search
            search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

            results = self.milvus_collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=filter_expr
            )

            # Convert to DiagramPrimitive objects
            primitives = []
            for hit in results[0]:
                if hit.score >= min_score:
                    primitive = DiagramPrimitive(
                        id=hit.entity.get('id'),
                        name=hit.entity.get('name'),
                        category=PrimitiveCategory(hit.entity.get('category')),
                        svg_content=hit.entity.get('svg_content'),
                        tags=hit.entity.get('tags', []),
                        similarity_score=hit.score,
                        metadata=hit.entity.get('metadata', {})
                    )
                    primitives.append(primitive)

            return primitives

        except Exception as e:
            self.logger.error(f"Milvus query failed: {e}")
            return []

    def _query_qdrant(self,
                     text: str,
                     top_k: int,
                     category: Optional[PrimitiveCategory],
                     min_score: float) -> List[DiagramPrimitive]:
        """Query Qdrant vector database"""
        if not self.qdrant_client:
            return []

        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Generate query embedding
            query_embedding = self._embed_text(text)

            # Build filter
            query_filter = None
            if category:
                query_filter = Filter(
                    must=[FieldCondition(key="category", match=MatchValue(value=category.value))]
                )

            # Search
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter,
                score_threshold=min_score
            )

            # Convert to DiagramPrimitive objects
            primitives = []
            for point in search_result:
                payload = point.payload
                primitive = DiagramPrimitive(
                    id=payload.get('id'),
                    name=payload.get('name'),
                    category=PrimitiveCategory(payload.get('category')),
                    svg_content=payload.get('svg_content'),
                    tags=payload.get('tags', []),
                    similarity_score=point.score,
                    metadata=payload.get('metadata', {})
                )
                primitives.append(primitive)

            return primitives

        except Exception as e:
            self.logger.error(f"Qdrant query failed: {e}")
            return []

    def add(self, primitive: DiagramPrimitive):
        """Add primitive to library"""
        if self.backend == "memory":
            if self.embedder:
                text = f"{primitive.name} {' '.join(primitive.tags)}"
                embedding = self._embed_text(text)
                self.memory_store.append((primitive, embedding))
            else:
                self.memory_store.append((primitive, []))
            self.logger.info(f"Added primitive to memory store: {primitive.name}")
        else:
            self.logger.warning(f"add() not implemented for backend: {self.backend}")

    def ingest_reference_diagram(
        self,
        image_path: str,
        *,
        category_hint: Optional[PrimitiveCategory] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        extractor: Optional['PrimitiveExtractor'] = None
    ) -> Dict[str, Any]:
        """
        Ingest a reference diagram by running the multimodal primitive extractor
        and auto-populating the library with the resulting components.
        """
        from core.primitive_ingestion import PrimitiveExtractor

        extractor = extractor or PrimitiveExtractor()
        hint_value = (category_hint.value if isinstance(category_hint, PrimitiveCategory) else None)
        extraction_results = extractor.extract_from_image(
            image_path,
            category_hint=hint_value,
            extra_tags=tags,
            extra_metadata=metadata,
        )

        ingested = 0
        detections: List[Dict[str, Any]] = []
        for result in extraction_results:
            category_enum = self._resolve_category(result.category or hint_value)
            primitive = DiagramPrimitive(
                id=result.primitive_id,
                name=result.name,
                category=category_enum,
                svg_content=result.svg_content,
                tags=result.tags,
                metadata=result.metadata,
            )
            self.add(primitive)
            ingested += 1
            detections.append({
                'primitive_id': result.primitive_id,
                'label': result.metadata.get('label'),
                'confidence': result.confidence,
                'bbox': result.bbox,
            })

        return {
            'ingested': ingested,
            'source_image': str(image_path),
            'detections': detections,
            'warnings': extractor.warnings,
        }

    def _resolve_category(self, category: Optional[str]) -> PrimitiveCategory:
        if not category:
            return PrimitiveCategory.GEOMETRY
        category_lower = category.lower()
        for member in PrimitiveCategory:
            if member.value == category_lower or member.name.lower() == category_lower:
                return member
        return PrimitiveCategory.GEOMETRY

    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        if self.backend == "memory":
            category_counts = {}
            for primitive, _ in self.memory_store:
                cat = primitive.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1

            return {
                'backend': self.backend,
                'total_primitives': len(self.memory_store),
                'categories': category_counts,
                'has_embedder': self.embedder is not None
            }
        else:
            return {
                'backend': self.backend,
                'total_primitives': 'unknown',
                'categories': {}
            }
