# Integration Examples

This directory contains comprehensive examples demonstrating the full STEM diagram generation pipeline with all advanced features.

## Full Pipeline Integration

**File**: `full_pipeline_integration.py`

Demonstrates the complete workflow integrating all 12 implemented phases:

### Features Demonstrated

1. **Property Graph Construction** (Phase 1A)
   - Creating nodes and edges
   - Querying the graph
   - Spatial relationship analysis

2. **Advanced NLP Enrichment** (Phases 2A, 3A, 4A, 6A)
   - OpenIE triple extraction
   - Stanza dependency parsing
   - SciBERT semantic similarity
   - DyGIE++ entity/relation extraction

3. **Ontology Validation** (Phase 5A)
   - OWL/RDF ontology creation
   - Domain-specific knowledge (physics, chemistry, biology)
   - Semantic validation
   - SPARQL queries

4. **Diagram Planning** (Phase 1B)
   - Complexity assessment
   - Strategy selection
   - Problem decomposition
   - Constraint generation

5. **Model Orchestration** (Phase 6B)
   - Automatic model selection
   - Complexity-driven routing
   - Performance tracking

6. **LLM Auditing** (Phase 5B)
   - Scene description generation
   - Quality validation
   - Issue identification
   - Iterative refinement

7. **End-to-End Pipeline**
   - Complete workflow from text to validated diagram

## Running the Examples

### Prerequisites

Minimal dependencies (required):
```bash
pip install spacy numpy networkx rdflib
```

Full features (recommended):
```bash
pip install -r ../requirements.txt
```

### Execute Examples

Run all examples:
```bash
python full_pipeline_integration.py
```

The script will:
- Run 7 comprehensive examples
- Show which features are available
- Gracefully handle missing dependencies
- Display results for each component

## Example Output

```
======================================================================
  STEM Diagram Pipeline - Full Integration Examples
  November 2025 Implementation
======================================================================

======================================================================
  Example 1: Property Graph Basics
======================================================================

Property Graph Created:
  Nodes: 4, Edges: 3
  Node Types: {'OBJECT': 2, 'FORCE': 2}
  Edge Types: {'ACTS_ON': 2, 'TOUCHES': 1}

Querying for all forces:
  - Gravitational Force: 49 N
  - Normal Force: 49 N

...
```

## Individual Examples

### Example 1: Property Graph Basics
Basic property graph operations including:
- Node/edge creation
- Querying by type
- Finding neighbors
- Spatial analysis

### Example 2: NLP Enrichment
Advanced NLP processing:
- OpenIE: Extract (subject, relation, object) triples
- Stanza: Dependency parsing and POS tagging
- SciBERT: Semantic similarity for scientific terms

### Example 3: Ontology Validation
Semantic knowledge representation:
- Physics ontology with force types
- Instance creation and validation
- SPARQL queries
- RDF export

### Example 4: Diagram Planning
Complexity-driven planning:
- Assess diagram complexity (0-1 scale)
- Select strategy (heuristic/constraint/symbolic/hybrid)
- Generate constraints
- Decompose complex problems

### Example 5: Model Orchestration
Automatic model selection:
- Test different complexity levels
- Show model selection logic
- Demonstrate fallback chains

### Example 6: LLM Auditor
Quality validation with LLMs:
- Generate scene descriptions
- Parse critique from LLM
- Identify issues by severity
- Suggest corrections

### Example 7: End-to-End Pipeline
Complete workflow:
1. Parse text description
2. Build property graph
3. Convert to CanonicalProblemSpec
4. Plan diagram layout
5. Select optimal model
6. Validate semantics
7. Audit quality

## Customization

You can modify the examples to test different scenarios:

```python
# Test your own text description
text = "Your custom physics problem description"

# Create custom property graph
graph = PropertyGraph()
# Add your nodes and edges...

# Test with real LLM (requires API key)
auditor = DiagramAuditor(
    backend=LLMBackend.CLAUDE,
    api_key="your-api-key"
)
```

## Troubleshooting

### Missing Dependencies

If you see "not available" messages:

```bash
# For advanced NLP
pip install stanza transformers torch allennlp allennlp-models

# For ontology
pip install rdflib owlrl

# For LLM auditing
pip install anthropic openai

# For constraint solving
pip install z3-solver

# For symbolic math
pip install sympy

# For geometry
pip install shapely
```

### Stanza Models

First-time Stanza usage requires downloading models:
```bash
python -m stanza download en
```

### Import Errors

Ensure you're running from the examples directory or adjust the path:
```python
sys.path.insert(0, '/path/to/pipeline_universal_STEM')
```

## Performance Notes

- **Property Graph**: Fast, works with any size
- **NLP Tools**: May be slow on first run (model loading)
- **Ontology**: Fast for small graphs, scales to millions of triples
- **LLM Auditor**: Depends on API latency (1-5 seconds typically)
- **Z3 Solver**: May timeout on very complex layouts (default 30s)

## Next Steps

After running these examples, explore:

1. **core/property_graph.py** - Graph operations and queries
2. **core/diagram_planner.py** - Planning strategies
3. **core/model_orchestrator.py** - Model selection logic
4. **core/auditor/diagram_auditor.py** - LLM integration
5. **core/ontology/ontology_manager.py** - Semantic validation

## Additional Resources

- Main README: `../README.md`
- Advanced NLP Roadmap: `../docs/ADVANCED_NLP_ROADMAP.md`
- Planning Roadmap: `../docs/PLANNING_REASONING_ROADMAP.md`
- Implementation Summary: `../docs/NOVEMBER_9_2025_FINAL_SUMMARY.md`
