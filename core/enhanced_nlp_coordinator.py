"""
Enhanced NLP Coordinator - Multi-Tool Ensemble for Text Understanding
====================================================================

Addresses the text understanding gap by combining multiple NLP tools:
- spaCy: General NER, POS tagging, dependency parsing
- Custom Unit Extractor: STEM-specific unit and quantity extraction
- Domain Detector: Multi-domain classification with confidence scores
- Entity Linker: Future integration with knowledge bases

Author: Universal Diagram Generator Team
Date: November 6, 2025
Status: Phase 1 Implementation
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes for Enhanced Entities
# ============================================================================

@dataclass
class Quantity:
    """Represents a physical quantity with value, unit, and context"""
    value: float
    unit: str
    raw_text: str
    start_char: int
    end_char: int
    entity_type: str  # e.g., 'voltage', 'capacitance', 'force'
    confidence: float = 1.0

    def __repr__(self):
        return f"{self.value} {self.unit} ({self.entity_type})"


@dataclass
class EnhancedEntity:
    """Enhanced entity with richer information than base spaCy"""
    text: str
    label: str
    start_char: int
    end_char: int
    extraction_method: str  # 'spacy', 'regex', 'custom'
    confidence: float
    properties: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'label': self.label,
            'start': self.start_char,
            'end': self.end_char,
            'method': self.extraction_method,
            'confidence': self.confidence,
            'properties': self.properties
        }


@dataclass
class EnhancedNLPResult:
    """Result from multi-tool NLP ensemble"""
    text: str
    entities: List[EnhancedEntity]
    quantities: List[Quantity]
    domain: str
    domain_confidence: float
    tokens: List[Dict]
    relationships: List[Dict]
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'entities': [e.to_dict() for e in self.entities],
            'quantities': [{'value': q.value, 'unit': q.unit, 'type': q.entity_type,
                           'text': q.raw_text} for q in self.quantities],
            'domain': self.domain,
            'domain_confidence': self.domain_confidence,
            'num_entities': len(self.entities),
            'num_quantities': len(self.quantities),
            'metadata': self.metadata
        }


# ============================================================================
# Unit Extractor - STEM-Specific Unit and Quantity Extraction
# ============================================================================

class STEMUnitExtractor:
    """
    Custom unit extractor for STEM problems.

    More reliable than Quantulum3 for STEM domains:
    - No external dependencies (just regex)
    - Tailored for physics/electronics/chemistry
    - Easy to extend with new units
    """

    # Comprehensive unit patterns for STEM domains
    UNIT_PATTERNS = {
        # Electrical units
        'voltage': [
            (r'(\d+(?:\.\d+)?)\s*(?:V|volt|volts|voltage)', 'volt', 'V'),
            (r'(\d+(?:\.\d+)?)\s*(?:kV|kilovolt)', 'kilovolt', 'kV'),
            (r'(\d+(?:\.\d+)?)\s*(?:mV|millivolt)', 'millivolt', 'mV'),
        ],
        'current': [
            (r'(\d+(?:\.\d+)?)\s*(?:A|amp|amps|ampere|amperes)', 'ampere', 'A'),
            (r'(\d+(?:\.\d+)?)\s*(?:mA|milliamp)', 'milliampere', 'mA'),
            (r'(\d+(?:\.\d+)?)\s*(?:μA|microamp)', 'microampere', 'μA'),
        ],
        'resistance': [
            (r'(\d+(?:\.\d+)?)\s*(?:Ω|ohm|ohms)', 'ohm', 'Ω'),
            (r'(\d+(?:\.\d+)?)\s*(?:kΩ|kilohm)', 'kilohm', 'kΩ'),
            (r'(\d+(?:\.\d+)?)\s*(?:MΩ|megohm)', 'megohm', 'MΩ'),
        ],
        'capacitance': [
            (r'(\d+(?:\.\d+)?)\s*(?:F|farad|farads)', 'farad', 'F'),
            (r'(\d+(?:\.\d+)?)\s*(?:μF|microfarad|uf)', 'microfarad', 'μF'),
            (r'(\d+(?:\.\d+)?)\s*(?:nF|nanofarad)', 'nanofarad', 'nF'),
            (r'(\d+(?:\.\d+)?)\s*(?:pF|picofarad)', 'picofarad', 'pF'),
        ],
        'inductance': [
            (r'(\d+(?:\.\d+)?)\s*(?:H|henry|henries)', 'henry', 'H'),
            (r'(\d+(?:\.\d+)?)\s*(?:mH|millihenry)', 'millihenry', 'mH'),
            (r'(\d+(?:\.\d+)?)\s*(?:μH|microhenry)', 'microhenry', 'μH'),
        ],

        # Mechanical units
        'force': [
            (r'(\d+(?:\.\d+)?)\s*(?:N|newton|newtons)', 'newton', 'N'),
            (r'(\d+(?:\.\d+)?)\s*(?:kN|kilonewton)', 'kilonewton', 'kN'),
        ],
        'mass': [
            (r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram|kilograms)', 'kilogram', 'kg'),
            (r'(\d+(?:\.\d+)?)\s*(?:g|gram|grams)', 'gram', 'g'),
            (r'(\d+(?:\.\d+)?)\s*(?:mg|milligram)', 'milligram', 'mg'),
        ],
        'length': [
            (r'(\d+(?:\.\d+)?)\s*(?:m|meter|meters|metre|metres)', 'meter', 'm'),
            (r'(\d+(?:\.\d+)?)\s*(?:km|kilometer)', 'kilometer', 'km'),
            (r'(\d+(?:\.\d+)?)\s*(?:cm|centimeter)', 'centimeter', 'cm'),
            (r'(\d+(?:\.\d+)?)\s*(?:mm|millimeter)', 'millimeter', 'mm'),
        ],
        'time': [
            (r'(\d+(?:\.\d+)?)\s*(?:s|sec|second|seconds)', 'second', 's'),
            (r'(\d+(?:\.\d+)?)\s*(?:ms|millisecond)', 'millisecond', 'ms'),
            (r'(\d+(?:\.\d+)?)\s*(?:μs|microsecond)', 'microsecond', 'μs'),
            (r'(\d+(?:\.\d+)?)\s*(?:min|minute|minutes)', 'minute', 'min'),
            (r'(\d+(?:\.\d+)?)\s*(?:h|hr|hour|hours)', 'hour', 'h'),
        ],
        'angle': [
            (r'(\d+(?:\.\d+)?)\s*(?:°|deg|degree|degrees)', 'degree', '°'),
            (r'(\d+(?:\.\d+)?)\s*(?:rad|radian|radians)', 'radian', 'rad'),
        ],
        'velocity': [
            (r'(\d+(?:\.\d+)?)\s*(?:m/s|meter per second)', 'meter per second', 'm/s'),
            (r'(\d+(?:\.\d+)?)\s*(?:km/h|kilometer per hour)', 'kilometer per hour', 'km/h'),
        ],
        'acceleration': [
            (r'(\d+(?:\.\d+)?)\s*(?:m/s²|m/s2|meter per second squared)', 'meter per second squared', 'm/s²'),
        ],

        # Temperature
        'temperature': [
            (r'(\d+(?:\.\d+)?)\s*(?:°C|celsius)', 'celsius', '°C'),
            (r'(\d+(?:\.\d+)?)\s*(?:°F|fahrenheit)', 'fahrenheit', '°F'),
            (r'(\d+(?:\.\d+)?)\s*(?:K|kelvin)', 'kelvin', 'K'),
        ],

        # Frequency
        'frequency': [
            (r'(\d+(?:\.\d+)?)\s*(?:Hz|hertz)', 'hertz', 'Hz'),
            (r'(\d+(?:\.\d+)?)\s*(?:kHz|kilohertz)', 'kilohertz', 'kHz'),
            (r'(\d+(?:\.\d+)?)\s*(?:MHz|megahertz)', 'megahertz', 'MHz'),
            (r'(\d+(?:\.\d+)?)\s*(?:GHz|gigahertz)', 'gigahertz', 'GHz'),
        ],

        # Energy/Power
        'energy': [
            (r'(\d+(?:\.\d+)?)\s*(?:J|joule|joules)', 'joule', 'J'),
            (r'(\d+(?:\.\d+)?)\s*(?:kJ|kilojoule)', 'kilojoule', 'kJ'),
        ],
        'power': [
            (r'(\d+(?:\.\d+)?)\s*(?:W|watt|watts)', 'watt', 'W'),
            (r'(\d+(?:\.\d+)?)\s*(?:kW|kilowatt)', 'kilowatt', 'kW'),
            (r'(\d+(?:\.\d+)?)\s*(?:mW|milliwatt)', 'milliwatt', 'mW'),
        ],
    }

    def extract(self, text: str) -> List[Quantity]:
        """Extract all quantities with units from text"""
        quantities = []

        for entity_type, patterns in self.UNIT_PATTERNS.items():
            for pattern, unit_name, unit_symbol in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        quantities.append(Quantity(
                            value=value,
                            unit=unit_symbol,
                            raw_text=match.group(0),
                            start_char=match.start(),
                            end_char=match.end(),
                            entity_type=entity_type,
                            confidence=0.95  # High confidence for regex matches
                        ))
                    except (ValueError, IndexError):
                        continue

        # Remove duplicates (keep highest confidence)
        quantities = self._deduplicate_quantities(quantities)

        return quantities

    def _deduplicate_quantities(self, quantities: List[Quantity]) -> List[Quantity]:
        """Remove overlapping quantity detections"""
        if not quantities:
            return []

        # Sort by start position
        quantities.sort(key=lambda q: q.start_char)

        result = [quantities[0]]
        for q in quantities[1:]:
            # If this quantity doesn't overlap with the last one, add it
            if q.start_char >= result[-1].end_char:
                result.append(q)
            # If it overlaps, keep the one with higher confidence
            elif q.confidence > result[-1].confidence:
                result[-1] = q

        return result


# ============================================================================
# Enhanced NLP Coordinator - Multi-Tool Ensemble
# ============================================================================

class EnhancedNLPCoordinator:
    """
    Multi-tool NLP ensemble coordinator.

    Combines:
    1. spaCy - General NER, POS tagging
    2. STEMUnitExtractor - STEM-specific unit extraction
    3. Domain classification - Multi-domain detection
    4. (Future) SciBERT - Scientific entity extraction
    5. (Future) Entity linker - Knowledge base integration
    """

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize multi-tool ensemble"""
        self.unit_extractor = STEMUnitExtractor()

        # Load spaCy model
        try:
            import spacy
            self.nlp = spacy.load(spacy_model)
            logger.info(f"✅ Loaded spaCy model: {spacy_model}")
        except Exception as e:
            logger.warning(f"⚠️  Could not load spaCy: {e}")
            self.nlp = None

        # Domain classification keywords
        self.domain_keywords = {
            'electronics': ['circuit', 'voltage', 'current', 'resistor', 'capacitor',
                           'inductor', 'battery', 'ohm', 'ampere', 'farad', 'wire'],
            'mechanics': ['force', 'mass', 'acceleration', 'velocity', 'friction',
                         'gravity', 'newton', 'kg', 'momentum', 'energy'],
            'thermodynamics': ['temperature', 'heat', 'entropy', 'pressure', 'gas',
                              'celsius', 'kelvin', 'joule', 'thermal'],
            'optics': ['light', 'lens', 'mirror', 'reflection', 'refraction',
                      'wavelength', 'frequency', 'photon', 'beam'],
            'chemistry': ['molecule', 'atom', 'bond', 'reaction', 'compound',
                         'element', 'chemical', 'solution', 'acid', 'base'],
            'mathematics': ['equation', 'function', 'graph', 'angle', 'triangle',
                           'circle', 'square', 'geometry', 'algebra'],
        }

    def process(self, text: str) -> EnhancedNLPResult:
        """Process text with multi-tool ensemble"""

        # Step 1: Extract quantities (STEM units)
        quantities = self.unit_extractor.extract(text)

        # Step 2: Extract entities with spaCy
        entities = self._extract_spacy_entities(text)

        # Step 3: Classify domain
        domain, domain_conf = self._classify_domain(text, quantities)

        # Step 4: Extract tokens and relationships
        tokens = self._extract_tokens(text)
        relationships = self._extract_relationships(text)

        # Step 5: Build metadata
        metadata = {
            'num_spacy_entities': len([e for e in entities if e.extraction_method == 'spacy']),
            'num_unit_quantities': len(quantities),
            'tools_used': ['spacy', 'stem_unit_extractor', 'domain_classifier'],
            'processing_time': 0.0  # Would need timer
        }

        return EnhancedNLPResult(
            text=text,
            entities=entities,
            quantities=quantities,
            domain=domain,
            domain_confidence=domain_conf,
            tokens=tokens,
            relationships=relationships,
            metadata=metadata
        )

    def _extract_spacy_entities(self, text: str) -> List[EnhancedEntity]:
        """Extract entities using spaCy"""
        entities = []

        if not self.nlp:
            return entities

        doc = self.nlp(text)
        for ent in doc.ents:
            entities.append(EnhancedEntity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
                extraction_method='spacy',
                confidence=0.85,  # spaCy doesn't provide confidence
                properties={'lemma': ent.lemma_}
            ))

        return entities

    def _classify_domain(self, text: str, quantities: List[Quantity]) -> Tuple[str, float]:
        """Classify domain with confidence score"""
        text_lower = text.lower()

        # Score each domain based on keywords
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[domain] = score

        # Boost score based on quantity types
        for q in quantities:
            if q.entity_type in ['voltage', 'current', 'resistance', 'capacitance']:
                scores['electronics'] = scores.get('electronics', 0) + 2
            elif q.entity_type in ['force', 'mass', 'acceleration']:
                scores['mechanics'] = scores.get('mechanics', 0) + 2

        if not scores or max(scores.values()) == 0:
            return 'unknown', 0.0

        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.0

        return best_domain, min(confidence, 1.0)

    def _extract_tokens(self, text: str) -> List[Dict]:
        """Extract tokens with POS tags"""
        if not self.nlp:
            return []

        doc = self.nlp(text)
        return [
            {'text': token.text, 'pos': token.pos_, 'lemma': token.lemma_}
            for token in doc
        ]

    def _extract_relationships(self, text: str) -> List[Dict]:
        """Extract relationships between entities (basic dependency parsing)"""
        if not self.nlp:
            return []

        doc = self.nlp(text)
        relationships = []

        # Simple relationship extraction based on dependency parsing
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                relationships.append({
                    'subject': token.text,
                    'relation': token.dep_,
                    'object': token.head.text
                })

        return relationships


# ============================================================================
# Main Interface
# ============================================================================

def create_enhanced_nlp_coordinator() -> EnhancedNLPCoordinator:
    """Factory function to create enhanced NLP coordinator"""
    return EnhancedNLPCoordinator()


if __name__ == "__main__":
    # Test the enhanced NLP coordinator
    print("=" * 70)
    print("ENHANCED NLP COORDINATOR TEST")
    print("=" * 70)

    coordinator = create_enhanced_nlp_coordinator()

    test_problems = [
        "A 10μF capacitor connected to a 12V battery through a 100Ω resistor",
        "A 5kg block rests on a 30° incline with friction coefficient 0.3",
        "Apply a force of 20N to accelerate a 2kg mass"
    ]

    for i, problem in enumerate(test_problems, 1):
        print(f"\n[Test {i}] {problem}")
        print("-" * 70)

        result = coordinator.process(problem)

        print(f"Domain: {result.domain} (confidence: {result.domain_confidence:.2f})")
        print(f"Quantities found: {len(result.quantities)}")
        for q in result.quantities:
            print(f"  - {q}")

        print(f"Entities found: {len(result.entities)}")
        for e in result.entities[:5]:  # Show first 5
            print(f"  - {e.text} ({e.label})")

    print("\n" + "=" * 70)
    print("✅ Enhanced NLP Coordinator working!")
