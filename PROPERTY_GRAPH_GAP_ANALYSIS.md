# Property Graph Implementation Gap Analysis

**Date:** November 12, 2025
**Issue:** Property graph construction is a stub - no persistence, no ontology integration, no downstream consumers

---

## Executive Summary

**User's Concern:**
> "Property graph construction is a stub. Phase 1 just reports { 'nodes': 9, 'edges': 5 } and moves on, so there is no persistence to Neo4j/ArangoDB, no ontology merge, and no downstream consumers—contrary to the roadmap's knowledge-representation layer."

**Current State:**
- ✅ Full property graph implementation exists ([core/property_graph.py](core/property_graph.py:1-667))
- ✅ Full ontology manager exists ([core/ontology/ontology_manager.py](core/ontology/ontology_manager.py:1-830))
- ❌ Pipeline builds a temporary graph and throws it away
- ❌ Only reports node/edge counts to trace
- ❌ No integration with ontology
- ❌ No downstream consumers
- ❌ No persistence

---

## What Exists (Unused Infrastructure)

### 1. Property Graph Implementation ([core/property_graph.py](core/property_graph.py))

**Full NetworkX-based implementation** with 667 lines of code:

```python
class PropertyGraph:
    """Property graph for knowledge representation using NetworkX"""

    # Node operations
    def add_node(self, node: GraphNode) -> None
    def get_node(self, node_id: str) -> Optional[GraphNode]
    def get_all_nodes(self, node_type: Optional[NodeType] = None) -> List[GraphNode]

    # Edge operations
    def add_edge(self, edge: GraphEdge) -> None
    def get_edges(source, target, edge_type) -> List[GraphEdge]
    def get_neighbors(self, node_id: str) -> List[str]

    # Graph queries
    def query_pattern(self, pattern: Dict) -> List[Dict]
    def find_paths(self, start: str, end: str) -> List[List[str]]
    def find_shortest_path(self, start: str, end: str) -> Optional[List[str]]

    # Graph analysis
    def get_subgraph(self, node_ids: List[str]) -> PropertyGraph
    def get_connected_components(self) -> List[Set[str]]

    # Conversion
    def to_canonical_spec(self) -> Dict
    def from_canonical_spec(cls, spec: Dict) -> PropertyGraph

    # Serialization
    def to_dict(self) -> Dict
    def to_json(self, filepath: str) -> None
    def from_json(cls, filepath: str) -> PropertyGraph
```

**Capabilities:**
- ✅ Typed nodes (OBJECT, FORCE, QUANTITY, etc.)
- ✅ Typed edges (ACTS_ON, CONNECTED_TO, CAUSES, etc.)
- ✅ Property storage on nodes and edges
- ✅ Pattern matching queries
- ✅ Path finding algorithms
- ✅ Connected component analysis
- ✅ JSON serialization
- ✅ Conversion to/from CanonicalProblemSpec

**Status:** Fully implemented but NOT USED

---

### 2. Ontology Manager ([core/ontology/ontology_manager.py](core/ontology/ontology_manager.py))

**Full RDF/OWL ontology implementation** with 830 lines of code:

```python
class OntologyManager:
    """Manages domain-specific OWL/RDF ontologies"""

    # Ontology initialization
    def __init__(self, domain: Domain, enable_reasoning: bool = True)
    def _init_physics_ontology(self) -> None
    def _init_chemistry_ontology(self) -> None
    def _init_biology_ontology(self) -> None

    # Triple management
    def add_triple(self, subject: str, predicate: str, obj: str) -> None
    def add_instance(self, instance_id: str, class_uri: str, properties: Dict) -> None

    # Reasoning
    def apply_reasoning(self) -> List[OntologyTriple]  # OWL-RL inference

    # Validation
    def validate(self, level: ValidationLevel) -> ValidationResult

    # SPARQL queries
    def query(self, sparql_query: str) -> List[Dict]
    def find_instances_of_class(self, class_uri: str) -> List[str]

    # PropertyGraph integration
    def from_property_graph(self, graph: PropertyGraph) -> None
    def to_property_graph(self) -> PropertyGraph

    # RDF export/import
    def export_rdf(self, format: str = 'turtle') -> str
    def import_rdf(self, rdf_data: str) -> None
```

**Capabilities:**
- ✅ Domain ontologies (Physics, Chemistry, Biology)
- ✅ Class hierarchies (Force → GravitationalForce, ElectrostaticForce, etc.)
- ✅ OWL-RL reasoning (inference of new facts)
- ✅ Semantic validation
- ✅ SPARQL queries
- ✅ **Integration with PropertyGraph** (key feature!)
- ✅ RDF/OWL export

**Status:** Fully implemented but NOT USED

---

## What's Actually Happening (Current Pipeline)

### Location: [unified_diagram_pipeline.py:702-748](unified_diagram_pipeline.py#L702-L748)

```python
# Phase 0.5: Property Graph Construction (NEW)
if self.property_graph is not None:
    stage_start_time = time.time()
    if self.logger:
        self.logger.start_phase("Property Graph Construction", 1, "Build knowledge graph from NLP results")
        self.logger.log_phase_input(nlp_results, "NLP extraction results")
    if self.progress:
        self.progress.start_phase("Property Graph", 1)
    print("┌─ PHASE 0.5: PROPERTY GRAPH CONSTRUCTION ──────────────────────┐")

    # Use OpenIE results to build property graph
    if 'openie' in nlp_results:
        current_property_graph = PropertyGraph()  # ❌ LOCAL VARIABLE!
        for subject, relation, obj in nlp_results['openie']['triples']:
            # Add nodes
            subj_node = GraphNode(id=subject, type=NodeType.OBJECT, label=subject)
            obj_node = GraphNode(id=obj, type=NodeType.OBJECT, label=obj)
            current_property_graph.add_node(subj_node)
            current_property_graph.add_node(obj_node)

            # Add edge
            edge = GraphEdge(
                source=subject,
                target=obj,
                type=EdgeType.RELATED_TO,
                label=relation
            )
            current_property_graph.add_edge(edge)

        print(f"  Built graph: {len(current_property_graph.get_all_nodes())} nodes, "
              f"{len(current_property_graph.get_edges())} edges")

    print("└───────────────────────────────────────────────────────────────┘\n")
    graph_output = {
        'nodes': len(current_property_graph.get_all_nodes()) if current_property_graph else 0,
        'edges': len(current_property_graph.get_edges()) if current_property_graph else 0
    }  # ❌ ONLY COUNTS!
    if self.logger:
        self.logger.log_phase_output(graph_output, f"Built graph with {graph_output['nodes']} nodes")
        self.logger.end_phase("success")
    # ❌ Graph is discarded here - goes out of scope!
```

### Problems Identified:

1. **❌ Local Variable:** `current_property_graph` is a local variable that goes out of scope
   - Should be: `self.property_graph` (instance variable)

2. **❌ Only OpenIE Data:** Only uses OpenIE triples
   - Should use: Stanza, SciBERT, ChemDataExtractor, MathBERT, AMR, DyGIE++

3. **❌ Minimal Output:** Only returns `{'nodes': 9, 'edges': 5}`
   - Should return: Full graph structure, node types, edge types, properties

4. **❌ No Ontology Integration:** Doesn't use OntologyManager at all
   - Should: Merge into ontology, apply reasoning, validate semantics

5. **❌ No Downstream Consumers:** Graph is never used by later phases
   - Should: Feed into Scene Builder, Constraint Solver, Validator

6. **❌ No Persistence:** Graph is not saved
   - Should: Export to JSON, optionally persist to Neo4j/ArangoDB

---

## Trace Evidence

**From:** [logs/req_20251111_235806_trace.json:47-88](logs/req_20251111_235806_trace.json#L47-L88)

```json
{
  "phase_number": 1,
  "phase_name": "Property Graph Construction",
  "description": "Build knowledge graph from NLP results",
  "start_time": 1762885698.909285,
  "duration_ms": 1.23,
  "input": {
    "openie": {
      "triples": [
        ["left half", "is filled on", "dielectric κ₁"],
        ["0 and", "bottom on", "κ₃"],
        ["12 mm", "is", "configured as"],
        ["left half", "is", "filled with"],
        ["right half", "is", "divided into"]
      ]
    }
  },
  "output": {
    "nodes": 9,
    "edges": 5
  },
  "logs": [],
  "status": "success"
}
```

**Analysis:**
- ✅ Phase runs and succeeds
- ✅ Receives OpenIE input
- ❌ Output is just counts
- ❌ No actual graph structure
- ❌ No node types
- ❌ No edge types
- ❌ No properties
- ❌ No downstream usage

---

## Roadmap Promise vs Reality

### Roadmap ([ADVANCED_NLP_ROADMAP.md](ADVANCED_NLP_ROADMAP.md))

**Promised Architecture:**

```
Problem Text
    ↓
┌─────────────────────────────────────┐
│ Multi-Tool NLP Ensemble             │
│  ├─ Stanza (dependency parsing)     │
│  ├─ DyGIE++ (relation extraction)   │
│  ├─ SciBERT (domain embeddings)     │
│  ├─ ChemDataExtractor (chemistry)   │
│  ├─ OpenIE (triple extraction)      │
│  └─ AMR (semantic parsing)          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Property Graph Construction         │
│  - Entities as nodes                │
│  - Relationships as edges           │
│  - Properties on nodes/edges        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Ontology Reasoning                  │
│  - Concept hierarchy                │
│  - Inference rules                  │
│  - Semantic validation              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Knowledge Graph Query               │
│  - Pattern matching                 │
│  - Path finding                     │
│  - Aggregation                      │
└─────────────────────────────────────┘
```

**Current Reality:**

```
Problem Text
    ↓
┌─────────────────────────────────────┐
│ Multi-Tool NLP Ensemble             │ ✅ IMPLEMENTED
│  ├─ OpenIE ✅                        │
│  ├─ Stanza ✅                        │
│  ├─ SciBERT ✅                       │
│  ├─ ChemDataExtractor ✅             │
│  ├─ MathBERT ✅                      │
│  ├─ AMR ✅                           │
│  └─ DyGIE++ ⚠️ (Python 3.13)        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Property Graph Construction         │ ❌ STUB
│  - Builds temporary graph           │
│  - Uses only OpenIE                 │
│  - Returns counts only              │
│  - Graph is discarded               │
└─────────────────────────────────────┘
    ↓
❌ NO ONTOLOGY INTEGRATION
❌ NO KNOWLEDGE GRAPH QUERIES
❌ NO DOWNSTREAM CONSUMERS
```

---

## What Needs to Be Implemented

### 1. Multi-Source Graph Construction

**Current:**
```python
# Only uses OpenIE
if 'openie' in nlp_results:
    for subject, relation, obj in nlp_results['openie']['triples']:
        # Add to graph
```

**Should Be:**
```python
# Use ALL NLP tools
graph = PropertyGraph()

# OpenIE: subject-relation-object triples
if 'openie' in nlp_results:
    for triple in nlp_results['openie']['triples']:
        add_openie_triple(graph, triple)

# Stanza: NER entities
if 'stanza' in nlp_results:
    for entity in nlp_results['stanza']['entities']:
        add_ner_entity(graph, entity)

# SciBERT: Scientific entities
if 'scibert' in nlp_results:
    for entity in nlp_results['scibert']['entities']:
        add_scientific_entity(graph, entity)

# ChemDataExtractor: Chemical entities
if 'chemdataextractor' in nlp_results:
    for formula in nlp_results['chemdataextractor']['formulas']:
        add_chemical_entity(graph, formula)

# MathBERT: Mathematical entities
if 'mathbert' in nlp_results:
    for variable in nlp_results['mathbert']['variables']:
        add_math_entity(graph, variable)

# AMR: Semantic concepts
if 'amr' in nlp_results:
    for concept in nlp_results['amr']['concepts']:
        add_semantic_concept(graph, concept)
```

### 2. Ontology Integration

```python
# Create ontology manager for domain
ontology = OntologyManager(domain=Domain.PHYSICS, enable_reasoning=True)

# Import property graph into ontology
ontology.from_property_graph(graph)

# Apply reasoning (infer new facts)
inferences = ontology.apply_reasoning()

# Validate semantic consistency
validation = ontology.validate(ValidationLevel.MODERATE)

# Export enriched graph
enriched_graph = ontology.to_property_graph()
```

### 3. Store Graph as Instance Variable

```python
# BEFORE (line 714):
current_property_graph = PropertyGraph()  # ❌ Local variable

# AFTER:
self.property_graph = PropertyGraph()  # ✅ Instance variable
```

### 4. Rich Trace Output

```python
# BEFORE:
graph_output = {'nodes': 9, 'edges': 5}  # ❌ Just counts

# AFTER:
graph_output = {
    'nodes': graph.get_all_nodes(),  # Full node data
    'edges': graph.get_edges(),      # Full edge data
    'node_types': count_by_type(graph.get_all_nodes()),
    'edge_types': count_by_type(graph.get_edges()),
    'connected_components': len(graph.get_connected_components()),
    'ontology_validation': validation.to_dict() if validation else None,
    'inferences': len(inferences) if inferences else 0
}
```

### 5. Downstream Consumers

**Scene Builder should use property graph:**
```python
# In scene builder
if self.property_graph:
    # Use graph to inform scene construction
    # - Query for spatial relationships
    # - Find connected objects
    # - Infer missing constraints
    spatial_rels = self.property_graph.get_edges(edge_type=EdgeType.LOCATED_AT)
    for edge in spatial_rels:
        # Use to position objects
```

**Constraint Solver should use property graph:**
```python
# In constraint solver
if self.property_graph:
    # Query graph for constraints
    force_relations = self.property_graph.get_edges(edge_type=EdgeType.ACTS_ON)
    for edge in force_relations:
        # Add force constraints
```

### 6. Optional Database Persistence

```python
# Save to JSON
graph.to_json(f"{output_dir}/property_graph.json")

# Optional: Neo4j integration
if config.enable_neo4j:
    from core.graph_db import Neo4jConnector
    connector = Neo4jConnector(config.neo4j_uri)
    connector.save_property_graph(graph)
```

---

## Implementation Priority

### Priority 1: Core Fixes (1-2 hours)
1. ✅ Change `current_property_graph` to `self.property_graph` (store as instance)
2. ✅ Integrate ALL NLP tool outputs (not just OpenIE)
3. ✅ Output full graph structure to trace (not just counts)
4. ✅ Save graph to JSON file

### Priority 2: Ontology Integration (2-4 hours)
1. ✅ Initialize OntologyManager for domain
2. ✅ Import property graph into ontology
3. ✅ Apply OWL-RL reasoning
4. ✅ Validate semantic consistency
5. ✅ Include validation results in trace

### Priority 3: Downstream Integration (4-8 hours)
1. ⚠️  Use property graph in Scene Builder
2. ⚠️  Use property graph in Constraint Solver
3. ⚠️  Use property graph in Validator

### Priority 4: Database Persistence (Optional)
1. ⚪ Neo4j connector
2. ⚪ ArangoDB connector
3. ⚪ Configuration for database backends

---

## Benefits of Full Implementation

### 1. Rich Knowledge Representation
- **Current:** 5 brittle triples from OpenIE
- **After:** Multi-source knowledge graph with types, properties, and semantic validation

### 2. Semantic Validation
- **Current:** No validation of extracted knowledge
- **After:** OWL-RL reasoning + domain-specific constraint checking

### 3. Downstream Integration
- **Current:** NLP results are ignored by later phases
- **After:** Knowledge graph informs scene construction, constraints, and validation

### 4. Debugging & Inspection
- **Current:** Can't inspect what was understood from text
- **After:** Full graph export shows all entities, relationships, and inferences

### 5. Extensibility
- **Current:** Adding new NLP tools is ad-hoc
- **After:** Standardized graph representation enables easy integration

---

## Summary

| Component | Implementation Status | Usage Status | Gap |
|-----------|---------------------|--------------|-----|
| PropertyGraph class | ✅ Fully implemented (667 lines) | ❌ Not used | 100% |
| OntologyManager class | ✅ Fully implemented (830 lines) | ❌ Not used | 100% |
| Multi-tool NLP | ✅ 6/7 tools working | ⚠️  Only OpenIE used for graph | 85% |
| Graph construction | ✅ Code exists | ❌ Builds then discards | 80% |
| Ontology integration | ✅ Methods exist | ❌ Never called | 100% |
| Downstream consumers | ⚠️  Could integrate | ❌ Not integrated | 100% |
| Persistence | ✅ JSON methods exist | ❌ Never called | 100% |

**Bottom Line:**
- We have ~1500 lines of sophisticated graph/ontology code
- It's almost completely unused
- Pipeline builds a temporary graph from 1 tool and throws it away
- User is absolutely correct: "Property graph construction is a stub"

**Next Step:** Implement Priority 1 fixes to make property graph actually useful.

---

**Files Referenced:**
- [core/property_graph.py](core/property_graph.py) - Full implementation (667 lines)
- [core/ontology/ontology_manager.py](core/ontology/ontology_manager.py) - Full implementation (830 lines)
- [unified_diagram_pipeline.py:702-748](unified_diagram_pipeline.py#L702-L748) - Current stub
- [logs/req_20251111_235806_trace.json:47-88](logs/req_20251111_235806_trace.json#L47-L88) - Evidence
- [ADVANCED_NLP_ROADMAP.md](ADVANCED_NLP_ROADMAP.md) - Promised architecture

