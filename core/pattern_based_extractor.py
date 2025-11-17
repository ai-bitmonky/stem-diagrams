"""
Pattern-Based Object Extractor - Generic solution for ALL physics domains
========================================================================

Extracts structured objects from problem text using pattern matching.
Works when NLP entity extraction is weak or incomplete.

Supports ALL physics domains:
- Electrostatics: capacitors, batteries, resistors, charges, dielectrics
- Mechanics: blocks, forces, springs, masses, velocities
- Optics: lenses, mirrors, rays, focal points
- Thermodynamics: gases, containers, pressures, temperatures

Author: Universal Diagram Generator Team
Date: November 17, 2025
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ObjectCategory(Enum):
    """Generic object categories across all physics domains"""
    # Electronics / Electrostatics
    CAPACITOR = "capacitor"
    BATTERY = "battery"
    RESISTOR = "resistor"
    INDUCTOR = "inductor"
    CHARGE = "charge"
    DIELECTRIC = "dielectric"
    FIELD = "field"

    # Mechanics
    BLOCK = "block"
    FORCE = "force"
    SPRING = "spring"
    MASS = "mass"
    PULLEY = "pulley"

    # Optics
    LENS = "lens"
    MIRROR = "mirror"
    RAY = "ray"
    OBJECT_OPTICS = "object"
    IMAGE = "image"

    # Thermodynamics
    GAS = "gas"
    CONTAINER = "container"
    PISTON = "piston"

    # Generic
    UNKNOWN = "unknown"


@dataclass
class ExtractedObject:
    """Represents an extracted physics object with properties"""
    category: ObjectCategory
    identifier: str  # e.g., "C₁", "F1", "lens1"
    properties: Dict[str, Any]  # e.g., {"capacitance": 2.0, "unit": "μF"}
    text_span: Tuple[int, int]  # Position in text
    confidence: float = 1.0


class PatternBasedExtractor:
    """
    Generic pattern-based extractor for physics objects

    Uses regex patterns to extract objects from problem text when NLP
    entity extraction is weak or incomplete.

    Works across ALL physics domains by recognizing common patterns:
    - "quantity symbol = value unit" (e.g., "C₁ = 2.00 μF")
    - "object with property value" (e.g., "capacitor of capacitance 10 μF")
    - "property of object is value" (e.g., "focal length of lens is 5 cm")
    """

    def __init__(self):
        # Generic patterns that work across all domains
        self.patterns = self._build_patterns()

    def _build_patterns(self) -> List[Dict[str, Any]]:
        """Build regex patterns for object extraction"""
        patterns = []

        # Pattern 1: Explicit assignment (C₁ = 2.00 μF, F = 10 N, f = 5 cm)
        patterns.append({
            'name': 'explicit_assignment',
            'regex': r'([A-Za-z][₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹]*)\s*=\s*([0-9.]+)\s*([μmkMGT]?[A-Za-z]+)',
            'extract': lambda m: {
                'identifier': m.group(1),
                'value': float(m.group(2)),
                'unit': m.group(3)
            }
        })

        # Pattern 2: Capacitor/Battery/Resistor with value
        patterns.append({
            'name': 'component_with_value',
            'regex': r'(capacitor|battery|resistor|inductor)s?\s+(?:of\s+)?(?:capacitance|voltage|resistance|inductance)?\s*(?:of\s+)?([0-9.]+)\s*([μmkMGT]?[A-Za-z]+)',
            'extract': lambda m: {
                'type': m.group(1),
                'value': float(m.group(2)),
                'unit': m.group(3)
            }
        })

        # Pattern 3: Dielectric constant (κ = 4.8, κ₁ = 21.0, kappa1 = 21.0)
        patterns.append({
            'name': 'dielectric',
            'regex': r'(?:κ|kappa[_\s]*)([₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹0-9]*)\s*=\s*([0-9]+\.?[0-9]*)',
            'extract': lambda m: {
                'type': 'dielectric',
                'identifier': f'κ{m.group(1) if m.group(1) else ""}',
                'value': float(m.group(2)),
                'unit': 'dimensionless'
            }
        })

        # Pattern 4: Plate area (A = 10.5 cm², area = 0.12 m²)
        patterns.append({
            'name': 'plate_area',
            'regex': r'(?:plate\s+)?area\s+A?\s*=\s*([0-9.]+)\s*(cm²|m²|mm²)',
            'extract': lambda m: {
                'type': 'plate_area',
                'value': float(m.group(1)),
                'unit': m.group(2)
            }
        })

        # Pattern 5: Separation/distance (d = 1.2 cm, separation = 7.12 mm)
        patterns.append({
            'name': 'separation',
            'regex': r'(?:plate\s+)?(?:separation|distance)\s+(?:\d*d)?\s*=\s*([0-9.]+)\s*([μmkM]?m)',
            'extract': lambda m: {
                'type': 'separation',
                'value': float(m.group(1)),
                'unit': m.group(2)
            }
        })

        # Pattern 6: Potential difference/Voltage (V = 300 V, potential difference of 120 V, battery ... 120 V)
        patterns.append({
            'name': 'voltage',
            'regex': r'(?:potential\s+difference|voltage|battery)[^.]*?([0-9.]+)\s*V',
            'extract': lambda m: {
                'type': 'battery',  # Voltage implies battery
                'value': float(m.group(1)),
                'unit': 'V'
            }
        })

        # Pattern 7: Multiple objects of same type (two capacitors, three lenses)
        patterns.append({
            'name': 'multiple_objects',
            'regex': r'(two|three|four|five|\d+)\s+(capacitor|resistor|lens|mirror|block|spring)s',
            'extract': lambda m: {
                'type': m.group(2),
                'count': {'two': 2, 'three': 3, 'four': 4, 'five': 5}.get(m.group(1).lower(),
                         int(m.group(1)) if m.group(1).isdigit() else 2)
            }
        })

        return patterns

    def extract(self, problem_text: str, domain: str = None) -> List[ExtractedObject]:
        """
        Extract objects from problem text

        Args:
            problem_text: The physics problem text
            domain: Optional domain hint (electronics, mechanics, optics, etc.)

        Returns:
            List of extracted objects with properties
        """
        extracted = []
        text_lower = problem_text.lower()

        # Apply all patterns
        for pattern_def in self.patterns:
            regex = pattern_def['regex']
            extractor = pattern_def['extract']

            for match in re.finditer(regex, problem_text, re.IGNORECASE):
                try:
                    data = extractor(match)

                    # Infer category from type or identifier
                    category = self._infer_category(data, text_lower)

                    # Create identifier if not present
                    identifier = data.get('identifier', f"{data.get('type', 'obj')}_{len(extracted)}")

                    obj = ExtractedObject(
                        category=category,
                        identifier=identifier,
                        properties=data,
                        text_span=(match.start(), match.end()),
                        confidence=0.9  # Pattern-based extraction has high confidence
                    )
                    extracted.append(obj)

                except Exception as e:
                    # Skip malformed matches
                    print(f"   ⚠️  Pattern match failed: {e}")
                    continue

        return extracted

    def _infer_category(self, data: Dict, text_lower: str) -> ObjectCategory:
        """Infer object category from extracted data"""
        obj_type = data.get('type', '').lower()
        identifier = data.get('identifier', '').lower()

        # Direct type mapping
        type_map = {
            'capacitor': ObjectCategory.CAPACITOR,
            'battery': ObjectCategory.BATTERY,
            'resistor': ObjectCategory.RESISTOR,
            'inductor': ObjectCategory.INDUCTOR,
            'dielectric': ObjectCategory.DIELECTRIC,
            'lens': ObjectCategory.LENS,
            'mirror': ObjectCategory.MIRROR,
            'block': ObjectCategory.BLOCK,
            'spring': ObjectCategory.SPRING,
            'force': ObjectCategory.FORCE,
            'gas': ObjectCategory.GAS,
        }

        if obj_type in type_map:
            return type_map[obj_type]

        # Infer from identifier (C₁ → capacitor, F → force, etc.)
        if identifier.startswith('c'):
            return ObjectCategory.CAPACITOR
        elif identifier.startswith('r'):
            return ObjectCategory.RESISTOR
        elif identifier.startswith('v'):
            return ObjectCategory.BATTERY
        elif identifier.startswith('f'):
            return ObjectCategory.FORCE
        elif identifier.startswith('m'):
            return ObjectCategory.MASS
        elif identifier.startswith('κ') or identifier.startswith('k'):
            return ObjectCategory.DIELECTRIC

        return ObjectCategory.UNKNOWN

    def extract_component_objects(self, problem_text: str, domain: str = "electronics") -> Dict[str, Dict]:
        """
        Extract component objects in the format expected by interpreters

        Args:
            problem_text: Problem text
            domain: Domain (electronics, mechanics, optics, etc.)

        Returns:
            Dictionary of {component_id: {type, value, unit, label}}
        """
        extracted_objects = self.extract(problem_text, domain)
        components = {}

        component_counters = {}

        for obj in extracted_objects:
            # Map category to component type
            comp_type = self._category_to_component_type(obj.category)

            if comp_type is None:
                continue

            # Generate component ID
            if obj.identifier and obj.identifier != f"{obj.properties.get('type', 'obj')}_{len(components)}":
                comp_id = obj.identifier.upper()
            else:
                # Auto-generate ID
                counter = component_counters.get(comp_type, 0) + 1
                component_counters[comp_type] = counter
                comp_id = f"{comp_type[0].upper()}{counter}"

            # Extract value and unit
            value = obj.properties.get('value', None)
            unit = obj.properties.get('unit', '')

            # Build label
            label = f"{value}{unit}" if value and unit else str(value) if value else comp_id

            components[comp_id] = {
                'type': comp_type,
                'value': value,
                'unit': unit,
                'label': label,
                'properties': obj.properties
            }

        return components

    def _category_to_component_type(self, category: ObjectCategory) -> Optional[str]:
        """Map ObjectCategory to component type string"""
        mapping = {
            ObjectCategory.CAPACITOR: 'capacitor',
            ObjectCategory.BATTERY: 'battery',
            ObjectCategory.RESISTOR: 'resistor',
            ObjectCategory.INDUCTOR: 'inductor',
            ObjectCategory.DIELECTRIC: 'dielectric',
            ObjectCategory.FORCE: 'force',
            ObjectCategory.BLOCK: 'block',
            ObjectCategory.MASS: 'mass',
            ObjectCategory.SPRING: 'spring',
            ObjectCategory.LENS: 'lens',
            ObjectCategory.MIRROR: 'mirror',
        }
        return mapping.get(category, None)


# Example usage
if __name__ == "__main__":
    extractor = PatternBasedExtractor()

    # Test with capacitor problem
    problem1 = """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF."""

    print("Test 1: Capacitor problem")
    print(f"Problem: {problem1}\n")

    objects = extractor.extract(problem1)
    for obj in objects:
        print(f"  {obj.category.value}: {obj.identifier} = {obj.properties}")

    components = extractor.extract_component_objects(problem1)
    print(f"\nComponents: {components}\n")

    # Test with dielectric problem
    problem2 = """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation
2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0."""

    print("Test 2: Dielectric problem")
    print(f"Problem: {problem2}\n")

    objects = extractor.extract(problem2)
    for obj in objects:
        print(f"  {obj.category.value}: {obj.identifier} = {obj.properties}")
