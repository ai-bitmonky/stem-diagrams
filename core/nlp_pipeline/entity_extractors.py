"""
Domain-Specific Entity Extractors for Multi-Domain NLP Pipeline
"""

import re
from typing import List, Dict, Any, Optional, Set
from abc import ABC, abstractmethod
import spacy
from spacy.tokens import Doc, Span

# Try to import quantulum3 for unit extraction
try:
    from quantulum3 import parser as quantity_parser
    HAS_QUANTULUM = True
except:
    HAS_QUANTULUM = False


class BaseEntityExtractor(ABC):
    """
    Base class for domain-specific entity extractors
    """

    def __init__(self, nlp: Optional[spacy.language.Language] = None):
        """
        Initialize entity extractor

        Args:
            nlp: spaCy language model (optional)
        """
        self.nlp = nlp
        self.entity_patterns = self._define_patterns()

    @abstractmethod
    def _define_patterns(self) -> List[Dict]:
        """Define entity patterns for this domain"""
        pass

    @abstractmethod
    def extract(self, doc: Doc) -> List[Dict]:
        """Extract entities from spaCy Doc"""
        pass

    def _extract_with_patterns(self, text: str) -> List[Dict]:
        """Extract entities using regex patterns"""
        entities = []

        for pattern_def in self.entity_patterns:
            pattern = pattern_def['pattern']
            entity_type = pattern_def['type']
            label = pattern_def.get('label', entity_type)

            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = {
                    'id': self._generate_id(match.group(0)),
                    'type': entity_type,
                    'label': label,
                    'text': match.group(0),
                    'properties': {
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9,
                        'method': 'pattern_match'
                    }
                }

                # Extract groups if present
                if match.groups():
                    entity['properties']['groups'] = list(match.groups())

                entities.append(entity)

        return entities

    def _generate_id(self, text: str) -> str:
        """Generate entity ID from text"""
        clean = re.sub(r'[^\w\s]', '', text.lower())
        return '_'.join(clean.split())


class PhysicsEntityExtractor(BaseEntityExtractor):
    """
    Extract physics-specific entities: masses, forces, velocities, etc.
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Mass patterns
            {
                'type': 'MASS',
                'label': 'Mass',
                'pattern': r'([\d.]+)\s*(kg|g|mg|ton|pound|lb)\s+(?:mass|block|object|body|particle)'
            },
            {
                'type': 'MASS',
                'label': 'Mass',
                'pattern': r'(?:mass|m)\s*=\s*([\d.]+)\s*(kg|g|mg)'
            },

            # Force patterns
            {
                'type': 'FORCE',
                'label': 'Force',
                'pattern': r'([\d.]+)\s*(N|newton|newtons|kN)\s+force'
            },
            {
                'type': 'FORCE',
                'label': 'Force',
                'pattern': r'(?:force|F)\s*=\s*([\d.]+)\s*(N|kN|mN)'
            },

            # Velocity patterns
            {
                'type': 'VELOCITY',
                'label': 'Velocity',
                'pattern': r'([\d.]+)\s*(m/s|km/h|mph|ft/s)\s*(?:velocity|speed)?'
            },
            {
                'type': 'VELOCITY',
                'label': 'Velocity',
                'pattern': r'(?:velocity|speed|v)\s*=\s*([\d.]+)\s*(m/s|km/h)'
            },

            # Acceleration patterns
            {
                'type': 'ACCELERATION',
                'label': 'Acceleration',
                'pattern': r'([\d.]+)\s*(m/s²|m/s2)\s*(?:acceleration)?'
            },
            {
                'type': 'ACCELERATION',
                'label': 'Acceleration',
                'pattern': r'(?:acceleration|a)\s*=\s*([\d.]+)\s*(m/s²|m/s2)'
            },

            # Angle patterns
            {
                'type': 'ANGLE',
                'label': 'Angle',
                'pattern': r'([\d.]+)\s*(?:°|degrees?|deg|rad|radians?)\s*(?:angle|incline)?'
            },

            # Distance patterns
            {
                'type': 'DISTANCE',
                'label': 'Distance',
                'pattern': r'([\d.]+)\s*(m|meters?|cm|mm|km|ft|feet|inches?|in)\s*(?:distance|length|height)?'
            },

            # Electric field patterns
            {
                'type': 'ELECTRIC_FIELD',
                'label': 'Electric Field',
                'pattern': r'electric\s+field|E-field|field\s+strength'
            },

            # Charge patterns
            {
                'type': 'CHARGE',
                'label': 'Electric Charge',
                'pattern': r'([\d.]+)\s*(C|coulomb|μC|nC|pC)\s*(?:charge)?'
            },
            {
                'type': 'CHARGE',
                'label': 'Electric Charge',
                'pattern': r'(?:charge|q|Q)\s*=\s*([\d.]+)\s*(C|μC|nC)'
            },

            # Spring constant
            {
                'type': 'SPRING_CONSTANT',
                'label': 'Spring Constant',
                'pattern': r'(?:spring\s+constant|k)\s*=\s*([\d.]+)\s*(N/m)'
            },

            # Friction coefficient
            {
                'type': 'FRICTION_COEFFICIENT',
                'label': 'Friction Coefficient',
                'pattern': r'(?:friction\s+coefficient|μ|mu)\s*=\s*([\d.]+)'
            },
        ]

    def extract(self, doc: Doc) -> List[Dict]:
        """Extract physics entities from doc"""
        entities = []

        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(doc.text)
        entities.extend(pattern_entities)

        # spaCy entity extraction for physics terms
        physics_keywords = {
            'spring', 'pulley', 'incline', 'ramp', 'pendulum',
            'projectile', 'collision', 'momentum', 'energy'
        }

        for token in doc:
            if token.text.lower() in physics_keywords:
                entity = {
                    'id': f'physics_{token.i}',
                    'type': 'PHYSICS_OBJECT',
                    'label': 'Physics Object',
                    'text': token.text,
                    'properties': {
                        'start': token.idx,
                        'end': token.idx + len(token.text),
                        'confidence': 0.85,
                        'method': 'keyword_match'
                    }
                }
                entities.append(entity)

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities based on text overlap"""
        unique = []
        seen_spans = set()

        for entity in sorted(entities, key=lambda e: e['properties']['start']):
            span = (entity['properties']['start'], entity['properties']['end'])

            # Check for overlap with existing spans
            overlap = False
            for seen_span in seen_spans:
                if (span[0] < seen_span[1] and span[1] > seen_span[0]):
                    overlap = True
                    break

            if not overlap:
                unique.append(entity)
                seen_spans.add(span)

        return unique


class ElectronicsEntityExtractor(BaseEntityExtractor):
    """
    Extract electronics-specific entities: components, values, connections
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Resistor patterns
            {
                'type': 'RESISTOR',
                'label': 'Resistor',
                'pattern': r'(?:resistor|R\d+)\s*(?:of|=)?\s*([\d.]+)\s*(Ω|ohm|ohms|kΩ|MΩ)'
            },

            # Capacitor patterns
            {
                'type': 'CAPACITOR',
                'label': 'Capacitor',
                'pattern': r'(?:capacitor|C\d+)\s*(?:of|=)?\s*([\d.]+)\s*(F|μF|nF|pF|farad)'
            },

            # Inductor patterns
            {
                'type': 'INDUCTOR',
                'label': 'Inductor',
                'pattern': r'(?:inductor|L\d+)\s*(?:of|=)?\s*([\d.]+)\s*(H|mH|μH|henry)'
            },

            # Voltage source patterns
            {
                'type': 'VOLTAGE_SOURCE',
                'label': 'Voltage Source',
                'pattern': r'(?:battery|voltage\s+source|power\s+supply|V\d+)\s*(?:of|=)?\s*([\d.]+)\s*(V|volt|volts|mV|kV)'
            },

            # Current patterns
            {
                'type': 'CURRENT',
                'label': 'Current',
                'pattern': r'(?:current|I\d*)\s*=\s*([\d.]+)\s*(A|amp|amps|mA|μA)'
            },

            # Voltage patterns
            {
                'type': 'VOLTAGE',
                'label': 'Voltage',
                'pattern': r'(?:voltage|potential|V\d*)\s*=\s*([\d.]+)\s*(V|volt|mV|kV)'
            },

            # Connection patterns
            {
                'type': 'CONNECTION',
                'label': 'Connection',
                'pattern': r'(?:connected|in\s+series|in\s+parallel|wired)'
            },

            # Node patterns
            {
                'type': 'NODE',
                'label': 'Node',
                'pattern': r'(?:node|junction|terminal)\s*[A-Z\d]+'
            },
        ]

    def extract(self, doc: Doc) -> List[Dict]:
        """Extract electronics entities from doc"""
        entities = []

        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(doc.text)
        entities.extend(pattern_entities)

        # Detect series/parallel configurations
        if re.search(r'in\s+series', doc.text, re.IGNORECASE):
            entity = {
                'id': 'series_configuration',
                'type': 'CONFIGURATION',
                'label': 'Series Configuration',
                'text': 'series',
                'properties': {
                    'configuration_type': 'series',
                    'confidence': 0.95,
                    'method': 'pattern_match'
                }
            }
            entities.append(entity)

        if re.search(r'in\s+parallel', doc.text, re.IGNORECASE):
            entity = {
                'id': 'parallel_configuration',
                'type': 'CONFIGURATION',
                'label': 'Parallel Configuration',
                'text': 'parallel',
                'properties': {
                    'configuration_type': 'parallel',
                    'confidence': 0.95,
                    'method': 'pattern_match'
                }
            }
            entities.append(entity)

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []

        for entity in entities:
            key = (entity['type'], entity['text'])
            if key not in seen:
                seen.add(key)
                unique.append(entity)

        return unique


class GeometryEntityExtractor(BaseEntityExtractor):
    """
    Extract geometry-specific entities: points, lines, angles, shapes
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Point patterns
            {
                'type': 'POINT',
                'label': 'Point',
                'pattern': r'(?:point|vertex|corner)\s+([A-Z])'
            },

            # Line patterns
            {
                'type': 'LINE',
                'label': 'Line',
                'pattern': r'(?:line|segment)\s+([A-Z]{2})'
            },

            # Angle patterns
            {
                'type': 'ANGLE',
                'label': 'Angle',
                'pattern': r'angle\s+([A-Z]{3})'
            },
            {
                'type': 'ANGLE',
                'label': 'Angle',
                'pattern': r'(?:∠|angle)\s*([A-Z]{3})\s*=\s*([\d.]+)°'
            },

            # Circle patterns
            {
                'type': 'CIRCLE',
                'label': 'Circle',
                'pattern': r'circle\s+(?:with\s+)?(?:center\s+)?([A-Z])?'
            },

            # Triangle patterns
            {
                'type': 'TRIANGLE',
                'label': 'Triangle',
                'pattern': r'triangle\s+([A-Z]{3})'
            },

            # Rectangle patterns
            {
                'type': 'RECTANGLE',
                'label': 'Rectangle',
                'pattern': r'rectangle\s+([A-Z]{4})'
            },

            # Length/distance patterns
            {
                'type': 'LENGTH',
                'label': 'Length',
                'pattern': r'(?:length|distance)\s+([A-Z]{2})\s*=\s*([\d.]+)\s*(cm|m|mm)'
            },

            # Area patterns
            {
                'type': 'AREA',
                'label': 'Area',
                'pattern': r'area\s*=\s*([\d.]+)\s*(cm²|m²|mm²)'
            },
        ]

    def extract(self, doc: Doc) -> List[Dict]:
        """Extract geometry entities from doc"""
        entities = []

        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(doc.text)
        entities.extend(pattern_entities)

        # Detect shape keywords
        shape_keywords = {
            'triangle': 'TRIANGLE',
            'square': 'SQUARE',
            'rectangle': 'RECTANGLE',
            'circle': 'CIRCLE',
            'pentagon': 'PENTAGON',
            'hexagon': 'HEXAGON',
            'polygon': 'POLYGON'
        }

        for token in doc:
            shape_type = shape_keywords.get(token.text.lower())
            if shape_type:
                entity = {
                    'id': f'shape_{token.i}',
                    'type': shape_type,
                    'label': shape_type.title(),
                    'text': token.text,
                    'properties': {
                        'start': token.idx,
                        'end': token.idx + len(token.text),
                        'confidence': 0.9,
                        'method': 'keyword_match'
                    }
                }
                entities.append(entity)

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        unique = {}
        for entity in entities:
            key = (entity['type'], entity['text'])
            if key not in unique:
                unique[key] = entity

        return list(unique.values())


class ChemistryEntityExtractor(BaseEntityExtractor):
    """
    Extract chemistry-specific entities: molecules, bonds, reactions
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Molecule patterns (simple chemical formulas)
            {
                'type': 'MOLECULE',
                'label': 'Molecule',
                'pattern': r'([A-Z][a-z]?\d*)+(?:\([A-Z][a-z]?\d*\)\d*)*'
            },

            # Ion patterns
            {
                'type': 'ION',
                'label': 'Ion',
                'pattern': r'([A-Z][a-z]?)\d*[⁺⁻+-]+'
            },

            # Reaction arrow
            {
                'type': 'REACTION',
                'label': 'Reaction',
                'pattern': r'→|-->|⇌|<-->|⇄'
            },

            # Bond patterns
            {
                'type': 'BOND',
                'label': 'Chemical Bond',
                'pattern': r'(?:single|double|triple|covalent|ionic|hydrogen)\s+bond'
            },

            # pH patterns
            {
                'type': 'PH',
                'label': 'pH Value',
                'pattern': r'pH\s*=\s*([\d.]+)'
            },

            # Concentration patterns
            {
                'type': 'CONCENTRATION',
                'label': 'Concentration',
                'pattern': r'([\d.]+)\s*(M|mM|μM|mol/L|molarity)'
            },
        ]

    def extract(self, doc: Doc) -> List[Dict]:
        """Extract chemistry entities from doc"""
        entities = []

        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(doc.text)
        entities.extend(pattern_entities)

        # Chemistry keywords
        chem_keywords = {
            'reactant', 'product', 'catalyst', 'solvent',
            'acid', 'base', 'salt', 'precipitate',
            'oxidation', 'reduction', 'equilibrium'
        }

        for token in doc:
            if token.text.lower() in chem_keywords:
                entity = {
                    'id': f'chem_{token.i}',
                    'type': 'CHEM_KEYWORD',
                    'label': 'Chemistry Term',
                    'text': token.text,
                    'properties': {
                        'start': token.idx,
                        'end': token.idx + len(token.text),
                        'confidence': 0.85,
                        'method': 'keyword_match'
                    }
                }
                entities.append(entity)

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []

        for entity in entities:
            key = (entity['type'], entity['text'])
            if key not in seen:
                seen.add(key)
                unique.append(entity)

        return unique


class BiologyEntityExtractor(BaseEntityExtractor):
    """
    Extract biology-specific entities: cells, organs, processes
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Cell patterns
            {
                'type': 'CELL',
                'label': 'Cell Type',
                'pattern': r'\w+\s+cell'
            },

            # Organ patterns
            {
                'type': 'ORGAN',
                'label': 'Organ',
                'pattern': r'(?:heart|lung|liver|kidney|brain|stomach|intestine)'
            },

            # Organism patterns
            {
                'type': 'ORGANISM',
                'label': 'Organism',
                'pattern': r'(?:bacteria|virus|plant|animal|fungus|human)'
            },

            # Protein patterns
            {
                'type': 'PROTEIN',
                'label': 'Protein',
                'pattern': r'\w+ase|protein|enzyme|antibody|antigen'
            },

            # DNA/RNA patterns
            {
                'type': 'NUCLEIC_ACID',
                'label': 'Nucleic Acid',
                'pattern': r'DNA|RNA|mRNA|tRNA|rRNA|nucleotide'
            },

            # Process patterns
            {
                'type': 'PROCESS',
                'label': 'Biological Process',
                'pattern': r'(?:photosynthesis|respiration|mitosis|meiosis|transcription|translation)'
            },
        ]

    def extract(self, doc: Doc) -> List[Dict]:
        """Extract biology entities from doc"""
        entities = []

        # Pattern-based extraction
        pattern_entities = self._extract_with_patterns(doc.text)
        entities.extend(pattern_entities)

        # Biology keywords
        bio_keywords = {
            'membrane', 'cytoplasm', 'nucleus', 'mitochondria',
            'chloroplast', 'ribosome', 'golgi', 'endoplasmic',
            'tissue', 'organ', 'system', 'organism'
        }

        for token in doc:
            if token.text.lower() in bio_keywords:
                entity = {
                    'id': f'bio_{token.i}',
                    'type': 'BIO_KEYWORD',
                    'label': 'Biology Term',
                    'text': token.text,
                    'properties': {
                        'start': token.idx,
                        'end': token.idx + len(token.text),
                        'confidence': 0.85,
                        'method': 'keyword_match'
                    }
                }
                entities.append(entity)

        return self._deduplicate_entities(entities)

    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []

        for entity in entities:
            key = (entity['type'], entity['text'])
            if key not in seen:
                seen.add(key)
                unique.append(entity)

        return unique
