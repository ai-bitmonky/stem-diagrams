# Pipeline Architecture Comparison & Migration Plan
**Date:** November 6, 2025
**Issue:** Multiple pipeline implementations with different architectures

---

## Problem Statement

The codebase has **THREE different pipeline implementations**:

1. **Baseline:** `unified_diagram_generator.py` (connected to web editor)
2. **Roadmap:** `unified_diagram_pipeline.py` (Phase 1-7 architecture)
3. **Enhanced:** `enhanced_diagram_generator.py` (Phase 2+ hybrid)

This creates confusion and prevents the new frameworks (LLM, VLM, Domain Registry) from integrating properly.

---

## Architecture Comparison

### 1. Baseline Pipeline (unified_diagram_generator.py)

**Status:** ✅ Working, connected to web editor

**Architecture:**
```
Text Input
    ↓
SimpleNLPPipeline (spaCy + keyword heuristics)
    ├─ Domain Classification (keyword matching - line 120)
    ├─ Entity Extraction (spaCy NER)
    └─ Relationship Extraction (proximity-based)
    ↓
Subject Interpreter (get_interpreter(domain))
    └─ Builds UniversalScene
    ↓
UniversalSVGRenderer
    ↓
SVG Output
```

**Key Characteristics:**
- ✅ **Simple and fast** (~1 second per diagram)
- ✅ **100% offline** (no API calls)
- ✅ **Web editor integration** (web/static/js/editor.js:1)
- ❌ **Keyword-based domain detection** (line 91-118)
- ❌ **Basic entity extraction** (only CARDINAL, QUANTITY, PRODUCT)
- ❌ **No LLM/VLM integration**
- ❌ **No domain registry** (hardcoded interpreters)

**Code Example:**
```python
# Line 91-118: Keyword-based domain classification
def _classify_domain(self, doc) -> str:
    domains = {
        'electronics': ['circuit', 'capacitor', 'resistor', ...],
        'physics': ['force', 'mass', 'acceleration', ...],
        ...
    }
    scores = {domain: sum(1 for kw in keywords if kw in text_lower)
              for domain, keywords in domains.items()}
    return max(scores, key=scores.get)
```

**Usage:**
```python
generator = UnifiedDiagramGenerator()
result = generator.generate(problem_text)
# Returns: {'svg': ..., 'scene': ..., 'nlp_results': ...}
```

---

### 2. Roadmap Pipeline (unified_diagram_pipeline.py)

**Status:** ⚠️ Requires API key, follows roadmap spec

**Architecture:**
```
Text Input
    ↓
Phase 1: UniversalAIAnalyzer (DeepSeek API)
    └─ Generates CanonicalProblemSpec
    ↓
Phase 2: UniversalSceneBuilder
    └─ Builds Scene (with JSON schema validation)
    ↓
Phase 3: JSON Schema Validation
    └─ Validates scene structure
    ↓
Phase 4: UniversalValidator
    └─ Semantic + geometric + physics checks
    ↓
Phase 5: UniversalLayoutEngine
    └─ Optimizes layout
    ↓
Phase 6: UniversalRenderer
    └─ Renders to SVG
    ↓
Phase 7: BidirectionalValidator (AI post-validation)
    └─ Quality check
    ↓
DiagramResult (SVG + Scene + Validation Reports)
```

**Key Characteristics:**
- ✅ **Follows roadmap architecture** (7 phases)
- ✅ **AI-powered analysis** (UniversalAIAnalyzer)
- ✅ **Multi-stage validation**
- ✅ **JSON schema compliance**
- ❌ **Requires API key** (DeepSeek/OpenAI)
- ❌ **Not connected to web editor**
- ❌ **Slower** (API calls add latency)

**Code Example:**
```python
# UnifiedDiagramPipeline configuration
config = PipelineConfig(
    api_key="sk-...",
    api_model="deepseek-chat",
    validation_mode="strict",
    enable_ai_validation=True
)

pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate_diagram(problem_text)
# Returns: DiagramResult with full validation reports
```

---

### 3. Enhanced Pipeline (enhanced_diagram_generator.py)

**Status:** ⚠️ Hybrid approach, used for batch processing

**Architecture:**
```
Text Input
    ↓
EnhancedNLPPipeline (spaCy + weighted keywords)
    ├─ Enhanced Domain Classification (weighted scoring)
    ├─ Enhanced Entity Extraction (with regex)
    └─ Enhanced Relationship Extraction
    ↓
AdvancedSceneBuilder (physics-aware)
    └─ Builds UniversalScene with detailed components
    ↓
UniversalSVGRenderer
    ↓
SVG Output
```

**Key Characteristics:**
- ✅ **Better than baseline** (weighted keywords, regex extraction)
- ✅ **Physics-aware scene building**
- ✅ **Offline operation**
- ❌ **Still keyword-based** (not AI-powered)
- ❌ **Not connected to web editor**
- ❌ **Separate from roadmap architecture**

**Code Example:**
```python
generator = EnhancedDiagramGenerator()
result = generator.generate(problem_text)
# Returns: {'svg': ..., 'scene': ..., 'nlp_results': ...}
```

---

## Feature Comparison Matrix

| Feature | Baseline | Roadmap | Enhanced | New Frameworks |
|---------|----------|---------|----------|----------------|
| **Domain Detection** | ❌ Keywords | ✅ AI | ⚠️ Weighted KW | ✅ Registry |
| **Entity Extraction** | ❌ Basic spaCy | ✅ AI | ⚠️ spaCy+Regex | ⚠️ Not integrated |
| **Scene Building** | ⚠️ Subject Interpreters | ✅ Universal | ✅ Advanced | ✅ Domain Builders |
| **LLM Integration** | ❌ None | ✅ AI Analyzer | ❌ None | ✅ Framework ready |
| **VLM Validation** | ❌ None | ⚠️ Bidirectional | ❌ None | ✅ Framework ready |
| **Primitive Library** | ❌ None | ❌ None | ❌ None | ✅ Production ready |
| **Validation** | ❌ None | ✅ Multi-stage | ❌ None | ✅ Rule-based |
| **Web Editor** | ✅ Integrated | ❌ No | ❌ No | ❌ No |
| **API Required** | ✅ No | ❌ Yes | ✅ No | ⚠️ Optional |
| **Speed** | ✅ Fast (1s) | ❌ Slow (5-10s) | ✅ Fast (1s) | ⚠️ Varies |
| **Maturity** | ✅ Working | ⚠️ Complete | ✅ Working | ⚠️ Framework |

---

## The Disconnect Issue

### Current State
```
┌─────────────────────────────────────────────────┐
│          Web Editor (editor.js)                 │
│                                                 │
│  Calls: UnifiedDiagramGenerator.generate()     │
└──────────────────┬──────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────┐
│    unified_diagram_generator.py (BASELINE)      │
│                                                 │
│  • SimpleNLPPipeline (keyword heuristics)       │
│  • Subject Interpreters (hardcoded)             │
│  • No LLM/VLM/Registry integration              │
└─────────────────────────────────────────────────┘

         [NEW FRAMEWORKS ISOLATED]

┌─────────────────────────────────────────────────┐
│  domain_registry.py  (not connected)            │
│  llm_integration.py  (not connected)            │
│  vlm_validator.py    (not connected)            │
│  primitive_library.py (not connected)           │
└─────────────────────────────────────────────────┘

         [ROADMAP PIPELINE ISOLATED]

┌─────────────────────────────────────────────────┐
│    unified_diagram_pipeline.py (ROADMAP)        │
│                                                 │
│  • Full Phase 1-7 architecture                  │
│  • AI-powered                                   │
│  • Not connected to web editor                  │
└─────────────────────────────────────────────────┘
```

### Issues
1. **Web editor uses baseline** - no access to new features
2. **New frameworks isolated** - not integrated anywhere
3. **Roadmap pipeline isolated** - exists but not used
4. **Three separate codepaths** - duplication and confusion

---

## Proposed Solution: Unified Architecture

### Goal
Create **ONE pipeline** that:
- ✅ Works with web editor
- ✅ Integrates new frameworks (LLM, VLM, Domain Registry)
- ✅ Follows roadmap architecture
- ✅ Supports both offline (fast) and AI-powered (accurate) modes
- ✅ Backward compatible

### Strategy: Mode-Based Pipeline

```python
class UnifiedPipeline:
    """
    Single pipeline with configurable modes
    """

    def __init__(self, mode: str = "fast"):
        """
        Modes:
        - 'fast': Offline, keyword-based (current baseline)
        - 'accurate': LLM-powered, slower
        - 'premium': LLM + VLM validation
        """
        self.mode = mode

        # Initialize components based on mode
        if mode == "fast":
            self.nlp = SimpleNLPPipeline()
            self.scene_builder = SubjectInterpreterAdapter()
        elif mode == "accurate":
            self.llm_planner = LLMDiagramPlanner()
            self.domain_registry = get_domain_registry()
        elif mode == "premium":
            self.llm_planner = LLMDiagramPlanner()
            self.domain_registry = get_domain_registry()
            self.vlm_validator = VLMValidator()
```

### Architecture

```
┌─────────────────────────────────────────────────┐
│              Web Editor (editor.js)             │
│                                                 │
│  Calls: UnifiedPipeline.generate(mode="fast")  │
└──────────────────┬──────────────────────────────┘
                   │
                   v
┌─────────────────────────────────────────────────┐
│         UnifiedPipeline (NEW)                   │
│                                                 │
│  ┌───────────────────────────────────┐          │
│  │  Mode: Fast (default)             │          │
│  ├───────────────────────────────────┤          │
│  │  SimpleNLPPipeline                │          │
│  │  Domain Registry (keyword-based)  │          │
│  │  Primitive Library                │          │
│  └───────────────────────────────────┘          │
│                                                 │
│  ┌───────────────────────────────────┐          │
│  │  Mode: Accurate (opt-in)          │          │
│  ├───────────────────────────────────┤          │
│  │  LLM Planner                      │          │
│  │  Domain Registry (AI-powered)     │          │
│  │  Primitive Library                │          │
│  └───────────────────────────────────┘          │
│                                                 │
│  ┌───────────────────────────────────┐          │
│  │  Mode: Premium (opt-in)           │          │
│  ├───────────────────────────────────┤          │
│  │  LLM Planner                      │          │
│  │  Domain Registry                  │          │
│  │  Primitive Library                │          │
│  │  VLM Validator                    │          │
│  └───────────────────────────────────┘          │
│                                                 │
│  Common Components:                             │
│  • UniversalScene                               │
│  • UniversalValidator                           │
│  • UniversalLayoutEngine                        │
│  • UniversalSVGRenderer                         │
└─────────────────────────────────────────────────┘
```

---

## Migration Plan

### Phase 1: Create Unified Pipeline (Week 1)
**Goal:** Single entry point with mode selection

1. Create `core/unified_pipeline.py`
2. Implement `UnifiedPipeline` class with 3 modes
3. Create adapters for existing components
4. Add mode parameter to web editor
5. Test all three modes

**Deliverables:**
- [ ] `core/unified_pipeline.py` (new)
- [ ] Mode selector in web editor UI
- [ ] Backward compatibility test suite

### Phase 2: Integrate New Frameworks (Week 2)
**Goal:** Make new frameworks accessible

1. Integrate Domain Registry into "fast" mode
2. Integrate LLM Planner into "accurate" mode
3. Integrate VLM Validator into "premium" mode
4. Add Primitive Library to all modes
5. Update web editor to show mode capabilities

**Deliverables:**
- [ ] Domain Registry integration
- [ ] LLM integration (with Ollama option)
- [ ] VLM integration (optional feature)
- [ ] Primitive Library usage

### Phase 3: Deprecate Old Pipelines (Week 3)
**Goal:** Clean up codebase

1. Mark `unified_diagram_generator.py` as deprecated
2. Mark `enhanced_diagram_generator.py` as deprecated
3. Update all scripts to use `UnifiedPipeline`
4. Add migration guide
5. Archive old files

**Deliverables:**
- [ ] Deprecation warnings
- [ ] Migration guide for users
- [ ] Updated documentation

---

## Implementation: Unified Pipeline

### Code Structure

```python
# core/unified_pipeline.py

from typing import Dict, Optional, Literal
from enum import Enum

class PipelineMode(Enum):
    FAST = "fast"          # Offline, keyword-based
    ACCURATE = "accurate"  # LLM-powered
    PREMIUM = "premium"    # LLM + VLM

class UnifiedPipeline:
    """
    Single unified pipeline for all diagram generation

    Replaces:
    - unified_diagram_generator.py (baseline)
    - enhanced_diagram_generator.py (Phase 2)
    - unified_diagram_pipeline.py (roadmap)
    """

    def __init__(
        self,
        mode: PipelineMode = PipelineMode.FAST,
        llm_config: Optional[LLMConfig] = None,
        vlm_config: Optional[VLMConfig] = None
    ):
        self.mode = mode

        # Initialize components based on mode
        self._init_nlp(mode)
        self._init_scene_builder(mode)
        self._init_validator(mode)
        self._init_renderer()

    def generate(self, problem_text: str) -> Dict:
        """
        Generate diagram from text

        Returns same format as baseline for compatibility
        """
        # Step 1: Analyze (mode-dependent)
        if self.mode == PipelineMode.FAST:
            analysis = self.nlp_pipeline.process(problem_text)
        else:
            analysis = self.llm_planner.generate_plan(problem_text)

        # Step 2: Build scene (uses domain registry)
        builder = self.domain_registry.get_builder_for_problem(
            analysis, problem_text
        )
        scene = builder.build_scene(analysis, problem_text)

        # Step 3: Validate
        validation = self.validator.validate(scene)

        # Step 4: Render
        svg = self.renderer.render(scene)

        # Step 5: VLM validation (premium mode only)
        if self.mode == PipelineMode.PREMIUM:
            vlm_result = self.vlm_validator.validate_diagram(
                svg_path, problem_text
            )
            validation['vlm'] = vlm_result

        return {
            'success': True,
            'svg': svg,
            'scene': scene,
            'validation': validation,
            'mode': self.mode.value
        }
```

### Web Editor Integration

```javascript
// web/static/js/editor.js

// Add mode selector
const modeSelector = document.getElementById('pipeline-mode');

// Update generate call
async function generateDiagram() {
    const mode = modeSelector.value; // 'fast', 'accurate', or 'premium'

    const response = await fetch('/api/generate', {
        method: 'POST',
        body: JSON.stringify({
            problem_text: editor.value,
            mode: mode
        })
    });

    const result = await response.json();

    // Show mode-specific feedback
    if (result.mode === 'premium' && result.validation.vlm) {
        showVLMValidation(result.validation.vlm);
    }
}
```

---

## Benefits of Unified Approach

### For Users
- ✅ **One interface** - no confusion about which pipeline to use
- ✅ **Mode choice** - can choose speed vs. accuracy
- ✅ **Progressive enhancement** - start with fast, upgrade to accurate
- ✅ **Web editor works** - with all new features

### For Developers
- ✅ **Single codebase** - easier to maintain
- ✅ **Clear architecture** - follows roadmap
- ✅ **Pluggable components** - easy to add features
- ✅ **Testable** - each mode can be tested independently

### For Roadmap
- ✅ **Gap closure** - connects baseline to roadmap
- ✅ **Framework utilization** - new frameworks actually used
- ✅ **Migration path** - clear upgrade from current state
- ✅ **Backward compatibility** - doesn't break existing code

---

## Timeline

| Week | Phase | Tasks | Status |
|------|-------|-------|--------|
| 1 | Architecture | Create UnifiedPipeline, mode system | 🔲 Not started |
| 2 | Integration | Add LLM/VLM/Registry to modes | 🔲 Not started |
| 3 | Web Editor | Update UI, add mode selector | 🔲 Not started |
| 4 | Testing | Test all modes, validate migration | 🔲 Not started |
| 5 | Deprecation | Mark old files, migration guide | 🔲 Not started |

---

## Next Steps

### Immediate Actions
1. ✅ Document the disconnect (this file)
2. 🔲 Get stakeholder approval for unified approach
3. 🔲 Create `core/unified_pipeline.py` skeleton
4. 🔲 Write migration tests

### This Week
5. 🔲 Implement "fast" mode (wraps baseline)
6. 🔲 Implement "accurate" mode (integrates LLM)
7. 🔲 Test backward compatibility

### Next Week
8. 🔲 Update web editor with mode selector
9. 🔲 Integrate new frameworks
10. 🔲 Write user documentation

---

## Conclusion

**The Problem:** Three separate pipelines with no integration of new frameworks.

**The Solution:** One unified pipeline with configurable modes.

**The Benefit:** Clean architecture that bridges baseline → roadmap while keeping web editor working.

**Status:** Framework implementations complete, ready for unification.
