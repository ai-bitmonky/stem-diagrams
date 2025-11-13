"""
Universal SVG Rendering Engine for All STEM Diagrams
====================================================

This module provides a comprehensive SVG rendering engine that can convert
UniversalScene objects into professional, publication-quality SVG diagrams.

Features:
- Domain-specific renderers for all STEM subjects
- Component library for common objects (resistors, atoms, cells, etc.)
- Automatic layout and positioning
- Professional styling and theming
- Annotations and labels
- Export to file or string

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import List, Dict, Optional, Tuple
from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Annotation,
    ObjectType, RelationType, Position, Style
)
import xml.etree.ElementTree as ET
from xml.dom import minidom


class SVGElement:
    """Helper class for building SVG elements"""

    def __init__(self, tag: str, **attributes):
        self.tag = tag
        self.attributes = attributes
        self.children: List['SVGElement'] = []
        self.text: Optional[str] = None

    def add_child(self, child: 'SVGElement') -> 'SVGElement':
        """Add a child element"""
        self.children.append(child)
        return child

    def set_text(self, text: str) -> None:
        """Set text content"""
        self.text = text

    def to_element(self) -> ET.Element:
        """Convert to xml.etree.ElementTree.Element"""
        elem = ET.Element(self.tag, self.attributes)
        if self.text:
            elem.text = self.text
        for child in self.children:
            elem.append(child.to_element())
        return elem

    def to_string(self, indent: bool = True) -> str:
        """Convert to SVG string"""
        elem = self.to_element()
        if indent:
            rough_string = ET.tostring(elem, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
        return ET.tostring(elem, encoding='unicode')


class ComponentLibrary:
    """
    Library of reusable SVG components for common STEM objects
    Each method returns an SVGElement that can be added to the scene
    """

    @staticmethod
    def create_resistor(x: float, y: float, width: float, height: float,
                       style: Style, label: Optional[str] = None) -> SVGElement:
        """Create a resistor symbol (zigzag)"""
        group = SVGElement("g", id=f"resistor_{x}_{y}")

        # Resistor zigzag path
        zigzag_height = height
        zigzag_width = width * 0.6
        x_start = x - zigzag_width / 2
        y_center = y

        # Create zigzag path
        path_data = f"M {x_start} {y_center} "
        segments = 6
        segment_width = zigzag_width / segments
        for i in range(segments):
            x_seg = x_start + (i + 0.5) * segment_width
            y_seg = y_center + (zigzag_height / 2 if i % 2 == 0 else -zigzag_height / 2)
            path_data += f"L {x_seg} {y_seg} "
        path_data += f"L {x_start + zigzag_width} {y_center}"

        resistor_path = SVGElement("path",
                                   d=path_data,
                                   stroke=style.color,
                                   fill="none",
                                   **{"stroke-width": str(style.stroke_width)})
        group.add_child(resistor_path)

        # Connection lines
        left_line = SVGElement("line",
                              x1=str(x - width / 2), y1=str(y),
                              x2=str(x_start), y2=str(y_center),
                              stroke=style.color,
                              **{"stroke-width": str(style.stroke_width)})
        group.add_child(left_line)

        right_line = SVGElement("line",
                               x1=str(x_start + zigzag_width), y1=str(y_center),
                               x2=str(x + width / 2), y2=str(y),
                               stroke=style.color,
                               **{"stroke-width": str(style.stroke_width)})
        group.add_child(right_line)

        # Label
        if label:
            text = SVGElement("text",
                            x=str(x), y=str(y - zigzag_height),
                            **{"text-anchor": "middle",
                               "font-size": str(style.font_size),
                               "font-family": style.font_family})
            text.set_text(label)
            group.add_child(text)

        return group

    @staticmethod
    def create_capacitor(x: float, y: float, width: float, height: float,
                        style: Style, label: Optional[str] = None) -> SVGElement:
        """Create a capacitor symbol (two parallel plates)"""
        group = SVGElement("g", id=f"capacitor_{x}_{y}")

        plate_spacing = width * 0.2
        plate_width = 2

        # Left plate
        left_plate = SVGElement("line",
                               x1=str(x - plate_spacing / 2), y1=str(y - height / 2),
                               x2=str(x - plate_spacing / 2), y2=str(y + height / 2),
                               stroke=style.color,
                               **{"stroke-width": str(plate_width)})
        group.add_child(left_plate)

        # Right plate
        right_plate = SVGElement("line",
                                x1=str(x + plate_spacing / 2), y1=str(y - height / 2),
                                x2=str(x + plate_spacing / 2), y2=str(y + height / 2),
                                stroke=style.color,
                                **{"stroke-width": str(plate_width)})
        group.add_child(right_plate)

        # Connection lines
        left_line = SVGElement("line",
                              x1=str(x - width / 2), y1=str(y),
                              x2=str(x - plate_spacing / 2), y2=str(y),
                              stroke=style.color,
                              **{"stroke-width": str(style.stroke_width)})
        group.add_child(left_line)

        right_line = SVGElement("line",
                               x1=str(x + plate_spacing / 2), y1=str(y),
                               x2=str(x + width / 2), y2=str(y),
                               stroke=style.color,
                               **{"stroke-width": str(style.stroke_width)})
        group.add_child(right_line)

        # Label
        if label:
            text = SVGElement("text",
                            x=str(x), y=str(y - height / 2 - 10),
                            **{"text-anchor": "middle",
                               "font-size": str(style.font_size),
                               "font-family": style.font_family})
            text.set_text(label)
            group.add_child(text)

        return group

    @staticmethod
    def create_battery(x: float, y: float, width: float, height: float,
                      style: Style, label: Optional[str] = None) -> SVGElement:
        """Create a battery symbol"""
        group = SVGElement("g", id=f"battery_{x}_{y}")

        # Long positive plate
        long_plate = SVGElement("line",
                               x1=str(x - 5), y1=str(y - height / 2),
                               x2=str(x - 5), y2=str(y + height / 2),
                               stroke=style.color,
                               **{"stroke-width": "3"})
        group.add_child(long_plate)

        # Short negative plate
        short_height = height * 0.6
        short_plate = SVGElement("line",
                                x1=str(x + 5), y1=str(y - short_height / 2),
                                x2=str(x + 5), y2=str(y + short_height / 2),
                                stroke=style.color,
                                **{"stroke-width": "2"})
        group.add_child(short_plate)

        # Connection lines
        left_line = SVGElement("line",
                              x1=str(x - width / 2), y1=str(y),
                              x2=str(x - 5), y2=str(y),
                              stroke=style.color,
                              **{"stroke-width": str(style.stroke_width)})
        group.add_child(left_line)

        right_line = SVGElement("line",
                               x1=str(x + 5), y1=str(y),
                               x2=str(x + width / 2), y2=str(y),
                               stroke=style.color,
                               **{"stroke-width": str(style.stroke_width)})
        group.add_child(right_line)

        # Plus sign for positive terminal
        plus_size = 8
        plus_x = x - 5 - 15
        plus = SVGElement("text",
                         x=str(plus_x), y=str(y + 5),
                         **{"text-anchor": "middle",
                            "font-size": "18",
                            "font-weight": "bold",
                            "fill": style.color})
        plus.set_text("+")
        group.add_child(plus)

        # Label
        if label:
            text = SVGElement("text",
                            x=str(x), y=str(y - height / 2 - 15),
                            **{"text-anchor": "middle",
                               "font-size": str(style.font_size),
                               "font-family": style.font_family})
            text.set_text(label)
            group.add_child(text)

        return group

    @staticmethod
    def create_atom(x: float, y: float, radius: float, style: Style,
                   element: str = "C", electrons: int = 6) -> SVGElement:
        """Create an atom with nucleus and electron cloud"""
        group = SVGElement("g", id=f"atom_{element}_{x}_{y}")

        # Nucleus
        nucleus = SVGElement("circle",
                            cx=str(x), cy=str(y), r=str(radius * 0.3),
                            fill=style.fill_color or "#FF6B6B",
                            stroke=style.color,
                            **{"stroke-width": str(style.stroke_width)})
        group.add_child(nucleus)

        # Element label in nucleus
        label = SVGElement("text",
                          x=str(x), y=str(y + 5),
                          **{"text-anchor": "middle",
                             "font-size": str(style.font_size),
                             "font-weight": "bold",
                             "fill": "#FFFFFF"})
        label.set_text(element)
        group.add_child(label)

        # Electron orbits
        import math
        num_orbits = (electrons + 1) // 2
        for i in range(num_orbits):
            orbit_radius = radius * (0.6 + i * 0.2)
            orbit = SVGElement("circle",
                              cx=str(x), cy=str(y), r=str(orbit_radius),
                              fill="none",
                              stroke=style.color,
                              opacity="0.3",
                              **{"stroke-width": "1"})
            group.add_child(orbit)

            # Electrons on this orbit
            electrons_on_orbit = min(2, electrons - i * 2)
            for j in range(electrons_on_orbit):
                angle = (j / electrons_on_orbit) * 2 * math.pi
                ex = x + orbit_radius * math.cos(angle)
                ey = y + orbit_radius * math.sin(angle)
                electron = SVGElement("circle",
                                     cx=str(ex), cy=str(ey), r="4",
                                     fill="#4ECDC4",
                                     stroke=style.color,
                                     **{"stroke-width": "1"})
                group.add_child(electron)

        return group

    @staticmethod
    def create_bond(x1: float, y1: float, x2: float, y2: float,
                   bond_order: int, style: Style) -> SVGElement:
        """Create a chemical bond (single, double, or triple)"""
        group = SVGElement("g", id=f"bond_{x1}_{y1}_{x2}_{y2}")

        import math
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)

        # Perpendicular offset for multiple bonds
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)
        offset = 3

        if bond_order == 1:
            # Single bond
            line = SVGElement("line",
                             x1=str(x1), y1=str(y1),
                             x2=str(x2), y2=str(y2),
                             stroke=style.color,
                             **{"stroke-width": str(style.stroke_width)})
            group.add_child(line)
        elif bond_order == 2:
            # Double bond
            for i in [-1, 1]:
                ox = perp_x * offset * i
                oy = perp_y * offset * i
                line = SVGElement("line",
                                 x1=str(x1 + ox), y1=str(y1 + oy),
                                 x2=str(x2 + ox), y2=str(y2 + oy),
                                 stroke=style.color,
                                 **{"stroke-width": str(style.stroke_width)})
                group.add_child(line)
        elif bond_order == 3:
            # Triple bond
            for i in [-1, 0, 1]:
                ox = perp_x * offset * i
                oy = perp_y * offset * i
                line = SVGElement("line",
                                 x1=str(x1 + ox), y1=str(y1 + oy),
                                 x2=str(x2 + ox), y2=str(y2 + oy),
                                 stroke=style.color,
                                 **{"stroke-width": str(style.stroke_width)})
                group.add_child(line)

        return group

    @staticmethod
    def create_vector(x: float, y: float, dx: float, dy: float,
                     style: Style, label: Optional[str] = None) -> SVGElement:
        """Create a vector arrow"""
        group = SVGElement("g", id=f"vector_{x}_{y}")

        import math
        # Arrow shaft
        shaft = SVGElement("line",
                          x1=str(x), y1=str(y),
                          x2=str(x + dx), y2=str(y + dy),
                          stroke=style.color,
                          **{"stroke-width": str(style.stroke_width),
                             "marker-end": "url(#arrowhead)"})
        group.add_child(shaft)

        # Label at midpoint
        if label:
            mid_x = x + dx / 2
            mid_y = y + dy / 2
            text = SVGElement("text",
                            x=str(mid_x + 10), y=str(mid_y - 10),
                            **{"font-size": str(style.font_size),
                               "font-family": style.font_family,
                               "fill": style.color})
            text.set_text(label)
            group.add_child(text)

        return group


class UniversalSVGRenderer:
    """
    Universal SVG Renderer for all STEM diagrams

    This renderer takes a UniversalScene and produces a professional SVG diagram
    """

    def __init__(self):
        self.component_library = ComponentLibrary()
        self.primitive_components = {}  # Cache for primitive SVG content

    def render(self, scene: UniversalScene, primitive_components: Optional[Dict] = None) -> str:
        """
        Render a UniversalScene to SVG string

        Args:
            scene: UniversalScene object to render
            primitive_components: Optional dict mapping object types/IDs to reusable primitive SVG content

        Returns:
            SVG string
        """
        # Store primitives for use in _render_object
        if primitive_components:
            self.primitive_components = primitive_components
        else:
            self.primitive_components = {}
        # Create root SVG element
        svg = SVGElement("svg",
                        width=str(scene.canvas_width),
                        height=str(scene.canvas_height),
                        xmlns="http://www.w3.org/2000/svg",
                        version="1.1")

        # Add definitions (markers, gradients, etc.)
        defs = self._create_definitions(scene)
        svg.add_child(defs)

        # Add background
        background = SVGElement("rect",
                               width=str(scene.canvas_width),
                               height=str(scene.canvas_height),
                               fill=scene.background_color)
        svg.add_child(background)

        # Add grid if enabled
        if scene.grid_enabled:
            grid_group = self._create_grid(scene)
            svg.add_child(grid_group)

        # Add title if present
        if scene.title:
            title_elem = self._create_title(scene)
            svg.add_child(title_elem)

        # Render objects
        objects_group = SVGElement("g", id="objects")
        for obj in scene.objects:
            obj_elem = self._render_object(obj)
            if obj_elem:
                objects_group.add_child(obj_elem)
        svg.add_child(objects_group)

        # Render relationships
        relationships_group = SVGElement("g", id="relationships")
        for rel in scene.relationships:
            rel_elem = self._render_relationship(rel, scene)
            if rel_elem:
                relationships_group.add_child(rel_elem)
        svg.add_child(relationships_group)

        # Render annotations
        annotations_group = SVGElement("g", id="annotations")
        for annotation in scene.annotations:
            ann_elem = self._render_annotation(annotation)
            if ann_elem:
                annotations_group.add_child(ann_elem)
        svg.add_child(annotations_group)

        return svg.to_string()

    def _create_definitions(self, scene: UniversalScene) -> SVGElement:
        """Create SVG definitions (markers, patterns, etc.)"""
        defs = SVGElement("defs")

        # Arrowhead marker
        marker = SVGElement("marker",
                           id="arrowhead",
                           markerWidth="10",
                           markerHeight="10",
                           refX="9",
                           refY="3",
                           orient="auto")
        arrow_polygon = SVGElement("polygon",
                                   points="0 0, 10 3, 0 6",
                                   fill="#000000")
        marker.add_child(arrow_polygon)
        defs.add_child(marker)

        # Add more markers for different styles
        # Blue arrowhead
        marker_blue = SVGElement("marker",
                                id="arrowhead-blue",
                                markerWidth="10",
                                markerHeight="10",
                                refX="9",
                                refY="3",
                                orient="auto")
        arrow_blue = SVGElement("polygon",
                               points="0 0, 10 3, 0 6",
                               fill="#0066cc")
        marker_blue.add_child(arrow_blue)
        defs.add_child(marker_blue)

        return defs

    def _create_grid(self, scene: UniversalScene) -> SVGElement:
        """Create grid background"""
        grid = SVGElement("g", id="grid", opacity="0.2")

        spacing = scene.grid_spacing
        width = scene.canvas_width
        height = scene.canvas_height

        # Vertical lines
        x = 0
        while x <= width:
            line = SVGElement("line",
                             x1=str(x), y1="0",
                             x2=str(x), y2=str(height),
                             stroke="#CCCCCC",
                             **{"stroke-width": "1"})
            grid.add_child(line)
            x += spacing

        # Horizontal lines
        y = 0
        while y <= height:
            line = SVGElement("line",
                             x1="0", y1=str(y),
                             x2=str(width), y2=str(y),
                             stroke="#CCCCCC",
                             **{"stroke-width": "1"})
            grid.add_child(line)
            y += spacing

        return grid

    def _create_title(self, scene: UniversalScene) -> SVGElement:
        """Create title text"""
        title = SVGElement("text",
                          x=str(scene.canvas_width / 2),
                          y="40",
                          **{"text-anchor": "middle",
                             "font-size": "24",
                             "font-weight": "bold",
                             "font-family": "Arial",
                             "fill": "#333333"})
        title.set_text(scene.title)
        return title

    def _render_object(self, obj: SceneObject) -> Optional[SVGElement]:
        """Render a scene object based on its type"""
        # Check if we have a reusable primitive for this object
        if self.primitive_components:
            # Try to match by object type or ID
            primitive_key = f"{obj.object_type.value}_{obj.type}" if hasattr(obj, 'type') else obj.object_type.value

            if primitive_key in self.primitive_components:
                primitive = self.primitive_components[primitive_key]
                # Parse and inject primitive SVG at object's position
                try:
                    svg_content = primitive.get('svg_content', '')
                    if svg_content:
                        # Parse SVG and wrap in a group positioned at obj.position
                        group = SVGElement("g",
                                         transform=f"translate({obj.position.x}, {obj.position.y})",
                                         id=f"primitive_{obj.id}")
                        # Note: In production, would parse svg_content and add as children
                        # For now, we'll fall through to standard rendering
                        # TODO: Implement SVG parsing and injection
                except Exception as e:
                    # If primitive reuse fails, fall back to standard rendering
                    pass

        x = obj.position.x
        y = obj.position.y
        w = obj.dimensions.width
        h = obj.dimensions.height
        r = obj.dimensions.radius
        style = obj.style

        # Route to appropriate component based on object type
        if obj.object_type == ObjectType.RESISTOR:
            return self.component_library.create_resistor(x, y, w, h, style, obj.label)
        elif obj.object_type == ObjectType.CAPACITOR:
            return self.component_library.create_capacitor(x, y, w, h, style, obj.label)
        elif obj.object_type == ObjectType.BATTERY:
            return self.component_library.create_battery(x, y, w, h, style, obj.label)
        elif obj.object_type == ObjectType.ATOM:
            element = obj.properties.get("element", "C")
            electrons = obj.properties.get("electrons", 6)
            return self.component_library.create_atom(x, y, r, style, element, electrons)
        elif obj.object_type == ObjectType.CIRCLE:
            return self._render_circle(obj)
        elif obj.object_type == ObjectType.RECTANGLE:
            return self._render_rectangle(obj)
        elif obj.object_type == ObjectType.LINE:
            return self._render_line(obj)
        elif obj.object_type == ObjectType.VECTOR:
            dx = obj.properties.get("dx", 50)
            dy = obj.properties.get("dy", 0)
            return self.component_library.create_vector(x, y, dx, dy, style, obj.label)
        else:
            # Default: render as a generic shape
            return self._render_generic(obj)

    def _render_circle(self, obj: SceneObject) -> SVGElement:
        """Render a circle"""
        circle = SVGElement("circle",
                           cx=str(obj.position.x),
                           cy=str(obj.position.y),
                           r=str(obj.dimensions.radius),
                           fill=obj.style.fill_color or "none",
                           stroke=obj.style.color,
                           **{"stroke-width": str(obj.style.stroke_width),
                              "opacity": str(obj.style.opacity)})
        return circle

    def _render_rectangle(self, obj: SceneObject) -> SVGElement:
        """Render a rectangle"""
        x = obj.position.x - obj.dimensions.width / 2
        y = obj.position.y - obj.dimensions.height / 2
        rect = SVGElement("rect",
                         x=str(x),
                         y=str(y),
                         width=str(obj.dimensions.width),
                         height=str(obj.dimensions.height),
                         fill=obj.style.fill_color or "none",
                         stroke=obj.style.color,
                         **{"stroke-width": str(obj.style.stroke_width),
                            "opacity": str(obj.style.opacity)})
        return rect

    def _render_line(self, obj: SceneObject) -> SVGElement:
        """Render a line"""
        x2 = obj.properties.get("x2", obj.position.x + 100)
        y2 = obj.properties.get("y2", obj.position.y)
        line = SVGElement("line",
                         x1=str(obj.position.x),
                         y1=str(obj.position.y),
                         x2=str(x2),
                         y2=str(y2),
                         stroke=obj.style.color,
                         **{"stroke-width": str(obj.style.stroke_width)})
        return line

    def _render_generic(self, obj: SceneObject) -> SVGElement:
        """Render a generic placeholder"""
        group = SVGElement("g", id=obj.id)
        rect = SVGElement("rect",
                         x=str(obj.position.x - 20),
                         y=str(obj.position.y - 20),
                         width="40",
                         height="40",
                         fill="#EEEEEE",
                         stroke="#999999",
                         **{"stroke-width": "2"})
        group.add_child(rect)
        if obj.label:
            text = SVGElement("text",
                            x=str(obj.position.x),
                            y=str(obj.position.y + 5),
                            **{"text-anchor": "middle",
                               "font-size": "10"})
            text.set_text(obj.label)
            group.add_child(text)
        return group

    def _render_relationship(self, rel: Relationship, scene: UniversalScene) -> Optional[SVGElement]:
        """Render a relationship between objects"""
        source = scene.get_object(rel.source_id)
        target = scene.get_object(rel.target_id)

        if not source or not target:
            return None

        # For CONNECTED_TO relationships, draw a line
        if rel.relation_type == RelationType.CONNECTED_TO:
            line = SVGElement("line",
                             x1=str(source.position.x),
                             y1=str(source.position.y),
                             x2=str(target.position.x),
                             y2=str(target.position.y),
                             stroke="#666666",
                             **{"stroke-width": "2"})
            return line
        elif rel.relation_type == RelationType.BONDED_TO:
            # Chemical bond
            bond_order = rel.properties.get("bond_order", 1)
            return self.component_library.create_bond(
                source.position.x, source.position.y,
                target.position.x, target.position.y,
                bond_order, source.style
            )

        return None

    def _render_annotation(self, annotation: Annotation) -> SVGElement:
        """Render an annotation"""
        text = SVGElement("text",
                         x=str(annotation.position.x),
                         y=str(annotation.position.y),
                         **{"font-size": str(annotation.style.font_size),
                            "font-family": annotation.style.font_family,
                            "fill": annotation.style.color})
        text.set_text(annotation.text)
        return text

    def save_svg(self, scene: UniversalScene, filepath: str) -> None:
        """Render scene and save to file"""
        svg_content = self.render(scene)
        with open(filepath, 'w') as f:
            f.write(svg_content)
        print(f"✅ SVG saved to: {filepath}")


if __name__ == "__main__":
    # Test the renderer with example scenes
    from core.universal_scene_format import (
        create_circuit_scene, SceneObject, ObjectType, Position,
        Dimensions, Style, Relationship, RelationType, Annotation
    )

    print("Universal SVG Renderer - Test\n" + "=" * 50)

    # Create a test circuit
    scene = create_circuit_scene("test_circuit", "RC Circuit")

    # Add components
    battery = SceneObject(
        id="V1",
        object_type=ObjectType.BATTERY,
        position=Position(150, 300),
        dimensions=Dimensions(width=80, height=50),
        label="12V"
    )
    scene.add_object(battery)

    resistor = SceneObject(
        id="R1",
        object_type=ObjectType.RESISTOR,
        position=Position(400, 300),
        dimensions=Dimensions(width=120, height=30),
        label="100Ω"
    )
    scene.add_object(resistor)

    capacitor = SceneObject(
        id="C1",
        object_type=ObjectType.CAPACITOR,
        position=Position(650, 300),
        dimensions=Dimensions(width=80, height=60),
        label="10μF"
    )
    scene.add_object(capacitor)

    # Add connections
    wire1 = Relationship(
        id="wire1",
        relation_type=RelationType.CONNECTED_TO,
        source_id="V1",
        target_id="R1"
    )
    scene.add_relationship(wire1)

    wire2 = Relationship(
        id="wire2",
        relation_type=RelationType.CONNECTED_TO,
        source_id="R1",
        target_id="C1"
    )
    scene.add_relationship(wire2)

    # Add annotation
    annotation = Annotation(
        id="note1",
        text="τ = RC = 1ms",
        position=Position(400, 200),
        annotation_type="equation"
    )
    scene.add_annotation(annotation)

    # Render
    renderer = UniversalSVGRenderer()
    svg_output = renderer.render(scene)

    print(f"\nRendered SVG ({len(svg_output)} characters)")
    print("Saving to test_circuit.svg...")

    renderer.save_svg(scene, "output/test_circuit.svg")

    print("\n✅ Universal SVG Renderer test complete!")
