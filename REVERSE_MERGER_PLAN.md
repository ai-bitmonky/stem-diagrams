# Reverse Merger Plan - The Right Direction

**Date**: November 10, 2025
**Decision**: ✅ **DEPRECATE core/unified_pipeline.py, KEEP unified_diagram_pipeline.py**

---

## Why This Makes More Sense

### unified_diagram_pipeline.py (KEEP THIS) ✅
**Advantages**:
1. ✅ **More complete architecture** - 7 phases with clear separation
2. ✅ **Has DiagramPlanner** - Complexity + strategy selection
3. ✅ **Has DiagramAuditor** - LLM quality auditing
4. ✅ **Has ModelOrchestrator** - Dynamic model selection
5. ✅ **OntologyManager ACTUALLY USED** - Not just initialized
6. ✅ **Complete result format** - All fields + save methods
7. ✅ **PipelineConfig dataclass** - Clean configuration
8. ✅ **UniversalAIAnalyzer** - Offline fallback support
9. ✅ **UniversalSceneBuilder** - Consistent scene building
10. ✅ **UniversalLayoutEngine** - Dedicated layout phase
11. ✅ **Proper phase architecture** - Well-organized flow
12. ✅ **Complete metadata tracking** - Traces, timing, features

**Missing (needs to be added)**:
1. ❌ PrimitiveLibrary integration
2. ❌ Multiple modes (FAST/ACCURATE/PREMIUM/BATCH)
3. ❌ EnhancedNLPAdapter option for fast mode
4. ❌ DomainRegistry option for scene building

### core/unified_pipeline.py (DEPRECATE THIS) ❌
**Advantages**:
1. ✅ PrimitiveLibrary integration (Steps 4, 5.5)
2. ✅ Multiple modes (FAST, ACCURATE, PREMIUM, BATCH)
3. ✅ EnhancedNLPAdapter for FAST mode
4. ✅ DomainRegistry for scene building
5. ✅ Web interface compatible

**Missing (critical gaps)**:
1. ❌ No DiagramPlanner
2. ❌ No DiagramAuditor
3. ❌ No ModelOrchestrator
4. ❌ OntologyManager initialized but never used
5. ❌ AestheticAnalyzer initialized but never used
6. ❌ Incomplete result format
7. ❌ No save_svg()/save_scene() methods
8. ❌ Different architecture (less organized)

---

## What Needs to Be Merged

### FROM core/unified_pipeline.py → unified_diagram_pipeline.py

#### 1. PrimitiveLibrary Integration ⭐ HIGH PRIORITY
**Location in core/unified_pipeline.py**:
- Lines 60-65: Import
- Lines 451-464: Initialization
- Lines 789-810: Query/search (Step 4)
- Lines 836-877: Ingestion (Step 5.5)

**Integration Plan**:
- Add to PipelineConfig as `enable_primitives: bool = True`
- Add initialization in `__init__`
- Add Phase 3.5: Primitive Library Query (before rendering)
- Add Phase 6.5: Primitive Ingestion (after rendering)
- Pass primitives to renderer

#### 2. Multiple Pipeline Modes ⭐ HIGH PRIORITY
**Location in core/unified_pipeline.py**:
- Lines 145-150: PipelineMode enum
- Lines 256-273: Auto-configuration logic
- Mode-specific initialization

**Integration Plan**:
- Add PipelineMode enum (FAST, ACCURATE, PREMIUM, BATCH)
- Update PipelineConfig to accept mode parameter
- Auto-configure features based on mode:
  - FAST: Minimal features, speed-optimized
  - ACCURATE: LLM + advanced features
  - PREMIUM: All features + VLM
  - BATCH: All features + PropertyGraph + NLP tools
- Keep existing feature flags for override

#### 3. EnhancedNLPAdapter (for FAST mode) 🔧 MEDIUM PRIORITY
**Location in core/unified_pipeline.py**:
- Lines 67-73: Import
- Lines 301-317: Initialization (FAST mode)
- Lines 624-635: Usage

**Integration Plan**:
- Add to imports with graceful degradation
- In FAST mode: Use EnhancedNLPAdapter instead of UniversalAIAnalyzer
- Fallback: Keep existing UniversalAIAnalyzer if EnhancedNLPAdapter unavailable

#### 4. DomainRegistry (alternative scene building) 🔧 MEDIUM PRIORITY
**Location in core/unified_pipeline.py**:
- Lines 32-37: Import
- Lines 333-355: Initialization
- Lines 663-670: Usage

**Integration Plan**:
- Add to imports with graceful degradation
- Add config option: `scene_builder: str = "universal"` (options: "universal", "domain_registry")
- Allow user to choose between UniversalSceneBuilder and DomainRegistry
- Keep UniversalSceneBuilder as default (more stable)

#### 5. Workflow Refinements 📝 LOW PRIORITY
**Better from core/unified_pipeline.py**:
- Step-by-step output with timing
- Better error messages
- Clear progress indicators

**Integration Plan**:
- Improve existing phase output in unified_diagram_pipeline.py
- Add timing per phase
- Keep existing phase architecture (it's cleaner)

---

## Migration Plan

### Phase 1: Add PrimitiveLibrary (2-3 hours)
1. Import PrimitiveLibrary with graceful degradation
2. Add `enable_primitives` to PipelineConfig
3. Initialize in `__init__`
4. Add Phase 3.5: Primitive Query (before Phase 6: Rendering)
5. Add Phase 6.5: Primitive Ingestion (after Phase 6: Rendering)
6. Pass primitives to renderer
7. Test with example diagram

### Phase 2: Add Multiple Modes (2-3 hours)
1. Add PipelineMode enum
2. Update PipelineConfig to accept `mode: PipelineMode`
3. Add auto-configuration logic based on mode
4. Update feature flags to respect mode defaults
5. Test all 4 modes (FAST, ACCURATE, PREMIUM, BATCH)

### Phase 3: Add EnhancedNLPAdapter for FAST mode (1-2 hours)
1. Import EnhancedNLPAdapter with fallback
2. Add mode-switching logic in Phase 1
3. Use EnhancedNLPAdapter if mode=FAST and available
4. Keep UniversalAIAnalyzer as default/fallback
5. Test FAST mode with EnhancedNLPAdapter

### Phase 4: Add DomainRegistry Option (1-2 hours)
1. Import DomainRegistry with fallback
2. Add `scene_builder` config option
3. Add switching logic in Phase 2
4. Keep UniversalSceneBuilder as default
5. Test with DomainRegistry option

### Phase 5: Update Web Interface (1 hour)
1. Update web_interface.py to import from unified_diagram_pipeline.py
2. Update to use new PipelineMode if needed
3. Update configuration
4. Test web interface

### Phase 6: Deprecate core/unified_pipeline.py (30 min)
1. Add deprecation notice to core/unified_pipeline.py
2. Update all documentation
3. Update README
4. Keep file for backward compatibility with deprecation warning

**Total Estimated Time**: 8-12 hours

---

## Updated Architecture

### unified_diagram_pipeline.py (PRODUCTION PIPELINE)

```
Configuration:
  - PipelineConfig (dataclass)
  - PipelineMode: FAST | ACCURATE | PREMIUM | BATCH
  - All feature flags
  - Auto-configuration based on mode

Phase 0: NLP Enrichment (OpenIE, Stanza, DyGIE++, SciBERT)
    ↓
Phase 0.5: Property Graph Construction
    ↓
Phase 1: Problem Understanding + Complexity Assessment
    - FAST mode: EnhancedNLPAdapter (optional)
    - ACCURATE/PREMIUM/BATCH: UniversalAIAnalyzer
    - DiagramPlanner: Complexity scoring
    ↓
Phase 2: Scene Synthesis + Strategic Planning
    - UniversalSceneBuilder (default)
    - DomainRegistry (optional)
    - DiagramPlanner: Strategy selection
    ↓
Phase 3: Ontology Validation
    - OntologyManager: Semantic validation
    ↓
Phase 3.5: Primitive Library Query (NEW)
    - PrimitiveLibrary: Search for reusable components
    ↓
Phase 4: Physics Validation
    - UniversalValidator: Physics validation
    ↓
Phase 5: Layout Optimization + Z3
    - UniversalLayoutEngine
    - Z3LayoutSolver: Constraint optimization
    ↓
Phase 6: Rendering
    - UniversalRenderer (with primitive support)
    ↓
Phase 6.5: Primitive Ingestion (NEW)
    - PrimitiveLibrary: Store new primitives
    ↓
Phase 7: Post-Validation + LLM Auditing
    - DiagramValidator: Structural validation
    - DiagramRefiner: Auto-improvement
    - VLMValidator: Visual-semantic validation
    - DiagramAuditor: LLM quality auditing
```

---

## Result Format (Complete)

```python
@dataclass
class DiagramResult:
    """Complete result from diagram generation"""

    # Output
    svg: str

    # Intermediate artifacts
    scene: Scene
    specs: CanonicalProblemSpec

    # Validation reports
    validation_report: ValidationReport
    quality_report: Optional[Dict] = None

    # Advanced pipeline artifacts
    property_graph: Optional[Any] = None
    nlp_results: Optional[Dict] = None
    complexity_score: Optional[float] = None
    selected_strategy: Optional[str] = None
    ontology_validation: Optional[Dict] = None
    audit_report: Optional[Dict] = None

    # NEW from core/unified_pipeline.py
    primitives_used: Optional[List[str]] = None
    primitives_ingested: Optional[int] = None
    refinement_applied: bool = False
    z3_layout_applied: bool = False

    # Metadata
    metadata: Dict = None

    # Convenience methods
    def save_svg(self, output_path: str)
    def save_scene(self, output_path: str)
```

---

## Files to Update

### 1. unified_diagram_pipeline.py (ENHANCE)
- Add PrimitiveLibrary integration
- Add PipelineMode enum
- Add mode-based auto-configuration
- Add EnhancedNLPAdapter option
- Add DomainRegistry option
- Update DiagramResult with new fields

### 2. core/unified_pipeline.py (DEPRECATE)
- Add deprecation warning at top
- Update docstring to point to unified_diagram_pipeline.py
- Keep for backward compatibility

### 3. web_interface.py (UPDATE)
- Change import from `core.unified_pipeline` to `unified_diagram_pipeline`
- Update configuration if needed
- Test compatibility

### 4. Documentation (UPDATE)
- SINGLE_UNIFIED_PIPELINE_COMPLETE.md → Update to reference unified_diagram_pipeline.py
- README.md → Update to reference unified_diagram_pipeline.py
- Add migration guide

---

## Backward Compatibility

### For existing code using core/unified_pipeline.py:
```python
# Option 1: Keep importing from core/unified_pipeline
from core.unified_pipeline import UnifiedPipeline, PipelineMode
# Will work but show deprecation warning

# Option 2: Update to new location
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
# New imports, full functionality
```

### For batch scripts using unified_diagram_pipeline.py:
```python
# No changes needed! Just get new features automatically:
# - PrimitiveLibrary (if enable_primitives=True)
# - Multiple modes (if mode specified)
# - Better performance options
```

---

## Benefits of This Approach

1. ✅ **Keep the better architecture** - 7 phases, cleaner separation
2. ✅ **Keep all existing features** - DiagramPlanner, DiagramAuditor, etc.
3. ✅ **Add missing features** - PrimitiveLibrary, multiple modes
4. ✅ **Minimal disruption** - Batch scripts keep working
5. ✅ **Better long-term maintainability** - One superior pipeline
6. ✅ **Complete functionality** - All features in one place
7. ✅ **Cleaner codebase** - Better organized phases
8. ✅ **Proper configuration** - PipelineConfig dataclass

---

## Decision

✅ **APPROVED**: Deprecate core/unified_pipeline.py, enhance unified_diagram_pipeline.py

**Next Steps**:
1. Implement Phase 1: PrimitiveLibrary integration
2. Implement Phase 2: Multiple modes
3. Implement Phase 3: EnhancedNLPAdapter option
4. Implement Phase 4: DomainRegistry option
5. Update web interface
6. Deprecate core/unified_pipeline.py
7. Update documentation

**Estimated Time**: 8-12 hours
**Priority**: HIGH - Consolidates architecture properly

---

**Generated**: November 10, 2025
**Status**: READY TO IMPLEMENT
**Approach**: CORRECT - Keep the better pipeline, enhance it
