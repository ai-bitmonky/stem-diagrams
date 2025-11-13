"""
MechanicsInterpreter - Converts mechanics problem specifications into visual scenes

Handles:
- Blocks and masses on horizontal surfaces
- Inclined planes
- Pulley systems (fixed and movable)
- Springs (compression and extension)
- Ropes and tension
- Force diagrams (gravity, normal, friction, tension, applied)
- Multi-body systems
"""

from typing import Dict, List, Optional, Tuple
from core.scene.schema_v1 import Scene, SceneObject, Constraint, PrimitiveType, ConstraintType
from core.universal_ai_analyzer import PhysicsDomain
import math


class MechanicsInterpreter:
    """Interprets mechanics problem specifications into visual scenes"""

    def interpret(self, spec: Dict) -> Scene:
        """
        Main entry point - converts mechanics spec to Scene

        Args:
            spec: Dictionary with keys:
                - objects: List of physical objects (block, pulley, spring, etc.)
                - relationships: List of relationships between objects
                - environment: Environmental properties (gravity, friction, etc.)

        Returns:
            Scene with visual objects and constraints
        """
        objects = spec.get('objects', [])
        relationships = spec.get('relationships', [])
        environment = spec.get('environment', {})

        print(f"   ⚙️  MechanicsInterpreter: Processing {len(objects)} objects")

        # Identify problem type
        has_pulley = any('pulley' in str(obj.get('type', '')).lower() for obj in objects)
        has_incline = any('incline' in str(obj.get('type', '')).lower() or 'ramp' in str(obj.get('type', '')).lower() for obj in objects)
        has_spring = any('spring' in str(obj.get('type', '')).lower() for obj in objects)

        # Count blocks/masses
        block_count = sum(1 for obj in objects if any(keyword in str(obj.get('type', '')).lower() for keyword in ['block', 'mass', 'box', 'object']))

        if has_pulley and block_count >= 2:
            scene_objects, constraints = self._create_pulley_system(objects, relationships)
        elif has_incline:
            scene_objects, constraints = self._create_incline_system(objects, relationships)
        elif has_spring:
            scene_objects, constraints = self._create_spring_system(objects, relationships)
        elif block_count >= 2:
            scene_objects, constraints = self._create_multiple_blocks(objects, relationships)
        else:
            scene_objects, constraints = self._create_simple_block(objects, environment)

        print(f"   ✅ Created {len(scene_objects)} scene objects, {len(constraints)} constraints")

        return Scene(
            metadata={"domain": PhysicsDomain.MECHANICS.value},
            objects=scene_objects,
            constraints=constraints
        )

    def _create_simple_block(self, objects: List[Dict], environment: Dict) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create a single block on a horizontal surface with forces"""

        scene_objects = []
        constraints = []

        # Extract properties
        mass = 5.0  # Default 5 kg
        friction_coefficient = 0.0
        applied_force = 0.0
        has_friction = False

        for obj in objects:
            if any(keyword in str(obj.get('type', '')).lower() for keyword in ['block', 'mass', 'box']):
                props = obj.get('properties', {})
                mass = props.get('mass', mass)
                friction_coefficient = props.get('friction', 0.0)
                applied_force = props.get('force', 0.0)
                if friction_coefficient > 0:
                    has_friction = True

        # Create ground/surface
        scene_objects.append(SceneObject(
            id="ground",
            type=PrimitiveType.LINE,
            properties={
                "orientation": "horizontal",
                "length": 200,
                "y_position": 0,
                "style": {"stroke": "#333333", "stroke_width": 3}
            }
        ))

        # Create block
        block_width = 50
        block_height = 40
        scene_objects.append(SceneObject(
            id="block1",
            type=PrimitiveType.MASS,
            properties={
                "mass": mass,
                "width": block_width,
                "height": block_height,
                "label": f"{mass} kg",
                "style": {"fill": "#8899cc", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Add forces
        g = 9.8  # Gravity constant
        weight = mass * g

        # Weight (downward)
        scene_objects.append(SceneObject(
            id="force_weight",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "downward",
                "magnitude": weight,
                "label": f"mg = {weight:.1f}N",
                "parent": "block1",
                "color": "#cc0000",
                "force_type": "weight"
            }
        ))

        # Normal force (upward)
        scene_objects.append(SceneObject(
            id="force_normal",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "magnitude": weight,
                "label": f"N = {weight:.1f}N",
                "parent": "block1",
                "color": "#0000cc",
                "force_type": "normal"
            }
        ))

        # Applied force (if present)
        if applied_force > 0:
            scene_objects.append(SceneObject(
                id="force_applied",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "rightward",
                    "magnitude": applied_force,
                    "label": f"F = {applied_force:.1f}N",
                    "parent": "block1",
                    "color": "#00cc00",
                    "force_type": "applied"
                }
            ))

        # Friction force (if present)
        if has_friction and applied_force > 0:
            friction_force = min(friction_coefficient * weight, applied_force)
            scene_objects.append(SceneObject(
                id="force_friction",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "leftward",
                    "magnitude": friction_force,
                    "label": f"f = {friction_force:.1f}N",
                    "parent": "block1",
                    "color": "#cc6600",
                    "force_type": "friction"
                }
            ))

        # Constraint: block on ground
        constraints.append(Constraint(
            type=ConstraintType.CONNECTED,
            objects=["block1", "ground"]
        ))

        return scene_objects, constraints

    def _create_incline_system(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create a block on an inclined plane"""

        scene_objects = []
        constraints = []

        # Extract properties
        mass = 5.0
        angle = 30.0  # Default 30 degrees
        friction_coefficient = 0.0

        for obj in objects:
            obj_type = str(obj.get('type', '')).lower()
            props = obj.get('properties', {})

            if 'block' in obj_type or 'mass' in obj_type:
                mass = props.get('mass', mass)
                friction_coefficient = props.get('friction', friction_coefficient)
            elif 'incline' in obj_type or 'ramp' in obj_type:
                angle = props.get('angle', angle)

        # Create inclined plane
        incline_length = 150
        incline_height = incline_length * math.sin(math.radians(angle))
        incline_base = incline_length * math.cos(math.radians(angle))

        scene_objects.append(SceneObject(
            id="incline",
            type=PrimitiveType.POLYLINE,
            properties={
                "points": [(0, 0), (incline_base, 0), (0, incline_height), (0, 0)],
                "angle": angle,
                "length": incline_length,
                "style": {"fill": "#cccccc", "stroke": "#333333", "stroke_width": 2}
            }
        ))

        # Create block on incline
        block_size = 40
        scene_objects.append(SceneObject(
            id="block1",
            type=PrimitiveType.MASS,
            properties={
                "mass": mass,
                "width": block_size,
                "height": block_size,
                "angle": angle,
                "label": f"{mass} kg",
                "on_incline": True,
                "style": {"fill": "#8899cc", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Forces
        g = 9.8
        weight = mass * g
        weight_parallel = weight * math.sin(math.radians(angle))
        weight_perpendicular = weight * math.cos(math.radians(angle))

        # Weight (vertically downward)
        scene_objects.append(SceneObject(
            id="force_weight",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "downward",
                "magnitude": weight,
                "label": f"mg = {weight:.1f}N",
                "parent": "block1",
                "color": "#cc0000"
            }
        ))

        # Component parallel to incline
        scene_objects.append(SceneObject(
            id="force_parallel",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "along_incline_down",
                "angle": angle,
                "magnitude": weight_parallel,
                "label": f"mg sin θ = {weight_parallel:.1f}N",
                "parent": "block1",
                "color": "#ff6600"
            }
        ))

        # Component perpendicular to incline
        scene_objects.append(SceneObject(
            id="force_perpendicular",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "perpendicular_to_incline",
                "angle": 90 - angle,
                "magnitude": weight_perpendicular,
                "label": f"mg cos θ = {weight_perpendicular:.1f}N",
                "parent": "block1",
                "color": "#ff9900"
            }
        ))

        # Normal force (perpendicular to incline, opposite direction)
        scene_objects.append(SceneObject(
            id="force_normal",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "away_from_incline",
                "angle": 90 + angle,
                "magnitude": weight_perpendicular,
                "label": f"N = {weight_perpendicular:.1f}N",
                "parent": "block1",
                "color": "#0000cc"
            }
        ))

        # Friction (if present)
        if friction_coefficient > 0:
            friction_force = friction_coefficient * weight_perpendicular
            scene_objects.append(SceneObject(
                id="force_friction",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "along_incline_up",
                    "angle": 180 - angle,
                    "magnitude": friction_force,
                    "label": f"f = {friction_force:.1f}N",
                    "parent": "block1",
                    "color": "#cc6600"
                }
            ))

        # Angle label
        scene_objects.append(SceneObject(
            id="angle_label",
            type=PrimitiveType.CIRCLE,
            properties={
                "label": f"θ = {angle}°",
                "position": "angle_indicator"
            }
        ))

        return scene_objects, constraints

    def _create_pulley_system(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create a pulley system with two blocks"""

        scene_objects = []
        constraints = []

        # Extract masses
        masses = []
        for obj in objects:
            if any(keyword in str(obj.get('type', '')).lower() for keyword in ['block', 'mass', 'box']):
                mass = obj.get('properties', {}).get('mass', 5.0)
                masses.append(mass)

        # Default to two masses if not enough found
        if len(masses) < 2:
            masses = [5.0, 3.0]

        # Create pulley
        scene_objects.append(SceneObject(
            id="pulley",
            type=PrimitiveType.PULLEY,
            properties={
                "radius": 20,
                "position": "top_center",
                "style": {"fill": "#666666", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Create rope
        scene_objects.append(SceneObject(
            id="rope",
            type=PrimitiveType.LINE,
            properties={
                "type": "rope",
                "connects": ["block1", "pulley", "block2"],
                "style": {"stroke": "#8B4513", "stroke_width": 3}
            }
        ))

        # Block 1 (left side, hanging)
        scene_objects.append(SceneObject(
            id="block1",
            type=PrimitiveType.MASS,
            properties={
                "mass": masses[0],
                "width": 40,
                "height": 40,
                "position": "left_hanging",
                "label": f"m₁ = {masses[0]} kg",
                "style": {"fill": "#8899cc", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Block 2 (right side, hanging)
        scene_objects.append(SceneObject(
            id="block2",
            type=PrimitiveType.MASS,
            properties={
                "mass": masses[1],
                "width": 40,
                "height": 40,
                "position": "right_hanging",
                "label": f"m₂ = {masses[1]} kg",
                "style": {"fill": "#cc9988", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Forces on block 1
        g = 9.8
        scene_objects.append(SceneObject(
            id="force_weight1",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "downward",
                "magnitude": masses[0] * g,
                "label": f"m₁g = {masses[0] * g:.1f}N",
                "parent": "block1",
                "color": "#cc0000"
            }
        ))

        scene_objects.append(SceneObject(
            id="force_tension1",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "magnitude": 0,  # To be calculated
                "label": "T",
                "parent": "block1",
                "color": "#0066cc"
            }
        ))

        # Forces on block 2
        scene_objects.append(SceneObject(
            id="force_weight2",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "downward",
                "magnitude": masses[1] * g,
                "label": f"m₂g = {masses[1] * g:.1f}N",
                "parent": "block2",
                "color": "#cc0000"
            }
        ))

        scene_objects.append(SceneObject(
            id="force_tension2",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "magnitude": 0,  # To be calculated
                "label": "T",
                "parent": "block2",
                "color": "#0066cc"
            }
        ))

        # Constraints
        constraints.append(Constraint(
            type=ConstraintType.CONNECTED,
            objects=["block1", "rope", "pulley"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.CONNECTED,
            objects=["block2", "rope", "pulley"]
        ))

        return scene_objects, constraints

    def _create_spring_system(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create a mass-spring system"""

        scene_objects = []
        constraints = []

        # Extract properties
        mass = 2.0
        spring_constant = 100.0  # N/m
        displacement = 0.1  # m

        for obj in objects:
            obj_type = str(obj.get('type', '')).lower()
            props = obj.get('properties', {})

            if 'block' in obj_type or 'mass' in obj_type:
                mass = props.get('mass', mass)
            elif 'spring' in obj_type:
                spring_constant = props.get('k', spring_constant)
                displacement = props.get('displacement', displacement)

        # Create wall (anchor point)
        scene_objects.append(SceneObject(
            id="wall",
            type=PrimitiveType.RECTANGLE,
            properties={
                "width": 10,
                "height": 80,
                "label": "Wall",
                "fixed": True,
                "style": {"fill": "#666666", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Create spring
        scene_objects.append(SceneObject(
            id="spring",
            type=PrimitiveType.SPRING,
            properties={
                "spring_constant": spring_constant,
                "displacement": displacement,
                "natural_length": 60,
                "coils": 8,
                "label": f"k = {spring_constant} N/m",
                "style": {"stroke": "#0066cc", "stroke_width": 2}
            }
        ))

        # Create mass
        scene_objects.append(SceneObject(
            id="block1",
            type=PrimitiveType.MASS,
            properties={
                "mass": mass,
                "width": 40,
                "height": 40,
                "label": f"{mass} kg",
                "style": {"fill": "#8899cc", "stroke": "#000000", "stroke_width": 2}
            }
        ))

        # Spring force (restoring)
        spring_force = spring_constant * displacement
        scene_objects.append(SceneObject(
            id="force_spring",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "leftward" if displacement > 0 else "rightward",
                "magnitude": spring_force,
                "label": f"F = kx = {spring_force:.1f}N",
                "parent": "block1",
                "color": "#00cc00"
            }
        ))

        # Constraints
        constraints.append(Constraint(
            type=ConstraintType.CONNECTED,
            objects=["wall", "spring"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.CONNECTED,
            objects=["spring", "block1"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.ALIGNED_H,
            objects=["wall", "spring", "block1"]
        ))

        return scene_objects, constraints

    def _create_multiple_blocks(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create multiple blocks in contact on a surface"""

        scene_objects = []
        constraints = []

        # Extract blocks
        blocks = []
        for obj in objects:
            if any(keyword in str(obj.get('type', '')).lower() for keyword in ['block', 'mass', 'box']):
                mass = obj.get('properties', {}).get('mass', 5.0)
                blocks.append(mass)

        if len(blocks) < 2:
            blocks = [5.0, 3.0]  # Default

        # Create ground
        scene_objects.append(SceneObject(
            id="ground",
            type=PrimitiveType.LINE,
            properties={
                "orientation": "horizontal",
                "length": 250,
                "style": {"stroke": "#333333", "stroke_width": 3}
            }
        ))

        # Create blocks in contact
        for i, mass in enumerate(blocks):
            block_id = f"block{i+1}"
            scene_objects.append(SceneObject(
                id=block_id,
                type=PrimitiveType.MASS,
                properties={
                    "mass": mass,
                    "width": 50,
                    "height": 40,
                    "label": f"m{i+1} = {mass} kg",
                    "style": {"fill": f"#{'88' if i % 2 == 0 else 'cc'}99cc", "stroke": "#000000", "stroke_width": 2}
                }
            ))

            # Weight force
            g = 9.8
            scene_objects.append(SceneObject(
                id=f"force_weight{i+1}",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "downward",
                    "magnitude": mass * g,
                    "label": f"m{i+1}g",
                    "parent": block_id,
                    "color": "#cc0000"
                }
            ))

        # Applied force on first block
        total_mass = sum(blocks)
        applied_force = total_mass * 10  # Arbitrary
        scene_objects.append(SceneObject(
            id="force_applied",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "rightward",
                "magnitude": applied_force,
                "label": f"F = {applied_force:.1f}N",
                "parent": "block1",
                "color": "#00cc00"
            }
        ))

        # Contact forces between blocks
        if len(blocks) >= 2:
            scene_objects.append(SceneObject(
                id="force_contact",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "rightward",
                    "magnitude": 0,  # To be calculated
                    "label": "N₁₂",
                    "parent": "block2",
                    "color": "#0066cc",
                    "contact_force": True
                }
            ))

        # Constraint: blocks in contact
        for i in range(len(blocks) - 1):
            constraints.append(Constraint(
                type=ConstraintType.CONNECTED,
                objects=[f"block{i+1}", f"block{i+2}"]
            ))

        # Constraint: all blocks aligned horizontally
        block_ids = [f"block{i+1}" for i in range(len(blocks))]
        constraints.append(Constraint(
            type=ConstraintType.ALIGNED_H,
            objects=block_ids
        ))

        return scene_objects, constraints
