"""
Universal Scene Description - The Contract Between All Components
This is THE most important addition - everything else builds on this
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Version 1.0 - Freeze this schema
SCHEMA_VERSION = "1.0"

class PrimitiveType(Enum):
    """Universal primitive types that cover ALL physics"""
    # Geometry
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    LINE = "line"
    POLYLINE = "polyline"
    POLYGON = "polygon"
    ARC = "arc"
    CURVE = "curve"

    # Physics-specific but generic
    ARROW = "arrow"  # Forces, vectors, rays
    SPRING = "spring"  # Oscillators
    CAPACITOR_PLATE = "plate"  # Parallel plates
    CHARGE = "charge"  # Point charges
    FIELD_LINE = "field_line"  # E/B fields

    # Composite glyphs
    CAPACITOR_SYMBOL = "capacitor"  # ||(
    RESISTOR_SYMBOL = "resistor"  # ~~~
    BATTERY_SYMBOL = "battery"  # -||-
    LENS = "lens"  # Convex/concave
    MASS = "mass"  # Block/sphere
    PULLEY = "pulley"  # Circle with groove

    # Annotations and labels
    TEXT = "text"  # Labels, dimension annotations, charge markers
    DIMENSION_ARROW = "dimension_arrow"  # Double-headed arrows with measurement

class ConstraintType(Enum):
    """Universal constraints for layout"""
    # Geometric
    COINCIDENT = "coincident"
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    COLLINEAR = "collinear"

    # Metric
    DISTANCE = "distance"
    ANGLE = "angle"
    LENGTH = "length"

    # Topological
    CONNECTED = "connected"
    CONTAINS = "contains"
    ADJACENT = "adjacent"

    # Layout
    ALIGNED_H = "aligned_h"
    ALIGNED_V = "aligned_v"
    CENTERED = "centered"
    SYMMETRIC = "symmetric"
    NO_OVERLAP = "no_overlap"

    # New layout constraints for declarative positioning
    RELATIVE_POSITION = "relative_position"  # above, below, left, right
    ALIGNMENT = "alignment"  # horizontal or vertical alignment
    CONTAINMENT = "containment"  # one object contains/between others

    # Generic spatial relationships (for universal constraint solver)
    BETWEEN = "between"        # obj1 is between obj2 and obj3
    # ADJACENT already defined above in Topological section
    ABOVE = "above"            # obj1 is above obj2
    BELOW = "below"            # obj1 is below obj2
    LEFT_OF = "left_of"        # obj1 is left of obj2
    RIGHT_OF = "right_of"      # obj1 is right of obj2
    STACKED_V = "stacked_v"    # objects stacked vertically (top to bottom)
    STACKED_H = "stacked_h"    # objects stacked horizontally (left to right)

class RenderLayer(Enum):
    """
    Explicit rendering layers for z-order control
    Objects are rendered in layer order (0 first, 7 last)
    """
    BACKGROUND = 0      # Grid, axes, coordinate system
    FILL = 1           # Filled shapes (dielectrics, regions)
    SHAPES = 2         # Primary objects (plates, masses, lenses)
    LINES = 3          # Connecting lines, boundaries, field lines
    ARROWS = 4         # Force arrows, vectors, rays
    ANNOTATIONS = 5    # Dimensions, angles, measurements
    LABELS = 6         # Text labels
    FOREGROUND = 7     # Overlays, highlights

@dataclass
class Position:
    """
    Standard position format for all scene objects

    All objects use (x, y) as anchor point, with dimensions in properties.
    This eliminates the confusion between different coordinate formats.

    Backwards compatible: can be converted to/from Dict for legacy code.
    """
    x: float  # Anchor x-coordinate
    y: float  # Anchor y-coordinate
    anchor: str = "center"  # "center", "top-left", "bottom-left", etc.
    rotation: float = 0.0  # Degrees, counter-clockwise from horizontal

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return {
            "x": self.x,
            "y": self.y,
            "anchor": self.anchor,
            "rotation": self.rotation
        }

    @classmethod
    def from_dict(cls, d: Dict) -> 'Position':
        """Create from dictionary (backwards compatibility)"""
        if isinstance(d, Position):
            return d
        return cls(
            x=d.get("x", 0.0),
            y=d.get("y", 0.0),
            anchor=d.get("anchor", "center"),
            rotation=d.get("rotation", 0.0)
        )

@dataclass
class SceneObject:
    """Universal object representation"""
    id: str
    type: PrimitiveType
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict] = None  # Set by solver - supports Dict for backwards compatibility
    style: Optional[Dict] = None  # Visual properties
    layer: RenderLayer = RenderLayer.SHAPES  # Explicit z-order control

    def get_position(self) -> Optional[Position]:
        """Get position as Position object (handles both Dict and Position)"""
        if self.position is None:
            return None
        if isinstance(self.position, Position):
            return self.position
        return Position.from_dict(self.position)

    def set_position(self, pos: Position):
        """Set position from Position object"""
        if isinstance(pos, Position):
            self.position = pos.to_dict()
        else:
            self.position = pos

@dataclass
class Constraint:
    """Universal constraint"""
    type: ConstraintType
    objects: List[str]  # Object IDs
    value: Optional[Any] = None
    tolerance: float = 1e-6
    properties: Dict[str, Any] = field(default_factory=dict)  # Additional constraint parameters

@dataclass
class Scene:
    """THE universal scene description"""
    version: str = SCHEMA_VERSION

    # Metadata
    metadata: Dict = field(default_factory=lambda: {
        "problem_id": "",
        "domain": "",
        "style_profile": "exam",  # or "annotated"
        "seed": 42
    })

    # Coordinate system
    coord_system: Dict = field(default_factory=lambda: {
        "frame": "cartesian",
        "origin": [600, 400],
        "scale": 100,  # pixels per unit
        "extent": [1200, 800],
        "margins": [40, 40, 40, 40]
    })

    # Content
    objects: List[SceneObject] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    annotations: List[Dict] = field(default_factory=list)

    def to_json(self) -> Dict:
        """Export to JSON for serialization"""
        return {
            "version": self.version,
            "metadata": self.metadata,
            "coord_system": self.coord_system,
            "objects": [
                {
                    "id": obj.id,
                    "type": obj.type.value,
                    "properties": obj.properties,
                    "position": obj.position,
                    "style": obj.style
                }
                for obj in self.objects
            ],
            "constraints": [
                {
                    "type": c.type.value,
                    "objects": c.objects,
                    "value": c.value
                }
                for c in self.constraints
            ],
            "annotations": self.annotations
        }

    @classmethod
    def from_legacy_specs(cls, specs: Dict) -> 'Scene':
        """
        Convert existing specs to Scene using domain-specific interpreters
        NOTE: This is a compatibility layer - prefer using interpreters directly
        """
        # Import here to avoid circular dependency
        try:
            from core.interpreters.domain_interpreters import SceneInterpreterFactory

            # Use domain-specific interpreter for rich content
            interpreter = SceneInterpreterFactory.get_interpreter(specs)
            return interpreter.interpret(specs)

        except ImportError:
            # Fallback to simple conversion if interpreters not available
            scene = cls()
            scene.metadata["domain"] = specs.get("problem_type", "unknown")

            # Convert based on domain
            if specs.get("problem_type") == "electrostatics":
                # Convert particles
                for p in specs.get("particles", []):
                    scene.objects.append(SceneObject(
                        id=p.get("id", f"q{len(scene.objects)}"),
                        type=PrimitiveType.CHARGE,
                        properties={
                            "value": p.get("value"),
                            "sign": p.get("sign"),
                            "unit": p.get("unit")
                        }
                    ))

                # Add geometry constraints
                geometry = specs.get("geometry", {})
                if geometry.get("shape") == "square":
                    # Charges at corners of square
                    if len(scene.objects) == 4:
                        scene.constraints.append(Constraint(
                            type=ConstraintType.SYMMETRIC,
                            objects=[obj.id for obj in scene.objects],
                            value="square"
                        ))

            elif specs.get("problem_type") == "current_electricity":
                # Convert capacitors
                for c in specs.get("capacitors", []):
                    scene.objects.append(SceneObject(
                        id=c.get("id"),
                        type=PrimitiveType.CAPACITOR_SYMBOL,
                        properties=c
                    ))

                # Add circuit topology
                topology = specs.get("topology", {})
                if "series" in str(topology):
                    scene.constraints.append(Constraint(
                        type=ConstraintType.CONNECTED,
                        objects=[obj.id for obj in scene.objects],
                        value="series"
                    ))

            return scene
