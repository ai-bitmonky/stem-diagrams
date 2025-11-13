# Text Understanding & Knowledge Integration Gap Analysis
**Date:** November 6, 2025
**Critical Issue:** Limited NLP stack, missing knowledge layer, DeepSeek dependency

---

## Executive Summary

**The Problem:** Current text understanding is limited to spaCy + regex with a flat dataclass representation. The roadmap envisions a multi-tool, knowledge-backed interpretation layer with property graphs and ontologies.

**Key Gaps:**
1. **Limited NLP Stack:** Only spaCy + regex (missing SciBERT, Stanza, AllenNLP)
2. **DeepSeek Dependency:** Paid API ($0.14/$1.10 per million tokens), not open-source
3. **Missing Schema Files:** stage_2_schema.json, stage_3_schema.json not in repo
4. **Flat Representation:** Simple dataclass, no property graph or ontology
5. **No Knowledge Integration:** Missing domain ontologies, knowledge graphs

**Impact:** Cannot achieve roadmap's vision of "multi-tool, knowledge-backed interpretation"

---

## Current State Analysis

### 1. NLP Stack (core/nlp_pipeline/unified_nlp_pipeline.py)

**What Exists:**
```python
# Line 83-84
self.nlp = spacy.load(spacy_model)  # Only spaCy!

# Line 99-101
if enable_scibert:
    self._initialize_scibert()  # Mentioned but not implemented
```

**Stack Components:**
- ✅ spaCy (en_core_web_sm) - Working
- ⚠️ SciBERT - Referenced but not implemented
- ❌ Stanza - Not mentioned
- ❌ AllenNLP - Not mentioned
- ❌ DyGIE++ - Not mentioned
- ✅ Regex extractors - Working (basic)

**Limitations:**
- Single NLP model (spaCy general domain, not scientific)
- No ensemble/multi-tool approach
- No domain-specific language models
- Basic entity extraction only

---

### 2. AI Analyzer (core/universal_ai_analyzer.py)

**DeepSeek Dependency:**
```python
# Line 107-108
def __init__(self, api_key: str,
             api_base_url: str = "https://api.deepseek.com/v1/chat/completions",
             api_model: str = "deepseek-chat", ...):
```

**Issues:**
- **Not Open Source:** Requires paid API key
- **Vendor Lock-in:** Tied to DeepSeek service
- **Cost:** $0.14 (input) / $1.10 (output) per million tokens
- **Availability:** Requires internet connection
- **Privacy:** Sends problem text to external API

**Missing Schema Files:**
```python
# Lines 130-135
with open("canonical_problem_spec_schema.json", 'r') as f:  # ✅ EXISTS
    self.spec_schema = json.load(f)
with open("stage_2_schema.json", 'r') as f:  # ❌ MISSING
    self.stage_2_schema = json.load(f)
with open("stage_3_schema.json", 'r') as f:  # ❌ MISSING
    self.stage_3_schema = json.load(f)
```

**Impact:** Code will crash on initialization if schema files don't exist

---

### 3. Canonical Representation (core/universal_ai_analyzer.py)

**Current Structure:**
```python
# Line 28-66
@dataclass
class CanonicalProblemSpec:
    domain: PhysicsDomain
    problem_type: str
    problem_text: str
    complexity_score: float = 0.0

    objects: List[Dict] = field(default_factory=list)  # Flat list!
    relationships: List[Dict] = field(default_factory=list)  # Flat list!
    environment: Dict = field(default_factory=dict)
    physics_context: Dict = field(default_factory=dict)
    # ... more flat fields
```

**Issues:**
- **Flat Structure:** No nested semantic graph
- **No Ontology:** No links to domain ontologies (PhySH, ChEBI, etc.)
- **No Property Graph:** No RDF/triple store integration
- **Limited Semantics:** Simple dicts, not rich objects
- **No Inference:** Cannot reason over relationships

**What's Missing (from Roadmap):**
- Property graph representation (Neo4j, RDFLib)
- Ontology integration (OWL, SKOS)
- Semantic web standards (RDF, SPARQL)
- Knowledge base linkage (Wikidata, DBpedia)
- Inference capabilities (reasoning engines)

---

## Roadmap Expectations vs Reality

### Multi-Tool NLP Stack

**Roadmap Vision:**
```
┌─────────────────────────────────────────────┐
│         Problem Text Input                   │
└──────────────┬──────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────┐
│     Multi-Tool NLP Ensemble                  │
├─────────────────────────────────────────────┤
│  • spaCy (general NER)                       │
│  • SciBERT (scientific entities)             │
│  • Stanza (dependency parsing)               │
│  • AllenNLP (coreference, SRL)              │
│  • DyGIE++ (scientific relations)            │
│  • Domain regex (measurements)               │
└──────────────┬──────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────┐
│    Knowledge Integration Layer               │
├─────────────────────────────────────────────┤
│  • Domain Ontologies (PhySH, ChEBI)         │
│  • Property Graph (Neo4j/RDFLib)            │
│  • Entity Linking (Wikidata)                │
│  • Inference Engine                          │
└──────────────┬──────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────┐
│    Rich Semantic Representation              │
│  (Property Graph + Ontology-Backed)         │
└─────────────────────────────────────────────┘
```

**Current Reality:**
```
┌─────────────────────────────────────────────┐
│         Problem Text Input                   │
└──────────────┬──────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────┐
│     spaCy + Regex                            │
│  (single tool, general domain)               │
└──────────────┬──────────────────────────────┘
               │
               v
┌─────────────────────────────────────────────┐
│    Flat Dataclass                            │
│  (simple dicts, no semantics)                │
└─────────────────────────────────────────────┘
```

---

## Specific Gaps

### Gap 1: Multi-Tool NLP (Missing 5 of 6 tools)

| Tool | Purpose | Status | Priority |
|------|---------|--------|----------|
| **spaCy** | General NER, POS | ✅ Working | Core |
| **SciBERT** | Scientific entities | ❌ Missing | P1 CRITICAL |
| **Stanza** | Dependency parsing | ❌ Missing | P2 HIGH |
| **AllenNLP** | Coreference, SRL | ❌ Missing | P3 MEDIUM |
| **DyGIE++** | Scientific relations | ❌ Missing | P3 MEDIUM |
| **Quantulum3** | Unit extraction | ⚠️ Partial (regex) | P2 HIGH |

**Recommendation:** Implement at minimum SciBERT + Stanza + Quantulum3

---

### Gap 2: DeepSeek Dependency (Closed Source API)

**Current:** Requires paid API key to external service

**Alternative Options:**

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Local LLM (Mistral via Ollama)** | Free, private, offline | Slower, lower accuracy | ✅ **Best** |
| **OpenAI API** | High quality | Expensive, not open | ❌ No |
| **Local Llama 2** | Open source, free | Resource intensive | ⚠️ Maybe |
| **HuggingFace Models** | Open, flexible | Setup complexity | ✅ Good |

**Solution:** Replace DeepSeek with Ollama + Mistral (already implemented in llm_integration.py!)

---

### Gap 3: Missing Schema Files

**Referenced but Missing:**
- `stage_2_schema.json` - For intermediate analysis
- `stage_3_schema.json` - For final synthesis

**Impact:** Code crashes on initialization

**Solution:** Create missing schema files based on multi-stage reasoning flow

---

### Gap 4: No Property Graph / Ontology

**Current:** Flat list of dicts

**Roadmap:** Property graph with ontology linkage

**Example of Gap:**

**Current Representation:**
```json
{
  "objects": [
    {"id": "C1", "type": "capacitor", "value": 2.0, "unit": "μF"}
  ],
  "relationships": [
    {"type": "connected_to", "subject": "C1", "target": "V1"}
  ]
}
```

**Roadmap Representation (RDF Triple Store):**
```turtle
@prefix ex: <http://example.org/> .
@prefix phys: <http://ontology.physics.org/> .
@prefix units: <http://qudt.org/vocab/unit/> .

ex:C1 a phys:Capacitor ;
    phys:hasCapacitance [
        a units:Farad ;
        units:numericValue 2.0e-6
    ] ;
    phys:connectedTo ex:V1 ;
    phys:hasPolarity phys:NonPolarized ;
    owl:sameAs <http://wikidata.org/entity/Q5322> .  # Link to Wikidata
```

**Benefits of Property Graph:**
- Semantic reasoning (infer properties)
- Ontology-backed validation (check physical plausibility)
- Knowledge graph queries (SPARQL)
- Entity linking (Wikidata, DBpedia)
- Rich metadata (provenance, confidence)

---

### Gap 5: No Knowledge Integration

**Missing Components:**

1. **Domain Ontologies:**
   - Physics: PhySH (Physics Subject Headings)
   - Chemistry: ChEBI (Chemical Entities of Biological Interest)
   - Biology: Gene Ontology
   - Cross-domain: Schema.org

2. **Knowledge Bases:**
   - Wikidata (general knowledge)
   - DBpedia (structured Wikipedia)
   - PubChem (chemistry)
   - NIST (physical constants)

3. **Inference Engines:**
   - OWL reasoner (ontology reasoning)
   - SWRL rules (semantic web rules)
   - Custom physics rules

**Impact:** Cannot leverage domain knowledge for:
- Entity disambiguation
- Property inference
- Constraint validation
- Unit conversion
- Physical plausibility checking

---

## Comparison Table

| Feature | Current | Roadmap | Gap |
|---------|---------|---------|-----|
| **NLP Tools** | spaCy only | 6+ tools | 83% |
| **Scientific NLP** | None | SciBERT, Stanza | 100% |
| **LLM Backend** | DeepSeek API | Open source | 100% |
| **Schema Files** | 1 of 3 | 3 of 3 | 67% |
| **Representation** | Flat dataclass | Property graph | 100% |
| **Ontology** | None | Domain ontologies | 100% |
| **Knowledge Base** | None | Wikidata, etc. | 100% |
| **Inference** | None | Reasoning engine | 100% |
| **Entity Linking** | None | Wikidata links | 100% |
| **Semantic Web** | None | RDF, SPARQL | 100% |

**Average Gap:** 85% of roadmap text understanding features missing

---

## Proposed Solution: Knowledge-Backed NLP System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Problem Text                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│            Enhanced Multi-Tool NLP Stack                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Tier 1: Fast Extractors (1s)                          │  │
│  │  • spaCy (en_core_web_sm) - General NER              │  │
│  │  • Regex patterns - Measurements, formulas            │  │
│  │  • Quantulum3 - Unit extraction                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Tier 2: Scientific Extractors (5s)                   │  │
│  │  • SciBERT - Scientific entities                      │  │
│  │  • Stanza - Dependency parsing                        │  │
│  │  • ChemDataExtractor - Chemical entities (optional)   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Tier 3: LLM Planning (10s) - Optional                │  │
│  │  • Mistral/Llama via Ollama                          │  │
│  │  • Replaces DeepSeek (open source!)                  │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│         Knowledge Integration & Enrichment                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Entity Linking                                        │  │
│  │  • Link to Wikidata (concepts)                       │  │
│  │  • Link to PhySH (physics topics)                    │  │
│  │  • Link to ChEBI (chemicals)                         │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Ontology Mapping                                      │  │
│  │  • Map entities to domain ontologies                 │  │
│  │  • Infer properties from ontology                    │  │
│  │  • Validate against ontology constraints             │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Property Graph Construction                           │  │
│  │  • Build RDF triples                                  │  │
│  │  • Add semantic annotations                           │  │
│  │  • Link to knowledge bases                            │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       v
┌─────────────────────────────────────────────────────────────┐
│       Enhanced Semantic Problem Specification                │
│                                                              │
│  • Property Graph (RDF triples)                             │
│  • Ontology-backed entities                                 │
│  • Knowledge base links                                     │
│  • Inference-ready representation                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Enhanced NLP Stack (Week 1-2)

**Goal:** Replace single-tool with multi-tool ensemble

1. Integrate SciBERT for scientific entity extraction
2. Add Quantulum3 for robust unit extraction
3. Add Stanza for dependency parsing (optional)
4. Create ensemble combiner (merge results)

**Deliverables:**
- `core/enhanced_nlp_stack.py` - Multi-tool NLP
- `core/nlp_tools/scibert_extractor.py` - SciBERT integration
- `core/nlp_tools/quantity_extractor.py` - Quantulum3 wrapper
- Tests demonstrating improved accuracy

---

### Phase 2: Replace DeepSeek (Week 2)

**Goal:** Open-source alternative to paid API

1. Use existing `llm_integration.py` (already implemented!)
2. Create adapter for UniversalAIAnalyzer
3. Create missing schema files
4. Test with local Mistral/Llama

**Deliverables:**
- `stage_2_schema.json` - Multi-stage intermediate schema
- `stage_3_schema.json` - Multi-stage final schema
- `core/open_ai_analyzer.py` - Ollama-based analyzer
- Performance comparison vs DeepSeek

---

### Phase 3: Property Graph Integration (Week 3-4)

**Goal:** Rich semantic representation

1. Create property graph builder (RDFLib)
2. Design enhanced CanonicalProblemSpec with graph support
3. Add ontology mapper
4. Implement entity linking to Wikidata

**Deliverables:**
- `core/property_graph.py` - RDF triple store
- `core/ontology_mapper.py` - Domain ontology integration
- `core/entity_linker.py` - Wikidata linkage
- `core/semantic_problem_spec.py` - Enhanced representation

---

### Phase 4: Knowledge Integration (Week 4-5)

**Goal:** Domain knowledge backing

1. Load domain ontologies (PhySH, ChEBI, etc.)
2. Create inference engine for property inference
3. Add knowledge base query interface
4. Implement semantic validation

**Deliverables:**
- `knowledge/ontologies/` - Domain ontology files
- `core/inference_engine.py` - Reasoning engine
- `core/knowledge_base.py` - KB query interface
- Integration tests

---

## Technology Stack

### NLP Tools
- **spaCy** (existing) - General NER, POS tagging
- **SciBERT** (new) - Scientific entity extraction
- **Quantulum3** (new) - Unit/quantity extraction
- **Stanza** (optional) - Dependency parsing

### LLM Backend
- **Ollama** - Local LLM hosting
- **Mistral 7B** - Open-source LLM (replaces DeepSeek)
- **Llama 2** - Alternative open-source LLM

### Knowledge Representation
- **RDFLib** - RDF triple store in Python
- **OWL** - Ontology Web Language
- **SPARQL** - Graph query language

### Knowledge Sources
- **Wikidata** - General knowledge graph
- **PhySH** - Physics ontology
- **ChEBI** - Chemical ontology
- **Schema.org** - Cross-domain vocabulary

### Inference
- **Owlready2** - OWL reasoning in Python
- **SWRL** - Semantic web rules

---

## Next Steps

### Immediate (This Week)
1. ✅ Document the gap (this file)
2. 🔲 Create missing schema files
3. 🔲 Implement open-source AI analyzer (Ollama-based)
4. 🔲 Integrate SciBERT for scientific NER

### Short Term (Next 2 Weeks)
5. 🔲 Add Quantulum3 for unit extraction
6. 🔲 Create property graph builder
7. 🔲 Design enhanced CanonicalProblemSpec
8. 🔲 Test multi-tool ensemble

### Medium Term (Next Month)
9. 🔲 Integrate domain ontologies
10. 🔲 Implement entity linking
11. 🔲 Create inference engine
12. 🔲 Full knowledge-backed pipeline

---

## Summary

**Critical Gaps Identified:**
1. ❌ 83% of roadmap NLP tools missing (5 of 6)
2. ❌ DeepSeek dependency (paid, closed source)
3. ❌ 67% of schema files missing (2 of 3)
4. ❌ 100% property graph/ontology missing
5. ❌ 100% knowledge integration missing

**Total Text Understanding Gap:** ~85% of roadmap features missing

**Solution:** Implement multi-tool NLP + property graphs + open-source LLM

**Timeline:** 4-5 weeks for complete implementation

**Priority:** CRITICAL - This blocks true "knowledge-backed interpretation"
