"""
SpaCy-based AI Analyzer with LLM Integration
Uses spaCy + spaCy-LLM for robust entity and relationship extraction
"""

import spacy
from spacy.tokens import Doc, Span
from spacy.language import Language
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Try to import quantulum3 for unit extraction
try:
    from quantulum3 import parser as quantity_parser
    HAS_QUANTULUM = True
except ImportError:
    HAS_QUANTULUM = False
    print("⚠️  quantulum3 not available - unit extraction will be limited")

from .scene.schema_v1 import PhysicsDomain
from .canonical_problem_spec import CanonicalProblemSpec
from .exceptions import IncompleteSpecsError


class SpaCyAIAnalyzer:
    """
    Enhanced AI Analyzer using spaCy + spaCy-LLM pipeline

    Features:
    - Linguistic preprocessing (tokenization, POS tagging, dependency parsing)
    - Custom entity recognition for physics terms
    - LLM-augmented entity and relationship extraction
    - Automatic unit parsing with quantulum3
    - Doc serialization and caching
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        config_path: Optional[str] = None,
        enable_caching: bool = True
    ):
        """
        Initialize SpaCy-based analyzer

        Args:
            api_key: DeepSeek API key
            model: LLM model name (default: deepseek-chat)
            config_path: Path to custom spaCy pipeline config
            enable_caching: Enable Doc serialization caching
        """
        self.api_key = api_key
        self.model_name = model
        self.enable_caching = enable_caching
        self.cache_dir = Path("cache/spacy_docs")

        if enable_caching:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load spaCy pipeline
        try:
            # Try to load custom physics pipeline if exists
            if config_path and Path(config_path).exists():
                print(f"Loading custom pipeline from {config_path}")
                self.nlp = spacy.load(config_path)
            else:
                # Fallback to base model + custom components
                print("Loading base en_core_web_sm model")
                self.nlp = spacy.load("en_core_web_sm")
                self._add_custom_components()

        except Exception as e:
            print(f"⚠️  Error loading spaCy pipeline: {e}")
            print("Falling back to base model")
            self.nlp = spacy.load("en_core_web_sm")
            self._add_custom_components()

        # Configure API key for LLM components
        self._configure_llm_api_key()

        print(f"✅ SpaCyAIAnalyzer initialized")
        print(f"   Pipeline: {self.nlp.pipe_names}")
        print(f"   Caching: {'enabled' if enable_caching else 'disabled'}")

    def _add_custom_components(self):
        """Add custom pipeline components for physics NLP"""
        # Add entity ruler for physics terms
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")

            # Load patterns from file if exists
            patterns_file = Path(__file__).parent / "physics_entity_patterns.jsonl"
            if patterns_file.exists():
                ruler.from_disk(patterns_file)
                print(f"   Loaded entity patterns from {patterns_file}")
            else:
                # Add some basic patterns
                patterns = [
                    {"label": "PHYSICS_OBJECT", "pattern": "capacitor"},
                    {"label": "PHYSICS_OBJECT", "pattern": "resistor"},
                    {"label": "PHYSICS_OBJECT", "pattern": "lens"},
                    {"label": "PHYSICS_OBJECT", "pattern": "mirror"},
                    {"label": "MATERIAL", "pattern": "dielectric"},
                    {"label": "CONSTRAINT", "pattern": "parallel"},
                    {"label": "CONSTRAINT", "pattern": "series"},
                ]
                ruler.add_patterns(patterns)

        # Add custom extensions for storing extracted data
        if not Doc.has_extension("physics_objects"):
            Doc.set_extension("physics_objects", default=[])
        if not Doc.has_extension("physics_relationships"):
            Doc.set_extension("physics_relationships", default=[])
        if not Doc.has_extension("domain"):
            Doc.set_extension("domain", default=None)
        if not Doc.has_extension("measurements"):
            Doc.set_extension("measurements", default=[])

    def _configure_llm_api_key(self):
        """Configure API key for LLM components in pipeline"""
        # Set environment variable for spacy-llm
        os.environ["OPENAI_API_KEY"] = self.api_key
        os.environ["DEEPSEEK_API_KEY"] = self.api_key

        # Try to configure LLM components directly
        for pipe_name in self.nlp.pipe_names:
            if "llm" in pipe_name:
                try:
                    component = self.nlp.get_pipe(pipe_name)
                    if hasattr(component, "model") and hasattr(component.model, "config"):
                        component.model.config["api_key"] = self.api_key
                except Exception as e:
                    print(f"   Could not configure {pipe_name}: {e}")

    def analyze(
        self,
        problem_text: str,
        bypass_cache: bool = False
    ) -> CanonicalProblemSpec:
        """
        Main analysis method using spaCy-LLM pipeline

        Args:
            problem_text: Physics problem text
            bypass_cache: If True, skip cache lookup

        Returns:
            CanonicalProblemSpec with extracted entities and relationships
        """
        # Check cache first
        if self.enable_caching and not bypass_cache:
            cached_doc = self._load_from_cache(problem_text)
            if cached_doc is not None:
                print("   📦 Loaded from cache")
                return self._build_spec_from_doc(cached_doc, problem_text)

        # Process with spaCy pipeline
        print("   🔄 Processing with spaCy pipeline...")
        doc = self.nlp(problem_text)

        # Extract domain
        domain = self._classify_domain(doc)
        doc._.domain = domain

        # Extract entities
        entities = self._extract_entities(doc)
        doc._.physics_objects = entities

        # Extract measurements with quantulum3
        if HAS_QUANTULUM:
            measurements = self._extract_measurements(problem_text)
            doc._.measurements = measurements

        # Extract relationships
        relationships = self._extract_relationships(doc)
        doc._.physics_relationships = relationships

        # Save to cache
        if self.enable_caching:
            self._save_to_cache(problem_text, doc)

        # Build canonical spec
        return self._build_spec_from_doc(doc, problem_text)

    def _classify_domain(self, doc: Doc) -> PhysicsDomain:
        """
        Classify physics domain using keyword matching

        Args:
            doc: spaCy Doc object

        Returns:
            PhysicsDomain enum
        """
        text_lower = doc.text.lower()

        keywords = {
            PhysicsDomain.ELECTROSTATICS: ['charge', 'electric field', 'coulomb', 'gauss', 'potential', 'capacitor'],
            PhysicsDomain.CURRENT_ELECTRICITY: ['circuit', 'resistor', 'battery', 'current', 'voltage', 'ohm'],
            PhysicsDomain.MECHANICS: ['mass', 'force', 'friction', 'acceleration', 'velocity', 'incline'],
            PhysicsDomain.OPTICS: ['lens', 'mirror', 'refraction', 'reflection', 'ray', 'image', 'focal'],
            PhysicsDomain.THERMODYNAMICS: ['temperature', 'heat', 'entropy', 'gas', 'isothermal'],
        }

        scores = {}
        for domain, kw_list in keywords.items():
            score = sum(1 for kw in kw_list if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores, key=scores.get)
        return PhysicsDomain.UNKNOWN

    def _extract_entities(self, doc: Doc) -> List[Dict]:
        """
        Extract physics entities from spaCy Doc

        Args:
            doc: spaCy Doc object

        Returns:
            List of entity dictionaries
        """
        entities = []
        seen_texts = set()  # Avoid duplicates

        for ent in doc.ents:
            # Skip duplicates
            if ent.text.lower() in seen_texts:
                continue
            seen_texts.add(ent.text.lower())

            entity = {
                "id": self._generate_id(ent.text),
                "type": self._map_entity_type(ent.label_),
                "text": ent.text,
                "properties": {
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_,
                    "confidence": 0.85  # Default confidence
                }
            }

            # Extract numerical values for measurements
            if ent.label_ in ["MEASUREMENT", "QUANTITY", "CARDINAL"]:
                measurement = self._parse_measurement_entity(ent)
                if measurement:
                    entity["properties"].update(measurement)

            entities.append(entity)

        return entities

    def _extract_measurements(self, text: str) -> List[Dict]:
        """
        Extract measurements using quantulum3

        Args:
            text: Problem text

        Returns:
            List of measurement dictionaries
        """
        if not HAS_QUANTULUM:
            return []

        measurements = []
        try:
            quantities = quantity_parser.parse(text)

            for q in quantities:
                measurement = {
                    "value": q.value,
                    "unit": str(q.unit),
                    "surface": q.surface,
                    "uncertainty": q.uncertainty if hasattr(q, 'uncertainty') else None,
                    "dimension": str(q.unit.entity) if hasattr(q.unit, 'entity') else None
                }
                measurements.append(measurement)
        except Exception as e:
            print(f"   ⚠️ quantulum3 parsing error: {e}")

        return measurements

    def _parse_measurement_entity(self, ent: Span) -> Optional[Dict]:
        """Parse measurement from entity text"""
        # Try to extract number and unit
        # Examples: "10.5 cm²", "7.12 mm", "21.0"
        pattern = r'([-+]?[\d,]+\.?\d*)\s*([a-zA-Zμ²³°]+)?'
        match = re.search(pattern, ent.text)

        if match:
            value_str = match.group(1).replace(',', '')
            unit = match.group(2) if match.group(2) else ""

            try:
                value = float(value_str)
                return {
                    "value": value,
                    "unit": unit,
                    "surface": ent.text
                }
            except ValueError:
                pass

        return None

    def _extract_relationships(self, doc: Doc) -> List[Dict]:
        """
        Extract relationships from dependency parse and entities

        Args:
            doc: spaCy Doc object

        Returns:
            List of relationship dictionaries
        """
        relationships = []

        # Method 1: Dependency-based extraction
        dep_rels = self._extract_dependency_relationships(doc)
        relationships.extend(dep_rels)

        # Method 2: Pattern-based extraction
        pattern_rels = self._extract_pattern_relationships(doc)
        relationships.extend(pattern_rels)

        # Method 3: Entity co-occurrence in same sentence
        cooccur_rels = self._extract_cooccurrence_relationships(doc)
        relationships.extend(cooccur_rels)

        return relationships

    def _extract_dependency_relationships(self, doc: Doc) -> List[Dict]:
        """Extract relationships from dependency parse"""
        relationships = []

        for token in doc:
            # Pattern: "capacitor connected to resistor"
            if token.dep_ == "prep" and token.head.pos_ in ["NOUN", "PROPN"]:
                # Look for objects of preposition
                for child in token.children:
                    if child.dep_ == "pobj":
                        rel = {
                            "type": "connected_to",
                            "subject": token.head.text,
                            "target": child.text,
                            "properties": {
                                "preposition": token.text,
                                "confidence": 0.7,
                                "method": "dependency_parse"
                            }
                        }
                        relationships.append(rel)

            # Pattern: "plates separated by distance"
            if token.dep_ == "agent" and "by" in token.text.lower():
                rel = {
                    "type": "separated_by",
                    "subject": token.head.text,
                    "target": " ".join([t.text for t in token.subtree]),
                    "properties": {
                        "confidence": 0.75,
                        "method": "dependency_parse"
                    }
                }
                relationships.append(rel)

        return relationships

    def _extract_pattern_relationships(self, doc: Doc) -> List[Dict]:
        """Extract relationships using regex patterns"""
        relationships = []

        # Pattern: "X in parallel with Y"
        parallel_pattern = r'(\w+)\s+in\s+parallel\s+with\s+(\w+)'
        for match in re.finditer(parallel_pattern, doc.text):
            rel = {
                "type": "parallel_with",
                "subject": match.group(1),
                "target": match.group(2),
                "properties": {
                    "confidence": 0.9,
                    "method": "pattern_match"
                }
            }
            relationships.append(rel)

        # Pattern: "X in series with Y"
        series_pattern = r'(\w+)\s+in\s+series\s+with\s+(\w+)'
        for match in re.finditer(series_pattern, doc.text):
            rel = {
                "type": "series_with",
                "subject": match.group(1),
                "target": match.group(2),
                "properties": {
                    "confidence": 0.9,
                    "method": "pattern_match"
                }
            }
            relationships.append(rel)

        return relationships

    def _extract_cooccurrence_relationships(self, doc: Doc) -> List[Dict]:
        """Extract relationships from entity co-occurrence"""
        relationships = []

        # Group entities by sentence
        for sent in doc.sents:
            sent_entities = [ent for ent in doc.ents if ent.start >= sent.start and ent.end <= sent.end]

            # If multiple physics objects in same sentence, assume relationship
            physics_objs = [ent for ent in sent_entities if ent.label_ in ["PHYSICS_OBJECT", "MATERIAL"]]

            if len(physics_objs) >= 2:
                for i in range(len(physics_objs) - 1):
                    rel = {
                        "type": "related_to",
                        "subject": physics_objs[i].text,
                        "target": physics_objs[i + 1].text,
                        "properties": {
                            "confidence": 0.6,
                            "method": "cooccurrence",
                            "sentence": sent.text
                        }
                    }
                    relationships.append(rel)

        return relationships

    def _build_spec_from_doc(self, doc: Doc, problem_text: str) -> CanonicalProblemSpec:
        """
        Build CanonicalProblemSpec from processed spaCy Doc

        Args:
            doc: Processed spaCy Doc
            problem_text: Original problem text

        Returns:
            CanonicalProblemSpec
        """
        # Get extracted data
        domain = doc._.domain or PhysicsDomain.UNKNOWN
        entities = doc._.physics_objects
        relationships = doc._.physics_relationships
        measurements = doc._.measurements if hasattr(doc._, 'measurements') else []

        # Merge measurements into entities
        for meas in measurements:
            entity = {
                "id": f"measurement_{len(entities)}",
                "type": "measurement",
                "properties": meas
            }
            entities.append(entity)

        # Build spec
        spec = CanonicalProblemSpec(
            domain=domain,
            problem_type="unknown",
            problem_text=problem_text,
            objects=entities,
            relationships=relationships,
            complexity_score=self._calculate_complexity(doc),
            environment={},
            physics_context={
                "processing_method": "spacy_llm",
                "pipeline": self.nlp.pipe_names,
                "entity_count": len(doc.ents),
                "token_count": len(doc)
            }
        )

        return spec

    def _calculate_complexity(self, doc: Doc) -> float:
        """Calculate problem complexity based on linguistic features"""
        # Base complexity on:
        # - Number of entities
        # - Number of sentences
        # - Average sentence length
        # - Number of numerical values

        num_entities = len(doc.ents)
        num_sents = len(list(doc.sents))
        avg_sent_len = len(doc) / max(num_sents, 1)
        num_numbers = len([token for token in doc if token.like_num])

        # Normalize to 0-1 scale
        complexity = min(1.0, (
            num_entities * 0.02 +
            num_sents * 0.05 +
            avg_sent_len * 0.01 +
            num_numbers * 0.03
        ))

        return complexity

    def _generate_id(self, text: str) -> str:
        """Generate ID from text"""
        # Clean and normalize
        clean = re.sub(r'[^\w\s]', '', text.lower())
        return '_'.join(clean.split())

    def _map_entity_type(self, label: str) -> str:
        """Map spaCy entity label to our type system"""
        mapping = {
            "PHYSICS_OBJECT": "physics_object",
            "MEASUREMENT": "measurement",
            "QUANTITY": "measurement",
            "CARDINAL": "number",
            "CONSTRAINT": "constraint",
            "MATERIAL": "material",
            "PHYSICAL_CONSTANT": "constant"
        }
        return mapping.get(label, "unknown")

    def _load_from_cache(self, problem_text: str) -> Optional[Doc]:
        """Load Doc from cache if exists"""
        # Generate cache key from problem text hash
        import hashlib
        cache_key = hashlib.md5(problem_text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.spacy"

        if cache_file.exists():
            try:
                doc = Doc(self.nlp.vocab).from_disk(cache_file)
                return doc
            except Exception as e:
                print(f"   ⚠️ Cache load error: {e}")

        return None

    def _save_to_cache(self, problem_text: str, doc: Doc):
        """Save Doc to cache"""
        import hashlib
        cache_key = hashlib.md5(problem_text.encode()).hexdigest()
        cache_file = self.cache_dir / f"{cache_key}.spacy"

        try:
            doc.to_disk(cache_file)
        except Exception as e:
            print(f"   ⚠️ Cache save error: {e}")
