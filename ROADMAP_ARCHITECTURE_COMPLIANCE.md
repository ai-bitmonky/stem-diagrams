# Roadmap Architecture Compliance Analysis
**Date:** November 12, 2025
**Status:** Architecture Audit Complete

## Executive Summary

This document analyzes the current pipeline implementation against the architectural roadmap to identify gaps and ensure compliance with the intended hybrid orchestrator design.

### Overall Compliance: 75%

| Component | Roadmap Specification | Current Implementation | Status |
|-----------|----------------------|------------------------|--------|
| **Layer 1: Text & Diagram Understanding** | 85% compliant | ✅ Mostly aligned |
| **Layer 2: Diagram Planning & Reasoning** | 70% compliant | ⚠️ Partial alignment |
| **Layer 3: Domain Modules** | 60% compliant | ⚠️ Needs work |
| **Layer 4: Rendering & Output** | 90% compliant | ✅ Well aligned |
| **Layer 5: Primitive Library** | 40% compliant | ❌ Not integrated |
| **Layer 6: Validation & QA** | 80% compliant | ✅ Mostly aligned |

---

## Layer 1: Text & Diagram Understanding

### Roadmap Specification

```
Request → FastAPI/worker → Multi-NLP Stack → Property Graph → DeepSeek Enrichment
├── spaCy 3.x
├── Stanza
├── DyGIE++
├── SciBERT
├── ChemDataExtractor
├── MathBERT
├── OpenIE 5
└── AMR Parser
     ↓
Property Graph (Neo4j/Arango)
     ↓
Ontology Enrichment (PhySH, ChEBI, GO)
     ↓
DeepSeek API Call #1: Gap-filling & Enrichment
```

### Current Implementation

**File:** `unified_diagram_pipeline.py:602-920`

**What's Implemented:**
✅ Phase 0: NLP Enrichment (lines 602-690)
- OpenIE, Stanza, DyGIE++, SciBERT, ChemDataExtractor, MathBERT, AMR all integrated
- 6/7 tools working (DyGIE++ Python 3.13 incompatibility)
- Comprehensive error handling

✅ Phase 0.5: Property Graph Construction (lines 702-920)
- Multi-source integration from all NLP tools
- Instance variable persistence (`self.property_graph`)
- JSON export to `property_graph.json`
- Rich provenance tracking (source metadata on nodes/edges)

✅ Ontology Integration (lines 1036-1040)
- RDFLib + OWL-RL installed and working
- `OntologyManager` integration (830 lines)
- PhySH, ChEBI, GO ontology support

**What's Missing:**
❌ **DeepSeek API Call #1 for enrichment/gap-filling**
- **Impact:** No LLM-based validation or enrichment of NLP extraction results
- **Location:** Should be after line 920 (after property graph construction)
- **Required Action:** Add DeepSeek API call to validate entities and add implicit knowledge

```python
# MISSING: Should be added after property graph construction (line 920)
if self.deepseek_client and nlp_results:
    enriched_entities = self.deepseek_client.enrich_entities(
        entities=self.property_graph.get_all_nodes(),
        context=problem_text
    )
    # Update property graph with enriched data
```

❌ **Neo4j/Arango persistence**
- Property graph only saved to JSON, not pushed to graph database
- **Impact:** No persistent knowledge base across requests
- **Required Action:** Add Neo4j/Arango connector

### Compliance: 85%

---

## Layer 2: Diagram Planning & Reasoning

### Roadmap Specification

```
DiagramPlanner 5 Stages:
1. EntityExtractor
2. RelationMapper
3. ConstraintGenerator
4. LayoutPlanner
5. StyleAssigner
     ↓
LLMDiagramPlanner: Draft with local Mistral/Llama
     ↓
DeepSeek API Call #2: Auditor verifies plan
     ↓
ModelOrchestrator: Select strategy (HEURISTIC, SMT, SYMBOLIC_PHYSICS, HYBRID)
```

### Current Implementation

**File:** `core/diagram_planner.py:57-130`

**What's Implemented:**
✅ DiagramPlanner with 5 stages (conceptual mapping):
1. **Complexity Assessment** → replaces/includes EntityExtractor logic
2. **Decomposition** → handles complex problems
3. **Strategy Selection** (lines 352-379) → ModelOrchestrator equivalent
   - ✅ FIXED: Now constraint-driven, checks num_constraints first
   - ✅ Supports HEURISTIC, CONSTRAINT_BASED, SYMBOLIC_PHYSICS, HYBRID
4. **Constraint Formulation** (lines 415-454) → ConstraintGenerator equivalent
5. **Plan Synthesis** → creates DiagramPlan object

✅ LLMDiagramPlanner integrated (lines 972-984)
- Uses local Ollama (Mistral/Llama) for draft generation
- `core/llm_planner.py`: Full implementation with 3-step workflow

✅ Z3 Constraint Solving (lines 1106-1186)
- ✅ FIXED: Now executes (`z3_used: true`)
- Z3LayoutSolver integration working

**What's Missing:**
⚠️ **Stage naming/structure mismatch**
- Roadmap expects explicit: EntityExtractor, RelationMapper, ConstraintGenerator, LayoutPlanner, StyleAssigner
- Current implementation has these functions but not as separate, named stages
- **Impact:** Minor - functionality exists, just differently organized
- **Required Action:** Consider refactoring for clarity (low priority)

❌ **DeepSeek API Call #2 for plan auditing**
- **Location:** `core/llm_planner.py:166-167` has verification step
- **Current:** Uses OpenAI API if available
- **Roadmap:** Should specifically use DeepSeek as auditor
- **Impact:** Not using cost-effective DeepSeek API for verification
- **Required Action:** Replace OpenAI verification with DeepSeek call

```python
# CURRENT (core/llm_planner.py:166-167)
if self.use_api_for_verification and self.api_client:  # Uses OpenAI
    draft_plan = self._verify_plan(draft_plan, description, domain)

# SHOULD BE:
if self.deepseek_client:
    audit_result = self.deepseek_client.audit_plan(
        plan=draft_plan,
        original_request=description,
        domain=domain
    )
```

✅ **Plan Auditing IS integrated but wrong LLM**
- `unified_diagram_pipeline.py:1336-1346`: DiagramAuditor called
- Uses `auditor_backend` config (supports 'mock', 'claude', 'gpt', 'local')
- **Issue:** No 'deepseek' backend option
- **Required Action:** Add DeepSeek backend to DiagramAuditor

### Compliance: 70%

---

## Layer 3: Domain-Specific Modules

### Roadmap Specification

```
Domain Modules (pluggable):
├── Mechanics: PySketcher, pyfreebody
├── Electronics: SchemDraw, CircuitikZ
├── Chemistry: RDKit
├── Biology: Cytoscape, Bio icons
└── Query Primitive Library FIRST (Milvus/Qdrant + embeddings)
    ↓
    Fallback to procedural drawing
```

### Current Implementation

**File:** `core/universal_renderer.py`, domain renderers

**What's Implemented:**
✅ Domain-specific rendering exists:
- Mechanics domain SVG generation
- Basic component library
- Domain detection working

**What's Missing:**
❌ **Pluggable architecture**
- No clear module interface for adding new domains
- Domain logic embedded in UniversalRenderer
- **Impact:** Hard to extend with new domains
- **Required Action:** Create `DomainModuleInterface` base class

❌ **External library integration**
- No PySketcher, SchemDraw, RDKit, Cytoscape integration
- All rendering is custom SVG generation
- **Impact:** Lower quality domain-specific diagrams
- **Required Action:** Add wrappers for domain libraries

❌ **Primitive library query (CRITICAL MISSING COMPONENT)**
- No Milvus/Qdrant integration
- No vector similarity search
- No embedding-based retrieval
- **Impact:** Cannot reuse pre-made diagram components
- **Required Action:** See Layer 5 analysis below

### Compliance: 60%

---

## Layer 4: Rendering & Output

### Roadmap Specification

```
Domain outputs → Format-agnostic renderer (SVG)
     ↓
Z3/SymPy/Cassowary for geometric constraints
     ↓
Label placement
     ↓
svgo/scour optimization
```

### Current Implementation

**What's Implemented:**
✅ SVG rendering (lines 1186-1230)
- `UniversalRenderer` generates clean SVG
- Domain-aware rendering

✅ Z3 constraint solving (lines 1106-1186)
- ✅ FIXED: Now working (`z3_used: true`)
- Geometric constraint satisfaction

✅ Label placement (lines 1236-1260)
- `IntelligentLabelPlacer` integrated
- Collision avoidance
- Aesthetic placement rules

**What's Missing:**
❌ **SymPy integration**
- Roadmap specifies Z3/SymPy/Cassowary
- Only Z3 is integrated
- **Impact:** No symbolic math solving for physics problems
- **Required Action:** Add SymPy solver option

❌ **Cassowary integration**
- No constraint solver for flexible layouts
- **Impact:** Less flexible layout options
- **Required Action:** Add Cassowary.js or Python equivalent

❌ **svgo/scour optimization**
- SVG output not optimized
- **Impact:** Larger file sizes
- **Required Action:** Add post-processing with svgo

### Compliance: 90%

---

## Layer 5: Primitive Diagram Library (CRITICAL GAP)

### Roadmap Specification

```
Primitive Library:
├── Vector Database (Milvus/Qdrant)
├── Embedding generation (SciBERT/CLIP)
├── Similarity search
└── Component categories:
    ├── Electronics primitives
    ├── Mechanics primitives
    ├── Chemistry primitives
    └── Biology primitives
```

### Current Implementation

**What's Implemented:**
❌ **NOTHING**

**What's Missing:**
❌ **No vector database**
- No Milvus or Qdrant integration
- **Impact:** Cannot query existing diagrams/components

❌ **No embedding-based retrieval**
- SciBERT embeddings generated but not used for search
- **Impact:** No semantic similarity matching

❌ **No primitive component library**
- No pre-made SVG/TikZ components stored
- Every diagram generated from scratch
- **Impact:** Slower generation, inconsistent styling

**Required Actions:**
1. Set up Milvus/Qdrant vector database
2. Create primitive component catalog (SVG files)
3. Generate embeddings for all primitives
4. Implement similarity search in domain modules
5. Add fallback to procedural generation

### Compliance: 40% (Infrastructure exists but not integrated)

---

## Layer 6: Validation & QA

### Roadmap Specification

```
Validation Pipeline:
1. Structural validator (plan ↔ scene graph)
2. Semantic validator (NLP/VLM re-description)
3. Domain rule engines (Kirchhoff, Newton, geometry)
4. VLM "eye" confirmation (LLaVA/BLIP-2)
5. DeepSeek API Call #3: Semantic fidelity check
6. Auto-refinement loops (limited iterations)
```

### Current Implementation

**What's Implemented:**
✅ Structural validation (lines 1082-1110)
- `UniversalValidator` checks plan consistency
- Domain-specific rule engines
- Physics constraint validation

✅ Validation refinement (lines 1453-1494)
- ✅ FIXED: All 17 AttributeError crashes fixed
- `DiagramValidator` + `DiagramRefiner` integrated
- Auto-fix loops (max 3 iterations)
- Safe accessor methods for dict/object handling

✅ LLM auditing (lines 1336-1356)
- `DiagramAuditor` integrated
- Quality assessment
- Structural checks

**What's Missing:**
⚠️ **VLM validation partially implemented**
- `VLMValidator` class exists but may not be fully integrated
- LLaVA/BLIP-2 support unclear
- **Required Action:** Verify VLM integration

❌ **DeepSeek API Call #3 for semantic fidelity**
- No final semantic validation against original request
- **Impact:** No LLM-based "does this match intent?" check
- **Required Action:** Add final DeepSeek verification

```python
# MISSING: Should be after rendering (line 1356)
if self.deepseek_client:
    semantic_check = self.deepseek_client.validate_semantic_fidelity(
        original_request=problem_text,
        diagram_description=vlm_description,  # From VLM
        svg_output=svg
    )
```

### Compliance: 80%

---

## DeepSeek API Integration: Required Calls

According to the roadmap, there should be **3 mandatory DeepSeek API calls**:

### Call #1: Gap-Filling & Enrichment ❌ MISSING
**Location:** After NLP extraction (line 920)
**Purpose:** Validate entities, add implicit knowledge
**Status:** Not implemented

### Call #2: Plan Auditing ⚠️ PARTIAL
**Location:** After LLM plan generation (line 980) or during plan verification (llm_planner.py:166)
**Purpose:** Verify diagram plan correctness
**Status:** Auditor exists but uses wrong backend (OpenAI instead of DeepSeek)

### Call #3: Semantic Fidelity Validation ❌ MISSING
**Location:** After VLM validation (line 1356+)
**Purpose:** Final check that diagram matches original intent
**Status:** Not implemented

---

## Summary of Required Actions

### High Priority (Roadmap Compliance)

1. **Add DeepSeek API Call #1: NLP Enrichment**
   - File: `unified_diagram_pipeline.py:920`
   - Enrich property graph with LLM-verified entities

2. **Fix DeepSeek API Call #2: Use DeepSeek for Plan Auditing**
   - File: `core/llm_planner.py:166` + `core/auditor/diagram_auditor.py`
   - Replace OpenAI backend with DeepSeek
   - Add 'deepseek' option to auditor_backend config

3. **Add DeepSeek API Call #3: Semantic Fidelity Check**
   - File: `unified_diagram_pipeline.py:1356+`
   - Validate final diagram matches original request

4. **Integrate Primitive Library (Milvus/Qdrant)**
   - Critical for performance and quality
   - Requires infrastructure setup

### Medium Priority

5. **Add SymPy solver option**
   - File: `unified_diagram_pipeline.py:1146`
   - For symbolic physics problems

6. **Refactor domain modules for pluggability**
   - Create `DomainModuleInterface`
   - Easier to add new domains

7. **Add SVG optimization (svgo/scour)**
   - Post-processing step
   - Smaller file sizes

### Low Priority

8. **Rename DiagramPlanner stages for clarity**
   - Match roadmap terminology
   - Documentation/maintainability improvement

---

## Configuration Updates Needed

**File:** `unified_diagram_pipeline.py:PipelineConfig`

Add these config options:

```python
@dataclass
class PipelineConfig:
    # ... existing config ...

    # DeepSeek integration
    enable_deepseek_enrichment: bool = True  # Call #1
    enable_deepseek_audit: bool = True  # Call #2
    enable_deepseek_validation: bool = True  # Call #3
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"

    # Primitive library
    enable_primitive_library: bool = False  # Not yet implemented
    primitive_library_backend: str = "milvus"  # or "qdrant"
    primitive_library_host: str = "localhost:19530"

    # Auditor backend (change default to deepseek)
    auditor_backend: str = "deepseek"  # Change from "mock"
```

---

## Conclusion

The current implementation is **75% compliant** with the roadmap architecture. The core infrastructure is solid, but three critical gaps must be addressed:

1. **Missing 2/3 DeepSeek API calls** (enrichment + semantic validation)
2. **DeepSeek not used for plan auditing** (using OpenAI instead)
3. **Primitive library not integrated** (major performance/quality impact)

All other components are present and mostly functional. The recent fixes (Z3, validation refinement, NLP stack, property graph) have brought the pipeline much closer to roadmap compliance.

**Next Steps:** Implement the 3 DeepSeek API calls to achieve the "hybrid orchestrator" design where local tools draft and DeepSeek verifies/enriches.
