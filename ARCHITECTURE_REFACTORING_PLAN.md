# Architecture Refactoring Plan - Roadmap Compliance
**Date:** November 12, 2025
**Status:** IN PROGRESS

---

## Executive Summary

**Problem:** The current pipeline builds a property graph from NLP tools but then **ignores it** and still calls UniversalAIAnalyzer which hits DeepSeek to extract specs. DiagramPlanner exists but is only used for complexity assessment, not actual planning from the property graph.

**Solution:** Refactor to a **property graph-driven architecture** where:
1. Local NLP tools extract entities/relations → Property graph
2. DiagramPlanner consumes property graph → DiagramPlan (5-stage: EntityExtractor → RelationMapper → ConstraintGenerator → LayoutPlanner → StyleAssigner)
3. DeepSeek used ONLY for 3 targeted calls (enrichment, audit, validation)
4. Domain modules query primitive library first
5. Z3/SymPy constraint solving in layout
6. VLM validation at the end

---

## Current Architecture (WRONG)

### Flow Diagram
```
User Request
    ↓
[Phase 0] NLP Tools (OpenIE, Stanza, SciBERT, etc.)
    ↓
[Phase 0.5] Property Graph Construction ✅
    ↓
[Phase 0.6] DeepSeek Enrichment (Call #1) ✅
    ↓
[Phase 1] UniversalAIAnalyzer.analyze() ❌
    ↓  (Hits DeepSeek to extract CanonicalProblemSpec)
    ↓
[Phase 2] DiagramPlanner (only complexity/strategy) ❌
    ↓
[Phase 2] UniversalSceneBuilder.build() ❌
    ↓  (Uses specs from LLM, ignores property graph)
    ↓
[Phase 3] Validation → Rendering
```

### Critical Issues

1. **Property Graph Ignored**: Built in Phase 0.5 but not used for planning
2. **LLM-First Extraction**: UniversalAIAnalyzer hits DeepSeek for extraction (should be local-first)
3. **DiagramPlanner Underutilized**: Only does complexity/strategy, not 5-stage planning
4. **No Staged Planning**: Missing EntityExtractor → RelationMapper → ConstraintGenerator → LayoutPlanner → StyleAssigner
5. **No Primitive Library Integration**: Domain modules don't query vector DB first
6. **Z3/SymPy Not Used**: Layout engine doesn't use constraint solving (z3_used: false)
7. **No VLM Validation**: Missing LLaVA/BLIP-2 visual validation

---

## Target Architecture (CORRECT - Roadmap Compliant)

### Flow Diagram
```
User Request
    ↓
╔════════════════════════════════════════════════════════════════╗
║ LAYER 1: Text & Diagram Understanding                         ║
╚════════════════════════════════════════════════════════════════╝
    ↓
[1.1] Multi-NLP Stack (LOCAL)
      • spaCy 3.x - NER, POS, dependencies
      • Stanza - Universal dependencies
      • DyGIE++ - Scientific entity/relation extraction
      • SciBERT - Scientific embeddings
      • ChemDataExtractor - Chemical entities
      • MathBERT - Mathematical entities
      • OpenIE 5 - Open triple extraction
      • AMR - Abstract meaning representation
    ↓
[1.2] Property Graph Construction (Neo4j/NetworkX)
      • Nodes: Entities with types, properties, ontology links
      • Edges: Relations with types, constraints
      • Enrichment: PhySH, ChEBI, GO ontologies
    ↓
[1.3] **DeepSeek API Call #1: Entity Enrichment** (ONLY for gaps)
      • Validate extracted entities
      • Add missing implicit properties (e.g., switch default state)
      • Identify missing entities from conventions
    ↓
╔════════════════════════════════════════════════════════════════╗
║ LAYER 2: Diagram Planning & Reasoning (NEW ARCHITECTURE)      ║
╚════════════════════════════════════════════════════════════════╝
    ↓
[2.1] DiagramPlanner.plan_from_property_graph()
      ┌─────────────────────────────────────────────────────┐
      │ Stage 1: EntityExtractor                            │
      │ • Extract drawable entities from property graph     │
      │ • Filter out non-visual concepts                    │
      │ • Map to domain primitives                          │
      ├─────────────────────────────────────────────────────┤
      │ Stage 2: RelationMapper                             │
      │ • Extract relationships between entities            │
      │ • Infer implicit relationships                      │
      │ • Map to visual connections                         │
      ├─────────────────────────────────────────────────────┤
      │ Stage 3: ConstraintGenerator                        │
      │ • Generate layout constraints from relations        │
      │ • Add domain-specific rules (Kirchhoff, Newton)    │
      │ • Add geometric constraints (alignment, spacing)    │
      ├─────────────────────────────────────────────────────┤
      │ Stage 4: LayoutPlanner                              │
      │ • Assign positions using constraints                │
      │ • Z3/SymPy constraint solving                       │
      │ • Cassowary for flexible layout                     │
      ├─────────────────────────────────────────────────────┤
      │ Stage 5: StyleAssigner                              │
      │ • Assign visual styles based on entity types        │
      │ • Domain-specific styling rules                     │
      │ • Color, size, shape selection                      │
      └─────────────────────────────────────────────────────┘
      ↓
      **DiagramPlan** (complete plan with entities, relations, constraints, layout hints, styles)
    ↓
[2.2] **LLMDiagramPlanner** (Optional - Local Mistral/Llama)
      • Generate alternative plan using local LLM
      • Compare with property-graph plan
      • Merge insights
    ↓
[2.3] **ModelOrchestrator** (Complexity-driven routing)
      • Assess complexity of DiagramPlan
      • Route to appropriate solver:
        - Low complexity: Local heuristics
        - Medium: Z3/CVC5 SMT solver
        - High: SymPy symbolic solver
        - Very high: Hybrid approach
    ↓
[2.4] **DeepSeek API Call #2: Plan Auditing** (ONLY if high complexity)
      • Verify plan correctness
      • Check domain rules (Kirchhoff, Newton, stoichiometry)
      • Identify missing/incorrect elements
    ↓
╔════════════════════════════════════════════════════════════════╗
║ LAYER 3: Domain Modules & Primitive Library                   ║
╚════════════════════════════════════════════════════════════════╝
    ↓
[3.1] Domain Module Selection (based on plan domain)
      • Electronics: SchemDraw, CircuitikZ
      • Mechanics: PySketcher, custom SVG
      • Chemistry: RDKit, ChemDraw
      • Biology: Cytoscape, Bio icons
      • Math/CS: Graphviz, TikZ
    ↓
[3.2] **Primitive Library Query** (Milvus/Qdrant)
      • Query vector DB for each entity
      • Retrieve prebuilt SVG primitives
      • Similarity search with SciBERT embeddings
      • FALLBACK: Procedural generation if not found
    ↓
[3.3] Component Generation
      • Use retrieved primitives OR generate procedurally
      • Apply layout hints from DiagramPlan
      • Apply styles from StyleAssigner
    ↓
╔════════════════════════════════════════════════════════════════╗
║ LAYER 4: Rendering & Output                                   ║
╚════════════════════════════════════════════════════════════════╝
    ↓
[4.1] SVG Assembly
      • Combine components into scene graph
      • Apply constraints with Z3/SymPy/Cassowary
      • Optimize label placement
    ↓
[4.2] SVG Optimization
      • svgo or scour post-processing
      • File size reduction
    ↓
╔════════════════════════════════════════════════════════════════╗
║ LAYER 5: Validation & QA                                      ║
╚════════════════════════════════════════════════════════════════╝
    ↓
[5.1] Structural Validation
      • Compare SVG graph with DiagramPlan graph (isomorphism)
      • Check all entities present
      • Check all connections present
    ↓
[5.2] Domain Rule Validation
      • Electrical: Kirchhoff's laws (Z3 verification)
      • Mechanics: Newton's laws, force balance
      • Chemistry: Mass balance, stoichiometry
      • Geometry: Angle sums, parallel/perpendicular
    ↓
[5.3] **VLM Validation** (Local LLaVA or BLIP-2)
      • Generate description of SVG
      • Extract visual elements seen
    ↓
[5.4] **DeepSeek API Call #3: Semantic Fidelity**
      • Compare original request with VLM description
      • Semantic match score (0-100)
      • Identify discrepancies
    ↓
[5.5] **Refinement Loop** (if validation fails)
      • Retry up to 3 times
      • Adjust plan based on validation feedback
      • Re-render
    ↓
╔════════════════════════════════════════════════════════════════╗
║ FINAL OUTPUT                                                   ║
╚════════════════════════════════════════════════════════════════╝
    ↓
Validated SVG Diagram
```

---

## Implementation Plan

### Phase 1: DiagramPlanner Refactoring ⚙️

#### 1.1. Create `plan_from_property_graph()` Method

**File:** `core/diagram_planner.py`

**New Method:**
```python
def plan_from_property_graph(self,
                             property_graph: PropertyGraph,
                             problem_text: str,
                             domain: Optional[str] = None) -> DiagramPlan:
    """
    Create diagram plan FROM property graph (roadmap-compliant)

    This is the NEW primary planning method that doesn't require LLM extraction.

    5-Stage Pipeline:
    1. EntityExtractor: Extract drawable entities from graph
    2. RelationMapper: Map graph edges to visual relations
    3. ConstraintGenerator: Generate layout constraints
    4. LayoutPlanner: Solve constraints with Z3/SymPy
    5. StyleAssigner: Assign visual styles

    Args:
        property_graph: PropertyGraph built from NLP tools
        problem_text: Original request (for context)
        domain: Optional domain hint

    Returns:
        DiagramPlan ready for rendering
    """
    # Initialize plan
    plan = DiagramPlan(
        original_request=problem_text,
        complexity_score=0.0,
        strategy=PlanningStrategy.CONSTRAINT_BASED,
        canvas_width=1200,
        canvas_height=800
    )

    # STAGE 1: EntityExtractor
    entities = self._extract_entities(property_graph, domain)
    plan.entities = entities
    plan.log_planning_step('entity_extraction', {
        'entity_count': len(entities),
        'types': [e.type for e in entities]
    })

    # STAGE 2: RelationMapper
    relations = self._map_relations(property_graph, entities)
    plan.relationships = relations
    plan.log_planning_step('relation_mapping', {
        'relation_count': len(relations),
        'types': [r.type for r in relations]
    })

    # STAGE 3: ConstraintGenerator
    constraints = self._generate_constraints(entities, relations, domain)
    plan.constraints = constraints
    plan.log_planning_step('constraint_generation', {
        'constraint_count': len(constraints),
        'types': [c.type for c in constraints]
    })

    # STAGE 4: LayoutPlanner
    layout = self._plan_layout(entities, constraints)
    plan.layout_hints = layout
    plan.log_planning_step('layout_planning', {
        'solver_used': layout['solver'],
        'positions_assigned': len(layout.get('positions', {}))
    })

    # STAGE 5: StyleAssigner
    styles = self._assign_styles(entities, domain)
    plan.style_hints = styles
    plan.log_planning_step('style_assignment', {
        'styles_assigned': len(styles)
    })

    # Assess complexity
    plan.complexity_score = self._assess_complexity_from_plan(plan)

    return plan
```

#### 1.2. Implement 5 Stages

**EntityExtractor:**
```python
def _extract_entities(self, graph: PropertyGraph, domain: Optional[str]) -> List[DiagramEntity]:
    """Extract drawable entities from property graph"""
    entities = []

    for node in graph.get_all_nodes():
        # Skip non-visual concepts (abstract relations, etc.)
        if self._is_drawable(node):
            entity = DiagramEntity(
                id=node.id,
                type=node.type,
                label=node.label,
                properties=node.properties,
                primitive_hint=self._get_primitive_hint(node, domain)
            )
            entities.append(entity)

    return entities

def _is_drawable(self, node: GraphNode) -> bool:
    """Check if node represents a drawable entity"""
    # Skip abstract concepts like 'connected', 'circuit', etc.
    abstract_types = ['CONCEPT', 'RELATION', 'ACTION']
    if node.type in abstract_types:
        return False

    # Check if node represents physical object
    physical_indicators = ['battery', 'resistor', 'switch', 'wire',
                          'mass', 'spring', 'pulley', 'force',
                          'molecule', 'atom', 'bond']

    return any(ind in node.label.lower() for ind in physical_indicators)
```

**RelationMapper:**
```python
def _map_relations(self, graph: PropertyGraph, entities: List[DiagramEntity]) -> List[DiagramRelation]:
    """Map graph edges to visual relations"""
    relations = []
    entity_ids = {e.id for e in entities}

    for edge in graph.get_edges():
        # Only include relations between drawable entities
        if edge.source in entity_ids and edge.target in entity_ids:
            relation = DiagramRelation(
                source_id=edge.source,
                target_id=edge.target,
                type=self._map_edge_type_to_visual(edge.type, edge.label),
                label=edge.label,
                properties=edge.metadata
            )
            relations.append(relation)

    # Infer implicit relations (e.g., "series connection")
    implicit_relations = self._infer_implicit_relations(entities, relations)
    relations.extend(implicit_relations)

    return relations
```

**ConstraintGenerator:**
```python
def _generate_constraints(self, entities: List[DiagramEntity],
                         relations: List[DiagramRelation],
                         domain: Optional[str]) -> List[LayoutConstraint]:
    """Generate layout constraints from entities and relations"""
    constraints = []

    # 1. Geometric constraints from relations
    for rel in relations:
        if rel.type == 'CONNECTED':
            # Connected entities should be close
            constraints.append(create_distance_constraint(
                rel.source_id, rel.target_id,
                min_dist=50, max_dist=200, priority=ConstraintPriority.HIGH
            ))
        elif rel.type == 'SERIES':
            # Series connections should be aligned
            constraints.append(create_alignment_constraint(
                rel.source_id, rel.target_id,
                axis='horizontal', priority=ConstraintPriority.HIGH
            ))

    # 2. Domain-specific constraints
    if domain == 'electronics':
        # Closed loop constraint for circuits
        if self._forms_closed_loop(relations):
            constraints.append(LayoutConstraint(
                type='CLOSED_LOOP',
                entities=self._get_loop_entities(relations),
                priority=ConstraintPriority.CRITICAL,
                properties={'domain_rule': 'Kirchhoff'}
            ))

    # 3. No-overlap constraints (all entities)
    for i, e1 in enumerate(entities):
        for e2 in entities[i+1:]:
            constraints.append(create_no_overlap_constraint(e1.id, e2.id))

    # 4. Bounds constraints (all entities within canvas)
    for entity in entities:
        constraints.append(create_bounds_constraint(
            entity.id, 0, 0, 1200, 800
        ))

    return constraints
```

**LayoutPlanner:**
```python
def _plan_layout(self, entities: List[DiagramEntity],
                constraints: List[LayoutConstraint]) -> Dict[str, Any]:
    """Plan layout using constraint solving"""

    # Determine solver based on complexity
    if len(entities) <= 5:
        solver = 'heuristic'
    elif len(entities) <= 15:
        solver = 'z3'
    else:
        solver = 'sympy'

    layout = {
        'solver': solver,
        'positions': {},
        'constraints_satisfied': []
    }

    if solver == 'z3':
        # Use Z3 SMT solver
        from core.z3_layout_solver import Z3LayoutSolver
        z3_solver = Z3LayoutSolver()
        solution = z3_solver.solve(entities, constraints)
        layout['positions'] = solution.positions
        layout['constraints_satisfied'] = solution.satisfied_constraints
        layout['z3_used'] = True

    elif solver == 'sympy':
        # Use SymPy symbolic solver
        from core.sympy_solver import SymPyLayoutSolver
        sympy_solver = SymPyLayoutSolver()
        solution = sympy_solver.solve_layout(entities, constraints)
        layout['positions'] = solution.positions
        layout['sympy_used'] = True

    else:
        # Simple heuristic layout
        layout['positions'] = self._heuristic_layout(entities, constraints)
        layout['heuristic_used'] = True

    return layout
```

**StyleAssigner:**
```python
def _assign_styles(self, entities: List[DiagramEntity],
                  domain: Optional[str]) -> Dict[str, Dict]:
    """Assign visual styles based on entity types and domain"""
    styles = {}

    for entity in entities:
        style = {
            'color': self._get_color_for_type(entity.type, domain),
            'size': self._get_size_for_type(entity.type),
            'shape': self._get_shape_for_type(entity.type),
            'stroke_width': 2,
            'font_size': 14
        }

        # Domain-specific style overrides
        if domain == 'electronics':
            if 'battery' in entity.label.lower():
                style['symbol'] = 'battery_symbol'
            elif 'resistor' in entity.label.lower():
                style['symbol'] = 'resistor_zigzag'

        styles[entity.id] = style

    return styles
```

---

### Phase 2: Pipeline Flow Refactoring 🔄

**File:** `unified_diagram_pipeline.py`

**Current Phase 1 (REMOVE/REPLACE):**
```python
# Phase 1: Problem Understanding
specs = self.ai_analyzer.analyze(problem_text)  # ❌ Hits DeepSeek
domain = specs.domain
```

**New Phase 1 (PROPERTY GRAPH-DRIVEN):**
```python
# Phase 1: Diagram Planning (from property graph - NO LLM NEEDED)
stage_start_time = time.time()
print("┌─ PHASE 1: DIAGRAM PLANNING (Property Graph-Driven) ───────────┐")

# NEW: Plan from property graph instead of LLM extraction
if self.diagram_planner and self.property_graph:
    diagram_plan = self.diagram_planner.plan_from_property_graph(
        property_graph=self.property_graph,
        problem_text=problem_text,
        domain=None  # Will be inferred from graph
    )

    print(f"  ✅ DiagramPlan created from property graph:")
    print(f"     • Entities: {len(diagram_plan.entities)}")
    print(f"     • Relations: {len(diagram_plan.relationships)}")
    print(f"     • Constraints: {len(diagram_plan.constraints)}")
    print(f"     • Complexity: {diagram_plan.complexity_score:.2f}")
    print(f"     • Strategy: {diagram_plan.strategy.value}")

    # Extract domain from plan
    domain = diagram_plan.domain or PhysicsDomain.MECHANICS

    # Build CanonicalProblemSpec from DiagramPlan (for backward compatibility)
    specs = self._diagram_plan_to_canonical_spec(diagram_plan)
else:
    # FALLBACK: Use old method if property graph unavailable
    print("  ⚠️  Property graph unavailable, falling back to LLM extraction")
    specs = self.ai_analyzer.analyze(problem_text)
    domain = specs.domain

print("└───────────────────────────────────────────────────────────────┘\n")
```

**Add Conversion Method:**
```python
def _diagram_plan_to_canonical_spec(self, plan: DiagramPlan) -> CanonicalProblemSpec:
    """Convert DiagramPlan to CanonicalProblemSpec for backward compatibility"""
    return CanonicalProblemSpec(
        domain=plan.domain,
        objects=[{
            'id': e.id,
            'type': e.type,
            'label': e.label,
            'properties': e.properties
        } for e in plan.entities],
        relationships=[{
            'source': r.source_id,
            'target': r.target_id,
            'type': r.type
        } for r in plan.relationships],
        constraints=[{
            'type': c.type,
            'entities': c.entities,
            'priority': c.priority
        } for c in plan.constraints]
    )
```

---

### Phase 3: Primitive Library Integration 📚

**File:** `core/primitive_library.py`

**Current (Stub):**
```python
def query(self, text: str, top_k: int = 5) -> List[DiagramPrimitive]:
    """Query for similar primitives (STUB - returns empty)"""
    return []
```

**New (Milvus/Qdrant Implementation):**
```python
def query(self, text: str, top_k: int = 5,
         category: Optional[PrimitiveCategory] = None) -> List[DiagramPrimitive]:
    """
    Query primitive library for similar components

    Args:
        text: Entity description (e.g., "resistor", "battery")
        top_k: Number of results to return
        category: Optional category filter

    Returns:
        List of matching primitives sorted by similarity
    """
    if self.backend == "stub":
        self.logger.warning("Primitive library is stub - no primitives available")
        return []

    # 1. Generate query embedding with SciBERT
    if not self.embedder:
        from core.nlp.scibert_embedder import SciBERTEmbedder
        self.embedder = SciBERTEmbedder()

    query_embedding = self.embedder.embed(text)

    # 2. Query vector database
    if self.backend == "milvus":
        results = self._query_milvus(query_embedding, top_k, category)
    elif self.backend == "qdrant":
        results = self._query_qdrant(query_embedding, top_k, category)
    else:
        raise ValueError(f"Unknown backend: {self.backend}")

    # 3. Convert to DiagramPrimitive objects
    primitives = []
    for result in results:
        primitive = DiagramPrimitive(
            id=result['id'],
            name=result['name'],
            category=PrimitiveCategory(result['category']),
            svg_content=result['svg_content'],
            tags=result['tags'],
            similarity_score=result['score']
        )
        primitives.append(primitive)

    return primitives

def _query_milvus(self, embedding, top_k, category):
    """Query Milvus vector database"""
    from pymilvus import connections, Collection

    # Connect to Milvus
    connections.connect(host=self.host, port=self.port)

    # Get collection
    collection = Collection(self.collection_name)

    # Search
    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

    filter_expr = f"category == '{category.value}'" if category else None

    results = collection.search(
        data=[embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=filter_expr
    )

    # Format results
    formatted = []
    for hit in results[0]:
        formatted.append({
            'id': hit.id,
            'name': hit.entity.get('name'),
            'category': hit.entity.get('category'),
            'svg_content': hit.entity.get('svg_content'),
            'tags': hit.entity.get('tags'),
            'score': hit.score
        })

    return formatted
```

**Domain Module Integration:**

**File:** `domains/electronics/interpreter.py`

**Before:**
```python
def interpret(self, spec_dict):
    # Generate components procedurally
    battery_svg = self._generate_battery_svg()
    resistor_svg = self._generate_resistor_svg()
    # ...
```

**After:**
```python
def interpret(self, spec_dict, primitive_library=None):
    components = []

    for entity in spec_dict['objects']:
        # 1. Try primitive library first
        if primitive_library:
            primitives = primitive_library.query(
                text=entity['label'],
                top_k=1,
                category=PrimitiveCategory.ELECTRONICS
            )

            if primitives:
                # Use retrieved primitive
                component = self._use_primitive(primitives[0], entity)
                components.append(component)
                continue

        # 2. FALLBACK: Procedural generation
        if 'battery' in entity['label'].lower():
            component = self._generate_battery_svg(entity)
        elif 'resistor' in entity['label'].lower():
            component = self._generate_resistor_svg(entity)
        # ...

        components.append(component)

    return components
```

---

### Phase 4: VLM Validation Integration 👁️

**New File:** `core/vlm_validator.py`

```python
"""
VLM (Vision-Language Model) Validator
Uses LLaVA or BLIP-2 for visual validation of diagrams
"""

from typing import Dict, Any, Optional
import base64
import io
from PIL import Image
from cairosvg import svg2png


class VLMValidator:
    """
    Visual validation using Vision-Language Models

    Supported backends:
    - llava: Local LLaVA model (best quality, requires GPU)
    - blip2: BLIP-2 via transformers (lighter, CPU-friendly)
    - mock: Stub for testing
    """

    def __init__(self, backend: str = "blip2", device: str = "cpu"):
        """
        Initialize VLM validator

        Args:
            backend: VLM backend ('llava', 'blip2', 'mock')
            device: 'cpu' or 'cuda'
        """
        self.backend = backend
        self.device = device
        self.model = None
        self.processor = None

        if backend == "blip2":
            from transformers import Blip2Processor, Blip2ForConditionalGeneration
            self.processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                "Salesforce/blip2-opt-2.7b",
                device_map=device
            )
        elif backend == "llava":
            # TODO: Implement LLaVA integration
            raise NotImplementedError("LLaVA backend not yet implemented")

    def validate_svg(self, svg_content: str,
                    original_request: str) -> Dict[str, Any]:
        """
        Validate SVG diagram using VLM

        Args:
            svg_content: SVG diagram string
            original_request: Original user request

        Returns:
            Validation result with description and elements
        """
        # 1. Convert SVG to PNG for VLM
        png_data = svg2png(bytestring=svg_content.encode('utf-8'))
        image = Image.open(io.BytesIO(png_data))

        # 2. Generate description using VLM
        if self.backend == "blip2":
            description = self._describe_with_blip2(image)
        elif self.backend == "llava":
            description = self._describe_with_llava(image)
        else:
            description = "Mock VLM description"

        # 3. Extract elements from description
        elements = self._extract_elements_from_description(description)

        return {
            'description': description,
            'elements': elements,
            'model': self.backend
        }

    def _describe_with_blip2(self, image: Image.Image) -> str:
        """Generate description using BLIP-2"""
        prompt = "Describe this scientific diagram in detail, listing all components and their connections."

        inputs = self.processor(image, text=prompt, return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(**inputs, max_new_tokens=200)
        description = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return description.strip()

    def _extract_elements_from_description(self, description: str) -> list:
        """Extract elements from VLM description"""
        # Simple keyword extraction (can be enhanced with NLP)
        keywords = ['battery', 'resistor', 'switch', 'wire', 'capacitor',
                   'mass', 'spring', 'pulley', 'force', 'arrow',
                   'molecule', 'atom', 'bond', 'label']

        found_elements = []
        description_lower = description.lower()

        for keyword in keywords:
            if keyword in description_lower:
                found_elements.append(keyword)

        return found_elements
```

**Integration in Pipeline:**

**File:** `unified_diagram_pipeline.py`

**Add before DeepSeek semantic validation:**
```python
# Phase 6.3: VLM Validation (NEW)
vlm_description = None
vlm_elements = []

if self.vlm_validator:
    print("  Running VLM validation...")
    vlm_result = self.vlm_validator.validate_svg(svg, problem_text)
    vlm_description = vlm_result['description']
    vlm_elements = vlm_result['elements']

    print(f"    VLM Description: {vlm_description}")
    print(f"    VLM Elements: {', '.join(vlm_elements)}")

    validation_results['vlm'] = vlm_result
```

---

## Testing Strategy

### Test 1: Simple Circuit (End-to-End)

**Input:**
```
"Draw a simple DC circuit with a 12V battery connected in series to a 100-ohm resistor and a switch."
```

**Expected Flow:**
1. NLP tools extract: Battery_1 (12V), Resistor_1 (100Ω), Switch_1
2. Property graph built with 3 nodes, 2 edges (series connections)
3. DeepSeek enrichment adds Switch_1.state = "open"
4. DiagramPlanner creates plan with 3 entities, 2 relations, 8 constraints
5. Z3 solver used for layout (closed loop constraint)
6. Primitive library queries return: battery.svg, resistor.svg, switch.svg
7. SVG rendered with constraint-based layout
8. VLM validates: "A circuit with a battery, resistor, and switch"
9. DeepSeek semantic validation confirms match

**Success Criteria:**
- ✅ Property graph has 3 nodes
- ✅ DiagramPlan created without LLM extraction call
- ✅ z3_used: true in metadata
- ✅ Primitive library queried (3 primitives retrieved)
- ✅ VLM description mentions all 3 components
- ✅ DeepSeek semantic fidelity score >= 90

---

## Migration Path

### Step 1: Implement New Methods (No Breaking Changes)
- Add `plan_from_property_graph()` to DiagramPlanner
- Add 5-stage methods to DiagramPlanner
- Add Milvus query to PrimitiveLibrary
- Add VLMValidator class

### Step 2: Add Configuration Flags
```python
use_property_graph_planning: bool = True  # Toggle new architecture
use_primitive_library: bool = True  # Toggle primitive queries
use_vlm_validation: bool = True  # Toggle VLM
```

### Step 3: Dual-Path Implementation
- Keep old path as fallback
- Add new path with flag checks
- Test both paths in parallel

### Step 4: Deprecate Old Path
- Remove UniversalAIAnalyzer extraction
- Remove direct procedural generation
- Make new path default

---

## Timeline Estimate

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| **Phase 1** | DiagramPlanner refactoring (5 stages) | 8 hours |
| **Phase 2** | Pipeline flow refactoring | 4 hours |
| **Phase 3** | Primitive library integration | 6 hours |
| **Phase 4** | VLM validation integration | 4 hours |
| **Testing** | End-to-end testing + bug fixes | 6 hours |
| **Total** | | **28 hours** |

---

## Conclusion

This refactoring will transform the pipeline from an **LLM-first extraction architecture** to a **property graph-driven planning architecture** that fully complies with the roadmap specification.

**Key Changes:**
1. ✅ Property graph actually drives planning (not ignored)
2. ✅ 5-stage DiagramPlanner (EntityExtractor → RelationMapper → ConstraintGenerator → LayoutPlanner → StyleAssigner)
3. ✅ DeepSeek only for 3 targeted calls (enrichment, audit, validation)
4. ✅ Primitive library queries before procedural generation
5. ✅ Z3/SymPy constraint solving in layout
6. ✅ VLM validation with LLaVA/BLIP-2
7. ✅ Roadmap-compliant 6-layer architecture

**Next Step:** Start Phase 1 implementation with DiagramPlanner refactoring.
