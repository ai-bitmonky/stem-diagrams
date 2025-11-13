#!/usr/bin/env python3
"""
MathBERT Extractor for Mathematical Expression Understanding

Extracts and understands:
- Mathematical expressions (equations, formulas)
- Mathematical variables and constants
- Mathematical operations and relationships
- Units and numerical values
- Mathematical entities (vectors, matrices, functions)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
import re
from enum import Enum


class MathEntityType(Enum):
    """Types of mathematical entities"""
    VARIABLE = "variable"
    CONSTANT = "constant"
    EQUATION = "equation"
    EXPRESSION = "expression"
    FUNCTION = "function"
    OPERATOR = "operator"
    UNIT = "unit"
    NUMBER = "number"
    VECTOR = "vector"
    MATRIX = "matrix"


@dataclass
class MathEntity:
    """Represents a mathematical entity"""
    text: str
    type: MathEntityType
    latex: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    properties: Dict[str, any] = field(default_factory=dict)


@dataclass
class MathExpression:
    """Represents a mathematical expression or equation"""
    text: str
    latex: Optional[str] = None
    variables: List[str] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)
    is_equation: bool = False


@dataclass
class MathBERTResult:
    """Result from MathBERT extraction"""
    entities: List[MathEntity]
    expressions: List[MathExpression]
    variables: Set[str]
    constants: Dict[str, float]
    units: Dict[str, str]
    raw_text: str


class MathBERTExtractor:
    """
    Mathematical expression extractor using pattern matching and mathematical rules.

    This is a lightweight implementation that provides core functionality.
    For production use with complex LaTeX expressions, consider using a full
    MathBERT model from Hugging Face.
    """

    def __init__(self):
        """Initialize the math extractor"""
        # Common mathematical variables (Greek letters)
        self.greek_letters = {
            'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ',
            'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω',
            'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ',
            'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω'
        }

        # Mathematical constants
        self.constants = {
            'π': 3.14159265359,
            'e': 2.71828182846,
            'c': 299792458,  # speed of light
            'h': 6.62607015e-34,  # Planck's constant
            'k': 1.380649e-23,  # Boltzmann constant
            'G': 6.67430e-11,  # Gravitational constant
            'ε₀': 8.854187817e-12,  # Permittivity of free space
            'μ₀': 1.25663706212e-6,  # Permeability of free space
            'g': 9.81,  # Acceleration due to gravity
        }

        # Mathematical operators
        self.operators = {
            '+', '-', '×', '÷', '/', '*', '=', '≠', '<', '>', '≤', '≥',
            '∫', '∑', '∏', '√', '∂', '∇', '∆', '±', '∓'
        }

        # Common units
        self.units = {
            # Length
            'm', 'cm', 'mm', 'km', 'ft', 'in', 'yd', 'mi',
            # Mass
            'kg', 'g', 'mg', 'lb', 'oz',
            # Time
            's', 'ms', 'μs', 'ns', 'min', 'h', 'hr', 'day',
            # Force
            'N', 'kN', 'lbf',
            # Energy
            'J', 'kJ', 'MJ', 'eV', 'keV', 'MeV', 'GeV', 'cal', 'kcal', 'BTU',
            # Power
            'W', 'kW', 'MW', 'hp',
            # Voltage
            'V', 'kV', 'mV',
            # Current
            'A', 'mA', 'μA',
            # Resistance
            'Ω', 'kΩ', 'MΩ',
            # Capacitance
            'F', 'μF', 'nF', 'pF',
            # Frequency
            'Hz', 'kHz', 'MHz', 'GHz',
            # Temperature
            'K', '°C', '°F',
            # Angle
            'rad', 'deg', '°',
            # Area
            'm²', 'cm²', 'mm²',
            # Volume
            'm³', 'L', 'mL', 'cm³',
            # Velocity
            'm/s', 'km/h', 'mph',
            # Acceleration
            'm/s²',
        }

        # Pattern for equations (contains =)
        self.equation_pattern = re.compile(
            r'([A-Za-zα-ωΑ-Ω₀-₉⁰-⁹]+\s*[+\-×÷*/^²³]*\s*)+\s*=\s*([A-Za-zα-ωΑ-Ω₀-₉⁰-⁹\s+\-×÷*/^²³()]+)'
        )

        # Pattern for numerical values with units
        self.value_unit_pattern = re.compile(
            r'([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*([a-zA-ZΩ°μ]+/?[a-zA-Z²³]*)'
        )

        # Pattern for single variable assignments
        self.assignment_pattern = re.compile(
            r'([A-Za-zα-ωΑ-Ω][₀-₉⁰-⁹]*)\s*=\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*([a-zA-ZΩ°μ]+/?[a-zA-Z²³]*)?'
        )

    def extract(self, text: str) -> MathBERTResult:
        """
        Extract mathematical entities and expressions from text.

        Args:
            text: Problem text containing mathematical expressions

        Returns:
            MathBERTResult with extracted mathematical information
        """
        entities = self._extract_entities(text)
        expressions = self._extract_expressions(text)
        variables = self._extract_variables(text)
        constants = self._extract_constant_values(text)
        units = self._extract_units(text)

        return MathBERTResult(
            entities=entities,
            expressions=expressions,
            variables=variables,
            constants=constants,
            units=units,
            raw_text=text
        )

    def _extract_entities(self, text: str) -> List[MathEntity]:
        """Extract all mathematical entities"""
        entities = []

        # Extract numerical values with units
        for match in self.value_unit_pattern.finditer(text):
            value = float(match.group(1))
            unit = match.group(2)

            entity = MathEntity(
                text=match.group(0),
                type=MathEntityType.NUMBER,
                value=value,
                unit=unit if unit in self.units else None
            )
            entities.append(entity)

        # Extract variable assignments
        for match in self.assignment_pattern.finditer(text):
            var_name = match.group(1)
            value = float(match.group(2))
            unit = match.group(3) if match.group(3) else None

            entity = MathEntity(
                text=match.group(0),
                type=MathEntityType.VARIABLE,
                value=value,
                unit=unit,
                properties={'name': var_name}
            )
            entities.append(entity)

        # Extract Greek letters as variables
        for char in text:
            if char in self.greek_letters:
                entity = MathEntity(
                    text=char,
                    type=MathEntityType.VARIABLE
                )
                if entity not in entities:
                    entities.append(entity)

        return entities

    def _extract_expressions(self, text: str) -> List[MathExpression]:
        """Extract mathematical expressions and equations"""
        expressions = []

        # Find equations (contains =)
        for match in self.equation_pattern.finditer(text):
            expr_text = match.group(0)

            # Extract components
            variables = self._find_variables_in_expr(expr_text)
            constants = self._find_constants_in_expr(expr_text)
            operators = self._find_operators_in_expr(expr_text)

            expression = MathExpression(
                text=expr_text,
                variables=variables,
                constants=constants,
                operators=operators,
                is_equation=True
            )
            expressions.append(expression)

        return expressions

    def _extract_variables(self, text: str) -> Set[str]:
        """Extract all variable names"""
        variables = set()

        # Single letter variables (A-Z, a-z)
        for match in re.finditer(r'\b([A-Za-z])[₀-₉⁰-⁹]*\b', text):
            var = match.group(1)
            # Exclude common words
            if var not in {'a', 'A', 'I'}:
                variables.add(var)

        # Greek letters
        for char in text:
            if char in self.greek_letters:
                variables.add(char)

        # Subscripted variables (e.g., V₁, F_2)
        for match in re.finditer(r'([A-Za-zα-ωΑ-Ω])[₀-₉⁰-⁹_]+', text):
            variables.add(match.group(0))

        return variables

    def _extract_constant_values(self, text: str) -> Dict[str, float]:
        """Extract constant values from assignments"""
        constants = {}

        # Look for variable = value patterns
        for match in self.assignment_pattern.finditer(text):
            var_name = match.group(1)
            value = float(match.group(2))
            constants[var_name] = value

        # Add known mathematical constants if mentioned
        for const_name, const_value in self.constants.items():
            if const_name in text:
                constants[const_name] = const_value

        return constants

    def _extract_units(self, text: str) -> Dict[str, str]:
        """Extract units associated with variables"""
        units_dict = {}

        # Look for variable = value unit patterns
        for match in self.assignment_pattern.finditer(text):
            var_name = match.group(1)
            unit = match.group(3)
            if unit and unit in self.units:
                units_dict[var_name] = unit

        return units_dict

    def _find_variables_in_expr(self, expr: str) -> List[str]:
        """Find all variables in an expression"""
        variables = []

        # Single letter variables
        for match in re.finditer(r'([A-Za-zα-ωΑ-Ω])[₀-₉⁰-⁹]*', expr):
            var = match.group(0)
            if var not in variables:
                variables.append(var)

        return variables

    def _find_constants_in_expr(self, expr: str) -> List[str]:
        """Find all constants in an expression"""
        constants = []

        # Look for known mathematical constants
        for const_name in self.constants:
            if const_name in expr and const_name not in constants:
                constants.append(const_name)

        # Look for numerical constants
        for match in re.finditer(r'([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)', expr):
            const = match.group(1)
            if const not in constants:
                constants.append(const)

        return constants

    def _find_operators_in_expr(self, expr: str) -> List[str]:
        """Find all operators in an expression"""
        operators = []

        for op in self.operators:
            if op in expr and op not in operators:
                operators.append(op)

        return operators

    def embed_expression(self, expression: str) -> List[float]:
        """
        Generate embedding for mathematical expression.

        This is a placeholder for actual MathBERT embedding.
        For production, use the real MathBERT model from Hugging Face.

        Args:
            expression: Mathematical expression text

        Returns:
            Embedding vector (currently returns dummy vector)
        """
        # This would use actual MathBERT model:
        # from transformers import AutoTokenizer, AutoModel
        # tokenizer = AutoTokenizer.from_pretrained("tbs17/MathBERT")
        # model = AutoModel.from_pretrained("tbs17/MathBERT")
        # ...

        # For now, return a simple feature vector based on expression characteristics
        features = [
            float(len(expression)),  # Length
            float(sum(1 for c in expression if c.isdigit())),  # Number count
            float(sum(1 for c in expression if c in self.operators)),  # Operator count
            float(sum(1 for c in expression if c in self.greek_letters)),  # Greek letters
        ]

        return features


# Convenience function for direct usage
def extract_math(text: str) -> MathBERTResult:
    """
    Convenience function to extract mathematical information from text.

    Args:
        text: Problem text containing mathematical expressions

    Returns:
        MathBERTResult with extracted information
    """
    extractor = MathBERTExtractor()
    return extractor.extract(text)


if __name__ == '__main__':
    # Test the extractor
    test_text = """
    A block of mass m = 2.5 kg is placed on an inclined plane at angle θ = 30°.
    The coefficient of friction μ = 0.25.
    The gravitational acceleration is g = 9.81 m/s².

    The force equation is: F = ma
    The potential energy is: PE = mgh
    The kinetic energy is: KE = ½mv²

    Calculate the acceleration a down the plane.
    """

    extractor = MathBERTExtractor()
    result = extractor.extract(test_text)

    print("=" * 60)
    print("MathBERT Extractor Test")
    print("=" * 60)

    print(f"\nVariables found: {result.variables}")
    print(f"\nConstants: {result.constants}")
    print(f"\nUnits: {result.units}")

    print(f"\nEntities found: {len(result.entities)}")
    for entity in result.entities[:10]:
        print(f"  - {entity.text} ({entity.type.value})", end="")
        if entity.value:
            print(f" = {entity.value}", end="")
        if entity.unit:
            print(f" {entity.unit}", end="")
        print()

    print(f"\nExpressions found: {len(result.expressions)}")
    for i, expr in enumerate(result.expressions):
        print(f"\nExpression {i+1}: {expr.text}")
        print(f"  Variables: {expr.variables}")
        print(f"  Is equation: {expr.is_equation}")

    print("=" * 60)
