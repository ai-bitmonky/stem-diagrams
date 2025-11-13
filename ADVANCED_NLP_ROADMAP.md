# Advanced NLP Architecture - Gap Analysis & Roadmap
**Date:** November 9, 2025
**Status:** Gap Documented, Roadmap Defined

---

## Executive Summary

**Current State:** Basic NLP implemented (spaCy + custom STEM extractor)
**Roadmap Promise:** Advanced multi-tool NLP ensemble with property graphs and ontologies
**Gap:** 85% of advanced NLP features not yet implemented

This document provides:
1. Clear assessment of what exists vs. what was promised
2. Detailed implementation roadmap for advanced features
3. Architectural design for property graph and ontology layers
4. Prioritized phases for implementation

---

## Current Implementation vs. Roadmap

### ✅ What's Implemented (FAST Mode - 15% of Roadmap)

**Enhanced NLP Adapter** ([core/enhanced_nlp_adapter.py](core/enhanced_nlp_adapter.py))
```python
class EnhancedNLPAdapter:
    - spaCy NER (en_core_web_sm)
    - Custom STEM Unit Extractor (50+ unit patterns)
    - Simple domain classifier (6 domains)
    - Regex-based quantity extraction
```

**Capabilities:**
- ✅ Named entity recognition (spaCy)
- ✅ STEM quantity extraction (custom regex)
- ✅ Unit conversion (kg, N, °, etc.)
- ✅ Domain classification (physics, chemistry, etc.)
- ✅ Backward compatibility with baseline

**Test Results:**
```
Problem: "A 10μF capacitor connected to a 12V battery through a 100Ω resistor"
Extracted:
  - 10.0 μF (capacitance)
  - 12.0 V (voltage)
  - 100.0 Ω (resistance)
Domain: electronics (confidence: 0.85)
```

---

### ❌ What's Missing (ACCURATE/PREMIUM Modes - 85% of Roadmap)

#### 1. Advanced NLP Tools (NOT Implemented)

**Stanza (Stanford NLP)**
- Status: ❌ Not implemented
- Purpose: Dependency parsing, POS tagging, lemmatization
- Use case: Extract grammatical relationships ("connected to", "acts on")
- Installation: `pip install stanza`
- Model size: ~250MB

**DyGIE++ (Allen Institute)**
- Status: ❌ Not implemented
- Purpose: Joint entity and relation extraction for scientific text
- Use case: Extract complex entity relationships from physics problems
- Installation: Custom (requires AllenNLP)
- Model: Pre-trained on SciERC, ChemProt

**SciBERT (Allen Institute)**
- Status: ❌ Not implemented
- Purpose: Scientific domain BERT for better entity extraction
- Use case: Understand scientific terminology and context
- Installation: `transformers` library
- Model: `allenai/scibert_scivocab_uncased`

**ChemDataExtractor**
- Status: ❌ Not implemented
- Purpose: Chemistry-specific NER (compounds, reactions, properties)
- Use case: Extract chemical formulas, reaction mechanisms
- Installation: `pip install chemdataextractor`
- Dependencies: Requires chemistry knowledge bases

**OpenIE (Open Information Extraction)**
- Status: ❌ Not implemented
- Purpose: Extract (subject, relation, object) triples
- Use case: Build knowledge graph from problem text
- Tools: Stanford OpenIE, AllenNLP OpenIE

**AMR (Abstract Meaning Representation)**
- Status: ❌ Not implemented
- Purpose: Semantic representation of sentence meaning
- Use case: Deep semantic understanding of problem structure
- Tools: AMR parsing libraries

#### 2. Property Graph Layer (NOT Implemented)

**Promised Architecture:**
```python
class PropertyGraph:
    """Graph-based knowledge representation"""
    nodes: Dict[str, Node]  # Entities as graph nodes
    edges: List[Edge]       # Relationships as edges

    def add_entity(self, entity: Entity) -> Node
    def add_relationship(self, rel: Relationship) -> Edge
    def query(self, pattern: str) -> List[Match]
    def to_canonical_spec(self) -> CanonicalProblemSpec
```

**Current State:** ❌ Only flat dataclass (CanonicalProblemSpec)

**Gap:**
- No graph-based representation
- No property propagation
- No relationship inference
- No graph queries (Cypher, SPARQL)

#### 3. Ontology Integration (NOT Implemented)

**Promised Features:**
- Physics ontology (forces, motion, energy)
- Chemistry ontology (elements, bonds, reactions)
- Biology ontology (cells, organs, systems)
- Mathematical ontology (functions, proofs, theorems)

**Current State:** ❌ Hard-coded rules only

**Gap:**
- No OWL/RDF ontologies
- No semantic reasoning
- No concept hierarchy
- No knowledge base integration

#### 4. Multi-Stage AI Analysis (PARTIAL)

**Implemented:**
- ✅ UniversalAIAnalyzer class exists
- ✅ Schema files exist (canonical_problem_spec_schema.json, etc.)
- ✅ Multi-stage pipeline structure defined

**Not Implemented:**
- ❌ Actual LLM integration (uses placeholder)
- ❌ DeepSeek API integration
- ❌ Retry logic with exponential backoff
- ❌ Completeness validation
- ❌ Subproblem decomposition

---

## Architecture Comparison

### Current (FAST Mode)

```
Problem Text
    ↓
spaCy NER
    ↓
STEM Unit Extractor (regex)
    ↓
Domain Classifier (keywords)
    ↓
Flat dataclass (dict)
    ↓
Scene Builder
```

**Strengths:**
- Fast (< 0.1s)
- No external dependencies
- Offline-capable
- Reliable for simple problems

**Limitations:**
- No relationship extraction
- Weak on complex grammar
- No semantic understanding
- Limited to explicit quantities

---

### Promised (ACCURATE/PREMIUM Modes)

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
    ↓
CanonicalProblemSpec (enriched)
    ↓
Scene Builder
```

**Strengths:**
- Deep semantic understanding
- Complex relationship extraction
- Handles ambiguous grammar
- Ontology-backed reasoning
- Inference and validation

**Limitations:**
- Slower (5-30s depending on tools)
- Requires external models/APIs
- Higher computational cost
- Network-dependent (for some tools)

---

## Implementation Roadmap

### Phase 1: Property Graph Foundation (4-6 weeks)

**Goal:** Implement graph-based knowledge representation

**Tasks:**
1. Create PropertyGraph class with NetworkX backend
2. Define Node and Edge schemas
3. Implement graph construction from existing NLP results
4. Add graph query interface (pattern matching)
5. Convert graph to CanonicalProblemSpec

**Deliverables:**
- `core/property_graph.py` (500 lines)
- `core/graph_query.py` (300 lines)
- Graph visualization tools
- Unit tests

**Example:**
```python
from core.property_graph import PropertyGraph

graph = PropertyGraph()
graph.add_node("battery", type="component", voltage=12.0)
graph.add_node("resistor", type="component", resistance=100.0)
graph.add_edge("battery", "resistor", relation="connected_to")

# Query
batteries = graph.query("MATCH (n:component {type: 'battery'}) RETURN n")
```

---

### Phase 2: Stanza Integration (2-3 weeks)

**Goal:** Add dependency parsing and POS tagging

**Tasks:**
1. Install and configure Stanza
2. Integrate with existing NLP pipeline
3. Extract grammatical relationships
4. Map dependencies to property graph edges
5. Test on physics/chemistry problems

**Dependencies:**
```bash
pip install stanza
python -c "import stanza; stanza.download('en')"
```

**Implementation:**
```python
class StanzaEnhancer:
    def __init__(self):
        import stanza
        self.nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')

    def extract_relationships(self, text: str) -> List[Relationship]:
        doc = self.nlp(text)
        relationships = []

        for sentence in doc.sentences:
            for word in sentence.words:
                if word.deprel in ['nsubj', 'dobj', 'nmod']:
                    # Extract subject-verb-object triples
                    relationships.append(Relationship(
                        subject=word.text,
                        relation=word.head.text,
                        object=word.text,
                        dependency=word.deprel
                    ))

        return relationships
```

---

### Phase 3: DyGIE++ Integration (3-4 weeks)

**Goal:** Joint entity and relation extraction for scientific text

**Tasks:**
1. Set up AllenNLP environment
2. Load pre-trained DyGIE++ model
3. Integrate with property graph
4. Fine-tune on STEM dataset (if needed)
5. Benchmark against baseline

**Dependencies:**
```bash
pip install allennlp==2.10.1
pip install allennlp-models==2.10.1
# Download DyGIE++ model
```

**Implementation:**
```python
from allennlp.predictors import Predictor

class DyGIEExtractor:
    def __init__(self):
        self.predictor = Predictor.from_path(
            "https://storage.googleapis.com/allennlp-public-models/dygiepp-scierc.tar.gz"
        )

    def extract(self, text: str) -> Tuple[List[Entity], List[Relation]]:
        result = self.predictor.predict(sentence=text)

        entities = []
        for ner in result['ner']:
            entities.append(Entity(
                text=ner[0],
                type=ner[1],
                start=ner[2],
                end=ner[3]
            ))

        relations = []
        for rel in result['relations']:
            relations.append(Relation(
                subject=entities[rel[0]],
                object=entities[rel[1]],
                type=rel[2]
            ))

        return entities, relations
```

---

### Phase 4: SciBERT Integration (2 weeks)

**Goal:** Scientific domain embeddings for better understanding

**Tasks:**
1. Load SciBERT from Hugging Face
2. Generate embeddings for entities
3. Use embeddings for similarity matching
4. Improve domain classification
5. Entity disambiguation

**Dependencies:**
```bash
pip install transformers torch
```

**Implementation:**
```python
from transformers import AutoTokenizer, AutoModel
import torch

class SciBERTEmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
        self.model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')

    def embed(self, text: str) -> torch.Tensor:
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use [CLS] token embedding
        embedding = outputs.last_hidden_state[:, 0, :]
        return embedding

    def similarity(self, text1: str, text2: str) -> float:
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        return torch.cosine_similarity(emb1, emb2).item()
```

---

### Phase 5: Ontology Layer (4-6 weeks)

**Goal:** Domain ontologies for semantic reasoning

**Tasks:**
1. Design physics ontology (OWL/RDF)
2. Implement ontology loader
3. Add reasoning engine (OWL-RL)
4. Integrate with property graph
5. Implement inference rules

**Ontology Structure (Example - Physics):**
```turtle
@prefix phys: <http://stem-diagram.org/ontology/physics#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Classes
phys:Force rdf:type rdfs:Class .
phys:Mass rdf:type rdfs:Class .
phys:Acceleration rdf:type rdfs:Class .

# Properties
phys:actsOn rdf:type rdf:Property ;
    rdfs:domain phys:Force ;
    rdfs:range phys:Mass .

phys:hasMagnitude rdf:type rdf:Property ;
    rdfs:domain phys:Force ;
    rdfs:range xsd:float .

# Inference Rules
{
    ?force rdf:type phys:Force .
    ?force phys:actsOn ?mass .
    ?force phys:hasMagnitude ?f .
    ?mass phys:hasMagnitude ?m .
} => {
    ?mass phys:hasAcceleration (?f / ?m) .  # F = ma
} .
```

**Implementation:**
```python
from rdflib import Graph, Namespace, RDF, RDFS
from owlrl import DeductiveClosure, OWLRL_Semantics

class PhysicsOntology:
    def __init__(self):
        self.graph = Graph()
        self.phys = Namespace("http://stem-diagram.org/ontology/physics#")
        self.graph.bind("phys", self.phys)

        # Load ontology from file
        self.graph.parse("ontologies/physics.ttl", format="turtle")

        # Apply reasoning
        DeductiveClosure(OWLRL_Semantics).expand(self.graph)

    def infer(self, problem_graph: PropertyGraph) -> PropertyGraph:
        """Apply ontology reasoning to enrich problem graph"""
        # Convert problem graph to RDF
        for node in problem_graph.nodes:
            self.graph.add((
                URIRef(node.id),
                RDF.type,
                self.phys[node.type]
            ))

        # Run reasoning
        DeductiveClosure(OWLRL_Semantics).expand(self.graph)

        # Extract inferred facts
        # Add back to problem graph
        return problem_graph
```

---

### Phase 6: OpenIE Integration (2-3 weeks)

**Goal:** Extract (subject, relation, object) triples

**Tasks:**
1. Set up Stanford OpenIE or AllenNLP OpenIE
2. Extract triples from problem text
3. Map triples to property graph
4. Deduplicate and merge with existing extractions
5. Benchmark precision/recall

---

### Phase 7: Full Integration & Testing (3-4 weeks)

**Goal:** Unified advanced NLP pipeline

**Tasks:**
1. Create NLP orchestrator (combines all tools)
2. Implement caching and optimization
3. Add fallback mechanisms
4. Comprehensive testing on benchmark dataset
5. Performance optimization

**Final Architecture:**
```python
class AdvancedNLPPipeline:
    def __init__(self, mode='accurate'):
        self.stanza = StanzaEnhancer()
        self.dygie = DyGIEExtractor()
        self.scibert = SciBERTEmbedder()
        self.openie = OpenIEExtractor()
        self.ontology = PhysicsOntology()

    def process(self, problem_text: str) -> PropertyGraph:
        # Stage 1: Basic NER with Stanza
        entities = self.stanza.extract_entities(problem_text)

        # Stage 2: Relation extraction with DyGIE++
        relations = self.dygie.extract_relations(problem_text)

        # Stage 3: Build property graph
        graph = PropertyGraph()
        for entity in entities:
            graph.add_node(entity)
        for relation in relations:
            graph.add_edge(relation)

        # Stage 4: Enrich with SciBERT embeddings
        graph = self.scibert.enrich_embeddings(graph)

        # Stage 5: Extract additional triples with OpenIE
        triples = self.openie.extract(problem_text)
        graph.merge_triples(triples)

        # Stage 6: Apply ontology reasoning
        graph = self.ontology.infer(graph)

        return graph
```

---

## Files to Create

### Core Infrastructure

1. **core/property_graph.py** (500 lines)
   - PropertyGraph class
   - Node and Edge schemas
   - Graph operations (add, query, merge)
   - Conversion to/from CanonicalProblemSpec

2. **core/graph_query.py** (300 lines)
   - Query language (Cypher-like)
   - Pattern matching
   - Path finding
   - Aggregation

3. **core/advanced_nlp_pipeline.py** (800 lines)
   - NLP orchestrator
   - Tool integration
   - Caching and optimization
   - Fallback mechanisms

4. **core/nlp_tools/stanza_enhancer.py** (400 lines)
   - Stanza integration
   - Dependency parsing
   - POS tagging
   - Relationship extraction

5. **core/nlp_tools/dygie_extractor.py** (500 lines)
   - DyGIE++ integration
   - Entity extraction
   - Relation extraction
   - Fine-tuning utilities

6. **core/nlp_tools/scibert_embedder.py** (300 lines)
   - SciBERT integration
   - Embedding generation
   - Similarity computation
   - Entity disambiguation

7. **core/nlp_tools/openie_extractor.py** (400 lines)
   - OpenIE integration
   - Triple extraction
   - Triple validation
   - Merging with graph

8. **core/ontology/physics_ontology.py** (600 lines)
   - Physics ontology loader
   - Reasoning engine
   - Inference rules
   - Ontology queries

9. **ontologies/physics.ttl** (1000 lines)
   - Physics domain ontology (OWL/RDF)
   - Concepts, properties, rules
   - Inference axioms

10. **ontologies/chemistry.ttl** (1000 lines)
    - Chemistry domain ontology

### Testing & Documentation

11. **tests/test_property_graph.py** (500 lines)
12. **tests/test_advanced_nlp.py** (600 lines)
13. **tests/test_ontology.py** (400 lines)
14. **ADVANCED_NLP_IMPLEMENTATION.md** (this file + progress tracking)

---

## Dependencies

### Required Packages

```txt
# Current (FAST mode)
spacy>=3.7.0

# Phase 1 (Property Graph)
networkx>=3.2.0
rdflib>=7.0.0

# Phase 2 (Stanza)
stanza>=1.6.0

# Phase 3 (DyGIE++)
allennlp==2.10.1
allennlp-models==2.10.1

# Phase 4 (SciBERT)
transformers>=4.35.0
torch>=2.1.0

# Phase 5 (Ontology)
owlrl>=6.0.2
rdflib>=7.0.0

# Phase 6 (OpenIE)
# Stanford CoreNLP or AllenNLP OpenIE

# Optional (Chemistry)
chemdataextractor>=2.1.0

# Optional (AMR)
# AMR parsing libraries
```

### Model Downloads

```bash
# Stanza
python -c "import stanza; stanza.download('en')"

# DyGIE++ (auto-downloaded from AllenNLP)

# SciBERT (auto-downloaded from Hugging Face)
```

---

## Timeline & Effort

| Phase | Duration | Effort | Dependencies |
|-------|----------|--------|--------------|
| Phase 1: Property Graph | 4-6 weeks | 120-150 hours | NetworkX, RDFLib |
| Phase 2: Stanza | 2-3 weeks | 60-80 hours | Phase 1 |
| Phase 3: DyGIE++ | 3-4 weeks | 80-100 hours | Phase 1, AllenNLP |
| Phase 4: SciBERT | 2 weeks | 40-50 hours | Phase 1, Transformers |
| Phase 5: Ontology | 4-6 weeks | 120-150 hours | Phase 1, OWL-RL |
| Phase 6: OpenIE | 2-3 weeks | 60-80 hours | Phase 1 |
| Phase 7: Integration | 3-4 weeks | 80-100 hours | All phases |
| **TOTAL** | **20-29 weeks** | **560-710 hours** | |

**Estimated completion:** 5-7 months (with 1 full-time developer)

---

## Current Workarounds

Until advanced NLP is implemented, the system uses:

1. **Enhanced NLP Adapter** (implemented)
   - spaCy + custom STEM extractor
   - Good enough for simple problems
   - Fast and reliable

2. **UniversalAIAnalyzer** (structure exists, no LLM)
   - Has schema files
   - Has pipeline structure
   - Missing: actual LLM integration

3. **Domain-specific builders** (implemented for physics)
   - Physics builder handles force diagrams well
   - Relies on enhanced NLP quantity extraction
   - Works without property graphs

---

## Priority Recommendation

**High Priority (Next 3 months):**
1. ✅ Property Graph Foundation (Phase 1)
   - Enables all other phases
   - Immediate benefit for scene building
   - Foundation for reasoning

2. ✅ Stanza Integration (Phase 2)
   - Low-hanging fruit (easy integration)
   - Immediate improvement in relationship extraction
   - No training required (pre-trained models)

**Medium Priority (3-6 months):**
3. DyGIE++ Integration (Phase 3)
   - Significant accuracy boost
   - Handles scientific text well

4. SciBERT Integration (Phase 4)
   - Better domain understanding
   - Entity disambiguation

**Lower Priority (6+ months):**
5. Ontology Layer (Phase 5)
   - Complex implementation
   - Requires domain expertise
   - High maintenance

6. OpenIE (Phase 6)
   - Incremental benefit over DyGIE++
   - Redundant with other tools

---

## Testing Strategy

### Benchmark Dataset

Create test suite with:
- 100 physics problems (simple to complex)
- 50 chemistry problems
- 50 biology problems
- Ground truth annotations

### Metrics

1. **Entity Extraction:**
   - Precision, Recall, F1
   - Per entity type

2. **Relation Extraction:**
   - Precision, Recall, F1
   - Per relation type

3. **Graph Quality:**
   - Node count (completeness)
   - Edge accuracy
   - Graph connectivity

4. **End-to-End:**
   - Diagram correctness
   - Physics validation pass rate
   - Processing time

---

## Summary

**Current State:**
- ✅ Basic NLP implemented (15% of roadmap)
- ✅ Works for simple problems
- ✅ Fast and reliable
- ❌ Limited semantic understanding
- ❌ No property graphs
- ❌ No ontology reasoning

**Gap:**
- ❌ 85% of advanced NLP features missing
- ❌ All specialized tools (Stanza, DyGIE++, SciBERT, etc.)
- ❌ Property graph layer
- ❌ Ontology integration
- ❌ Knowledge-backed reasoning

**Roadmap:**
- 7 phases over 5-7 months
- 560-710 hours of development
- Clear prioritization
- Incremental value delivery

**Recommendation:**
Start with Phase 1 (Property Graph) as it enables all other features and provides immediate benefit to scene building and validation.

---

**Status:** Gap Documented, Roadmap Defined
**Next Action:** Prioritize and begin Phase 1 implementation
**Timeline:** 5-7 months for full implementation
**Effort:** ~600 hours total
