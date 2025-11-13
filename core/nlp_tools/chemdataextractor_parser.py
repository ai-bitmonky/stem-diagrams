#!/usr/bin/env python3
"""
ChemDataExtractor Parser for Chemistry Diagram Generation

Extracts:
- Chemical formulas (H₂O, NaCl, C₆H₁₂O₆)
- Chemical reactions (A + B → C)
- Chemical properties (melting point, boiling point, pH)
- Chemical entities (acid, base, salt, catalyst)
- Stoichiometric coefficients
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import re
from enum import Enum


class ChemicalEntityType(Enum):
    """Types of chemical entities"""
    COMPOUND = "compound"
    ELEMENT = "element"
    ION = "ion"
    FUNCTIONAL_GROUP = "functional_group"
    REACTION = "reaction"
    PROPERTY = "property"


@dataclass
class ChemicalEntity:
    """Represents a chemical entity extracted from text"""
    text: str
    type: ChemicalEntityType
    formula: Optional[str] = None
    properties: Dict[str, any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0


@dataclass
class ChemicalReaction:
    """Represents a chemical reaction"""
    reactants: List[Tuple[float, str]]  # (coefficient, formula)
    products: List[Tuple[float, str]]
    reaction_type: Optional[str] = None
    conditions: List[str] = field(default_factory=list)


@dataclass
class ChemDataExtractorResult:
    """Result from ChemDataExtractor parsing"""
    entities: List[ChemicalEntity]
    reactions: List[ChemicalReaction]
    formulas: List[str]
    properties: Dict[str, any]
    raw_text: str


class ChemDataExtractorParser:
    """
    Chemistry-specific NLP parser using pattern matching and chemical rules.

    This is a lightweight implementation that doesn't require the full ChemDataExtractor library.
    For production use with more complex chemistry problems, consider installing the full library.
    """

    def __init__(self):
        """Initialize the chemistry parser"""
        # Common element symbols
        self.elements = {
            'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
            'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
            'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
            'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
            'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
            'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
            'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
            'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
        }

        # Chemical formula pattern (e.g., H2O, CaCO3, C6H12O6)
        self.formula_pattern = re.compile(
            r'\b([A-Z][a-z]?(?:[₀-₉0-9]+)?(?:[A-Z][a-z]?[₀-₉0-9]*)*)\b'
        )

        # Reaction arrow patterns
        self.reaction_arrows = [
            '→', '⟶', '⇒', '⟹', '-->', '==>', '->', '=>'
        ]

        # Chemical property keywords
        self.property_keywords = {
            'melting point': 'melting_point',
            'boiling point': 'boiling_point',
            'density': 'density',
            'molecular weight': 'molecular_weight',
            'molar mass': 'molar_mass',
            'pH': 'pH',
            'pKa': 'pKa',
            'solubility': 'solubility',
            'concentration': 'concentration',
            'molarity': 'molarity',
            'molality': 'molality',
        }

        # Reaction type keywords
        self.reaction_types = {
            'combustion', 'synthesis', 'decomposition', 'single replacement',
            'double replacement', 'neutralization', 'oxidation', 'reduction',
            'redox', 'acid-base', 'precipitation', 'endothermic', 'exothermic'
        }

        # Chemical entity keywords
        self.chemical_keywords = {
            'acid', 'base', 'salt', 'catalyst', 'solvent', 'solute',
            'reactant', 'product', 'precipitate', 'solution', 'mixture',
            'compound', 'element', 'molecule', 'ion', 'cation', 'anion'
        }

    def parse(self, text: str) -> ChemDataExtractorResult:
        """
        Parse chemical text and extract entities, reactions, formulas, and properties.

        Args:
            text: Chemistry problem text

        Returns:
            ChemDataExtractorResult with extracted information
        """
        entities = self._extract_entities(text)
        reactions = self._extract_reactions(text)
        formulas = self._extract_formulas(text)
        properties = self._extract_properties(text)

        return ChemDataExtractorResult(
            entities=entities,
            reactions=reactions,
            formulas=formulas,
            properties=properties,
            raw_text=text
        )

    def _extract_formulas(self, text: str) -> List[str]:
        """Extract chemical formulas from text"""
        formulas = []

        # Convert subscript numbers to regular numbers for processing
        text_normalized = self._normalize_subscripts(text)

        # Find all potential formulas
        for match in self.formula_pattern.finditer(text_normalized):
            formula = match.group(1)

            # Validate formula (must contain at least one element symbol)
            if self._is_valid_formula(formula):
                # Convert back to subscript notation
                formula_subscript = self._to_subscript(formula)
                if formula_subscript not in formulas:
                    formulas.append(formula_subscript)

        return formulas

    def _extract_entities(self, text: str) -> List[ChemicalEntity]:
        """Extract chemical entities from text"""
        entities = []

        # Extract formulas as compound entities
        formulas = self._extract_formulas(text)
        for formula in formulas:
            entity = ChemicalEntity(
                text=formula,
                type=ChemicalEntityType.COMPOUND,
                formula=formula
            )
            entities.append(entity)

        # Extract chemical keywords
        text_lower = text.lower()
        for keyword in self.chemical_keywords:
            if keyword in text_lower:
                entity = ChemicalEntity(
                    text=keyword,
                    type=ChemicalEntityType.COMPOUND,
                    start_char=text_lower.index(keyword),
                    end_char=text_lower.index(keyword) + len(keyword)
                )
                entities.append(entity)

        return entities

    def _extract_reactions(self, text: str) -> List[ChemicalReaction]:
        """Extract chemical reactions from text"""
        reactions = []

        # Look for reaction arrows
        for arrow in self.reaction_arrows:
            if arrow in text:
                # Split text by arrow
                parts = text.split(arrow)
                if len(parts) >= 2:
                    reactants_text = parts[0]
                    products_text = parts[1]

                    # Extract formulas from each side
                    reactants = self._parse_reaction_side(reactants_text)
                    products = self._parse_reaction_side(products_text)

                    # Determine reaction type
                    reaction_type = self._determine_reaction_type(text)

                    reaction = ChemicalReaction(
                        reactants=reactants,
                        products=products,
                        reaction_type=reaction_type
                    )
                    reactions.append(reaction)

        return reactions

    def _extract_properties(self, text: str) -> Dict[str, any]:
        """Extract chemical properties from text"""
        properties = {}

        text_lower = text.lower()

        # Extract numerical properties
        for keyword, prop_name in self.property_keywords.items():
            if keyword in text_lower:
                # Look for number near keyword
                pattern = rf'{keyword}\s*[:=]?\s*([-+]?\d+\.?\d*)\s*([a-zA-Z/°]+)?'
                match = re.search(pattern, text_lower)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) if match.group(2) else None
                    properties[prop_name] = {
                        'value': value,
                        'unit': unit
                    }

        return properties

    def _parse_reaction_side(self, text: str) -> List[Tuple[float, str]]:
        """Parse one side of a chemical reaction (reactants or products)"""
        components = []

        # Split by + sign
        parts = [p.strip() for p in text.split('+')]

        for part in parts:
            # Look for coefficient (number at start)
            coef_match = re.match(r'^(\d+\.?\d*)\s*', part)
            if coef_match:
                coefficient = float(coef_match.group(1))
                formula_part = part[coef_match.end():].strip()
            else:
                coefficient = 1.0
                formula_part = part.strip()

            # Extract formula
            formulas = self._extract_formulas(formula_part)
            if formulas:
                components.append((coefficient, formulas[0]))

        return components

    def _determine_reaction_type(self, text: str) -> Optional[str]:
        """Determine the type of chemical reaction"""
        text_lower = text.lower()

        for reaction_type in self.reaction_types:
            if reaction_type in text_lower:
                return reaction_type

        return None

    def _is_valid_formula(self, formula: str) -> bool:
        """Check if a string is a valid chemical formula"""
        if not formula:
            return False

        # Must start with capital letter (element symbol)
        if not formula[0].isupper():
            return False

        # Must contain at least one known element
        # Extract all element symbols
        elements_in_formula = re.findall(r'[A-Z][a-z]?', formula)
        return any(elem in self.elements for elem in elements_in_formula)

    def _normalize_subscripts(self, text: str) -> str:
        """Convert subscript numbers to regular numbers"""
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
        }

        for sub, normal in subscript_map.items():
            text = text.replace(sub, normal)

        return text

    def _to_subscript(self, text: str) -> str:
        """Convert regular numbers in formulas to subscripts"""
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }

        result = []
        for i, char in enumerate(text):
            # Only convert digits that come after letters
            if char.isdigit() and i > 0 and text[i-1].isalpha():
                result.append(subscript_map.get(char, char))
            else:
                result.append(char)

        return ''.join(result)


# Convenience function for direct usage
def extract_chemistry(text: str) -> ChemDataExtractorResult:
    """
    Convenience function to extract chemistry information from text.

    Args:
        text: Chemistry problem text

    Returns:
        ChemDataExtractorResult with extracted information
    """
    parser = ChemDataExtractorParser()
    return parser.parse(text)


if __name__ == '__main__':
    # Test the parser
    test_text = """
    Consider the reaction: 2H₂ + O₂ → 2H₂O
    This is a combustion reaction with a heat of reaction of -285.8 kJ/mol.
    The reactants are hydrogen gas (H₂) and oxygen gas (O₂).
    The product is water (H₂O) with a boiling point of 100°C.
    A catalyst such as platinum (Pt) can be used to increase the reaction rate.
    """

    parser = ChemDataExtractorParser()
    result = parser.parse(test_text)

    print("=" * 60)
    print("ChemDataExtractor Parser Test")
    print("=" * 60)
    print(f"\nFormulas found: {result.formulas}")
    print(f"\nReactions found: {len(result.reactions)}")
    for i, rxn in enumerate(result.reactions):
        print(f"\nReaction {i+1}:")
        print(f"  Reactants: {rxn.reactants}")
        print(f"  Products: {rxn.products}")
        print(f"  Type: {rxn.reaction_type}")

    print(f"\nEntities found: {len(result.entities)}")
    for entity in result.entities[:5]:
        print(f"  - {entity.text} ({entity.type.value})")

    print(f"\nProperties found: {result.properties}")
    print("=" * 60)
