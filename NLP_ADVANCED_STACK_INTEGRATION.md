# Advanced NLP Stack Integration Plan
## November 5, 2025

---

## 🎯 Objective

Enhance the current multi-domain NLP pipeline with state-of-the-art NLP tools to achieve:
- **Entity Recognition:** 85-95% → **95-99%** accuracy
- **Relationship Extraction:** 75-85% → **90-95%** accuracy
- **Semantic Understanding:** Basic → **Deep semantic representation**
- **Scientific Domain:** Generic → **Domain-optimized** (Physics, Chemistry, Electronics)

---

## 📊 Current State Analysis

### What We Have (Basic Pipeline)

**Strengths:**
- ✅ Fast (1-2 seconds processing)
- ✅ Zero cost (local processing)
- ✅ Offline capable
- ✅ 5 domain extractors
- ✅ Multi-method relationship extraction

**Limitations:**
- ⚠️ Generic entity types (CARDINAL, QUANTITY) instead of domain-specific (CAPACITOR, DIELECTRIC)
- ⚠️ Pattern-based relationships miss implicit connections
- ⚠️ No semantic understanding of scientific concepts
- ⚠️ Limited mathematical expression parsing
- ⚠️ No knowledge graph integration

### Question 8 Current Results

**Entities Extracted (Current):**
```json
{
  "type": "CARDINAL",  // Generic!
  "text": "21.0",
  "confidence": 0.85
}
```

**What We Want (With Advanced Stack):**
```json
{
  "type": "DIELECTRIC_CONSTANT",  // Domain-specific!
  "text": "κ₁ = 21.0",
  "properties": {
    "symbol": "κ₁",
    "value": 21.0,
    "unit": "dimensionless",
    "region": "left_half"
  },
  "confidence": 0.98,
  "method": "scibert + grobid"
}
```

---

## 🏗️ Advanced Stack Architecture

### Layer 1: Base NLP Pipeline (CURRENT)
```
spaCy 3.7+ (tokenization, POS, dependency parsing)
├── Already integrated ✅
└── Performance: Fast, reliable
```

### Layer 2: Entity Recognition (ENHANCEMENT)

#### 2A. SciBERT (Scientific Entity Recognition)
```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

# Scientific concept recognition
scibert_tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
scibert_model = AutoModelForTokenClassification.from_pretrained(
    "allenai/scibert_scivocab_uncased",
    num_labels=len(ENTITY_TYPES)
)

# Recognizes:
- "parallel-plate capacitor" → CAPACITOR_TYPE
- "dielectric" → MATERIAL_TYPE
- "plate separation" → GEOMETRIC_PROPERTY
```

**Expected Improvement:**
- Generic entities (CARDINAL) → Scientific entities (DIELECTRIC_CONSTANT, CAPACITOR, PLATE_AREA)
- Confidence: 0.85 → 0.95-0.98
- Domain specificity: +80%

#### 2B. GrobidQuantities (Measurement Extraction)
```python
from grobid_quantities import QuantitiesAPI

# Enhanced measurement parsing
grobid = QuantitiesAPI()

# Input: "plate area A = 10.5 cm²"
# Output:
{
  "type": "area",
  "value": 10.5,
  "unit": {
    "name": "square centimeter",
    "symbol": "cm²",
    "si_conversion": 1.05e-3  # to m²
  },
  "normalized_value": 1.05e-3,  # in SI units
  "variable": "A"
}
```

**Expected Improvement:**
- Better unit parsing: "cm²", "mm" correctly identified with conversions
- Variable linking: Associates "A" with "plate area"
- SI normalization: Automatic conversion to standard units

#### 2C. MathBERT (Mathematical Expression Understanding)
```python
from transformers import AutoTokenizer, AutoModel

mathbert_tokenizer = AutoTokenizer.from_pretrained("tbs17/MathBERT")
mathbert_model = AutoModel.from_pretrained("tbs17/MathBERT")

# Input: "κ₁ = 21.0"
# Output:
{
  "type": "equation",
  "lhs": "κ₁",
  "operator": "=",
  "rhs": "21.0",
  "equation_type": "assignment",
  "variables": ["κ₁"],
  "constants": [21.0]
}
```

**Expected Improvement:**
- Mathematical expressions parsed as structured objects
- Variable-value associations explicit
- Equation type classification (assignment, formula, constraint)

### Layer 3: Relationship Extraction (ENHANCEMENT)

#### 3A. OpenIE 5.1 (Open Information Extraction)
```python
from openie import StanfordOpenIE

openie = StanfordOpenIE()

# Input: "The left half is filled with dielectric κ₁ = 21.0"
# Output:
[
  {
    "subject": "left half",
    "relation": "is filled with",
    "object": "dielectric κ₁",
    "confidence": 0.92
  },
  {
    "subject": "dielectric κ₁",
    "relation": "has value",
    "object": "21.0",
    "confidence": 0.95
  }
]
```

**Expected Improvement:**
- Extracts implicit relationships current pipeline misses
- Natural language relations ("is filled with") → structured triples
- Higher confidence (0.92-0.95 vs. 0.50 proximity-based)

#### 3B. DyGIE++ (Scientific Relation Extraction)
```python
from dygie import DyGIE

dygie = DyGIE.from_pretrained("dygie-scibert")

# Domain-specific relation extraction
# Input: Full Question 8 text
# Output:
[
  {
    "entity1": {"text": "parallel-plate capacitor", "type": "DEVICE"},
    "entity2": {"text": "plate area A = 10.5 cm²", "type": "PROPERTY"},
    "relation": "HAS_PROPERTY",
    "confidence": 0.94
  },
  {
    "entity1": {"text": "left half", "type": "REGION"},
    "entity2": {"text": "dielectric κ₁ = 21.0", "type": "MATERIAL"},
    "relation": "CONTAINS",
    "confidence": 0.91
  },
  {
    "entity1": {"text": "right half", "type": "REGION"},
    "entity2": {"text": "two regions", "type": "SUBDIVISION"},
    "relation": "DIVIDED_INTO",
    "confidence": 0.89
  }
]
```

**Expected Improvement:**
- Scientific domain relations: HAS_PROPERTY, CONTAINS, DIVIDED_INTO
- Joint entity and relation extraction (entities inform relations)
- Confidence: 0.89-0.94 vs. 0.50-0.95 current mix

#### 3C. PL-Marker (SOTA Entity-Relation Joint Extraction)
```python
from pl_marker import PLMarker

pl_marker = PLMarker.from_pretrained("pl-marker-scibert")

# State-of-the-art joint extraction
# Simultaneously identifies entities and their relationships
# Better than pipeline approach (entity then relation)
```

**Expected Improvement:**
- 5-10% higher F1 score vs. pipeline approach
- Better entity-relation consistency
- Handles overlapping entities and nested relations

### Layer 4: Semantic Understanding (NEW CAPABILITY)

#### 4A. AMR 3.0 Parser (Abstract Meaning Representation)
```python
from amrlib import load_stog_model

amr_parser = load_stog_model()

# Input: "The left half is filled with dielectric κ₁ = 21.0"
# Output: AMR graph
"""
(f / fill-01
   :ARG0 (d / dielectric
            :name (n / name :op1 "κ₁")
            :value (v / value :quant 21.0))
   :ARG1 (h / half
            :mod (l / left)
            :part-of (c / capacitor)))
"""
```

**Capability:**
- Deep semantic representation beyond syntax
- Event structure: "fill-01" with arguments (what fills, what is filled)
- Spatial relations: "left half" part-of "capacitor"
- Can query: "What is in the left region?" → "dielectric κ₁"

#### 4B. FrameNet (Semantic Frame Analysis)
```python
from framenet import FrameNet

fn = FrameNet()

# Input: "The right half is divided into two regions"
# Output:
{
  "frame": "Separating",
  "frame_elements": {
    "Whole": "right half",
    "Parts": "two regions",
    "Manner": "divided"
  },
  "semantic_type": "GEOMETRIC_PARTITION"
}
```

**Capability:**
- Understands "divided into" as SEPARATING frame
- Maps to geometric partition concept
- Enables reasoning: "If A is divided into B and C, then B and C are parts of A"

#### 4C. VerbNet (Verb Semantics)
```python
from verbnet import VerbNet

vn = VerbNet()

# Input: "is filled with"
# Output:
{
  "verb_class": "fill-9.8",
  "roles": {
    "Agent": null,  # implicit or unspecified
    "Theme": "dielectric κ₁",
    "Destination": "left half"
  },
  "semantic_predicates": [
    "motion(during(E), Theme)",
    "location(end(E), Theme, Destination)"
  ]
}
```

**Capability:**
- Deep verb semantics: "fill" involves motion of Theme to Destination
- Semantic predicates for reasoning
- Role mapping for knowledge graph construction

---

## 📋 Integration Roadmap

### Phase 1: Enhanced Entity Recognition (Week 1-2)

**Goal:** Improve entity extraction from 85% → 95%+ accuracy

**Tasks:**
1. **Install SciBERT** (1 day)
   ```bash
   pip install transformers torch
   ```
   - Load allenai/scibert_scivocab_uncased
   - Fine-tune on physics/electronics corpus (optional)

2. **Integrate GrobidQuantities** (2 days)
   ```bash
   pip install grobid-quantities
   ```
   - Set up Grobid server (Docker)
   - Replace quantulum3 with GrobidQuantities
   - Add SI unit normalization

3. **Add MathBERT** (2 days)
   ```bash
   pip install transformers
   ```
   - Load tbs17/MathBERT
   - Parse mathematical expressions
   - Extract equation structure

4. **Test on Question 8** (1 day)
   - Compare entity types: CARDINAL → DIELECTRIC_CONSTANT, CAPACITOR
   - Measure confidence improvement: 0.85 → 0.95+
   - Verify unit parsing: "cm²", "mm" correctly handled

**Expected Results:**
- Entity types: +60% domain-specific (vs. generic)
- Confidence: +10-15% (0.85 → 0.95-0.98)
- Unit parsing: 100% accuracy with SI conversion

### Phase 2: Advanced Relationship Extraction (Week 3-4)

**Goal:** Improve relationship extraction from 75-85% → 90-95% accuracy

**Tasks:**
1. **Install OpenIE 5.1** (2 days)
   ```bash
   # Requires Java
   pip install stanford-openie
   ```
   - Set up Stanford CoreNLP server
   - Extract triples from sentences
   - Add to relationship extractor pipeline

2. **Integrate DyGIE++** (3 days)
   ```bash
   git clone https://github.com/dwadden/dygiepp
   pip install -e dygiepp
   ```
   - Load pre-trained SciERC model
   - Fine-tune on electronics/physics corpus
   - Joint entity-relation extraction

3. **Add PL-Marker** (2 days)
   ```bash
   git clone https://github.com/thunlp/PL-Marker
   pip install -e PL-Marker
   ```
   - Load SOTA model
   - Benchmark against current pipeline
   - A/B testing on Batch 2 questions

4. **Test on Question 8** (1 day)
   - Compare relationships: RELATED_TO → HAS_PROPERTY, CONTAINS, DIVIDED_INTO
   - Measure F1 score improvement
   - Check implicit relationship detection

**Expected Results:**
- Relationship types: +40% semantic (vs. generic RELATED_TO)
- Confidence: +15-20% (0.75 → 0.90-0.95)
- Implicit relations: +30% coverage

### Phase 3: Semantic Understanding (Week 5-6)

**Goal:** Add deep semantic representation for reasoning and knowledge graph

**Tasks:**
1. **Install AMR Parser** (2 days)
   ```bash
   pip install amrlib
   ```
   - Load AMR 3.0 model
   - Parse sentences to AMR graphs
   - Store in graph database (Neo4j)

2. **Integrate FrameNet** (2 days)
   ```bash
   pip install nltk
   python -m nltk.downloader framenet_v17
   ```
   - Frame semantic parsing
   - Map frames to domain concepts
   - Build frame hierarchy

3. **Add VerbNet** (2 days)
   ```bash
   pip install verbnetparser
   ```
   - Verb class identification
   - Role mapping
   - Semantic predicate extraction

4. **Build Knowledge Graph** (2 days)
   - Combine entities, relations, AMR, frames
   - Store in Neo4j graph database
   - Enable semantic queries

**Expected Results:**
- Deep semantic representation beyond surface text
- Reasoning capability: "What is in the left region?" → "dielectric κ₁"
- Knowledge graph with 100+ nodes and 200+ edges per problem

### Phase 4: Integration and Testing (Week 7-8)

**Tasks:**
1. **Integrate all components** (3 days)
   - Create unified AdvancedNLPPipeline class
   - Orchestrate all extractors
   - Optimize processing order

2. **Test on Batch 2** (2 days)
   - Run all 5 questions through advanced pipeline
   - Compare with basic pipeline
   - Measure accuracy improvements

3. **A/B Comparison** (2 days)
   - Basic pipeline vs. Advanced pipeline
   - Processing time analysis
   - Cost-benefit analysis

4. **Documentation** (1 day)
   - Update README with advanced stack
   - Create usage guide
   - Document API changes

**Expected Results:**
- Full integration tested on 5 questions
- Comprehensive comparison report
- Production-ready advanced pipeline

---

## 📊 Expected Improvements: Question 8 Example

### Current Basic Pipeline Output

```json
{
  "entities": [
    {"type": "CARDINAL", "text": "10.5"},
    {"type": "CARDINAL", "text": "21.0"},
    {"type": "QUANTITY", "text": "7.12 mm"}
  ],
  "relationships": [
    {"type": "RELATED_TO", "confidence": 0.50},
    {"type": "EQUALS", "subject": "A", "target": "10.5 cm²", "confidence": 0.95}
  ],
  "metadata": {
    "num_entities": 9,
    "num_relationships": 14
  }
}
```

### Advanced Stack Output (Projected)

```json
{
  "entities": [
    {
      "type": "PLATE_AREA",
      "text": "plate area A = 10.5 cm²",
      "properties": {
        "variable": "A",
        "value": 10.5,
        "unit": "cm²",
        "si_value": 1.05e-3,
        "si_unit": "m²",
        "geometric_property": "area"
      },
      "confidence": 0.97,
      "method": "scibert + grobid"
    },
    {
      "type": "DIELECTRIC_CONSTANT",
      "text": "dielectric κ₁ = 21.0",
      "properties": {
        "symbol": "κ₁",
        "value": 21.0,
        "unit": "dimensionless",
        "region": "left_half",
        "material_property": "relative_permittivity"
      },
      "confidence": 0.98,
      "method": "scibert + mathbert"
    },
    {
      "type": "CAPACITOR_DEVICE",
      "text": "parallel-plate capacitor",
      "properties": {
        "device_type": "capacitor",
        "configuration": "parallel_plate",
        "components": ["plates", "dielectrics"]
      },
      "confidence": 0.96,
      "method": "scibert"
    },
    {
      "type": "GEOMETRIC_REGION",
      "text": "left half",
      "properties": {
        "spatial_position": "left",
        "fraction": 0.5,
        "part_of": "capacitor"
      },
      "confidence": 0.94,
      "method": "scibert + amr"
    }
  ],
  "relationships": [
    {
      "type": "HAS_PROPERTY",
      "entity1": "parallel-plate capacitor",
      "entity2": "plate area A = 10.5 cm²",
      "confidence": 0.94,
      "method": "dygie++",
      "semantic_frame": "Possession"
    },
    {
      "type": "CONTAINS",
      "entity1": "left half",
      "entity2": "dielectric κ₁ = 21.0",
      "confidence": 0.92,
      "method": "openie + dygie++",
      "semantic_frame": "Container",
      "triple": {
        "subject": "left half",
        "relation": "is filled with",
        "object": "dielectric κ₁"
      }
    },
    {
      "type": "DIVIDED_INTO",
      "entity1": "right half",
      "entity2": "two regions",
      "confidence": 0.89,
      "method": "dygie++",
      "semantic_frame": "Separating",
      "details": {
        "parts": ["top region", "bottom region"]
      }
    },
    {
      "type": "SPATIAL_CONFIGURATION",
      "entity1": "top region",
      "entity2": "bottom region",
      "relation_subtype": "ABOVE",
      "confidence": 0.91,
      "method": "spatial_reasoner + amr"
    }
  ],
  "semantic_graph": {
    "nodes": 15,
    "edges": 24,
    "amr_representation": "(c / capacitor :ARG0-of (c2 / configure-01 ...))",
    "frames": ["Container", "Separating", "Possession"],
    "verb_classes": ["fill-9.8", "divide-23.4"]
  },
  "metadata": {
    "num_entities": 15,  // +67% increase
    "num_relationships": 24,  // +71% increase
    "entity_confidence_avg": 0.96,  // +13% increase
    "relationship_confidence_avg": 0.92,  // +84% increase (vs 0.50 proximity)
    "processing_time": "5-8 seconds",  // 3-5x slower but still fast
    "methods": ["scibert", "grobid", "mathbert", "openie", "dygie++", "amr"]
  }
}
```

### Comparison Table

| Metric | Basic Pipeline | Advanced Stack | Improvement |
|--------|---------------|----------------|-------------|
| **Entity Types** | Generic (CARDINAL) | Domain-specific (DIELECTRIC_CONSTANT) | +80% specificity |
| **Entity Count** | 9 | 15 | +67% |
| **Entity Confidence** | 0.85 avg | 0.96 avg | +13% |
| **Relationship Types** | Generic (RELATED_TO) | Semantic (HAS_PROPERTY, CONTAINS) | +60% specificity |
| **Relationship Count** | 14 | 24 | +71% |
| **Relationship Confidence** | 0.50-0.95 (mixed) | 0.89-0.94 (consistent) | +84% avg |
| **Semantic Understanding** | None | AMR + Frames + VerbNet | New capability |
| **Processing Time** | 1-2s | 5-8s | 3-5x slower |
| **Knowledge Graph** | No | Yes (15 nodes, 24 edges) | New capability |

---

## 💰 Cost-Benefit Analysis

### Implementation Costs

**Development Time:**
- Phase 1 (Entity): 6 days × $500/day = $3,000
- Phase 2 (Relations): 8 days × $500/day = $4,000
- Phase 3 (Semantics): 8 days × $500/day = $4,000
- Phase 4 (Integration): 8 days × $500/day = $4,000
- **Total:** 30 days, **$15,000**

**Infrastructure Costs:**
- Grobid server: $50/month (Docker)
- Stanford CoreNLP: $50/month (server)
- GPU for BERT models: $200/month (cloud)
- Neo4j database: $100/month
- **Total:** $400/month

**Model Storage:**
- SciBERT: ~500MB
- DyGIE++: ~1GB
- AMR models: ~2GB
- **Total:** ~4GB storage

### Benefits

**Accuracy Improvements:**
- Entity extraction: 85% → 96% (+13%)
- Relationship extraction: 75% → 92% (+23%)
- Overall success rate: 20% → 45-60% (+25-40% projected)

**Capabilities Gained:**
- Domain-specific entity types (not generic)
- Semantic understanding (reasoning capability)
- Knowledge graph (queryable structure)
- SI unit normalization (automatic conversion)
- Mathematical expression parsing
- Implicit relationship detection

**Time Savings:**
- Manual correction: 30min/problem → 5min/problem (6x reduction)
- Over 1000 problems: **417 hours saved**
- At $50/hour: **$20,850 saved**

**ROI:**
- Initial investment: $15,000 (development) + $400/month (infrastructure)
- Year 1 savings: $20,850 (manual correction) + priceless (new capabilities)
- **Break-even:** ~9 months
- **Year 2+ profit:** $20,000+/year

---

## 🚀 Recommendation

### Phased Approach (Recommended)

**Phase 1A: Quick Wins (Week 1-2) - HIGHEST PRIORITY**
1. ✅ SciBERT integration → +60% entity specificity
2. ✅ GrobidQuantities → +100% unit parsing accuracy
3. ✅ Test on Question 8 and Batch 2

**Phase 2A: Relationship Enhancement (Week 3-4)**
1. OpenIE 5.1 → +30% implicit relations
2. DyGIE++ → +60% semantic relations
3. A/B comparison with basic pipeline

**Phase 3A: Semantic Layer (Week 5-6) - OPTIONAL**
1. AMR parser → deep semantic representation
2. Knowledge graph → queryable structure
3. Enable advanced reasoning

**Phase 4A: Production Deployment (Week 7-8)**
1. Full integration and testing
2. Documentation and training
3. Rollout to production

### Alternative: Hybrid Approach (Recommended for MVP)

**Use Basic Pipeline (Current) for:**
- Initial processing (fast, cheap)
- Simple problems (1-2 entities/relationships)
- Offline scenarios

**Use Advanced Stack for:**
- Complex problems (5+ entities/relationships)
- Scientific domain text (physics, chemistry)
- When high accuracy is critical (exam questions, publications)

**Trigger Logic:**
```python
if complexity_score < 1.0 or num_entities < 5:
    use_basic_pipeline()  # Fast path
else:
    use_advanced_stack()  # Accuracy path
```

---

## 📈 Success Metrics

### Quantitative Targets
- Entity extraction F1: 0.85 → 0.95 (+12%)
- Relationship extraction F1: 0.75 → 0.92 (+23%)
- End-to-end success: 20% → 50% (+150% relative)
- Processing time: <10 seconds per problem
- Cost: <$0.10 per problem (infrastructure)

### Qualitative Targets
- Domain-specific entity types (not generic CARDINAL)
- Semantic relationship types (not generic RELATED_TO)
- Knowledge graph construction (queryable)
- Reasoning capability (answer semantic queries)
- Explainable results (trace extraction methods)

---

## 🎯 Next Steps

1. **Review and Approve Stack** - Confirm technology choices
2. **Prioritize Phases** - Decide which components to implement first
3. **Set Up Development Environment** - Install base tools
4. **Begin Phase 1A** - SciBERT + GrobidQuantities integration
5. **Test on Question 8** - Validate improvements immediately

---

**Document Version:** 1.0
**Date:** November 5, 2025
**Status:** Ready for Review and Approval
**Estimated Timeline:** 8 weeks (phased approach)
**Estimated Cost:** $15,000 development + $400/month infrastructure
**Expected ROI:** Break-even in 9 months, $20,000+/year profit thereafter
