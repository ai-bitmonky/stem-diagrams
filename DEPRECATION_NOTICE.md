# Deprecation Notice

**Date**: November 10, 2025
**Status**: ⚠️ **core/unified_pipeline.py is DEPRECATED**

---

## Summary

**DEPRECATED**: `core/unified_pipeline.py`
**USE INSTEAD**: `unified_diagram_pipeline.py`

---

## Why Deprecated?

After comprehensive analysis (see [PIPELINE_MERGER_GAP_ANALYSIS.md](PIPELINE_MERGER_GAP_ANALYSIS.md)), we discovered that `core/unified_pipeline.py` is **incomplete** and missing critical components.

### Missing Components in core/unified_pipeline.py

1. ❌ **DiagramPlanner** - Complexity assessment + strategy selection
2. ❌ **DiagramAuditor** - LLM quality auditing
3. ❌ **ModelOrchestrator** - Dynamic model selection
4. ⚠️ **OntologyManager** - Initialized but never executed
5. ⚠️ **AestheticAnalyzer** - Initialized but never executed
6. ❌ **Complete PipelineResult** - Missing fields:
   - `complexity_score`
   - `selected_strategy`
   - `ontology_validation`
   - `audit_report`
   - `save_svg()` method
   - `save_scene()` method

### Why unified_diagram_pipeline.py is Better

✅ **Complete Feature Set**:
- All features from core/unified_pipeline.py
- PLUS: DiagramPlanner, DiagramAuditor, ModelOrchestrator
- Ontology validation that actually executes
- LLM quality auditing
- Complete result format

✅ **Better Architecture**:
- 7 clean phases (vs mixed steps)
- Clear separation of concerns
- Proper phase naming and organization

✅ **Better Configuration**:
- PipelineConfig dataclass (vs individual parameters)
- Comprehensive feature flags
- Better defaults

✅ **Complete Results**:
- All metadata fields
- Convenience methods (save_svg, save_scene)
- Proper tracing and timing

---

## Migration Guide

### Old Code (core/unified_pipeline.py) - DEPRECATED

```python
from core.unified_pipeline import UnifiedPipeline, PipelineMode

# FAST mode
pipeline = UnifiedPipeline(mode=PipelineMode.FAST)
result = pipeline.generate("A 2μF capacitor...")

# ACCURATE mode
pipeline = UnifiedPipeline(mode=PipelineMode.ACCURATE)
result = pipeline.generate("Problem text...")

# PREMIUM mode
pipeline = UnifiedPipeline(mode=PipelineMode.PREMIUM)
result = pipeline.generate("Problem text...")

# BATCH mode
pipeline = UnifiedPipeline(
    mode=PipelineMode.BATCH,
    enable_property_graph=True,
    enable_nlp_enrichment=True
)
result = pipeline.generate("Problem text...")
```

### New Code (unified_diagram_pipeline.py) - RECOMMENDED

```python
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import os

# Get API key (optional - can run offline without it)
api_key = os.environ.get('DEEPSEEK_API_KEY')

# Create configuration
config = PipelineConfig(
    api_key=api_key,  # None = offline mode with local fallback

    # Original features
    validation_mode="strict",
    enable_layout_optimization=True,
    enable_domain_embellishments=True,
    enable_ai_validation=True,

    # Advanced features
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_complexity_assessment=True,
    enable_strategic_planning=True,
    enable_ontology_validation=True,
    enable_z3_optimization=True,
    enable_llm_auditing=True,

    # NLP tools (choose which to use)
    nlp_tools=['openie', 'stanza', 'scibert', 'dygie'],

    # Auditor backend
    auditor_backend='mock'  # Options: 'claude', 'gpt', 'local', 'mock'
)

# Create pipeline
pipeline = UnifiedDiagramPipeline(config)

# Generate diagram
result = pipeline.generate("A 2μF capacitor...")

# Access complete results
print(f"SVG: {result.svg}")
print(f"Complexity: {result.complexity_score}")
print(f"Strategy: {result.selected_strategy}")
print(f"Ontology valid: {result.ontology_validation}")
print(f"Audit score: {result.audit_report['overall_score']}")

# Save files (convenience methods)
result.save_svg("output.svg")
result.save_scene("output_scene.json")

# Access advanced features
if result.property_graph:
    print(f"Nodes: {len(result.property_graph.get_all_nodes())}")
    print(f"Edges: {len(result.property_graph.get_all_edges())}")

if result.nlp_results:
    print(f"NLP tools used: {list(result.nlp_results.keys())}")
```

---

## Feature Comparison

| Feature | core/unified_pipeline.py | unified_diagram_pipeline.py |
|---------|-------------------------|---------------------------|
| **PropertyGraph** | ✅ | ✅ |
| **NLP Tools** (OpenIE, Stanza, etc.) | ✅ | ✅ |
| **DiagramRefiner** | ✅ | ✅ |
| **Z3LayoutSolver** | ✅ | ✅ |
| **DiagramValidator** | ✅ | ✅ |
| **VLMValidator** | ✅ | ✅ |
| **PrimitiveLibrary** | ✅ | ❌ (not needed) |
| **DiagramPlanner** | ❌ | ✅ |
| **DiagramAuditor** | ❌ | ✅ |
| **ModelOrchestrator** | ❌ | ✅ |
| **OntologyManager** (actually used) | ❌ | ✅ |
| **AestheticAnalyzer** (actually used) | ❌ | ❌ (exists but not used) |
| **Pipeline Modes** | 4 modes | Config-based |
| **Architecture** | Mixed steps | 7 clean phases |
| **Configuration** | Individual params | PipelineConfig dataclass |
| **Result Format** | Incomplete | Complete |

---

## Timeline

- **November 6, 2025**: core/unified_pipeline.py created
- **November 10, 2025**: Gap analysis revealed incompleteness
- **November 10, 2025**: core/unified_pipeline.py deprecated
- **Going Forward**: Use unified_diagram_pipeline.py for all new code

---

## Files Status

### ✅ ACTIVE (Use These)

1. **unified_diagram_pipeline.py** - PRIMARY PIPELINE
   - Complete feature set
   - 7-phase architecture
   - All advanced features
   - Complete result format

### ⚠️ DEPRECATED (Don't Use)

1. **core/unified_pipeline.py** - DEPRECATED
   - Incomplete feature set
   - Missing critical components
   - Kept for backward compatibility only
   - Shows deprecation warning when imported

### 📚 Documentation

1. **PIPELINE_MERGER_GAP_ANALYSIS.md** - Detailed comparison
2. **REVERSE_MERGER_PLAN.md** - Why unified_diagram_pipeline.py is better
3. **DEPRECATION_NOTICE.md** - This file
4. **SINGLE_UNIFIED_PIPELINE_COMPLETE.md** - Original merger docs (outdated)

---

## Web Interface Update Required

**Current**: web_interface.py uses `core.unified_pipeline`
**Required**: Update to use `unified_diagram_pipeline`

```python
# OLD:
from core.unified_pipeline import UnifiedPipeline, PipelineMode

# NEW:
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
```

---

## Testing

All existing tests using core/unified_pipeline.py will continue to work but will show deprecation warnings:

```
⚠️  DEPRECATION WARNING
core.unified_pipeline is DEPRECATED.
Please use 'unified_diagram_pipeline.py' instead.
```

To suppress warnings during transition:
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

---

## Support

- **Questions**: See PIPELINE_MERGER_GAP_ANALYSIS.md for detailed comparison
- **Migration Help**: See code examples above
- **Issues**: Check if unified_diagram_pipeline.py already supports your use case

---

## Future Plans

1. ✅ **Immediate**: core/unified_pipeline.py deprecated
2. ⬜ **Short-term**: Update web_interface.py to use unified_diagram_pipeline.py
3. ⬜ **Long-term**: Remove core/unified_pipeline.py after transition period
4. ⬜ **Optional**: Add PrimitiveLibrary to unified_diagram_pipeline.py if needed

---

**Decision**: Deprecate core/unified_pipeline.py ✅
**Reason**: Incomplete implementation, better alternative exists
**Action**: Use unified_diagram_pipeline.py for all new code
**Timeline**: Immediate

---

**Generated**: November 10, 2025
**Status**: ACTIVE DEPRECATION NOTICE
