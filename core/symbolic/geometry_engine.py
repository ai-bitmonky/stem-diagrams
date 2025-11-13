"""
Geometry Engine - Computational Geometry for Diagram Layout
Phase 4B of Planning & Reasoning Roadmap

Provides computational geometry capabilities:
- Collision detection (polygon intersections)
- Spatial indexing (R-tree for fast queries)
- 2D bin packing algorithms
- Convex hulls and bounding boxes
- Distance calculations

Installation:
    pip install shapely rtree

Example:
    engine = GeometryEngine()
    overlap = engine.check_overlap(obj1, obj2)
    position = engine.find_non_overlapping_position(new_obj, existing_objs)
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import math

# Shapely is optional - graceful degradation if not installed
try:
    from shapely.geometry import Point, Polygon, LineString, box, MultiPolygon
    from shapely.ops import unary_union, nearest_points
    from shapely.prepared import prep
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    Point = Polygon = LineString = box = MultiPolygon = None
    unary_union = nearest_points = prep = None

# R-tree is optional
try:
    from shapely.strtree import STRtree
    RTREE_AVAILABLE = True
except ImportError:
    RTREE_AVAILABLE = False
    STRtree = None


@dataclass
class Rectangle:
    """Simple rectangle representation"""
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_box(self):
        """Convert to shapely box"""
        if not SHAPELY_AVAILABLE:
            return None
        return box(self.left, self.top, self.right, self.bottom)

    def intersects(self, other: 'Rectangle') -> bool:
        """Check if this rectangle intersects with another"""
        return not (self.right <= other.left or
                   other.right <= self.left or
                   self.bottom <= other.top or
                   other.bottom <= self.top)

    def distance_to(self, other: 'Rectangle') -> float:
        """Calculate distance between rectangle centers"""
        dx = other.center_x - self.center_x
        dy = other.center_y - self.center_y
        return math.sqrt(dx * dx + dy * dy)


@dataclass
class PackingResult:
    """Result of 2D bin packing"""
    rectangles: List[Rectangle] = field(default_factory=list)
    total_area: float = 0.0
    bounding_box: Optional[Rectangle] = None
    packing_efficiency: float = 0.0
    success: bool = True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'rectangle_count': len(self.rectangles),
            'total_area': self.total_area,
            'bounding_box': {
                'x': self.bounding_box.x,
                'y': self.bounding_box.y,
                'width': self.bounding_box.width,
                'height': self.bounding_box.height
            } if self.bounding_box else None,
            'packing_efficiency': self.packing_efficiency,
            'success': self.success
        }


class GeometryEngine:
    """
    Computational geometry engine for diagram layout

    Provides:
    - Collision detection using Shapely polygons
    - Spatial indexing with R-tree for O(log n) queries
    - 2D bin packing algorithms
    - Geometric calculations
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize geometry engine

        Args:
            verbose: Enable verbose logging

        Raises:
            ImportError: If Shapely is not installed
        """
        if not SHAPELY_AVAILABLE:
            raise ImportError(
                "Shapely is not installed. Install with: pip install shapely rtree"
            )

        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.spatial_index: Optional[Any] = None

    # ========== Collision Detection ==========

    def check_overlap(self, rect1: Rectangle, rect2: Rectangle, margin: float = 0.0) -> bool:
        """
        Check if two rectangles overlap

        Args:
            rect1: First rectangle
            rect2: Second rectangle
            margin: Additional margin to consider (default: 0)

        Returns:
            True if rectangles overlap, False otherwise

        Example:
            >>> r1 = Rectangle(0, 0, 100, 100)
            >>> r2 = Rectangle(50, 50, 100, 100)
            >>> engine.check_overlap(r1, r2)
            True
        """
        # Add margin to rectangles
        if margin > 0:
            r1_expanded = Rectangle(
                rect1.x - margin,
                rect1.y - margin,
                rect1.width + 2 * margin,
                rect1.height + 2 * margin
            )
            r2_expanded = Rectangle(
                rect2.x - margin,
                rect2.y - margin,
                rect2.width + 2 * margin,
                rect2.height + 2 * margin
            )
            return r1_expanded.intersects(r2_expanded)

        return rect1.intersects(rect2)

    def check_overlap_shapely(self, rect1: Rectangle, rect2: Rectangle) -> bool:
        """Check overlap using Shapely (more accurate for complex shapes)"""
        box1 = rect1.to_box()
        box2 = rect2.to_box()
        return box1.intersects(box2)

    def find_overlaps(self, rectangles: List[Rectangle], margin: float = 0.0) -> List[Tuple[int, int]]:
        """
        Find all pairs of overlapping rectangles

        Args:
            rectangles: List of rectangles to check
            margin: Additional margin to consider

        Returns:
            List of (i, j) index pairs that overlap

        Example:
            >>> overlaps = engine.find_overlaps(rectangles)
            >>> print(f"Found {len(overlaps)} overlapping pairs")
        """
        overlaps = []

        for i in range(len(rectangles)):
            for j in range(i + 1, len(rectangles)):
                if self.check_overlap(rectangles[i], rectangles[j], margin):
                    overlaps.append((i, j))

        return overlaps

    # ========== Spatial Indexing ==========

    def build_spatial_index(self, rectangles: List[Rectangle]) -> None:
        """
        Build R-tree spatial index for fast queries

        Args:
            rectangles: List of rectangles to index

        Example:
            >>> engine.build_spatial_index(rectangles)
            >>> nearby = engine.query_nearby(query_rect)
        """
        if not RTREE_AVAILABLE:
            self.logger.warning("R-tree not available, using linear search")
            self.spatial_index = None
            return

        # Convert rectangles to shapely boxes
        geometries = [rect.to_box() for rect in rectangles]

        # Build STRtree (Sort-Tile-Recursive tree)
        self.spatial_index = STRtree(geometries)

        if self.verbose:
            self.logger.info(f"Built spatial index with {len(geometries)} objects")

    def query_nearby(self, query_rect: Rectangle, rectangles: List[Rectangle]) -> List[int]:
        """
        Query rectangles near a query rectangle using spatial index

        Args:
            query_rect: Rectangle to query around
            rectangles: Original list of rectangles

        Returns:
            List of indices of nearby rectangles

        Example:
            >>> nearby_indices = engine.query_nearby(new_rect, existing_rects)
        """
        if self.spatial_index is None:
            # Fallback to linear search
            nearby = []
            for i, rect in enumerate(rectangles):
                if query_rect.distance_to(rect) < max(query_rect.width, query_rect.height) * 3:
                    nearby.append(i)
            return nearby

        # Use spatial index
        query_box = query_rect.to_box()
        nearby_geoms = self.spatial_index.query(query_box)

        # Find indices
        nearby_indices = []
        for i, rect in enumerate(rectangles):
            if rect.to_box() in nearby_geoms:
                nearby_indices.append(i)

        return nearby_indices

    # ========== Non-Overlapping Positioning ==========

    def find_non_overlapping_position(self,
                                     new_rect: Rectangle,
                                     existing_rects: List[Rectangle],
                                     canvas: Rectangle,
                                     margin: float = 10.0,
                                     grid_size: int = 20) -> Optional[Tuple[float, float]]:
        """
        Find a non-overlapping position for a new rectangle

        Args:
            new_rect: Rectangle to place (dimensions are used, position is ignored)
            existing_rects: List of already placed rectangles
            canvas: Canvas bounds
            margin: Minimum margin between rectangles
            grid_size: Grid step size for search

        Returns:
            (x, y) position if found, None if no valid position exists

        Example:
            >>> position = engine.find_non_overlapping_position(
            ...     Rectangle(0, 0, 50, 50),
            ...     existing_rectangles,
            ...     Rectangle(0, 0, 800, 600)
            ... )
        """
        if not existing_rects:
            # No existing rectangles, place at center
            return (canvas.center_x - new_rect.width / 2,
                   canvas.center_y - new_rect.height / 2)

        # Build spatial index for faster queries
        self.build_spatial_index(existing_rects)

        # Try positions in a grid
        for y in range(int(canvas.top), int(canvas.bottom - new_rect.height), grid_size):
            for x in range(int(canvas.left), int(canvas.right - new_rect.width), grid_size):
                # Create candidate rectangle
                candidate = Rectangle(x, y, new_rect.width, new_rect.height)

                # Check if within canvas
                if (candidate.left < canvas.left or
                    candidate.right > canvas.right or
                    candidate.top < canvas.top or
                    candidate.bottom > canvas.bottom):
                    continue

                # Check for overlaps with existing rectangles
                overlaps = False
                for existing in existing_rects:
                    if self.check_overlap(candidate, existing, margin):
                        overlaps = True
                        break

                if not overlaps:
                    return (x, y)

        # No position found
        return None

    # ========== 2D Bin Packing ==========

    def pack_rectangles(self,
                       rectangles: List[Rectangle],
                       canvas: Rectangle,
                       algorithm: str = 'largest_first',
                       margin: float = 10.0) -> PackingResult:
        """
        Pack rectangles into a canvas using bin packing algorithm

        Args:
            rectangles: List of rectangles to pack
            canvas: Canvas bounds
            algorithm: Packing algorithm ('largest_first', 'best_fit', 'skyline')
            margin: Minimum margin between rectangles

        Returns:
            PackingResult with packed positions

        Algorithms:
        - largest_first: Sort by area, place largest first
        - best_fit: Try to minimize wasted space
        - skyline: Maintain skyline of occupied space

        Example:
            >>> result = engine.pack_rectangles(
            ...     rectangles,
            ...     Rectangle(0, 0, 800, 600),
            ...     algorithm='largest_first'
            ... )
            >>> print(f"Efficiency: {result.packing_efficiency:.1%}")
        """
        if algorithm == 'largest_first':
            return self._pack_largest_first(rectangles, canvas, margin)
        elif algorithm == 'best_fit':
            return self._pack_best_fit(rectangles, canvas, margin)
        elif algorithm == 'skyline':
            return self._pack_skyline(rectangles, canvas, margin)
        else:
            raise ValueError(f"Unknown packing algorithm: {algorithm}")

    def _pack_largest_first(self,
                           rectangles: List[Rectangle],
                           canvas: Rectangle,
                           margin: float) -> PackingResult:
        """Pack rectangles largest first"""
        # Sort by area (largest first)
        sorted_rects = sorted(rectangles, key=lambda r: r.area, reverse=True)

        packed = []
        for rect in sorted_rects:
            position = self.find_non_overlapping_position(rect, packed, canvas, margin)

            if position:
                # Create packed rectangle at found position
                packed_rect = Rectangle(position[0], position[1], rect.width, rect.height)
                packed.append(packed_rect)
            else:
                # Could not pack this rectangle
                if self.verbose:
                    self.logger.warning(f"Could not pack rectangle {rect.width}x{rect.height}")

        # Calculate statistics
        return self._calculate_packing_stats(packed, canvas)

    def _pack_best_fit(self,
                      rectangles: List[Rectangle],
                      canvas: Rectangle,
                      margin: float) -> PackingResult:
        """Pack rectangles using best-fit heuristic"""
        # For now, use largest_first (best_fit would require more complex logic)
        return self._pack_largest_first(rectangles, canvas, margin)

    def _pack_skyline(self,
                     rectangles: List[Rectangle],
                     canvas: Rectangle,
                     margin: float) -> PackingResult:
        """Pack rectangles using skyline algorithm"""
        # Simplified skyline: maintain y-levels
        sorted_rects = sorted(rectangles, key=lambda r: r.height, reverse=True)

        packed = []
        current_x = canvas.left + margin
        current_y = canvas.top + margin
        row_height = 0

        for rect in sorted_rects:
            # Try to place in current row
            if current_x + rect.width + margin <= canvas.right:
                # Fits in current row
                packed_rect = Rectangle(current_x, current_y, rect.width, rect.height)
                packed.append(packed_rect)

                current_x += rect.width + margin
                row_height = max(row_height, rect.height)
            else:
                # Start new row
                current_y += row_height + margin
                current_x = canvas.left + margin
                row_height = rect.height

                if current_y + rect.height + margin <= canvas.bottom:
                    packed_rect = Rectangle(current_x, current_y, rect.width, rect.height)
                    packed.append(packed_rect)
                    current_x += rect.width + margin
                else:
                    # Out of vertical space
                    if self.verbose:
                        self.logger.warning(f"Out of vertical space for {rect.width}x{rect.height}")

        return self._calculate_packing_stats(packed, canvas)

    def _calculate_packing_stats(self, packed: List[Rectangle], canvas: Rectangle) -> PackingResult:
        """Calculate packing statistics"""
        if not packed:
            return PackingResult(success=False)

        total_area = sum(r.area for r in packed)

        # Calculate bounding box
        min_x = min(r.left for r in packed)
        max_x = max(r.right for r in packed)
        min_y = min(r.top for r in packed)
        max_y = max(r.bottom for r in packed)

        bounding_box = Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

        # Packing efficiency = total area / bounding box area
        efficiency = total_area / bounding_box.area if bounding_box.area > 0 else 0

        return PackingResult(
            rectangles=packed,
            total_area=total_area,
            bounding_box=bounding_box,
            packing_efficiency=efficiency,
            success=True
        )

    # ========== Geometric Calculations ==========

    def calculate_distance(self, rect1: Rectangle, rect2: Rectangle) -> float:
        """Calculate distance between rectangle centers"""
        return rect1.distance_to(rect2)

    def calculate_nearest_edge_distance(self, rect1: Rectangle, rect2: Rectangle) -> float:
        """
        Calculate minimum distance between edges of two rectangles

        Returns 0 if rectangles overlap
        """
        if self.check_overlap(rect1, rect2):
            return 0.0

        # Calculate horizontal and vertical gaps
        horizontal_gap = max(rect1.left - rect2.right, rect2.left - rect1.right, 0)
        vertical_gap = max(rect1.top - rect2.bottom, rect2.top - rect1.bottom, 0)

        if horizontal_gap > 0 and vertical_gap > 0:
            # Diagonal distance
            return math.sqrt(horizontal_gap ** 2 + vertical_gap ** 2)
        else:
            # Along one axis
            return max(horizontal_gap, vertical_gap)

    def calculate_bounding_box(self, rectangles: List[Rectangle]) -> Rectangle:
        """Calculate bounding box containing all rectangles"""
        if not rectangles:
            return Rectangle(0, 0, 0, 0)

        min_x = min(r.left for r in rectangles)
        max_x = max(r.right for r in rectangles)
        min_y = min(r.top for r in rectangles)
        max_y = max(r.bottom for r in rectangles)

        return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

    def calculate_convex_hull(self, rectangles: List[Rectangle]) -> List[Tuple[float, float]]:
        """
        Calculate convex hull of rectangle corners

        Returns:
            List of (x, y) points forming the convex hull
        """
        if not SHAPELY_AVAILABLE:
            # Fallback to bounding box
            bbox = self.calculate_bounding_box(rectangles)
            return [
                (bbox.left, bbox.top),
                (bbox.right, bbox.top),
                (bbox.right, bbox.bottom),
                (bbox.left, bbox.bottom)
            ]

        # Collect all corner points
        points = []
        for rect in rectangles:
            points.extend([
                Point(rect.left, rect.top),
                Point(rect.right, rect.top),
                Point(rect.right, rect.bottom),
                Point(rect.left, rect.bottom)
            ])

        # Create MultiPoint and get convex hull
        from shapely.geometry import MultiPoint
        hull = MultiPoint(points).convex_hull

        # Extract coordinates
        if hasattr(hull, 'exterior'):
            return list(hull.exterior.coords)
        else:
            return [(p.x, p.y) for p in points]

    # ========== Utility Methods ==========

    def is_available(self) -> bool:
        """Check if Shapely is available"""
        return SHAPELY_AVAILABLE

    def __repr__(self) -> str:
        """String representation"""
        return f"GeometryEngine(shapely={SHAPELY_AVAILABLE}, rtree={RTREE_AVAILABLE})"


# ========== Standalone Functions ==========

def check_shapely_availability() -> bool:
    """Check if Shapely is available"""
    return SHAPELY_AVAILABLE


def simple_overlap_check(rects: List[Tuple[float, float, float, float]]) -> List[Tuple[int, int]]:
    """
    Simple overlap check without Shapely

    Args:
        rects: List of (x, y, width, height) tuples

    Returns:
        List of (i, j) index pairs that overlap

    Example:
        >>> overlaps = simple_overlap_check([
        ...     (0, 0, 100, 100),
        ...     (50, 50, 100, 100),
        ...     (200, 200, 50, 50)
        ... ])
        >>> print(overlaps)  # [(0, 1)]
    """
    rectangles = [Rectangle(x, y, w, h) for x, y, w, h in rects]
    overlaps = []

    for i in range(len(rectangles)):
        for j in range(i + 1, len(rectangles)):
            if rectangles[i].intersects(rectangles[j]):
                overlaps.append((i, j))

    return overlaps


def pack_simple(sizes: List[Tuple[float, float]],
                canvas_width: float = 800,
                canvas_height: float = 600) -> List[Tuple[float, float]]:
    """
    Simple packing without Shapely

    Args:
        sizes: List of (width, height) tuples
        canvas_width: Canvas width
        canvas_height: Canvas height

    Returns:
        List of (x, y) positions

    Example:
        >>> positions = pack_simple([(100, 100), (50, 50), (75, 75)])
    """
    if not SHAPELY_AVAILABLE:
        # Simple grid packing
        positions = []
        current_x = 0
        current_y = 0
        row_height = 0

        for width, height in sizes:
            if current_x + width > canvas_width:
                # New row
                current_x = 0
                current_y += row_height
                row_height = 0

            positions.append((current_x, current_y))
            current_x += width
            row_height = max(row_height, height)

        return positions

    # Use GeometryEngine
    engine = GeometryEngine()
    rectangles = [Rectangle(0, 0, w, h) for w, h in sizes]
    canvas = Rectangle(0, 0, canvas_width, canvas_height)

    result = engine.pack_rectangles(rectangles, canvas, algorithm='skyline')

    if result.success:
        return [(r.x, r.y) for r in result.rectangles]
    else:
        return []
