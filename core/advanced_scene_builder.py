"""
Advanced Scene Builder with Physics Rules
=========================================

This module provides sophisticated scene building that understands:
- Physical constraints and relationships
- Spatial arrangements
- Component connections
- Domain-specific rules

It takes NLP results and builds accurate, physically meaningful scenes.

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import Dict, List, Any, Optional, Tuple
from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Annotation, Constraint,
    ObjectType, RelationType, Position, Dimensions, Style,
    DiagramDomain, DiagramType
)
import re
import math


class PhysicsRuleEngine:
    """
    Rule engine for physics-based constraints and relationships
    """

    @staticmethod
    def validate_capacitor_configuration(scene: UniversalScene) -> List[str]:
        """Validate capacitor configuration makes physical sense"""
        warnings = []
        capacitors = [obj for obj in scene.objects if obj.object_type == ObjectType.CAPACITOR]

        if len(capacitors) > 1:
            # Check for proper connections
            connections = scene.relationships
            if len(connections) < len(capacitors) - 1:
                warnings.append("Capacitors may not be properly connected")

        return warnings

    @staticmethod
    def infer_circuit_topology(components: List[Dict]) -> str:
        """Infer if circuit is series, parallel, or mixed"""
        # Look for keywords in component descriptions
        series_keywords = ['series', 'in series', 'connected in series']
        parallel_keywords = ['parallel', 'in parallel', 'connected in parallel']

        text = ' '.join([c.get('label', '').lower() for c in components])

        if any(kw in text for kw in series_keywords):
            return 'series'
        elif any(kw in text for kw in parallel_keywords):
            return 'parallel'
        return 'series'  # default

    @staticmethod
    def calculate_capacitor_spacing(num_capacitors: int, canvas_width: float) -> float:
        """Calculate optimal spacing between capacitors"""
        available_width = canvas_width * 0.8  # 80% of canvas
        component_width = 100  # average component width
        total_component_width = num_capacitors * component_width
        remaining_space = available_width - total_component_width

        if num_capacitors > 1:
            return remaining_space / (num_capacitors + 1)
        return remaining_space / 2


class AdvancedSceneBuilder:
    """
    Advanced scene builder that creates physically accurate scenes
    """

    def __init__(self):
        self.rule_engine = PhysicsRuleEngine()

    def build_scene(self, nlp_results: Dict, scene_id: str = None, **kwargs) -> UniversalScene:
        """
        Build scene from NLP results - dispatches to domain-specific builder

        Args:
            nlp_results: NLP extraction results
            scene_id: Optional scene identifier
            **kwargs: Additional parameters

        Returns:
            UniversalScene object
        """
        problem_text = nlp_results.get('text', '')
        domain = nlp_results.get('domain', 'electrical')

        # Dispatch to domain-specific builder
        if domain in ['electrical', 'electronics', 'capacitance']:
            return self.build_capacitor_scene(nlp_results, problem_text)
        else:
            # Default to capacitor for now
            return self.build_capacitor_scene(nlp_results, problem_text)

    def build_capacitor_scene(self, nlp_results: Dict, problem_text: str) -> UniversalScene:
        """
        Build an accurate capacitor circuit scene with detailed physical structure

        This method analyzes the problem and creates a detailed representation showing:
        - Capacitor plates (not just symbols)
        - Charge distributions
        - Dielectrics (if present)
        - Multi-stage configurations (if applicable)
        """
        scene_id = f"capacitor_{hash(problem_text) % 10000}"
        scene = UniversalScene(
            scene_id=scene_id,
            domain=DiagramDomain.ELECTRONICS,
            diagram_type=DiagramType.CIRCUIT_DIAGRAM,
            title="Capacitor Circuit",
            canvas_width=1000,
            canvas_height=600
        )

        # Extract circuit information
        circuit_info = self._analyze_circuit(nlp_results, problem_text)

        # Check if this is a detailed capacitor problem (plates, dielectric, etc.)
        use_detailed_repr = (circuit_info['has_plates'] or circuit_info['has_dielectric'] or
                           circuit_info['has_area'] or circuit_info['has_separation'])

        if use_detailed_repr:
            # Use detailed physical representation
            return self._build_detailed_capacitor_scene(circuit_info, scene, nlp_results)
        else:
            # Use circuit diagram representation (original method)
            return self._build_circuit_diagram_scene(circuit_info, scene)

    def _build_circuit_diagram_scene(self, circuit_info: Dict, scene: UniversalScene) -> UniversalScene:
        """Build traditional circuit diagram with schematic symbols"""
        # Build components based on analysis
        components = self._create_circuit_components(circuit_info)

        # Calculate layout
        layout = self._calculate_circuit_layout(components, circuit_info, scene)

        # Add components to scene
        for comp_id, comp_data in components.items():
            position = layout[comp_id]
            obj = self._create_component_with_properties(comp_id, comp_data, position)
            scene.add_object(obj)

        # Create connections
        connections = self._create_circuit_connections(components, circuit_info)
        for conn in connections:
            scene.add_relationship(conn)

        # Add annotations
        annotations = self._create_circuit_annotations(circuit_info, scene)
        for ann in annotations:
            scene.add_annotation(ann)

        # Validate scene
        warnings = self.rule_engine.validate_capacitor_configuration(scene)
        if warnings:
            scene.metadata['validation_warnings'] = warnings

        return scene

    def _build_detailed_capacitor_scene(self, circuit_info: Dict, scene: UniversalScene,
                                       nlp_results: Dict) -> UniversalScene:
        """
        Build detailed physical representation of capacitors showing plates, gaps, charges

        This is used for problems that discuss physical structure (plates, area, separation, dielectric)
        """
        capacitances = circuit_info['capacitances']
        voltages = circuit_info['voltages']

        # Determine number of capacitors
        num_caps = len(capacitances) if capacitances else 1

        # Calculate layout for detailed capacitors
        x_start = 150
        x_spacing = 300
        y_center = scene.canvas_height / 2

        for i in range(num_caps):
            cap_x = x_start + i * x_spacing
            cap_label = capacitances[i]['text'] if i < len(capacitances) else f"C{i+1}"
            cap_value = capacitances[i]['value'] if i < len(capacitances) else 10e-6
            cap_unit = capacitances[i]['unit'] if i < len(capacitances) else "μF"

            # Create detailed capacitor structure
            self._add_detailed_capacitor(scene, f"C{i+1}", cap_x, y_center,
                                        cap_label, cap_value, cap_unit,
                                        circuit_info)

        # Add battery if present
        if circuit_info['has_battery'] and voltages:
            battery_x = 100
            battery_y = y_center
            voltage_val = voltages[0]['value']
            voltage_text = voltages[0]['text']

            battery = SceneObject(
                id="battery",
                object_type=ObjectType.BATTERY,
                position=Position(battery_x, battery_y),
                dimensions=Dimensions(width=80, height=50),
                label=voltage_text,
                properties={'value': voltage_val, 'unit': 'V'},
                style=Style(color="#000000", stroke_width=2.0)
            )
            scene.add_object(battery)

        # Add connections between detailed capacitors
        if circuit_info['is_series'] and num_caps > 1:
            for i in range(num_caps - 1):
                conn = Relationship(
                    id=f"series_conn_{i}",
                    relation_type=RelationType.CONNECTED_TO,
                    source_id=f"C{i+1}_right_plate",
                    target_id=f"C{i+2}_left_plate",
                    properties={'connection_type': 'series'}
                )
                scene.add_relationship(conn)

        # Add key annotations
        annotations = self._create_detailed_annotations(circuit_info, scene, num_caps)
        for ann in annotations:
            scene.add_annotation(ann)

        return scene

    def _add_detailed_capacitor(self, scene: UniversalScene, cap_id: str, x: float, y: float,
                               label: str, value: float, unit: str, circuit_info: Dict):
        """
        Add a detailed capacitor showing plates, gap, charges, and dielectric
        """
        plate_width = 80
        plate_height = 150
        plate_gap = 40
        plate_thickness = 3

        # Left plate
        left_plate = SceneObject(
            id=f"{cap_id}_left_plate",
            object_type=ObjectType.RECTANGLE,
            position=Position(x - plate_gap/2 - plate_thickness, y),
            dimensions=Dimensions(width=plate_thickness, height=plate_height),
            label="",
            properties={'plate': 'negative', 'capacitor_id': cap_id},
            style=Style(color="#000000", fill_color="#2c3e50", stroke_width=2.0)
        )
        scene.add_object(left_plate)

        # Right plate
        right_plate = SceneObject(
            id=f"{cap_id}_right_plate",
            object_type=ObjectType.RECTANGLE,
            position=Position(x + plate_gap/2, y),
            dimensions=Dimensions(width=plate_thickness, height=plate_height),
            label="",
            properties={'plate': 'positive', 'capacitor_id': cap_id},
            style=Style(color="#000000", fill_color="#2c3e50", stroke_width=2.0)
        )
        scene.add_object(right_plate)

        # Dielectric (if mentioned)
        if circuit_info['has_dielectric']:
            dielectric = SceneObject(
                id=f"{cap_id}_dielectric",
                object_type=ObjectType.RECTANGLE,
                position=Position(x, y),
                dimensions=Dimensions(width=plate_gap * 0.6, height=plate_height * 0.8),
                label="κ",
                properties={'material': 'dielectric', 'capacitor_id': cap_id},
                style=Style(color="#3498db", fill_color="#e3f2fd", stroke_width=1.0,
                          opacity=0.6)
            )
            scene.add_object(dielectric)

        # Add charge symbols on plates
        # Left plate: negative charges
        for i in range(5):
            y_pos = y - plate_height/2 + (i+1) * plate_height/6
            charge = SceneObject(
                id=f"{cap_id}_neg_charge_{i}",
                object_type=ObjectType.LABEL,
                position=Position(x - plate_gap/2 - 15, y_pos),
                dimensions=Dimensions(width=10, height=10),
                label="−",
                properties={'charge_type': 'negative'},
                style=Style(color="#e74c3c", font_size=18, font_weight="bold")
            )
            scene.add_object(charge)

        # Right plate: positive charges
        for i in range(5):
            y_pos = y - plate_height/2 + (i+1) * plate_height/6
            charge = SceneObject(
                id=f"{cap_id}_pos_charge_{i}",
                object_type=ObjectType.LABEL,
                position=Position(x + plate_gap/2 + 15, y_pos),
                dimensions=Dimensions(width=10, height=10),
                label="+",
                properties={'charge_type': 'positive'},
                style=Style(color="#2980b9", font_size=18, font_weight="bold")
            )
            scene.add_object(charge)

        # Add capacitor label below
        cap_label_obj = SceneObject(
            id=f"{cap_id}_label",
            object_type=ObjectType.LABEL,
            position=Position(x, y + plate_height/2 + 30),
            dimensions=Dimensions(width=100, height=20),
            label=label,
            properties={'value': value, 'unit': unit},
            style=Style(color="#000000", font_size=16, font_weight="bold")
        )
        scene.add_object(cap_label_obj)

        # Add relationship between plates
        plate_rel = Relationship(
            id=f"{cap_id}_plates_rel",
            relation_type=RelationType.ACTS_ON,
            source_id=f"{cap_id}_left_plate",
            target_id=f"{cap_id}_right_plate",
            properties={'relationship': 'opposite_charges', 'gap': plate_gap}
        )
        scene.add_relationship(plate_rel)

    def _create_detailed_annotations(self, circuit_info: Dict, scene: UniversalScene,
                                    num_caps: int) -> List[Annotation]:
        """Create annotations for detailed capacitor diagrams"""
        annotations = []

        # Title annotation
        if circuit_info['is_series']:
            title = Annotation(
                id="config_title",
                text=f"Series Capacitor Configuration ({num_caps} capacitors)",
                position=Position(scene.canvas_width / 2, 40),
                annotation_type="title",
                style=Style(color="#2c3e50", font_size=20, font_weight="bold")
            )
            annotations.append(title)
        elif circuit_info['is_parallel']:
            title = Annotation(
                id="config_title",
                text=f"Parallel Capacitor Configuration ({num_caps} capacitors)",
                position=Position(scene.canvas_width / 2, 40),
                annotation_type="title",
                style=Style(color="#2c3e50", font_size=20, font_weight="bold")
            )
            annotations.append(title)

        # Add voltage annotation if present
        if circuit_info['voltages']:
            v_text = f"V = {circuit_info['voltages'][0]['text']}"
            voltage_ann = Annotation(
                id="voltage_label",
                text=v_text,
                position=Position(50, 80),
                annotation_type="label",
                style=Style(color="#e74c3c", font_size=16, font_weight="bold")
            )
            annotations.append(voltage_ann)

        # Add physical quantities if present
        y_offset = 120
        if circuit_info['has_area']:
            area_matches = re.findall(r'area.*?(\d+\.?\d*)\s*(m²|cm²)',
                                     circuit_info['problem_text'], re.IGNORECASE)
            if area_matches:
                area_ann = Annotation(
                    id="area_label",
                    text=f"Plate Area: {area_matches[0][0]} {area_matches[0][1]}",
                    position=Position(scene.canvas_width - 150, y_offset),
                    annotation_type="parameter",
                    style=Style(color="#16a085", font_size=14)
                )
                annotations.append(area_ann)
                y_offset += 30

        if circuit_info['has_separation']:
            sep_matches = re.findall(r'separation.*?(\d+\.?\d*)\s*(mm|cm|m)',
                                    circuit_info['problem_text'], re.IGNORECASE)
            if sep_matches:
                sep_ann = Annotation(
                    id="separation_label",
                    text=f"Plate Separation: {sep_matches[0][0]} {sep_matches[0][1]}",
                    position=Position(scene.canvas_width - 150, y_offset),
                    annotation_type="parameter",
                    style=Style(color="#16a085", font_size=14)
                )
                annotations.append(sep_ann)

        return annotations

    def _analyze_circuit(self, nlp_results: Dict, problem_text: str) -> Dict:
        """
        Analyze the circuit from NLP results and problem text

        Returns comprehensive circuit information
        """
        text_lower = problem_text.lower()
        entities = nlp_results.get('entities', [])

        # Detect components
        has_battery = 'battery' in text_lower or 'voltage' in text_lower or ' V' in problem_text
        has_capacitors = 'capacitor' in text_lower
        has_resistor = 'resistor' in text_lower or 'resistance' in text_lower
        has_dielectric = 'dielectric' in text_lower

        # Extract values
        voltages = self._extract_values(entities, problem_text, ['V', 'volt'])
        capacitances = self._extract_values(entities, problem_text, ['F', 'μF', 'pF', 'nF', 'mF'])
        resistances = self._extract_values(entities, problem_text, ['Ω', 'ohm', 'kΩ', 'MΩ'])

        # Detect configuration
        is_series = 'series' in text_lower
        is_parallel = 'parallel' in text_lower

        # Detect special features
        has_plates = 'plate' in text_lower
        has_separation = 'separation' in text_lower
        has_area = 'area' in text_lower

        return {
            'has_battery': has_battery,
            'has_capacitors': has_capacitors,
            'has_resistor': has_resistor,
            'has_dielectric': has_dielectric,
            'voltages': voltages,
            'capacitances': capacitances,
            'resistances': resistances,
            'is_series': is_series,
            'is_parallel': is_parallel,
            'has_plates': has_plates,
            'has_separation': has_separation,
            'has_area': has_area,
            'problem_text': problem_text
        }

    def _extract_values(self, entities: List[Dict], text: str, units: List[str]) -> List[Dict]:
        """Extract numerical values with specific units"""
        values = []

        # Pattern to match number + unit
        for unit in units:
            pattern = rf'(\d+\.?\d*)\s*{re.escape(unit)}'
            matches = re.finditer(pattern, text)
            for match in matches:
                values.append({
                    'value': float(match.group(1)),
                    'unit': unit,
                    'text': match.group(0)
                })

        return values

    def _create_circuit_components(self, circuit_info: Dict) -> Dict[str, Dict]:
        """Create circuit components based on analysis"""
        components = {}

        # Add battery if present
        if circuit_info['has_battery'] and circuit_info['voltages']:
            voltage = circuit_info['voltages'][0]
            components['V1'] = {
                'type': 'battery',
                'value': voltage['value'],
                'unit': voltage['unit'],
                'label': voltage['text']
            }

        # Add capacitors
        capacitances = circuit_info['capacitances']
        if capacitances:
            for i, cap in enumerate(capacitances, 1):
                components[f'C{i}'] = {
                    'type': 'capacitor',
                    'value': cap['value'],
                    'unit': cap['unit'],
                    'label': cap['text']
                }
        elif circuit_info['has_capacitors']:
            # Add generic capacitor if mentioned but no values
            components['C1'] = {
                'type': 'capacitor',
                'value': 10e-6,
                'unit': 'μF',
                'label': 'C'
            }

        # Add resistor if present
        resistances = circuit_info['resistances']
        if resistances:
            for i, res in enumerate(resistances, 1):
                components[f'R{i}'] = {
                    'type': 'resistor',
                    'value': res['value'],
                    'unit': res['unit'],
                    'label': res['text']
                }

        return components

    def _calculate_circuit_layout(self, components: Dict, circuit_info: Dict,
                                  scene: UniversalScene) -> Dict[str, Position]:
        """Calculate optimal layout for circuit components"""
        layout = {}

        # Get component types
        comp_list = list(components.keys())
        num_components = len(comp_list)

        if num_components == 0:
            return layout

        # Determine layout style based on configuration
        if circuit_info['is_series']:
            # Horizontal series layout
            spacing = self.rule_engine.calculate_capacitor_spacing(
                num_components, scene.canvas_width
            )

            x = spacing
            y = scene.canvas_height / 2

            for comp_id in comp_list:
                layout[comp_id] = Position(x, y)
                x += 100 + spacing  # component width + spacing

        elif circuit_info['is_parallel']:
            # Vertical parallel layout
            x = scene.canvas_width / 2
            y_start = 200
            y_spacing = 150

            for i, comp_id in enumerate(comp_list):
                layout[comp_id] = Position(x, y_start + i * y_spacing)

        else:
            # Default horizontal layout
            spacing = self.rule_engine.calculate_capacitor_spacing(
                num_components, scene.canvas_width
            )

            x = spacing + 100
            y = scene.canvas_height / 2

            for comp_id in comp_list:
                layout[comp_id] = Position(x, y)
                x += 150 + spacing

        return layout

    def _create_component_with_properties(self, comp_id: str, comp_data: Dict,
                                         position: Position) -> SceneObject:
        """Create a component with full properties"""
        comp_type = comp_data['type']

        type_map = {
            'battery': ObjectType.BATTERY,
            'capacitor': ObjectType.CAPACITOR,
            'resistor': ObjectType.RESISTOR,
            'inductor': ObjectType.INDUCTOR
        }

        dims_map = {
            'battery': Dimensions(width=80, height=50),
            'capacitor': Dimensions(width=80, height=60),
            'resistor': Dimensions(width=120, height=30),
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
                'unit': comp_data.get('unit'),
                'component_type': comp_type
            },
            style=Style(color="#000000", stroke_width=2.0)
        )

    def _create_circuit_connections(self, components: Dict,
                                   circuit_info: Dict) -> List[Relationship]:
        """Create proper connections between components"""
        connections = []
        comp_ids = list(components.keys())

        if len(comp_ids) < 2:
            return connections

        # Create connections based on topology
        if circuit_info['is_series']:
            # Connect in series: A -> B -> C -> ...
            for i in range(len(comp_ids) - 1):
                conn = Relationship(
                    id=f"wire_{i+1}",
                    relation_type=RelationType.CONNECTED_TO,
                    source_id=comp_ids[i],
                    target_id=comp_ids[i+1],
                    properties={'connection_type': 'series'}
                )
                connections.append(conn)
        else:
            # Default: connect all to first component
            for i in range(1, len(comp_ids)):
                conn = Relationship(
                    id=f"wire_{i}",
                    relation_type=RelationType.CONNECTED_TO,
                    source_id=comp_ids[0],
                    target_id=comp_ids[i],
                    properties={'connection_type': 'default'}
                )
                connections.append(conn)

        return connections

    def _create_circuit_annotations(self, circuit_info: Dict,
                                    scene: UniversalScene) -> List[Annotation]:
        """Create informative annotations"""
        annotations = []

        # Extract equations from problem text
        text = circuit_info['problem_text']
        equations = re.findall(r'[A-Za-z]\s*=\s*[^,\.]+', text)

        y = 100
        for i, eq in enumerate(equations[:3]):
            ann = Annotation(
                id=f"eq_{i+1}",
                text=eq.strip(),
                position=Position(scene.canvas_width / 2, y + i * 30),
                annotation_type="equation",
                style=Style(font_size=14, color="#333333", font_weight="bold")
            )
            annotations.append(ann)

        # Add circuit type annotation
        if circuit_info['is_series']:
            circuit_type = Annotation(
                id="circuit_type",
                text="Series Configuration",
                position=Position(scene.canvas_width / 2, 50),
                annotation_type="label",
                style=Style(font_size=16, color="#667eea", font_weight="bold")
            )
            annotations.append(circuit_type)
        elif circuit_info['is_parallel']:
            circuit_type = Annotation(
                id="circuit_type",
                text="Parallel Configuration",
                position=Position(scene.canvas_width / 2, 50),
                annotation_type="label",
                style=Style(font_size=16, color="#667eea", font_weight="bold")
            )
            annotations.append(circuit_type)

        return annotations


# Factory function
def build_advanced_scene(nlp_results: Dict, problem_text: str, domain: str) -> UniversalScene:
    """
    Build an advanced scene with physics rules

    Args:
        nlp_results: NLP analysis results
        problem_text: Original problem text
        domain: Domain (electronics, physics, etc.)

    Returns:
        UniversalScene with accurate representation
    """
    builder = AdvancedSceneBuilder()

    # Route to appropriate builder based on domain and problem type
    text_lower = problem_text.lower()

    if 'capacitor' in text_lower or 'capacitance' in text_lower:
        return builder.build_capacitor_scene(nlp_results, problem_text)
    else:
        # Fall back to basic scene
        return builder.build_capacitor_scene(nlp_results, problem_text)


if __name__ == "__main__":
    print("Advanced Scene Builder - Test\n" + "=" * 50)

    # Test with a sample problem
    problem = """A potential difference of 300 V is applied to a series connection of two capacitors
    of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF."""

    nlp_results = {
        'domain': 'electronics',
        'entities': [],
        'relationships': []
    }

    builder = AdvancedSceneBuilder()
    scene = builder.build_capacitor_scene(nlp_results, problem)

    print(f"Scene created: {scene.title}")
    print(f"Objects: {len(scene.objects)}")
    print(f"Relationships: {len(scene.relationships)}")
    print(f"Annotations: {len(scene.annotations)}")

    for obj in scene.objects:
        print(f"  - {obj.id}: {obj.label} at ({obj.position.x}, {obj.position.y})")

    print("\n✅ Advanced Scene Builder test complete!")
