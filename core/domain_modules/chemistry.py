"""Chemistry domain module using RDKit templates."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from core.domain_modules.base import DomainModule, DomainModuleArtifact
from core.primitive_library import DiagramPrimitive


class ChemistryRDKitModule(DomainModule):
    module_id = "chemistry_rdkit"
    display_name = "RDKit Molecule Renderer"
    supported_domains = ["chemistry"]
    priority = 35

    def __init__(self) -> None:
        super().__init__()
        try:
            import rdkit  # type: ignore
            from rdkit import Chem  # type: ignore
            from rdkit.Chem import AllChem  # type: ignore  # noqa
            self.available = True
        except Exception:
            self.available = False

    def build_artifact(
        self,
        domain: str,
        diagram_plan: Any,
        spec: Any = None,
        property_graph: Any = None,
        scene: Any = None,
    ) -> DomainModuleArtifact | None:
        entities = self.normalize_entities(diagram_plan)
        molecules = [e for e in entities if 'molecule' in e.get('type', '').lower() or 'chemical' in e.get('type', '').lower()]
        if not molecules and spec:
            molecules = [obj for obj in getattr(spec, 'objects', []) if 'formula' in obj.get('properties', {})]
        if not molecules:
            return None

        svg_payload = self._build_svg_from_primitives(molecules)
        if svg_payload:
            svg_content, match_count = svg_payload
            metadata = {
                'primitive_matches': match_count,
                'available': True,
                'molecule_count': len(molecules)
            }
            return DomainModuleArtifact(
                module_id=f"{self.module_id}_svg",
                title="Chemistry primitives (SVG)",
                format="svg",
                content=svg_content,
                description="SVG layout assembled from reusable atom/bond primitives.",
                metadata=metadata,
            )

        script = self._generate_rdkit_script(molecules)
        metadata: Dict[str, Any] = {
            'available': self.available,
            'molecule_count': len(molecules),
            'primitive_matches': 0,
        }
        if not self.available:
            metadata['warning'] = 'rdkit not installed - script is provided for offline execution'

        return DomainModuleArtifact(
            module_id=self.module_id,
            title="RDKit molecule template",
            format="python",
            content=script,
            description="RDKit script scaffolding for rendering molecules detected in the property-graph plan.",
            metadata=metadata,
        )

    def _generate_rdkit_script(self, molecules: List[Dict[str, Any]]) -> str:
        entries = []
        for mol in molecules:
            label = mol.get('label') or mol.get('id') or 'Molecule'
            formula = mol.get('properties', {}).get('formula', label)
            smiles = mol.get('properties', {}).get('smiles', '')
            entries.append((label, smiles or formula))

        lines = [
            "from rdkit import Chem",
            "from rdkit.Chem import Draw",
            "",
            "molecules = []",
        ]
        for label, token in entries:
            if len(token) > 1 and all(c.isalpha() or c.isdigit() for c in token):
                assignment = f"Chem.MolFromSmarts('{token}')"
            else:
                assignment = f"Chem.MolFromSmiles('{token}')"
            lines.append(f"mol = {assignment}")
            lines.append(f"mol.SetProp('label', '{label}')")
            lines.append("molecules.append(mol)")

        lines.extend([
            "img = Draw.MolsToGridImage(molecules, legends=[m.GetProp('label') for m in molecules], molsPerRow=3)",
            "img.save('chemistry_plan.png')",
        ])
        return "\n".join(lines)

    def _build_svg_from_primitives(self, molecules: List[Dict[str, Any]]) -> Optional[tuple[str, int]]:
        matches: List[tuple[Dict[str, Any], DiagramPrimitive]] = []
        for molecule in molecules:
            primitive = self._fetch_primitive(molecule)
            if primitive:
                matches.append((molecule, primitive))

        if not matches:
            return None

        columns = 3
        spacing = 140
        width = spacing * min(len(matches), columns)
        height = spacing * ((len(matches) - 1) // columns + 1)
        fragments: List[str] = []

        for idx, (molecule, primitive) in enumerate(matches):
            col = idx % columns
            row = idx // columns
            transform = f"translate({col * spacing + 20}, {row * spacing + 20})"
            fragments.append(f'<g transform="{transform}">{primitive.svg_content}</g>')
            label = escape(molecule.get('label', molecule.get('id', '')))
            if label:
                fragments.append(f'<text x="{col * spacing + 20}" y="{row * spacing + 120}" font-size="14">{label}</text>')

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">{"".join(fragments)}</svg>'
        return svg, len(matches)

    def _fetch_primitive(self, molecule: Dict[str, Any]) -> Optional[DiagramPrimitive]:
        queries = [
            molecule.get('label'),
            molecule.get('properties', {}).get('formula'),
            molecule.get('type'),
            molecule.get('id')
        ]
        for query in filter(None, queries):
            primitives = self.query_primitives(query, "chemistry", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        fallback_keywords = ['atom', 'bond', 'molecule']
        for keyword in fallback_keywords:
            primitives = self.query_primitives(keyword, "chemistry", top_k=1, min_score=0.2)
            if primitives:
                return primitives[0]
        return None
