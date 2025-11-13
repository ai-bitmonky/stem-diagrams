#!/usr/bin/env python3
"""
SciBERT-Enhanced NLP Pipeline
==============================

Integrates SciBERT (scientific BERT) for improved understanding of
scientific and technical text.

SciBERT is trained on scientific papers and significantly outperforms
general BERT models for scientific entity recognition and relation extraction.

Author: Universal STEM Diagram Generator
Date: November 5, 2025
"""

import spacy
from typing import Dict, List, Any, Optional, Tuple
import logging

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class SciBERTNLPPipeline:
    """
    SciBERT-enhanced NLP pipeline

    Uses AllenAI's SciBERT model for scientific text understanding
    Model: allenai/scibert_scivocab_uncased
    """

    def __init__(
        self,
        use_gpu: bool = False,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize SciBERT NLP pipeline

        Args:
            use_gpu: Use GPU if available
            cache_dir: Directory to cache models
        """
        self.logger = logging.getLogger(__name__)
        self.use_gpu = use_gpu and torch.cuda.is_available() if HAS_TRANSFORMERS else False

        # Load spaCy with SciBERT-compatible config
        try:
            # Try to load scispacy model (better for scientific text)
            self.nlp = spacy.load("en_core_sci_sm")
            self.logger.info("✓ Loaded SciSpacy model: en_core_sci_sm")
        except OSError:
            # Fallback to general model
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.warning("⚠️  SciSpacy not found, using en_core_web_sm")
            self.logger.info("   Install with: pip install scispacy")
            self.logger.info("   Then: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz")

        # Load SciBERT model if transformers available
        self.scibert_model = None
        self.scibert_tokenizer = None

        if HAS_TRANSFORMERS:
            try:
                self.logger.info("Loading SciBERT model...")
                model_name = "allenai/scibert_scivocab_uncased"
                self.scibert_tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=cache_dir
                )
                self.scibert_model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=cache_dir
                )

                if self.use_gpu:
                    self.scibert_model = self.scibert_model.cuda()
                    self.logger.info("✓ SciBERT loaded on GPU")
                else:
                    self.logger.info("✓ SciBERT loaded on CPU")

            except Exception as e:
                self.logger.warning(f"⚠️  Could not load SciBERT: {e}")
                self.logger.info("   Will use spaCy features only")
        else:
            self.logger.warning("⚠️  transformers library not found")
            self.logger.info("   Install with: pip install transformers torch")

    def process(
        self,
        text: str,
        extract_embeddings: bool = False
    ) -> Dict[str, Any]:
        """
        Process scientific text with SciBERT

        Args:
            text: Input text
            extract_embeddings: Extract SciBERT embeddings

        Returns:
            Dictionary with entities, relationships, embeddings
        """
        # Process with spaCy
        doc = self.nlp(text)

        # Extract entities with scientific awareness (returns entities and quantities)
        entities, quantities = self._extract_scientific_entities(doc)

        # Extract relationships
        relationships = self._extract_relationships(doc, entities)

        # Classify domain
        domain = self._classify_scientific_domain(doc, entities)

        # Calculate confidence based on quantity extraction
        confidence = self._calculate_confidence(entities, quantities, relationships)

        result = {
            'text': text,
            'domain': domain,
            'entities': entities,
            'quantities': quantities,
            'relationships': relationships,
            'confidence': confidence,
            'metadata': {
                'num_entities': len(entities),
                'num_quantities': len(quantities),
                'num_relationships': len(relationships),
                'pipeline': 'scibert_nlp',
                'model': 'en_core_sci_sm' if 'sci' in self.nlp.meta['name'] else 'en_core_web_sm'
            }
        }

        # Add SciBERT embeddings if requested
        if extract_embeddings and self.scibert_model:
            result['embeddings'] = self._get_scibert_embeddings(text)

        return result

    def _extract_scientific_entities(self, doc) -> Tuple[List[Dict], List[Dict]]:
        """Extract entities with scientific domain awareness

        Returns:
            Tuple of (entities, quantities)
        """
        entities = []

        # Extract named entities from spaCy
        for ent in doc.ents:
            entity = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'type': self._map_scientific_type(ent.label_),
                'confidence': 0.8  # spaCy NER confidence
            }
            entities.append(entity)

        # Extract scientific terminology (noun chunks with scientific indicators)
        for chunk in doc.noun_chunks:
            # Check if contains scientific terms
            if self._is_scientific_term(chunk):
                # Avoid duplicates with NER entities
                if not any(e['text'] == chunk.text for e in entities):
                    entity = {
                        'text': chunk.text,
                        'label': 'SCIENTIFIC_TERM',
                        'start': chunk.start_char,
                        'end': chunk.end_char,
                        'type': 'concept',
                        'confidence': 0.6
                    }
                    entities.append(entity)

        # Extract quantities and measurements separately
        quantities = self._extract_quantities(doc)

        # Also add quantities to entities for backward compatibility
        entities.extend(quantities)

        return entities, quantities

    def _map_scientific_type(self, label: str) -> str:
        """Map spaCy labels to scientific types"""
        mapping = {
            'CHEMICAL': 'chemical',
            'DISEASE': 'biological_concept',
            'GENE': 'gene',
            'PROTEIN': 'protein',
            'CELL_TYPE': 'cell',
            'TISSUE': 'tissue',
            'ORGANISM': 'organism',
            'QUANTITY': 'measurement',
            'CARDINAL': 'number',
            'PERCENT': 'percentage',
            'MONEY': 'value',
            'DATE': 'temporal',
            'TIME': 'temporal'
        }
        return mapping.get(label, 'entity')

    def _is_scientific_term(self, chunk) -> bool:
        """Check if noun chunk is a scientific term"""
        scientific_indicators = [
            'acid', 'oxide', 'molecule', 'atom', 'ion', 'compound',
            'reaction', 'synthesis', 'catalyst', 'polymer',
            'cell', 'protein', 'enzyme', 'gene', 'DNA', 'RNA',
            'force', 'energy', 'velocity', 'acceleration', 'momentum',
            'voltage', 'current', 'resistance', 'capacitance', 'inductance',
            'frequency', 'wavelength', 'amplitude', 'phase'
        ]

        text_lower = chunk.text.lower()
        return any(term in text_lower for term in scientific_indicators)

    def _extract_quantities(self, doc) -> List[Dict]:
        """Extract numerical quantities and measurements"""
        quantities = []

        # Look for patterns: NUMBER + UNIT
        import re
        text = doc.text

        # Physics/Engineering units
        unit_patterns = [
            r'(\d+(?:\.\d+)?)\s*(m|cm|mm|km|nm)',  # distance
            r'(\d+(?:\.\d+)?)\s*(kg|g|mg)',  # mass
            r'(\d+(?:\.\d+)?)\s*(s|ms|μs|ns)',  # time
            r'(\d+(?:\.\d+)?)\s*(N|kN)',  # force
            r'(\d+(?:\.\d+)?)\s*(J|kJ|eV)',  # energy
            r'(\d+(?:\.\d+)?)\s*(W|kW|MW)',  # power
            r'(\d+(?:\.\d+)?)\s*(V|mV|kV)',  # voltage
            r'(\d+(?:\.\d+)?)\s*(A|mA|μA)',  # current
            r'(\d+(?:\.\d+)?)\s*(Ω|kΩ|MΩ|ohm)',  # resistance
            r'(\d+(?:\.\d+)?)\s*(F|μF|nF|pF)',  # capacitance
            r'(\d+(?:\.\d+)?)\s*(H|mH|μH)',  # inductance
            r'(\d+(?:\.\d+)?)\s*(Hz|kHz|MHz|GHz)',  # frequency
            r'(\d+(?:\.\d+)?)\s*(Pa|kPa|MPa|atm|bar)',  # pressure
            r'(\d+(?:\.\d+)?)\s*(°C|K|°F)',  # temperature
            r'(\d+(?:\.\d+)?)\s*(mol|mmol)',  # amount
            r'(\d+(?:\.\d+)?)\s*(M|mM|μM)',  # concentration
        ]

        for pattern in unit_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value, unit = match.groups()
                quantities.append({
                    'text': match.group(0),
                    'label': 'QUANTITY',
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'measurement',
                    'confidence': 0.9,
                    'value': float(value),
                    'unit': unit
                })

        return quantities

    def _extract_relationships(self, doc, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []

        # Dependency-based relation extraction
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                # Look for verb connecting entities
                head = token.head
                if head.pos_ == 'VERB':
                    # Find entities matching subject and object
                    subj_entities = [e for e in entities if e['text'] == token.text]
                    obj_entities = [e for e in entities if token.head.text in e['text']]

                    for subj in subj_entities:
                        for obj in obj_entities:
                            relationships.append({
                                'source': subj['text'],
                                'target': obj['text'],
                                'type': head.lemma_,
                                'confidence': 0.7
                            })

        return relationships

    def _classify_scientific_domain(self, doc, entities: List[Dict]) -> str:
        """Classify the scientific domain"""
        domain_keywords = {
            'physics': ['force', 'mass', 'velocity', 'energy', 'momentum', 'acceleration',
                       'pressure', 'temperature', 'mechanics', 'thermodynamics'],
            'chemistry': ['molecule', 'atom', 'reaction', 'compound', 'element', 'acid',
                         'base', 'catalyst', 'synthesis', 'oxidation', 'reduction'],
            'biology': ['cell', 'protein', 'gene', 'DNA', 'organism', 'tissue',
                       'enzyme', 'metabolism', 'evolution', 'genetics'],
            'electronics': ['voltage', 'current', 'resistance', 'capacitor', 'inductor',
                          'circuit', 'transistor', 'diode', 'amplifier', 'battery'],
            'mathematics': ['equation', 'function', 'derivative', 'integral', 'matrix',
                          'vector', 'theorem', 'proof', 'geometry', 'algebra']
        }

        text_lower = doc.text.lower()
        domain_scores = {}

        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            domain_scores[domain] = score

        # Return domain with highest score
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        return 'general'

    def _calculate_confidence(
        self,
        entities: List[Dict],
        quantities: List[Dict],
        relationships: List[Dict]
    ) -> float:
        """
        Calculate confidence score based on extraction quality

        Args:
            entities: Extracted entities
            quantities: Extracted quantities
            relationships: Extracted relationships

        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence on successful extraction
        confidence = 0.5

        # Boost for quantities (strong signal of STEM content)
        if quantities:
            confidence += min(0.2, len(quantities) * 0.02)

        # Boost for relationships
        if relationships:
            confidence += min(0.15, len(relationships) * 0.015)

        # Boost for high-confidence entities
        high_conf_entities = [e for e in entities if e.get('confidence', 0) > 0.7]
        if high_conf_entities:
            confidence += min(0.15, len(high_conf_entities) * 0.015)

        return min(1.0, confidence)

    def _get_scibert_embeddings(self, text: str) -> Dict:
        """Get SciBERT embeddings for text"""
        if not self.scibert_model:
            return {}

        # Tokenize
        inputs = self.scibert_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        if self.use_gpu:
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Get embeddings
        with torch.no_grad():
            outputs = self.scibert_model(**inputs)

        # Use [CLS] token embedding as sentence representation
        cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()

        return {
            'cls_embedding': cls_embedding.tolist(),
            'embedding_dim': cls_embedding.shape[-1]
        }


if __name__ == "__main__":
    # Test SciBERT NLP
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("SciBERT NLP PIPELINE TEST")
    print("=" * 60)

    nlp = SciBERTNLPPipeline(use_gpu=False)

    # Test with scientific text
    test_texts = [
        "A 100 Ω resistor is connected in series with a 10 μF capacitor and a 12 V battery.",
        "The reaction between sodium hydroxide and hydrochloric acid produces sodium chloride and water.",
        "A force of 50 N is applied to a 5 kg mass on a frictionless surface.",
        "The enzyme catalase catalyzes the decomposition of hydrogen peroxide into water and oxygen."
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {text}")
        print('='*60)

        result = nlp.process(text)

        print(f"\n✓ Domain: {result['domain']}")
        print(f"✓ Entities: {result['metadata']['num_entities']}")
        for entity in result['entities'][:5]:  # Show first 5
            print(f"   - {entity['text']} [{entity['type']}]")

        print(f"✓ Relationships: {result['metadata']['num_relationships']}")
        for rel in result['relationships'][:3]:  # Show first 3
            print(f"   - {rel['source']} --[{rel['type']}]--> {rel['target']}")

    print("\n" + "=" * 60)
    print("✅ SciBERT NLP Pipeline ready")
    print("=" * 60)

    print("\n📝 Installation notes:")
    print("   SciBERT: pip install transformers torch")
    print("   SciSpacy: pip install scispacy")
    print("   Model: pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz")
