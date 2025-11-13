# Known Issues - STEM Diagram Generator UI

## Issue 1: Overlapping Elements in Generated Diagrams

**Status:** Known Limitation
**Severity:** Medium
**Affects:** All problem types

### Description
When generating diagrams through the UI, elements may overlap and the diagrams appear too basic or generic.

### Root Cause
1. **Scene interpreters use hardcoded logic** - They don't fully utilize the extracted NLP/complexity/strategy information
2. **Layout engine over-optimizes** - The constraint solver repositions objects, sometimes causing overlaps
3. **Generic scenes** - All capacitor problems currently generate similar parallel-plate diagrams

### Example
- **Input:** Complex capacitor problem with multiple dielectrics
- **Expected:** Diagram showing different dielectric regions with proper labels
- **Actual:** Basic parallel-plate capacitor with overlapping field lines

### Workarounds

#### Option 1: Use Pre-Generated Diagrams (Recommended)
For batch 2 questions (6-10), use the professionally-designed diagrams that were extracted from HTML:

```bash
# View the correct diagrams
ls output/batch_2_generated/question_*.svg

# These diagrams are:
# - question_6.svg  - Dielectric insertion with battery circuit
# - question_7.svg  - Series capacitor configuration
# - question_8.svg  - Multiple dielectric regions
# - question_9.svg  - Variable capacitor circuit
# - question_10.svg - Cylindrical container capacitor
```

See [BATCH_2_DIAGRAMS_FINAL_STATUS.md](BATCH_2_DIAGRAMS_FINAL_STATUS.md) for details.

#### Option 2: Adjust Layout Settings
Modify the pipeline config to reduce optimization:

```python
# In api_server.py, change:
config = PipelineConfig(
    # ...
    enable_layout_optimization=False,  # Disable to keep initial positions
    # ...
)
```

This will use the initial positions from the interpreter without further optimization.

#### Option 3: Use Specific Problem Keywords
The interpreter detects problem types based on keywords. Include these for better results:

- **Dielectric:** Include "dielectric" and "kappa" or "permittivity"
- **Series circuit:** Include "series connection" and "battery"
- **Cylindrical:** Include "cylindrical" or "cylinder"
- **Variable capacitor:** Include "variable capacitor"

### Long-term Fix (Requires Development)

To properly fix this issue:

1. **Rework scene interpreters** (20-30 hours)
   - Make them use extracted NLP information
   - Create problem-specific scenes based on complexity/strategy
   - Add logic to detect and render specific configurations

2. **Improve layout engine** (10-15 hours)
   - Better handling of pre-positioned objects
   - Smarter overlap detection and resolution
   - Domain-specific layout rules

3. **LLM-based scene generation** (Future)
   - Use LLM to generate scene descriptions
   - Convert descriptions to SceneObjects
   - Validate against physics constraints

### Related Files
- [capacitor_interpreter.py](core/interpreters/capacitor_interpreter.py) - Scene generation logic
- [universal_layout_engine.py](core/universal_layout_engine.py) - Layout optimization
- [DIAGRAM_GENERATION_ISSUE_REPORT.md](DIAGRAM_GENERATION_ISSUE_REPORT.md) - Detailed analysis

---

## Issue 2: Port 5000 Conflict on macOS

**Status:** Fixed
**Severity:** Low

### Description
macOS AirPlay Receiver uses port 5000, causing Flask API to fail on startup.

### Fix
Changed Flask to use port 5001:
- [api_server.py](api_server.py:132) - Updated to `port=5001`
- [.env.local](diagram-ui/.env.local) - Updated to `http://127.0.0.1:5001`

---

## Issue 3: IPv6/IPv4 Connection Issues

**Status:** Fixed
**Severity:** Medium

### Description
Next.js trying to connect via IPv6 (`::1`) while Flask listens on IPv4.

### Fix
- Flask binds to `127.0.0.1` (IPv4 only)
- Next.js API route uses `127.0.0.1` instead of `localhost`
- `.env.local` updated to use `127.0.0.1`

---

## Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Flask API | ✅ Working | Port 5001, IPv4 |
| Next.js UI | ✅ Working | Port 3000 |
| Connection | ✅ Working | Using 127.0.0.1 |
| Pipeline | ✅ Working | All 7 phases active |
| Diagram Quality | ⚠️ Limited | Generic scenes, overlapping |

---

**Last Updated:** November 10, 2025
