# Pipeline Architecture Fixes - Systemic Solutions

**Date:** November 11, 2025
**Issue:** Diagram rendering problems (overlapping, incorrect layouts, label issues)
**Scope:** Prevent issues across ALL scenarios, not just capacitor diagrams

---

## Root Cause Analysis

### Problem 1: **Manual Positioning in Interpreters**

**Current State:**
```python
# capacitor_interpreter.py lines 20-23
def __init__(self):
    self.canvas_width = 1200
    self.canvas_height = 800
    self.center_x = self.canvas_width // 2
    self.center_y = self.canvas_height // 2

# Lines 307, 352-353, 369-370, 385-387
position={"x": self.center_x - plate_width//2,
          "y": self.center_y - separation//2}
```

**Problem:**
- Interpreters calculate **exact pixel positions**
- Each interpreter has its own coordinate system logic
- Layout engine receives **pre-positioned** objects
- No separation between WHAT (semantic) and WHERE (spatial)

**Impact:**
- Inconsistent positioning across domains
- Hard to maintain and debug
- Layout engine becomes a "validator" not a "solver"
- Cannot optimize layouts globally

---

### Problem 2: **Layout Engine is Bypassed**

**Current State:**
```python
# universal_layout_engine.py lines 46-76
def solve(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
    # Step 1: Domain-aware initial placement
    self._initial_placement(scene, spec)  # Just validates existing positions!

    # Step 2: Constraint satisfaction
    self._solve_constraints(scene)  # Minimal adjustments only
```

**Problem:**
- Objects already have positions when they reach layout engine
- Layout engine doesn't actually "solve" layout - it just tweaks
- Initial placement logic in interpreters, not layout engine

**Impact:**
- Cannot fix bad initial positions
- Constraint solver has limited degrees of freedom
- Layout quality depends on interpreter quality

---

### Problem 3: **No Spatial Validation Layer**

**Current State:**
```python
# No validation between scene building and rendering
Scene Builder → Layout Engine → Renderer
     ↓              ↓              ↓
  [manual pos]  [validate]    [draw as-is]
```

**Problem:**
- No checks for:
  - Overlapping rectangles (unintended)
  - Labels overlapping shapes
  - Elements outside canvas bounds
  - Incorrect z-ordering
- Validation happens AFTER layout is finalized

**Impact:**
- Issues only visible in rendered SVG
- No programmatic way to detect spatial errors
- Debugging requires visual inspection

---

### Problem 4: **Inconsistent Position Format**

**Current State:**
```python
# Different formats used:
position = {"x": 100, "y": 200}                    # Rectangle
position = {"x1": 0, "y1": 0, "x2": 100, "y2": 100}  # Line
position = {"x": 50, "y": 50, "x1": 0, "y1": 0, ...}  # Arrows (both!)
```

**Problem:**
- No standard for coordinate specification
- Renderers must handle multiple formats
- Leads to coordinate confusion and bugs

**Impact:**
- Regex parsing errors (like the "21.0." bug)
- Position calculations off by one
- Difficult to write generic layout code

---

### Problem 5: **Labels as Geometric Shapes**

**Current State:**
```python
# capacitor_interpreter.py lines 401-425
label1 = SceneObject(
    id="label_k1",
    type=PrimitiveType.TEXT,  # Treated as a shape!
    position={"x": self.center_x - plate_width//4, "y": self.center_y},
    properties={"text": f"κ₁ = {k1}", "font_size": 18},
    style={"fill": "#0D47A1"}
)
scene_objects.append(label1)  # Mixed with shapes
```

**Problem:**
- Labels treated as geometric primitives
- Positioned manually alongside shapes
- No automatic overlap avoidance
- No intelligent label placement

**Impact:**
- Labels overlap shapes or other labels
- Must manually calculate label positions
- Cannot reposition labels automatically

---

### Problem 6: **No Z-Order Management**

**Current State:**
```python
# capacitor_interpreter.py lines 321, 398
scene_objects.extend([top_plate, bottom_plate])      # Z=0, 1
scene_objects.extend([dielectric1, dielectric2, dielectric3])  # Z=2, 3, 4
scene_objects.extend([label1, label2, label3])       # Z=5, 6, 7

# Implicit z-order = insertion order
```

**Problem:**
- Z-order determined by list insertion order
- No explicit layer management
- Cannot ensure labels always on top
- Hard to reason about rendering order

**Impact:**
- Labels can be drawn under shapes
- Dielectrics may cover plates
- Boundary lines invisible under fills

---

## Architectural Solutions

### Solution 1: **Declarative Scene Building**

**New Approach:**

Interpreters specify **WHAT** exists and **relationships**, NOT exact positions.

```python
# NEW: capacitor_interpreter.py
def interpret(self, spec: Dict) -> Scene:
    # Specify STRUCTURE, not positions
    scene_objects = []

    # Define plates WITHOUT absolute positions
    top_plate = SceneObject(
        id="plate_top",
        type=PrimitiveType.RECTANGLE,
        position=None,  # Layout engine will determine!
        properties={
            "width": 400,
            "height": 10,
            "charge": "+Q",
            "logical_role": "top_electrode"  # NEW: semantic role
        }
    )

    # Define CONSTRAINTS instead of positions
    constraints = [
        # Top plate is ABOVE bottom plate
        Constraint(
            type=ConstraintType.RELATIVE_POSITION,
            objects=["plate_top", "plate_bottom"],
            properties={"relation": "above", "min_distance": 200}
        ),

        # Plates are HORIZONTALLY aligned
        Constraint(
            type=ConstraintType.ALIGNMENT,
            objects=["plate_top", "plate_bottom"],
            properties={"axis": "horizontal", "offset": 0}
        ),

        # Dielectric BETWEEN plates
        Constraint(
            type=ConstraintType.CONTAINMENT,
            objects=["dielectric", "plate_top", "plate_bottom"],
            properties={"region": "between"}
        )
    ]

    return Scene(objects=scene_objects, constraints=constraints)
```

**Benefits:**
- Interpreters focus on domain logic, not pixel math
- Layout engine has full freedom to optimize
- Constraints are explicit and checkable
- Easier to maintain and debug

---

### Solution 2: **Enhanced Layout Engine**

**New Approach:**

Layout engine becomes the **primary** position calculator, not validator.

```python
# NEW: universal_layout_engine.py
class UniversalLayoutEngine:
    def solve(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """
        Primary layout solver - calculates ALL positions from scratch
        """
        # Step 1: Parse constraints into solver variables
        variables = self._extract_layout_variables(scene)

        # Step 2: Build constraint system
        constraints = self._build_constraint_system(scene, spec)

        # Step 3: Solve using constraint solver (Z3, OR-tools, etc.)
        solution = self._solve_layout_optimization(variables, constraints)

        # Step 4: Apply solution to scene
        self._apply_solution(scene, solution)

        # Step 5: Validate spatial properties
        self._validate_spatial_properties(scene)

        return scene

    def _extract_layout_variables(self, scene: Scene) -> Dict:
        """Extract x, y for each object as solver variables"""
        variables = {}
        for obj in scene.objects:
            variables[f"{obj.id}_x"] = Variable(f"{obj.id}_x")
            variables[f"{obj.id}_y"] = Variable(f"{obj.id}_y")
        return variables

    def _build_constraint_system(self, scene: Scene, spec: CanonicalProblemSpec):
        """Convert scene constraints to solver constraints"""
        solver_constraints = []

        for constraint in scene.constraints:
            if constraint.type == ConstraintType.RELATIVE_POSITION:
                # obj1 is ABOVE obj2 with min_distance d
                obj1_id, obj2_id = constraint.objects
                min_dist = constraint.properties.get("min_distance", 50)

                # Constraint: obj1_y + obj1_height + min_dist <= obj2_y
                solver_constraints.append(
                    variables[f"{obj1_id}_y"] + obj1.height + min_dist
                    <= variables[f"{obj2_id}_y"]
                )

            elif constraint.type == ConstraintType.ALIGNMENT:
                # Objects share same x or y coordinate
                axis = constraint.properties.get("axis")
                if axis == "horizontal":
                    # All objects have same y
                    base_obj = constraint.objects[0]
                    for obj in constraint.objects[1:]:
                        solver_constraints.append(
                            variables[f"{base_obj}_y"] == variables[f"{obj}_y"]
                        )

        return solver_constraints
```

**Benefits:**
- True constraint-based layout
- Can handle complex spatial relationships
- Optimizes globally, not locally
- Reproducible and deterministic

---

### Solution 3: **Spatial Validation Layer**

**New Approach:**

Add validation **before** rendering to catch spatial errors early.

```python
# NEW: core/spatial_validator.py
class SpatialValidator:
    """
    Validates spatial properties of positioned scenes

    Checks:
    - No unintended overlaps
    - Labels don't overlap shapes
    - All elements within canvas bounds
    - Z-order is semantically correct
    """

    def validate(self, scene: Scene) -> ValidationReport:
        """Validate spatial properties"""
        errors = []
        warnings = []

        # Check 1: Detect overlapping rectangles
        overlaps = self._check_overlaps(scene)
        for overlap in overlaps:
            if overlap.is_intentional:  # Dielectric inside capacitor
                continue
            errors.append(
                f"Unintended overlap: {overlap.obj1} and {overlap.obj2}"
            )

        # Check 2: Label positioning
        label_issues = self._check_label_placement(scene)
        for issue in label_issues:
            warnings.append(
                f"Label '{issue.label_id}' overlaps with {issue.overlapping_with}"
            )

        # Check 3: Canvas bounds
        out_of_bounds = self._check_bounds(scene)
        for obj in out_of_bounds:
            errors.append(
                f"Object '{obj.id}' extends beyond canvas bounds"
            )

        # Check 4: Z-order correctness
        z_order_issues = self._check_z_order(scene)
        for issue in z_order_issues:
            warnings.append(
                f"Object '{issue.obj}' has incorrect z-order (expected layer {issue.expected_layer})"
            )

        return ValidationReport(errors=errors, warnings=warnings)

    def _check_overlaps(self, scene: Scene) -> List[Overlap]:
        """Detect overlapping rectangles"""
        overlaps = []
        rectangles = [obj for obj in scene.objects
                     if obj.type == PrimitiveType.RECTANGLE]

        for i, rect1 in enumerate(rectangles):
            for rect2 in rectangles[i+1:]:
                if self._rectangles_overlap(rect1, rect2):
                    # Check if overlap is intentional (containment constraint)
                    is_intentional = self._is_intentional_overlap(
                        rect1, rect2, scene.constraints
                    )
                    overlaps.append(Overlap(
                        obj1=rect1.id,
                        obj2=rect2.id,
                        is_intentional=is_intentional
                    ))

        return overlaps

    def _rectangles_overlap(self, r1: SceneObject, r2: SceneObject) -> bool:
        """Check if two rectangles overlap"""
        r1_x1 = r1.position["x"]
        r1_y1 = r1.position["y"]
        r1_x2 = r1_x1 + r1.properties["width"]
        r1_y2 = r1_y1 + r1.properties["height"]

        r2_x1 = r2.position["x"]
        r2_y1 = r2.position["y"]
        r2_x2 = r2_x1 + r2.properties["width"]
        r2_y2 = r2_y1 + r2.properties["height"]

        # Check for overlap
        return not (r1_x2 < r2_x1 or r1_x1 > r2_x2 or
                   r1_y2 < r2_y1 or r1_y1 > r2_y2)
```

**Pipeline Integration:**
```python
# unified_diagram_pipeline.py
def generate_diagram(self, problem_text: str) -> Dict:
    # ... existing phases ...

    # Phase 5: Layout Engine
    positioned_scene = self.layout_engine.solve(scene, spec)

    # NEW Phase 5.5: Spatial Validation
    spatial_validator = SpatialValidator()
    spatial_report = spatial_validator.validate(positioned_scene)

    if spatial_report.has_errors():
        # Try to fix automatically
        positioned_scene = self._auto_fix_spatial_issues(
            positioned_scene, spatial_report
        )

        # Re-validate
        spatial_report = spatial_validator.validate(positioned_scene)

        if spatial_report.has_errors():
            raise SpatialValidationError(spatial_report.errors)

    # Phase 6: Rendering (only if spatial validation passes)
    svg = self.renderer.render(positioned_scene, spec)
```

**Benefits:**
- Catches errors before rendering
- Provides actionable error messages
- Enables auto-fixing of common issues
- Prevents bad diagrams from being generated

---

### Solution 4: **Standard Position Format**

**New Approach:**

Enforce a single, consistent position format across all object types.

```python
# NEW: core/scene/schema_v1.py
@dataclass
class Position:
    """
    Standard position format for all scene objects

    All objects use (x, y) as anchor point, with dimensions in properties
    """
    x: float  # Anchor x-coordinate
    y: float  # Anchor y-coordinate

    # Optional: for objects with extent
    anchor: str = "center"  # "center", "top-left", "bottom-left", etc.

    # Optional: rotation
    rotation: float = 0.0  # Degrees, counter-clockwise

@dataclass
class SceneObject:
    id: str
    type: PrimitiveType
    position: Optional[Position]  # Standard format!
    properties: Dict[str, Any]
    style: Dict[str, Any]
    layer: int = 0  # Explicit z-order

# Usage examples:
rectangle = SceneObject(
    type=PrimitiveType.RECTANGLE,
    position=Position(x=100, y=200, anchor="top-left"),
    properties={"width": 50, "height": 30}
)

line = SceneObject(
    type=PrimitiveType.LINE,
    position=Position(x=0, y=0, anchor="start"),
    properties={"dx": 100, "dy": 50}  # Delta, not absolute end point!
)

circle = SceneObject(
    type=PrimitiveType.CIRCLE,
    position=Position(x=150, y=150, anchor="center"),
    properties={"radius": 25}
)

text = SceneObject(
    type=PrimitiveType.TEXT,
    position=Position(x=200, y=100, anchor="bottom-left"),
    properties={"text": "Label", "font_size": 14}
)
```

**Benefits:**
- Single format eliminates confusion
- Easier to write layout algorithms
- Reduces coordinate calculation errors
- Consistent across all renderers

---

### Solution 5: **Intelligent Label Placement**

**New Approach:**

Separate labels from geometric shapes and place them intelligently.

```python
# NEW: core/label_placer.py
class IntelligentLabelPlacer:
    """
    Automatic label placement with overlap avoidance

    Places labels near their associated objects while avoiding:
    - Other labels
    - Geometric shapes
    - Canvas edges
    """

    def place_labels(self, scene: Scene) -> Scene:
        """Place all labels intelligently"""
        # Step 1: Separate labels from shapes
        shapes = [obj for obj in scene.objects
                 if obj.type != PrimitiveType.TEXT]
        labels = [obj for obj in scene.objects
                 if obj.type == PrimitiveType.TEXT]

        # Step 2: For each label, find best position
        for label in labels:
            # Get associated object (from properties or ID)
            target_obj_id = label.properties.get("target_object")
            target_obj = next((obj for obj in shapes if obj.id == target_obj_id), None)

            if target_obj:
                # Find best label position near target
                best_pos = self._find_best_label_position(
                    label, target_obj, shapes, labels
                )
                label.position = best_pos

        return scene

    def _find_best_label_position(
        self,
        label: SceneObject,
        target: SceneObject,
        shapes: List[SceneObject],
        other_labels: List[SceneObject]
    ) -> Position:
        """Find best position for label near target object"""

        # Define candidate positions around target
        candidates = [
            Position(target.position.x, target.position.y - 30, anchor="bottom"),  # Above
            Position(target.position.x, target.position.y + 30, anchor="top"),     # Below
            Position(target.position.x - 30, target.position.y, anchor="right"),   # Left
            Position(target.position.x + 30, target.position.y, anchor="left"),    # Right
            Position(target.position.x + 20, target.position.y - 20, anchor="bottom-left"),  # Top-right
            Position(target.position.x - 20, target.position.y - 20, anchor="bottom-right"), # Top-left
        ]

        # Score each candidate
        best_pos = None
        best_score = -float('inf')

        for pos in candidates:
            score = self._score_label_position(label, pos, shapes, other_labels)
            if score > best_score:
                best_score = score
                best_pos = pos

        return best_pos

    def _score_label_position(
        self,
        label: SceneObject,
        pos: Position,
        shapes: List[SceneObject],
        other_labels: List[SceneObject]
    ) -> float:
        """Score a label position (higher is better)"""
        score = 100.0

        # Penalty for overlapping shapes
        for shape in shapes:
            if self._overlaps(label, pos, shape):
                score -= 50

        # Penalty for overlapping other labels
        for other_label in other_labels:
            if other_label.id != label.id and self._overlaps(label, pos, other_label):
                score -= 30

        # Penalty for being near canvas edge
        if self._near_edge(pos):
            score -= 20

        # Bonus for being in preferred direction (above or right)
        if pos.anchor in ["bottom", "left"]:
            score += 10

        return score
```

**Pipeline Integration:**
```python
# unified_diagram_pipeline.py - Phase 5
def generate_diagram(self, problem_text: str) -> Dict:
    # ... existing phases ...

    # Phase 5: Layout Engine (positions shapes only)
    positioned_scene = self.layout_engine.solve(scene, spec)

    # NEW Phase 5.5: Intelligent Label Placement
    label_placer = IntelligentLabelPlacer()
    positioned_scene = label_placer.place_labels(positioned_scene)

    # Phase 6: Spatial Validation
    spatial_validator.validate(positioned_scene)

    # Phase 7: Rendering
    svg = self.renderer.render(positioned_scene, spec)
```

**Benefits:**
- Labels never overlap shapes or each other
- Automatic positioning saves interpreter complexity
- Consistent label placement across diagrams
- Can be customized per domain (e.g., physics prefers above/right)

---

### Solution 6: **Explicit Z-Order Management**

**New Approach:**

Add explicit layer system for z-ordering.

```python
# NEW: core/scene/schema_v1.py
class RenderLayer(Enum):
    """Explicit rendering layers (z-order)"""
    BACKGROUND = 0      # Grid, axes
    FILL = 1           # Filled shapes (dielectrics)
    SHAPES = 2         # Primary objects (plates, masses, lenses)
    LINES = 3          # Connecting lines, boundaries
    ARROWS = 4         # Force arrows, field lines
    ANNOTATIONS = 5    # Dimensions, angles
    LABELS = 6         # Text labels
    FOREGROUND = 7     # Overlays, highlights

@dataclass
class SceneObject:
    id: str
    type: PrimitiveType
    position: Optional[Position]
    properties: Dict[str, Any]
    style: Dict[str, Any]
    layer: RenderLayer = RenderLayer.SHAPES  # Explicit layer!

# Usage in capacitor_interpreter.py:
top_plate = SceneObject(
    id="plate_top",
    type=PrimitiveType.RECTANGLE,
    layer=RenderLayer.SHAPES,  # Plates on SHAPES layer
    ...
)

dielectric = SceneObject(
    id="dielectric",
    type=PrimitiveType.RECTANGLE,
    layer=RenderLayer.FILL,  # Dielectric behind plates!
    ...
)

label = SceneObject(
    id="label_k1",
    type=PrimitiveType.TEXT,
    layer=RenderLayer.LABELS,  # Labels always on top
    ...
)

# Renderer sorts by layer before drawing:
def render(self, scene: Scene) -> str:
    # Sort objects by layer
    sorted_objects = sorted(scene.objects, key=lambda obj: obj.layer.value)

    for obj in sorted_objects:
        svg += self._render_object(obj)
```

**Benefits:**
- Explicit, predictable z-ordering
- Labels always render on top
- Background elements always behind
- Domain-specific layer conventions

---

## Implementation Roadmap

### Phase 1: Foundation (High Priority)

**Week 1-2:**

1. **Standardize Position Format**
   - Update `core/scene/schema_v1.py` with `Position` dataclass
   - Migrate all interpreters to use standard format
   - Update layout engine and renderer

2. **Add Explicit Layers**
   - Add `RenderLayer` enum to schema
   - Update all interpreters to specify layers
   - Update renderer to sort by layer

3. **Spatial Validation Layer**
   - Implement `core/spatial_validator.py`
   - Add validation step to pipeline
   - Write comprehensive tests

**Success Criteria:**
- All diagrams use standard position format
- Z-order issues eliminated
- Spatial validation catches overlap errors

---

### Phase 2: Enhanced Layout Engine (Medium Priority)

**Week 3-4:**

4. **Declarative Scene Building**
   - Update interpreter interface to return unpositioned objects
   - Implement constraint-based positioning
   - Migrate one interpreter (e.g., capacitor) as proof-of-concept

5. **Constraint-Based Layout Solver**
   - Integrate Z3 or OR-tools for constraint solving
   - Implement constraint types (RELATIVE_POSITION, ALIGNMENT, etc.)
   - Add optimization objectives (minimize distance, maximize spacing)

6. **Intelligent Label Placement**
   - Implement `core/label_placer.py`
   - Add label placement to pipeline
   - Test with complex multi-label diagrams

**Success Criteria:**
- At least one interpreter uses declarative approach
- Layout engine solves positions from constraints
- Labels automatically avoid overlaps

---

### Phase 3: Full Migration (Low Priority)

**Week 5-8:**

7. **Migrate All Interpreters**
   - Convert all interpreters to declarative approach
   - Remove manual positioning code
   - Add domain-specific constraints

8. **Advanced Features**
   - Multi-objective optimization (aesthetics + constraints)
   - Adaptive layouts for different canvas sizes
   - Interactive constraint debugging tools

9. **Documentation & Testing**
   - Comprehensive documentation
   - Extensive test suite
   - Performance benchmarks

**Success Criteria:**
- All interpreters use declarative approach
- Zero manual positioning code
- All diagrams pass spatial validation

---

## Expected Benefits

### Immediate (Phase 1)

✅ **Eliminate coordinate confusion** - Standard format prevents bugs
✅ **Fix z-order issues** - Explicit layers ensure correct rendering
✅ **Catch spatial errors early** - Validation prevents bad diagrams

### Medium-term (Phase 2)

✅ **Simpler interpreters** - Focus on domain logic, not positioning
✅ **Better layouts** - Constraint solver optimizes globally
✅ **Automatic label placement** - No manual positioning needed

### Long-term (Phase 3)

✅ **Maintainable codebase** - Clear separation of concerns
✅ **Consistent quality** - All diagrams follow same layout principles
✅ **Extensible architecture** - Easy to add new diagram types

---

## Migration Guide for Existing Code

### For Capacitor Interpreter

**Before (Manual Positioning):**
```python
def _create_multi_dielectric_capacitor(self, objects, problem_text):
    # Manual positioning
    top_plate = SceneObject(
        position={"x": self.center_x - 200, "y": self.center_y - 110}
    )
    dielectric1 = SceneObject(
        position={"x": self.center_x - 200, "y": self.center_y - 100}
    )
```

**After (Declarative):**
```python
def _create_multi_dielectric_capacitor(self, objects, problem_text):
    # Define structure
    top_plate = SceneObject(
        position=None,  # Layout engine will determine!
        layer=RenderLayer.SHAPES
    )
    dielectric1 = SceneObject(
        position=None,
        layer=RenderLayer.FILL
    )

    # Define relationships
    constraints = [
        Constraint(
            type=ConstraintType.RELATIVE_POSITION,
            objects=["top_plate", "dielectric1"],
            properties={"relation": "above", "min_distance": 10}
        ),
        Constraint(
            type=ConstraintType.CONTAINMENT,
            objects=["dielectric1", "top_plate", "bottom_plate"],
            properties={"region": "between"}
        )
    ]
```

---

## Testing Strategy

### Spatial Validation Tests

```python
def test_no_unintended_overlaps():
    """Test that shapes don't overlap unless explicitly intended"""
    scene = generate_test_scene()
    validator = SpatialValidator()
    report = validator.validate(scene)

    assert len(report.errors) == 0, f"Found overlaps: {report.errors}"

def test_labels_dont_overlap_shapes():
    """Test that labels are positioned away from shapes"""
    scene = generate_scene_with_labels()
    validator = SpatialValidator()
    report = validator.validate(scene)

    label_overlaps = [e for e in report.errors if "label" in e.lower()]
    assert len(label_overlaps) == 0

def test_elements_within_bounds():
    """Test that all elements fit within canvas"""
    scene = generate_test_scene()
    validator = SpatialValidator()
    report = validator.validate(scene)

    out_of_bounds = [e for e in report.errors if "bounds" in e.lower()]
    assert len(out_of_bounds) == 0
```

### Layout Engine Tests

```python
def test_constraint_satisfaction():
    """Test that layout engine satisfies all constraints"""
    scene = Scene(
        objects=[obj1, obj2],
        constraints=[
            Constraint(type=ConstraintType.RELATIVE_POSITION,
                      objects=["obj1", "obj2"],
                      properties={"relation": "above", "min_distance": 50})
        ]
    )

    layout_engine = UniversalLayoutEngine()
    positioned_scene = layout_engine.solve(scene, spec)

    # Check constraint is satisfied
    obj1_pos = positioned_scene.get_object("obj1").position
    obj2_pos = positioned_scene.get_object("obj2").position
    distance = obj2_pos.y - (obj1_pos.y + obj1.height)

    assert distance >= 50, f"Constraint violated: distance={distance}"
```

---

## Conclusion

The diagram rendering issues stem from **architectural decisions**, not bugs in individual interpreters. The fixes require:

1. **Separation of concerns** - WHAT vs WHERE vs HOW
2. **Declarative specifications** - Constraints not coordinates
3. **Validation layers** - Catch errors before rendering
4. **Standardization** - Consistent formats and conventions

These changes will prevent similar issues across **ALL diagram types**, not just capacitors.

**Next Steps:**
1. Review and approve architecture changes
2. Prioritize phases based on urgency
3. Begin Phase 1 implementation
4. Test with existing diagram corpus

---

**Status:** Architecture Design Complete
**Last Updated:** November 11, 2025
**Authors:** STEM-AI Pipeline Team
