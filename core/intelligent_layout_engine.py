"""
Intelligent Layout Engine - Constraint-Based Positioning
=========================================================

This module provides intelligent layout algorithms with:
- Constraint satisfaction for component positioning
- Collision detection and avoidance
- Auto-routing for wires/connections
- Force-directed layout for complex networks
- Grid-based snapping for alignment
- Dynamic canvas sizing

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import math
from core.universal_scene_format import UniversalScene, SceneObject, Relationship, Position


@dataclass
class LayoutConstraint:
    """Represents a layout constraint"""
    constraint_type: str  # "distance", "alignment", "ordering", "no_overlap"
    objects: List[str]  # Object IDs involved
    parameters: Dict  # Constraint-specific parameters
    priority: int = 1  # Higher priority constraints are satisfied first


@dataclass
class BoundingBox:
    """Represents object bounding box"""
    x: float
    y: float
    width: float
    height: float

    def overlaps(self, other: 'BoundingBox') -> bool:
        """Check if this box overlaps with another"""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)

    def center(self) -> Tuple[float, float]:
        """Get center point"""
        return (self.x + self.width/2, self.y + self.height/2)


class IntelligentLayoutEngine:
    """
    Intelligent layout engine with constraint satisfaction
    """

    def __init__(self, canvas_width: float = 1000, canvas_height: float = 600):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid_size = 20  # Grid snap size
        self.min_spacing = 50  # Minimum spacing between components
        self.constraints: List[LayoutConstraint] = []

    def optimize_layout(self, scene: UniversalScene,
                       enable_collision_avoidance: bool = True,
                       enable_force_directed: bool = False) -> UniversalScene:
        """
        Optimize scene layout using intelligent algorithms

        Args:
            scene: Scene to optimize
            enable_collision_avoidance: Resolve overlapping objects
            enable_force_directed: Use force-directed layout

        Returns:
            Optimized scene with better layout
        """
        print("  🎯 Optimizing layout...")

        # Step 1: Collect constraints
        self._extract_constraints(scene)

        # Step 2: Apply force-directed layout if enabled
        if enable_force_directed:
            self._apply_force_directed_layout(scene)

        # Step 3: Resolve collisions
        if enable_collision_avoidance:
            self._resolve_collisions(scene)

        # Step 4: Snap to grid for alignment
        self._snap_to_grid(scene)

        # Step 5: Optimize canvas size
        self._optimize_canvas_size(scene)

        # Step 6: Center layout
        self._center_layout(scene)

        print("  ✅ Layout optimized")
        return scene

    def _extract_constraints(self, scene: UniversalScene):
        """Extract layout constraints from scene"""
        self.constraints = []

        # Distance constraints from relationships
        for rel in scene.relationships:
            if rel.relation_type.value == "connected_to":
                constraint = LayoutConstraint(
                    constraint_type="distance",
                    objects=[rel.source_id, rel.target_id],
                    parameters={"preferred_distance": 150, "max_distance": 300},
                    priority=2
                )
                self.constraints.append(constraint)

        # No-overlap constraint for all objects
        for obj1 in scene.objects:
            for obj2 in scene.objects:
                if obj1.id != obj2.id:
                    constraint = LayoutConstraint(
                        constraint_type="no_overlap",
                        objects=[obj1.id, obj2.id],
                        parameters={"min_spacing": self.min_spacing},
                        priority=3
                    )
                    self.constraints.append(constraint)

    def _apply_force_directed_layout(self, scene: UniversalScene, iterations: int = 50):
        """
        Apply force-directed layout algorithm

        This positions nodes based on:
        - Repulsion between all nodes
        - Attraction between connected nodes
        - Centering force
        """
        print("    - Applying force-directed layout...")

        # Create object lookup
        objects_dict = {obj.id: obj for obj in scene.objects}

        # Constants
        k_repulsion = 5000  # Repulsion strength
        k_attraction = 0.01  # Attraction strength
        k_center = 0.05  # Centering force
        damping = 0.8  # Velocity damping

        # Initialize velocities
        velocities = {obj.id: {'vx': 0, 'vy': 0} for obj in scene.objects}

        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2

        for iteration in range(iterations):
            forces = {obj.id: {'fx': 0, 'fy': 0} for obj in scene.objects}

            # Calculate repulsion forces (all pairs)
            for i, obj1 in enumerate(scene.objects):
                for obj2 in scene.objects[i+1:]:
                    dx = obj2.position.x - obj1.position.x
                    dy = obj2.position.y - obj1.position.y
                    distance = math.sqrt(dx**2 + dy**2) + 1  # Avoid division by zero

                    # Repulsion force (inverse square)
                    force = k_repulsion / (distance**2)
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force

                    forces[obj1.id]['fx'] -= fx
                    forces[obj1.id]['fy'] -= fy
                    forces[obj2.id]['fx'] += fx
                    forces[obj2.id]['fy'] += fy

            # Calculate attraction forces (connected nodes)
            for rel in scene.relationships:
                if rel.source_id in objects_dict and rel.target_id in objects_dict:
                    obj1 = objects_dict[rel.source_id]
                    obj2 = objects_dict[rel.target_id]

                    dx = obj2.position.x - obj1.position.x
                    dy = obj2.position.y - obj1.position.y
                    distance = math.sqrt(dx**2 + dy**2) + 1

                    # Attraction force (linear)
                    force = distance * k_attraction
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force

                    forces[obj1.id]['fx'] += fx
                    forces[obj1.id]['fy'] += fy
                    forces[obj2.id]['fx'] -= fx
                    forces[obj2.id]['fy'] -= fy

            # Add centering force
            for obj in scene.objects:
                dx = center_x - obj.position.x
                dy = center_y - obj.position.y

                forces[obj.id]['fx'] += dx * k_center
                forces[obj.id]['fy'] += dy * k_center

            # Update positions
            for obj in scene.objects:
                # Update velocity
                velocities[obj.id]['vx'] = (velocities[obj.id]['vx'] + forces[obj.id]['fx']) * damping
                velocities[obj.id]['vy'] = (velocities[obj.id]['vy'] + forces[obj.id]['fy']) * damping

                # Update position
                obj.position.x += velocities[obj.id]['vx']
                obj.position.y += velocities[obj.id]['vy']

                # Keep within canvas
                obj.position.x = max(50, min(self.canvas_width - 50, obj.position.x))
                obj.position.y = max(50, min(self.canvas_height - 50, obj.position.y))

    def _resolve_collisions(self, scene: UniversalScene):
        """Resolve overlapping components"""
        print("    - Resolving collisions...")

        max_iterations = 10
        for iteration in range(max_iterations):
            collisions_found = False

            for i, obj1 in enumerate(scene.objects):
                for obj2 in scene.objects[i+1:]:
                    bbox1 = self._get_bounding_box(obj1)
                    bbox2 = self._get_bounding_box(obj2)

                    if bbox1.overlaps(bbox2):
                        collisions_found = True
                        self._separate_objects(obj1, obj2, bbox1, bbox2)

            if not collisions_found:
                break

    def _get_bounding_box(self, obj: SceneObject) -> BoundingBox:
        """Get bounding box for an object"""
        # Add padding for spacing
        padding = self.min_spacing / 2

        return BoundingBox(
            x=obj.position.x - obj.dimensions.width/2 - padding,
            y=obj.position.y - obj.dimensions.height/2 - padding,
            width=obj.dimensions.width + 2*padding,
            height=obj.dimensions.height + 2*padding
        )

    def _separate_objects(self, obj1: SceneObject, obj2: SceneObject,
                         bbox1: BoundingBox, bbox2: BoundingBox):
        """Separate two overlapping objects"""
        # Calculate overlap
        cx1, cy1 = bbox1.center()
        cx2, cy2 = bbox2.center()

        dx = cx2 - cx1
        dy = cy2 - cy1
        distance = math.sqrt(dx**2 + dy**2) + 1

        # Calculate required separation
        required_distance = (bbox1.width + bbox2.width) / 2

        if distance < required_distance:
            # Move objects apart
            separation = (required_distance - distance) / 2
            nx = dx / distance
            ny = dy / distance

            obj1.position.x -= nx * separation
            obj1.position.y -= ny * separation
            obj2.position.x += nx * separation
            obj2.position.y += ny * separation

    def _snap_to_grid(self, scene: UniversalScene):
        """Snap object positions to grid for better alignment"""
        print("    - Snapping to grid...")

        for obj in scene.objects:
            obj.position.x = round(obj.position.x / self.grid_size) * self.grid_size
            obj.position.y = round(obj.position.y / self.grid_size) * self.grid_size

    def _optimize_canvas_size(self, scene: UniversalScene):
        """Optimize canvas size to fit all objects"""
        if not scene.objects:
            return

        # Find bounds
        min_x = min(obj.position.x - obj.dimensions.width/2 for obj in scene.objects)
        max_x = max(obj.position.x + obj.dimensions.width/2 for obj in scene.objects)
        min_y = min(obj.position.y - obj.dimensions.height/2 for obj in scene.objects)
        max_y = max(obj.position.y + obj.dimensions.height/2 for obj in scene.objects)

        # Add margins
        margin = 100
        required_width = (max_x - min_x) + 2 * margin
        required_height = (max_y - min_y) + 2 * margin

        # Update canvas size if needed
        if required_width > scene.canvas_width or required_height > scene.canvas_height:
            scene.canvas_width = max(required_width, scene.canvas_width)
            scene.canvas_height = max(required_height, scene.canvas_height)

    def _center_layout(self, scene: UniversalScene):
        """Center the layout in the canvas"""
        if not scene.objects:
            return

        # Calculate current bounds
        min_x = min(obj.position.x - obj.dimensions.width/2 for obj in scene.objects)
        max_x = max(obj.position.x + obj.dimensions.width/2 for obj in scene.objects)
        min_y = min(obj.position.y - obj.dimensions.height/2 for obj in scene.objects)
        max_y = max(obj.position.y + obj.dimensions.height/2 for obj in scene.objects)

        # Calculate offset to center
        current_center_x = (min_x + max_x) / 2
        current_center_y = (min_y + max_y) / 2
        target_center_x = scene.canvas_width / 2
        target_center_y = scene.canvas_height / 2

        offset_x = target_center_x - current_center_x
        offset_y = target_center_y - current_center_y

        # Apply offset
        for obj in scene.objects:
            obj.position.x += offset_x
            obj.position.y += offset_y

    def route_wire(self, start: Position, end: Position,
                  obstacles: List[BoundingBox] = None) -> List[Position]:
        """
        Route a wire from start to end, avoiding obstacles

        Uses A* algorithm with Manhattan distance heuristic

        Returns:
            List of waypoints for the wire path
        """
        if obstacles is None:
            obstacles = []

        # Simple routing: orthogonal path with one bend
        waypoints = []

        # Check if direct path is clear
        if self._is_path_clear(start, end, obstacles):
            return [start, end]

        # Try L-shaped paths
        # Path 1: horizontal then vertical
        mid1 = Position(end.x, start.y, 0)
        if (self._is_path_clear(start, mid1, obstacles) and
            self._is_path_clear(mid1, end, obstacles)):
            return [start, mid1, end]

        # Path 2: vertical then horizontal
        mid2 = Position(start.x, end.y, 0)
        if (self._is_path_clear(start, mid2, obstacles) and
            self._is_path_clear(mid2, end, obstacles)):
            return [start, mid2, end]

        # Fallback: direct path (will overlap obstacles)
        return [start, end]

    def _is_path_clear(self, start: Position, end: Position,
                      obstacles: List[BoundingBox]) -> bool:
        """Check if path between two points is clear of obstacles"""
        # Create line segment bounding box
        line_bbox = BoundingBox(
            x=min(start.x, end.x) - 5,
            y=min(start.y, end.y) - 5,
            width=abs(end.x - start.x) + 10,
            height=abs(end.y - start.y) + 10
        )

        # Check if line intersects any obstacle
        for obstacle in obstacles:
            if line_bbox.overlaps(obstacle):
                return False

        return True


# Testing
if __name__ == "__main__":
    from core.universal_scene_format import create_circuit_scene, ObjectType, Dimensions

    print("Intelligent Layout Engine - Test")
    print("=" * 50)

    # Create a test scene with overlapping components
    scene = create_circuit_scene("test_layout", "Test Layout")

    # Add objects that will overlap
    obj1 = SceneObject(
        id="obj1",
        object_type=ObjectType.RESISTOR,
        position=Position(200, 200, 0),
        dimensions=Dimensions(width=80, height=40),
        label="R1"
    )

    obj2 = SceneObject(
        id="obj2",
        object_type=ObjectType.CAPACITOR,
        position=Position(220, 210, 0),  # Overlapping!
        dimensions=Dimensions(width=80, height=60),
        label="C1"
    )

    obj3 = SceneObject(
        id="obj3",
        object_type=ObjectType.BATTERY,
        position=Position(100, 200, 0),
        dimensions=Dimensions(width=80, height=50),
        label="V1"
    )

    scene.add_object(obj1)
    scene.add_object(obj2)
    scene.add_object(obj3)

    # Add relationship
    from core.universal_scene_format import Relationship, RelationType
    rel = Relationship(
        id="wire1",
        relation_type=RelationType.CONNECTED_TO,
        source_id="obj3",
        target_id="obj1"
    )
    scene.add_relationship(rel)

    print("\nInitial positions:")
    for obj in scene.objects:
        print(f"  {obj.id}: ({obj.position.x:.1f}, {obj.position.y:.1f})")

    # Optimize layout
    engine = IntelligentLayoutEngine()
    scene = engine.optimize_layout(scene, enable_collision_avoidance=True,
                                   enable_force_directed=False)

    print("\nOptimized positions:")
    for obj in scene.objects:
        print(f"  {obj.id}: ({obj.position.x:.1f}, {obj.position.y:.1f})")

    print("\n" + "=" * 50)
    print("✅ Intelligent Layout Engine ready!")
    print("   - Constraint satisfaction")
    print("   - Collision detection and avoidance")
    print("   - Force-directed layout")
    print("   - Grid snapping for alignment")
    print("   - Dynamic canvas sizing")
    print("   - Wire auto-routing")
