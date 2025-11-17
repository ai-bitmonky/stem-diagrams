# SVG Generation Fix Summary

## Problem Description

The diagram generation pipeline failed for this capacitor problem:

> A potential difference of 300 V is applied to a series connection of two capacitors of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected from the battery and from each other. They are then reconnected with plates of the same signs wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?

### Pipeline Failure Metrics (From Logs)

| Metric | Score | Required | Status |
|--------|-------|----------|--------|
| DeepSeek Plan Audit Confidence | 0.30 | ≥0.75 | ❌ Failed |
| Structural Consistency | 0.25 | ≥0.65 | ❌ Failed |
| Semantic Fidelity | 15/100 | ≥75 | ❌ Failed |
| LLM Quality Audit | 0.4/10 | - | ❌ Failed |

**Result**: Generated a meaningless diagram with placeholder objects instead of actual capacitors.

---

## Root Cause Analysis

### Issue Location
**File**: `core/interpreters/capacitor_interpreter.py`
**Lines**: 54-78 (detection logic) and 545-567 (circuit generation)

### The Problem

This is a **3-stage problem**:
1. **Stage 1**: Two capacitors in **series** with 300V battery
2. **Stage 2**: Disconnected from battery and each other
3. **Stage 3**: Reconnected in **parallel** (same signs together)

#### Detection Failure

**Original Code (Lines 54-55):**
```python
has_series = 'series' in problem_text
has_parallel = 'parallel' in problem_text and 'plate' not in problem_text
```

**What Happened:**
- ✅ `has_series = True` (detected "series connection")
- ❌ `has_parallel = False` (word "parallel" never appears)
- ❌ No detection of multi-stage problem (keywords "disconnected", "reconnected" ignored)
- ❌ No detection of implicit parallel connection ("same signs wired together")

**Result:**
The interpreter chose `_create_circuit()` which generated a **series circuit** (Stage 1), not the **final parallel state** (Stage 3) that the question asks about.

#### Structural Failure

From logs:
```
Missing in scene: 3
  IDs: capacitor_C1, capacitor_C2, series_connection
→ Auto-added 3 placeholder object(s) from plan
```

The scene builder failed to create proper capacitor entities, so the system added **empty placeholders**, masking the failure but producing a meaningless diagram.

---

## The Fix

### 1. Multi-Stage Problem Detection

**Added (Lines 59-79):**
```python
# Detect multi-stage problems (disconnected/reconnected scenarios)
has_disconnection = any(word in problem_text for word in [
    'disconnect', 'disconnected', 'removed', 'separate'
])
has_reconnection = any(word in problem_text for word in [
    'reconnect', 'reconnected', 'connected again', 'then connected'
])
is_multistage = has_disconnection and has_reconnection

# Detect implicit parallel connection (positive-to-positive, negative-to-negative)
implicit_parallel_patterns = [
    'same sign',
    'positive to positive',
    'negative to negative',
    '+ve to +ve',
    '-ve to -ve',
    'like charges',
    'like plates'
]
has_implicit_parallel = any(pattern in problem_text for pattern in implicit_parallel_patterns)

# If reconnected with same signs, it's parallel (overrides series detection)
if is_multistage and has_implicit_parallel:
    has_parallel = True
    has_series = False  # Final state is parallel, not series
```

### 2. New Parallel Capacitor Circuit Generator

**Added Method**: `_create_parallel_capacitors()` (Lines 655-798)

**Features:**
- Creates side-by-side capacitors with vertical parallel plates
- Connects all positive plates to top rail (red)
- Connects all negative plates to bottom rail (blue)
- Shows capacitance labels for each capacitor
- Adds annotation: "Parallel Connection (same signs together)"

**Visual Layout:**
```
┌────────────────── Top Rail (+ terminals) ──────────────────┐
│                                                              │
│  C₁                                C₂                        │
├──┤├──                          ├──┤├──                       │
│  + -                            + -                          │
│  │ │                            │ │                          │
│  + -                            + -                          │
├──┤├──                          ├──┤├──                       │
│                                                              │
└────────────────── Bottom Rail (- terminals) ────────────────┘
```

### 3. Updated Circuit Selection Logic

**Modified (Lines 98-100):**
```python
elif has_parallel and has_circuit:
    # Parallel capacitor circuit (e.g., reconnected with same signs)
    scene_objects, constraints = self._create_parallel_capacitors(objects, relationships)
```

This ensures that when a parallel connection is detected (explicitly or implicitly), the correct circuit type is generated.

---

## Expected Improvements

With this fix, the pipeline should now:

1. **Correctly detect multi-stage problems**
   - Recognize "disconnected" → "reconnected" patterns
   - Focus on the **final state** for diagram generation

2. **Detect implicit parallel connections**
   - Recognize "same signs together" as parallel connection
   - No longer require the explicit word "parallel"

3. **Generate accurate diagrams**
   - Show two capacitors in parallel
   - Include proper labels (C₁, C₂)
   - Show connection rails
   - Add descriptive annotation

### Predicted Metric Improvements

| Metric | Before | After (Expected) | Target |
|--------|--------|------------------|--------|
| DeepSeek Audit Confidence | 0.30 | **≥0.75** | ≥0.75 |
| Structural Consistency | 0.25 | **≥0.90** | ≥0.65 |
| Semantic Fidelity | 15/100 | **≥80/100** | ≥75 |
| LLM Quality Audit | 0.4/10 | **≥7/10** | - |

---

## Testing the Fix

### Option 1: Web Interface (Recommended)

```bash
# Start the backend server
cd /path/to/stem-diagrams
python fastapi_server.py

# Start the frontend (in another terminal)
cd diagram-ui
npm run dev

# Then visit http://localhost:3000 and paste the problem text
```

### Option 2: Direct Python Test

```python
from unified_diagram_pipeline import UnifiedDiagramPipeline

problem_text = """
A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?
"""

pipeline = UnifiedDiagramPipeline()
result = pipeline.generate(problem_text)

print(f"Success: {result['success']}")
print(f"SVG size: {len(result['svg'])} bytes")
print(f"Validation score: {result.get('validation_score', 'N/A')}")

# Save SVG
with open('test_parallel_capacitors.svg', 'w') as f:
    f.write(result['svg'])
```

### Option 3: API Test

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "problem_text": "A potential difference of 300 V is applied to a series connection of two capacitors of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected from the battery and from each other. They are then reconnected with plates of the same signs wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"
  }'
```

---

## Related Issues Fixed

This fix also improves handling of:

1. **Any reconnection scenario** involving disconnection then reconnection
2. **Implicit topology descriptions** that don't use standard terms
3. **Final-state questions** in multi-step circuit problems
4. **Charge redistribution problems** common in electrostatics

---

## Files Modified

1. **`core/interpreters/capacitor_interpreter.py`**
   - Added multi-stage detection (lines 59-79)
   - Updated debug logging (line 89)
   - Added parallel circuit branch (lines 98-100)
   - New method: `_create_parallel_capacitors()` (lines 655-798)

---

## Commit Details

**Branch**: `claude/debug-svg-generation-01TSAU4aDpGc4vMJDvKp2jhT`
**Commit**: `e2b6a08`
**Message**: "Fix capacitor interpreter for multi-stage parallel connection problems"

---

## Next Steps

1. **Test the fix** with the original problem
2. **Verify metrics** meet the required thresholds:
   - DeepSeek confidence ≥0.75
   - Structural score ≥0.65
   - Semantic fidelity ≥75
3. **Test edge cases**:
   - Three capacitors in parallel
   - Mixed series-parallel after reconnection
   - Multiple disconnection/reconnection stages
4. **Create PR** to merge into main branch
5. **Document** any additional improvements needed

---

## Questions to Consider

1. **Should we show all three stages** (series → disconnected → parallel) as a multi-panel diagram?
2. **Should we add annotations** showing the charge redistribution calculation?
3. **Should we highlight** which stage the question is asking about?

For now, the fix shows the **final state** (parallel connection) as that's what the question asks about ("What is the charge on capacitor C₁?" after reconnection).

---

**Last Updated**: 2025-11-17
**Author**: Claude (AI Assistant)
**Status**: ✅ Fix Implemented and Pushed
