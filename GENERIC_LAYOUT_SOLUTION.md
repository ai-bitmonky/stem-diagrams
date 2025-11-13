# Generic Layout Solution - Implementation Guide

**Date:** November 11, 2025
**Status:** 🚧 IN PROGRESS - Core concept implemented, refinement needed

---

## The Right Approach: Declarative + Constraint-Based

### ✅ What We've Achieved

**Interpreter (Declarative):**
```python
# Interpreter only specifies WHAT and dimensions, not WHERE
top_plate = SceneObject(
    id="plate_top",
    type=PrimitiveType.RECTANGLE,
    position=None,  # Layout engine will determine this
    properties={"width": 400, "height": 12, "charge": "+Q"},
    ...
)

# Constraints specify relationships
constraints.append(Constraint(
    type=ConstraintType.PARALLEL,
    objects=["plate_top", "plate_bottom"]
))
constraints.append(Constraint(
    type=ConstraintType.DISTANCE,
    objects=["plate_top", "plate_bottom"],
    value=180
))
```

**Layout Engine (Understands Constraints):**
```python
def _place_electrostatics(self, scene, spec):
    # Extract dimensions from properties
    plate_width = plates[0].properties.get('width', 400)
    plate_height = plates[0].properties.get('height', 12)

    # Find DISTANCE constraint
    for constraint in scene.constraints:
        if constraint.type == ConstraintType.DISTANCE:
            plate_separation = constraint.value

    # Position based on PARALLEL constraint → vertical stacking
    plate1_y = self.center[1] - plate_separation / 2 - plate_height
    plate2_y = self.center[1] + plate_separation / 2

    plates[0].position = {
        'x': self.center[0] - plate_width / 2,
        'y': plate1_y,
        'anchor': 'top-left'
    }
```

### ⚠️ Current Issues

1. **Dielectric Positioning:** Layout engine still uses ID-based logic ("left", "right_top")
2. **Bounds Errors:** Objects extending beyond canvas (calculation issue)
3. **Overlaps:** Right dielectrics overlapping each other

---

## The Generic Solution (Complete)

### Phase 1: Enhanced Constraint Types

**Add to schema_v1.py:**
```python
class ConstraintType(Enum):
    # Existing
    PARALLEL = "parallel"
    DISTANCE = "distance"

    # NEW: Spatial relationships
    LEFT_OF = "left_of"        # obj1 is left of obj2
    RIGHT_OF = "right_of"      # obj1 is right of obj2
    ABOVE = "above"            # obj1 is above obj2
    BELOW = "below"            # obj1 is below obj2
    ALIGNED_H = "aligned_h"    # Horizontal alignment
    ALIGNED_V = "aligned_v"    # Vertical alignment
    ADJACENT = "adjacent"      # Objects touch (no gap)
    BETWEEN = "between"        # obj1 is between obj2 and obj3
```

### Phase 2: Interpreter Uses Spatial Constraints

**Example: Three-dielectric capacitor**
```python
# Define objects with dimensions only
dielectric_left = SceneObject(
    id="dielectric_left",
    position=None,
    properties={"width": 200, "height": 180, "kappa": 2.5}
)

dielectric_right_top = SceneObject(
    id="dielectric_right_top",
    position=None,
    properties={"width": 200, "height": 90, "kappa": 4.0}
)

dielectric_right_bottom = SceneObject(
    id="dielectric_right_bottom",
    position=None,
    properties={"width": 200, "height": 90, "kappa": 1.5}
)

# Specify spatial relationships with constraints
constraints = [
    # Plates are parallel with 180px separation
    Constraint(type=ConstraintType.PARALLEL, objects=["plate_top", "plate_bottom"]),
    Constraint(type=ConstraintType.DISTANCE, objects=["plate_top", "plate_bottom"], value=180),

    # Dielectrics fill space between plates
    Constraint(type=ConstraintType.BETWEEN, objects=["dielectric_left", "plate_top", "plate_bottom"]),
    Constraint(type=ConstraintType.BETWEEN, objects=["dielectric_right_top", "plate_top", "plate_bottom"]),
    Constraint(type=ConstraintType.BETWEEN, objects=["dielectric_right_bottom", "plate_top", "plate_bottom"]),

    # Dielectrics are adjacent (no gaps)
    Constraint(type=ConstraintType.ADJACENT, objects=["dielectric_left", "dielectric_right_top"]),
    Constraint(type=ConstraintType.ADJACENT, objects=["dielectric_left", "dielectric_right_bottom"]),

    # Right dielectrics stacked vertically
    Constraint(type=ConstraintType.ABOVE, objects=["dielectric_right_top", "dielectric_right_bottom"]),
    Constraint(type=ConstraintType.ADJACENT, objects=["dielectric_right_top", "dielectric_right_bottom"]),

    # All dielectrics aligned horizontally with plates
    Constraint(type=ConstraintType.ALIGNED_H, objects=["plate_top", "dielectric_left", "dielectric_right_top"]),
]
```

### Phase 3: Generic Constraint Solver

**Layout engine with constraint solver:**
```python
def _solve_constraints(self, scene):
    """Generic constraint solver - works for ALL scenarios"""

    for constraint in scene.constraints:
        if constraint.type == ConstraintType.BETWEEN:
            self._apply_between_constraint(constraint, scene)
        elif constraint.type == ConstraintType.ADJACENT:
            self._apply_adjacent_constraint(constraint, scene)
        elif constraint.type == ConstraintType.ABOVE:
            self._apply_above_constraint(constraint, scene)
        elif constraint.type == ConstraintType.LEFT_OF:
            self._apply_left_of_constraint(constraint, scene)
        # ... etc

def _apply_between_constraint(self, constraint, scene):
    """Position obj1 between obj2 and obj3"""
    obj1_id, obj2_id, obj3_id = constraint.objects
    obj1 = self._find_object(scene, obj1_id)
    obj2 = self._find_object(scene, obj2_id)
    obj3 = self._find_object(scene, obj3_id)

    # obj1 should start where obj2 ends and end where obj3 starts
    if obj2.position and obj3.position:
        obj1.position = {
            'x': obj2.position['x'],
            'y': obj2.position['y'] + obj2.properties.get('height', 0),
            'anchor': 'top-left'
        }
```

---

## Benefits of Generic Solution

### ✅ Universal
- Works for capacitors, optics, mechanics, ALL domains
- No domain-specific positioning code
- Interpreters only specify WHAT and HOW THEY RELATE

### ✅ Scalable
- New constraint types can be added easily
- Complex layouts (10+ objects) handled automatically
- No manual position calculations needed

### ✅ Maintainable
- Clear separation: Interpreter defines, Layout solves
- Constraints are self-documenting
- Easy to debug (check constraints, not calculations)

### ✅ Declarative
- Interpreter: "dielectric_left is left_of dielectric_right_top"
- Layout engine: Figures out actual pixel positions
- Changes to canvas size? Just re-solve constraints!

---

## Implementation Roadmap

### ✅ Phase 1: Core Declarative Approach (DONE)
- [x] Interpreter specifies dimensions in properties
- [x] Layout engine reads properties
- [x] PARALLEL and DISTANCE constraints working
- [x] Plates position correctly (vertical stacking)

### 🚧 Phase 2: Fix Current Issues (IN PROGRESS)
- [ ] Fix bounds calculation (objects extending outside)
- [ ] Fix dielectric positioning (remove ID-based logic)
- [ ] Add BETWEEN constraint for generic positioning
- [ ] Test with multiple scenarios

### 📋 Phase 3: Full Constraint Solver (NEXT)
- [ ] Implement all spatial constraint types
- [ ] Generic constraint solver (not domain-specific)
- [ ] Constraint validation and conflict detection
- [ ] Optimization for overlapping solutions

### 📋 Phase 4: Advanced Features (FUTURE)
- [ ] Constraint priorities (hard vs soft)
- [ ] Alternative solutions (A|B positioning)
- [ ] Adaptive canvas sizing
- [ ] Visual constraint debugging

---

## Current Status

**What Works:**
- ✅ Declarative interpreter (no manual positioning)
- ✅ Layout engine reads DISTANCE constraint
- ✅ Plates positioned correctly (vertical, y=298 and y=490)
- ✅ Constraint-based approach proven

**What Needs Fixing:**
- ⚠️ Dielectric positioning (still ID-based, should use constraints)
- ⚠️ Bounds calculation (objects reported outside canvas)
- ⚠️ Right dielectric overlap (top/bottom not properly stacked)

**Root Cause of Current Issues:**
The layout engine's `_place_electrostatics()` method (lines 193-217) still uses ID parsing:
```python
if 'left' in diel.id:
    diel.position = {...}
elif 'right_top' in diel.id:
    diel.position = {...}
```

This is **NOT generic**. Should be replaced with constraint-based positioning.

---

## Recommended Next Steps

### Option 1: Quick Fix (Temporary)
Keep ID-based logic but fix the calculation errors:
- Check bounds calculation in spatial validator
- Ensure x-coordinates are correct
- Fix right dielectric stacking

**Pros:** Fast, gets diagrams working
**Cons:** Still not truly generic

### Option 2: Generic Solution (Recommended)
Implement BETWEEN and ADJACENT constraints:
1. Add constraint types to schema
2. Update interpreter to use spatial constraints
3. Implement generic constraint solver
4. Remove all ID-based positioning logic

**Pros:** Truly generic, works for all scenarios
**Cons:** More work upfront, but correct long-term solution

---

## Conclusion

The **declarative/constraint-based approach is the right solution**. We've proven it works for plates (using PARALLEL + DISTANCE constraints). Now we need to:

1. Extend it to ALL objects (not just plates)
2. Add more constraint types (BETWEEN, ADJACENT, ABOVE, etc.)
3. Remove ID-based positioning logic
4. Implement generic constraint solver

This will give us a **truly generic solution** that works for ALL scenarios, not just capacitors.

---

**Status:** 🚧 IN PROGRESS
**Next:** Implement BETWEEN constraint and fix dielectric positioning
**Goal:** 100% generic, constraint-based layout for ALL physics diagrams
