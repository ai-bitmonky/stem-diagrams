# Pipeline Architecture Audit Report

**Date:** November 11, 2025
**Status:** 🚨 CRITICAL GAPS IDENTIFIED
**Triggered By:** HTML trace analysis revealing feature stubs

---

## Executive Summary

The logging system successfully exposed a **critical architecture problem**: many features marked as `[ACTIVE]` in the pipeline are either:
- Not actually invoked in production code paths
- Stub implementations with TODO comments
- Generate output that's never used downstream
- Exist in isolation without integration

This report documents the gap between **claimed functionality** vs **actual implementation**.

---

## 1. NLP Stack - CLAIMED BUT NOT USED

### Claimed Features (Marked [ACTIVE])
```
✓ Phase 0.5: OpenIE [ACTIVE]
✓ Phase 0.5: Stanza [ACTIVE]
✓ Phase 0.5: DyGIE++ [ACTIVE]
✓ Phase 0.5: SciBERT [ACTIVE]
✓ Phase 0.5: ChemDataExtractor [ACTIVE]
✓ Phase 0.5: MathBERT [ACTIVE]
✓ Phase 0.5: AMR Parser [ACTIVE]
```

### Actual Reality

**File:** [unified_diagram_pipeline.py](unified_diagram_pipeline.py:580-630)

```python
# Lines 580-630: NLP tools ARE called
if 'openie' in self.nlp_tools:
    openie_result = self.nlp_tools['openie'].extract(problem_text)
    nlp_results['openie'] = {...}

if 'stanza' in self.nlp_tools:
    stanza_result = self.nlp_tools['stanza'].enhance(problem_text)
    nlp_results['stanza'] = {...}

if 'scibert' in self.nlp_tools:
    scibert_result = self.nlp_tools['scibert'].embed(problem_text)
    nlp_results['scibert'] = {...}
```

**Problem:** NLP tools ARE invoked BUT their output is **NEVER USED**:
- `nlp_results` dictionary is populated
- Passed to `PipelineResult` object (line 1077)
- **NEVER read or used by any downstream phase**
- No integration with DeepSeek API
- No multi-source understanding or ontology enrichment

**Evidence from Trace:**
```json
{
  "phase_name": "NLP Enrichment",
  "output": {"openie": {...}},  // Generated but unused
  "duration_ms": 0.94
}
```

### Missing Integration

The NLP outputs SHOULD be used for:
1. **Property Graph enrichment** - Currently property graph only uses OpenIE triples superficially
2. **Scene synthesis** - Should inform object detection and relationships
3. **DeepSeek API augmentation** - Should provide context for LLM calls
4. **Ontology validation** - Should verify domain concepts

**Current State:** NLP tools run in isolation, output discarded.

---

## 2. Property Graph - INVOKED BUT NOT PRODUCTIVE

### Claimed Feature
```
✓ Phase 0: PropertyGraph [ACTIVE]
```

### Actual Reality

**File:** [unified_diagram_pipeline.py](unified_diagram_pipeline.py:645-680)

```python
# Lines 645-680: PropertyGraph IS built
if self.property_graph is not None:
    if nlp_results and 'openie' in nlp_results:
        current_property_graph = PropertyGraph()
        for subject, relation, obj in nlp_results['openie']['triples']:
            # Add nodes and edges
            current_property_graph.add_node(subj_node)
            current_property_graph.add_edge(edge)
```

**Problem:** Property graph IS built BUT:
- Only uses OpenIE triples (ignores Stanza entities, SciBERT embeddings, etc.)
- **Graph is NEVER queried or traversed**
- Not used for relationship extraction
- Not used for property propagation
- Not used for semantic queries
- Simply passed to `PipelineResult` and ignored

**Evidence from Trace:**
```json
{
  "phase_name": "Property Graph Construction",
  "output": {
    "nodes": 24,
    "edges": 12
  },
  "duration_ms": 0.5
}
```

**File exists but unused:** [core/property_graph.py](core/property_graph.py:1-700)
- 700 lines of graph infrastructure
- Query methods, traversal algorithms, pattern matching
- **NEVER CALLED from production code**

### Missing Integration

Property graph SHOULD be used for:
1. **Multi-source understanding** - Merge NLP outputs into unified graph
2. **Ontology enrichment** - Link entities to domain ontologies
3. **Relationship inference** - Derive implicit relationships
4. **Scene synthesis** - Inform object placement and connections

**Current State:** Built but never queried.

---

## 3. DiagramPlanner + Z3 Solver - INSTANTIATED BUT NOT USED

### Claimed Features
```
✓ Phase 1+2: DiagramPlanner [ACTIVE]
✓ Phase 5: Z3 Layout Solver [ACTIVE]
```

### Actual Reality

**File:** [unified_diagram_pipeline.py](unified_diagram_pipeline.py:422-463)

```python
# Lines 422-427: DiagramPlanner IS instantiated
if config.enable_diagram_planning and DIAGRAM_PLANNER_AVAILABLE:
    self.diagram_planner = DiagramPlanner()
    print("✓ Phase 1+2: DiagramPlanner [ACTIVE]")

# Lines 461-463: Z3 Solver IS instantiated
if config.enable_z3_optimization and Z3_AVAILABLE:
    self.z3_solver = Z3LayoutSolver()
    print("✓ Phase 5: Z3 Layout Solver [ACTIVE]")
```

**Problem:** Both ARE instantiated BUT:

**DiagramPlanner usage** (Lines 704-705, 739-740):
```python
# Only used for complexity assessment and strategy selection
if self.diagram_planner:
    complexity_score = self.diagram_planner.assess_complexity(specs)
    strategy = self.diagram_planner.select_strategy(specs, complexity_score)
```
- Complexity score is calculated but barely used
- Strategy is selected but not acted upon
- **Planning scaffolding never invoked**

**Z3 Solver usage** (Lines 876-889):
```python
# Z3 is attempted but ALWAYS FAILS OR SKIPPED
if self.z3_solver and self.diagram_planner:
    try:
        plan = self.diagram_planner.create_plan(specs)
        z3_solution = self.z3_solver.solve_layout(plan, object_dims)
        if z3_solution.satisfiable:
            print(f"  Z3 Solution: {len(z3_solution.positions)} positions optimized")
            z3_used = True
    except Exception as e:
        print(f"  Z3 failed, falling back to standard layout: {e}")

# ALWAYS falls back to heuristic layout
positioned_scene = self.layout_engine.solve(scene, specs)
```

**Evidence from Trace:**
```json
{
  "phase_name": "Layout Optimization + Z3",
  "output": {
    "object_count": 12,
    "z3_used": false  // ❌ Z3 NEVER USED
  },
  "duration_ms": 4.44
}
```

### Missing Integration

**Files exist but underutilized:**
- [core/diagram_planner.py](core/diagram_planner.py:1-200) - Planning logic exists
- [core/diagram_plan.py](core/diagram_plan.py:1-200) - Plan data structures
- [core/solvers/z3_layout_solver.py](core/solvers/z3_layout_solver.py:1-210) - SMT solver
- [core/model_orchestrator.py](core/model_orchestrator.py:1-350) - Model selection

**Current State:**
- Complexity assessment runs but results unused
- Planning scaffolding exists but not invoked
- Z3 solver instantiated but always skipped
- Falls back to heuristic layout 100% of the time

---

## 4. Layout Engine - PURELY HEURISTIC (No SMT)

### Claimed Feature
```
✓ Phase 5: Z3 Layout Solver [ACTIVE]
```

### Actual Reality

**File:** [core/universal_layout_engine.py](core/universal_layout_engine.py:1-200)

```python
def solve(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
    """
    Solve layout for scene

    Pipeline:
    1. Domain-aware initial placement
    2. Iterative constraint satisfaction (max 50 iterations)
    3. Aesthetic optimization (spacing, alignment)
    4. Intelligent label placement
    5. Final validation
    """
    # Step 1: Domain-aware initial placement
    self._initial_placement(scene, spec)

    # Step 2: Iterative constraint satisfaction
    iterations = self._solve_constraints(scene)

    # Step 3: Aesthetic optimization
    self._optimize_aesthetics(scene, spec)
```

**Problem:** Layout is **100% heuristic-based**:
- No SMT solver integration
- No constraint verification loop
- No satisfiability checking
- Simple iterative refinement

### Missing Implementation

Layout SHOULD use:
1. **Staged planning** - DiagramPlanner → DiagramPlan → Z3 solver
2. **Constraint formulation** - Convert scene constraints to Z3 constraints
3. **Optimization objectives** - Minimize overlap, maximize clarity
4. **Post-layout verification** - Check constraint satisfaction

**Current State:** Pure heuristics, no formal verification.

---

## 5. Validation - LARGELY STUBBED

### Claimed Features
```
✓ Phase 3: Ontology Validation [ACTIVE]
✓ Phase 7: DiagramValidator [ACTIVE]
✓ Phase 7: VLMValidator [ACTIVE]
```

### Actual Reality

**File:** [core/universal_validator.py](core/universal_validator.py:1-200)

```python
# Lines 371-382: TODO stubs
def _validate_units(self, scene: Scene, spec: CanonicalProblemSpec) -> ValidationReport:
    pass  # TODO: Implement unit validation

def _validate_equilibrium(self, scene: Scene, spec: CanonicalProblemSpec) -> ValidationReport:
    # TODO: Verify sum of forces = 0
    pass

def _validate_circuit_laws(self, scene: Scene, spec: CanonicalProblemSpec) -> ValidationReport:
    # TODO: Implement circuit law validation
    pass
```

**File:** [unified_diagram_pipeline.py](unified_diagram_pipeline.py:1110-1130)

```python
def _post_validate(self, svg: str, scene: Scene, problem_text: str) -> Dict:
    """Phase 7: AI-based quality validation (structural + visual-semantic)"""

    validation_results = {
        'structural': None,
        'visual_semantic': None,
        'overall_confidence': 0.0,
        'issues': [],
        'suggestions': []
    }

    # Structural/Quality validation with DiagramValidator
    if self.diagram_validator:
        try:
            quality_score = self.diagram_validator.validate(scene)
            validation_results['structural'] = {...}  // Returns scores but no refinement
```

**Problem:**
- Validation runs but **returns dummy/fixed data**
- No structural validation loop
- No semantic validation
- No VLM validation (visual quality checking)
- No refinement loop based on validation results

### Missing Implementation

Validation SHOULD include:
1. **Structural validation** - Scene graph completeness, connectivity
2. **Semantic validation** - Domain rules, physics constraints
3. **Visual validation** - VLM-based quality assessment
4. **Refinement loop** - Fix issues and re-validate
5. **Multi-stage QA** - Progressive refinement

**Current State:** Validation scores returned but never acted upon.

---

## 6. Model Orchestrator - NOT WIRED

### Claimed Feature
```
✓ Model Orchestrator [ACTIVE]
```

### Actual Reality

**File:** [core/model_orchestrator.py](core/model_orchestrator.py:1-350)
- Defines `HybridModelOrchestrator` class
- Has logic for model selection (DeepSeek, Claude, GPT-4)
- Routing based on task complexity

**Problem:**
- **NEVER INSTANTIATED in production code paths**
- All LLM calls go directly to DeepSeek
- No hybrid model selection
- No task-based routing

**Search results:**
```bash
grep -r "ModelOrchestrator\|model_orchestrator" unified_diagram_pipeline.py
# No results - never imported or used
```

### Missing Integration

Model orchestrator SHOULD:
1. **Route tasks** - Simple → DeepSeek, Complex → Claude/GPT-4
2. **Optimize costs** - Use cheaper models for routine tasks
3. **Fallback logic** - Retry with different models on failure

**Current State:** Code exists but completely unused.

---

## 7. Symbolic Reasoning - MISSING ENTIRELY

### Claimed Capability
Pipeline documentation mentions:
- SymPy geometry engine
- Physics simulation
- Circuit rule checker

### Actual Reality

**Search results:**
```bash
grep -r "sympy\|SymPy" core/
# No results

grep -r "physics.*simul" core/
# No results

grep -r "circuit.*checker" core/
# No circuit validation beyond stubs
```

**Problem:** No symbolic reasoning engines exist:
- No SymPy integration
- No geometry verification
- No physics simulation
- No circuit analysis

### Missing Implementation

Should have:
1. **SymPy geometry** - Verify spatial relationships
2. **Physics engine** - Check force balance, energy conservation
3. **Circuit analyzer** - Verify KCL/KVL, current flow

**Current State:** Completely missing.

---

## 8. Electronics Support - MISSING

### Claimed Capability
Support for circuit diagrams mentioned in roadmap

### Actual Reality

**Search results:**
```bash
grep -r "schemdraw\|circuitikz" .
# No results

ls domains/electronics/
# Directory exists but no SchemDraw/CircuitikZ integration
```

**Problem:** No electronics rendering:
- No SchemDraw integration
- No CircuitikZ support
- Basic SVG shapes only

### Missing Implementation

Should have:
1. **SchemDraw** - Professional circuit diagrams (Python)
2. **CircuitikZ** - LaTeX-based circuit rendering
3. **Component library** - Resistors, capacitors, inductors, etc.

**Current State:** Generic shapes only, no circuit-specific rendering.

---

## Summary Table: Claimed vs Actual

| Feature | Status | Code Location | Issue |
|---------|--------|---------------|-------|
| **NLP Stack** | ❌ **Unused** | [unified_diagram_pipeline.py](unified_diagram_pipeline.py:580-630) | Tools run, output discarded |
| **Property Graph** | ⚠️ **Built but not queried** | [core/property_graph.py](core/property_graph.py:1-700) | Graph created, never traversed |
| **DiagramPlanner** | ⚠️ **Partially used** | [core/diagram_planner.py](core/diagram_planner.py:1-200) | Only complexity assessment |
| **Z3 Solver** | ❌ **Never runs** | [core/solvers/z3_layout_solver.py](core/solvers/z3_layout_solver.py:1-210) | Always falls back to heuristics |
| **Layout Engine** | ⚠️ **Heuristic only** | [core/universal_layout_engine.py](core/universal_layout_engine.py:1-200) | No SMT solving |
| **Validation** | ⚠️ **Stubbed** | [core/universal_validator.py](core/universal_validator.py:371-382) | TODO comments, no refinement |
| **Model Orchestrator** | ❌ **Not wired** | [core/model_orchestrator.py](core/model_orchestrator.py:1-350) | Never instantiated |
| **SymPy Geometry** | ❌ **Missing** | N/A | Doesn't exist |
| **Physics Simulation** | ❌ **Missing** | N/A | Doesn't exist |
| **Circuit Checker** | ❌ **Missing** | N/A | Doesn't exist |
| **SchemDraw/CircuitikZ** | ❌ **Missing** | N/A | Doesn't exist |

---

## Impact Assessment

### High Priority (Blocking Core Functionality)
1. **NLP → Property Graph → Scene Synthesis pipeline** - Currently broken, data flows but never used
2. **Z3 Solver integration** - Claims constraint-based layout but uses heuristics
3. **Validation refinement loop** - Validates but never fixes issues

### Medium Priority (Claimed but Missing)
4. **Model Orchestrator** - All code exists, just needs wiring
5. **DiagramPlanner full integration** - Partially used, needs planning loop
6. **Property Graph querying** - Built but never queried

### Low Priority (Future Enhancements)
7. **SymPy geometry verification** - Net new feature
8. **Physics simulation** - Net new feature
9. **Electronics rendering** - Net new feature

---

## Root Cause Analysis

### Why This Happened

1. **Feature Completeness Illusion**
   - Code exists → marked as [ACTIVE]
   - Integration never completed
   - No end-to-end testing

2. **Logging Revealed Truth**
   - Trace shows phases execute quickly (sub-millisecond)
   - Output is generated but never consumed
   - No downstream dependencies

3. **Missing Integration Points**
   - Components exist in isolation
   - No data flow between phases
   - No verification of feature usage

---

## Verification Commands

Run these to confirm findings:

```bash
# 1. Check if NLP outputs are used anywhere
grep -r "nlp_results\[" unified_diagram_pipeline.py core/
# Result: Only stored, never read

# 2. Check if property graph is queried
grep -r "property_graph\.query\|property_graph\.find" unified_diagram_pipeline.py core/
# Result: Never queried

# 3. Check Z3 usage in latest trace
python3 -c "
import json
with open('logs/req_20251111_212251_trace.json') as f:
    trace = json.load(f)
    for p in trace['phases']:
        if 'Layout' in p['phase_name']:
            print(f'Z3 used: {p[\"output\"].get(\"z3_used\", False)}')
"
# Result: z3_used: false

# 4. Check for SymPy usage
grep -r "import sympy\|from sympy" core/
# Result: Not found
```

---

## Next Steps

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for prioritized fix plan.
