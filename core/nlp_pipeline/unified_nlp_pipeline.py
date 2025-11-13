"""
Unified NLP Pipeline for Multi-Domain Diagram Generation

Orchestrates entity extraction and relationship extraction across multiple domains
"""

import spacy
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import hashlib

from .entity_extractors import (
    PhysicsEntityExtractor,
    ElectronicsEntityExtractor,
    GeometryEntityExtractor,
    ChemistryEntityExtractor,
    BiologyEntityExtractor
)
from .relationship_extractors import (
    SpatialRelationshipExtractor,
    FunctionalRelationshipExtractor,
    QuantitativeRelationshipExtractor
)

# Try to import parent modules
try:
    from ..scene.schema_v1 import PhysicsDomain
    from ..canonical_problem_spec import CanonicalProblemSpec
except:
    # Fallback if imports fail
    class PhysicsDomain:
        UNKNOWN = "unknown"
        PHYSICS = "physics"
        ELECTRONICS = "electronics"
        GEOMETRY = "geometry"
        CHEMISTRY = "chemistry"
        BIOLOGY = "biology"

    CanonicalProblemSpec = dict


class UnifiedNLPPipeline:
    """
    Unified Multi-Domain NLP Pipeline

    Combines multiple NLP models and extractors to provide comprehensive
    entity and relationship extraction for scientific diagram descriptions.

    Features:
    - Multi-domain entity extraction (Physics, Electronics, Geometry, Chemistry, Biology)
    - Multi-method relationship extraction (Spatial, Functional, Quantitative)
    - spaCy + SciBERT + DeepSeek API integration
    - Caching and performance optimization
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        domains: Optional[List[str]] = None,
        enable_scibert: bool = False,
        enable_domain_extractors: bool = True,
        enable_caching: bool = True,
        spacy_model: str = "en_core_web_sm"
    ):
        """
        Initialize Unified NLP Pipeline

        Args:
            api_key: DeepSeek API key for LLM-based extraction
            domains: List of domains to enable (default: all)
            enable_scibert: Whether to use SciBERT for scientific entities
            enable_domain_extractors: Whether to use domain-specific extractors
            enable_caching: Whether to cache processed documents
            spacy_model: spaCy model to use (default: en_core_web_sm)
        """
        self.api_key = api_key
        self.domains = domains or ['all']
        self.enable_scibert = enable_scibert
        self.enable_domain_extractors = enable_domain_extractors
        self.enable_caching = enable_caching

        # Load spaCy model
        print(f"Loading spaCy model: {spacy_model}...")
        self.nlp = spacy.load(spacy_model)

        # Initialize caching
        if enable_caching:
            self.cache_dir = Path("cache/nlp_pipeline")
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize entity extractors
        self.entity_extractors = {}
        if enable_domain_extractors:
            self._initialize_entity_extractors()

        # Initialize relationship extractors
        self._initialize_relationship_extractors()

        # Initialize SciBERT if enabled
        if enable_scibert:
            self._initialize_scibert()

        print(f"✅ Unified NLP Pipeline initialized")
        print(f"   Domains: {', '.join(self.domains)}")
        print(f"   Entity Extractors: {len(self.entity_extractors)}")
        print(f"   Relationship Extractors: {len(self.relationship_extractors)}")

    def _initialize_entity_extractors(self):
        """Initialize domain-specific entity extractors"""
        extractors_map = {
            'physics': PhysicsEntityExtractor,
            'electronics': ElectronicsEntityExtractor,
            'geometry': GeometryEntityExtractor,
            'chemistry': ChemistryEntityExtractor,
            'biology': BiologyEntityExtractor
        }

        for domain in self.domains:
            if domain == 'all':
                # Initialize all extractors
                for name, extractor_class in extractors_map.items():
                    self.entity_extractors[name] = extractor_class(self.nlp)
                break
            elif domain in extractors_map:
                self.entity_extractors[domain] = extractors_map[domain](self.nlp)

    def _initialize_relationship_extractors(self):
        """Initialize relationship extractors"""
        self.relationship_extractors = {
            'spatial': SpatialRelationshipExtractor(self.nlp),
            'functional': FunctionalRelationshipExtractor(self.nlp),
            'quantitative': QuantitativeRelationshipExtractor(self.nlp)
        }

    def _initialize_scibert(self):
        """Initialize SciBERT model"""
        try:
            from transformers import AutoTokenizer, AutoModel
            print("   Loading SciBERT model...")
            self.scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
            self.scibert_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
            print("   ✓ SciBERT loaded")
        except Exception as e:
            print(f"   ⚠️ Could not load SciBERT: {e}")
            self.enable_scibert = False

    def process(
        self,
        text: str,
        bypass_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Process text through unified NLP pipeline

        Args:
            text: Problem description text
            bypass_cache: Skip cache lookup if True

        Returns:
            Dictionary with extracted entities and relationships
        """
        # Check cache
        if self.enable_caching and not bypass_cache:
            cached_result = self._load_from_cache(text)
            if cached_result:
                print("   📦 Loaded from cache")
                return cached_result

        print("   🔄 Processing with Unified NLP Pipeline...")

        # Step 1: spaCy processing
        doc = self.nlp(text)

        # Step 2: Classify domain
        domain = self._classify_domain(doc)

        # Step 3: Extract entities
        entities = self._extract_entities(doc, domain)

        # Step 4: Extract relationships
        relationships = self._extract_relationships(doc, entities, domain)

        # Step 5: Build result
        result = {
            'domain': domain,
            'text': text,
            'entities': entities,
            'relationships': relationships,
            'metadata': {
                'num_entities': len(entities),
                'num_relationships': len(relationships),
                'pipeline': 'unified_nlp',
                'extractors_used': list(self.entity_extractors.keys()),
                'sentence_count': len(list(doc.sents)),
                'token_count': len(doc)
            }
        }

        # Save to cache
        if self.enable_caching:
            self._save_to_cache(text, result)

        return result

    def _classify_domain(self, doc: spacy.tokens.Doc) -> str:
        """
        Classify the problem domain

        Args:
            doc: spaCy Doc object

        Returns:
            Domain string (physics, electronics, etc.)
        """
        text_lower = doc.text.lower()

        # Domain keywords
        domain_keywords = {
            'physics': ['force', 'mass', 'velocity', 'acceleration', 'momentum', 'energy', 'spring', 'incline'],
            'electronics': ['resistor', 'capacitor', 'circuit', 'voltage', 'current', 'battery', 'inductor'],
            'geometry': ['triangle', 'angle', 'point', 'line', 'circle', 'polygon', 'area', 'perimeter'],
            'chemistry': ['molecule', 'reaction', 'bond', 'atom', 'compound', 'element', 'pH', 'ion'],
            'biology': ['cell', 'organ', 'tissue', 'organism', 'protein', 'DNA', 'enzyme', 'membrane']
        }

        # Score each domain
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores, key=scores.get)

        return 'unknown'

    def _extract_entities(self, doc: spacy.tokens.Doc, domain: str) -> List[Dict]:
        """
        Extract entities using all available extractors

        Args:
            doc: spaCy Doc object
            domain: Classified domain

        Returns:
            List of extracted entities
        """
        all_entities = []

        # spaCy base NER
        for ent in doc.ents:
            entity = {
                'id': f'spacy_{ent.start}_{ent.end}',
                'type': ent.label_,
                'label': ent.label_,
                'text': ent.text,
                'properties': {
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.85,
                    'method': 'spacy_ner'
                }
            }
            all_entities.append(entity)

        # Domain-specific extractors
        if self.enable_domain_extractors:
            # Use domain-specific extractor
            if domain in self.entity_extractors:
                extractor = self.entity_extractors[domain]
                domain_entities = extractor.extract(doc)
                all_entities.extend(domain_entities)
            else:
                # Use all extractors
                for extractor in self.entity_extractors.values():
                    domain_entities = extractor.extract(doc)
                    all_entities.extend(domain_entities)

        # SciBERT extraction (if enabled)
        if self.enable_scibert:
            scibert_entities = self._extract_with_scibert(doc.text)
            all_entities.extend(scibert_entities)

        # Deduplicate
        return self._deduplicate_entities(all_entities)

    def _extract_relationships(
        self,
        doc: spacy.tokens.Doc,
        entities: List[Dict],
        domain: str
    ) -> List[Dict]:
        """
        Extract relationships using all relationship extractors

        Args:
            doc: spaCy Doc object
            entities: Extracted entities
            domain: Classified domain

        Returns:
            List of extracted relationships
        """
        all_relationships = []

        # Run all relationship extractors
        for extractor_name, extractor in self.relationship_extractors.items():
            relationships = extractor.extract(doc, entities)
            all_relationships.extend(relationships)

        # Deduplicate
        return self._deduplicate_relationships(all_relationships)

    def _extract_with_scibert(self, text: str) -> List[Dict]:
        """Extract scientific entities using SciBERT"""
        # Placeholder for SciBERT extraction
        # In a full implementation, this would:
        # 1. Tokenize text with SciBERT tokenizer
        # 2. Get embeddings from SciBERT model
        # 3. Use embeddings to identify scientific entities
        # 4. Return list of entities

        return []

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Deduplicate entities based on text span overlap

        Args:
            entities: List of entities

        Returns:
            Deduplicated list of entities
        """
        if not entities:
            return []

        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e['properties']['start'])

        unique = []
        seen_spans = []

        for entity in sorted_entities:
            start = entity['properties']['start']
            end = entity['properties']['end']

            # Check for overlap
            overlap = False
            for seen_start, seen_end in seen_spans:
                if (start < seen_end and end > seen_start):
                    overlap = True
                    break

            if not overlap:
                unique.append(entity)
                seen_spans.append((start, end))

        return unique

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """
        Deduplicate relationships

        Args:
            relationships: List of relationships

        Returns:
            Deduplicated list of relationships
        """
        seen = set()
        unique = []

        for rel in relationships:
            key = (rel['type'], rel.get('subject'), rel.get('target'))
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique

    def _load_from_cache(self, text: str) -> Optional[Dict]:
        """Load result from cache"""
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"   ⚠️ Cache load error: {e}")

        return None

    def _save_to_cache(self, text: str, result: Dict):
        """Save result to cache"""
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            import json
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            print(f"   ⚠️ Cache save error: {e}")

    def to_canonical_spec(self, result: Dict, problem_text: str) -> Any:
        """
        Convert pipeline result to CanonicalProblemSpec

        Args:
            result: Pipeline result dictionary
            problem_text: Original problem text

        Returns:
            CanonicalProblemSpec object
        """
        if CanonicalProblemSpec == dict:
            # Fallback if CanonicalProblemSpec not available
            return result

        return CanonicalProblemSpec(
            domain=result['domain'],
            problem_type="diagram",
            problem_text=problem_text,
            objects=result['entities'],
            relationships=result['relationships'],
            complexity_score=self._calculate_complexity(result),
            environment={},
            physics_context=result['metadata']
        )

    def _calculate_complexity(self, result: Dict) -> float:
        """Calculate problem complexity"""
        num_entities = result['metadata']['num_entities']
        num_relationships = result['metadata']['num_relationships']
        num_sentences = result['metadata']['sentence_count']

        # Simple complexity metric
        complexity = min(1.0, (
            num_entities * 0.05 +
            num_relationships * 0.08 +
            num_sentences * 0.02
        ))

        return complexity
