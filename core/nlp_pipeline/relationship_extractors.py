"""
Relationship Extractors for Multi-Domain NLP Pipeline

Extracts spatial, functional, and quantitative relationships between entities
"""

import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import spacy
from spacy.tokens import Doc, Token


class BaseRelationshipExtractor(ABC):
    """
    Base class for relationship extractors
    """

    def __init__(self, nlp: Optional[spacy.language.Language] = None):
        """
        Initialize relationship extractor

        Args:
            nlp: spaCy language model (optional)
        """
        self.nlp = nlp
        self.relationship_patterns = self._define_patterns()

    @abstractmethod
    def _define_patterns(self) -> List[Dict]:
        """Define relationship patterns"""
        pass

    @abstractmethod
    def extract(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract relationships from doc and entities"""
        pass


class SpatialRelationshipExtractor(BaseRelationshipExtractor):
    """
    Extract spatial relationships: above, below, connected_to, perpendicular, etc.
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Above/Below patterns
            {
                'type': 'ABOVE',
                'pattern': r'(\w+)\s+(?:is\s+)?above\s+(\w+)',
                'description': 'A is above B'
            },
            {
                'type': 'BELOW',
                'pattern': r'(\w+)\s+(?:is\s+)?below\s+(\w+)',
                'description': 'A is below B'
            },

            # Left/Right patterns
            {
                'type': 'LEFT_OF',
                'pattern': r'(\w+)\s+(?:is\s+)?(?:to\s+the\s+)?left\s+of\s+(\w+)',
                'description': 'A is left of B'
            },
            {
                'type': 'RIGHT_OF',
                'pattern': r'(\w+)\s+(?:is\s+)?(?:to\s+the\s+)?right\s+of\s+(\w+)',
                'description': 'A is right of B'
            },

            # Connection patterns
            {
                'type': 'CONNECTED_TO',
                'pattern': r'(\w+)\s+(?:is\s+)?connected\s+to\s+(\w+)',
                'description': 'A is connected to B'
            },
            {
                'type': 'CONNECTED_TO',
                'pattern': r'(\w+)\s+and\s+(\w+)\s+are\s+connected',
                'description': 'A and B are connected'
            },

            # Inside/Contains patterns
            {
                'type': 'INSIDE',
                'pattern': r'(\w+)\s+(?:is\s+)?inside\s+(\w+)',
                'description': 'A is inside B'
            },
            {
                'type': 'CONTAINS',
                'pattern': r'(\w+)\s+contains\s+(\w+)',
                'description': 'A contains B'
            },

            # Perpendicular/Parallel patterns
            {
                'type': 'PERPENDICULAR_TO',
                'pattern': r'(\w+)\s+(?:is\s+)?perpendicular\s+to\s+(\w+)',
                'description': 'A is perpendicular to B'
            },
            {
                'type': 'PARALLEL_TO',
                'pattern': r'(\w+)\s+(?:is\s+)?parallel\s+to\s+(\w+)',
                'description': 'A is parallel to B'
            },
            {
                'type': 'PARALLEL_WITH',
                'pattern': r'(\w+)\s+in\s+parallel\s+with\s+(\w+)',
                'description': 'A in parallel with B'
            },

            # Series pattern
            {
                'type': 'SERIES_WITH',
                'pattern': r'(\w+)\s+in\s+series\s+with\s+(\w+)',
                'description': 'A in series with B'
            },

            # Distance patterns
            {
                'type': 'DISTANCE_FROM',
                'pattern': r'(\w+)\s+is\s+([\d.]+\s*\w+)\s+from\s+(\w+)',
                'description': 'A is X distance from B'
            },
            {
                'type': 'SEPARATED_BY',
                'pattern': r'(\w+)\s+separated\s+by\s+([\d.]+\s*\w+)\s+from\s+(\w+)',
                'description': 'A separated by X from B'
            },

            # On/At patterns
            {
                'type': 'ON',
                'pattern': r'(\w+)\s+(?:is\s+)?on\s+(\w+)',
                'description': 'A is on B'
            },
            {
                'type': 'AT',
                'pattern': r'(\w+)\s+(?:is\s+)?at\s+(\w+)',
                'description': 'A is at B'
            },

            # Between pattern
            {
                'type': 'BETWEEN',
                'pattern': r'(\w+)\s+(?:is\s+)?between\s+(\w+)\s+and\s+(\w+)',
                'description': 'A is between B and C'
            },
        ]

    def extract(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract spatial relationships"""
        relationships = []

        # Method 1: Pattern-based extraction
        pattern_rels = self._extract_with_patterns(doc.text)
        relationships.extend(pattern_rels)

        # Method 2: Dependency-based extraction
        dep_rels = self._extract_from_dependencies(doc)
        relationships.extend(dep_rels)

        # Method 3: Entity proximity
        proximity_rels = self._extract_from_proximity(doc, entities)
        relationships.extend(proximity_rels)

        return self._deduplicate_relationships(relationships)

    def _extract_with_patterns(self, text: str) -> List[Dict]:
        """Extract relationships using regex patterns"""
        relationships = []

        for pattern_def in self.relationship_patterns:
            pattern = pattern_def['pattern']
            rel_type = pattern_def['type']

            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.groups():
                    groups = list(match.groups())

                    relationship = {
                        'type': rel_type,
                        'subject': groups[0] if len(groups) > 0 else None,
                        'target': groups[-1] if len(groups) > 1 else None,
                        'properties': {
                            'confidence': 0.9,
                            'method': 'pattern_match',
                            'description': pattern_def['description']
                        }
                    }

                    # Add middle value for DISTANCE_FROM type relationships
                    if rel_type in ['DISTANCE_FROM', 'SEPARATED_BY'] and len(groups) == 3:
                        relationship['properties']['distance'] = groups[1]

                    # Add third entity for BETWEEN relationships
                    if rel_type == 'BETWEEN' and len(groups) == 3:
                        relationship['properties']['third_entity'] = groups[2]

                    relationships.append(relationship)

        return relationships

    def _extract_from_dependencies(self, doc: Doc) -> List[Dict]:
        """Extract relationships from dependency parse"""
        relationships = []

        for token in doc:
            # Pattern: "A above B" or "A on B"
            if token.dep_ == "prep" and token.text.lower() in ['above', 'below', 'on', 'at', 'in']:
                # Find the subject (head of prep)
                subject = token.head.text

                # Find the object (pobj child of prep)
                for child in token.children:
                    if child.dep_ == "pobj":
                        target = child.text

                        rel_type_map = {
                            'above': 'ABOVE',
                            'below': 'BELOW',
                            'on': 'ON',
                            'at': 'AT',
                            'in': 'INSIDE'
                        }

                        relationship = {
                            'type': rel_type_map.get(token.text.lower(), 'SPATIAL'),
                            'subject': subject,
                            'target': target,
                            'properties': {
                                'confidence': 0.75,
                                'method': 'dependency_parse',
                                'preposition': token.text
                            }
                        }
                        relationships.append(relationship)

        return relationships

    def _extract_from_proximity(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract relationships from entity proximity in text"""
        relationships = []

        # Group entities by sentence
        for sent in doc.sents:
            sent_entities = [
                e for e in entities
                if e['properties']['start'] >= sent.start_char
                and e['properties']['end'] <= sent.end_char
            ]

            # If 2+ entities in same sentence, assume spatial relationship
            if len(sent_entities) >= 2:
                for i in range(len(sent_entities) - 1):
                    relationship = {
                        'type': 'RELATED_TO',
                        'subject': sent_entities[i]['id'],
                        'target': sent_entities[i + 1]['id'],
                        'properties': {
                            'confidence': 0.5,
                            'method': 'proximity',
                            'sentence': sent.text
                        }
                    }
                    relationships.append(relationship)

        return relationships

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships"""
        seen = set()
        unique = []

        for rel in relationships:
            key = (rel['type'], rel.get('subject'), rel.get('target'))
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique


class FunctionalRelationshipExtractor(BaseRelationshipExtractor):
    """
    Extract functional relationships: acts_on, flows_through, depends_on, produces
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Acts on pattern
            {
                'type': 'ACTS_ON',
                'pattern': r'(\w+)\s+acts\s+on\s+(\w+)',
                'description': 'A acts on B'
            },
            {
                'type': 'ACTS_ON',
                'pattern': r'(\w+)\s+(?:force|pressure)\s+on\s+(\w+)',
                'description': 'A exerts force on B'
            },

            # Flows through pattern
            {
                'type': 'FLOWS_THROUGH',
                'pattern': r'(\w+)\s+flows\s+through\s+(\w+)',
                'description': 'A flows through B'
            },
            {
                'type': 'FLOWS_THROUGH',
                'pattern': r'current\s+through\s+(\w+)',
                'description': 'Current flows through A'
            },

            # Depends on pattern
            {
                'type': 'DEPENDS_ON',
                'pattern': r'(\w+)\s+depends\s+on\s+(\w+)',
                'description': 'A depends on B'
            },
            {
                'type': 'DEPENDS_ON',
                'pattern': r'(\w+)\s+(?:is\s+)?(?:a\s+)?function\s+of\s+(\w+)',
                'description': 'A is a function of B'
            },

            # Produces/Creates pattern
            {
                'type': 'PRODUCES',
                'pattern': r'(\w+)\s+produces\s+(\w+)',
                'description': 'A produces B'
            },
            {
                'type': 'PRODUCES',
                'pattern': r'(\w+)\s+creates\s+(\w+)',
                'description': 'A creates B'
            },
            {
                'type': 'PRODUCES',
                'pattern': r'(\w+)\s+generates\s+(\w+)',
                'description': 'A generates B'
            },

            # Applies to pattern
            {
                'type': 'APPLIES_TO',
                'pattern': r'(\w+)\s+(?:is\s+)?applied\s+to\s+(\w+)',
                'description': 'A is applied to B'
            },

            # Affects pattern
            {
                'type': 'AFFECTS',
                'pattern': r'(\w+)\s+affects\s+(\w+)',
                'description': 'A affects B'
            },
            {
                'type': 'AFFECTS',
                'pattern': r'(\w+)\s+influences\s+(\w+)',
                'description': 'A influences B'
            },

            # Transforms pattern
            {
                'type': 'TRANSFORMS',
                'pattern': r'(\w+)\s+transforms\s+into\s+(\w+)',
                'description': 'A transforms into B'
            },
            {
                'type': 'TRANSFORMS',
                'pattern': r'(\w+)\s+converts\s+to\s+(\w+)',
                'description': 'A converts to B'
            },

            # Reacts with pattern (chemistry)
            {
                'type': 'REACTS_WITH',
                'pattern': r'(\w+)\s+reacts\s+with\s+(\w+)',
                'description': 'A reacts with B'
            },
        ]

    def extract(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract functional relationships"""
        relationships = []

        # Pattern-based extraction
        pattern_rels = self._extract_with_patterns(doc.text)
        relationships.extend(pattern_rels)

        # Verb-based extraction
        verb_rels = self._extract_from_verbs(doc)
        relationships.extend(verb_rels)

        return self._deduplicate_relationships(relationships)

    def _extract_with_patterns(self, text: str) -> List[Dict]:
        """Extract relationships using regex patterns"""
        relationships = []

        for pattern_def in self.relationship_patterns:
            pattern = pattern_def['pattern']
            rel_type = pattern_def['type']

            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.groups():
                    groups = list(match.groups())

                    relationship = {
                        'type': rel_type,
                        'subject': groups[0] if len(groups) > 0 else None,
                        'target': groups[1] if len(groups) > 1 else None,
                        'properties': {
                            'confidence': 0.85,
                            'method': 'pattern_match',
                            'description': pattern_def['description']
                        }
                    }
                    relationships.append(relationship)

        return relationships

    def _extract_from_verbs(self, doc: Doc) -> List[Dict]:
        """Extract relationships from verb dependencies"""
        relationships = []

        action_verbs = {
            'acts', 'flows', 'moves', 'pushes', 'pulls', 'applies',
            'produces', 'creates', 'generates', 'transforms', 'converts'
        }

        for token in doc:
            if token.lemma_.lower() in action_verbs:
                # Find subject
                subject = None
                for child in token.children:
                    if child.dep_ in ['nsubj', 'nsubjpass']:
                        subject = child.text
                        break

                # Find object
                obj = None
                for child in token.children:
                    if child.dep_ in ['dobj', 'pobj']:
                        obj = child.text
                        break

                if subject and obj:
                    relationship = {
                        'type': 'FUNCTIONAL',
                        'subject': subject,
                        'target': obj,
                        'properties': {
                            'verb': token.text,
                            'confidence': 0.70,
                            'method': 'verb_dependency'
                        }
                    }
                    relationships.append(relationship)

        return relationships

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []

        for rel in relationships:
            key = (rel['type'], rel.get('subject'), rel.get('target'))
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique


class QuantitativeRelationshipExtractor(BaseRelationshipExtractor):
    """
    Extract quantitative relationships: equals, greater_than, proportional_to
    """

    def _define_patterns(self) -> List[Dict]:
        return [
            # Equals pattern
            {
                'type': 'EQUALS',
                'pattern': r'(\w+)\s*=\s*([\d.]+(?:\s*[a-zA-Zμ²³°]+)?)',
                'description': 'A = B'
            },
            {
                'type': 'EQUALS',
                'pattern': r'(\w+)\s+equals\s+(\w+)',
                'description': 'A equals B'
            },

            # Greater than pattern
            {
                'type': 'GREATER_THAN',
                'pattern': r'(\w+)\s*>\s*(\w+)',
                'description': 'A > B'
            },
            {
                'type': 'GREATER_THAN',
                'pattern': r'(\w+)\s+(?:is\s+)?greater\s+than\s+(\w+)',
                'description': 'A is greater than B'
            },

            # Less than pattern
            {
                'type': 'LESS_THAN',
                'pattern': r'(\w+)\s*<\s*(\w+)',
                'description': 'A < B'
            },
            {
                'type': 'LESS_THAN',
                'pattern': r'(\w+)\s+(?:is\s+)?less\s+than\s+(\w+)',
                'description': 'A is less than B'
            },

            # Proportional to pattern
            {
                'type': 'PROPORTIONAL_TO',
                'pattern': r'(\w+)\s+(?:is\s+)?proportional\s+to\s+(\w+)',
                'description': 'A is proportional to B'
            },
            {
                'type': 'PROPORTIONAL_TO',
                'pattern': r'(\w+)\s*∝\s*(\w+)',
                'description': 'A ∝ B'
            },

            # Inversely proportional pattern
            {
                'type': 'INVERSELY_PROPORTIONAL',
                'pattern': r'(\w+)\s+(?:is\s+)?inversely\s+proportional\s+to\s+(\w+)',
                'description': 'A is inversely proportional to B'
            },

            # Sum/Product patterns
            {
                'type': 'SUM_OF',
                'pattern': r'(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)',
                'description': 'A = B + C'
            },
            {
                'type': 'PRODUCT_OF',
                'pattern': r'(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)',
                'description': 'A = B * C'
            },

            # Ratio pattern
            {
                'type': 'RATIO',
                'pattern': r'(\w+)\s*\/\s*(\w+)\s*=\s*([\d.]+)',
                'description': 'A/B = value'
            },
        ]

    def extract(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract quantitative relationships"""
        relationships = []

        # Pattern-based extraction
        pattern_rels = self._extract_with_patterns(doc.text)
        relationships.extend(pattern_rels)

        # Mathematical equation extraction
        eq_rels = self._extract_equations(doc.text)
        relationships.extend(eq_rels)

        return self._deduplicate_relationships(relationships)

    def _extract_with_patterns(self, text: str) -> List[Dict]:
        """Extract relationships using regex patterns"""
        relationships = []

        for pattern_def in self.relationship_patterns:
            pattern = pattern_def['pattern']
            rel_type = pattern_def['type']

            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.groups():
                    groups = list(match.groups())

                    relationship = {
                        'type': rel_type,
                        'subject': groups[0] if len(groups) > 0 else None,
                        'target': groups[1] if len(groups) > 1 else None,
                        'properties': {
                            'confidence': 0.95,
                            'method': 'pattern_match',
                            'description': pattern_def['description']
                        }
                    }

                    # Add value for EQUALS relationships
                    if rel_type == 'EQUALS' and len(groups) == 2:
                        relationship['properties']['value'] = groups[1]

                    # Add third component for SUM_OF/PRODUCT_OF
                    if rel_type in ['SUM_OF', 'PRODUCT_OF'] and len(groups) == 3:
                        relationship['properties']['components'] = [groups[1], groups[2]]

                    relationships.append(relationship)

        return relationships

    def _extract_equations(self, text: str) -> List[Dict]:
        """Extract mathematical equations"""
        relationships = []

        # Find all equations (variable = expression)
        eq_pattern = r'([a-zA-Z_]\w*)\s*=\s*([\d.+\-*/()a-zA-Z\s]+)'

        for match in re.finditer(eq_pattern, text):
            variable = match.group(1)
            expression = match.group(2).strip()

            relationship = {
                'type': 'EQUATION',
                'subject': variable,
                'target': expression,
                'properties': {
                    'equation': f'{variable} = {expression}',
                    'confidence': 0.90,
                    'method': 'equation_extraction'
                }
            }
            relationships.append(relationship)

        return relationships

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []

        for rel in relationships:
            key = (rel['type'], rel.get('subject'), rel.get('target'))
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique
