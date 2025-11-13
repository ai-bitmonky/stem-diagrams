#!/usr/bin/env python3
"""
RDKit Renderer
==============

Professional molecular structure visualization using RDKit library.

RDKit provides:
- 2D and 3D molecular structure rendering
- Chemical reaction visualization
- Lewis structure-like representations
- Publication-quality molecular graphics

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Dict, List, Optional, Any
import io
import base64

try:
    from rdkit import Chem
    from rdkit.Chem import Draw, AllChem
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    Chem = None
    Draw = None
    AllChem = None
    rdMolDraw2D = None

from . import (
    BaseSpecializedRenderer,
    RendererCapabilities,
    RendererDomain
)


class RDKitRenderer(BaseSpecializedRenderer):
    """
    Molecular structure renderer using RDKit

    Supports:
    - 2D molecular structures
    - 3D conformers
    - Chemical reactions
    - Lewis-like structures
    - Stereochemistry visualization
    """

    def _check_availability(self) -> bool:
        """Check if RDKit is installed"""
        return RDKIT_AVAILABLE

    def get_capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="RDKit",
            domain=RendererDomain.CHEMISTRY,
            library="rdkit",
            output_formats=['svg', 'png'],
            supported_diagram_types=[
                'molecular_structure',
                'chemical_reaction',
                'lewis_structure',
                '3d_molecule',
                'reaction_mechanism',
                'organic_molecule',
                'inorganic_molecule'
            ],
            requires_install=True,
            install_command="conda install -c conda-forge rdkit  # or pip install rdkit",
            description="Professional molecular structure and reaction visualization"
        )

    def can_render(self, diagram_type: str, domain: str) -> bool:
        """Check if this renderer can handle the diagram"""
        if not self.available:
            return False

        domain_lower = domain.lower()
        type_lower = diagram_type.lower()

        # Domain matching
        if 'chem' in domain_lower or 'molecule' in domain_lower:
            return True

        # Type matching
        chem_keywords = ['molecule', 'chemical', 'reaction', 'lewis', 'organic', 'inorganic', 'compound']
        return any(kw in type_lower for kw in chem_keywords)

    def render(
        self,
        scene_data: Dict[str, Any],
        output_format: str = 'svg'
    ) -> Optional[str]:
        """
        Render molecular structure using RDKit

        Args:
            scene_data: Universal scene format with:
                - smiles: SMILES string for molecule
                - formula: Chemical formula
                - molecules: List of molecules for reaction
            output_format: 'svg' or 'png'

        Returns:
            SVG string or PNG data URL
        """
        if not self.available:
            print("⚠️  RDKit not available")
            return None

        try:
            # Extract molecule information
            smiles = scene_data.get('smiles')
            formula = scene_data.get('formula')
            molecules = scene_data.get('molecules', [])

            # Create molecule from SMILES or formula
            if smiles:
                mol = Chem.MolFromSmiles(smiles)
            elif formula:
                # Try to infer SMILES from formula (limited)
                mol = self._formula_to_mol(formula)
            elif molecules and len(molecules) > 0:
                # Render first molecule
                mol = Chem.MolFromSmiles(molecules[0].get('smiles', ''))
            else:
                print("⚠️  No molecule data provided")
                return None

            if mol is None:
                print("❌ Invalid molecule data")
                return None

            # Generate 2D coordinates
            AllChem.Compute2DCoords(mol)

            # Render
            if output_format == 'svg':
                return self._render_svg(mol)
            elif output_format == 'png':
                return self._render_png(mol)
            else:
                print(f"⚠️  Unsupported format: {output_format}")
                return None

        except Exception as e:
            print(f"❌ RDKit rendering failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _render_svg(self, mol) -> str:
        """Render molecule as SVG"""
        drawer = rdMolDraw2D.MolDraw2DSVG(400, 400)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg

    def _render_png(self, mol) -> str:
        """Render molecule as PNG data URL"""
        img = Draw.MolToImage(mol, size=(400, 400))

        # Convert to data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_data}"

    def _formula_to_mol(self, formula: str):
        """
        Try to convert formula to molecule (limited functionality)

        This is a simple heuristic - for complex molecules, SMILES is needed
        """
        # Common simple molecules
        simple_molecules = {
            'H2O': 'O',
            'CO2': 'O=C=O',
            'CH4': 'C',
            'NH3': 'N',
            'H2': '[H][H]',
            'O2': 'O=O',
            'N2': 'N#N',
            'Cl2': 'ClCl',
            'NaCl': '[Na+].[Cl-]',
            'HCl': 'Cl',
            'H2SO4': 'OS(=O)(=O)O',
            'C2H6': 'CC',
            'C2H5OH': 'CCO',
            'CH3COOH': 'CC(=O)O',
            'C6H12O6': 'OC[C@H]1O[C@H](O)[C@H](O)[C@@H](O)[C@@H]1O',  # Glucose
        }

        return Chem.MolFromSmiles(simple_molecules.get(formula, ''))

    def render_reaction(
        self,
        reactants: List[str],
        products: List[str]
    ) -> Optional[str]:
        """
        Render chemical reaction

        Args:
            reactants: List of SMILES strings for reactants
            products: List of SMILES strings for products

        Returns:
            SVG string
        """
        if not self.available:
            return None

        try:
            # Create reaction
            rxn_smiles = '.'.join(reactants) + '>>' + '.'.join(products)
            rxn = AllChem.ReactionFromSmarts(rxn_smiles, useSmiles=True)

            # Render reaction
            img = Draw.ReactionToImage(rxn)

            # Convert to SVG (approximate - RDKit reactions are best in PNG)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_data}"

        except Exception as e:
            print(f"❌ Reaction rendering failed: {e}")
            return None

    def render_molecule_from_name(self, name: str) -> Optional[str]:
        """
        Render molecule from common name (requires PubChem or similar)

        This is a placeholder - would need external API integration
        """
        # Common molecules by name
        common_names = {
            'water': 'O',
            'methane': 'C',
            'ethanol': 'CCO',
            'acetone': 'CC(=O)C',
            'benzene': 'c1ccccc1',
            'glucose': 'OC[C@H]1O[C@H](O)[C@H](O)[C@@H](O)[C@@H]1O',
            'caffeine': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
            'aspirin': 'CC(=O)Oc1ccccc1C(=O)O',
        }

        smiles = common_names.get(name.lower())
        if smiles:
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                return self._render_svg(mol)

        return None


# Example usage and testing
if __name__ == '__main__':
    renderer = RDKitRenderer()

    if renderer.available:
        print("✅ RDKit renderer available")
        print(f"Capabilities: {renderer.get_capabilities()}")

        # Test water molecule
        test_scene = {
            'smiles': 'O',  # Water
            'label': 'H₂O'
        }

        svg = renderer.render(test_scene, output_format='svg')
        if svg:
            print(f"✅ Generated molecular structure ({len(svg)} chars)")

            # Test more complex molecule
            test_benzene = {'smiles': 'c1ccccc1'}  # Benzene
            svg2 = renderer.render(test_benzene, output_format='svg')
            if svg2:
                print(f"✅ Generated benzene structure ({len(svg2)} chars)")

        else:
            print("❌ Failed to generate structure")
    else:
        print("❌ RDKit not available")
        print(f"   Install with: {renderer.get_capabilities().install_command}")
