# Diagram Generation Issue Report

**Date**: November 10, 2025
**Issue**: All generated diagrams are identical
**Status**: ⚠️ **ROOT CAUSE IDENTIFIED**

---

## Summary

After fixing the bugs in `unified_diagram_pipeline.py`, all 5 batch 2 questions generate successfully with advanced features enabled, BUT all diagrams are identical (same MD5 hash).

---

## What's Working ✅

The advanced pipeline features ARE working correctly:

| Question | Complexity | Strategy | Objects | Constraints | Triples | Graph Nodes |
|----------|------------|----------|---------|-------------|---------|-------------|
| Q6 | 0.32 | symbolic_physics | 8 | 1 | 8 | 10 |
| Q7 | 0.39 | constraint_based | 11 | 2 | 12 | 7 |
| Q8 | 0.34 | symbolic_physics | 5 | 5 | 5 | 9 |
| Q9 | 0.38 | constraint_based | 12 | 1 | 10 | 9 |
| Q10 | 0.34 | symbolic_physics | 2 | 7 | 13 | 10 |

**Observations**:
- ✅ **Different complexity scores** (0.32 to 0.39)
- ✅ **Different strategies selected** (symbolic_physics vs constraint_based)
- ✅ **Different object counts** (2 to 12 objects detected)
- ✅ **Different constraint counts** (1 to 7 constraints)
- ✅ **Different NLP extraction** (5 to 13 triples)
- ✅ **Different property graphs** (7 to 10 nodes)

**The advanced analysis IS differentiating the problems correctly!**

---

## What's NOT Working ❌

Despite all the different analyses, **the final SVG output is identical**:

```bash
$ md5 output/batch_2_generated/question_*.svg
MD5 (question_10.svg) = 2dba4d5522249057ea2fd82d90245ddd
MD5 (question_6.svg)  = 2dba4d5522249057ea2fd82d90245ddd
MD5 (question_7.svg)  = 2dba4d5522249057ea2fd82d90245ddd
MD5 (question_8.svg)  = 2dba4d5522249057ea2fd82d90245ddd
MD5 (question_9.svg)  = 2dba4d5522249057ea2fd82d90245ddd
```

**All 5 diagrams are exactly the same**: Generic parallel-plate capacitor with 5 field lines.

---

## Root Cause Analysis

### The Problem

**The Scene Builder doesn't use the extracted information to customize diagrams.**

Pipeline flow:
```
Phase 0: NLP Enrichment → Extracts problem-specific info ✅
Phase 0.5: Property Graph → Builds knowledge graph ✅
Phase 1: Complexity Analysis → Scores complexity ✅
Phase 2: Scene Synthesis → Creates scene... ❌ IGNORES ALL THE ABOVE

⚠️  The CapacitorInterpreter creates a generic capacitor scene
    regardless of what was extracted in previous phases!
```

### Evidence

From the logs, we can see:

**Question 6** (Dielectric Insertion):
- Detected: 8 objects, 1 constraint
- Generated scene: 7 objects (2 plates, 5 field lines)
- **No dielectric slab in the scene!**

**Question 7** (Charge Redistribution - Series Capacitors):
- Detected: 11 objects, 2 constraints
- Generated scene: 7 objects (2 plates, 5 field lines)
- **No series connection, no two separate capacitors!**

**Question 8** (Multiple Dielectrics):
- Detected: 5 objects, 5 constraints
- Generated scene: 7 objects (2 plates, 5 field lines)
- **No multiple dielectric regions!**

**Question 9** (Variable Capacitor Circuit):
- Detected: 12 objects, 1 constraint
- Generated scene: 7 objects (2 plates, 5 field lines)
- **No circuit, no variable capacitor, no C1/C2/C3!**

**Question 10** (Cylindrical Container):
- Detected: 2 objects, 7 constraints
- Generated scene: 7 objects (2 plates, 5 field lines)
- **Should be a cylinder, not parallel plates!**

---

## Why This Happens

The `CapacitorInterpreter` in `core/domain_interpreters/electrostatics_interpreter.py`:

```python
def _interpret_capacitors(self, objects, constraints):
    """
    Interpret capacitor objects
    """
    # Create generic parallel-plate capacitor
    scene_objects = []

    # Always creates:
    # - 2 rectangular plates
    # - 5 field lines between them
    # - Fixed positions

    return scene_objects  # Same every time!
```

**The interpreter has hardcoded logic** - it doesn't actually look at:
- The problem text details (dielectric insertion, series connection, etc.)
- The extracted objects (what type of capacitor, how many, configuration)
- The constraints (spatial relationships)
- The complexity or strategy

It just creates the same generic scene every time.

---

## Architectural Limitation

This is a **fundamental architectural issue**, not a bug:

1. **NLP & Analysis Phases**: Extract rich information about the problem
2. **Scene Building Phase**: **IGNORES** all that information
3. **Layout & Rendering**: Works with whatever scene was built

The pipeline phases are **disconnected** - the extracted information doesn't flow through to scene customization.

---

## Why unified_diagram_pipeline.py Has This Issue

The `unified_diagram_pipeline.py` uses `UniversalSceneBuilder` which delegates to domain interpreters:

```
UniversalSceneBuilder
  ├─ ElectrostaticsInterpreter
  │   └─ CapacitorInterpreter (hardcoded scenes)
  ├─ OpticsInterpreter (hardcoded scenes)
  ├─ MechanicsInterpreter (hardcoded scenes)
  └─ ...
```

Each interpreter has **hardcoded scene templates** and doesn't use the extracted NLP/complexity/strategy information.

---

## Why We Deprecated core/unified_pipeline.py

We deprecated `core/unified_pipeline.py` because it was missing:
- DiagramPlanner
- DiagramAuditor
- ModelOrchestrator
- Ontology validation

**But** it turns out `core/unified_pipeline.py` has the SAME scene building issue - it uses the same `DomainRegistry` with the same hardcoded interpreters!

Both pipelines have this fundamental limitation.

---

## Solutions

### Option 1: Extract Existing Diagrams from HTML ✅ **RECOMMENDED**

The HTML file already has good diagrams embedded:
```html
<div class="problem-diagram">
    <svg viewbox="0 0 2000 1400" xmlns="http://www.w3.org/2000/svg">
    <!-- Well-designed diagram specific to each problem -->
    </svg>
</div>
```

**Advantages**:
- Diagrams already exist and are correct
- Specific to each problem
- Professional quality
- No generation bugs

**Extract script**:
```python
from bs4 import BeautifulSoup

html = open('batch_2_questions.html').read()
soup = BeautifulSoup(html, 'html.parser')

for i, svg in enumerate(soup.find_all('svg'), start=6):
    with open(f'question_{i}.svg', 'w') as f:
        f.write(str(svg))
```

### Option 2: Fix Scene Interpreters 🔧 **MAJOR REWORK**

Make interpreters use extracted information:

**Required Changes**:
1. Modify `CapacitorInterpreter` to parse problem specifics:
   - Detect "dielectric insertion" → add dielectric slab
   - Detect "series connection" → create multiple capacitors
   - Detect "variable capacitor" → add circuit elements
   - Detect "cylindrical" → use cylinder instead of plates

2. Pass NLP results to interpreters:
   - Currently: `interpreter.interpret(objects, constraints)`
   - Needed: `interpreter.interpret(objects, constraints, nlp_results, complexity, strategy)`

3. Create scene variations based on strategy:
   - symbolic_physics → Simplified symbolic diagram
   - constraint_based → Detailed geometric diagram

**Estimated Effort**: 20-30 hours to rework all interpreters

### Option 3: Use LLM for Scene Generation 🤖 **FUTURE WORK**

Use LLM to generate scene descriptions from problem text:

```python
def generate_scene_with_llm(problem_text, complexity, nlp_results):
    prompt = f"""
    Problem: {problem_text}
    Complexity: {complexity}
    Extracted Info: {nlp_results}

    Generate a scene description with specific objects and layouts.
    """
    scene_desc = llm.generate(prompt)
    scene = parse_scene_description(scene_desc)
    return scene
```

**Requires**: LLM API access (DeepSeek, GPT-4, etc.)

---

## Recommendation

### For Immediate Use: Option 1 (Extract from HTML)

The HTML already has correct, problem-specific diagrams. Extract them:

```bash
# Simple extraction script
python3 extract_diagrams_from_html.py batch_2_questions.html
```

**Result**:
- 5 unique, correct diagrams
- Specific to each problem
- Professional quality
- No bugs or limitations

### For Future Development: Option 2 or 3

If the goal is to have a working generation pipeline:
- **Option 2**: Rework interpreters (20-30 hours)
- **Option 3**: LLM-based generation (requires API)

---

## Conclusion

**Current State**:
- ✅ Advanced features working (NLP, complexity, property graphs, strategy)
- ❌ Scene building doesn't use the extracted information
- ❌ All diagrams identical due to hardcoded interpreter logic

**Root Cause**: Architectural limitation in scene interpreter design

**Immediate Solution**: Extract diagrams from HTML (they're already correct)

**Long-term Solution**: Rework scene interpreters to use extracted information

---

**Generated**: November 10, 2025
**Analysis**: Complete
**Recommendation**: Use HTML diagrams for now, rework interpreters later
