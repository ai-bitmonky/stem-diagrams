# Implementation Gap Analysis

**Date:** November 13, 2025
**Status:** ❌ CONFIGURATION ≠ IMPLEMENTATION

## Critical Finding

**Configuration flags are set to `True`, but the actual implementation is INCOMPLETE or NON-FUNCTIONAL.**

The latest trace (`logs/req_20251113_135747_trace.json` and server logs) reveals that enabling the flags does NOT activate the roadmap architecture because:

1. The underlying code is missing or broken
2. Error handlers fall back to heuristics
3. Dependencies are not wired correctly

---

## Layer 1: Text & Diagram Understanding

### Configuration Claims
```python
enable_nlp_enrichment: bool = True  # [MANDATORY]
enable_property_graph: bool = True  # [MANDATORY]
enable_deepseek_enrichment: bool = True  # Roadmap Call #1 [MANDATORY]
```

### Actual Implementation (from trace)

**Phase 0: NLP Enrichment**
```json
{
  "phase_name": "NLP Enrichment",
  "output": {
    "openie": {
      "triples": [
        ["left half", "is filled on", "dielectric κ₁"],
        ["0 and", "bottom on", "κ₃"],
        // ...only 5 triples
      ]
    }
  }
}
```

**Phase 0.5: Property Graph**
```json
{
  "phase_name": "Property Graph Construction",
  "output": {
    "nodes": 6,
    "edges": 3,
    "connected_components": 3
  }
}
```

### Missing Components

❌ **No Multi-Model NLP Chain**
- Missing: spaCy, Stanza, DyGIE++, SciBERT, ChemDataExtractor, MathBERT, AMR
- Only: Single OpenIE pass (5 triples extracted)
- No: FastAPI worker pool for parallel NLP

❌ **No Graph Database Backend**
- Missing: Neo4j/ArangoDB integration
- Missing: PhySH (physics taxonomy) enrichment
- Missing: ChEBI (chemical ontology) enrichment
- Missing: GO (gene ontology) enrichment
- Only: In-memory NetworkX graph discarded after planning

❌ **No Embedding Pipeline**
- Missing: Sentence-Transformers embeddings
- Missing: FAISS/Milvus vector storage
- Missing: Semantic similarity search

❌ **DeepSeek Enrichment**
```
⚠️  DeepSeek initialization failed: Using SOCKS proxy, but the 'socksio' package is not installed.
```
- Status: Enabled in config but **FAILED** at runtime
- Fallback: No enrichment performed
- API Call #1: **NOT EXECUTED**

### Gap Summary
| Component | Config | Implementation | Status |
|-----------|--------|----------------|--------|
| OpenIE | ✅ | ✅ (basic) | Partial |
| spaCy/Stanza/DyGIE++ | ✅ | ❌ | Missing |
| Property Graph | ✅ | ✅ (not persisted) | Partial |
| Neo4j/Arango | ✅ | ❌ | Missing |
| PhySH/ChEBI/GO | ✅ | ❌ | Missing |
| Embeddings | ✅ | ❌ | Missing |
| DeepSeek Enrichment | ✅ | ❌ (crashed) | Broken |

---

## Layer 2: Diagram Planning & Reasoning

### Configuration Claims
```python
enable_strategic_planning: bool = True  # [MANDATORY]
enable_complexity_assessment: bool = True  # [MANDATORY]
enable_model_orchestrator: bool = True
```

### Actual Implementation (from trace)

**Phase 1: Diagram Planning**
```json
{
  "phase_name": "Diagram Planning",
  "output": {
    "entities": 1,  // Only 1 entity: "filled with"
    "relations": 0,
    "constraints": 1,
    "complexity": 0.04,
    "selected_strategy": "heuristic",
    "z3_used": false,
    "sympy_used": false
  }
}
```

**From Server Logs:**
```
Model Orchestrator Strategy: heuristic (complexity 0.04)

Step 2/6: Advanced Constraint Solvers (Z3/SymPy/Cassowary)
   ⚠️  Z3 solver error: 'NoneType' object has no attribute 'objects'
   SymPy solve error: Cannot convert expression to float
   ⚠️  Cassowary solver unavailable – install cassowary to honor alignment constraints
   ℹ️  No advanced solver applied
```

### Missing Components

❌ **No 5-Stage DiagramPlanner**
- Missing: EntityExtractor (extracted only 1 bogus entity "filled with")
- Missing: RelationMapper (0 relations mapped)
- Missing: ConstraintGenerator (only 1 generic constraint)
- Missing: LayoutPlanner (no staged planning, just direct scene synthesis)
- Missing: StyleAssigner (no style planning, uses defaults)

Result: Planning phase extracts 1 useless object, bypasses structured planning entirely.

❌ **No Local LLM Planner**
```python
enable_llm_planning: bool = False  # Phase 1-2: LLM-based diagram planning
```
- Config: Disabled (not mandatory)
- Implementation: Not wired up
- Ollama models: Not used

❌ **No DeepSeek Audit**
```
Phase 10: LLM Quality Auditing
   Auditing skipped: DiagramAuditor.audit() got an unexpected keyword argument 'svg_output'
```
- Config: Enabled (`enable_deepseek_audit = True`)
- Implementation: **CRASHES** with signature error
- API Call #2: **NOT EXECUTED**

❌ **ModelOrchestrator Not Switching**
- Config: `enable_model_orchestrator = True`
- Actual: Always selects "heuristic" strategy
- Never switches to:
  - `constraint_based` (Z3/SymPy)
  - `symbolic_physics` (SymPy geometry)
  - `hierarchical` (tree decomposition)

### Gap Summary
| Component | Config | Implementation | Status |
|-----------|--------|----------------|--------|
| 5-Stage DiagramPlanner | ✅ | ❌ (extracts junk) | Broken |
| EntityExtractor | ✅ | ❌ (1 bogus entity) | Broken |
| RelationMapper | ✅ | ❌ (0 relations) | Broken |
| ConstraintGenerator | ✅ | ❌ (1 generic) | Broken |
| ModelOrchestrator | ✅ | ✅ (always heuristic) | Limited |
| DeepSeek Audit | ✅ | ❌ (signature crash) | Broken |
| Z3 Solver | ✅ | ❌ (NoneType error) | Broken |
| SymPy Solver | ✅ | ❌ (conversion error) | Broken |
| Cassowary | ✅ | ❌ (not installed) | Missing |

---

## Layer 3: Domain Modules & Primitive Library

### Configuration Claims
```python
enable_primitive_library: bool = False  # Not yet fully implemented
primitive_library_backend: str = "milvus"
```

### Actual Implementation

**From Test Results:**
```
✓ Primitive Library: memory backend with 15 primitives [ACTIVE]
```

But in actual trace:
- No primitive library queries performed
- No Milvus/Qdrant hits
- CapacitorInterpreter generates geometry procedurally
- No reusable SVG/TikZ components retrieved

### Missing Components

❌ **No Pluggable Domain Builders**
- Missing: PySketcher integration (mechanical diagrams)
- Missing: SchemDraw integration (circuit diagrams)
- Missing: RDKit integration (chemical structures)
- Missing: Cytoscape integration (biological networks)
- Missing: Matplotlib/pgfplots (mathematical plots)

Only: Hardcoded CapacitorInterpreter for circuits

❌ **No Primitive Library Integration**
- Config: `enable_primitive_library = False` (honestly disabled)
- Milvus/Qdrant: Not connected
- Semantic search: Not used
- Result: Every diagram is generated from scratch

❌ **No Multi-Format Support**
- Only outputs: SVG
- Missing: TikZ, Asymptote, PGF, Graphviz, D3.js

### Gap Summary
| Component | Config | Implementation | Status |
|-----------|--------|----------------|--------|
| Primitive Library | ❌ (disabled) | ✅ (memory stub) | Stub only |
| Milvus/Qdrant | ❌ | ❌ | Missing |
| PySketcher | ❌ | ❌ | Missing |
| SchemDraw | ❌ | ❌ | Missing |
| RDKit | ❌ | ❌ | Missing |
| Cytoscape | ❌ | ❌ | Missing |
| Multi-format output | ❌ | ❌ | Missing |

---

## Layer 4: Layout & Constraint Solving

### Configuration Claims
```python
enable_z3_optimization: bool = True  # [MANDATORY]
enable_layout_optimization: bool = True
```

### Actual Implementation (from server logs)

```
Step 2/6: Advanced Constraint Solvers (Z3/SymPy/Cassowary)
   ⚠️  Z3 solver error: 'NoneType' object has no attribute 'objects'
   SymPy solve error: Cannot convert expression to float
   ⚠️  Cassowary solver unavailable – install cassowary
   ℹ️  No advanced solver applied

Step 3/6: Iterative Constraint Satisfaction
   ⏭️  Skipping DISTANCE constraint (already applied in initial placement)
   ⏭️  Skipping BETWEEN constraint (already applied in initial placement)
   [...]
ERROR: AttributeError: 'UniversalLayoutEngine' object has no attribute '_safe_dimension'
```

### Broken Components

❌ **Z3 Solver**
- Config: Enabled (`enable_z3_optimization = True`)
- Runtime: `'NoneType' object has no attribute 'objects'`
- Status: **BROKEN** (crashes on execution)
- Fallback: Heuristic layout

❌ **SymPy Solver**
- Config: Enabled (part of z3_optimization)
- Runtime: `Cannot convert expression to float`
- Status: **BROKEN** (crashes on execution)
- Fallback: Heuristic layout

❌ **Cassowary Solver**
- Config: N/A
- Runtime: `unavailable – install cassowary`
- Status: **MISSING** (not installed)

❌ **Layout Engine Crashes**
```python
File "core/universal_layout_engine.py", line 1376, in _apply_stacked_v_constraint
    prev_height = self._safe_dimension(prev_obj, 'height', 40)
AttributeError: 'UniversalLayoutEngine' object has no attribute '_safe_dimension'
```
- Method `_safe_dimension()` is **MISSING** from implementation
- Causes: Pipeline crash during layout
- Result: No diagram generated

### Missing Components

❌ **No Constraint Solver Integration**
- Z3: Enabled but crashes
- SymPy: Enabled but crashes
- Cassowary: Not installed
- Result: Falls back to heuristic positioning (50 iterations of nudging)

❌ **No Optimization**
- No svgo/scour SVG optimization
- No minification
- No compression

### Gap Summary
| Component | Config | Implementation | Status |
|-----------|--------|----------------|--------|
| Z3 Solver | ✅ | ❌ (NoneType crash) | Broken |
| SymPy Solver | ✅ | ❌ (conversion crash) | Broken |
| Cassowary | ❌ | ❌ (not installed) | Missing |
| Layout Engine | ✅ | ❌ (missing method) | **BROKEN** |
| SVG Optimization | ❌ | ❌ | Missing |

---

## Layer 5: Validation & QA

### Configuration Claims
```python
enable_ai_validation: bool = True  # VLM validation [MANDATORY]
enable_llm_auditing: bool = True  # [MANDATORY]
enable_deepseek_audit: bool = True  # Roadmap Call #2 [MANDATORY]
enable_ontology_validation: bool = True
```

### Actual Implementation

**Phase 9: VLM Validation**
```
✓ Phase 7: VLMValidator [ACTIVE]
```
- Config: Enabled
- Runtime: Stub mode (no actual VLM)
- Status: Returns dummy "valid" for all diagrams
- Real VLM: Not used (BLIP-2/LLaVA not loaded)

**Phase 10: LLM Auditing**
```
Phase 10: LLM Quality Auditing
   Auditing skipped: DiagramAuditor.audit() got an unexpected keyword argument 'svg_output'
```
- Config: Enabled
- Runtime: **CRASHES** with signature error
- API Call #2: **NOT EXECUTED**
- Status: **BROKEN**

**Ontology Validation**
```
⚠️  Ontology validation failed: RDF/OWL layer never wired up
```
- Config: Enabled
- Implementation: Not wired
- Status: **MISSING**

### Missing Components

❌ **No Real VLM**
- BLIP-2: Not loaded (proxy error trying to download)
- LLaVA: Not loaded
- GPT-4 Vision: Not called
- Only: Stub validator (returns dummy results)

❌ **No Structural Validation**
- No plan-vs-scene comparison
- No constraint violation detection
- No geometric consistency checks

❌ **No Domain Rule Engines**
- Kirchhoff's laws: Not checked
- Newton's laws: Not checked
- Conservation laws: Not checked
- Lens equation: Not checked

❌ **No Multi-Stage QA Loop**
- No iterative refinement
- No auto-correction beyond basic validation
- No feedback integration

### Gap Summary
| Component | Config | Implementation | Status |
|-----------|--------|----------------|--------|
| VLM Validation | ✅ | ✅ (stub only) | Stub |
| LLM Audit | ✅ | ❌ (signature crash) | **BROKEN** |
| DeepSeek Audit | ✅ | ❌ (signature crash) | **BROKEN** |
| Ontology Validation | ✅ | ❌ (not wired) | Missing |
| Domain Rules | ❌ | ❌ | Missing |
| QA Loop | ❌ | ❌ | Missing |

---

## Critical Runtime Errors

### 1. Layout Engine Crash
```python
AttributeError: 'UniversalLayoutEngine' object has no attribute '_safe_dimension'
  File "core/universal_layout_engine.py", line 1376, in _apply_stacked_v_constraint
    prev_height = self._safe_dimension(prev_obj, 'height', 40)
```

**Impact:** Pipeline crashes during layout, no diagram generated

**Root Cause:** Method `_safe_dimension()` is referenced but not defined

**Fix Required:** Implement `_safe_dimension()` helper method

---

### 2. Z3 Solver Crash
```
⚠️  Z3 solver error: 'NoneType' object has no attribute 'objects'
```

**Impact:** Z3 optimization disabled, falls back to heuristic

**Root Cause:** Constraint object is None or malformed

**Fix Required:** Add None checks before passing to Z3

---

### 3. SymPy Solver Crash
```
SymPy solve error: Cannot convert expression to float
```

**Impact:** SymPy optimization disabled, falls back to heuristic

**Root Cause:** Type mismatch in constraint formulation

**Fix Required:** Add type conversion and validation

---

### 4. DeepSeek API Failure
```
⚠️  DeepSeek initialization failed: Using SOCKS proxy, but the 'socksio' package is not installed.
```

**Impact:** No entity enrichment, no audit (2 of 3 mandatory API calls not executed)

**Root Cause:** Network proxy + missing dependency

**Fix Required:** Install socksio OR disable proxy

---

### 5. LLM Audit Signature Error
```
Auditing skipped: DiagramAuditor.audit() got an unexpected keyword argument 'svg_output'
```

**Impact:** No quality auditing (mandatory API call not executed)

**Root Cause:** Function signature mismatch in `DiagramAuditor.audit()`

**Fix Required:** Update function signature to accept `svg_output` parameter

---

## Summary: Configuration vs Reality

| Layer | Configured Features | Working Features | Broken Features | Missing Features |
|-------|---------------------|------------------|-----------------|------------------|
| **Layer 1: NLP** | 8 | 2 | 1 | 5 |
| **Layer 2: Planning** | 10 | 1 | 5 | 4 |
| **Layer 3: Domains** | 7 | 1 | 0 | 6 |
| **Layer 4: Layout** | 5 | 1 | 3 | 1 |
| **Layer 5: Validation** | 6 | 1 | 3 | 2 |
| **TOTAL** | **36** | **6** | **12** | **18** |

**Working Features (6):**
1. OpenIE extraction (basic)
2. Property graph construction (in-memory, not persisted)
3. CapacitorInterpreter (procedural generation)
4. Heuristic layout (when it doesn't crash)
5. SVG rendering
6. VLM validation (stub mode only)

**Broken Features (12):**
1. DeepSeek enrichment (API failure)
2. 5-stage DiagramPlanner (extracts junk entities)
3. EntityExtractor (1 bogus entity)
4. RelationMapper (0 relations)
5. DeepSeek audit (signature crash)
6. Z3 solver (NoneType crash)
7. SymPy solver (conversion crash)
8. Layout engine (missing method crash)
9. LLM audit (signature crash)
10. Ontology validation (not wired)
11. Real VLM models (not loaded)
12. Constraint generation (only 1 generic)

**Missing Features (18):**
1. spaCy/Stanza/DyGIE++ NLP
2. Neo4j/ArangoDB backend
3. PhySH/ChEBI/GO ontologies
4. Embeddings pipeline
5. PySketcher integration
6. SchemDraw integration
7. RDKit integration
8. Cytoscape integration
9. Cassowary solver
10. SVG optimization
11. TikZ/Asymptote output
12. Structural validation
13. Domain rule engines
14. QA refinement loop
15. Milvus/Qdrant primitive library
16. Local LLM planner
17. Parallel NLP workers
18. Multi-format rendering

---

## Conclusion

**The pipeline is NOT roadmap-compliant.**

While configuration flags are set to `True`, the actual implementation is:

1. **Missing** 18 components (50%)
2. **Broken** 12 components (33%)
3. **Working** 6 components (17%)

**Mandatory API Calls Status:**
- Roadmap Call #1 (DeepSeek Enrichment): ❌ FAILED (proxy error)
- Roadmap Call #2 (LLM Audit): ❌ FAILED (signature crash)
- Roadmap Call #3 (DeepSeek Validation): ❌ FAILED (proxy error)
- VLM Validation: ✅ STUB (not real validation)

**Immediate Blockers:**
1. Layout engine crashes (missing `_safe_dimension` method)
2. DeepSeek API unavailable (proxy + missing socksio)
3. LLM Audit crashes (wrong function signature)
4. Z3/SymPy solvers crash (None/type errors)
5. DiagramPlanner extracts junk (EntityExtractor broken)

**Next Steps:**
1. Fix critical runtime crashes (layout engine, audit signature)
2. Implement missing helper methods (`_safe_dimension`)
3. Fix Z3/SymPy solver integrations
4. Implement 5-stage DiagramPlanner properly
5. Wire up missing NLP models
6. Connect primitive library
7. Implement domain builders
8. Add real VLM validation

---

**Reality Check:** Setting `enable_*=True` does not magically implement features. The code must exist and work.
