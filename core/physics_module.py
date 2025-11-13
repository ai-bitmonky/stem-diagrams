#!/usr/bin/env python3
"""
Physics Diagram Module
======================

Domain-specific module for generating physics diagrams:
- Free-body diagrams
- Force vectors
- Spring-mass systems
- Incline planes
- Pulley systems
- Projectile motion
- Energy diagrams

Author: Universal STEM Diagram Generator
Date: November 5, 2025
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Annotation,
    ObjectType, RelationType, DiagramDomain, DiagramType, Position, Dimensions, Style
)


@dataclass
class PhysicsVector:
    """Represents a force or velocity vector"""
    magnitude: float
    angle: float  # degrees from positive x-axis
    label: str
    color: str = "#e74c3c"  # default red for forces


class PhysicsDiagramModule:
    """
    Physics diagram generator

    Handles mechanics, forces, kinematics, and basic physics visualizations
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """
        Generate physics diagram from plan

        Args:
            plan: Diagram plan with entities and relationships
            problem_text: Original problem text

        Returns:
            UniversalScene object
        """
        diagram_type = plan.get('diagram_type', 'free_body')

        # Dispatch to specific diagram type
        if 'free' in diagram_type.lower() and 'body' in diagram_type.lower():
            return self._generate_free_body_diagram(plan, problem_text)
        elif 'spring' in diagram_type.lower():
            return self._generate_spring_mass_diagram(plan, problem_text)
        elif 'incline' in diagram_type.lower() or 'plane' in diagram_type.lower():
            return self._generate_incline_diagram(plan, problem_text)
        elif 'pulley' in diagram_type.lower():
            return self._generate_pulley_diagram(plan, problem_text)
        else:
            # Default: general physics diagram
            return self._generate_general_physics_diagram(plan, problem_text)

    def _generate_free_body_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """Generate a free-body diagram showing forces on an object"""

        scene = UniversalScene(
            scene_id=f"fbd_{hash(problem_text) % 10000}",
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.FREE_BODY_DIAGRAM,
            title="Free-Body Diagram",
            canvas_width=800,
            canvas_height=600
        )

        # Extract entities
        entities = plan.get('entities', [])

        # Find the main object (block, mass, etc.)
        main_object = None
        forces = []

        for entity in entities:
            entity_type = entity.get('type', '').lower()
            if entity_type in ['block', 'mass', 'object', 'body']:
                main_object = entity
            elif entity_type in ['force', 'vector']:
                forces.append(entity)

        if not main_object:
            # Create default object if none found
            main_object = {'type': 'block', 'label': 'm', 'properties': {}}

        # Place main object at center
        obj_x, obj_y = 400, 300
        obj_width, obj_height = 80, 60

        # Create main object
        main_obj = SceneObject(
            id=f"object_{obj_x}_{obj_y}",
            object_type=ObjectType.MASS,
            label=main_object.get('label', 'm'),
            position=Position(obj_x, obj_y),
            dimensions=Dimensions(obj_width, obj_height),
            style=Style(
                color="#2c3e50",
                fill_color="#ecf0f1",
                stroke_width=2.0
            ),
            properties=main_object.get('properties', {})
        )
        scene.objects.append(main_obj)

        # Add forces as vectors
        force_vectors = self._extract_force_vectors(forces, problem_text)

        # Standard force positions around object
        force_positions = {
            'weight': (0, 1),  # downward
            'normal': (0, -1),  # upward
            'tension': (0, -1),  # upward
            'friction': (-1, 0),  # left (opposing motion)
            'applied': (1, 0),  # right
            'drag': (-1, 0),  # opposing
            'thrust': (1, 0),  # forward
        }

        for i, vector in enumerate(force_vectors):
            # Determine direction
            direction = None
            for force_name, dir_vec in force_positions.items():
                if force_name in vector.label.lower():
                    direction = dir_vec
                    break

            if not direction:
                # Use angle from vector or default
                rad = math.radians(vector.angle)
                direction = (math.cos(rad), math.sin(rad))

            # Calculate arrow end point
            arrow_length = min(100, vector.magnitude * 20)  # Scale magnitude
            end_x = obj_x + direction[0] * (obj_width/2 + arrow_length)
            end_y = obj_y + direction[1] * (obj_height/2 + arrow_length)

            # Create force vector as arrow
            force_obj = SceneObject(
                id=f"force_{i}_{obj_x}_{obj_y}",
                object_type=ObjectType.FORCE_VECTOR,
                label=vector.label,
                position=Position(obj_x + direction[0] * obj_width/2,
                                obj_y + direction[1] * obj_height/2),
                dimensions=Dimensions(abs(end_x - obj_x), abs(end_y - obj_y)),
                style=Style(
                    color=vector.color,
                    stroke_width=3.0
                ),
                properties={
                    'magnitude': vector.magnitude,
                    'angle': vector.angle,
                    'end_x': end_x,
                    'end_y': end_y
                }
            )
            scene.objects.append(force_obj)

            # Add relationship (force applies to object)
            scene.relationships.append(Relationship(
                id=f"rel_force_{i}_to_obj",
                relation_type=RelationType.ACTS_ON,
                source_id=force_obj.id,
                target_id=main_obj.id
            ))

        # Add annotation for equilibrium if mentioned
        if 'equilibrium' in problem_text.lower() or 'rest' in problem_text.lower():
            scene.annotations.append(Annotation(
                id="annotation_equilibrium",
                text="ΣF = 0 (Equilibrium)",
                position=Position(50, 50),
                style=Style(color="#27ae60")
            ))

        return scene

    def _generate_spring_mass_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """Generate spring-mass system diagram"""

        scene = UniversalScene(
            scene_id=f"spring_{hash(problem_text) % 10000}",
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.SCHEMATIC,
            title="Spring-Mass System",
            canvas_width=600,
            canvas_height=400
        )

        # Fixed support
        support = SceneObject(
            id="support",
            object_type=ObjectType.RECTANGLE,
            label="",
            position=Position(100, 200),
            dimensions=Dimensions(20, 150),
            style=Style(
                color="#34495e",
                fill_color="#34495e",
                stroke_width=2.0
            ),
            properties={'type': 'fixed_support'}
        )
        scene.objects.append(support)

        # Spring
        spring = SceneObject(
            id="spring",
            object_type=ObjectType.SPRING,
            label="k",
            position=Position(200, 250),
            dimensions=Dimensions(150, 30),
            style=Style(color="#3498db", stroke_width=2.0),
            properties={'type': 'spring', 'stiffness': 'k'}
        )
        scene.objects.append(spring)

        # Mass
        mass = SceneObject(
            id="mass",
            object_type=ObjectType.MASS,
            label="m",
            position=Position(400, 250),
            dimensions=Dimensions(60, 60),
            style=Style(
                color="#2c3e50",
                fill_color="#ecf0f1",
                stroke_width=2.0
            ),
            properties={'type': 'mass'}
        )
        scene.objects.append(mass)

        # Relationships
        scene.relationships.append(Relationship(
            id="rel_support_spring",
            relation_type=RelationType.CONNECTED_TO,
            source_id="support",
            target_id="spring"
        ))
        scene.relationships.append(Relationship(
            id="rel_spring_mass",
            relation_type=RelationType.CONNECTED_TO,
            source_id="spring",
            target_id="mass"
        ))

        return scene

    def _generate_incline_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """Generate inclined plane diagram"""

        scene = UniversalScene(
            scene_id=f"incline_{hash(problem_text) % 10000}",
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.SCHEMATIC,
            title="Inclined Plane",
            canvas_width=700,
            canvas_height=500
        )

        # Extract angle
        angle = self._extract_angle(problem_text)

        # Draw inclined plane
        incline = SceneObject(
            id="incline",
            object_type=ObjectType.INCLINE,
            label=f"{angle}°",
            position=Position(350, 350),
            dimensions=Dimensions(400, 200),
            style=Style(
                color="#34495e",
                fill_color="#95a5a6",
                stroke_width=3.0
            ),
            properties={'angle': angle, 'type': 'incline'}
        )
        scene.objects.append(incline)

        # Object on incline
        obj_x = 350
        obj_y = 250 - (200 * math.sin(math.radians(angle)) / 2)

        obj = SceneObject(
            id="block",
            object_type=ObjectType.MASS,
            label="m",
            position=Position(obj_x, obj_y),
            dimensions=Dimensions(50, 50),
            style=Style(
                color="#2c3e50",
                fill_color="#ecf0f1",
                stroke_width=2.0
            ),
            properties={'type': 'block'}
        )
        scene.objects.append(obj)

        return scene

    def _generate_pulley_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """Generate pulley system diagram"""

        scene = UniversalScene(
            scene_id=f"pulley_{hash(problem_text) % 10000}",
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.SCHEMATIC,
            title="Pulley System",
            canvas_width=600,
            canvas_height=600
        )

        # Pulley
        pulley = SceneObject(
            id="pulley",
            object_type=ObjectType.PULLEY,
            label="",
            position=Position(300, 150),
            dimensions=Dimensions(60, 60),
            style=Style(
                color="#34495e",
                stroke_width=2.0
            ),
            properties={'type': 'pulley'}
        )
        scene.objects.append(pulley)

        # Mass 1 (left side)
        mass1 = SceneObject(
            id="mass1",
            object_type=ObjectType.MASS,
            label="m₁",
            position=Position(220, 350),
            dimensions=Dimensions(60, 60),
            style=Style(
                color="#2c3e50",
                fill_color="#ecf0f1",
                stroke_width=2.0
            ),
            properties={'type': 'mass'}
        )
        scene.objects.append(mass1)

        # Mass 2 (right side)
        mass2 = SceneObject(
            id="mass2",
            object_type=ObjectType.MASS,
            label="m₂",
            position=Position(380, 350),
            dimensions=Dimensions(60, 60),
            style=Style(
                color="#2c3e50",
                fill_color="#ecf0f1",
                stroke_width=2.0
            ),
            properties={'type': 'mass'}
        )
        scene.objects.append(mass2)

        return scene

    def _generate_general_physics_diagram(
        self,
        plan: Dict,
        problem_text: str
    ) -> UniversalScene:
        """Generate general physics diagram"""

        scene = UniversalScene(
            scene_id=f"physics_{hash(problem_text) % 10000}",
            domain=DiagramDomain.PHYSICS,
            diagram_type=DiagramType.GENERIC,
            title="Physics Diagram",
            canvas_width=800,
            canvas_height=600
        )

        # Add objects from plan
        entities = plan.get('entities', [])

        for i, entity in enumerate(entities):
            x = 200 + (i * 150)
            y = 300

            obj = SceneObject(
                id=f"{entity.get('type', 'obj')}_{i}",
                object_type=ObjectType.MASS,
                label=entity.get('label', ''),
                position=Position(x, y),
                dimensions=Dimensions(80, 60),
                style=Style(
                    color="#2c3e50",
                    fill_color="#ecf0f1",
                    stroke_width=2.0
                ),
                properties=entity.get('properties', {})
            )
            scene.objects.append(obj)

        return scene

    def _extract_force_vectors(
        self,
        forces: List[Dict],
        problem_text: str
    ) -> List[PhysicsVector]:
        """Extract force vectors from entities and text"""
        vectors = []

        # Common forces and their typical angles
        standard_forces = {
            'weight': (0, 90, '#e74c3c'),  # downward
            'gravity': (0, 90, '#e74c3c'),
            'normal': (0, -90, '#3498db'),  # upward
            'tension': (0, -90, '#9b59b6'),
            'friction': (0, 0, '#e67e22'),  # horizontal
            'applied': (0, 0, '#27ae60'),
        }

        for force in forces:
            label = force.get('label', 'F')
            magnitude = force.get('properties', {}).get('magnitude', 1.0)

            # Determine angle and color
            angle = 0
            color = '#e74c3c'  # default red

            for force_name, (default_mag, default_angle, default_color) in standard_forces.items():
                if force_name in label.lower():
                    angle = default_angle
                    color = default_color
                    if default_mag > 0:
                        magnitude = default_mag
                    break

            vectors.append(PhysicsVector(
                magnitude=magnitude,
                angle=angle,
                label=label,
                color=color
            ))

        return vectors

    def _extract_angle(self, text: str) -> float:
        """Extract angle from text"""
        import re

        # Look for patterns like "30°", "30 degrees", "angle of 30"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:°|degrees?)',
            r'angle\s+of\s+(\d+(?:\.\d+)?)',
            r'inclined?\s+at\s+(\d+(?:\.\d+)?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return 30.0  # default angle


if __name__ == "__main__":
    # Test physics module
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("PHYSICS MODULE TEST")
    print("=" * 60)

    module = PhysicsDiagramModule()

    # Test free-body diagram
    test_plan = {
        'diagram_type': 'free_body',
        'entities': [
            {'type': 'block', 'label': 'm', 'properties': {'mass': '5 kg'}},
            {'type': 'force', 'label': 'N', 'properties': {}},
            {'type': 'force', 'label': 'mg', 'properties': {}},
            {'type': 'force', 'label': 'f', 'properties': {}}
        ],
        'relationships': [
            {'source': 'N', 'target': 'block', 'type': 'applies_to'},
            {'source': 'mg', 'target': 'block', 'type': 'applies_to'},
            {'source': 'f', 'target': 'block', 'type': 'applies_to'}
        ]
    }

    problem_text = "A 5 kg block rests on a horizontal surface. Draw a free-body diagram showing all forces."

    scene = module.generate_diagram(test_plan, problem_text)

    print("\n✓ Generated free-body diagram")
    print(f"  Objects: {len(scene.objects)}")
    print(f"  Relationships: {len(scene.relationships)}")
    print(f"  Domain: {scene.domain}")

    for obj in scene.objects:
        print(f"    - {obj.label} at ({obj.position.x}, {obj.position.y})")

    print("\n" + "=" * 60)
    print("✅ Physics Module ready")
    print("=" * 60)
