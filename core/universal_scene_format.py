"""
Universal Scene Representation Format for All STEM Diagrams
============================================================

This module defines a universal, extensible format for representing all types
of STEM diagrams: physics, chemistry, biology, mathematics, engineering, etc.

Design Principles:
- Domain-agnostic core structure
- Subject-specific extensions via metadata
- Support for 2D and 3D spatial layouts
- Relationships and constraints
- Annotations and labels
- Style and theming

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import json


class DiagramDomain(Enum):
    """Supported diagram domains"""
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    MATHEMATICS = "mathematics"
    ELECTRONICS = "electronics"
    MECHANICS = "mechanics"
    THERMODYNAMICS = "thermodynamics"
    OPTICS = "optics"
    GEOMETRY = "geometry"
    CIRCUITS = "circuits"
    ORGANIC_CHEMISTRY = "organic_chemistry"
    CELL_BIOLOGY = "cell_biology"
    ANATOMY = "anatomy"
    GRAPHS = "graphs"
    STATISTICS = "statistics"


class DiagramType(Enum):
    """Specific diagram types within domains"""
    # Physics
    FREE_BODY_DIAGRAM = "free_body_diagram"
    CIRCUIT_DIAGRAM = "circuit_diagram"
    RAY_DIAGRAM = "ray_diagram"
    FIELD_DIAGRAM = "field_diagram"
    ENERGY_DIAGRAM = "energy_diagram"
    WAVE_DIAGRAM = "wave_diagram"

    # Chemistry
    MOLECULAR_STRUCTURE = "molecular_structure"
    LEWIS_STRUCTURE = "lewis_structure"
    REACTION_MECHANISM = "reaction_mechanism"
    PHASE_DIAGRAM = "phase_diagram"
    ORBITAL_DIAGRAM = "orbital_diagram"

    # Biology
    CELL_DIAGRAM = "cell_diagram"
    DNA_STRUCTURE = "dna_structure"
    METABOLIC_PATHWAY = "metabolic_pathway"
    ANATOMICAL_DIAGRAM = "anatomical_diagram"
    ECOSYSTEM_DIAGRAM = "ecosystem_diagram"

    # Mathematics
    FUNCTION_GRAPH = "function_graph"
    GEOMETRIC_FIGURE = "geometric_figure"
    VECTOR_DIAGRAM = "vector_diagram"
    PROBABILITY_TREE = "probability_tree"
    STATISTICAL_CHART = "statistical_chart"

    # Generic
    SCHEMATIC = "schematic"
    CONCEPTUAL = "conceptual"
    PROCESS_FLOW = "process_flow"


class ObjectType(Enum):
    """Universal object types"""
    # Geometric primitives
    POINT = "point"
    LINE = "line"
    CURVE = "curve"
    CIRCLE = "circle"
    ELLIPSE = "ellipse"
    RECTANGLE = "rectangle"
    POLYGON = "polygon"

    # Physics objects
    MASS = "mass"
    SPRING = "spring"
    PULLEY = "pulley"
    INCLINE = "incline"
    FORCE_VECTOR = "force_vector"

    # Circuit elements
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    BATTERY = "battery"
    WIRE = "wire"
    SWITCH = "switch"
    DIODE = "diode"

    # Chemistry objects
    ATOM = "atom"
    BOND = "bond"
    MOLECULE = "molecule"
    ORBITAL = "orbital"
    ELECTRON = "electron"

    # Biology objects
    CELL = "cell"
    ORGANELLE = "organelle"
    PROTEIN = "protein"
    DNA_STRAND = "dna_strand"
    MEMBRANE = "membrane"

    # Math objects
    AXIS = "axis"
    GRAPH_POINT = "graph_point"
    CURVE_PLOT = "curve_plot"
    VECTOR = "vector"
    ANGLE = "angle"

    # Generic
    LABEL = "label"
    ANNOTATION = "annotation"
    CONTAINER = "container"
    GROUP = "group"


class RelationType(Enum):
    """Types of relationships between objects"""
    CONNECTED_TO = "connected_to"
    CONTAINS = "contains"
    PART_OF = "part_of"
    ACTS_ON = "acts_on"
    BONDED_TO = "bonded_to"
    ADJACENT_TO = "adjacent_to"
    PARALLEL_TO = "parallel_to"
    PERPENDICULAR_TO = "perpendicular_to"
    EQUAL_TO = "equal_to"
    PROPORTIONAL_TO = "proportional_to"
    ALIGNED_WITH = "aligned_with"
    FLOWS_TO = "flows_to"
    REACTS_WITH = "reacts_with"
    POSITIONED_AT = "positioned_at"


@dataclass
class Position:
    """2D or 3D position"""
    x: float
    y: float
    z: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Position':
        return cls(data["x"], data["y"], data.get("z", 0.0))


@dataclass
class Dimensions:
    """Object dimensions"""
    width: float = 0.0
    height: float = 0.0
    depth: float = 0.0
    radius: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "radius": self.radius
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Dimensions':
        return cls(
            data.get("width", 0.0),
            data.get("height", 0.0),
            data.get("depth", 0.0),
            data.get("radius", 0.0)
        )


@dataclass
class Style:
    """Visual styling for objects"""
    color: str = "#000000"
    fill_color: Optional[str] = None
    stroke_width: float = 2.0
    opacity: float = 1.0
    dashed: bool = False
    dash_pattern: Optional[List[float]] = None
    font_size: int = 14
    font_family: str = "Arial"
    font_weight: str = "normal"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "color": self.color,
            "fill_color": self.fill_color,
            "stroke_width": self.stroke_width,
            "opacity": self.opacity,
            "dashed": self.dashed,
            "dash_pattern": self.dash_pattern,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "font_weight": self.font_weight
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Style':
        return cls(
            data.get("color", "#000000"),
            data.get("fill_color"),
            data.get("stroke_width", 2.0),
            data.get("opacity", 1.0),
            data.get("dashed", False),
            data.get("dash_pattern"),
            data.get("font_size", 14),
            data.get("font_family", "Arial"),
            data.get("font_weight", "normal")
        )


@dataclass
class SceneObject:
    """Universal scene object representation"""
    id: str
    object_type: ObjectType
    position: Position
    dimensions: Dimensions = field(default_factory=Dimensions)
    rotation: float = 0.0  # degrees
    style: Style = field(default_factory=Style)
    label: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "object_type": self.object_type.value,
            "position": self.position.to_dict(),
            "dimensions": self.dimensions.to_dict(),
            "rotation": self.rotation,
            "style": self.style.to_dict(),
            "label": self.label,
            "properties": self.properties,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneObject':
        return cls(
            id=data["id"],
            object_type=ObjectType(data["object_type"]),
            position=Position.from_dict(data["position"]),
            dimensions=Dimensions.from_dict(data["dimensions"]),
            rotation=data.get("rotation", 0.0),
            style=Style.from_dict(data.get("style", {})),
            label=data.get("label"),
            properties=data.get("properties", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class Relationship:
    """Relationship between objects"""
    id: str
    relation_type: RelationType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    bidirectional: bool = False
    strength: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "relation_type": self.relation_type.value,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "properties": self.properties,
            "bidirectional": self.bidirectional,
            "strength": self.strength
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        return cls(
            id=data["id"],
            relation_type=RelationType(data["relation_type"]),
            source_id=data["source_id"],
            target_id=data["target_id"],
            properties=data.get("properties", {}),
            bidirectional=data.get("bidirectional", False),
            strength=data.get("strength", 1.0)
        )


@dataclass
class Constraint:
    """Spatial or logical constraint"""
    constraint_type: str  # e.g., "distance", "alignment", "ordering"
    objects: List[str]  # object IDs
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_type": self.constraint_type,
            "objects": self.objects,
            "parameters": self.parameters,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Constraint':
        return cls(
            constraint_type=data["constraint_type"],
            objects=data["objects"],
            parameters=data.get("parameters", {}),
            priority=data.get("priority", 1.0)
        )


@dataclass
class Annotation:
    """Text annotation or measurement"""
    id: str
    text: str
    position: Position
    target_ids: List[str] = field(default_factory=list)
    annotation_type: str = "label"  # label, measurement, note, equation
    style: Style = field(default_factory=Style)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "position": self.position.to_dict(),
            "target_ids": self.target_ids,
            "annotation_type": self.annotation_type,
            "style": self.style.to_dict(),
            "properties": self.properties
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        return cls(
            id=data["id"],
            text=data["text"],
            position=Position.from_dict(data["position"]),
            target_ids=data.get("target_ids", []),
            annotation_type=data.get("annotation_type", "label"),
            style=Style.from_dict(data.get("style", {})),
            properties=data.get("properties", {})
        )


@dataclass
class UniversalScene:
    """
    Universal scene representation for all STEM diagrams

    This is the core data structure that represents any STEM diagram
    in a domain-agnostic way, with subject-specific extensions via metadata.
    """

    # Core identification
    scene_id: str
    domain: DiagramDomain
    diagram_type: DiagramType
    title: Optional[str] = None
    description: Optional[str] = None

    # Scene content
    objects: List[SceneObject] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)

    # Scene properties
    canvas_width: float = 800.0
    canvas_height: float = 600.0
    background_color: str = "#FFFFFF"
    grid_enabled: bool = False
    grid_spacing: float = 50.0

    # Domain-specific data
    physics_data: Dict[str, Any] = field(default_factory=dict)
    chemistry_data: Dict[str, Any] = field(default_factory=dict)
    biology_data: Dict[str, Any] = field(default_factory=dict)
    math_data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_object(self, obj: SceneObject) -> None:
        """Add an object to the scene"""
        self.objects.append(obj)

    def add_relationship(self, rel: Relationship) -> None:
        """Add a relationship to the scene"""
        self.relationships.append(rel)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the scene"""
        self.constraints.append(constraint)

    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to the scene"""
        self.annotations.append(annotation)

    def get_object(self, object_id: str) -> Optional[SceneObject]:
        """Get an object by ID"""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None

    def get_relationships_for_object(self, object_id: str) -> List[Relationship]:
        """Get all relationships involving an object"""
        return [
            rel for rel in self.relationships
            if rel.source_id == object_id or rel.target_id == object_id
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary"""
        return {
            "scene_id": self.scene_id,
            "domain": self.domain.value,
            "diagram_type": self.diagram_type.value,
            "title": self.title,
            "description": self.description,
            "objects": [obj.to_dict() for obj in self.objects],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "constraints": [c.to_dict() for c in self.constraints],
            "annotations": [a.to_dict() for a in self.annotations],
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "background_color": self.background_color,
            "grid_enabled": self.grid_enabled,
            "grid_spacing": self.grid_spacing,
            "physics_data": self.physics_data,
            "chemistry_data": self.chemistry_data,
            "biology_data": self.biology_data,
            "math_data": self.math_data,
            "metadata": self.metadata
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert scene to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalScene':
        """Create scene from dictionary"""
        return cls(
            scene_id=data["scene_id"],
            domain=DiagramDomain(data["domain"]),
            diagram_type=DiagramType(data["diagram_type"]),
            title=data.get("title"),
            description=data.get("description"),
            objects=[SceneObject.from_dict(o) for o in data.get("objects", [])],
            relationships=[Relationship.from_dict(r) for r in data.get("relationships", [])],
            constraints=[Constraint.from_dict(c) for c in data.get("constraints", [])],
            annotations=[Annotation.from_dict(a) for a in data.get("annotations", [])],
            canvas_width=data.get("canvas_width", 800.0),
            canvas_height=data.get("canvas_height", 600.0),
            background_color=data.get("background_color", "#FFFFFF"),
            grid_enabled=data.get("grid_enabled", False),
            grid_spacing=data.get("grid_spacing", 50.0),
            physics_data=data.get("physics_data", {}),
            chemistry_data=data.get("chemistry_data", {}),
            biology_data=data.get("biology_data", {}),
            math_data=data.get("math_data", {}),
            metadata=data.get("metadata", {})
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'UniversalScene':
        """Create scene from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save(self, filepath: str) -> None:
        """Save scene to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'UniversalScene':
        """Load scene from file"""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())


# Example helper functions for common scene operations

def create_circuit_scene(scene_id: str, title: str = "Circuit Diagram") -> UniversalScene:
    """Create a basic circuit diagram scene"""
    return UniversalScene(
        scene_id=scene_id,
        domain=DiagramDomain.ELECTRONICS,
        diagram_type=DiagramType.CIRCUIT_DIAGRAM,
        title=title,
        canvas_width=1000,
        canvas_height=600
    )


def create_molecular_scene(scene_id: str, title: str = "Molecular Structure") -> UniversalScene:
    """Create a basic molecular structure scene"""
    return UniversalScene(
        scene_id=scene_id,
        domain=DiagramDomain.CHEMISTRY,
        diagram_type=DiagramType.MOLECULAR_STRUCTURE,
        title=title,
        canvas_width=800,
        canvas_height=600
    )


def create_cell_scene(scene_id: str, title: str = "Cell Diagram") -> UniversalScene:
    """Create a basic cell diagram scene"""
    return UniversalScene(
        scene_id=scene_id,
        domain=DiagramDomain.BIOLOGY,
        diagram_type=DiagramType.CELL_DIAGRAM,
        title=title,
        canvas_width=1000,
        canvas_height=800
    )


def create_graph_scene(scene_id: str, title: str = "Function Graph") -> UniversalScene:
    """Create a basic function graph scene"""
    return UniversalScene(
        scene_id=scene_id,
        domain=DiagramDomain.MATHEMATICS,
        diagram_type=DiagramType.FUNCTION_GRAPH,
        title=title,
        canvas_width=800,
        canvas_height=600,
        grid_enabled=True
    )


if __name__ == "__main__":
    # Example usage
    print("Universal Scene Format - Example Usage\n" + "=" * 50)

    # Create a simple circuit scene
    scene = create_circuit_scene("circuit_001", "Simple RC Circuit")

    # Add a battery
    battery = SceneObject(
        id="battery_1",
        object_type=ObjectType.BATTERY,
        position=Position(100, 300),
        dimensions=Dimensions(width=60, height=40),
        label="12V",
        properties={"voltage": 12.0, "unit": "V"}
    )
    scene.add_object(battery)

    # Add a resistor
    resistor = SceneObject(
        id="resistor_1",
        object_type=ObjectType.RESISTOR,
        position=Position(300, 300),
        dimensions=Dimensions(width=80, height=20),
        label="100Ω",
        properties={"resistance": 100.0, "unit": "Ω", "tolerance": 0.05}
    )
    scene.add_object(resistor)

    # Add a capacitor
    capacitor = SceneObject(
        id="capacitor_1",
        object_type=ObjectType.CAPACITOR,
        position=Position(500, 300),
        dimensions=Dimensions(width=40, height=60),
        label="10μF",
        properties={"capacitance": 10e-6, "unit": "F"}
    )
    scene.add_object(capacitor)

    # Add connections
    wire1 = Relationship(
        id="wire_1",
        relation_type=RelationType.CONNECTED_TO,
        source_id="battery_1",
        target_id="resistor_1",
        properties={"connection_type": "series"}
    )
    scene.add_relationship(wire1)

    wire2 = Relationship(
        id="wire_2",
        relation_type=RelationType.CONNECTED_TO,
        source_id="resistor_1",
        target_id="capacitor_1",
        properties={"connection_type": "series"}
    )
    scene.add_relationship(wire2)

    # Add annotation
    annotation = Annotation(
        id="note_1",
        text="RC time constant: τ = RC",
        position=Position(300, 150),
        annotation_type="equation"
    )
    scene.add_annotation(annotation)

    # Print scene summary
    print(f"\nScene: {scene.title}")
    print(f"Domain: {scene.domain.value}")
    print(f"Type: {scene.diagram_type.value}")
    print(f"Objects: {len(scene.objects)}")
    print(f"Relationships: {len(scene.relationships)}")
    print(f"Annotations: {len(scene.annotations)}")

    # Export to JSON
    json_output = scene.to_json()
    print(f"\nJSON Output (first 500 chars):\n{json_output[:500]}...")

    print("\n✅ Universal Scene Format loaded successfully!")
