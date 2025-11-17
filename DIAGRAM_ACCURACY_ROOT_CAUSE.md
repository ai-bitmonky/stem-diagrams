# Diagram Accuracy Root Cause Analysis

**Date:** November 17, 2025
**Latest Request:** req_20251117_094636
**Problem:** Diagrams are not accurate - missing power sources, nonsensical objects

---

## Critical Finding: DeepSeek JSON Import Bug Still Present

### Issue

The **duplicate `import json`** bug that was supposedly fixed in the previous session was **NEVER committed** to the repository. The fix exists in documentation (DEEPSEEK_JSON_IMPORT_FIX.md) but **NOT in the actual code**.

**Evidence from logs/req_20251117_094636.log:**
```
2025-11-17 09:47:31 | INFO     | PHASE 1: DeepSeek Enrichment
2025-11-17 09:47:31 | INFO     | Phase Output:
2025-11-17 09:47:31 | INFO     | Summary: DeepSeek entity enrichment
2025-11-17 09:47:31 | INFO     |   error: cannot access local variable 'json' where it is not associated with a value
2025-11-17 09:47:31 | INFO     | Phase completed: WARNING
```

### Root Cause

**File:** [core/deepseek_llm_adapter.py](core/deepseek_llm_adapter.py)

**Duplicate imports found at:**
- Line 247: `import json` (inside `enrich_entities()`)
- Line 325: `import json` (inside `audit_plan()`)
- Line 415: `import json` (inside `validate_semantic_fidelity()`)

**Missing:** Module-level `import json` statement

**Python Scoping Issue:** When `import json` appears inside a function, Python treats `json` as a local variable. However, the import hasn't executed yet when `json.loads()` is called, causing the error:
```python
cannot access local variable 'json' where it is not associated with a value
```

### Impact

**ALL 3 DeepSeek phases are failing:**
- ❌ **Phase 0.6** (Entity Enrichment) - Fails to validate/enrich entities from NLP
- ❌ **Phase 4.5** (Plan Auditing) - Fails to audit diagram plan
- ❌ **Phase 6.5** (Semantic Validation) - Fails to validate final diagram

**This is catastrophic** because DeepSeek is the ONLY component that can:
1. Filter out nonsensical NLP extractions
2. Identify missing implied components (like batteries)
3. Validate diagram correctness

---

## Cascade Effect: Garbage NLP Entities

### What NLP Extracted

From trace file analysis:

**Entities extracted by OpenIE/Stanza/spaCy:**
```
- "300 V"
- "a series"
- "They are"
- "plates of"
- "What is"
- "capacitor C₁"
- "Capacitor"
- "What"
- "applied to"
- "a"
- "connection of"
- "is applied on"
- "is applied"
- "is"
- "then reconnected on"
- "the charge on"
- "is the charge"
- "is"
- "series"
```

**Analysis:**
- ✅ Valid entities: "300 V", "capacitor C₁", "Capacitor" (3/19 = 16% accuracy)
- ❌ Garbage entities: "They are", "What is", "is applied", "a", "is" (16/19 = 84% junk)

### Why Garbage Wasn't Filtered

**Normal Flow (When DeepSeek Works):**
```
NLP Extraction → Property Graph → DeepSeek Enrichment → Filtered Entities
                                   ↑
                                   Removes nonsense
                                   Adds missing components
                                   Validates entity types
```

**Actual Flow (DeepSeek Broken):**
```
NLP Extraction → Property Graph → ❌ DeepSeek Fails → Garbage Goes to Scene Builder
                                   ↑
                                   JSON import error
                                   No filtering
                                   No enrichment
```

---

## Missing Power Source

### Problem Text Analysis

**Original problem:**
> "A potential difference of 300 V is applied to a series connection of two capacitors..."

**Implied Component:** Battery/Voltage Source (300V)

**Why It's Missing:**
1. **NLP extractors are literal** - They only extract explicitly mentioned entities
2. **Passive voice hides the battery** - "is applied" doesn't explicitly mention a battery
3. **DeepSeek should infer the battery** - But it's failing due to JSON import error

### DeepSeek's Role

**Phase 0.6 Entity Enrichment should:**
```json
{
  "enriched_entities": [...],
  "missing_entities": [
    {
      "type": "voltage_source",
      "label": "Battery (300V)",
      "inferred_from": "A potential difference of 300 V is applied",
      "reason": "Passive voice implies power source"
    }
  ],
  "corrections": [...],
  "removed_entities": [
    {
      "original": "They are",
      "reason": "Not a physical component"
    },
    {
      "original": "What is",
      "reason": "Question phrase, not entity"
    }
  ]
}
```

**But it returns:**
```json
{
  "error": "cannot access local variable 'json' where it is not associated with a value"
}
```

---

## Scene Building Consequences

### Current Scene Objects (7 objects)

**From logs:**
```
Phase Output: Scene with 7 objects
  object_count: 7
  selected_strategy: constraint_based
```

**Likely Contents:**
- 2 capacitors (C₁ = 2 μF, C₂ = 8 μF) - ✅ Valid
- ~5 garbage objects like "What is", "They are", "is applied" - ❌ Invalid
- 0 power sources - ❌ **CRITICAL MISSING**

### Domain Rule Validation Results

**From trace file:**
```json
{
  "domain": "current_electricity",
  "checks": [
    {
      "name": "Kirchhoff Loop",
      "passed": false,
      "severity": "error",
      "details": "No power source detected in circuit graph"
    },
    {
      "name": "Power Source Presence",
      "passed": false,
      "severity": "error",
      "details": "No power source objects"
    }
  ],
  "errors": 2,
  "warnings": 0
}
```

**Analysis:** Domain rules are **correctly identifying** the structural problems, but these errors come too late in the pipeline to fix the diagram.

---

## Fix Applied (This Session)

### Changes Made

**File:** [core/deepseek_llm_adapter.py](core/deepseek_llm_adapter.py)

1. **Added module-level import** (line 21):
   ```python
   import json
   ```

2. **Removed duplicate imports:**
   - Line 247: Removed `import json` from `enrich_entities()`
   - Line 325: Removed `import json` from `audit_plan()`
   - Line 415: Removed `import json` from `validate_semantic_fidelity()`

### Verification

```bash
$ python3 -m py_compile core/deepseek_llm_adapter.py
# ✅ No errors

$ grep -n "import json" core/deepseek_llm_adapter.py
21:import json
# ✅ Only one import at module level
```

---

## Expected Improvement After Fix

### Phase 0.6 Output (After Fix)

**Expected successful enrichment:**
```
✅ DeepSeek enriched 2 entities (capacitors)
ℹ️  Identified 1 missing entity (battery)
✏️  Made 16 corrections (removed garbage entities)
🗑️  Removed 16 invalid entities
💰 API cost: $0.0004-0.0008
```

### Scene Building (After Fix)

**Expected objects:**
```
Scene with 3 objects:
  - Battery (300V) - ✅ Added by DeepSeek
  - Capacitor C₁ (2 μF) - ✅ Validated by DeepSeek
  - Capacitor C₂ (8 μF) - ✅ Validated by DeepSeek
```

### Domain Validation (After Fix)

**Expected:**
```
Domain rule evaluation:
  - Kirchhoff Loop: ✅ PASSED (circuit has battery)
  - Power Source Presence: ✅ PASSED (1 power source)
  errors: 0
  warnings: 0
```

---

## Why This Wasn't Caught Earlier

### Previous Session (November 15)

**What we thought happened:**
1. Fixed duplicate `import json` in deepseek_llm_adapter.py ✅
2. Verified with syntax check ✅
3. Committed fix to git ✅

**What actually happened:**
1. Fixed duplicate `import json` in deepseek_llm_adapter.py ✅
2. Verified with syntax check ✅
3. ❌ **FIX WAS NEVER COMMITTED TO GIT**
4. ❌ **Server was never restarted to pick up changes**

**The commit on Nov 15 included:**
- ✅ OUTSTANDING_ISSUES_RESOLVED.md (documentation)
- ✅ core/nlp_tools/spacy_extractor.py (new file)
- ✅ core/ontology/ontology_manager.py (URI serialization fix)
- ✅ fastapi_server.py (HuggingFace warning fix)
- ❌ **core/deepseek_llm_adapter.py (NOT INCLUDED)**

### Git Status Check

```bash
$ git status
Changes not staged for commit:
  modified:   core/deepseek_llm_adapter.py  # ← This file was MODIFIED but NEVER COMMITTED
```

---

## Action Items

### Immediate Actions (CRITICAL)

1. ✅ **Fix applied** - Added module-level `import json`, removed duplicates
2. ⏳ **Commit changes** - Add deepseek_llm_adapter.py to git
3. ⏳ **Restart server** - Reload Python modules to pick up fix
4. ⏳ **Test diagram generation** - Verify DeepSeek phases work
5. ⏳ **Verify output quality** - Check for battery in circuit diagrams

### Verification Commands

```bash
# 1. Commit the fix
git add core/deepseek_llm_adapter.py
git commit -m "Fix DeepSeek JSON import bug - add module-level import, remove duplicates"

# 2. Restart server
# (Kill existing server, then:)
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload

# 3. Test diagram generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"problem_text": "A potential difference of 300 V is applied to a series connection of two capacitors of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF."}'

# 4. Check logs for DeepSeek success
grep "DeepSeek" logs/req_*.log | tail -20
```

### Long-term Improvements

1. **Add integration tests** - Test DeepSeek phases with sample circuits
2. **Add pre-commit hooks** - Prevent commits that skip modified files
3. **Improve NLP filtering** - Add heuristics to filter garbage entities before DeepSeek
4. **Add circuit-specific patterns** - Regex patterns to detect implied components

---

## Summary

**Root Cause:** Duplicate `import json` statements in deepseek_llm_adapter.py causing Python scoping error

**Impact:** All 3 DeepSeek enrichment phases failing → No entity validation → Garbage NLP entities → Missing power sources → Invalid diagrams

**Fix Status:** ✅ **Code fixed** (this session) → ⏳ **Needs commit + server restart**

**Expected Result:** After server restart, DeepSeek will filter garbage entities and add missing battery, resulting in accurate circuit diagrams.

---

**Next Step:** Commit the fix and restart the server to verify diagram accuracy improves.
