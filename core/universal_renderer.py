"""
Universal Renderer - Single Robust Pipeline Phase 5
Merges GenericSVGRenderer + JEEEnhancedRenderer + MultiDomainRenderer
Uses UniversalGlyphLibrary + domain embellishments
"""

from typing import Dict, List, Tuple
from pathlib import Path
import json

from core.scene.schema_v1 import Scene, SceneObject, PrimitiveType
from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain


class UniversalRenderer:
    """
    Universal Renderer - Single robust implementation

    Merges:
    - GenericSVGRenderer (domain-agnostic rendering)
    - JEEEnhancedRenderer (hybrid plugin support)
    - MultiDomainRenderer (domain-specific rendering)

    Uses:
    - UniversalGlyphLibrary (covers ALL physics primitives)
    - Domain embellishments (loaded as data from domains/)
    """

    def __init__(self, width: int = 1200, height: int = 800, domains_path: str = "domains"):
        """
        Initialize Universal Renderer

        Args:
            width: Canvas width
            height: Canvas height
            domains_path: Path to domains directory
        """
        self.width = width
        self.height = height
        self.domains_path = Path(domains_path)

        # Load universal glyph library
        self.glyphs = self._load_glyph_library()

        # Load domain themes/styles
        self.themes = self._load_domain_themes()

        # Load domain embellishments
        self.embellishments = self._load_embellishments()

        print(f"✅ UniversalRenderer initialized")
        print(f"   Canvas: {width}x{height}")
        print(f"   Glyphs: {len(self.glyphs)} primitives")
        print(f"   Themes: {len(self.themes)} domains")

    def render(self, scene: Scene, spec: CanonicalProblemSpec = None, fmt: str = "svg") -> str:
        """
        Render scene in requested format (svg, tikz, png)
        """
        return self.render_format(scene, spec, fmt)

    def render_format(self, scene: Scene, spec: CanonicalProblemSpec = None, fmt: str = "svg") -> str:
        fmt = fmt.lower()
        if fmt == "svg":
            return self._render_svg(scene, spec)
        if fmt == "tikz":
            return self._render_tikz(scene, spec)
        if fmt == "png":
            svg = self._render_svg(scene, spec)
            return self._svg_to_png(svg)
        raise ValueError(f"Unsupported format: {fmt}")

    def _render_svg(self, scene: Scene, spec: CanonicalProblemSpec = None) -> str:
        """
        Render scene to SVG

        Pipeline:
        1. Apply domain theme/style
        2. Render objects using glyphs
        3. Add domain embellishments (field lines, annotations)
        4. Add labels and legend
        5. Generate final SVG

        Args:
            scene: Positioned scene with all objects
            spec: Optional problem spec for domain context

        Returns:
            Complete SVG string
        """
        print(f"\n{'='*80}")
        print(f"🎨 UNIVERSAL RENDERER - Phase 5")
        print(f"{'='*80}\n")

        # Step 1: Apply domain theme
        print("Step 1/5: Theme Application")
        theme = self._apply_theme(scene, spec)
        print(f"   ✅ Applied: {theme.get('name', 'default')} theme")

        # Step 2: Render objects
        print("\nStep 2/5: Object Rendering")
        object_svg = self._render_objects(scene, theme)
        print(f"   ✅ Rendered {len(scene.objects)} objects")

        # Step 3: Add embellishments
        print("\nStep 3/5: Domain Embellishments")
        embellishments_svg = self._add_embellishments(scene, spec, theme)
        print(f"   ✅ Added domain-specific elements")

        # Step 4: Add labels and legend
        print("\nStep 4/5: Labels and Legend")
        labels_svg = self._render_labels(scene, theme)
        legend_svg = self._render_legend(scene, theme)
        print(f"   ✅ Added labels and legend")

        # Step 5: Assemble final SVG
        print("\nStep 5/5: SVG Assembly")
        svg = self._assemble_svg(scene, theme, object_svg, embellishments_svg, labels_svg, legend_svg)
        print(f"   ✅ Generated {len(svg)} bytes of SVG")

        print(f"\n{'='*80}")
        print(f"✅ UNIVERSAL RENDERER COMPLETE")
        print(f"{'='*80}\n")

        return self._optimize_svg(svg)

    def _load_glyph_library(self) -> Dict:
        """Load universal glyph library"""

        glyphs = {}

        # Try to load existing glyph library
        try:
            from core.glyphs.library import GlyphLibrary
            lib = GlyphLibrary()
            glyphs = {ptype: lib.get(ptype) for ptype in PrimitiveType}
            print("   ✅ Loaded existing glyph library")
        except ImportError:
            print("   ⚠️  No existing glyph library found, using built-in")

        # Add built-in glyphs for core primitives
        glyphs.update({
            PrimitiveType.CIRCLE: CircleGlyph(),
            PrimitiveType.RECTANGLE: RectangleGlyph(),
            PrimitiveType.LINE: LineGlyph(),
            PrimitiveType.ARROW: ArrowGlyph(),
            PrimitiveType.CHARGE: ChargeGlyph(),
            PrimitiveType.CAPACITOR_PLATE: PlateGlyph(),
            PrimitiveType.BATTERY_SYMBOL: BatteryGlyph(),
            PrimitiveType.RESISTOR_SYMBOL: ResistorGlyph(),
            PrimitiveType.CAPACITOR_SYMBOL: CapacitorGlyph(),
            PrimitiveType.MASS: MassGlyph(),
            PrimitiveType.LENS: LensGlyph(),
            PrimitiveType.POLYLINE: PolylineGlyph(),
            PrimitiveType.PULLEY: PulleyGlyph(),
            PrimitiveType.FIELD_LINE: FieldLineGlyph(),
            PrimitiveType.SPRING: SpringGlyph(),
            PrimitiveType.TEXT: TextGlyph(),
        })

        return glyphs

    def _load_domain_themes(self) -> Dict:
        """Load domain themes from JSON configs"""

        themes = {}

        for domain in PhysicsDomain:
            theme_file = self.domains_path / domain.value / "theme.json"
            if theme_file.exists():
                with open(theme_file) as f:
                    themes[domain] = json.load(f)

        # Default theme
        themes['default'] = {
            'name': 'default',
            'styles': {
                'exam': {
                    'canvas': {'background': '#ffffff', 'width': 1200, 'height': 800},
                    'components': {'stroke': '#000000', 'stroke_width': 2, 'fill': 'none'},
                    'labels': {'font_size': 14, 'font_weight': 'normal', 'fill': '#000000'}
                }
            }
        }

        return themes

    def _load_embellishments(self) -> Dict:
        """Load domain embellishments (field lines, etc.)"""

        embellishments = {}

        # Electrostatics: field lines, equipotential lines
        embellishments[PhysicsDomain.ELECTROSTATICS] = {
            'field_lines': True,
            'equipotential': False
        }

        # Current electricity: current flow arrows
        embellishments[PhysicsDomain.CURRENT_ELECTRICITY] = {
            'current_flow': True,
            'voltage_labels': False
        }

        # Mechanics: force vectors, trajectory
        embellishments[PhysicsDomain.MECHANICS] = {
            'force_vectors': True,
            'trajectory': False
        }

        return embellishments

    def _apply_theme(self, scene: Scene, spec: CanonicalProblemSpec = None) -> Dict:
        """Step 1: Apply domain-specific theme"""

        domain = spec.domain if spec else PhysicsDomain.UNKNOWN
        style_profile = scene.metadata.get('style_profile', 'exam')

        # Get theme for domain
        if domain in self.themes:
            theme_config = self.themes[domain]
        else:
            theme_config = self.themes['default']

        # Get style from theme
        if 'styles' in theme_config and style_profile in theme_config['styles']:
            theme = theme_config['styles'][style_profile]
        else:
            theme = self.themes['default']['styles']['exam']

        # Add metadata
        theme['name'] = f"{domain.value}_{style_profile}" if spec else 'default'

        return theme

    def _render_objects(self, scene: Scene, theme: Dict) -> List[str]:
        """Step 2: Render all objects using glyphs"""

        svg_parts = []

        for obj in scene.objects:
            if not obj.position:
                continue  # Skip unpositioned objects

            # Get glyph for object type
            glyph = self.glyphs.get(obj.type)

            if glyph:
                # Render using glyph
                svg = glyph.render(
                    position=obj.position,
                    properties=obj.properties,
                    style=obj.style or theme.get('components', {})
                )
                svg_parts.append(svg)
            else:
                # Fallback: generic shape
                x = obj.position.get('x', 0)
                y = obj.position.get('y', 0)
                svg_parts.append(f'<circle cx="{x}" cy="{y}" r="10" fill="gray" opacity="0.5"/>')

        return svg_parts

    def _add_embellishments(self, scene: Scene, spec: CanonicalProblemSpec, theme: Dict) -> List[str]:
        """Step 3: Add domain-specific embellishments"""

        svg_parts = []

        if not spec:
            return svg_parts

        embellishment_config = self.embellishments.get(spec.domain, {})

        # Electrostatics: field lines
        if spec.domain == PhysicsDomain.ELECTROSTATICS and embellishment_config.get('field_lines'):
            charges = [obj for obj in scene.objects if obj.type == PrimitiveType.CHARGE]
            svg_parts.extend(self._render_field_lines(charges))

        # Circuits: current flow
        if spec.domain == PhysicsDomain.CURRENT_ELECTRICITY and embellishment_config.get('current_flow'):
            svg_parts.extend(self._render_current_flow(scene))

        # Mechanics: force vectors (already in scene, just ensure visibility)
        if spec.domain == PhysicsDomain.MECHANICS and embellishment_config.get('force_vectors'):
            pass  # Forces already rendered as arrows

        return svg_parts

    def _render_field_lines(self, charges: List[SceneObject]) -> List[str]:
        """Render electric field lines between charges"""

        svg_parts = []

        for i, charge1 in enumerate(charges):
            for charge2 in charges[i+1:]:
                if not charge1.position or not charge2.position:
                    continue

                x1 = charge1.position.get('x', 0)
                y1 = charge1.position.get('y', 0)
                x2 = charge2.position.get('x', 0)
                y2 = charge2.position.get('y', 0)

                # Draw field line (curved)
                svg_parts.append(
                    f'<path d="M {x1} {y1} Q {(x1+x2)/2} {(y1+y2)/2-30} {x2} {y2}" '
                    f'stroke="#0066cc" stroke-width="1" fill="none" stroke-dasharray="5,5" opacity="0.6"/>'
                )

        return svg_parts

    def _render_current_flow(self, scene: Scene) -> List[str]:
        """Render current flow arrows in circuit"""

        svg_parts = []

        # Find wires and add current direction arrows
        # TODO: Implement based on circuit topology

        return svg_parts

    def _render_labels(self, scene: Scene, theme: Dict) -> List[str]:
        """Step 4: Render labels for all objects"""

        svg_parts = []

        label_style = theme.get('labels', {})
        font_size = label_style.get('font_size', 14)
        font_weight = label_style.get('font_weight', 'normal')
        fill = label_style.get('fill', '#000000')

        for obj in scene.objects:
            label = obj.properties.get('label')
            if label and obj.position:
                # Get label position (computed in layout engine)
                label_pos = obj.properties.get('label_position', {})
                x = label_pos.get('x', obj.position.get('x', 0))
                y = label_pos.get('y', obj.position.get('y', 0) - 15)

                svg_parts.append(
                    f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="{font_weight}" '
                    f'fill="{fill}" text-anchor="middle">{label}</text>'
                )

        return svg_parts

    def _render_legend(self, scene: Scene, theme: Dict) -> str:
        """Step 4b: Render legend (exam mode only)"""

        style_profile = scene.metadata.get('style_profile', 'exam')
        if style_profile != 'exam':
            return ""

        legend_x = self.width - 250
        legend_y = 50

        svg = f'<rect x="{legend_x}" y="{legend_y}" width="230" height="150" fill="white" stroke="black" stroke-width="1" opacity="0.9"/>'
        svg += f'<text x="{legend_x + 10}" y="{legend_y + 25}" font-size="14" font-weight="bold">Legend</text>'

        # Add object descriptions
        y_offset = legend_y + 50
        for i, obj in enumerate(scene.objects[:5]):  # Max 5 items
            obj_type = obj.type.value.replace("_", " ").title()
            obj_label = obj.properties.get("label", obj.id)

            svg += f'<text x="{legend_x + 10}" y="{y_offset}" font-size="12">{obj_label}: {obj_type}</text>'
            y_offset += 20

        return svg

    def _assemble_svg(self, scene: Scene, theme: Dict, object_svg: List[str],
                     embellishments_svg: List[str], labels_svg: List[str], legend_svg: str) -> str:
        """Step 5: Assemble final SVG document"""

        canvas = theme.get('canvas', {})
        bg_color = canvas.get('background', '#ffffff')

        svg_parts = [
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            self._add_defs(),
            f'<rect width="100%" height="100%" fill="{bg_color}"/>',
        ]

        # Add all rendered parts
        svg_parts.extend(object_svg)
        svg_parts.extend(embellishments_svg)
        svg_parts.extend(labels_svg)
        svg_parts.append(legend_svg)

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def _render_tikz(self, scene: Scene, spec: CanonicalProblemSpec = None) -> str:
        lines = ["\\begin{tikzpicture}[scale=0.02]"]
        for obj in scene.objects:
            if not obj.position:
                continue
            x = obj.position.get('x', 0)
            y = obj.position.get('y', 0)
            label = obj.properties.get('label', obj.id)
            if obj.type == PrimitiveType.RECTANGLE:
                width = obj.properties.get('width', 100)
                height = obj.properties.get('height', 60)
                lines.append(f"  \\draw ({x},{y}) rectangle ({x + width},{y + height});")
            elif obj.type == PrimitiveType.CIRCLE:
                radius = obj.properties.get('radius', 40)
                lines.append(f"  \\draw ({x},{y}) circle ({radius});")
            elif obj.type == PrimitiveType.ARROW:
                dx = obj.properties.get('dx', 80)
                dy = obj.properties.get('dy', 0)
                lines.append(f"  \\draw[->] ({x},{y}) -- ({x + dx},{y + dy});")
            else:
                lines.append(f"  \\fill ({x},{y}) circle (5);")
            if label:
                lines.append(f"  \\node[below] at ({x},{y}) {{{label}}};")
        lines.append("\\end{tikzpicture}")
        return "\n".join(lines)

    def _svg_to_png(self, svg: str) -> str:
        try:
            import base64
            import cairosvg  # type: ignore
            png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'),
                                         output_width=self.width,
                                         output_height=self.height)
            return base64.b64encode(png_bytes).decode('utf-8')
        except Exception as exc:
            print(f"⚠️  PNG conversion unavailable ({exc}); returning SVG instead")
            return svg

    def _optimize_svg(self, svg: str) -> str:
        try:
            from scour import scour  # type: ignore
            options = scour.sanitizeOptions()
            options.remove_metadata = True
            options.strip_comments = True
            optimized, _ = scour.scourString(svg, options=options)
            return optimized
        except Exception:
            return svg

    def _add_defs(self) -> str:
        """Add SVG definitions (markers, gradients)"""
        return '''
        <defs>
            <!-- Arrowhead marker -->
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="black"/>
            </marker>
            <!-- Field line marker -->
            <marker id="field-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                <polygon points="0 0, 8 3, 0 6" fill="#0066cc"/>
            </marker>
        </defs>
        '''


# ============================================================================
# Built-in Glyphs (minimal implementations)
# ============================================================================

class CircleGlyph:
    """Render circle primitive"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        r = properties.get('radius', position.get('width', 20) / 2)
        fill = properties.get('fill', style.get('fill', 'none'))
        stroke = style.get('stroke', '#000000')
        stroke_width = style.get('stroke_width', 2)

        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


class RectangleGlyph:
    """Render rectangle primitive"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        # FIX: Read dimensions from properties, NOT position
        # Layout engine stores dimensions in properties, not position
        w = properties.get('width', 40)
        h = properties.get('height', 40)
        fill = properties.get('fill', style.get('fill', 'none'))
        fill_opacity = properties.get('fill_opacity', 1.0)
        stroke = style.get('stroke', '#000000')
        stroke_width = style.get('stroke_width', 2)

        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" fill-opacity="{fill_opacity}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


class LineGlyph:
    """Render line primitive"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x1 = position.get('x', 0)
        y1 = position.get('y', 0)
        x2 = position.get('x2', x1 + position.get('width', 100))
        y2 = position.get('y2', y1)
        stroke = style.get('stroke', '#000000')
        stroke_width = style.get('stroke_width', 2)

        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


class ArrowGlyph:
    """Render arrow (force/vector)"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        direction = properties.get('direction', 'right')
        length = properties.get('length', 60)
        color = properties.get('color', '#cc0000')

        # Calculate endpoint based on direction
        if direction == 'upward' or direction == 'up':
            x2, y2 = x, y - length
        elif direction == 'downward' or direction == 'down':
            x2, y2 = x, y + length
        elif direction == 'right':
            x2, y2 = x + length, y
        elif direction == 'left':
            x2, y2 = x - length, y
        else:
            x2, y2 = x + length, y

        return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2" marker-end="url(#arrowhead)"/>'


class ChargeGlyph:
    """Render point charge"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        sign = properties.get('sign', '+')
        r = 15

        color = '#ff0000' if sign == '+' else '#0000ff'

        svg = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="black" stroke-width="2"/>'
        svg += f'<text x="{x}" y="{y+5}" font-size="16" font-weight="bold" fill="white" text-anchor="middle">{sign}</text>'

        return svg


class PlateGlyph:
    """Render capacitor plate"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        w = position.get('width', 300)
        h = position.get('height', 10)

        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#666666" stroke="black" stroke-width="2"/>'


class BatteryGlyph:
    """Render battery symbol"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)

        svg = f'<line x1="{x-10}" y1="{y-15}" x2="{x-10}" y2="{y+15}" stroke="black" stroke-width="3"/>'  # Long plate
        svg += f'<line x1="{x+10}" y1="{y-8}" x2="{x+10}" y2="{y+8}" stroke="black" stroke-width="3"/>'  # Short plate

        return svg


class ResistorGlyph:
    """Render resistor symbol"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)

        # Zigzag pattern
        path = f'M {x-30} {y} l 10 -10 l 10 20 l 10 -20 l 10 20 l 10 -20 l 10 10'

        return f'<path d="{path}" stroke="black" stroke-width="2" fill="none"/>'


class CapacitorGlyph:
    """Render capacitor symbol"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)

        svg = f'<line x1="{x-5}" y1="{y-15}" x2="{x-5}" y2="{y+15}" stroke="black" stroke-width="2"/>'
        svg += f'<line x1="{x+5}" y1="{y-15}" x2="{x+5}" y2="{y+15}" stroke="black" stroke-width="2"/>'

        return svg


class MassGlyph:
    """Render mass/block"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        w = position.get('width', 60)
        h = position.get('height', 60)

        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#cccccc" stroke="black" stroke-width="2"/>'

class FieldLineGlyph:
    """Renders an electric or magnetic field line."""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        source = self._get_obj(scene, properties.get('source'))
        target = self._get_obj(scene, properties.get('target'))

        if not source or not source.position or not target or not target.position:
            return "<!-- FieldLine glyph missing source/target positions -->"

        x1, y1 = source.position['x'], source.position['y']
        x2, y2 = target.position['x'], target.position['y']
        
        # Simple curved path for now
        cx = (x1 + x2) / 2 + (y1 - y2) * 0.2
        cy = (y1 + y2) / 2 + (x2 - x1) * 0.2

        return (f'<path d="M {x1} {y1} Q {cx} {cy} {x2} {y2}" '
                f'stroke="#0066cc" stroke-width="1.5" fill="none" stroke-dasharray="4,4" opacity="0.7" marker-end="url(#field-arrow)"/>')

class LensGlyph:
    """Render a thin lens symbol"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        height = 200
        
        svg = f'<line x1="{x}" y1="{y - height/2}" x2="{x}" y2="{y + height/2}" stroke="#42a5f5" stroke-width="4"/>'
        # Arrowheads for converging lens
        if properties.get('type') == 'converging':
            svg += f'<path d="M {x-10},{y - height/2} L {x},{y - height/2 - 15} L {x+10},{y - height/2}" fill="none" stroke="#42a5f5" stroke-width="4"/>'
            svg += f'<path d="M {x-10},{y + height/2} L {x},{y + height/2 + 15} L {x+10},{y + height/2}" fill="none" stroke="#42a5f5" stroke-width="4"/>'
        return svg

class FocalPointGlyph:
    """Render a focal point marker"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        label = properties.get('label', 'F')
        
        svg = f'<circle cx="{x}" cy="{y}" r="5" fill="#d32f2f"/>'
        svg += f'<text x="{x}" y="{y + 25}" text-anchor="middle" font-size="14" fill="#d32f2f">{label}</text>'
        return svg

class PointGlyph:
    """Render a simple point marker"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        label = properties.get('label', '')
        
        svg = f'<circle cx="{x}" cy="{y}" r="4" fill="black"/>'
        if label:
            svg += f'<text x="{x+5}" y="{y-5}" font-size="12">{label}</text>'
        return svg

class PolylineGlyph:
    """Render a polyline, used for rays"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:
        """
        Renders a polyline by connecting waypoints defined in properties.
        """
        properties = obj.properties
        style = obj.style or theme.get('components', {})

        waypoints_pos = self.resolve_waypoints(scene, obj)
        if not waypoints_pos or len(waypoints_pos) < 2:
            return "<!-- PolylineGlyph missing waypoint data -->"

        color = properties.get('color', '#ff6f00')
        stroke_width = style.get('stroke_width', 2)
        
        path_data = f"M {waypoints_pos[0][0]} {waypoints_pos[0][1]}"
        for point in waypoints_pos[1:]:
            path_data += f" L {point[0]} {point[1]}"
            
        return f'<path d="{path_data}" stroke="{color}" stroke-width="{stroke_width}" fill="none" marker-end="url(#arrowhead)"/>'

    def resolve_waypoints(self, scene: Scene, obj: SceneObject) -> List[Tuple[float, float]]:
        """Helper method to resolve waypoint IDs to coordinates."""
        waypoint_ids = obj.properties.get("segments", [])
        resolved_points = []
        for point_id in waypoint_ids:
            point_obj = next((o for o in scene.objects if o.id == point_id), None)
            if point_obj and point_obj.position:
                resolved_points.append((point_obj.position['x'], point_obj.position['y']))
        return resolved_points

class SpringGlyph:
    """Render a spring"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x1 = position.get('x', 0)
        y1 = position.get('y', 0)
        x2 = position.get('x2', x1 + 100)
        y2 = position.get('y2', y1)
        coils = properties.get('coils', 10)
        radius = properties.get('radius', 10)

        # Path for a horizontal spring
        path = f'M {x1} {y1}'
        for i in range(coils):
            path += f' l 5 {radius}'
            path += f' l 5 -{2*radius}'
            path += f' l 5 {radius}'

        return f'<path d="{path}" stroke="black" stroke-width="2" fill="none"/>'


class PulleyGlyph:
    """Render a pulley"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:

        x = position.get('x', 0)
        y = position.get('y', 0)
        r = properties.get('radius', 30)

        svg = f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="black" stroke-width="3"/>'
        svg += f'<circle cx="{x}" cy="{y}" r="{r-10}" fill="none" stroke="black" stroke-width="1"/>'

        return svg

class TextGlyph:
    """Render text labels and annotations"""
    def render(self, position: Dict, properties: Dict, style: Dict) -> str:
        x = position.get('x', 0)
        y = position.get('y', 0)
        text = properties.get('text', '')

        # Style properties
        font_size = properties.get('font_size', style.get('font_size', 14))
        font_weight = properties.get('font_weight', style.get('font_weight', 'normal'))
        font_family = style.get('font_family', 'Arial, sans-serif')
        fill = style.get('fill', '#000000')
        text_anchor = style.get('text_anchor', 'start')

        svg = f'<text x="{x}" y="{y}" font-size="{font_size}" font-weight="{font_weight}" '
        svg += f'font-family="{font_family}" fill="{fill}" text-anchor="{text_anchor}">{text}</text>'

        return svg
