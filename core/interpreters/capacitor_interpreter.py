"""
CapacitorInterpreter - Converts capacitor problem specs into renderable scenes

Handles:
- Parallel-plate capacitors (with/without dielectrics)
- Series/parallel capacitor circuits
- Electric fields and charge distributions
- Battery connections
"""

from typing import Dict, List, Optional
from core.scene.schema_v1 import Scene, SceneObject, Constraint, PrimitiveType, ConstraintType, RenderLayer
from core.universal_ai_analyzer import PhysicsDomain


class CapacitorInterpreter:
    """Interprets capacitor problem specifications into visual scenes"""

    def __init__(self):
        self.canvas_width = 1200
        self.canvas_height = 800
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2

    def interpret(self, spec: Dict) -> Scene:
        """Main entry point - converts spec to Scene

        Args:
            spec: Dictionary with keys:
                - objects: List of physical objects (capacitors, dielectrics, etc.)
                - relationships: Connections between objects
                - environment: Physical constants
                - problem_text: Original problem text (for keyword detection)
                - temporal_analysis: Generic temporal analysis (optional, from TemporalAnalyzer)

        Returns:
            Scene with positioned objects and constraints
        """
        print(f"   🔌 CapacitorInterpreter: Processing {len(spec.get('objects', []))} objects")

        scene_objects = []
        constraints = []

        objects = spec.get('objects', [])
        relationships = spec.get('relationships', [])
        problem_text = spec.get('problem_text', '').lower()

        # Get temporal analysis (generic framework)
        temporal_analysis = spec.get('temporal_analysis', {})

        # Identify problem type from objects AND problem text
        has_capacitor = any('capacitor' in str(obj.get('type', '')).lower() for obj in objects)
        has_dielectric = (any('dielectric' in str(obj.get('type', '')).lower() for obj in objects) or
                         'dielectric' in problem_text)
        has_circuit = (any('battery' in str(obj.get('type', '')).lower() or
                          'wire' in str(obj.get('type', '')).lower() for obj in objects) or
                      'battery' in problem_text or 'circuit' in problem_text)
        has_series = 'series' in problem_text
        has_parallel = 'parallel' in problem_text and 'plate' not in problem_text  # Avoid "parallel-plate"
        has_cylinder = 'cylinder' in problem_text or 'cylindrical' in problem_text
        has_variable = 'variable' in problem_text

        # Use generic temporal analysis (if available)
        is_multistage = temporal_analysis.get('is_multistage', False)
        implicit_relationships = temporal_analysis.get('implicit_relationships', {})

        # Check for circuit topology from generic temporal analyzer
        if 'circuit_topology' in implicit_relationships:
            topology = implicit_relationships['circuit_topology']
            if topology == 'parallel':
                has_parallel = True
                has_series = False  # Final state is parallel, overrides initial series
                print(f"   🔄 Temporal analyzer detected final state: PARALLEL connection")
            elif topology == 'series':
                has_series = True
                has_parallel = False

        # Detect multiple dielectrics (κ₁, κ₂, κ₃ or kappa1, kappa2, kappa3)
        import re
        kappa_matches = re.findall(r'κ[₁₂₃]|kappa[_\s]*[123]', problem_text)
        has_multiple_dielectrics = len(set(kappa_matches)) >= 2

        # Detect regions (left/right, top/bottom, quarters)
        has_regions = any(word in problem_text for word in ['left half', 'right half', 'top', 'bottom', 'quarter'])

        print(f"   📝 Detected: dielectric={has_dielectric}, multi_dielectric={has_multiple_dielectrics}, regions={has_regions}, circuit={has_circuit}, series={has_series}, parallel={has_parallel}, variable={has_variable}, cylinder={has_cylinder}, multistage={is_multistage}")

        # Choose scene type based on detected features (order matters!)
        if has_cylinder:
            # Cylindrical capacitor
            scene_objects, constraints = self._create_cylindrical_capacitor(objects)
        elif has_variable:
            # Variable capacitor circuit (check before series!)
            scene_objects, constraints = self._create_variable_capacitor_circuit(objects)
        elif has_parallel and has_circuit:
            # Parallel capacitor circuit (e.g., reconnected with same signs)
            scene_objects, constraints = self._create_parallel_capacitors(objects, relationships)
        elif has_series or (has_circuit and len(objects) >= 10):
            # Series/parallel circuit with multiple capacitors
            scene_objects, constraints = self._create_circuit(objects, relationships)
        elif has_multiple_dielectrics and has_regions:
            # Multiple dielectrics in different regions
            scene_objects, constraints = self._create_multi_dielectric_capacitor(objects, problem_text)
        elif has_dielectric:
            # Single capacitor with dielectric
            scene_objects, constraints = self._create_capacitor_with_dielectric(objects)
        else:
            # Simple parallel-plate capacitor
            scene_objects, constraints = self._create_simple_capacitor(objects)

        print(f"   ✅ Created {len(scene_objects)} scene objects, {len(constraints)} constraints")

        return Scene(
            metadata={"domain": PhysicsDomain.ELECTROSTATICS.value, "renderer": "capacitor"},
            objects=scene_objects,
            constraints=constraints
        )

    def _create_simple_capacitor(self, objects: List[Dict]) -> tuple:
        """Create a simple parallel-plate capacitor"""
        scene_objects = []
        constraints = []

        # Find capacitor properties
        capacitor = next((obj for obj in objects if 'capacitor' in str(obj.get('type', '')).lower()), None)

        plate_width = 300
        plate_height = 10
        separation = 150

        if capacitor:
            props = capacitor.get('properties', {})
            # Extract separation if available
            if 'separation' in props:
                separation = props['separation'] * 10000  # Convert m to pixels (rough scale)
                separation = min(max(separation, 100), 300)  # Clamp between 100-300px

        # Top plate (positive)
        top_plate = SceneObject(
            id="plate_top",
            type=PrimitiveType.RECTANGLE,
            position={"x": self.center_x - plate_width//2, "y": self.center_y - separation//2 - plate_height},
            properties={"width": plate_width, "height": plate_height, "charge": "+Q"},
            style={"fill": "#ff4444", "stroke": "#d32f2f", "stroke_width": 2}
        )

        # Bottom plate (negative)
        bottom_plate = SceneObject(
            id="plate_bottom",
            type=PrimitiveType.RECTANGLE,
            position={"x": self.center_x - plate_width//2, "y": self.center_y + separation//2},
            properties={"width": plate_width, "height": plate_height, "charge": "-Q"},
            style={"fill": "#4444ff", "stroke": "#1976d2", "stroke_width": 2}
        )

        scene_objects.extend([top_plate, bottom_plate])

        # Add electric field lines (arrows pointing downward)
        num_field_lines = 5
        for i in range(num_field_lines):
            x_offset = (i - num_field_lines//2) * (plate_width // num_field_lines)
            field_line = SceneObject(
                id=f"field_line_{i}",
                type=PrimitiveType.ARROW,
                position={
                    "x1": self.center_x + x_offset,
                    "y1": self.center_y - separation//2 + plate_height + 10,
                    "x2": self.center_x + x_offset,
                    "y2": self.center_y + separation//2 - 10
                },
                properties={"direction": "down"},
                style={"stroke": "#ff6600", "stroke_width": 2, "marker_end": "arrowhead"}
            )
            scene_objects.append(field_line)

        # Add constraints
        constraints.append(Constraint(
            type=ConstraintType.PARALLEL,
            objects=["plate_top", "plate_bottom"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.DISTANCE,
            objects=["plate_top", "plate_bottom"],
            value=separation
        ))

        return scene_objects, constraints

    def _create_capacitor_with_dielectric(self, objects: List[Dict]) -> tuple:
        """Create capacitor with dielectric slab including detailed annotations"""
        # Start with simple capacitor
        scene_objects, constraints = self._create_simple_capacitor(objects)

        # Extract capacitor and dielectric properties
        capacitor = next((obj for obj in objects if 'capacitor' in str(obj.get('type', '')).lower()), None)
        dielectric = next((obj for obj in objects if 'dielectric' in str(obj.get('type', '')).lower()), None)

        cap_props = capacitor.get('properties', {}) if capacitor else {}
        di_props = dielectric.get('properties', {}) if dielectric else {}

        # Extract physical values
        plate_area = cap_props.get('plate_area', cap_props.get('area', ''))
        plate_sep = cap_props.get('plate_separation', cap_props.get('separation', ''))
        voltage = cap_props.get('voltage', cap_props.get('initial_potential_difference', ''))
        thickness = di_props.get('thickness', 0.004) * 10000  # Convert m to pixels
        thickness = min(max(thickness, 40), 100)  # Clamp
        kappa = di_props.get('dielectric_constant', di_props.get('kappa', di_props.get('k', ''))) if dielectric else 4.0

        # ALWAYS add dielectric slab (since this method is called when dielectric detected in problem text)
        # Add dielectric slab between plates
        dielectric_obj = SceneObject(
            id="dielectric",
            type=PrimitiveType.RECTANGLE,
            position={
                "x": self.center_x - 130,
                "y": self.center_y - thickness//2
            },
            properties={"width": 260, "height": thickness, "kappa": kappa},
            style={
                "fill": "#E3F2FD",  # Light blue instead of pattern
                "fill_opacity": 0.8,
                "stroke": "#42a5f5",
                "stroke_width": 3
            }
        )
        scene_objects.insert(2, dielectric_obj)  # Insert after plates, before field lines

        # Add CHARGE LABELS to plates
        for obj in scene_objects:
            if obj.id == 'plate_top':
                obj.properties['label'] = '+Q'
            elif obj.id == 'plate_bottom':
                obj.properties['label'] = '-Q'

        # Add DISTANCE ARROW showing plate separation
        arrow_x = self.center_x - 200
        distance_arrow = SceneObject(
            id="separation_arrow",
            type=PrimitiveType.ARROW,
            position={
                "x": arrow_x, "y": self.center_y - 75,  # Add x/y for layout engine
                "x1": arrow_x, "y1": self.center_y - 75,
                "x2": arrow_x, "y2": self.center_y + 75,
                "double_headed": True
            },
            properties={"bidirectional": True},
            style={"stroke": "#555", "stroke_width": 2, "marker_start": "arrowhead", "marker_end": "arrowhead"}
        )
        scene_objects.append(distance_arrow)

        # Add separation distance label
        if plate_sep:
            sep_label = SceneObject(
                id="separation_label",
                type=PrimitiveType.TEXT,
                position={"x": arrow_x - 40, "y": self.center_y},
                properties={"text": f"d = {plate_sep}", "font_size": 14},
                style={"fill": "#333", "font_family": "Arial"}
            )
            scene_objects.append(sep_label)

        # Add PLATE AREA annotation
        if plate_area:
            area_label = SceneObject(
                id="area_label",
                type=PrimitiveType.TEXT,
                position={"x": self.center_x, "y": self.center_y - 120},
                properties={"text": f"Area A = {plate_area}", "font_size": 14},
                style={"fill": "#333", "font_family": "Arial", "text_anchor": "middle"}
            )
            scene_objects.append(area_label)

        # Add VOLTAGE annotation
        if voltage:
            voltage_label = SceneObject(
                id="voltage_label",
                type=PrimitiveType.TEXT,
                position={"x": self.center_x + 200, "y": self.center_y},
                properties={"text": f"V = {voltage}", "font_size": 16, "font_weight": "bold"},
                style={"fill": "#e65100", "font_family": "Arial"}
            )
            scene_objects.append(voltage_label)

        # Add DIELECTRIC CONSTANT label
        if kappa:
            kappa_label = SceneObject(
                id="kappa_label",
                type=PrimitiveType.TEXT,
                position={"x": self.center_x, "y": self.center_y + 130},
                properties={"text": f"κ = {kappa}", "font_size": 14, "font_weight": "bold"},
                style={"fill": "#1565c0", "font_family": "Arial", "text_anchor": "middle"}
            )
            scene_objects.append(kappa_label)

        # Add dielectric thickness annotation
        if dielectric:
            thickness_label = SceneObject(
                id="thickness_label",
                type=PrimitiveType.TEXT,
                position={"x": self.center_x - 50, "y": self.center_y + 50},
                properties={"text": f"t = {di_props.get('thickness', '')}", "font_size": 12},
                style={"fill": "#42a5f5", "font_family": "Arial"}
            )
            scene_objects.append(thickness_label)

        return scene_objects, constraints

    def _create_multi_dielectric_capacitor(self, objects: List[Dict], problem_text: str) -> tuple:
        """Create capacitor with multiple dielectrics in different regions

        Handles cases like:
        - Left half κ₁, right half divided into top κ₂ and bottom κ₃
        - Top/bottom/left/right regions with different dielectrics
        """
        import re
        scene_objects = []
        constraints = []

        # DECLARATIVE APPROACH: Specify WHAT and dimensions, not WHERE
        # Layout engine will position based on constraints
        plate_width = 400
        plate_height = 12
        separation = 180  # Distance between plates (used in DISTANCE constraint)

        # Define plates with dimensions only (NO manual positioning)
        top_plate = SceneObject(
            id="plate_top",
            type=PrimitiveType.RECTANGLE,
            position=None,  # Layout engine will position this
            properties={"width": plate_width, "height": plate_height, "charge": "+Q"},
            style={"fill": "#ff4444", "stroke": "#d32f2f", "stroke_width": 2},
            layer=RenderLayer.SHAPES
        )

        bottom_plate = SceneObject(
            id="plate_bottom",
            type=PrimitiveType.RECTANGLE,
            position=None,  # Layout engine will position this
            properties={"width": plate_width, "height": plate_height, "charge": "-Q"},
            style={"fill": "#4444ff", "stroke": "#1976d2", "stroke_width": 2},
            layer=RenderLayer.SHAPES
        )

        scene_objects.extend([top_plate, bottom_plate])

        # Extract kappa values from problem text
        # Pattern matches numbers like 21.0 or 3 but not trailing periods
        kappa_pattern = r'κ[₁₂₃]\s*=\s*(\d+(?:\.\d+)?)|kappa[_\s]*([123])\s*=\s*(\d+(?:\.\d+)?)'
        kappa_matches = re.findall(kappa_pattern, problem_text)

        kappas = {}
        for match in kappa_matches:
            if match[0]:  # κ₁ = 21.0 format
                kappa_val = float(match[0])
                # Determine which kappa based on context
                if 'κ₁' in problem_text or 'κ1' in problem_text:
                    kappas['k1'] = kappa_val
            # Extract from objects as fallback

        # Simpler: extract all numbers after κ or kappa
        k1_match = re.search(r'κ[₁1]\s*=\s*(\d+(?:\.\d+)?)|left.*?(\d+(?:\.\d+)?)', problem_text)
        k2_match = re.search(r'κ[₂2]\s*=\s*(\d+(?:\.\d+)?)|top.*?(\d+(?:\.\d+)?)', problem_text)
        k3_match = re.search(r'κ[₃3]\s*=\s*(\d+(?:\.\d+)?)|bottom.*?(\d+(?:\.\d+)?)', problem_text)

        k1 = float(k1_match.group(1) or k1_match.group(2)) if k1_match and (k1_match.group(1) or k1_match.group(2)) else 2.5
        k2 = float(k2_match.group(1) or k2_match.group(2)) if k2_match and (k2_match.group(1) or k2_match.group(2)) else 4.0
        k3 = float(k3_match.group(1) or k3_match.group(2)) if k3_match and (k3_match.group(1) or k3_match.group(2)) else 1.5

        # DECLARATIVE APPROACH: Specify dimensions, layout engine positions
        # Define dielectric regions with dimensions only (NO manual positioning)
        dielectric_height_full = separation
        dielectric_height_half = separation // 2

        # Region 1: Left half (κ₁) - full height
        # Provide initial X position to help layout engine
        dielectric1 = SceneObject(
            id="dielectric_left",
            type=PrimitiveType.RECTANGLE,
            position={'x': self.center_x - plate_width//2, 'y': None},  # X positioned on left, Y will be set by BETWEEN
            properties={"width": plate_width//2, "height": dielectric_height_full, "kappa": k1},
            style={
                "fill": "#BBDEFB",
                "fill_opacity": 0.6,
                "stroke": "#1976D2",
                "stroke_width": 1
            },
            layer=RenderLayer.FILL
        )

        # Region 2: Right top half (κ₂)
        # Provide initial X position to help layout engine
        dielectric2 = SceneObject(
            id="dielectric_right_top",
            type=PrimitiveType.RECTANGLE,
            position={'x': self.center_x, 'y': None},  # X positioned on right, Y will be set by BETWEEN
            properties={"width": plate_width//2, "height": dielectric_height_half, "kappa": k2},
            style={
                "fill": "#C5E1A5",
                "fill_opacity": 0.6,
                "stroke": "#689F38",
                "stroke_width": 1
            },
            layer=RenderLayer.FILL
        )

        # Region 3: Right bottom half (κ₃)
        # Provide initial X position to help layout engine
        dielectric3 = SceneObject(
            id="dielectric_right_bottom",
            type=PrimitiveType.RECTANGLE,
            position={'x': self.center_x, 'y': None},  # X positioned on right, Y will be set by STACKED_V
            properties={"width": plate_width//2, "height": dielectric_height_half, "kappa": k3},
            style={
                "fill": "#FFCCBC",
                "fill_opacity": 0.6,
                "stroke": "#E64A19",
                "stroke_width": 1
            },
            layer=RenderLayer.FILL
        )

        scene_objects.extend([dielectric1, dielectric2, dielectric3])

        # Add labels for each dielectric - LET INTELLIGENT PLACER POSITION THEM
        label1 = SceneObject(
            id="label_k1",
            type=PrimitiveType.TEXT,
            position=None,  # Let intelligent label placer determine position
            properties={
                "text": f"κ₁ = {k1}",
                "font_size": 16,
                "font_weight": "bold",
                "target_object": "dielectric_left"  # Associate with target
            },
            style={"fill": "#0D47A1", "font_family": "Arial", "text_anchor": "middle"},
            layer=RenderLayer.LABELS  # Labels always on top
        )

        label2 = SceneObject(
            id="label_k2",
            type=PrimitiveType.TEXT,
            position=None,  # Let intelligent label placer determine position
            properties={
                "text": f"κ₂ = {k2}",
                "font_size": 16,
                "font_weight": "bold",
                "target_object": "dielectric_right_top"
            },
            style={"fill": "#33691E", "font_family": "Arial", "text_anchor": "middle"},
            layer=RenderLayer.LABELS
        )

        label3 = SceneObject(
            id="label_k3",
            type=PrimitiveType.TEXT,
            position=None,  # Let intelligent label placer determine position
            properties={
                "text": f"κ₃ = {k3}",
                "font_size": 16,
                "font_weight": "bold",
                "target_object": "dielectric_right_bottom"
            },
            style={"fill": "#BF360C", "font_family": "Arial", "text_anchor": "middle"},
            layer=RenderLayer.LABELS
        )

        scene_objects.extend([label1, label2, label3])

        # Add region boundary lines
        # Vertical line separating left/right
        vert_line = SceneObject(
            id="boundary_vertical",
            type=PrimitiveType.LINE,
            position={
                "x": self.center_x, "y": self.center_y - separation//2,
                "x1": self.center_x, "y1": self.center_y - separation//2,
                "x2": self.center_x, "y2": self.center_y + separation//2
            },
            properties={},
            style={"stroke": "#000", "stroke_width": 2, "stroke_dasharray": "5,5"}
        )

        # Horizontal line separating top/bottom on right
        horiz_line = SceneObject(
            id="boundary_horizontal",
            type=PrimitiveType.LINE,
            position={
                "x": self.center_x, "y": self.center_y,
                "x1": self.center_x, "y1": self.center_y,
                "x2": self.center_x + plate_width//2, "y2": self.center_y
            },
            properties={},
            style={"stroke": "#000", "stroke_width": 2, "stroke_dasharray": "5,5"}
        )

        scene_objects.extend([vert_line, horiz_line])

        # Add annotations for "Left Half" and "Right Half"
        left_label = SceneObject(
            id="region_left",
            type=PrimitiveType.TEXT,
            position={"x": self.center_x - plate_width//4, "y": self.center_y - separation//2 - 40},
            properties={"text": "Left Half", "font_size": 14},
            style={"fill": "#555", "font_family": "Arial", "text_anchor": "middle"}
        )

        right_label = SceneObject(
            id="region_right",
            type=PrimitiveType.TEXT,
            position={"x": self.center_x + plate_width//4, "y": self.center_y - separation//2 - 40},
            properties={"text": "Right Half", "font_size": 14},
            style={"fill": "#555", "font_family": "Arial", "text_anchor": "middle"}
        )

        scene_objects.extend([left_label, right_label])

        # Add constraints
        constraints.append(Constraint(
            type=ConstraintType.PARALLEL,
            objects=["plate_top", "plate_bottom"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.DISTANCE,
            objects=["plate_top", "plate_bottom"],
            value=separation
        ))

        # GENERIC SPATIAL CONSTRAINTS for dielectric positioning
        # These tell layout engine HOW objects relate, not WHERE they go

        # Constraint 1: All dielectrics are BETWEEN the plates (fill space vertically)
        constraints.append(Constraint(
            type=ConstraintType.BETWEEN,
            objects=["dielectric_left", "plate_top", "plate_bottom"]
        ))
        constraints.append(Constraint(
            type=ConstraintType.BETWEEN,
            objects=["dielectric_right_top", "plate_top", "plate_bottom"]
        ))
        constraints.append(Constraint(
            type=ConstraintType.BETWEEN,
            objects=["dielectric_right_bottom", "plate_top", "plate_bottom"]
        ))

        # Constraint 2: Left and right_top dielectrics are ADJACENT (touch horizontally)
        # Only constrain the TOP right dielectric - the bottom will be positioned by STACKED_V
        constraints.append(Constraint(
            type=ConstraintType.ADJACENT,
            objects=["dielectric_left", "dielectric_right_top"]
        ))

        # Constraint 3: Right dielectrics are STACKED_V (top to bottom with no gap)
        # This will position right_bottom below right_top automatically
        constraints.append(Constraint(
            type=ConstraintType.STACKED_V,
            objects=["dielectric_right_top", "dielectric_right_bottom"],
            value=0  # No gap between stacked objects
        ))

        # NOTE: No ALIGNED_H constraint needed - BETWEEN constraints already position
        # dielectrics at the correct Y position between plates

        return scene_objects, constraints

    def _create_circuit(self, objects: List[Dict], relationships: List[Dict]) -> tuple:
        """Create circuit with multiple capacitors"""
        scene_objects = []
        constraints = []

        # Identify capacitors
        capacitors = [obj for obj in objects if 'capacitor' in str(obj.get('type', '')).lower()]
        battery = next((obj for obj in objects if 'battery' in str(obj.get('type', '')).lower()), None)

        num_caps = len(capacitors)

        if num_caps == 2:
            # Two capacitors - likely series
            scene_objects, constraints = self._create_series_capacitors(capacitors, battery)
        elif num_caps == 3:
            # Three capacitors - check relationships for series/parallel
            scene_objects, constraints = self._create_three_capacitor_circuit(capacitors, relationships, battery)
        else:
            # Fallback to simple capacitor
            scene_objects, constraints = self._create_simple_capacitor(objects)

        return scene_objects, constraints

    def _create_series_capacitors(self, capacitors: List[Dict], battery: Optional[Dict]) -> tuple:
        """Create two capacitors in series"""
        scene_objects = []
        constraints = []

        # Battery on left
        if battery:
            voltage = battery.get('properties', {}).get('voltage', 0)
            battery_obj = SceneObject(
                id="battery",
                type=PrimitiveType.RECTANGLE,
                position={"x": 200, "y": self.center_y - 40},
                properties={"width": 30, "height": 80, "voltage": voltage},
                style={"fill": "#555", "stroke": "#333", "stroke_width": 2}
            )
            scene_objects.append(battery_obj)

        # Capacitor 1 (top)
        cap1_obj = SceneObject(
            id="capacitor_1",
            type=PrimitiveType.RECTANGLE,
            position={"x": 370, "y": 250},
            properties={"capacitance": capacitors[0].get('properties', {}).get('capacitance', 0)},
            style={"fill": "none", "stroke": "#2c3e50", "stroke_width": 4}
        )
        scene_objects.append(cap1_obj)

        # Capacitor 2 (bottom)
        cap2_obj = SceneObject(
            id="capacitor_2",
            type=PrimitiveType.RECTANGLE,
            position={"x": 620, "y": 250},
            properties={"capacitance": capacitors[1].get('properties', {}).get('capacitance', 0) if len(capacitors) > 1 else 0},
            style={"fill": "none", "stroke": "#2c3e50", "stroke_width": 4}
        )
        scene_objects.append(cap2_obj)

        # Add wires connecting them
        wires = [
            # Battery to C1
            {"id": "wire1", "x1": 230, "y1": self.center_y, "x2": 370, "y2": self.center_y},
            # C1 to C2
            {"id": "wire2", "x1": 430, "y1": self.center_y, "x2": 620, "y2": self.center_y},
            # C2 back to battery
            {"id": "wire3", "x1": 680, "y1": self.center_y, "x2": 750, "y2": self.center_y},
            {"id": "wire4", "x1": 750, "y1": self.center_y, "x2": 750, "y2": self.center_y + 200},
            {"id": "wire5", "x1": 750, "y1": self.center_y + 200, "x2": 200, "y2": self.center_y + 200},
            {"id": "wire6", "x1": 200, "y1": self.center_y + 200, "x2": 200, "y2": self.center_y + 40}
        ]

        for wire in wires:
            wire_obj = SceneObject(
                id=wire["id"],
                type=PrimitiveType.LINE,
                position={"x": wire["x1"], "y": wire["y1"], "x1": wire["x1"], "y1": wire["y1"], "x2": wire["x2"], "y2": wire["y2"]},  # Add x/y for layout engine
                properties={},
                style={"stroke": "#2c3e50", "stroke_width": 3}
            )
            scene_objects.append(wire_obj)

        return scene_objects, constraints

    def _create_parallel_capacitors(self, objects: List[Dict], relationships: List[Dict]) -> tuple:
        """Create two or more capacitors connected in parallel (positive-to-positive, negative-to-negative)

        This represents the FINAL STATE after capacitors are reconnected with plates of same signs together.
        """
        scene_objects = []
        constraints = []

        # Identify capacitors (should be 2 in this case)
        capacitors = [obj for obj in objects if 'capacitor' in str(obj.get('type', '')).lower()]

        if len(capacitors) < 2:
            # Fallback to simple capacitor
            return self._create_simple_capacitor(objects)

        num_caps = len(capacitors)

        # Layout: Capacitors side-by-side, connected at top and bottom rails
        cap_width = 60
        cap_height = 150
        spacing = 100  # Horizontal spacing between capacitors

        # Calculate starting X position to center the array
        total_width = num_caps * cap_width + (num_caps - 1) * spacing
        start_x = self.center_x - total_width // 2

        # Create capacitor symbols (vertical parallel plates)
        for i, cap in enumerate(capacitors):
            cap_id = f"capacitor_{i+1}"
            x_pos = start_x + i * (cap_width + spacing)

            # Get capacitance value
            cap_props = cap.get('properties', {})
            capacitance = cap_props.get('capacitance', f'C{i+1}')

            # Left plate of capacitor
            left_plate = SceneObject(
                id=f"{cap_id}_left_plate",
                type=PrimitiveType.RECTANGLE,
                position={"x": x_pos, "y": self.center_y - cap_height//2},
                properties={"width": 8, "height": cap_height, "charge": "+Q"},
                style={"fill": "#ff4444", "stroke": "#d32f2f", "stroke_width": 2}
            )

            # Right plate of capacitor
            right_plate = SceneObject(
                id=f"{cap_id}_right_plate",
                type=PrimitiveType.RECTANGLE,
                position={"x": x_pos + cap_width - 8, "y": self.center_y - cap_height//2},
                properties={"width": 8, "height": cap_height, "charge": "-Q"},
                style={"fill": "#4444ff", "stroke": "#1976d2", "stroke_width": 2}
            )

            scene_objects.extend([left_plate, right_plate])

            # Add capacitance label below each capacitor
            label = SceneObject(
                id=f"{cap_id}_label",
                type=PrimitiveType.TEXT,
                position={"x": x_pos + cap_width//2, "y": self.center_y + cap_height//2 + 30},
                properties={"text": str(capacitance), "font_size": 14, "font_weight": "bold"},
                style={"fill": "#333", "font_family": "Arial", "text_anchor": "middle"}
            )
            scene_objects.append(label)

        # Add top rail (connecting all positive plates)
        top_rail_y = self.center_y - cap_height//2 - 30
        top_rail = SceneObject(
            id="top_rail",
            type=PrimitiveType.LINE,
            position={
                "x": start_x, "y": top_rail_y,
                "x1": start_x, "y1": top_rail_y,
                "x2": start_x + total_width, "y2": top_rail_y
            },
            properties={},
            style={"stroke": "#ff4444", "stroke_width": 4}
        )
        scene_objects.append(top_rail)

        # Add bottom rail (connecting all negative plates)
        bottom_rail_y = self.center_y + cap_height//2 + 30
        bottom_rail = SceneObject(
            id="bottom_rail",
            type=PrimitiveType.LINE,
            position={
                "x": start_x, "y": bottom_rail_y,
                "x1": start_x, "y1": bottom_rail_y,
                "x2": start_x + total_width, "y2": bottom_rail_y
            },
            properties={},
            style={"stroke": "#4444ff", "stroke_width": 4}
        )
        scene_objects.append(bottom_rail)

        # Add vertical wires connecting each capacitor to the rails
        for i in range(num_caps):
            x_pos = start_x + i * (cap_width + spacing)

            # Wire from top rail to positive plate
            top_wire = SceneObject(
                id=f"wire_top_{i+1}",
                type=PrimitiveType.LINE,
                position={
                    "x": x_pos + 4, "y": top_rail_y,
                    "x1": x_pos + 4, "y1": top_rail_y,
                    "x2": x_pos + 4, "y2": self.center_y - cap_height//2
                },
                properties={},
                style={"stroke": "#ff4444", "stroke_width": 3}
            )

            # Wire from bottom rail to negative plate
            bottom_wire = SceneObject(
                id=f"wire_bottom_{i+1}",
                type=PrimitiveType.LINE,
                position={
                    "x": x_pos + cap_width - 4, "y": self.center_y + cap_height//2,
                    "x1": x_pos + cap_width - 4, "y1": self.center_y + cap_height//2,
                    "x2": x_pos + cap_width - 4, "y2": bottom_rail_y
                },
                properties={},
                style={"stroke": "#4444ff", "stroke_width": 3}
            )

            scene_objects.extend([top_wire, bottom_wire])

        # Add annotation showing parallel connection
        parallel_label = SceneObject(
            id="parallel_label",
            type=PrimitiveType.TEXT,
            position={"x": self.center_x, "y": top_rail_y - 30},
            properties={"text": "Parallel Connection (same signs together)", "font_size": 16, "font_weight": "bold"},
            style={"fill": "#e65100", "font_family": "Arial", "text_anchor": "middle"}
        )
        scene_objects.append(parallel_label)

        # Add constraints
        constraints.append(Constraint(
            type=ConstraintType.PARALLEL,
            objects=[f"capacitor_{i+1}_left_plate" for i in range(num_caps)]
        ))

        return scene_objects, constraints

    def _create_three_capacitor_circuit(self, capacitors: List[Dict], relationships: List[Dict], battery: Optional[Dict]) -> tuple:
        """Create circuit with 3 capacitors (C1 in series with parallel C2||C3)"""
        # For now, create a simple layout
        # TODO: Parse relationships to determine exact topology
        scene_objects, constraints = self._create_series_capacitors(capacitors[:2], battery)
        return scene_objects, constraints

    def _create_cylindrical_capacitor(self, objects: List[Dict]) -> tuple:
        """Create a cylindrical capacitor (coaxial cylinders)"""
        scene_objects = []
        constraints = []

        # Draw two concentric cylinders
        outer_radius = 120
        inner_radius = 60

        # Outer cylinder
        outer_cyl = SceneObject(
            id="outer_cylinder",
            type=PrimitiveType.CIRCLE,
            position={"x": self.center_x, "y": self.center_y, "cx": self.center_x, "cy": self.center_y},
            properties={"radius": outer_radius, "charge": "-Q"},
            style={"fill": "none", "stroke": "#4444ff", "stroke_width": 4}
        )
        scene_objects.append(outer_cyl)

        # Inner cylinder
        inner_cyl = SceneObject(
            id="inner_cylinder",
            type=PrimitiveType.CIRCLE,
            position={"x": self.center_x, "y": self.center_y, "cx": self.center_x, "cy": self.center_y},
            properties={"radius": inner_radius, "charge": "+Q"},
            style={"fill": "none", "stroke": "#ff4444", "stroke_width": 4}
        )
        scene_objects.append(inner_cyl)

        # Add radial field lines
        import math
        num_field_lines = 8
        for i in range(num_field_lines):
            angle = i * (2 * math.pi / num_field_lines)
            x1 = self.center_x + inner_radius * math.cos(angle)
            y1 = self.center_y + inner_radius * math.sin(angle)
            x2 = self.center_x + outer_radius * math.cos(angle)
            y2 = self.center_y + outer_radius * math.sin(angle)

            field_line = SceneObject(
                id=f"field_line_{i}",
                type=PrimitiveType.ARROW,
                position={"x": x1, "y": y1, "x1": x1, "y1": y1, "x2": x2, "y2": y2},  # Add x/y for layout engine
                properties={"direction": "radial"},
                style={"stroke": "#ff6600", "stroke_width": 2, "marker_end": "arrowhead"}
            )
            scene_objects.append(field_line)

        # Add labels
        inner_label = SceneObject(
            id="inner_label",
            type=PrimitiveType.TEXT,
            position={"x": self.center_x, "y": self.center_y - inner_radius - 20},
            properties={"text": "Inner: +Q", "font_size": 14},
            style={"fill": "#ff4444", "font_family": "Arial", "text_anchor": "middle"}
        )
        scene_objects.append(inner_label)

        outer_label = SceneObject(
            id="outer_label",
            type=PrimitiveType.TEXT,
            position={"x": self.center_x, "y": self.center_y - outer_radius - 20},
            properties={"text": "Outer: -Q", "font_size": 14},
            style={"fill": "#4444ff", "font_family": "Arial", "text_anchor": "middle"}
        )
        scene_objects.append(outer_label)

        return scene_objects, constraints

    def _create_variable_capacitor_circuit(self, objects: List[Dict]) -> tuple:
        """Create circuit with variable capacitor and other capacitors"""
        scene_objects = []
        constraints = []

        # Create 3 capacitors in a mixed configuration
        # C1 and C2 in parallel, then in series with C3 (variable)

        # Battery on left
        battery_obj = SceneObject(
            id="battery",
            type=PrimitiveType.RECTANGLE,
            position={"x": 150, "y": self.center_y - 40},
            properties={"width": 30, "height": 80, "voltage": "V"},
            style={"fill": "#555", "stroke": "#333", "stroke_width": 2}
        )
        scene_objects.append(battery_obj)

        # C1 (top parallel)
        c1_obj = SceneObject(
            id="capacitor_1",
            type=PrimitiveType.RECTANGLE,
            position={"x": 350, "y": 220},
            properties={"capacitance": "C₁", "width": 40, "height": 80},
            style={"fill": "none", "stroke": "#2c3e50", "stroke_width": 4}
        )
        scene_objects.append(c1_obj)

        # C2 (bottom parallel)
        c2_obj = SceneObject(
            id="capacitor_2",
            type=PrimitiveType.RECTANGLE,
            position={"x": 350, "y": 480},
            properties={"capacitance": "C₂", "width": 40, "height": 80},
            style={"fill": "none", "stroke": "#2c3e50", "stroke_width": 4}
        )
        scene_objects.append(c2_obj)

        # C3 (variable, in series)
        c3_obj = SceneObject(
            id="capacitor_3",
            type=PrimitiveType.RECTANGLE,
            position={"x": 650, "y": self.center_y - 40},
            properties={"capacitance": "C₃ (variable)", "width": 40, "height": 80},
            style={"fill": "none", "stroke": "#e65100", "stroke_width": 5}
        )
        scene_objects.append(c3_obj)

        # Add arrow to indicate variability
        variable_arrow = SceneObject(
            id="variable_arrow",
            type=PrimitiveType.ARROW,
            position={"x": 640, "y": self.center_y + 60, "x1": 640, "y1": self.center_y + 60, "x2": 700, "y2": self.center_y + 60, "double_headed": True},
            properties={"bidirectional": True},
            style={"stroke": "#e65100", "stroke_width": 2, "marker_start": "arrowhead", "marker_end": "arrowhead"}
        )
        scene_objects.append(variable_arrow)

        # Variable label
        var_label = SceneObject(
            id="variable_label",
            type=PrimitiveType.TEXT,
            position={"x": 670, "y": self.center_y + 90},
            properties={"text": "Variable", "font_size": 12, "font_weight": "bold"},
            style={"fill": "#e65100", "font_family": "Arial", "text_anchor": "middle"}
        )
        scene_objects.append(var_label)

        # Wires connecting everything
        wires = [
            # Battery to split
            {"id": "wire1", "x1": 180, "y1": self.center_y, "x2": 300, "y2": self.center_y},
            # Split to C1 top
            {"id": "wire2", "x1": 300, "y1": self.center_y, "x2": 300, "y2": 260},
            {"id": "wire3", "x1": 300, "y1": 260, "x2": 350, "y2": 260},
            # Split to C2 bottom
            {"id": "wire4", "x1": 300, "y1": self.center_y, "x2": 300, "y2": 520},
            {"id": "wire5", "x1": 300, "y1": 520, "x2": 350, "y2": 520},
            # C1 and C2 to junction
            {"id": "wire6", "x1": 390, "y1": 260, "x2": 500, "y2": 260},
            {"id": "wire7", "x1": 390, "y1": 520, "x2": 500, "y2": 520},
            {"id": "wire8", "x1": 500, "y1": 260, "x2": 500, "y2": self.center_y},
            {"id": "wire9", "x1": 500, "y1": 520, "x2": 500, "y2": self.center_y},
            # Junction to C3
            {"id": "wire10", "x1": 500, "y1": self.center_y, "x2": 650, "y2": self.center_y},
            # C3 back to battery
            {"id": "wire11", "x1": 690, "y1": self.center_y, "x2": 850, "y2": self.center_y},
            {"id": "wire12", "x1": 850, "y1": self.center_y, "x2": 850, "y2": self.center_y + 200},
            {"id": "wire13", "x1": 850, "y1": self.center_y + 200, "x2": 150, "y2": self.center_y + 200},
            {"id": "wire14", "x1": 150, "y1": self.center_y + 200, "x2": 150, "y2": self.center_y + 40}
        ]

        for wire in wires:
            wire_obj = SceneObject(
                id=wire["id"],
                type=PrimitiveType.LINE,
                position={"x": wire["x1"], "y": wire["y1"], "x1": wire["x1"], "y1": wire["y1"], "x2": wire["x2"], "y2": wire["y2"]},  # Add x/y for layout engine
                properties={},
                style={"stroke": "#2c3e50", "stroke_width": 3}
            )
            scene_objects.append(wire_obj)

        return scene_objects, constraints
