"""
Subject-Specific Interpreters for STEM Diagram Generation
=========================================================

This module provides interpreters that convert NLP analysis results
into UniversalScene objects for different STEM subjects.

Interpreters:
- ElectronicsInterpreter: Circuits, capacitors, resistors, etc.
- ChemistryInterpreter: Molecular structures, reactions, bonds
- BiologyInterpreter: Cells, organelles, DNA, anatomical diagrams
- MathematicsInterpreter: Graphs, geometric figures, vectors
- PhysicsInterpreter: Free body diagrams, forces, motion

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import Dict, List, Any, Optional
from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Annotation, Constraint,
    ObjectType, RelationType, Position, Dimensions, Style,
    DiagramDomain, DiagramType, create_circuit_scene,
    create_molecular_scene, create_cell_scene, create_graph_scene
)
from core.pattern_based_extractor import PatternBasedExtractor
import re


class BaseInterpreter:
    """Base class for all subject interpreters"""

    def __init__(self):
        self.scene: Optional[UniversalScene] = None

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """
        Convert NLP results to UniversalScene

        Args:
            nlp_results: Dictionary with 'entities', 'relationships', 'domain', 'metadata'
            problem_text: Original problem text

        Returns:
            UniversalScene object
        """
        raise NotImplementedError("Subclasses must implement interpret()")

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        match = re.search(r'[-+]?\d*\.?\d+', text)
        if match:
            try:
                return float(match.group())
            except:
                pass
        return None

    def _extract_unit(self, text: str) -> Optional[str]:
        """Extract unit from text"""
        # Common units
        units = ['V', 'A', 'Ω', 'F', 'H', 'W', 'J', 'N', 'm', 'kg', 's',
                 'μF', 'mF', 'pF', 'nF', 'mA', 'μA', 'kΩ', 'MΩ',
                 'cm', 'mm', 'km', 'g', 'mg', 'μg']
        for unit in units:
            if unit in text:
                return unit
        return None


class ElectronicsInterpreter(BaseInterpreter):
    """
    Interpreter for electronics and circuit diagrams
    Handles capacitors, resistors, inductors, batteries, etc.
    """

    def __init__(self):
        super().__init__()
        self.pattern_extractor = PatternBasedExtractor()

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """Convert NLP results to circuit diagram scene"""
        # Create base scene
        scene_id = f"circuit_{hash(problem_text) % 10000}"
        scene = create_circuit_scene(scene_id, "Circuit Diagram")
        scene.description = problem_text[:200] + "..." if len(problem_text) > 200 else problem_text

        # Extract component information using pattern-based extraction + NLP entities
        components = self._identify_components(nlp_results.get('entities', []), problem_text)

        # Layout components
        component_positions = self._layout_components(components)

        # Create scene objects for each component
        for comp_id, comp_data in components.items():
            obj = self._create_component_object(comp_id, comp_data, component_positions[comp_id])
            scene.add_object(obj)

        # Create connections based on relationships
        relationships = nlp_results.get('relationships', [])
        self._create_connections(scene, relationships, problem_text)

        # Add annotations
        self._add_circuit_annotations(scene, nlp_results, problem_text)

        return scene

    def _identify_components(self, entities: List[Dict], problem_text: str) -> Dict[str, Dict]:
        """
        Identify circuit components using pattern-based extraction + NLP entities

        Strategy:
        1. First try pattern-based extraction (direct from problem text)
        2. If insufficient, supplement with NLP entity extraction
        3. If still empty, log warning (no dangerous defaults!)
        """
        components = {}

        # Method 1: Pattern-based extraction (PRIMARY METHOD)
        print("   🔍 Pattern-based component extraction...")
        pattern_components = self.pattern_extractor.extract_component_objects(problem_text, domain='electronics')

        if pattern_components:
            components = pattern_components
            print(f"   ✅ Extracted {len(components)} components via patterns: {list(components.keys())}")
        else:
            print("   ⚠️  Pattern extraction found no components")

        # Method 2: NLP entity-based extraction (SUPPLEMENTARY)
        if not components or len(components) < 2:
            print("   🔍 Supplementing with NLP entity extraction...")
            entity_components = self._extract_from_entities(entities)

            if entity_components:
                # Merge with pattern components (pattern takes precedence)
                for comp_id, comp_data in entity_components.items():
                    if comp_id not in components:
                        components[comp_id] = comp_data
                print(f"   ✅ Added {len(entity_components)} components from entities")

        # Final check: If still empty, log error (no defaults!)
        if not components:
            print("   ❌ WARNING: No components extracted! Check problem text format.")
            print(f"   Problem: {problem_text[:100]}...")

        return components

    def _extract_from_entities(self, entities: List[Dict]) -> Dict[str, Dict]:
        """Extract components from NLP entities (fallback method)"""
        components = {}
        component_counter = {'resistor': 0, 'capacitor': 0, 'battery': 0, 'inductor': 0}

        # Look for component keywords in entities
        for entity in entities:
            text = entity.get('text', '').lower()

            comp_type = None
            if 'resistor' in text or 'resistance' in text or 'Ω' in text:
                comp_type = 'resistor'
            elif 'capacitor' in text or 'capacitance' in text or 'F' in entity.get('text', ''):
                comp_type = 'capacitor'
            elif 'battery' in text or 'voltage' in text or 'V' in entity.get('text', ''):
                comp_type = 'battery'
            elif 'inductor' in text or 'inductance' in text or 'H' in entity.get('text', ''):
                comp_type = 'inductor'

            if comp_type:
                component_counter[comp_type] += 1
                comp_id = f"{comp_type[0].upper()}{component_counter[comp_type]}"

                value = self._extract_numeric_value(entity.get('text', ''))
                unit = self._extract_unit(entity.get('text', ''))

                components[comp_id] = {
                    'type': comp_type,
                    'value': value,
                    'unit': unit,
                    'label': entity.get('text', ''),
                    'entity': entity
                }

        return components

    def _layout_components(self, components: Dict[str, Dict]) -> Dict[str, Position]:
        """Layout components in a sensible arrangement"""
        positions = {}
        x = 150
        y = 300
        spacing = 250

        for i, comp_id in enumerate(components.keys()):
            positions[comp_id] = Position(x + i * spacing, y)

        return positions

    def _create_component_object(self, comp_id: str, comp_data: Dict,
                                 position: Position) -> SceneObject:
        """Create a scene object for a component"""
        comp_type = comp_data['type']

        # Map component type to ObjectType
        type_map = {
            'resistor': ObjectType.RESISTOR,
            'capacitor': ObjectType.CAPACITOR,
            'battery': ObjectType.BATTERY,
            'inductor': ObjectType.INDUCTOR
        }

        # Default dimensions for each type
        dims_map = {
            'resistor': Dimensions(width=120, height=30),
            'capacitor': Dimensions(width=80, height=60),
            'battery': Dimensions(width=80, height=50),
            'inductor': Dimensions(width=100, height=40)
        }

        return SceneObject(
            id=comp_id,
            object_type=type_map.get(comp_type, ObjectType.RECTANGLE),
            position=position,
            dimensions=dims_map.get(comp_type, Dimensions(width=80, height=40)),
            label=comp_data.get('label', comp_id),
            properties={
                'value': comp_data.get('value'),
                'unit': comp_data.get('unit')
            },
            style=Style(color="#000000", stroke_width=2.0)
        )

    def _create_connections(self, scene: UniversalScene, relationships: List[Dict],
                           problem_text: str) -> None:
        """Create wire connections between components"""
        # Get all component objects
        objects = scene.objects

        # Look for series/parallel keywords
        is_series = 'series' in problem_text.lower()
        is_parallel = 'parallel' in problem_text.lower()

        # Connect components in series by default
        if is_series or (not is_parallel and len(objects) > 1):
            for i in range(len(objects) - 1):
                wire = Relationship(
                    id=f"wire_{i+1}",
                    relation_type=RelationType.CONNECTED_TO,
                    source_id=objects[i].id,
                    target_id=objects[i+1].id,
                    properties={'connection_type': 'series'}
                )
                scene.add_relationship(wire)

    def _add_circuit_annotations(self, scene: UniversalScene, nlp_results: Dict,
                                 problem_text: str) -> None:
        """Add relevant annotations to the circuit"""
        # Look for equations or important values
        equations = re.findall(r'[A-Za-z]\s*=\s*[^,\.]+', problem_text)

        y = 150
        for i, eq in enumerate(equations[:3]):  # Limit to 3 annotations
            annotation = Annotation(
                id=f"eq_{i+1}",
                text=eq.strip(),
                position=Position(scene.canvas_width / 2, y + i * 30),
                annotation_type="equation",
                style=Style(font_size=14, color="#333333")
            )
            scene.add_annotation(annotation)


class ChemistryInterpreter(BaseInterpreter):
    """
    Interpreter for chemistry diagrams
    Handles molecular structures, atoms, bonds, reactions
    """

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """Convert NLP results to molecular structure scene"""
        scene_id = f"molecule_{hash(problem_text) % 10000}"
        scene = create_molecular_scene(scene_id, "Molecular Structure")
        scene.description = problem_text[:200] + "..." if len(problem_text) > 200 else problem_text

        # Extract atoms
        atoms = self._identify_atoms(nlp_results.get('entities', []), problem_text)

        # Layout atoms
        atom_positions = self._layout_atoms(atoms)

        # Create atom objects
        for atom_id, atom_data in atoms.items():
            obj = self._create_atom_object(atom_id, atom_data, atom_positions[atom_id])
            scene.add_object(obj)

        # Create bonds
        bonds = self._identify_bonds(nlp_results.get('relationships', []), problem_text)
        for bond_id, bond_data in bonds.items():
            bond_rel = self._create_bond_relationship(bond_id, bond_data, atoms)
            if bond_rel:
                scene.add_relationship(bond_rel)

        return scene

    def _identify_atoms(self, entities: List[Dict], problem_text: str) -> Dict[str, Dict]:
        """Identify atoms from entities"""
        atoms = {}

        # Common elements
        elements = ['H', 'C', 'N', 'O', 'S', 'P', 'Cl', 'Br', 'F', 'I']

        # Look for element symbols
        for elem in elements:
            # Find all occurrences
            pattern = rf'\b{elem}\d*\b'
            matches = re.finditer(pattern, problem_text)
            for i, match in enumerate(matches):
                atom_id = f"{elem}{i+1}"
                atoms[atom_id] = {
                    'element': elem,
                    'text': match.group()
                }

        # If no atoms found, create a simple molecule (e.g., water)
        if not atoms:
            atoms = {
                'O1': {'element': 'O', 'text': 'O'},
                'H1': {'element': 'H', 'text': 'H'},
                'H2': {'element': 'H', 'text': 'H'}
            }

        return atoms

    def _layout_atoms(self, atoms: Dict[str, Dict]) -> Dict[str, Position]:
        """Layout atoms in a molecular structure"""
        positions = {}
        center_x = 400
        center_y = 300

        import math
        n = len(atoms)

        if n <= 3:
            # Linear or triangular
            for i, atom_id in enumerate(atoms.keys()):
                angle = (i / n) * 2 * math.pi
                radius = 100
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[atom_id] = Position(x, y)
        else:
            # Circular arrangement
            for i, atom_id in enumerate(atoms.keys()):
                angle = (i / n) * 2 * math.pi
                radius = 150
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[atom_id] = Position(x, y)

        return positions

    def _create_atom_object(self, atom_id: str, atom_data: Dict,
                           position: Position) -> SceneObject:
        """Create a scene object for an atom"""
        element = atom_data['element']

        # Electron counts for common elements
        electron_map = {'H': 1, 'C': 6, 'N': 7, 'O': 8, 'S': 16, 'P': 15,
                       'Cl': 17, 'Br': 35, 'F': 9, 'I': 53}

        return SceneObject(
            id=atom_id,
            object_type=ObjectType.ATOM,
            position=position,
            dimensions=Dimensions(radius=50),
            label=element,
            properties={
                'element': element,
                'electrons': electron_map.get(element, 6)
            },
            style=Style(color="#333333", stroke_width=2.0)
        )

    def _identify_bonds(self, relationships: List[Dict], problem_text: str) -> Dict[str, Dict]:
        """Identify bonds from relationships"""
        bonds = {}

        # Look for bond keywords
        single_bond = 'single bond' in problem_text.lower()
        double_bond = 'double bond' in problem_text.lower()
        triple_bond = 'triple bond' in problem_text.lower()

        bond_order = 1
        if triple_bond:
            bond_order = 3
        elif double_bond:
            bond_order = 2

        # Create bonds from relationships
        for i, rel in enumerate(relationships):
            if rel.get('type') in ['RELATED_TO', 'BONDED_TO', 'CONNECTED_TO']:
                bonds[f"bond_{i+1}"] = {
                    'source': rel.get('subject', ''),
                    'target': rel.get('target', ''),
                    'order': bond_order
                }

        return bonds

    def _create_bond_relationship(self, bond_id: str, bond_data: Dict,
                                  atoms: Dict[str, Dict]) -> Optional[Relationship]:
        """Create a bond relationship"""
        # Try to match source/target to atom IDs
        source_id = None
        target_id = None

        source_text = bond_data['source']
        target_text = bond_data['target']

        # Find matching atoms
        for atom_id, atom_data in atoms.items():
            if atom_data['element'] in source_text and not source_id:
                source_id = atom_id
            if atom_data['element'] in target_text and not target_id:
                target_id = atom_id

        # If we have both, create the bond
        if source_id and target_id:
            return Relationship(
                id=bond_id,
                relation_type=RelationType.BONDED_TO,
                source_id=source_id,
                target_id=target_id,
                properties={'bond_order': bond_data['order']}
            )

        return None


class MathematicsInterpreter(BaseInterpreter):
    """
    Interpreter for mathematical diagrams
    Handles function graphs, geometric figures, vectors
    """

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """Convert NLP results to mathematical diagram scene"""
        scene_id = f"math_{hash(problem_text) % 10000}"

        # Determine diagram type
        if any(keyword in problem_text.lower() for keyword in ['graph', 'function', 'plot', 'curve']):
            scene = create_graph_scene(scene_id, "Function Graph")
            self._add_axes(scene)
        elif any(keyword in problem_text.lower() for keyword in ['triangle', 'circle', 'rectangle', 'polygon']):
            scene = UniversalScene(
                scene_id=scene_id,
                domain=DiagramDomain.MATHEMATICS,
                diagram_type=DiagramType.GEOMETRIC_FIGURE,
                title="Geometric Figure"
            )
            self._add_geometric_shapes(scene, problem_text)
        elif any(keyword in problem_text.lower() for keyword in ['vector', 'force', 'velocity']):
            scene = UniversalScene(
                scene_id=scene_id,
                domain=DiagramDomain.MATHEMATICS,
                diagram_type=DiagramType.VECTOR_DIAGRAM,
                title="Vector Diagram"
            )
            self._add_vectors(scene, nlp_results)
        else:
            scene = create_graph_scene(scene_id, "Mathematical Diagram")

        scene.description = problem_text[:200] + "..." if len(problem_text) > 200 else problem_text
        return scene

    def _add_axes(self, scene: UniversalScene) -> None:
        """Add coordinate axes"""
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        # X-axis
        x_axis = SceneObject(
            id="x_axis",
            object_type=ObjectType.AXIS,
            position=Position(center_x, center_y),
            properties={'x2': scene.canvas_width - 50, 'y2': center_y},
            style=Style(color="#333333", stroke_width=2.0)
        )
        scene.add_object(x_axis)

        # Y-axis
        y_axis = SceneObject(
            id="y_axis",
            object_type=ObjectType.AXIS,
            position=Position(center_x, 50),
            properties={'x2': center_x, 'y2': scene.canvas_height - 50},
            style=Style(color="#333333", stroke_width=2.0)
        )
        scene.add_object(y_axis)

        # Labels
        x_label = Annotation(
            id="x_label",
            text="x",
            position=Position(scene.canvas_width - 30, center_y + 30),
            style=Style(font_size=18, font_weight="bold")
        )
        scene.add_annotation(x_label)

        y_label = Annotation(
            id="y_label",
            text="y",
            position=Position(center_x + 20, 30),
            style=Style(font_size=18, font_weight="bold")
        )
        scene.add_annotation(y_label)

    def _add_geometric_shapes(self, scene: UniversalScene, problem_text: str) -> None:
        """Add geometric shapes based on problem text"""
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        if 'circle' in problem_text.lower():
            circle = SceneObject(
                id="circle_1",
                object_type=ObjectType.CIRCLE,
                position=Position(center_x, center_y),
                dimensions=Dimensions(radius=100),
                style=Style(color="#0066cc", stroke_width=3.0)
            )
            scene.add_object(circle)
        elif 'rectangle' in problem_text.lower() or 'square' in problem_text.lower():
            rect = SceneObject(
                id="rect_1",
                object_type=ObjectType.RECTANGLE,
                position=Position(center_x, center_y),
                dimensions=Dimensions(width=200, height=150),
                style=Style(color="#0066cc", stroke_width=3.0)
            )
            scene.add_object(rect)

    def _add_vectors(self, scene: UniversalScene, nlp_results: Dict) -> None:
        """Add vector arrows"""
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        # Extract vector information from entities
        vectors = []
        for entity in nlp_results.get('entities', []):
            text = entity.get('text', '').lower()
            if 'vector' in text or 'force' in text:
                vectors.append(entity)

        # Create vector objects
        for i, vec_entity in enumerate(vectors[:4]):  # Limit to 4 vectors
            angle = (i / 4) * 360 * 0.017453  # Convert to radians
            import math
            dx = 100 * math.cos(angle)
            dy = 100 * math.sin(angle)

            vector = SceneObject(
                id=f"vector_{i+1}",
                object_type=ObjectType.VECTOR,
                position=Position(center_x, center_y),
                properties={'dx': dx, 'dy': dy},
                label=f"v{i+1}",
                style=Style(color="#cc0000", stroke_width=2.5)
            )
            scene.add_object(vector)


class PhysicsInterpreter(ElectronicsInterpreter):
    """
    Interpreter for physics diagrams
    Inherits from ElectronicsInterpreter and adds physics-specific features
    """

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """Convert NLP results to physics diagram"""
        # Check if it's a circuit problem (delegate to electronics)
        if any(keyword in problem_text.lower() for keyword in
               ['circuit', 'capacitor', 'resistor', 'voltage', 'current']):
            return super().interpret(nlp_results, problem_text)

        # Otherwise, create a general physics diagram
        scene_id = f"physics_{hash(problem_text) % 10000}"
        scene = UniversalScene(
            scene_id=scene_id,
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.FREE_BODY_DIAGRAM,
            title="Physics Diagram"
        )

        scene.description = problem_text[:200] + "..." if len(problem_text) > 200 else problem_text

        # Add objects and forces based on problem text
        self._add_physics_objects(scene, nlp_results, problem_text)

        return scene

    def _add_physics_objects(self, scene: UniversalScene, nlp_results: Dict,
                            problem_text: str) -> None:
        """Add physics-specific objects (masses, forces, etc.)"""
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        # Add a mass
        mass = SceneObject(
            id="mass_1",
            object_type=ObjectType.MASS,
            position=Position(center_x, center_y),
            dimensions=Dimensions(width=80, height=80),
            label="m",
            style=Style(color="#333333", fill_color="#CCCCCC", stroke_width=3.0)
        )
        scene.add_object(mass)

        # Add force vectors
        forces = ['weight', 'normal', 'friction', 'tension']
        for i, force in enumerate(forces):
            if force in problem_text.lower():
                angle = (i / 4) * 360 * 0.017453
                import math
                dx = 80 * math.cos(angle)
                dy = 80 * math.sin(angle)

                force_vector = SceneObject(
                    id=f"force_{force}",
                    object_type=ObjectType.FORCE_VECTOR,
                    position=Position(center_x, center_y),
                    properties={'dx': dx, 'dy': dy},
                    label=f"F_{force[0]}",
                    style=Style(color="#cc0000", stroke_width=2.5)
                )
                scene.add_object(force_vector)


class BiologyInterpreter(BaseInterpreter):
    """
    Interpreter for biology diagrams
    Handles cells, organelles, DNA, anatomical structures
    """

    def interpret(self, nlp_results: Dict[str, Any], problem_text: str) -> UniversalScene:
        """Convert NLP results to biology diagram"""
        scene_id = f"bio_{hash(problem_text) % 10000}"
        scene = create_cell_scene(scene_id, "Cell Diagram")
        scene.description = problem_text[:200] + "..." if len(problem_text) > 200 else problem_text

        # Add cell membrane
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        cell_membrane = SceneObject(
            id="cell_membrane",
            object_type=ObjectType.CELL,
            position=Position(center_x, center_y),
            dimensions=Dimensions(radius=250),
            label="Cell",
            style=Style(color="#4ECDC4", stroke_width=4.0, opacity=0.3, fill_color="#E8F8F5")
        )
        scene.add_object(cell_membrane)

        # Add organelles
        self._add_organelles(scene, nlp_results, problem_text)

        return scene

    def _add_organelles(self, scene: UniversalScene, nlp_results: Dict,
                       problem_text: str) -> None:
        """Add organelles to the cell"""
        center_x = scene.canvas_width / 2
        center_y = scene.canvas_height / 2

        organelles = [
            ('nucleus', Position(center_x, center_y), 80, "#FF6B6B"),
            ('mitochondria', Position(center_x + 120, center_y - 80), 50, "#FFE66D"),
            ('ribosome', Position(center_x - 100, center_y + 80), 20, "#4ECDC4")
        ]

        for name, pos, radius, color in organelles:
            if name in problem_text.lower():
                organelle = SceneObject(
                    id=name,
                    object_type=ObjectType.ORGANELLE,
                    position=pos,
                    dimensions=Dimensions(radius=radius),
                    label=name.capitalize(),
                    style=Style(color="#333333", fill_color=color, stroke_width=2.0)
                )
                scene.add_object(organelle)


# Factory function to get appropriate interpreter
def get_interpreter(domain: str) -> BaseInterpreter:
    """Get appropriate interpreter for domain"""
    interpreters = {
        'electronics': ElectronicsInterpreter(),
        'physics': PhysicsInterpreter(),
        'chemistry': ChemistryInterpreter(),
        'biology': BiologyInterpreter(),
        'mathematics': MathematicsInterpreter(),
        'geometry': MathematicsInterpreter(),
        'electrostatics': PhysicsInterpreter(),
        'circuits': ElectronicsInterpreter()
    }

    return interpreters.get(domain.lower(), ElectronicsInterpreter())


if __name__ == "__main__":
    print("Subject-Specific Interpreters - Test\n" + "=" * 50)

    # Test electronics interpreter
    nlp_results = {
        'domain': 'electronics',
        'entities': [
            {'text': '12V', 'type': 'QUANTITY'},
            {'text': '100Ω', 'type': 'QUANTITY'},
            {'text': '10μF', 'type': 'QUANTITY'}
        ],
        'relationships': []
    }

    problem_text = "A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor."

    interpreter = get_interpreter('electronics')
    scene = interpreter.interpret(nlp_results, problem_text)

    print(f"Generated Scene: {scene.title}")
    print(f"Domain: {scene.domain.value}")
    print(f"Objects: {len(scene.objects)}")
    print(f"Relationships: {len(scene.relationships)}")

    # Render to SVG
    from core.universal_svg_renderer import UniversalSVGRenderer
    renderer = UniversalSVGRenderer()
    renderer.save_svg(scene, "output/test_interpreted_circuit.svg")

    print("\n✅ Subject-specific interpreters test complete!")
