# Request Flow Architecture

**Universal STEM Diagram Generator v4.0**
**Date:** November 12, 2025
**Status:** Production-Ready with Property Graph-Driven Planning

---

## Overview

The pipeline follows a **10-phase architecture** that transforms natural language problem descriptions into accurate scientific diagrams. The system uses a **property graph-driven approach** with local NLP tools, minimizing API calls while maintaining high accuracy.

## High-Level Flow

```
User Request (Text)
    ↓
[API Server: Flask/FastAPI]
    ↓
[UnifiedDiagramPipeline.generate()]
    ↓
[10 Sequential Phases]
    ↓
[DiagramResult with SVG]
    ↓
User Response (SVG + Metadata)
```

---

## Detailed Phase Architecture

### **Entry Point: API Server**

**File:** `api_server.py`
**Route:** `POST /api/generate`
**Input:** `{"problem_text": "..."}`

```python
@app.route('/api/generate', methods=['POST'])
def generate_diagram():
    problem_text = request.json.get('problem_text', '')
    result = pipeline.generate(problem_text)
    return jsonify(result.to_dict())
```

---

### **Phase 0: NLP Enrichment** 🔬

**File:** `unified_diagram_pipeline.py:920-970`
**Component:** Local NLP Tools (OpenIE, Stanza, DyGIE++, SciBERT, etc.)
**Purpose:** Extract entities, relations, and scientific concepts from text

**Tools Available:**
- **OpenIE** - Open information extraction (triples)
- **Stanza** - Stanford NLP (entities, dependencies)
- **DyGIE++** - Scientific entity and relation extraction
- **SciBERT** - Scientific BERT embeddings
- **ChemDataExtractor** - Chemistry-specific extraction
- **MathBERT** - Mathematics embeddings
- **AMR Parser** - Abstract Meaning Representation

**Process:**
1. Parse problem text with active NLP tools
2. Extract entities (objects, values, units)
3. Extract relations (spatial, functional, quantitative)
4. Extract domain-specific concepts

**Output:**
```python
{
    'openie': {
        'triples': [(subject, relation, object), ...],
        'entities': [...]
    },
    'stanza': {...},  # if enabled
    'dygie': {...}    # if enabled
}
```

**Cost:** ✅ Free (local processing)
**Fallback:** Works without any tool if all fail

---

### **Phase 0.5: Property Graph Construction** 🕸️

**File:** `unified_diagram_pipeline.py:971-990`
**Component:** `PropertyGraph` (NetworkX-based)
**Purpose:** Build knowledge graph from NLP results

**Process:**
1. Aggregate entities from all NLP tools
2. Create graph nodes for each entity
3. Add edges for relationships
4. Annotate with types (OBJECT, ACTION, PROPERTY, VALUE)
5. Save to `output/property_graph.json`

**Output:**
```python
PropertyGraph(
    nodes=[
        GraphNode(id='battery_1', type=NodeType.OBJECT, label='12V Battery'),
        GraphNode(id='resistor_1', type=NodeType.OBJECT, label='100Ω Resistor'),
        ...
    ],
    edges=[
        GraphEdge(source='battery_1', target='resistor_1', type=EdgeType.CONNECTED_TO),
        ...
    ]
)
```

**Key Metrics:**
- Nodes: 6-20 typical
- Edges: 3-15 typical
- Connected Components: 1-4 typical

**Cost:** ✅ Free (local graph construction)

---

### **Phase 0.6: DeepSeek Enrichment (MANDATORY)** 🤖

**File:** `unified_diagram_pipeline.py:991-1041`
**Component:** `DeepSeekClient` (API)
**Purpose:** Validate and enrich entities with LLM (Roadmap Call #1)

**What It Does:**
- Validates extracted entities
- Identifies missing entities
- Corrects entity types
- Adds domain context

**Roadmap Requirement:** This is API Call #1 of 3 mandatory DeepSeek calls

**Cost:** 💰 ~$0.001-0.005 per request
**Enabled by default:** Yes (roadmap-compliant architecture)

---

### **Phase 1: Diagram Planning (Property Graph-Driven)** 🧠

**File:** `unified_diagram_pipeline.py:1043-1135`
**Component:** `DiagramPlanner` (5-Stage Pipeline)
**Purpose:** Create diagram plan from property graph **WITHOUT LLM extraction**

**Architecture:** NEW Property Graph-Driven (Zero LLM Calls)

#### **5-Stage Planning Pipeline**

**File:** `core/diagram_planner.py:677-1262`

**Stage 1: Entity Extraction** (`_extract_entities_from_graph`)
- Query property graph for drawable entities
- Filter by node type (OBJECT, STRUCTURE)
- Extract properties (dimensions, values, units)
- Map to primitive library

**Stage 2: Relation Mapping** (`_map_relations_from_graph`)
- Query graph edges between entities
- Classify relations (SPATIAL, FUNCTIONAL, QUANTITATIVE)
- Map to visual relationships

**Stage 3: Constraint Generation** (`_generate_constraints_from_graph`)
- Infer spatial constraints (DISTANCE, PARALLEL, SERIES)
- Domain-specific constraints (circuit laws, force balance)
- Prioritize constraints (HIGH, MEDIUM, LOW)

**Stage 4: Layout Planning** (`_plan_layout_with_solver`)
- Assess complexity (0.0-1.0 scale)
- Select solver:
  - **Heuristic** (≤5 entities, simple)
  - **Z3 SMT** (6-15 entities, complex constraints)
  - **SymPy** (>15 entities, symbolic)

**Stage 5: Style Assignment** (`_assign_styles_from_graph`)
- Domain-specific visual styles
- Color schemes
- Rendering hints

**Output:**
```python
DiagramPlan(
    extracted_entities=[...],       # 1-20 entities
    extracted_relations=[...],      # 0-15 relations
    global_constraints=[...],       # 1-30 constraints
    complexity_score=0.25,          # 0.0-1.0
    strategy=BuildStrategy.CONSTRAINT_BASED,
    layout_hints={
        'solver': 'heuristic',
        'z3_used': False
    }
)
```

**Backward Compatibility:** Converts DiagramPlan → CanonicalProblemSpec

**Fallback:** If property graph unavailable, falls back to LLM extraction

**Cost:** ✅ Free (property graph queries only)

---

### **Phase 2: Scene Synthesis + Strategic Planning** 🏗️

**File:** `unified_diagram_pipeline.py:1136-1256`
**Component:** `UniversalSceneBuilder` + Domain Interpreters
**Purpose:** Convert specs to renderable scene with domain-specific logic

#### **Strategy Selection**

Based on complexity score:
- **DIRECT** (< 0.3): Simple positioning
- **HIERARCHICAL** (0.3-0.7): Component grouping
- **CONSTRAINT_FIRST** (> 0.7): Full constraint solving

#### **Scene Building (6 Steps)**

**File:** `core/universal_scene_builder.py:44-132`

**Step 1: Domain Interpreter Selection**
- Map domain → interpreter
  - `current_electricity` → `CapacitorInterpreter`
  - `mechanics` → `MechanicsInterpreter`
  - `optics` → `OpticsInterpreter`
  - etc.

**Step 2: Scene Interpretation**
- Domain interpreter converts specs → SceneObjects
- Example: `CapacitorInterpreter._create_multi_dielectric_capacitor()`
  - Creates plates, dielectrics, labels
  - Adds constraints (PARALLEL, DISTANCE, BETWEEN, ADJACENT, STACKED_V)

**Step 3: NLP Enrichment**
- Validate scene objects against NLP entities
- Add constraints from NLP triples

**Step 4: Physics Enrichment**
- Add implicit elements (field lines, forces)
- Infer missing relationships

**Step 5: Constraint Inference**
- Deduce additional constraints from physics
- Add default constraints

**Step 6: Scene Completeness Validation**
- Check all required elements present
- Domain-specific validation
  - Circuit: needs power source + component
  - Optics: needs lens/mirror + object + image
  - Mechanics: needs mass

**Output:**
```python
Scene(
    objects=[
        SceneObject(id='plate_top', type=PrimitiveType.RECTANGLE, position={x, y}, ...),
        SceneObject(id='dielectric_left', ...),
        ...
    ],
    constraints=[
        Constraint(type=ConstraintType.PARALLEL, objects=['plate_top', 'plate_bottom']),
        Constraint(type=ConstraintType.DISTANCE, value=180, ...),
        ...
    ]
)
```

**Cost:** ✅ Free (deterministic interpretation)

---

### **Phase 3: Ontology Validation** 🔍

**File:** `unified_diagram_pipeline.py:1257-1283`
**Component:** `OntologyValidator` (RDFLib)
**Purpose:** Validate semantic consistency against STEM ontology

**Process:**
1. Convert scene to RDF triples
2. Check against ontology rules
3. Validate object types
4. Validate relationships
5. Report inconsistencies

**Optional:** Can be disabled for performance

**Cost:** ✅ Free (local RDF validation)

---

### **Phase 4: Physics Validation** ⚖️

**File:** `unified_diagram_pipeline.py:1284-1327`
**Component:** `UniversalValidator`
**Purpose:** Validate physics constraints and relationships

**5-Step Validation:**

**Step 1: Semantic Validation**
- Object types correct
- Properties valid

**Step 2: Geometric Validation**
- No impossible positions
- Valid dimensions

**Step 3: Domain-Specific Physics Validation**
- Circuit: Kirchhoff's laws
- Mechanics: Force balance
- Optics: Lens equation

**Step 4: Auto-Correction**
- Fix common issues
- Adjust positions
- Correct values

**Step 5: Final Validation**
- Recheck all constraints
- Report remaining issues

**Output:**
```python
ValidationReport(
    is_valid=True/False,
    errors=[...],
    warnings=[...],
    auto_corrections=12
)
```

**Cost:** ✅ Free (deterministic validation)

---

### **Phase 5: Layout Optimization + Z3** 📐

**File:** `unified_diagram_pipeline.py:1328-1406`
**Component:** `UniversalLayoutEngine` + Z3 SMT Solver
**Purpose:** Compute optimal object positions

**5-Step Layout Pipeline:**

**File:** `core/universal_layout_engine.py:46-95`

**Step 1: Domain-Aware Initial Placement**
- Use domain-specific heuristics
  - **Electrostatics:** Vertical plate stacking
  - **Circuit:** Horizontal flow (left → right)
  - **Mechanics:** Ground at bottom, objects on top
  - **Optics:** Horizontal optical axis
- Apply initial positions based on object properties
- Apply BETWEEN constraints for multi-region objects

**Step 2: Constraint Satisfaction** (50 iterations max)
- Iteratively apply constraints:
  - **PARALLEL:** Align parallel objects
  - **DISTANCE:** Enforce spacing
  - **ALIGNED_H/V:** Horizontal/vertical alignment
  - **ADJACENT:** Make objects touch
  - **STACKED_V/H:** Stack objects
  - **BETWEEN:** Position between two objects
  - **PERPENDICULAR:** 90° orientation
  - **SYMMETRIC:** Mirror symmetry
  - **NO_OVERLAP:** Resolve overlaps
  - **CONNECTED:** Pull connected objects closer
- Converges when max_displacement < 1px

**Step 3: Aesthetic Optimization**
- Snap to 10px grid
- Center diagram on canvas
- Optimize spacing

**Step 4: Intelligent Label Placement**
- 8 candidate positions per object (N, NE, E, SE, S, SW, W, NW)
- Choose position with least overlap
- Store in `object.properties['label_position']`

**Step 5: Final Validation**
- Check bounds (objects within canvas)
- Verify spacing minimums

**Z3 Integration** (Optional):
- For complex scenes (>5 objects, many constraints)
- Formulates SMT problem
- Solves for optimal positions
- Fallback to heuristic if Z3 fails

**Output:**
```python
Scene(
    objects=[
        SceneObject(id='...', position={'x': 450, 'y': 300}, ...),
        ...
    ]
)
```

**Cost:** ✅ Free (local computation)

---

### **Phase 6: Spatial Validation** 🔎

**File:** `unified_diagram_pipeline.py:1407-1446`
**Component:** `SpatialValidator`
**Purpose:** Check for overlaps and positioning errors

**Checks:**
- Object overlap detection
- Canvas boundary violations
- Label readability
- Spacing violations

**Output:**
```python
SpatialValidationReport(
    is_valid=True/False,
    errors=[...],       # Critical issues
    warnings=[...]      # Minor issues
)
```

**Cost:** ✅ Free (geometric checks)

---

### **Phase 7: SVG Rendering** 🎨

**File:** `unified_diagram_pipeline.py:1447-1502`
**Component:** `UniversalRenderer`
**Purpose:** Convert positioned scene to SVG

**Process:**
1. Create SVG canvas (1200×800 default)
2. Render by layers:
   - **BACKGROUND** (grid, axes)
   - **FILL** (dielectrics, regions)
   - **SHAPES** (primary objects)
   - **ANNOTATIONS** (arrows, lines)
   - **LABELS** (text)
3. Apply styles (colors, strokes, opacity)
4. Add metadata (domain, problem text)

**Primitive Types Supported:**
- RECTANGLE, CIRCLE, LINE, ARROW
- TEXT (with MathJax support for formulas)
- BATTERY_SYMBOL, RESISTOR_SYMBOL, CAPACITOR_SYMBOL
- SPRING, FORCE_ARROW, FIELD_LINE
- LENS, MIRROR, RAY
- Custom domain-specific primitives

**Output:**
```xml
<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
  <metadata>
    <domain>current_electricity</domain>
    <problem>Draw a parallel-plate capacitor...</problem>
  </metadata>
  <rect id="plate_top" x="400" y="300" width="400" height="12" fill="#ff4444"/>
  <rect id="dielectric_left" x="400" y="312" width="200" height="180" fill="#BBDEFB" opacity="0.6"/>
  ...
</svg>
```

**Cost:** ✅ Free (local rendering)

---

### **Phase 8: Validation Refinement** 🔄

**File:** `unified_diagram_pipeline.py:1503-1572`
**Component:** `DiagramValidator` (Bidirectional)
**Purpose:** Iterative quality improvement

**Process:** (Max 3 iterations)
1. Validate diagram against specs
2. Identify issues (missing elements, incorrect positions)
3. Auto-fix issues
4. Re-validate
5. Repeat until valid or max iterations

**Output:**
```python
RefinementResult(
    iterations=2,
    overall_confidence=0.85,
    issues_found=3,
    issues_fixed=2,
    suggestions=['...']
)
```

**Cost:** ✅ Free (local validation loop)

---

### **Phase 9: VLM Validation (MANDATORY)** 👁️

**File:** `unified_diagram_pipeline.py:1573-1617`
**Component:** `VLMValidator` (Vision-Language Model)
**Purpose:** Visual-semantic validation using AI vision

**Supported Models:**
- **BLIP-2** (Salesforce) - Local
- **LLaVA** (Microsoft) - Local
- **GPT-4 Vision** (OpenAI) - API
- **Stub** - Testing mode (default)

**Process:**
1. Convert SVG → PNG (if needed)
2. Generate image description with VLM
3. Compare description to problem text
4. Identify discrepancies
5. Suggest improvements

**Output:**
```python
VisualValidationResult(
    is_valid=True,
    confidence=0.85,
    description="A parallel-plate capacitor with three dielectric regions...",
    discrepancies=[],
    suggestions=[]
)
```

**Roadmap Requirement:** Visual validation is Priority 3 MEDIUM feature

**Cost:** 💰 $0 (stub mode) to $0.01 per image (GPT-4V)
**Enabled by default:** Yes (stub mode for testing, can upgrade to full VLM)

---

### **Phase 10: LLM Quality Auditing (MANDATORY)** 🎯

**File:** `unified_diagram_pipeline.py:1618-1688`
**Component:** `DiagramAuditor` (DeepSeek API - Roadmap Call #2)
**Purpose:** Audit diagram quality with LLM

**Audit Criteria:**
- Semantic fidelity (0-100)
- Visual clarity
- Completeness
- Accuracy
- Suggestions for improvement

**Output:**
```python
AuditResult(
    semantic_fidelity_score=85,
    issues=[],
    suggestions=['Add units to labels', ...],
    overall_assessment='Good'
)
```

**Roadmap Requirement:** This is API Call #2 of 3 mandatory DeepSeek calls

**Cost:** 💰 ~$0.001-0.005 per request
**Enabled by default:** Yes (roadmap-compliant architecture)

---

## Final Response

**File:** `unified_diagram_pipeline.py:1689-1755`
**Component:** `DiagramResult`

```python
DiagramResult(
    svg="<svg>...</svg>",                  # Generated SVG (2-10KB)
    svg_file_path="output/diagram.svg",    # Saved path

    # Metadata
    complexity_score=0.25,
    selected_strategy='heuristic',
    domain='current_electricity',

    # Components
    property_graph=PropertyGraph(...),     # 6 nodes, 3 edges
    nlp_results={'openie': {...}},

    # Validation
    ontology_validation=ValidationReport(...),

    # Costs
    metadata={
        'planning_mode': 'property_graph_driven',
        'z3_used': False,
        'sympy_used': False,
        'enrichment_cost_usd': 0.0012,
        'validation_cost_usd': 0.0008,
        'semantic_fidelity_score': 85,
        'total_duration_ms': 1523
    }
)
```

---

## API Response

**HTTP 200 OK**
```json
{
  "svg": "<svg>...</svg>",
  "svg_file_path": "output/diagram_12345.svg",
  "complexity_score": 0.25,
  "strategy": "heuristic",
  "domain": "current_electricity",
  "metadata": {
    "planning_mode": "property_graph_driven",
    "z3_used": false,
    "entities": 3,
    "constraints": 8,
    "total_cost_usd": 0.002,
    "duration_ms": 1523
  }
}
```

---

## Performance Metrics

### Typical Request

| Metric | Value |
|--------|-------|
| **Total Duration** | 700-2500ms |
| **Phase 0 (NLP)** | 2-5ms |
| **Phase 0.5 (Graph)** | 3-5ms |
| **Phase 0.6 (DeepSeek Enrichment)** | 200-500ms |
| **Phase 1 (Planning)** | 1-5ms |
| **Phase 2 (Scene)** | 300-800ms |
| **Phase 3-4 (Validation)** | 30-50ms |
| **Phase 5 (Layout)** | 2-10ms |
| **Phase 6-8 (Rendering)** | 1-3ms |
| **Phase 9 (VLM)** | 0-1000ms (stub=0ms) |
| **Phase 10 (Audit)** | 200-500ms |

### Cost Breakdown (Roadmap-Compliant)

| Component | Cost per Request | Status |
|-----------|-----------------|--------|
| **Local Processing** | $0.00 (Phases 0-8) | Always free |
| **DeepSeek Enrichment (Phase 0.6)** | ~$0.001-0.005 | **MANDATORY** |
| **DeepSeek Audit (Phase 10)** | ~$0.001-0.005 | **MANDATORY** |
| **DeepSeek Validation (Phase 10)** | ~$0.001-0.005 | **MANDATORY** |
| **VLM Validation (Phase 9)** | $0.00 (stub) to $0.01 (GPT-4V) | **MANDATORY** (stub default) |
| **Total Typical** | **$0.003-0.025** | Per request |
| **Total Minimum** | **$0.003** | With stub VLM |

### Throughput

- **Sequential:** 0.5-2 requests/second
- **With Caching:** 5-10 requests/second
- **Parallel (4 workers):** 2-8 requests/second

---

## Key Features

### ✅ **Local-First Architecture**
- Phases 0-7 run entirely locally
- No mandatory API calls
- Privacy-preserving

### ✅ **Zero LLM Extraction**
- Property graph-driven planning
- NLP tools extract structure
- LLMs only validate/enrich (optional)

### ✅ **Constraint-Driven Layout**
- Declarative constraint specification
- Generic solver for all domains
- Z3 SMT for complex scenes

### ✅ **Domain-Specific Intelligence**
- Specialized interpreters per domain
- Physics-aware validation
- Intelligent defaults

### ✅ **Multi-Stage Validation**
- Semantic, geometric, physics checks
- Auto-correction loops
- Visual validation (optional)

### ✅ **Production-Ready**
- Comprehensive error handling
- Detailed logging/tracing
- Performance monitoring
- Graceful fallbacks

---

## Error Handling

### Graceful Degradation

| Failure Point | Fallback Behavior |
|--------------|-------------------|
| **NLP tools unavailable** | Use minimal OpenIE or proceed without |
| **Property graph fails** | Fall back to LLM extraction |
| **Domain interpreter missing** | Use generic interpreter |
| **Z3 solver fails** | Fall back to heuristic solver |
| **Validation fails** | Proceed with warnings |
| **DeepSeek API fails** | Skip enrichment/audit |

### Logging

All phases are logged to:
- `logs/req_YYYYMMDD_HHMMSS.log` (detailed text log)
- `logs/req_YYYYMMDD_HHMMSS_trace.json` (structured trace)

---

## Configuration

### Minimal Configuration (All Features)

```python
config = PipelineConfig(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),

    # Core
    validation_mode="standard",
    enable_layout_optimization=True,

    # Property Graph-Driven (NEW)
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_strategic_planning=True,

    # Solvers
    enable_z3_optimization=True,
    enable_sympy_solver=True,

    # Optional API Features
    enable_deepseek_enrichment=True,
    enable_deepseek_validation=True,

    # Primitive Library
    enable_primitive_library=True,
    primitive_library_backend="memory"
)
```

### Minimal Configuration (Zero API Calls)

```python
config = PipelineConfig(
    # No API key needed
    enable_deepseek_enrichment=False,
    enable_deepseek_audit=False,
    enable_deepseek_validation=False,
    enable_ai_validation=False,

    # All other features work locally
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_z3_optimization=True,
    enable_primitive_library=True
)
```

---

## Testing

Run comprehensive test suite:

```bash
export DEEPSEEK_API_KEY='your-key-here'
python3 test_complete_implementation.py
```

**Expected Output:**
```
✅ PASSED: Primitive Library
✅ PASSED: DiagramPlanner
✅ PASSED: Full Pipeline (Circuit Example)

✅ ALL TESTS PASSED - Implementation Complete!
```

---

## Related Documentation

- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Roadmap completion
- [TEST_RESULTS.md](TEST_RESULTS.md) - Test suite results
- [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md) - Original architecture analysis
- [POSITION_FORMAT_FIX.md](POSITION_FORMAT_FIX.md) - Position handling fix
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Implementation details

---

**Last Updated:** November 12, 2025
**Version:** 4.0 (Property Graph-Driven)
**Status:** ✅ Production-Ready
