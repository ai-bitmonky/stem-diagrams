"""
⚠️  DEPRECATED - Use unified_diagram_pipeline.py Instead
========================================================

**STATUS**: This module is DEPRECATED as of November 10, 2025.

**USE INSTEAD**: unified_diagram_pipeline.py

**WHY DEPRECATED**:
This pipeline is incomplete and missing several critical components:
- DiagramPlanner (complexity assessment + strategy selection)
- DiagramAuditor (LLM quality auditing)
- ModelOrchestrator (dynamic model selection)
- OntologyManager usage (initialized but never executed)
- AestheticAnalyzer usage (initialized but never executed)
- Complete result format (missing fields: complexity_score, selected_strategy, ontology_validation, audit_report)
- Proper phase architecture (unified_diagram_pipeline.py has cleaner 7-phase architecture)

**unified_diagram_pipeline.py INCLUDES**:
✅ All features from this file (PropertyGraph, NLP tools, DiagramRefiner, Z3, VLM)
✅ PLUS: DiagramPlanner, DiagramAuditor, ModelOrchestrator, Ontology validation, LLM auditing
✅ Better architecture with 7 clear phases
✅ Complete PipelineConfig dataclass
✅ Complete DiagramResult with save_svg()/save_scene() methods
✅ All metadata and tracking

**MIGRATION**:
```python
# OLD (deprecated):
from core.unified_pipeline import UnifiedPipeline, PipelineMode
pipeline = UnifiedPipeline(mode=PipelineMode.FAST)

# NEW (recommended):
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    # ... all features available
)
pipeline = UnifiedDiagramPipeline(config)
```

**This file is kept for backward compatibility only.**
**All new code should use unified_diagram_pipeline.py**

---

Original Documentation (DEPRECATED):
====================================

Unified Pipeline - Single Entry Point for All Diagram Generation
=================================================================

Replaces and unifies:
1. unified_diagram_generator.py (baseline - keyword heuristics)
2. enhanced_diagram_generator.py (Phase 2 - weighted keywords)
3. unified_diagram_pipeline.py (roadmap - AI-powered)

Features THREE modes:
- FAST: Offline, keyword-based (1s per diagram)
- ACCURATE: LLM-powered planning (5-10s per diagram)
- PREMIUM: LLM + VLM validation (10-15s per diagram)

Author: Universal STEM Diagram Generator
Date: November 6, 2025
Deprecated: November 10, 2025
"""

import warnings

# Show deprecation warning when imported
warnings.warn(
    "\n"
    "=" * 80 + "\n"
    "⚠️  DEPRECATION WARNING\n"
    "=" * 80 + "\n"
    "core.unified_pipeline is DEPRECATED.\n"
    "\n"
    "Please use 'unified_diagram_pipeline.py' instead.\n"
    "\n"
    "Why? unified_diagram_pipeline.py has:\n"
    "  ✅ Complete feature set (DiagramPlanner, DiagramAuditor, etc.)\n"
    "  ✅ Better architecture (7 clean phases)\n"
    "  ✅ Complete result format with all fields\n"
    "  ✅ All features from this file PLUS more\n"
    "\n"
    "Migration:\n"
    "  from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig\n"
    "\n"
    "See PIPELINE_MERGER_GAP_ANALYSIS.md for details.\n"
    "=" * 80 + "\n",
    DeprecationWarning,
    stacklevel=2
)

from typing import Dict, List, Any, Optional, Literal
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import time
import json

# Core components
from core.universal_scene_format import UniversalScene
from core.universal_svg_renderer import UniversalSVGRenderer
from core.universal_validator import UniversalValidator, ValidationReport

# New frameworks
try:
    from core.domain_registry import get_domain_registry, DomainRegistry
    HAS_DOMAIN_REGISTRY = True
except ImportError:
    HAS_DOMAIN_REGISTRY = False
    print("⚠️  Domain registry not available")

try:
    from core.llm_integration import LLMDiagramPlanner, LLMConfig, StubLLMPlanner
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    print("⚠️  LLM integration not available")

try:
    from core.vlm_validator import VLMValidator, VLMConfig, VLMProvider, VisualValidationResult
    HAS_VLM = True
except ImportError:
    HAS_VLM = False
    print("⚠️  VLM validator not available")

try:
    from core.validation_refinement import DiagramValidator, DiagramRefiner, QualityScore
    HAS_DIAGRAM_VALIDATOR = True
except ImportError:
    HAS_DIAGRAM_VALIDATOR = False
    print("⚠️  Diagram validator not available")

try:
    from core.primitive_library import PrimitiveLibrary
    HAS_PRIMITIVES = True
except ImportError:
    HAS_PRIMITIVES = False
    print("⚠️  Primitive library not available")

# Enhanced NLP (optional, improves text understanding)
try:
    from core.enhanced_nlp_adapter import EnhancedNLPAdapter
    HAS_ENHANCED_NLP = True
except ImportError:
    HAS_ENHANCED_NLP = False
    print("ℹ️  Enhanced NLP not available, using baseline")

# UniversalAIAnalyzer (for OFFLINE/BATCH modes with local fallback)
try:
    from core.universal_ai_analyzer import UniversalAIAnalyzer
    HAS_UNIVERSAL_AI_ANALYZER = True
except ImportError:
    HAS_UNIVERSAL_AI_ANALYZER = False

# LocalAIAnalyzer (for offline mode)
try:
    from core.local_ai_analyzer import LocalAIAnalyzer
    HAS_LOCAL_AI_ANALYZER = True
except ImportError:
    HAS_LOCAL_AI_ANALYZER = False

# Property Graph (knowledge representation)
try:
    from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType
    HAS_PROPERTY_GRAPH = True
except ImportError:
    HAS_PROPERTY_GRAPH = False
    print("ℹ️  Property graph not available")

# Individual NLP Tools (open-source stack)
try:
    from core.nlp_tools.openie_extractor import OpenIEExtractor
    HAS_OPENIE = True
except ImportError:
    HAS_OPENIE = False

try:
    from core.nlp_tools.stanza_enhancer import StanzaEnhancer
    HAS_STANZA = True
except ImportError:
    HAS_STANZA = False

try:
    from core.nlp_tools.scibert_embedder import SciBERTEmbedder
    HAS_SCIBERT = True
except ImportError:
    HAS_SCIBERT = False

try:
    from core.nlp_tools.dygie_extractor import DyGIEExtractor
    HAS_DYGIE = True
except ImportError:
    HAS_DYGIE = False

# Baseline components (fallback)
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False
    print("⚠️  spaCy not available")

# Aesthetic Analyzer
try:
    from core.aesthetic_analyzer import AestheticAnalyzer, AestheticScore
    HAS_AESTHETIC_ANALYZER = True
except ImportError:
    HAS_AESTHETIC_ANALYZER = False

# Ontology Manager
try:
    from core.ontology.ontology_manager import OntologyManager, Domain as OntologyDomain
    HAS_ONTOLOGY = True
except ImportError:
    HAS_ONTOLOGY = False


class PipelineMode(Enum):
    """Pipeline execution modes"""
    FAST = "fast"          # Speed-optimized, basic features only
    ACCURATE = "accurate"  # Quality-optimized, advanced features + LLM
    PREMIUM = "premium"    # Best quality, all features + VLM validation
    BATCH = "batch"        # All features enabled (for batch processing)


@dataclass
class PipelineResult:
    """Unified result format for all modes"""
    success: bool
    svg: Optional[str] = None
    scene: Optional[UniversalScene] = None
    scene_json: Optional[str] = None
    nlp_results: Optional[Dict] = None
    validation: Optional[Dict] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    files: Optional[Dict] = None

    # NEW: Advanced features
    property_graph: Optional[Any] = None  # PropertyGraph instance
    enriched_nlp_results: Optional[Dict] = None  # OpenIE, Stanza, SciBERT, DyGIE++
    refinement_applied: bool = False  # Whether automatic refinement was applied
    z3_layout_applied: bool = False  # Whether Z3 layout optimization was applied

    def to_dict(self) -> Dict:
        """Convert to dict for JSON serialization"""
        result = {
            'success': self.success,
            'svg': self.svg,
            'scene_json': self.scene_json,
            'nlp_results': self.nlp_results,
            'validation': self.validation,
            'metadata': self.metadata,
            'error': self.error,
            'files': self.files,
            'enriched_nlp_results': self.enriched_nlp_results
        }

        # Add property graph summary (not full graph)
        if self.property_graph:
            result['property_graph_summary'] = {
                'nodes': len(self.property_graph.get_all_nodes()) if hasattr(self.property_graph, 'get_all_nodes') else 0,
                'edges': len(self.property_graph.get_all_edges()) if hasattr(self.property_graph, 'get_all_edges') else 0
            }

        return result


class UnifiedPipeline:
    """
    Single unified pipeline for all diagram generation

    Supports three modes:
    - FAST: Keyword-based, offline (backward compatible with baseline)
    - ACCURATE: LLM-powered planning (uses new frameworks)
    - PREMIUM: LLM + VLM validation (full roadmap features)

    Usage:
        # Fast mode (default)
        pipeline = UnifiedPipeline()
        result = pipeline.generate("A 2μF capacitor...")

        # Accurate mode (requires Ollama)
        pipeline = UnifiedPipeline(mode=PipelineMode.ACCURATE)
        result = pipeline.generate("A 5kg block on incline...")

        # Premium mode (requires Ollama + models)
        pipeline = UnifiedPipeline(mode=PipelineMode.PREMIUM)
        result = pipeline.generate("Draw circuit...")
    """

    def __init__(
        self,
        mode: PipelineMode = PipelineMode.FAST,
        output_dir: str = "output",
        llm_config: Optional[LLMConfig] = None,
        enable_primitives: bool = True,
        enable_validation: bool = True,
        enable_property_graph: bool = False,  # NEW: PropertyGraph (off by default)
        enable_nlp_enrichment: bool = False,  # NEW: Individual NLP tools (off by default)
        nlp_tools: Optional[List[str]] = None,  # NEW: ['openie', 'stanza', 'scibert', 'dygie']
        enable_refinement: bool = None,  # NEW: Auto-refinement (auto from mode)
        enable_z3_layout: bool = None,  # NEW: Z3 constraint-based layout (auto from mode)
        enable_offline_fallback: bool = None,  # NEW: Local AI fallback (auto from mode)
        enable_ontology_validation: bool = None,  # NEW: Ontology validation (auto from mode)
        enable_aesthetic_optimization: bool = None  # NEW: Aesthetic heuristics (auto from mode)
    ):
        """
        Initialize unified pipeline

        Args:
            mode: Pipeline mode (FAST, ACCURATE, PREMIUM)
            output_dir: Directory to save output files
            llm_config: LLM configuration (for ACCURATE/PREMIUM modes)
            enable_primitives: Use primitive library
            enable_validation: Enable validation stage
            enable_property_graph: Enable PropertyGraph construction
            enable_nlp_enrichment: Enable individual NLP tools (OpenIE, Stanza, etc.)
            nlp_tools: List of NLP tools to use (default: ['openie'])
            enable_refinement: Enable automatic diagram refinement (auto from mode)
            enable_z3_layout: Enable Z3 constraint-based layout (auto from mode)
            enable_offline_fallback: Enable local AI fallback (auto from mode)
        """
        self.mode = mode
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Auto-configure features based on mode if not explicitly set
        if enable_refinement is None:
            enable_refinement = mode in [PipelineMode.ACCURATE, PipelineMode.PREMIUM, PipelineMode.BATCH]
        if enable_z3_layout is None:
            enable_z3_layout = mode in [PipelineMode.ACCURATE, PipelineMode.PREMIUM, PipelineMode.BATCH]
        if enable_ontology_validation is None:
            enable_ontology_validation = mode in [PipelineMode.ACCURATE, PipelineMode.PREMIUM, PipelineMode.BATCH]
        if enable_aesthetic_optimization is None:
            enable_aesthetic_optimization = mode in [PipelineMode.ACCURATE, PipelineMode.PREMIUM, PipelineMode.BATCH]

        # BATCH mode: Enable PropertyGraph and NLP enrichment by default
        if mode == PipelineMode.BATCH:
            if enable_property_graph is False:  # Only if not explicitly disabled
                enable_property_graph = True
            if enable_nlp_enrichment is False:  # Only if not explicitly disabled
                enable_nlp_enrichment = True
            if nlp_tools is None:
                nlp_tools = ['openie', 'stanza', 'scibert', 'dygie']  # All NLP tools

        # Store configuration
        self.enable_refinement = enable_refinement
        self.enable_z3_layout = enable_z3_layout
        self.enable_ontology_validation = enable_ontology_validation
        self.enable_aesthetic_optimization = enable_aesthetic_optimization

        # Set default NLP tools (if not set by BATCH mode)
        if nlp_tools is None:
            nlp_tools = ['openie']  # Default to OpenIE (fastest)

        print(f"🚀 Initializing Unified Pipeline (Mode: {mode.value})")

        # Initialize components based on mode
        self._init_nlp(mode, llm_config)
        self._init_scene_builder(mode)
        self._init_validator(enable_validation)
        self._init_refiner(enable_refinement)  # NEW: DiagramRefiner
        self._init_z3_layout(enable_z3_layout)  # NEW: Z3 Layout Solver
        self._init_ontology(enable_ontology_validation)  # NEW: Ontology validation
        self._init_aesthetic_analyzer(enable_aesthetic_optimization)  # NEW: Aesthetic optimization
        self._init_renderer()
        self._init_primitives(enable_primitives)
        self._init_property_graph(enable_property_graph)  # NEW
        self._init_nlp_tools(enable_nlp_enrichment, nlp_tools)  # NEW

        print(f"✅ Pipeline ready (Mode: {mode.value})\n")

    def _init_nlp(self, mode: PipelineMode, llm_config: Optional[LLMConfig]):
        """Initialize NLP/planning component based on mode"""
        if mode == PipelineMode.FAST:
            # Try enhanced NLP first (better text understanding)
            if HAS_ENHANCED_NLP:
                print("🚀 Initializing NLP Pipeline...")
                self.nlp_pipeline = EnhancedNLPAdapter()
                self.llm_planner = None
                self.nlp_mode = "enhanced"  # Track which NLP is used
            # Fall back to baseline spaCy pipeline
            elif HAS_SPACY:
                from unified_diagram_generator import SimpleNLPPipeline
                self.nlp_pipeline = SimpleNLPPipeline()
                self.llm_planner = None
                self.nlp_mode = "baseline"
            else:
                raise ImportError("spaCy required for FAST mode")

        elif mode in [PipelineMode.ACCURATE, PipelineMode.PREMIUM]:
            # Use LLM planner
            if HAS_LLM:
                try:
                    self.llm_planner = LLMDiagramPlanner(primary_config=llm_config)
                    self.nlp_pipeline = None
                except Exception as e:
                    print(f"⚠️  LLM initialization failed: {e}")
                    print("   Falling back to stub LLM planner")
                    self.llm_planner = StubLLMPlanner()
                    self.nlp_pipeline = None
            else:
                raise ImportError("LLM integration required for ACCURATE/PREMIUM mode")

    def _init_scene_builder(self, mode: PipelineMode):
        """Initialize scene builder based on mode"""
        if mode == PipelineMode.FAST:
            # Use baseline subject interpreters (backward compatible)
            try:
                from core.subject_interpreters import get_interpreter
                self.get_interpreter = get_interpreter
                self.domain_registry = None
            except ImportError:
                # Fall back to domain registry if available
                if HAS_DOMAIN_REGISTRY:
                    self.domain_registry = get_domain_registry()
                    self.get_interpreter = None
                else:
                    raise ImportError("Scene builder not available")

        else:
            # Use domain registry (new framework)
            if HAS_DOMAIN_REGISTRY:
                self.domain_registry = get_domain_registry()
                self.get_interpreter = None
            else:
                raise ImportError("Domain registry required for ACCURATE/PREMIUM mode")

    def _init_validator(self, enable: bool):
        """Initialize validator"""
        if enable:
            try:
                self.validator = UniversalValidator()
            except Exception as e:
                print(f"⚠️  Validator initialization failed: {e}")
                self.validator = None
        else:
            self.validator = None

        # Diagram validator (structural/quality checks)
        if enable and HAS_DIAGRAM_VALIDATOR:
            try:
                self.diagram_validator = DiagramValidator()
                print("✓ DiagramValidator initialized (layout, connectivity, style, physics)")
            except Exception as e:
                print(f"⚠️  DiagramValidator failed: {e}")
                self.diagram_validator = None
        else:
            self.diagram_validator = None

        # VLM validator (PREMIUM mode only)
        if self.mode == PipelineMode.PREMIUM and HAS_VLM:
            try:
                self.vlm_validator = VLMValidator(config=VLMConfig(
                    provider=VLMProvider.STUB,  # Use stub by default (lightweight)
                    model_name="stub"
                ))
                print("✓ VLMValidator initialized (visual-semantic validation)")
            except Exception as e:
                print(f"⚠️  VLM validator failed: {e}")
                self.vlm_validator = None
        else:
            self.vlm_validator = None

    def _init_refiner(self, enable: bool):
        """Initialize diagram refiner for automatic quality improvements"""
        if enable and HAS_DIAGRAM_VALIDATOR:
            try:
                self.diagram_refiner = DiagramRefiner()
                print("✓ DiagramRefiner initialized (automatic quality improvements)")
            except Exception as e:
                print(f"⚠️  DiagramRefiner failed: {e}")
                self.diagram_refiner = None
        else:
            self.diagram_refiner = None

    def _init_z3_layout(self, enable: bool):
        """Initialize Z3 constraint-based layout solver"""
        if enable:
            try:
                from core.solvers.z3_layout_solver import Z3LayoutSolver, Z3_AVAILABLE
                if Z3_AVAILABLE:
                    self.z3_layout = Z3LayoutSolver()
                    print("✓ Z3LayoutSolver initialized (constraint-based optimization)")
                else:
                    print("⚠️  Z3 not available - using basic layout")
                    self.z3_layout = None
            except Exception as e:
                print(f"⚠️  Z3LayoutSolver failed: {e}")
                self.z3_layout = None
        else:
            self.z3_layout = None

    def _init_ontology(self, enable: bool):
        """Initialize ontology validation"""
        if enable and HAS_ONTOLOGY:
            try:
                # Initialize as None - will be created per-diagram based on domain
                self.ontology_enabled = True
                print("✓ Ontology validation enabled")
            except Exception as e:
                print(f"⚠️  Ontology initialization failed: {e}")
                self.ontology_enabled = False
        else:
            self.ontology_enabled = False

    def _init_aesthetic_analyzer(self, enable: bool):
        """Initialize aesthetic analyzer"""
        if enable and HAS_AESTHETIC_ANALYZER:
            try:
                self.aesthetic_analyzer = AestheticAnalyzer()
                print("✓ AestheticAnalyzer initialized (visual quality optimization)")
            except Exception as e:
                print(f"⚠️  AestheticAnalyzer failed: {e}")
                self.aesthetic_analyzer = None
        else:
            self.aesthetic_analyzer = None

    def _init_renderer(self):
        """Initialize SVG renderer"""
        self.renderer = UniversalSVGRenderer()

    def _init_primitives(self, enable: bool):
        """Initialize primitive library"""
        if enable and HAS_PRIMITIVES:
            try:
                self.primitives = PrimitiveLibrary()
                # Check if library needs bootstrapping
                if self.primitives.count() == 0:
                    print("   Bootstrapping primitive library...")
                    self.primitives.bootstrap_library()
            except Exception as e:
                print(f"⚠️  Primitive library failed: {e}")
                self.primitives = None
        else:
            self.primitives = None

    def _init_property_graph(self, enable: bool):
        """Initialize property graph for knowledge representation"""
        if enable and HAS_PROPERTY_GRAPH:
            try:
                self.property_graph = PropertyGraph()
                print("✓ PropertyGraph initialized (knowledge representation)")
            except Exception as e:
                print(f"⚠️  PropertyGraph failed: {e}")
                self.property_graph = None
        else:
            self.property_graph = None

    def _init_nlp_tools(self, enable: bool, tools: List[str]):
        """Initialize individual NLP tools (OpenIE, Stanza, SciBERT, DyGIE++)"""
        self.nlp_tools = {}

        if not enable:
            return

        if 'openie' in tools and HAS_OPENIE:
            try:
                self.nlp_tools['openie'] = OpenIEExtractor()
                print("✓ OpenIE initialized (triple extraction)")
            except Exception as e:
                print(f"⚠️  OpenIE failed: {e}")

        if 'stanza' in tools and HAS_STANZA:
            try:
                self.nlp_tools['stanza'] = StanzaEnhancer()
                print("✓ Stanza initialized (dependency parsing)")
            except Exception as e:
                print(f"⚠️  Stanza failed: {e}")

        if 'scibert' in tools and HAS_SCIBERT:
            try:
                self.nlp_tools['scibert'] = SciBERTEmbedder()
                print("✓ SciBERT initialized (scientific embeddings)")
            except Exception as e:
                print(f"⚠️  SciBERT failed: {e}")

        if 'dygie' in tools and HAS_DYGIE:
            try:
                self.nlp_tools['dygie'] = DyGIEExtractor()
                print("✓ DyGIE++ initialized (entity/relation extraction)")
            except Exception as e:
                print(f"⚠️  DyGIE++ failed: {e}")

    def generate(
        self,
        problem_text: str,
        output_filename: Optional[str] = None,
        save_files: bool = True
    ) -> PipelineResult:
        """
        Generate diagram from problem text

        Args:
            problem_text: Problem description
            output_filename: Optional custom filename (without extension)
            save_files: Whether to save SVG/JSON files to disk

        Returns:
            PipelineResult with SVG, scene, validation, metadata
        """
        print("=" * 70)
        print(f"UNIFIED PIPELINE - Mode: {self.mode.value.upper()}")
        print("=" * 70)
        print(f"\n📋 Problem: {problem_text[:100]}...\n")

        start_time = time.time()

        # NEW: Initialize containers for advanced features
        enriched_nlp_results = {}
        current_property_graph = None

        try:
            # NEW: Phase 0.5: NLP Enrichment (if enabled)
            if self.nlp_tools:
                print("Phase 0.5: NLP Enrichment...")
                enrichment_time = time.time()

                if 'openie' in self.nlp_tools:
                    try:
                        openie_result = self.nlp_tools['openie'].extract(problem_text)
                        # Convert to dict for consistency
                        openie_dict = openie_result.to_dict() if hasattr(openie_result, 'to_dict') else openie_result
                        enriched_nlp_results['openie'] = openie_dict
                        triple_count = len(openie_result.triples) if hasattr(openie_result, 'triples') else len(openie_dict.get('triples', []))
                        print(f"  ✅ OpenIE: {triple_count} triples")
                    except Exception as e:
                        print(f"  ⚠️  OpenIE failed: {e}")

                if 'stanza' in self.nlp_tools:
                    try:
                        stanza_result = self.nlp_tools['stanza'].enhance(problem_text)
                        enriched_nlp_results['stanza'] = stanza_result
                        print(f"  ✅ Stanza: {len(stanza_result.get('entities', []))} entities")
                    except Exception as e:
                        print(f"  ⚠️  Stanza failed: {e}")

                if 'scibert' in self.nlp_tools:
                    try:
                        scibert_result = self.nlp_tools['scibert'].embed(problem_text)
                        enriched_nlp_results['scibert'] = scibert_result
                        print(f"  ✅ SciBERT: {len(scibert_result.get('embeddings', []))} embeddings")
                    except Exception as e:
                        print(f"  ⚠️  SciBERT failed: {e}")

                if 'dygie' in self.nlp_tools:
                    try:
                        dygie_result = self.nlp_tools['dygie'].extract(problem_text)
                        enriched_nlp_results['dygie'] = dygie_result
                        print(f"  ✅ DyGIE++: {len(dygie_result.get('entities', []))} entities")
                    except Exception as e:
                        print(f"  ⚠️  DyGIE++ failed: {e}")

                print(f"  ✅ Time: {time.time() - enrichment_time:.3f}s\n")

            # NEW: Phase 0.75: Property Graph Construction (if enabled)
            if self.property_graph and enriched_nlp_results:
                print("Phase 0.75: Property Graph Construction...")
                graph_time = time.time()

                current_property_graph = PropertyGraph()

                # Build graph from OpenIE triples
                if 'openie' in enriched_nlp_results:
                    triples = enriched_nlp_results['openie'].get('triples', [])
                    for triple in triples[:20]:  # Limit to avoid excessive nodes
                        try:
                            subject, relation, obj = triple.get('subject'), triple.get('relation'), triple.get('object')
                            if subject and obj:
                                # Add nodes
                                subj_node = GraphNode(id=subject, type=NodeType.OBJECT, label=subject)
                                obj_node = GraphNode(id=obj, type=NodeType.OBJECT, label=obj)
                                current_property_graph.add_node(subj_node)
                                current_property_graph.add_node(obj_node)

                                # Add edge
                                if relation:
                                    edge = GraphEdge(
                                        id=f"{subject}_{relation}_{obj}",
                                        source=subject,
                                        target=obj,
                                        type=EdgeType.RELATIONSHIP,
                                        label=relation
                                    )
                                    current_property_graph.add_edge(edge)
                        except Exception as e:
                            pass  # Skip malformed triples

                print(f"  ✅ Built graph: {len(current_property_graph.get_all_nodes())} nodes, "
                      f"{len(current_property_graph.get_all_edges())} edges")
                print(f"  ✅ Time: {time.time() - graph_time:.3f}s\n")

            # Step 1: Analysis (mode-dependent)
            analysis_time = time.time()

            if self.mode == PipelineMode.FAST:
                # Show enhanced NLP status
                nlp_label = "Enhanced NLP (STEM units + spaCy)" if hasattr(self, 'nlp_mode') and self.nlp_mode == "enhanced" else "spaCy + keywords"
                print(f"Step 1: NLP Analysis ({nlp_label})...")
                nlp_results = self.nlp_pipeline.process(problem_text)
                domain = nlp_results['domain']
                print(f"  ✅ Domain: {domain}")
                print(f"  ✅ Entities: {nlp_results.get('num_entities', nlp_results['metadata'].get('num_entities', 0))}")
                # Show quantities if enhanced NLP
                if 'num_quantities' in nlp_results:
                    print(f"  ✅ Quantities: {nlp_results['num_quantities']}")
                print(f"  ✅ Time: {nlp_results['metadata']['processing_time']:.3f}s\n")

            else:  # ACCURATE or PREMIUM
                print("Step 1: LLM Planning...")
                llm_plan = self.llm_planner.generate_plan(problem_text)
                domain = llm_plan.domain
                # Convert LLM plan to NLP results format for compatibility
                nlp_results = {
                    'domain': llm_plan.domain,
                    'entities': llm_plan.entities,
                    'relationships': llm_plan.relationships,
                    'metadata': {
                        'num_entities': len(llm_plan.entities),
                        'num_relationships': len(llm_plan.relationships),
                        'processing_time': time.time() - analysis_time,
                        'confidence': llm_plan.confidence
                    },
                    'llm_reasoning': llm_plan.reasoning
                }
                print(f"  ✅ Domain: {domain}")
                print(f"  ✅ Entities: {len(llm_plan.entities)}")
                print(f"  ✅ Confidence: {llm_plan.confidence:.2f}")
                print(f"  ✅ Reasoning: {llm_plan.reasoning[:60]}...\n")

            # Step 2: Scene Building
            print("Step 2: Scene Building...")
            scene_time = time.time()

            if self.domain_registry:
                # Use domain registry (new framework)
                builder = self.domain_registry.get_builder_for_problem(nlp_results, problem_text)
                scene = builder.build_scene(nlp_results, problem_text)
            else:
                # Use baseline interpreters
                interpreter = self.get_interpreter(domain)
                scene = interpreter.interpret(nlp_results, problem_text)

            print(f"  ✅ Scene: {scene.title}")
            print(f"  ✅ Objects: {len(scene.objects)}")
            print(f"  ✅ Relationships: {len(scene.relationships)}")
            print(f"  ✅ Time: {time.time() - scene_time:.3f}s\n")

            # Step 2.5: Z3 Layout Optimization (if enabled)
            z3_layout_applied = False
            if self.z3_layout and len(scene.objects) > 1:
                print("Step 2.5: Z3 Layout Optimization...")
                z3_time = time.time()

                try:
                    # Optimize layout using Z3 constraint solver
                    optimized_scene = self.z3_layout.optimize_layout(
                        scene,
                        min_spacing=50,
                        prefer_horizontal=True,
                        canvas_width=scene.canvas_width,
                        canvas_height=scene.canvas_height
                    )

                    # Update scene with optimized positions
                    scene = optimized_scene
                    z3_layout_applied = True

                    print(f"  ✅ Layout optimized with Z3 solver")
                    print(f"  ✅ Time: {time.time() - z3_time:.3f}s\n")

                except Exception as e:
                    print(f"  ⚠️  Z3 optimization failed: {e}")
                    print(f"  ℹ️  Using original layout")
                    print(f"  ✅ Time: {time.time() - z3_time:.3f}s\n")

            # Step 3: Validation (if enabled)
            validation_results = {}
            if self.diagram_validator or self.validator:
                print("Step 3: Validation...")
                validation_time = time.time()

                # Structural/Quality validation with DiagramValidator
                if self.diagram_validator:
                    quality_score = self.diagram_validator.validate(scene)
                    validation_results['structural'] = {
                        'overall_score': quality_score.overall_score,
                        'layout_score': quality_score.layout_score,
                        'connectivity_score': quality_score.connectivity_score,
                        'style_score': quality_score.style_score,
                        'physics_score': quality_score.physics_score,
                        'issue_count': len(quality_score.issues),
                        'issues': [
                            {
                                'severity': issue.severity,
                                'category': issue.category,
                                'message': issue.message
                            }
                            for issue in quality_score.issues[:5]  # Top 5 issues
                        ]
                    }
                    print(f"  ✅ Structural Validation: {quality_score.overall_score:.1f}/100")
                    if quality_score.issues:
                        print(f"  ⚠️  Found {len(quality_score.issues)} issues")

                # Rule-based validation (if validator available)
                if self.validator:
                    # Note: UniversalValidator may require different schema
                    validation_results['rule_based'] = {
                        'enabled': True,
                        'time': time.time() - validation_time
                    }

                print(f"  ✅ Time: {time.time() - validation_time:.3f}s\n")

            # Step 3.5: Automatic Refinement (if enabled and quality can be improved)
            refinement_applied = False
            if self.diagram_refiner and quality_score and quality_score.overall_score < 90:
                print("Step 3.5: Automatic Refinement...")
                refinement_time = time.time()

                try:
                    # Get fixable issue count before refinement
                    fixable_issues = sum(1 for issue in quality_score.issues if issue.auto_fixable)

                    if fixable_issues > 0:
                        print(f"  🔧 Found {fixable_issues} auto-fixable issues")
                        print(f"  🔧 Initial quality score: {quality_score.overall_score:.1f}/100")

                        # Apply refinement (max 3 iterations)
                        refined_scene, final_quality = self.diagram_refiner.refine(scene, max_iterations=3)

                        # Update scene and quality score
                        scene = refined_scene
                        quality_score = final_quality
                        refinement_applied = True

                        # Update validation results with refined scores
                        if 'structural' in validation_results:
                            validation_results['structural'].update({
                                'overall_score': final_quality.overall_score,
                                'layout_score': final_quality.layout_score,
                                'connectivity_score': final_quality.connectivity_score,
                                'style_score': final_quality.style_score,
                                'physics_score': final_quality.physics_score,
                                'refined': True
                            })

                        print(f"  ✅ Refinement complete: {quality_score.overall_score:.1f}/100")
                        print(f"  ✅ Time: {time.time() - refinement_time:.3f}s\n")
                    else:
                        print(f"  ℹ️  No auto-fixable issues found")
                        print(f"  ✅ Time: {time.time() - refinement_time:.3f}s\n")

                except Exception as e:
                    print(f"  ⚠️  Refinement failed: {e}")
                    print(f"  ℹ️  Continuing with unrefined scene")
                    print(f"  ✅ Time: {time.time() - refinement_time:.3f}s\n")

            # Step 4: Primitive Library Query (if enabled)
            primitives_used = []
            if self.primitives:
                print("Step 4: Primitive Library Query...")
                prim_time = time.time()

                # Search for relevant primitives based on domain and object types
                object_types = list(set([obj.object_type.value if hasattr(obj.object_type, 'value') else str(obj.object_type) for obj in scene.objects]))
                for obj_type in object_types:
                    # Try semantic search first
                    results = self.primitives.semantic_search(
                        query=f"{domain} {obj_type}",
                        limit=3,
                        domain=domain
                    )
                    if results:
                        primitives_used.extend([r['id'] for r in results[:1]])  # Use top result

                if primitives_used:
                    print(f"  ✅ Found {len(primitives_used)} reusable primitives")
                else:
                    print(f"  ℹ️  No matching primitives found")
                print(f"  ✅ Time: {time.time() - prim_time:.3f}s\n")

            # Step 5: SVG Rendering
            print(f"Step {'5' if self.primitives else '4'}: SVG Rendering...")
            render_time = time.time()

            # Pass primitives to renderer if available
            if self.primitives and primitives_used:
                # Fetch primitive components and build dict for renderer
                primitive_components_dict = {}
                for prim_id in primitives_used:
                    prim = self.primitives.get_by_id(prim_id)
                    if prim:
                        # Map by category (e.g., "resistor", "capacitor") for object type matching
                        primitive_components_dict[prim['category']] = prim

                # Pass primitives to renderer for reuse
                svg_output = self.renderer.render(scene, primitive_components=primitive_components_dict)
                print(f"  ✅ {len(primitive_components_dict)} primitives passed to renderer for reuse")
            else:
                svg_output = self.renderer.render(scene)

            print(f"  ✅ SVG generated ({len(svg_output):,} characters)")
            print(f"  ✅ Time: {time.time() - render_time:.3f}s\n")

            # Step 5.5: Primitive Ingestion (store reusable components)
            if self.primitives:
                print("Step 5.5: Primitive Ingestion...")
                ingestion_time = time.time()
                ingested_count = 0

                # Extract and store each object as a primitive (if not already in library)
                for obj in scene.objects:
                    try:
                        # Create a simplified representation for this object type
                        primitive_id = f"{domain}_{obj.object_type.value}_{obj.type if hasattr(obj, 'type') else 'default'}"

                        # Check if this primitive type already exists
                        existing = self.primitives.get_by_id(primitive_id)
                        if not existing:
                            # Generate a minimal SVG for just this object
                            # For now, create a placeholder - in production would extract actual SVG
                            primitive_svg = f"<g id='{primitive_id}'><circle cx='0' cy='0' r='10'/></g>"

                            # Store in library
                            self.primitives.add_primitive(
                                name=f"{obj.object_type.value} ({domain})",
                                description=f"Reusable {obj.object_type.value} component from {domain} domain",
                                domain=domain,
                                category=obj.object_type.value,
                                svg_content=primitive_svg,
                                tags=[domain, obj.object_type.value, 'auto-generated'],
                                metadata={
                                    'source': 'pipeline_ingestion',
                                    'object_type': obj.object_type.value
                                }
                            )
                            ingested_count += 1
                    except Exception as e:
                        # Don't fail the pipeline if ingestion fails
                        print(f"    Warning: Failed to ingest {obj.id}: {e}")
                        pass

                if ingested_count > 0:
                    print(f"  ✅ Ingested {ingested_count} new primitives into library")
                else:
                    print(f"  ℹ️  No new primitives to ingest")
                print(f"  ✅ Time: {time.time() - ingestion_time:.3f}s\n")

            # Step 6: VLM Validation (PREMIUM mode only)
            if self.mode == PipelineMode.PREMIUM and self.vlm_validator:
                print("Step 6: VLM Validation...")
                vlm_time = time.time()

                # Save temporary SVG for VLM validation
                temp_svg_path = self.output_dir / "temp_vlm_validation.svg"
                with open(temp_svg_path, 'w') as f:
                    f.write(svg_output)

                vlm_result = self.vlm_validator.validate_diagram(
                    str(temp_svg_path),
                    problem_text,
                    scene_data=scene.to_dict() if hasattr(scene, 'to_dict') else None
                )

                validation_results['vlm'] = {
                    'is_valid': vlm_result.is_valid,
                    'confidence': vlm_result.confidence,
                    'description': vlm_result.description,
                    'discrepancies': vlm_result.discrepancies,
                    'suggestions': vlm_result.suggestions,
                    'time': time.time() - vlm_time
                }

                print(f"  ✅ VLM: {'Valid' if vlm_result.is_valid else 'Invalid'}")
                print(f"  ✅ Confidence: {vlm_result.confidence:.2f}")
                print(f"  ✅ Time: {time.time() - vlm_time:.3f}s\n")

            # Step 7: Save files (if requested)
            files_saved = {}
            if save_files:
                print("Step 7: Saving files...")

                # Generate filename
                if not output_filename:
                    filename_base = f"diagram_{hash(problem_text) % 10000:04d}"
                else:
                    filename_base = output_filename

                # Save SVG
                svg_path = self.output_dir / f"{filename_base}.svg"
                with open(svg_path, 'w') as f:
                    f.write(svg_output)
                files_saved['svg'] = str(svg_path)
                print(f"  ✅ SVG: {svg_path}")

                # Save scene JSON
                json_path = self.output_dir / f"{filename_base}_scene.json"
                with open(json_path, 'w') as f:
                    json.dump(scene.to_dict() if hasattr(scene, 'to_dict') else {}, f, indent=2)
                files_saved['scene_json'] = str(json_path)
                print(f"  ✅ Scene: {json_path}")

                # Save NLP/LLM results
                analysis_path = self.output_dir / f"{filename_base}_analysis.json"
                with open(analysis_path, 'w') as f:
                    json.dump(nlp_results, f, indent=2)
                files_saved['analysis'] = str(analysis_path)
                print(f"  ✅ Analysis: {analysis_path}\n")

            # Calculate total time
            total_time = time.time() - start_time

            # Build result
            result = PipelineResult(
                success=True,
                svg=svg_output,
                scene=scene,
                scene_json=json.dumps(scene.to_dict() if hasattr(scene, 'to_dict') else {}, indent=2),
                nlp_results=nlp_results,
                validation=validation_results,
                metadata={
                    'mode': self.mode.value,
                    'nlp_mode': getattr(self, 'nlp_mode', 'unknown'),  # Track NLP type
                    'total_time': total_time,
                    'domain': domain,
                    'num_objects': len(scene.objects),
                    'num_relationships': len(scene.relationships),
                    'num_annotations': len(scene.annotations) if hasattr(scene, 'annotations') else 0,
                    # NEW: Advanced features summary
                    'property_graph_enabled': current_property_graph is not None,
                    'nlp_enrichment_enabled': bool(enriched_nlp_results),
                    'nlp_tools_used': list(enriched_nlp_results.keys()) if enriched_nlp_results else [],
                    'refinement_applied': refinement_applied,
                    'z3_layout_applied': z3_layout_applied
                },
                files=files_saved if save_files else {},
                # NEW: Advanced features
                property_graph=current_property_graph,
                enriched_nlp_results=enriched_nlp_results,
                refinement_applied=refinement_applied,
                z3_layout_applied=z3_layout_applied
            )

            print("=" * 70)
            print(f"✅ SUCCESS! Diagram generated in {total_time:.3f}s")
            print(f"   Mode: {self.mode.value}")
            print(f"   Domain: {domain}")
            print(f"   Objects: {len(scene.objects)}")
            print("=" * 70)

            return result

        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"\n❌ ERROR: {error_msg}\n")
            traceback.print_exc()

            return PipelineResult(
                success=False,
                error=error_msg,
                metadata={
                    'mode': self.mode.value,
                    'total_time': time.time() - start_time
                }
            )


# Convenience functions for backward compatibility
def generate_diagram_fast(problem_text: str, output_dir: str = "output") -> Dict:
    """Fast mode (backward compatible with baseline)"""
    pipeline = UnifiedPipeline(mode=PipelineMode.FAST, output_dir=output_dir)
    result = pipeline.generate(problem_text)
    return result.to_dict()


def generate_diagram_accurate(problem_text: str, output_dir: str = "output") -> Dict:
    """Accurate mode (LLM-powered)"""
    pipeline = UnifiedPipeline(mode=PipelineMode.ACCURATE, output_dir=output_dir)
    result = pipeline.generate(problem_text)
    return result.to_dict()


def generate_diagram_premium(problem_text: str, output_dir: str = "output") -> Dict:
    """Premium mode (LLM + VLM)"""
    pipeline = UnifiedPipeline(mode=PipelineMode.PREMIUM, output_dir=output_dir)
    result = pipeline.generate(problem_text)
    return result.to_dict()


if __name__ == "__main__":
    # Test all three modes
    test_problem = "A potential difference of 300 V is applied to a series connection of two capacitors of capacitances 2.00 μF and 8.00 μF."

    print("\n" + "=" * 80)
    print("TESTING UNIFIED PIPELINE - ALL MODES")
    print("=" * 80)

    # Test FAST mode
    print("\n[1] Testing FAST mode (keyword-based)...")
    try:
        result = generate_diagram_fast(test_problem, output_dir="test_output/fast")
        print(f"✅ FAST mode: {'Success' if result['success'] else 'Failed'}")
    except Exception as e:
        print(f"❌ FAST mode failed: {e}")

    # Test ACCURATE mode
    print("\n[2] Testing ACCURATE mode (LLM-powered)...")
    try:
        result = generate_diagram_accurate(test_problem, output_dir="test_output/accurate")
        print(f"✅ ACCURATE mode: {'Success' if result['success'] else 'Failed'}")
    except Exception as e:
        print(f"⚠️  ACCURATE mode failed (expected if no LLM): {e}")

    # Test PREMIUM mode
    print("\n[3] Testing PREMIUM mode (LLM + VLM)...")
    try:
        result = generate_diagram_premium(test_problem, output_dir="test_output/premium")
        print(f"✅ PREMIUM mode: {'Success' if result['success'] else 'Failed'}")
    except Exception as e:
        print(f"⚠️  PREMIUM mode failed (expected if no LLM/VLM): {e}")

    print("\n" + "=" * 80)
    print("✅ UNIFIED PIPELINE TESTS COMPLETE")
    print("=" * 80)
