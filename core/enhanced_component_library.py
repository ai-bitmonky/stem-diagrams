"""
Enhanced Component Library - Professional Visual Components
===========================================================

This module provides enhanced, detailed visual components with:
- Professional styling with gradients and shadows
- Multiple rendering styles (classic, modern, 3D-like)
- Component variants (different sizes, orientations)
- High-quality visual output
- Support for all STEM domains

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class ComponentStyle:
    """Visual style configuration for components"""
    style_type: str = "modern"  # classic, modern, 3d
    color_scheme: str = "default"  # default, colorful, monochrome
    show_shadows: bool = True
    show_gradients: bool = True
    line_style: str = "solid"  # solid, dashed, dotted
    background_color: str = "#FFFFFF"  # Background color for diagrams
    show_grid: bool = False  # Show grid lines in background


class EnhancedSVGElement:
    """Helper class for building SVG elements"""

    def __init__(self, tag: str, **attributes):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.text_content = None

    def add_child(self, child: 'EnhancedSVGElement'):
        self.children.append(child)
        return self

    def set_text(self, text: str):
        self.text_content = text
        return self

    def to_svg(self, indent: int = 0) -> str:
        """Convert to SVG string"""
        indent_str = "  " * indent

        # Build opening tag
        attrs = " ".join([f'{k.replace("_", "-")}="{v}"' for k, v in self.attributes.items()])
        opening = f"{indent_str}<{self.tag}"
        if attrs:
            opening += f" {attrs}"

        # Handle self-closing tags
        if not self.children and not self.text_content:
            return f"{opening}/>"

        opening += ">"

        # Handle text content
        if self.text_content:
            return f"{opening}{self.text_content}</{self.tag}>"

        # Handle children
        result = opening + "\n"
        for child in self.children:
            result += child.to_svg(indent + 1) + "\n"
        result += f"{indent_str}</{self.tag}>"

        return result


class EnhancedComponentLibrary:
    """
    Enhanced component library with professional, detailed components
    """

    def __init__(self, style: ComponentStyle = None):
        self.style = style or ComponentStyle()

    # ==================== ELECTRONICS COMPONENTS ====================

    def create_enhanced_resistor(self, x: float, y: float, width: float, height: float,
                                label: str = "", orientation: str = "horizontal") -> EnhancedSVGElement:
        """
        Create an enhanced resistor with professional styling

        Styles:
        - classic: Traditional zigzag
        - modern: Rectangular with rounded corners
        - 3d: 3D perspective effect
        """
        group = EnhancedSVGElement("g", id=f"resistor_{x}_{y}")

        if self.style.style_type == "modern":
            # Modern rectangular resistor
            if orientation == "horizontal":
                # Main body with gradient
                if self.style.show_gradients:
                    # Add gradient definition
                    grad = EnhancedSVGElement("defs")
                    gradient = EnhancedSVGElement("linearGradient",
                                                 id=f"resistor_grad_{x}_{y}",
                                                 x1="0%", y1="0%", x2="0%", y2="100%")
                    gradient.add_child(EnhancedSVGElement("stop", offset="0%",
                                                          style="stop-color:#d4a574;stop-opacity:1"))
                    gradient.add_child(EnhancedSVGElement("stop", offset="100%",
                                                          style="stop-color:#8b6f47;stop-opacity:1"))
                    grad.add_child(gradient)
                    group.add_child(grad)

                    fill = f"url(#resistor_grad_{x}_{y})"
                else:
                    fill = "#d4a574"

                # Resistor body
                body = EnhancedSVGElement("rect",
                                         x=x - width/2, y=y - height/3,
                                         width=width, height=height*2/3,
                                         rx=3, ry=3,
                                         fill=fill, stroke="#000000", stroke_width=2)
                group.add_child(body)

                # Color bands
                band_width = width / 15
                band_positions = [0.25, 0.40, 0.55, 0.70]
                band_colors = ["#ff0000", "#ff9900", "#ffff00", "#c0c0c0"]

                for i, pos in enumerate(band_positions):
                    band_x = x - width/2 + pos * width
                    band = EnhancedSVGElement("rect",
                                            x=band_x, y=y - height/3,
                                            width=band_width, height=height*2/3,
                                            fill=band_colors[i % len(band_colors)])
                    group.add_child(band)

                # Connection wires
                wire1 = EnhancedSVGElement("line",
                                          x1=x - width, y1=y,
                                          x2=x - width/2, y2=y,
                                          stroke="#000000", stroke_width=2)
                wire2 = EnhancedSVGElement("line",
                                          x1=x + width/2, y1=y,
                                          x2=x + width, y2=y,
                                          stroke="#000000", stroke_width=2)
                group.add_child(wire1)
                group.add_child(wire2)

        elif self.style.style_type == "3d":
            # 3D-style resistor with perspective
            if orientation == "horizontal":
                # Top face
                top = EnhancedSVGElement("polygon",
                                        points=f"{x-width/2},{y-height/2} {x+width/2},{y-height/2} "
                                              f"{x+width/2-5},{y-height/2-5} {x-width/2-5},{y-height/2-5}",
                                        fill="#e6b885", stroke="#000000", stroke_width=1)
                group.add_child(top)

                # Front face
                front = EnhancedSVGElement("rect",
                                          x=x-width/2, y=y-height/2,
                                          width=width, height=height,
                                          fill="#d4a574", stroke="#000000", stroke_width=2)
                group.add_child(front)

                # Side face
                side = EnhancedSVGElement("polygon",
                                         points=f"{x+width/2},{y-height/2} {x+width/2},{y+height/2} "
                                               f"{x+width/2-5},{y+height/2-5} {x+width/2-5},{y-height/2-5}",
                                         fill="#b8956a", stroke="#000000", stroke_width=1)
                group.add_child(side)

        else:  # classic zigzag
            if orientation == "horizontal":
                y_center = y
                x_start = x - width / 2
                x_end = x + width / 2

                segments = 6
                segment_width = width / segments
                zigzag_height = height / 2

                # Build zigzag path
                path_data = f"M {x_start} {y_center} "
                for i in range(segments):
                    x_seg = x_start + (i + 0.5) * segment_width
                    y_seg = y_center + (zigzag_height if i % 2 == 0 else -zigzag_height)
                    path_data += f"L {x_seg} {y_seg} "
                path_data += f"L {x_end} {y_center}"

                zigzag = EnhancedSVGElement("path", d=path_data,
                                           stroke="#000000", stroke_width=3,
                                           fill="none")
                group.add_child(zigzag)

                # Connection lines
                wire1 = EnhancedSVGElement("line",
                                          x1=x - width, y1=y_center,
                                          x2=x_start, y2=y_center,
                                          stroke="#000000", stroke_width=2)
                wire2 = EnhancedSVGElement("line",
                                          x1=x_end, y1=y_center,
                                          x2=x + width, y2=y_center,
                                          stroke="#000000", stroke_width=2)
                group.add_child(wire1)
                group.add_child(wire2)

        # Add label
        if label:
            label_elem = EnhancedSVGElement("text",
                                           x=x, y=y - height,
                                           text_anchor="middle",
                                           font_size=14, font_family="Arial",
                                           fill="#000000")
            label_elem.set_text(label)
            group.add_child(label_elem)

        return group

    def create_enhanced_capacitor(self, x: float, y: float, width: float, height: float,
                                 label: str = "", capacitor_type: str = "standard") -> EnhancedSVGElement:
        """
        Create an enhanced capacitor with professional styling

        Types:
        - standard: Parallel plates
        - electrolytic: Polarized capacitor
        - variable: Variable capacitor symbol
        """
        group = EnhancedSVGElement("g", id=f"capacitor_{x}_{y}")

        plate_width = 2
        plate_spacing = 16

        if capacitor_type == "electrolytic":
            # Left plate (positive) - curved
            arc_radius = height / 2
            left_plate = EnhancedSVGElement("path",
                                           d=f"M {x - plate_spacing/2} {y - height/2} "
                                             f"Q {x - plate_spacing/2 - 10} {y} "
                                             f"{x - plate_spacing/2} {y + height/2}",
                                           stroke="#000000", stroke_width=plate_width,
                                           fill="none")
            group.add_child(left_plate)

            # Right plate (negative) - straight
            right_plate = EnhancedSVGElement("line",
                                            x1=x + plate_spacing/2, y1=y - height/2,
                                            x2=x + plate_spacing/2, y2=y + height/2,
                                            stroke="#000000", stroke_width=plate_width)
            group.add_child(right_plate)

            # Polarity markers
            plus = EnhancedSVGElement("text",
                                     x=x - plate_spacing/2 - 20, y=y + 5,
                                     text_anchor="middle", font_size=16,
                                     font_weight="bold", fill="#ff0000")
            plus.set_text("+")
            group.add_child(plus)

        elif capacitor_type == "variable":
            # Left plate
            left_plate = EnhancedSVGElement("line",
                                           x1=x - plate_spacing/2, y1=y - height/2,
                                           x2=x - plate_spacing/2, y2=y + height/2,
                                           stroke="#000000", stroke_width=plate_width)
            group.add_child(left_plate)

            # Right plate
            right_plate = EnhancedSVGElement("line",
                                            x1=x + plate_spacing/2, y1=y - height/2,
                                            x2=x + plate_spacing/2, y2=y + height/2,
                                            stroke="#000000", stroke_width=plate_width)
            group.add_child(right_plate)

            # Arrow showing variability
            arrow = EnhancedSVGElement("path",
                                      d=f"M {x} {y + height/2 + 15} L {x + 15} {y + height/2 + 25} "
                                        f"M {x} {y + height/2 + 15} L {x - 15} {y + height/2 + 25}",
                                      stroke="#0066cc", stroke_width=2, fill="none")
            group.add_child(arrow)

        else:  # standard capacitor
            # Add 3D effect with gradient
            if self.style.show_gradients and self.style.style_type == "modern":
                # Left plate with depth
                for i in range(3):
                    offset = i * 2
                    opacity = 1.0 - (i * 0.2)
                    plate = EnhancedSVGElement("line",
                                              x1=x - plate_spacing/2 - offset, y1=y - height/2,
                                              x2=x - plate_spacing/2 - offset, y2=y + height/2,
                                              stroke="#000000", stroke_width=plate_width,
                                              opacity=opacity)
                    group.add_child(plate)

                # Right plate with depth
                for i in range(3):
                    offset = i * 2
                    opacity = 1.0 - (i * 0.2)
                    plate = EnhancedSVGElement("line",
                                              x1=x + plate_spacing/2 + offset, y1=y - height/2,
                                              x2=x + plate_spacing/2 + offset, y2=y + height/2,
                                              stroke="#000000", stroke_width=plate_width,
                                              opacity=opacity)
                    group.add_child(plate)
            else:
                # Simple parallel plates
                left_plate = EnhancedSVGElement("line",
                                               x1=x - plate_spacing/2, y1=y - height/2,
                                               x2=x - plate_spacing/2, y2=y + height/2,
                                               stroke="#000000", stroke_width=plate_width)
                right_plate = EnhancedSVGElement("line",
                                                x1=x + plate_spacing/2, y1=y - height/2,
                                                x2=x + plate_spacing/2, y2=y + height/2,
                                                stroke="#000000", stroke_width=plate_width)
                group.add_child(left_plate)
                group.add_child(right_plate)

        # Connection wires
        wire_left = EnhancedSVGElement("line",
                                      x1=x - width/2, y1=y,
                                      x2=x - plate_spacing/2, y2=y,
                                      stroke="#000000", stroke_width=2)
        wire_right = EnhancedSVGElement("line",
                                       x1=x + plate_spacing/2, y1=y,
                                       x2=x + width/2, y2=y,
                                       stroke="#000000", stroke_width=2)
        group.add_child(wire_left)
        group.add_child(wire_right)

        # Label
        if label:
            label_elem = EnhancedSVGElement("text",
                                           x=x, y=y - height/2 - 10,
                                           text_anchor="middle",
                                           font_size=14, font_family="Arial",
                                           fill="#000000")
            label_elem.set_text(label)
            group.add_child(label_elem)

        return group

    def create_enhanced_battery(self, x: float, y: float, width: float, height: float,
                               label: str = "", num_cells: int = 1) -> EnhancedSVGElement:
        """
        Create an enhanced battery with professional styling
        """
        group = EnhancedSVGElement("g", id=f"battery_{x}_{y}")

        if self.style.style_type == "modern":
            # Modern battery with 3D effect
            cell_spacing = 10
            cell_width = 6

            for i in range(num_cells):
                offset = i * cell_spacing - (num_cells - 1) * cell_spacing / 2

                # Negative terminal (short line)
                neg = EnhancedSVGElement("line",
                                        x1=x + offset, y1=y - height/4,
                                        x2=x + offset, y2=y + height/4,
                                        stroke="#000000", stroke_width=3)
                group.add_child(neg)

                # Positive terminal (long line)
                pos = EnhancedSVGElement("line",
                                        x1=x + offset + cell_width, y1=y - height/2,
                                        x2=x + offset + cell_width, y2=y + height/2,
                                        stroke="#000000", stroke_width=2)
                group.add_child(pos)
        else:
            # Classic battery symbol
            # Short line (negative)
            neg_line = EnhancedSVGElement("line",
                                         x1=x - 5, y1=y - height/4,
                                         x2=x - 5, y2=y + height/4,
                                         stroke="#000000", stroke_width=4)
            group.add_child(neg_line)

            # Long line (positive)
            pos_line = EnhancedSVGElement("line",
                                         x1=x + 5, y1=y - height/2,
                                         x2=x + 5, y2=y + height/2,
                                         stroke="#000000", stroke_width=2)
            group.add_child(pos_line)

        # Polarity markers
        plus = EnhancedSVGElement("text",
                                 x=x + 20, y=y + 5,
                                 text_anchor="middle", font_size=18,
                                 font_weight="bold", fill="#000000")
        plus.set_text("+")
        group.add_child(plus)

        # Connection wires
        wire_left = EnhancedSVGElement("line",
                                      x1=x - width/2, y1=y,
                                      x2=x - 10, y2=y,
                                      stroke="#000000", stroke_width=2)
        wire_right = EnhancedSVGElement("line",
                                       x1=x + 10, y1=y,
                                       x2=x + width/2, y2=y,
                                       stroke="#000000", stroke_width=2)
        group.add_child(wire_left)
        group.add_child(wire_right)

        # Label
        if label:
            label_elem = EnhancedSVGElement("text",
                                           x=x, y=y - height/2 - 10,
                                           text_anchor="middle",
                                           font_size=14, font_family="Arial",
                                           font_weight="bold", fill="#000000")
            label_elem.set_text(label)
            group.add_child(label_elem)

        return group

    # ==================== CHEMISTRY COMPONENTS ====================

    def create_enhanced_atom(self, x: float, y: float, radius: float,
                           label: str = "", num_electrons: int = 2) -> EnhancedSVGElement:
        """
        Create an enhanced atom with nucleus and electron orbits
        """
        group = EnhancedSVGElement("g", id=f"atom_{x}_{y}")

        if self.style.show_gradients:
            # Gradient for nucleus
            grad = EnhancedSVGElement("defs")
            gradient = EnhancedSVGElement("radialGradient",
                                         id=f"nucleus_grad_{x}_{y}")
            gradient.add_child(EnhancedSVGElement("stop", offset="0%",
                                                  style="stop-color:#ffeb3b;stop-opacity:1"))
            gradient.add_child(EnhancedSVGElement("stop", offset="100%",
                                                  style="stop-color:#ff9800;stop-opacity:1"))
            grad.add_child(gradient)
            group.add_child(grad)

            fill = f"url(#nucleus_grad_{x}_{y})"
        else:
            fill = "#ffeb3b"

        # Nucleus with shadow
        if self.style.show_shadows:
            shadow = EnhancedSVGElement("circle",
                                       cx=x + 2, cy=y + 2, r=radius/3,
                                       fill="#000000", opacity=0.3)
            group.add_child(shadow)

        nucleus = EnhancedSVGElement("circle",
                                    cx=x, cy=y, r=radius/3,
                                    fill=fill, stroke="#000000", stroke_width=2)
        group.add_child(nucleus)

        # Electron orbits
        for i in range(num_electrons):
            orbit_radius = radius * (0.5 + i * 0.3)
            angle = (360 / num_electrons) * i

            # Orbit path
            orbit = EnhancedSVGElement("ellipse",
                                      cx=x, cy=y,
                                      rx=orbit_radius, ry=orbit_radius * 0.3,
                                      fill="none", stroke="#0066cc",
                                      stroke_width=1, stroke_dasharray="5,3",
                                      transform=f"rotate({angle} {x} {y})")
            group.add_child(orbit)

            # Electron
            e_angle = math.radians(angle + 90)
            e_x = x + orbit_radius * math.cos(e_angle)
            e_y = y + orbit_radius * 0.3 * math.sin(e_angle)

            electron = EnhancedSVGElement("circle",
                                         cx=e_x, cy=e_y, r=4,
                                         fill="#2196f3", stroke="#000000", stroke_width=1)
            group.add_child(electron)

        # Label
        if label:
            label_elem = EnhancedSVGElement("text",
                                           x=x, y=y + radius + 20,
                                           text_anchor="middle",
                                           font_size=14, font_family="Arial",
                                           font_weight="bold", fill="#000000")
            label_elem.set_text(label)
            group.add_child(label_elem)

        return group

    def create_enhanced_bond(self, x1: float, y1: float, x2: float, y2: float,
                           bond_type: str = "single") -> EnhancedSVGElement:
        """
        Create an enhanced chemical bond

        Types: single, double, triple, dashed (coordination)
        """
        group = EnhancedSVGElement("g", id=f"bond_{x1}_{y1}_{x2}_{y2}")

        # Calculate perpendicular offset for multiple bonds
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        if length == 0:
            return group

        # Unit perpendicular vector
        perp_x = -dy / length
        perp_y = dx / length
        offset = 3

        if bond_type == "single":
            bond = EnhancedSVGElement("line",
                                     x1=x1, y1=y1, x2=x2, y2=y2,
                                     stroke="#000000", stroke_width=2)
            group.add_child(bond)

        elif bond_type == "double":
            bond1 = EnhancedSVGElement("line",
                                      x1=x1 + perp_x * offset, y1=y1 + perp_y * offset,
                                      x2=x2 + perp_x * offset, y2=y2 + perp_y * offset,
                                      stroke="#000000", stroke_width=2)
            bond2 = EnhancedSVGElement("line",
                                      x1=x1 - perp_x * offset, y1=y1 - perp_y * offset,
                                      x2=x2 - perp_x * offset, y2=y2 - perp_y * offset,
                                      stroke="#000000", stroke_width=2)
            group.add_child(bond1)
            group.add_child(bond2)

        elif bond_type == "triple":
            bond1 = EnhancedSVGElement("line",
                                      x1=x1, y1=y1, x2=x2, y2=y2,
                                      stroke="#000000", stroke_width=2)
            bond2 = EnhancedSVGElement("line",
                                      x1=x1 + perp_x * offset * 1.5, y1=y1 + perp_y * offset * 1.5,
                                      x2=x2 + perp_x * offset * 1.5, y2=y2 + perp_y * offset * 1.5,
                                      stroke="#000000", stroke_width=2)
            bond3 = EnhancedSVGElement("line",
                                      x1=x1 - perp_x * offset * 1.5, y1=y1 - perp_y * offset * 1.5,
                                      x2=x2 - perp_x * offset * 1.5, y2=y2 - perp_y * offset * 1.5,
                                      stroke="#000000", stroke_width=2)
            group.add_child(bond1)
            group.add_child(bond2)
            group.add_child(bond3)

        elif bond_type == "dashed":
            bond = EnhancedSVGElement("line",
                                     x1=x1, y1=y1, x2=x2, y2=y2,
                                     stroke="#000000", stroke_width=2,
                                     stroke_dasharray="5,3")
            group.add_child(bond)

        return group


# Testing and demo
if __name__ == "__main__":
    print("Enhanced Component Library - Demo")
    print("=" * 50)

    # Test different styles
    styles = [
        ("classic", ComponentStyle(style_type="classic")),
        ("modern", ComponentStyle(style_type="modern")),
        ("3d", ComponentStyle(style_type="3d"))
    ]

    for style_name, style in styles:
        lib = EnhancedComponentLibrary(style)

        print(f"\n{style_name.upper()} Style:")
        print("-" * 50)

        # Create sample components
        resistor = lib.create_enhanced_resistor(200, 100, 80, 30, "10kΩ")
        print(f"  ✓ Resistor created")

        capacitor = lib.create_enhanced_capacitor(200, 200, 80, 60, "100μF", "electrolytic")
        print(f"  ✓ Capacitor created")

        battery = lib.create_enhanced_battery(200, 300, 80, 50, "9V", num_cells=1)
        print(f"  ✓ Battery created")

        atom = lib.create_enhanced_atom(400, 200, 40, "H", num_electrons=1)
        print(f"  ✓ Atom created")

    print("\n" + "=" * 50)
    print("✅ Enhanced Component Library ready!")
    print("   - 3 rendering styles (classic, modern, 3D)")
    print("   - Enhanced resistors with color bands")
    print("   - Professional capacitors with variants")
    print("   - Modern batteries with polarity markers")
    print("   - Detailed atoms with electron orbits")
    print("   - Chemical bonds with multiple types")
