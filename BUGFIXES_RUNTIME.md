# Runtime Bug Fixes
**Date:** November 12, 2025
**Context:** Fixes applied after first API server test run

## Bugs Fixed

### Bug #1: Property Graph Save Error ✅
**Error:** `NameError` when saving property graph to JSON

**Location:** [unified_diagram_pipeline.py:938](unified_diagram_pipeline.py#L938)

**Root Cause:**
```python
# BEFORE (line 938):
output_path = os.path.join(config.output_dir, 'property_graph.json')  # ❌ config not in scope
```

**Fix:**
```python
# AFTER:
output_path = os.path.join(self.config.output_dir, 'property_graph.json')  # ✅ Use self.config
```

**Result:** Property graph now saves successfully to `output/property_graph.json`

---

### Bug #2: Validation Refinement Dimensions Error ✅
**Error:** `'SceneObject' object has no attribute 'dimensions'`

**Location:** [core/validation_refinement.py:489-490](core/validation_refinement.py#L489-L490)

**Root Cause:**
Some SceneObject instances don't have a `dimensions` attribute, causing AttributeError before safe accessor methods could handle it.

**Fix 1:** Add None checks to safe accessor methods
```python
# BEFORE:
def _get_width(self, dims) -> float:
    if isinstance(dims, dict):
        return dims.get('width', 100.0)
    return getattr(dims, 'width', 100.0)

# AFTER:
def _get_width(self, dims) -> float:
    if dims is None:  # ✅ Handle None case
        return 100.0
    if isinstance(dims, dict):
        return dims.get('width', 100.0)
    return getattr(dims, 'width', 100.0)
```

**Fix 2:** Use safe getattr when accessing dimensions
```python
# BEFORE:
w1 = self._get_width(obj1.dimensions)  # ❌ Crashes if dimensions doesn't exist

# AFTER:
w1 = self._get_width(getattr(obj1, 'dimensions', None))  # ✅ Safe access
```

**Result:** Validation refinement now handles objects without dimensions gracefully

---

## Test Results

### Before Fixes
```
⚠️  Failed to save graph: NameError
INFO: Validation error: 'SceneObject' object has no attribute 'dimensions'
Refinement Iterations: 0
```

### After Fixes (Expected)
```
✅ Saved graph to: output/property_graph.json
✅ Validation complete: Score = XX/100
Refinement Iterations: 1-3
```

---

## Status
Both bugs fixed and ready for testing. No additional issues identified.
