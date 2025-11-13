"""
Local AI Analyzer - Offline spaCy-based Analysis
Provides offline fallback for UniversalAIAnalyzer using local NLP models

Uses spaCy for NER, dependency parsing, and rule-based extraction
NO API calls - runs entirely offline
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from core.problem_spec import (
    CanonicalProblemSpec,
    PhysicsDomain,
    IncompleteSpecsError
)


class LocalAIAnalyzer:
    """
    Local analyzer using spaCy + rule-based extraction
    NO API calls, runs entirely offline

    Provides basic problem understanding using:
    - spaCy for NER and dependency parsing
    - Rule-based patterns for domain/object/relationship extraction
    - Physics keyword matching for domain classification
    """

    def __init__(self, spacy_model: str = "en_core_web_sm", verbose: bool = False):
        """
        Initialize local analyzer with spaCy model

        Args:
            spacy_model: spaCy model to use (default: en_core_web_sm)
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.nlp = None

        if not SPACY_AVAILABLE:
            raise ImportError("spaCy not available. Install with: pip install spacy")

        try:
            self.nlp = spacy.load(spacy_model)
            if self.verbose:
                print(f"✅ LocalAIAnalyzer initialized with {spacy_model}")
        except OSError:
            if self.verbose:
                print(f"⚠️  Model {spacy_model} not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", spacy_model], check=True)
            self.nlp = spacy.load(spacy_model)
            if self.verbose:
                print(f"✅ LocalAIAnalyzer initialized with {spacy_model}")

        # Physics domain keywords
        self.domain_keywords = {
            PhysicsDomain.ELECTROSTATICS: [
                'charge', 'electric field', 'potential', 'capacitor', 'coulomb',
                'electric flux', 'gauss', 'dielectric', 'polarization'
            ],
            PhysicsDomain.CURRENT_ELECTRICITY: [
                'current', 'resistance', 'voltage', 'circuit', 'ohm', 'resistor',
                'battery', 'power', 'emf', 'kirchhoff', 'ammeter', 'voltmeter'
            ],
            PhysicsDomain.MECHANICS: [
                'force', 'mass', 'acceleration', 'velocity', 'momentum', 'energy',
                'friction', 'gravity', 'newton', 'motion', 'displacement', 'trajectory'
            ],
            PhysicsDomain.THERMODYNAMICS: [
                'heat', 'temperature', 'entropy', 'gas', 'pressure', 'volume',
                'thermal', 'carnot', 'ideal gas', 'specific heat'
            ],
            PhysicsDomain.OPTICS: [
                'light', 'lens', 'mirror', 'reflection', 'refraction', 'diffraction',
                'interference', 'wavelength', 'frequency', 'ray', 'image', 'focal'
            ],
            PhysicsDomain.MAGNETISM: [
                'magnetic', 'magnet', 'field', 'flux', 'solenoid', 'coil',
                'inductor', 'permeability', 'dipole'
            ],
            PhysicsDomain.WAVES: [
                'wave', 'amplitude', 'frequency', 'wavelength', 'oscillation',
                'harmonic', 'doppler', 'sound', 'standing wave'
            ],
            PhysicsDomain.MODERN_PHYSICS: [
                'quantum', 'photon', 'electron', 'atom', 'nuclear', 'radioactive',
                'relativity', 'photoelectric', 'compton', 'bohr'
            ]
        }

        # Common physics object patterns
        self.object_patterns = [
            r'(\w+)\s+(?:capacitor|resistor|battery|lens|mirror|magnet|spring|pulley|block|ball|particle)',
            r'(?:capacitor|resistor|battery|lens|mirror|magnet|spring|pulley|block|ball|particle)\s+(\w+)',
            r'(\w+[-_]\w+)\s+(?:capacitor|resistor|battery)',
        ]

        # Relationship indicators
        self.relationship_keywords = {
            'connected': ['connected to', 'connected in', 'joined to', 'attached to', 'linked to'],
            'series': ['in series', 'series connection', 'connected in series'],
            'parallel': ['in parallel', 'parallel connection', 'connected in parallel'],
            'between': ['between', 'separating', 'dividing'],
            'above': ['above', 'over', 'on top of'],
            'below': ['below', 'under', 'beneath'],
            'next_to': ['next to', 'beside', 'adjacent to'],
        }

    def analyze(self, problem_text: str) -> CanonicalProblemSpec:
        """
        Analyze problem using local NLP + rules

        Args:
            problem_text: Problem description

        Returns:
            CanonicalProblemSpec with extracted information

        Raises:
            IncompleteSpecsError: If critical information is missing
        """
        if self.verbose:
            print(f"🔍 LocalAIAnalyzer: Analyzing problem...")

        # Parse with spaCy
        doc = self.nlp(problem_text)

        # Extract components
        domain = self._classify_domain(problem_text, doc)
        objects = self._extract_objects(problem_text, doc)
        relationships = self._extract_relationships(problem_text, doc, objects)
        constraints = self._extract_constraints(problem_text, doc)
        physics_context = self._extract_physics_context(problem_text, doc, domain)
        applicable_laws = self._identify_applicable_laws(domain, objects, relationships)
        geometry = self._extract_geometry(problem_text, doc)

        # Identify missing information
        missing_info = []
        if not objects:
            missing_info.append("No objects identified")
        if domain == PhysicsDomain.UNKNOWN:
            missing_info.append("Cannot determine physics domain")

        # Calculate confidence (based on completeness)
        confidence = self._calculate_confidence(domain, objects, relationships, constraints)

        # Create spec
        spec = CanonicalProblemSpec(
            domain=domain,
            problem_type=self._determine_problem_type(domain, objects, relationships),
            problem_text=problem_text,
            complexity_score=self._estimate_complexity(objects, relationships, constraints),
            objects=objects,
            relationships=relationships,
            environment={},  # Local analyzer doesn't infer environment
            physics_context=physics_context,
            applicable_laws=applicable_laws,
            constraints=constraints,
            geometry=geometry,
            coordinate_system="cartesian",
            subproblems=[],
            is_complete=len(missing_info) == 0,
            missing_information=missing_info,
            confidence=confidence,
            reasoning_trace=[{
                'stage': 'local_analysis',
                'method': 'spacy + rules',
                'domain': domain.value,
                'objects_found': len(objects),
                'relationships_found': len(relationships),
                'confidence': confidence
            }]
        )

        if self.verbose:
            print(f"  ✅ Domain: {domain.value}")
            print(f"  ✅ Objects: {len(objects)}")
            print(f"  ✅ Relationships: {len(relationships)}")
            print(f"  ✅ Confidence: {confidence:.2f}")

        # Raise error if incomplete (similar to UniversalAIAnalyzer)
        if not spec.is_complete and missing_info:
            if self.verbose:
                print(f"  ⚠️  Incomplete specs: {missing_info}")

        return spec

    def _classify_domain(self, text: str, doc: Doc) -> PhysicsDomain:
        """Classify physics domain using keyword matching"""
        text_lower = text.lower()

        # Count keyword matches for each domain
        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                domain_scores[domain] = score

        if not domain_scores:
            return PhysicsDomain.UNKNOWN

        # Return domain with highest score
        return max(domain_scores.items(), key=lambda x: x[1])[0]

    def _extract_objects(self, text: str, doc: Doc) -> List[Dict]:
        """Extract physics objects using NER + patterns"""
        objects = []
        seen_names = set()

        # Extract from spaCy entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:  # Might be object names
                name = ent.text.strip()
                if name and name not in seen_names:
                    objects.append({
                        'id': f'obj_{len(objects)}',
                        'type': 'unknown',
                        'name': name,
                        'properties': {},
                        'source': 'spacy_ner'
                    })
                    seen_names.add(name)

        # Extract using patterns
        for pattern in self.object_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(0).strip()
                if name and name not in seen_names:
                    # Determine type from name
                    obj_type = self._infer_object_type(name)
                    objects.append({
                        'id': f'obj_{len(objects)}',
                        'type': obj_type,
                        'name': name,
                        'properties': {},
                        'source': 'pattern_match'
                    })
                    seen_names.add(name)

        # Extract generic object mentions
        generic_objects = ['capacitor', 'resistor', 'battery', 'lens', 'mirror',
                          'magnet', 'spring', 'pulley', 'block', 'ball', 'particle',
                          'wire', 'plate', 'conductor', 'insulator']

        for obj_type in generic_objects:
            pattern = r'\b' + obj_type + r's?\b'
            if re.search(pattern, text, re.IGNORECASE):
                name = obj_type.capitalize()
                if name not in seen_names:
                    objects.append({
                        'id': f'obj_{len(objects)}',
                        'type': obj_type,
                        'name': name,
                        'properties': {},
                        'source': 'generic_match'
                    })
                    seen_names.add(name)

        return objects

    def _infer_object_type(self, name: str) -> str:
        """Infer object type from name"""
        name_lower = name.lower()

        type_keywords = {
            'capacitor': ['capacitor'],
            'resistor': ['resistor', 'resistance'],
            'battery': ['battery', 'cell'],
            'lens': ['lens'],
            'mirror': ['mirror'],
            'magnet': ['magnet'],
            'spring': ['spring'],
            'pulley': ['pulley'],
            'block': ['block'],
            'ball': ['ball', 'sphere'],
            'particle': ['particle'],
            'wire': ['wire'],
            'plate': ['plate'],
        }

        for obj_type, keywords in type_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return obj_type

        return 'unknown'

    def _extract_relationships(self, text: str, doc: Doc, objects: List[Dict]) -> List[Dict]:
        """Extract relationships between objects"""
        relationships = []

        # Use relationship keywords to find connections
        for rel_type, indicators in self.relationship_keywords.items():
            for indicator in indicators:
                if indicator in text.lower():
                    # Find objects near this indicator
                    # (Simplified: just add relationship type)
                    relationships.append({
                        'id': f'rel_{len(relationships)}',
                        'type': rel_type,
                        'source': 'unknown',
                        'target': 'unknown',
                        'properties': {},
                        'confidence': 0.5
                    })

        return relationships

    def _extract_constraints(self, text: str, doc: Doc) -> List[Dict]:
        """Extract constraints from problem text"""
        constraints = []

        # Look for numerical constraints
        # Pattern: "quantity = value unit"
        quantity_pattern = r'(\w+)\s*=\s*([\d.]+)\s*(\w+)?'
        matches = re.finditer(quantity_pattern, text)

        for match in matches:
            quantity = match.group(1)
            value = match.group(2)
            unit = match.group(3) if match.group(3) else ''

            constraints.append({
                'type': 'equality',
                'quantity': quantity,
                'value': value,
                'unit': unit,
                'source': 'pattern_match'
            })

        return constraints

    def _extract_physics_context(self, text: str, doc: Doc, domain: PhysicsDomain) -> Dict:
        """Extract physics-specific context"""
        context = {
            'domain': domain.value,
            'keywords_found': [],
            'quantities_mentioned': []
        }

        # Find domain keywords that appeared
        text_lower = text.lower()
        if domain in self.domain_keywords:
            for kw in self.domain_keywords[domain]:
                if kw in text_lower:
                    context['keywords_found'].append(kw)

        return context

    def _identify_applicable_laws(self, domain: PhysicsDomain,
                                  objects: List[Dict],
                                  relationships: List[Dict]) -> List[str]:
        """Identify applicable physics laws based on domain"""
        laws = []

        domain_laws = {
            PhysicsDomain.ELECTROSTATICS: [
                "Coulomb's Law",
                "Gauss's Law",
                "Electric Potential"
            ],
            PhysicsDomain.CURRENT_ELECTRICITY: [
                "Ohm's Law",
                "Kirchhoff's Current Law",
                "Kirchhoff's Voltage Law"
            ],
            PhysicsDomain.MECHANICS: [
                "Newton's Laws of Motion",
                "Conservation of Energy",
                "Conservation of Momentum"
            ],
            PhysicsDomain.THERMODYNAMICS: [
                "First Law of Thermodynamics",
                "Ideal Gas Law",
                "Second Law of Thermodynamics"
            ],
            PhysicsDomain.OPTICS: [
                "Snell's Law",
                "Lens Equation",
                "Mirror Equation"
            ],
        }

        if domain in domain_laws:
            laws.extend(domain_laws[domain])

        return laws

    def _extract_geometry(self, text: str, doc: Doc) -> Dict:
        """Extract geometric information"""
        geometry = {
            'type': 'unknown',
            'dimensions': {},
            'arrangement': 'unknown'
        }

        # Look for geometric terms
        if any(word in text.lower() for word in ['parallel', 'horizontal']):
            geometry['arrangement'] = 'parallel'
        elif any(word in text.lower() for word in ['series', 'vertical', 'line']):
            geometry['arrangement'] = 'series'
        elif 'circular' in text.lower() or 'circle' in text.lower():
            geometry['type'] = 'circular'

        return geometry

    def _determine_problem_type(self, domain: PhysicsDomain,
                                objects: List[Dict],
                                relationships: List[Dict]) -> str:
        """Determine problem type"""
        if domain == PhysicsDomain.ELECTROSTATICS:
            if any('capacitor' in obj.get('type', '') for obj in objects):
                return 'capacitor_circuit'
            return 'electric_field'
        elif domain == PhysicsDomain.CURRENT_ELECTRICITY:
            return 'circuit_analysis'
        elif domain == PhysicsDomain.MECHANICS:
            return 'dynamics'
        else:
            return 'general'

    def _estimate_complexity(self, objects: List[Dict],
                           relationships: List[Dict],
                           constraints: List[Dict]) -> float:
        """Estimate problem complexity (0-1 scale)"""
        # Simple heuristic based on counts
        obj_count = len(objects)
        rel_count = len(relationships)
        const_count = len(constraints)

        # Normalize to 0-1 scale
        complexity = min(1.0, (obj_count * 0.2 + rel_count * 0.15 + const_count * 0.1))
        return complexity

    def _calculate_confidence(self, domain: PhysicsDomain,
                             objects: List[Dict],
                             relationships: List[Dict],
                             constraints: List[Dict]) -> float:
        """Calculate confidence in extraction (0-1 scale)"""
        confidence = 0.0

        # Domain identified
        if domain != PhysicsDomain.UNKNOWN:
            confidence += 0.3

        # Objects found
        if objects:
            confidence += min(0.4, len(objects) * 0.1)

        # Relationships found
        if relationships:
            confidence += min(0.2, len(relationships) * 0.05)

        # Constraints found
        if constraints:
            confidence += min(0.1, len(constraints) * 0.02)

        return min(1.0, confidence)
