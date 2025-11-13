"""
OpticsInterpreter - Converts optics problem specifications into visual scenes

Handles:
- Converging and diverging lenses
- Concave and convex mirrors
- Object and image positions
- Principal axis
- Focal points (F and 2F)
- Ray diagrams with three principal rays
"""

from typing import Dict, List, Optional, Tuple
from core.scene.schema_v1 import Scene, SceneObject, Constraint, PrimitiveType, ConstraintType
from core.universal_ai_analyzer import PhysicsDomain


class OpticsInterpreter:
    """Interprets optics problem specifications into visual scenes"""

    def interpret(self, spec: Dict) -> Scene:
        """
        Main entry point - converts optics spec to Scene

        Args:
            spec: Dictionary with keys:
                - objects: List of physical objects (lens, mirror, object, etc.)
                - relationships: List of relationships between objects
                - environment: Environmental properties

        Returns:
            Scene with visual objects and constraints
        """
        objects = spec.get('objects', [])
        relationships = spec.get('relationships', [])

        print(f"   🔬 OpticsInterpreter: Processing {len(objects)} objects")

        # Identify problem type
        has_lens = any('lens' in str(obj.get('type', '')).lower() for obj in objects)
        has_mirror = any('mirror' in str(obj.get('type', '')).lower() for obj in objects)
        has_object = any('object' in str(obj.get('type', '')).lower() or obj.get('properties', {}).get('is_object') for obj in objects)

        if has_lens:
            scene_objects, constraints = self._create_lens_system(objects, relationships)
        elif has_mirror:
            scene_objects, constraints = self._create_mirror_system(objects, relationships)
        else:
            # Default: simple lens system
            scene_objects, constraints = self._create_simple_lens(objects)

        print(f"   ✅ Created {len(scene_objects)} scene objects, {len(constraints)} constraints")

        return Scene(
            metadata={"domain": PhysicsDomain.OPTICS.value},
            objects=scene_objects,
            constraints=constraints
        )

    def _create_simple_lens(self, objects: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create a simple converging lens with object and image"""

        scene_objects = []
        constraints = []

        # Extract properties
        focal_length = 20  # Default 20 cm
        object_distance = 30  # Default 30 cm (beyond F)

        for obj in objects:
            if 'lens' in str(obj.get('type', '')).lower():
                focal_length = obj.get('properties', {}).get('focal_length', focal_length)
            if 'object' in str(obj.get('type', '')).lower():
                object_distance = obj.get('properties', {}).get('distance', object_distance)

        # Calculate image distance using lens equation: 1/f = 1/u + 1/v
        # u is negative (object on left), v will be positive (real image on right)
        try:
            image_distance = (focal_length * object_distance) / (object_distance - focal_length)
        except ZeroDivisionError:
            image_distance = focal_length * 2  # Fallback

        # Create principal axis (horizontal line through center)
        scene_objects.append(SceneObject(
            id="principal_axis",
            type=PrimitiveType.LINE,
            properties={
                "orientation": "horizontal",
                "style": {"stroke": "#666666", "stroke_width": 1, "stroke_dasharray": "5,5"}
            }
        ))

        # Create lens (vertical line at center)
        scene_objects.append(SceneObject(
            id="lens",
            type=PrimitiveType.LENS,
            properties={
                "lens_type": "converging",
                "focal_length": focal_length,
                "height": 60,
                "style": {"stroke": "#0066cc", "stroke_width": 3}
            }
        ))

        # Create focal points (2 on each side)
        scene_objects.append(SceneObject(
            id="focal_point_left",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": -focal_length,
                "label": "F",
                "side": "left"
            }
        ))

        scene_objects.append(SceneObject(
            id="focal_point_right",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": focal_length,
                "label": "F",
                "side": "right"
            }
        ))

        # Create 2F points
        scene_objects.append(SceneObject(
            id="2f_left",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": -2 * focal_length,
                "label": "2F",
                "side": "left"
            }
        ))

        scene_objects.append(SceneObject(
            id="2f_right",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": 2 * focal_length,
                "label": "2F",
                "side": "right"
            }
        ))

        # Create object (arrow on left)
        object_height = 20
        scene_objects.append(SceneObject(
            id="object",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "distance": -object_distance,
                "height": object_height,
                "label": "O",
                "is_object": True,
                "style": {"stroke": "#cc0000", "stroke_width": 2, "marker_end": "arrowhead"}
            }
        ))

        # Create image (arrow on right, inverted if real)
        image_height = -(object_height * image_distance / object_distance)  # Magnification formula
        scene_objects.append(SceneObject(
            id="image",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "downward" if image_height < 0 else "upward",
                "distance": image_distance,
                "height": abs(image_height),
                "label": "I",
                "is_image": True,
                "inverted": image_height < 0,
                "style": {"stroke": "#00cc00", "stroke_width": 2, "stroke_dasharray": "3,3"}
            }
        ))

        # Create 3 principal rays
        # Ray 1: Parallel to axis, passes through focal point
        scene_objects.append(SceneObject(
            id="ray1",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "parallel_to_focal",
                "color": "#ff6600",
                "label": "Ray 1"
            }
        ))

        # Ray 2: Through optical center, continues straight
        scene_objects.append(SceneObject(
            id="ray2",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "through_center",
                "color": "#6600ff",
                "label": "Ray 2"
            }
        ))

        # Ray 3: Through focal point, emerges parallel
        scene_objects.append(SceneObject(
            id="ray3",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "focal_to_parallel",
                "color": "#00cc99",
                "label": "Ray 3"
            }
        ))

        # Add constraints
        constraints.append(Constraint(
            type=ConstraintType.COLLINEAR,
            objects=["principal_axis", "lens"]
        ))

        constraints.append(Constraint(
            type=ConstraintType.PERPENDICULAR,
            objects=["lens", "principal_axis"]
        ))

        return scene_objects, constraints

    def _create_lens_system(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create lens system based on detected objects"""

        # Check for lens type
        lens_type = "converging"
        for obj in objects:
            if 'lens' in str(obj.get('type', '')).lower():
                lens_props = obj.get('properties', {})
                focal_length = lens_props.get('focal_length', 20)
                if focal_length < 0 or 'diverging' in str(lens_props.get('lens_type', '')).lower():
                    lens_type = "diverging"
                break

        if lens_type == "diverging":
            return self._create_diverging_lens(objects, relationships)
        else:
            return self._create_simple_lens(objects)

    def _create_diverging_lens(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create diverging lens system"""

        scene_objects = []
        constraints = []

        focal_length = -15  # Negative for diverging
        object_distance = 25

        # Extract properties
        for obj in objects:
            if 'lens' in str(obj.get('type', '')).lower():
                focal_length = -abs(obj.get('properties', {}).get('focal_length', 15))
            if 'object' in str(obj.get('type', '')).lower():
                object_distance = obj.get('properties', {}).get('distance', object_distance)

        # Principal axis
        scene_objects.append(SceneObject(
            id="principal_axis",
            type=PrimitiveType.LINE,
            properties={
                "orientation": "horizontal",
                "style": {"stroke": "#666666", "stroke_width": 1, "stroke_dasharray": "5,5"}
            }
        ))

        # Diverging lens
        scene_objects.append(SceneObject(
            id="lens",
            type=PrimitiveType.LENS,
            properties={
                "lens_type": "diverging",
                "focal_length": focal_length,
                "height": 60,
                "style": {"stroke": "#cc0066", "stroke_width": 3}
            }
        ))

        # Focal points (negative side for diverging lens)
        scene_objects.append(SceneObject(
            id="focal_point_left",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": focal_length,
                "label": "F",
                "side": "left"
            }
        ))

        scene_objects.append(SceneObject(
            id="focal_point_right",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": -focal_length,
                "label": "F'",
                "side": "right",
                "virtual": True
            }
        ))

        # Object
        scene_objects.append(SceneObject(
            id="object",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "distance": -object_distance,
                "height": 20,
                "label": "O",
                "is_object": True,
                "style": {"stroke": "#cc0000", "stroke_width": 2}
            }
        ))

        # Virtual image (on same side as object, upright, smaller)
        image_distance = (focal_length * object_distance) / (object_distance + abs(focal_length))
        magnification = abs(image_distance / object_distance)

        scene_objects.append(SceneObject(
            id="image",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "distance": image_distance,
                "height": 20 * magnification,
                "label": "I",
                "is_image": True,
                "virtual": True,
                "style": {"stroke": "#00cc00", "stroke_width": 2, "stroke_dasharray": "5,5"}
            }
        ))

        # Rays for diverging lens
        scene_objects.append(SceneObject(
            id="ray1",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "parallel_diverges",
                "color": "#ff6600"
            }
        ))

        scene_objects.append(SceneObject(
            id="ray2",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "through_center",
                "color": "#6600ff"
            }
        ))

        return scene_objects, constraints

    def _create_mirror_system(self, objects: List[Dict], relationships: List[Dict]) -> Tuple[List[SceneObject], List[Constraint]]:
        """Create concave or convex mirror system"""

        scene_objects = []
        constraints = []

        # Determine mirror type
        mirror_type = "concave"
        focal_length = 15
        object_distance = 25

        for obj in objects:
            if 'mirror' in str(obj.get('type', '')).lower():
                mirror_props = obj.get('properties', {})
                focal_length = mirror_props.get('focal_length', focal_length)
                if 'convex' in str(mirror_props.get('mirror_type', '')).lower():
                    mirror_type = "convex"
                    focal_length = -abs(focal_length)
            if 'object' in str(obj.get('type', '')).lower():
                object_distance = obj.get('properties', {}).get('distance', object_distance)

        # Principal axis
        scene_objects.append(SceneObject(
            id="principal_axis",
            type=PrimitiveType.LINE,
            properties={
                "orientation": "horizontal",
                "style": {"stroke": "#666666", "stroke_width": 1, "stroke_dasharray": "5,5"}
            }
        ))

        # Mirror
        scene_objects.append(SceneObject(
            id="mirror",
            type=PrimitiveType.LENS,
            properties={
                "mirror_type": mirror_type,
                "focal_length": focal_length,
                "height": 60,
                "style": {"stroke": "#0099cc", "stroke_width": 4}
            }
        ))

        # Focal point and center of curvature
        scene_objects.append(SceneObject(
            id="focal_point",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": -abs(focal_length),
                "label": "F",
                "side": "left"
            }
        ))

        scene_objects.append(SceneObject(
            id="center_curvature",
            type=PrimitiveType.CIRCLE,
            properties={
                "distance": -2 * abs(focal_length),
                "label": "C",
                "side": "left"
            }
        ))

        # Object
        scene_objects.append(SceneObject(
            id="object",
            type=PrimitiveType.ARROW,
            properties={
                "direction": "upward",
                "distance": -object_distance,
                "height": 20,
                "label": "O",
                "is_object": True,
                "style": {"stroke": "#cc0000", "stroke_width": 2}
            }
        ))

        # Image (real or virtual depending on object position)
        if object_distance > abs(focal_length):
            # Real image
            image_distance = -(focal_length * object_distance) / (object_distance + focal_length)
            magnification = -image_distance / object_distance

            scene_objects.append(SceneObject(
                id="image",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "downward",
                    "distance": image_distance,
                    "height": 20 * abs(magnification),
                    "label": "I",
                    "is_image": True,
                    "inverted": True,
                    "style": {"stroke": "#00cc00", "stroke_width": 2}
                }
            ))

        # Reflection rays
        scene_objects.append(SceneObject(
            id="ray1",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "parallel_to_focal_reflection",
                "color": "#ff6600"
            }
        ))

        scene_objects.append(SceneObject(
            id="ray2",
            type=PrimitiveType.POLYLINE,
            properties={
                "ray_type": "through_focal_parallel_reflection",
                "color": "#6600ff"
            }
        ))

        return scene_objects, constraints
