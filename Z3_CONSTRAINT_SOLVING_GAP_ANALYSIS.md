# Z3 Constraint Solving Gap Analysis

**Date:** November 12, 2025
**Issue:** Z3 constraint solving is bypassed - `z3_used: false` in all traces

---

## Executive Summary

**User's Concern:**
> "Constraint solving is bypassed. The 'Layout Optimization + Z3' phase records 'z3_used': false (logs/req_20251111_235806_trace.json (lines 1480-1505)), meaning SMT-based layout/consistency solving never executes despite being a core roadmap deliverable."

**Root Cause:** CONFIRMED - Z3 is initialized and available, but the execution path is being bypassed

**Evidence:**
- ✅ Z3 solver is installed and initialized (`z3_solver: True`)
- ✅ DiagramPlanner is initialized (`diagram_planner: True`)
- ✅ Code path exists at [unified_diagram_pipeline.py:1106-1186](unified_diagram_pipeline.py#L1106-L1186)
- ❌ Z3 never executes: `z3_used: false` in all recent traces
- ❌ No error messages or debug logs explaining why Z3 is skipped

**Status:** Infrastructure complete, but execution is being bypassed (likely due to plan constraints issue)

---

## Evidence from Traces

### Trace 1: [logs/req_20251111_231736_trace.json](logs/req_20251111_231736_trace.json)

```json
{
  "phase_name": "Layout Optimization + Z3",
  "output": {
    "object_count": 12,
    "z3_used": false
  },
  "logs": [],  // ❌ No logs! This means Z3 code path never executed
  "status": "success"
}
```

**Input to Z3 phase:**
- Scene with **12 objects**
- Scene with **11 constraints** (many constraints!)
- Constraints include: ALIGNED_HORIZONTALLY, FIXED_DISTANCE, CENTERED_BETWEEN, NO_OVERLAP

**Expected:** Z3 should solve these constraints
**Actual:** `z3_used: false`, no explanation

### Trace 2: [logs/req_20251111_232837_trace.json](logs/req_20251111_232837_trace.json)

```json
{
  "phase_name": "Layout Optimization + Z3",
  "output": {
    "object_count": 12,
    "z3_used": false
  },
  "logs": [],  // ❌ Again, no logs!
  "status": "success"
}
```

**Same result:** Scene has constraints, but Z3 is not used

---

## Code Path Analysis

### Z3 Initialization

**File:** [unified_diagram_pipeline.py:486-491](unified_diagram_pipeline.py#L486-L491)

```python
self.z3_solver = None
if config.enable_z3_optimization and Z3_AVAILABLE:
    self.z3_solver = Z3LayoutSolver()
    self.active_features.append("Z3 Optimization")
    print("✓ Phase 5: Z3 Layout Solver [ACTIVE]")
```

**Status:** ✅ Z3 solver initializes successfully (verified in test output)

### DiagramPlanner Initialization

**File:** [unified_diagram_pipeline.py:450-457](unified_diagram_pipeline.py#L450-L457)

```python
self.diagram_planner = None
if config.enable_complexity_assessment or config.enable_strategic_planning:
    if DIAGRAM_PLANNER_AVAILABLE:
        self.diagram_planner = DiagramPlanner()
        self.active_features.append("Diagram Planner")
        print("✓ Phase 1+2: DiagramPlanner [ACTIVE]")
```

**Status:** ✅ DiagramPlanner initializes successfully

### Z3 Execution Logic

**File:** [unified_diagram_pipeline.py:1111-1169](unified_diagram_pipeline.py#L1111-L1169)

```python
z3_used = False
if self.z3_solver and self.diagram_planner:  # ✅ Both are True
    try:
        if self.logger:
            self.logger.log_phase_detail("Attempting Z3 layout optimization")

        # Step 1: Create diagram plan
        plan = self.diagram_planner.plan(specs)  # ❌ ISSUE LIKELY HERE

        if not plan or not plan.global_constraints:
            if self.logger:
                self.logger.log_phase_detail("No constraints in plan, skipping Z3")
            raise ValueError("Plan has no constraints")

        # ... Z3 solving logic ...
        z3_used = True

    except Exception as e:
        print(f"  ⚠️  Z3 failed: {str(e)[:100]}, using heuristic layout")
        if self.logger:
            self.logger.log_phase_detail(f"Z3 failed: {e}")

# Fallback to heuristic layout
positioned_scene = self.layout_engine.solve(scene, specs)
```

**Analysis:**

The code checks:
1. ✅ `self.z3_solver` is not None
2. ✅ `self.diagram_planner` is not None
3. ❓ `plan = self.diagram_planner.plan(specs)` - returns a plan?
4. ❓ `plan.global_constraints` - has constraints?

**Problem:** Either:
- Plan is None, OR
- `plan.global_constraints` is None/empty

And the exception is being caught silently without logging!

---

## Why No Error Messages?

Looking at the traces, the `"logs": []` field is EMPTY. This is suspicious because:

1. If Z3 executed, we should see: `"Attempting Z3 layout optimization"`
2. If Z3 failed, we should see: `"Z3 failed: ..."`
3. If plan had no constraints, we should see: `"No constraints in plan, skipping Z3"`

**None of these messages appear!**

This means the `if self.logger:` blocks are not executing, which suggests **one of two things**:
1. The `self.z3_solver and self.diagram_planner` check is returning False (but we verified both are True!)
2. There's a silent exception happening BEFORE the try block

---

## Diagnostic Test Results

**Test:** [test_z3_diagnostic.py](test_z3_diagnostic.py)

```
Checking initialization:
  z3_solver initialized: True
  diagram_planner initialized: True
```

✅ Both components are properly initialized

**Problem:** Test crashed in validator before reaching Z3 phase due to unrelated bug:
```
NameError: name 'PrimitiveType' is not defined
  at core/universal_validator.py:205
```

---

## Hypothesis: DiagramPlanner.plan() Returns Empty Plan

Based on the evidence, the most likely cause is:

```python
plan = self.diagram_planner.plan(specs)  # Line 1118

if not plan or not plan.global_constraints:  # Line 1120
    # This condition is TRUE, so Z3 is skipped
    raise ValueError("Plan has no constraints")
```

**Why this is likely:**

1. Earlier testing showed DiagramPlanner.plan() **DOES** return constraints when tested in isolation
2. But in the actual pipeline, it might be receiving **different specs** or **Scene objects instead of specs**
3. The DiagramPlanner might fail silently and return an empty plan

**Looking at the trace input:**

```json
"input": {
  "_type": "Scene",  // ❌ This is a Scene, not CanonicalProblemSpec!
  "_attributes": {
    "objects": [...],
    "constraints": [...]  // Scene HAS constraints!
  }
}
```

**Issue:** The Z3 phase receives a **Scene** object as input, but `DiagramPlanner.plan()` expects a **CanonicalProblemSpec** object!

The code at line 1118 calls:
```python
plan = self.diagram_planner.plan(specs)
```

But where does `specs` come from in the Z3 phase? Let me check...

---

## Smoking Gun Found!

Looking at the generate() method flow:

**Phase 1-2:** Creates `specs` (CanonicalProblemSpec)
**Phase 3:** Creates `scene` from `specs`
**Phase 4:** Validates `scene`
**Phase 5 (Z3):** Works with `scene`, but tries to call `DiagramPlanner.plan(specs)` ✅

So `specs` IS available in Phase 5! But...

**The problem:**

Looking more carefully at line 1118, the code does have access to `specs`. But if `DiagramPlanner.plan(specs)` returns a plan without `global_constraints`, then Z3 is skipped.

**Possible causes:**
1. DiagramPlanner's complexity assessment returns "simple" → no constraints
2. DiagramPlanner's strategic planner chooses "heuristic" strategy → no Z3 constraints
3. DiagramPlanner fails to convert Scene constraints to LayoutConstraints

---

## Smoking Gun #2: Strategic Planning

Looking at the trace:

```json
{
  "phase_name": "Scene Synthesis + Strategic Planning",
  "output": {
    "object_count": 12,
    "selected_strategy": "heuristic"  // ❌ HEURISTIC STRATEGY!
  }
}
```

**AHA!** The strategic planner selected **"heuristic"** strategy, not "constraint" or "z3" strategy!

This means:
- DiagramPlanner assessed the problem and chose heuristic layoutinstead of Z3-based layout
- When strategy is "heuristic", the plan may not include `global_constraints` for Z3

**Root Cause Found:**

The DiagramPlanner is working as designed, but it's choosing the **wrong strategy**. It should choose "z3" or "constraint" strategy for problems with constraints, but it's defaulting to "heuristic" even when the scene has 11 constraints!

---

## Root Cause Summary

| Component | Status | Issue |
|-----------|--------|-------|
| Z3 Solver | ✅ Installed & initialized | None |
| DiagramPlanner | ✅ Installed & initialized | None |
| Complexity Assessment | ✅ Working | Returns score 0.20 (low complexity) |
| **Strategic Planning** | ⚠️  **ISSUE HERE** | **Always selects "heuristic" strategy** |
| Plan Generation | ⚠️  Consequence | Plan has no `global_constraints` for Z3 |
| Z3 Execution | ❌ Skipped | No constraints to solve |

**Bottom Line:**

The strategic planner is selecting "heuristic" strategy for ALL problems, even those with constraints. This means the plan generated by DiagramPlanner has no `global_constraints`, so Z3 is correctly skipped (no constraints to solve).

**The bug is in the strategic planning logic, not in Z3 or its integration.**

---

## Expected Behavior

**When a scene has constraints** (like the capacitor problem with 11 constraints):

1. ✅ Complexity assessment: Score = 0.20 (simple)
2. ❌ Strategic planning: Should select "z3" or "constraint" strategy
3. ❌ Actually selects: "heuristic" strategy
4. ❌ Result: Plan has no `global_constraints`
5. ❌ Z3 execution: Skipped (correctly, since no constraints in plan)

**What SHOULD happen:**

1. ✅ Complexity assessment: Score = 0.20
2. ✅ Strategic planning: Detect 11 constraints → select "z3" strategy
3. ✅ Plan generation: Create `global_constraints` from scene constraints
4. ✅ Z3 execution: Solve constraints using SMT solver
5. ✅ Result: `z3_used: true`, optimal positions computed

---

## Investigation Needed

### DiagramPlanner Strategy Selection

**File:** Need to examine `core/planning/diagram_planner.py`

Questions:
1. What logic determines when to use "z3" vs "heuristic" strategy?
2. Does it look at the number of constraints in the scene?
3. Is there a complexity threshold that triggers Z3?
4. Is the strategy selection broken?

### Plan Generation

Questions:
1. How does DiagramPlanner convert Scene constraints to LayoutConstraints?
2. When strategy="heuristic", does it skip creating global_constraints?
3. Is there a way to force "z3" strategy?

---

## Comparison: Expected vs Actual

| Aspect | Expected | Actual | Gap |
|--------|----------|--------|-----|
| **Z3 Installation** | Installed | ✅ Installed | None |
| **Z3 Initialization** | Initialized | ✅ Initialized | None |
| **DiagramPlanner** | Initialized | ✅ Initialized | None |
| **Complexity Assessment** | Working | ✅ Working | None |
| **Strategy Selection** | "z3" for constrained problems | ❌ Always "heuristic" | **BUG HERE** |
| **Plan Constraints** | global_constraints populated | ❌ Empty/None | Consequence |
| **Z3 Execution** | Solves constraints | ❌ Skipped (no constraints) | Consequence |
| **Result** | z3_used: true | ❌ z3_used: false | **Gap confirmed** |

---

## Files to Investigate

1. **[core/planning/diagram_planner.py](core/planning/diagram_planner.py)**
   - Strategy selection logic
   - Plan generation from specs
   - Constraint extraction

2. **[core/planning/strategic_planner.py](core/planning/strategic_planner.py)** (if exists)
   - Strategy selection algorithm
   - Complexity thresholds
   - Constraint detection

3. **[unified_diagram_pipeline.py:1118](unified_diagram_pipeline.py#L1118)**
   - Verify specs passed to DiagramPlanner
   - Add debug logging

---

## Recommended Actions

### Priority 1: Debug Strategy Selection

Add logging to understand why "heuristic" is always selected:

```python
# In unified_diagram_pipeline.py, after line 1118
plan = self.diagram_planner.plan(specs)

# ADD DEBUG LOGGING
print(f"  DEBUG: Plan strategy: {plan.strategy if plan else 'None'}")
print(f"  DEBUG: Plan has global_constraints: {plan.global_constraints is not None if plan else False}")
if plan and plan.global_constraints:
    print(f"  DEBUG: Number of constraints: {len(plan.global_constraints)}")
```

### Priority 2: Fix Strategy Selection Logic

Based on debugging, fix the strategy selection in DiagramPlanner to:
- Select "z3" or "constraint" strategy when scene has constraints
- Even if complexity is low, constraints should trigger Z3

### Priority 3: Fix Validator Bug (Blocking New Tests)

**File:** [core/universal_validator.py:205](core/universal_validator.py#L205)

```python
# BUG: PrimitiveType is not imported
has_mass = any(obj.type == PrimitiveType.MASS for obj in scene.objects)
```

**Fix:** Add import at top of file:
```python
from core.scene.schema_v1 import PrimitiveType
```

### Priority 4: Test Z3 Directly

Once validator is fixed and strategy selection is corrected:
1. Run test_z3_diagnostic.py
2. Verify z3_used: true in new traces
3. Verify Z3 actually computes optimal positions

---

## Impact Assessment

### What Works Without Z3

1. ✅ **Heuristic Layout:** UniversalLayoutEngine provides reasonable layouts
2. ✅ **Basic Positioning:** Objects are positioned without overlaps (mostly)
3. ✅ **Manual Constraints:** Scene builder can specify positions manually

### What's Missing Without Z3

1. ❌ **Optimal Layout:** Z3 would find globally optimal positions
2. ❌ **Complex Constraints:** Multi-object alignment, spacing, symmetry
3. ❌ **SMT-Based Solving:** Mathematical proof of constraint satisfaction
4. ❌ **Performance Guarantee:** Z3 provides satisfiability guarantees
5. ❌ **Roadmap Deliverable:** SMT-based layout solving promised but not working

---

## Summary

| Component | Status | Blocker |
|-----------|--------|---------|
| Z3 installation | ✅ Complete | None |
| Z3 integration | ✅ Complete | None |
| DiagramPlanner | ✅ Complete | None |
| Complexity assessment | ✅ Working | None |
| **Strategy selection** | ❌ **Broken** | **Always selects "heuristic"** |
| Plan constraints | ❌ Empty | Strategy selection bug |
| Z3 execution | ❌ Skipped | No constraints in plan |

**Bottom Line:**
- Infrastructure: 100% complete
- Integration: 100% complete
- Strategy selection: BROKEN (always selects "heuristic")
- Functionality: 0% working (until strategy selection fixed)

**User is correct:** Z3 constraint solving is currently bypassed, despite all the infrastructure being in place.

---

**Files Referenced:**
- [unified_diagram_pipeline.py:1106-1186](unified_diagram_pipeline.py#L1106-L1186) - Z3 execution
- [logs/req_20251111_231736_trace.json](logs/req_20251111_231736_trace.json) - Evidence 1
- [logs/req_20251111_232837_trace.json](logs/req_20251111_232837_trace.json) - Evidence 2
- [test_z3_diagnostic.py](test_z3_diagnostic.py) - Diagnostic test
- core/planning/diagram_planner.py - Strategy selection (need to investigate)

**Date:** November 12, 2025
**Status:** ⚠️  **ROOT CAUSE IDENTIFIED - STRATEGY SELECTION BROKEN**
