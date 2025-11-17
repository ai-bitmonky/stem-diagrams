"""
Unified Diagram Pipeline - THE ONLY Entry Point
Single robust flow that handles ALL physics diagrams
NOW with offline capability, open-source NLP stack, property graphs, and advanced reasoning

OFFLINE CAPABLE - Can run without API key using local spaCy-based analyzer:
- With API key: Uses DeepSeek API for best quality (with local fallback)
- Without API key: Uses local spaCy + rule-based analyzer (100% offline)

This is the culmination of the unified architecture:
- Phase 0: Property Graph Construction (NEW)
- Phase 0.5: NLP Enrichment (OpenIE, Stanza, DyGIE++, SciBERT) (NEW)
- Phase 1: UniversalAIAnalyzer + Complexity Assessment (ENHANCED - OFFLINE CAPABLE)
- Phase 2: SceneGraphGenerator + Strategic Planning (ENHANCED)
- Phase 3: JSON Schema Validation + Ontology Validation (ENHANCED)
- Phase 4: UniversalValidator
- Phase 5: UniversalLayoutEngine + Z3 Optimization (ENHANCED)
- Phase 6: UniversalRenderer
- Phase 7: Post-validation (BidirectionalValidator + LLM Auditor) (ENHANCED)

Version: 4.1-offline (Open-Source NLP + Property Graph + Offline Mode)
Date: November 10, 2025
"""

import os
import json
import time
import logging
import copy
import uuid
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional, List, Any, Tuple
from pathlib import Path
import jsonschema

# Pipeline tracing and logging
from core.pipeline_tracer import PipelineTracer

# Original pipeline components
from core.universal_ai_analyzer import (
    UniversalAIAnalyzer,
    CanonicalProblemSpec,
    IncompleteSpecsError
)
from core.problem_spec import PhysicsDomain
from core.universal_scene_builder import (
    UniversalSceneBuilder,
    IncompleteSceneError
)
from core.universal_validator import (
    UniversalValidator,
    ValidationReport
)
from core.universal_layout_engine import UniversalLayoutEngine
from core.universal_renderer import UniversalRenderer
from core.scene.schema_v1 import Scene, PrimitiveType, Position
from core.domain_modules import DomainModuleRegistry
from core.validation.structural_validator import compare_plan_scene
from core.domain_rules import run_domain_rules

# NEW: Spatial validation and label placement (Phase 1 Architecture Fixes)
from core.spatial_validator import SpatialValidator, SpatialValidationReport
from core.label_placer import IntelligentLabelPlacer

# NEW: Pipeline logging for request/response tracing
from core.pipeline_logger import PipelineLogger, ConsoleProgressLogger

# NEW: Advanced pipeline components (with graceful degradation)
try:
    from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType
    PROPERTY_GRAPH_AVAILABLE = True
except ImportError:
    PROPERTY_GRAPH_AVAILABLE = False

try:
    from core.symbolic.sympy_geometry_verifier import SymPyGeometryVerifier
    SYMPY_VERIFIER_AVAILABLE = True
except ImportError:
    SYMPY_VERIFIER_AVAILABLE = False

try:
    from core.diagram_planner import DiagramPlanner, PlanningStrategy
    DIAGRAM_PLANNER_AVAILABLE = True
except ImportError:
    DIAGRAM_PLANNER_AVAILABLE = False

try:
    from core.model_orchestrator import ModelOrchestrator, ModelType
    MODEL_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    MODEL_ORCHESTRATOR_AVAILABLE = False

try:
    from core.nlp_tools.openie_extractor import OpenIEExtractor
    OPENIE_AVAILABLE = True
except ImportError:
    OPENIE_AVAILABLE = False

try:
    from core.nlp_tools.stanza_enhancer import StanzaEnhancer
    STANZA_AVAILABLE = True
except ImportError:
    STANZA_AVAILABLE = False

try:
    from core.nlp_tools.dygie_extractor import DyGIEExtractor
    DYGIE_AVAILABLE = True
except ImportError:
    DYGIE_AVAILABLE = False

try:
    from core.nlp_tools.scibert_embedder import SciBERTEmbedder
    SCIBERT_AVAILABLE = True
except ImportError:
    SCIBERT_AVAILABLE = False

try:
    from core.nlp_tools.chemdataextractor_parser import ChemDataExtractorParser
    CHEMDATAEXTRACTOR_AVAILABLE = True
except ImportError:
    CHEMDATAEXTRACTOR_AVAILABLE = False

try:
    from core.nlp_tools.mathbert_extractor import MathBERTExtractor
    MATHBERT_AVAILABLE = True
except ImportError:
    MATHBERT_AVAILABLE = False

try:
    from core.nlp_tools.amr_parser import AMRParser
    AMR_AVAILABLE = True
except ImportError:
    AMR_AVAILABLE = False

try:
    from core.ontology.ontology_manager import OntologyManager, Domain
    ONTOLOGY_AVAILABLE = True
except ImportError:
    ONTOLOGY_AVAILABLE = False

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from arango import ArangoClient
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False

try:
    from core.auditor.diagram_auditor import DiagramAuditor
    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False

try:
    from core.llm_planner import LLMDiagramPlanner
    LLM_PLANNER_AVAILABLE = True
except ImportError:
    LLM_PLANNER_AVAILABLE = False

try:
    from core.solvers.z3_layout_solver import Z3LayoutSolver
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

try:
    from core.validation_refinement import DiagramValidator, DiagramRefiner, QualityScore
    DIAGRAM_VALIDATOR_AVAILABLE = True
except ImportError:
    DIAGRAM_VALIDATOR_AVAILABLE = False

try:
    from core.vlm_validator import VLMValidator, VLMConfig, VLMProvider, VisualValidationResult
    VLM_VALIDATOR_AVAILABLE = True
except ImportError:
    VLM_VALIDATOR_AVAILABLE = False


@dataclass
class PipelineConfig:
    """Configuration for unified pipeline"""

    # API configuration (api_key is now OPTIONAL for offline mode)
    api_key: Optional[str] = None  # If None, uses local analyzer only (offline)
    api_base_url: str = "https://api.deepseek.com/v1/chat/completions"
    api_model: str = "deepseek-chat"
    api_timeout: int = 180
    use_local_fallback: bool = True  # Fallback to local analyzer if API fails

    # Canvas configuration
    canvas_width: int = 1200
    canvas_height: int = 800

    # Validation configuration
    validation_mode: str = "strict"  # strict, standard, permissive
    schema_path: str = "scene_graph_schema.json"

    # Paths
    domains_path: str = "domains"

    # Logging configuration
    enable_logging: bool = True
    log_level: str = "INFO"
    log_dir: str = "logs"
    output_dir: str = "output"

    # Feature flags - Original
    enable_ai_validation: bool = True  # VLM validation (Phase 9) [MANDATORY for roadmap compliance]
    enable_layout_optimization: bool = True
    enable_domain_embellishments: bool = True

    # Feature flags - NEW Advanced Features
    enable_property_graph: bool = True  # Phase 0: Property graph construction [MANDATORY]
    enable_nlp_enrichment: bool = True  # Phase 0.5: NLP tools (OpenIE, Stanza, etc.) [MANDATORY]
    enable_nlp_warmup: bool = True  # Preload NLP models at startup to eliminate cold start delay
    enable_complexity_assessment: bool = True  # Phase 1: Complexity scoring [MANDATORY]
    enable_strategic_planning: bool = True  # Phase 2: Strategy selection [MANDATORY]
    enable_ontology_validation: bool = True  # Phase 3: Semantic validation
    enable_z3_optimization: bool = True  # Phase 5: SMT-based layout [MANDATORY]
    enable_llm_auditing: bool = True  # Phase 10: LLM-based quality audit [MANDATORY]

    # NLP tool selection (when enable_nlp_enrichment=True)
    nlp_tools: List[str] = None  # Options: 'openie', 'stanza', 'dygie', 'scibert', 'chemdataextractor', 'mathbert', 'amr'

    # Model orchestration
    enable_model_orchestration: bool = True
    enable_model_orchestrator: bool = True  # Intelligent LLM routing  # Automatic model selection based on complexity

    # LLM auditor configuration
    auditor_backend: str = "mock"  # Options: 'claude', 'gpt', 'local', 'mock', 'deepseek'
    auditor_api_key: Optional[str] = None

    # LLM planner configuration
    enable_llm_planning: bool = True  # Phase 1-2: LLM-based diagram planning
    llm_planner_local_model: str = "mistral:7b"  # Ollama model for planning
    llm_planner_api_model: Optional[str] = None  # OpenAI model for planning/verification
    llm_planner_ollama_url: str = "http://localhost:11434"  # Ollama server URL

    # DeepSeek integration (Roadmap: 3 MANDATORY API calls)
    enable_deepseek_enrichment: bool = True  # Roadmap Call #1: Entity enrichment after NLP [MANDATORY]
    enable_deepseek_audit: bool = True  # Roadmap Call #2: Plan auditing (uses auditor_backend) [MANDATORY]
    enable_deepseek_validation: bool = True  # Roadmap Call #3: Semantic fidelity validation [MANDATORY]
    deepseek_api_key: Optional[str] = None  # DeepSeek API key (or set DEEPSEEK_API_KEY env var)
    deepseek_model: str = "deepseek-chat"  # Model name
    deepseek_base_url: str = "https://api.deepseek.com"  # API base URL

    # Primitive library (Roadmap Layer 5)
    enable_primitive_library: bool = True  # [ENABLED] Roadmap Layer 5: Query primitive library first
    primitive_library_backend: str = "memory"  # Options: 'milvus', 'qdrant', 'memory'
    primitive_library_host: str = "localhost:19530"  # Vector DB host

    # Additional solvers
    enable_sympy_solver: bool = False  # SymPy for symbolic physics
    enable_svg_optimization: bool = False  # svgo/scour post-processing
    enable_structural_validation: bool = True
    enable_domain_rule_validation: bool = True
    auto_refinement_max_iterations: int = 2
    auto_refinement_min_score: float = 0.85
    enable_domain_modules: bool = True  # Pluggable domain builders (SchemDraw, RDKit, etc.)

    # Property graph persistence
    property_graph_persist_to_disk: bool = True
    property_graph_dump_dir: str = "output/property_graphs"
    property_graph_graphdb_backend: Optional[str] = None  # 'neo4j' or 'arango'
    property_graph_graphdb_uri: Optional[str] = None
    property_graph_graphdb_username: Optional[str] = None
    property_graph_graphdb_password: Optional[str] = None
    property_graph_graphdb_database: Optional[str] = None
    property_graph_graphdb_collection: str = "diagram_property_graphs"

    def __post_init__(self):
        if self.nlp_tools is None:
            # Default: use all available tools
            self.nlp_tools = ['openie', 'stanza', 'dygie', 'scibert', 'chemdataextractor', 'mathbert', 'amr']


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

    # NEW: Advanced pipeline artifacts
    property_graph: Optional[Any] = None  # PropertyGraph instance
    nlp_results: Optional[Dict] = None  # Results from OpenIE, Stanza, etc.
    complexity_score: Optional[float] = None  # 0-1 complexity score
    selected_strategy: Optional[str] = None  # Planning strategy used
    llm_plan: Optional[Dict] = None  # LLM-generated diagram plan
    diagram_plan: Optional[Any] = None  # Property-graph-driven plan
    domain_module_outputs: Optional[List[Dict]] = None  # Domain-specific artifacts
    ontology_validation: Optional[Dict] = None  # Semantic validation results
    audit_report: Optional[Dict] = None  # LLM auditor results

    # Metadata
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def save_svg(self, output_path: str):
        """Save SVG to file"""
        with open(output_path, 'w') as f:
            f.write(self.svg)
        print(f"✅ Saved SVG to: {output_path}")

    def save_scene(self, output_path: str):
        """Save scene JSON to file"""
        import json
        scene_dict = {
            'version': self.scene.version,
            'metadata': self.scene.metadata,
            'coord_system': self.scene.coord_system,
            'objects': [
                {
                    'id': obj.id,
                    'type': obj.type.value,
                    'properties': obj.properties,
                    'position': obj.position,
                    'style': obj.style
                }
                for obj in self.scene.objects
            ],
            'constraints': [
                {
                    'type': c.type.value,
                    'objects': c.objects,
                    'value': c.value
                }
                for c in self.scene.constraints
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(scene_dict, f, indent=2)
        print(f"✅ Saved scene to: {output_path}")


class UnifiedDiagramPipeline:
    """
    THE ONLY entry point for physics diagram generation

    NOW with open-source NLP stack, property graphs, and advanced reasoning
    Single flow with optional advanced features
    Either returns perfect diagram OR fails with clear explanation

    NO silent failures, graceful degradation for optional features
    """

    _SUBSCRIPT_TRANSLATION = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    _UNIT_PREFIX_SCALES = {
        'P': 1e-12,
        'N': 1e-9,
        'U': 1e-6,
        'M': 1e-3,
        'K': 1e3,
        'G': 1e9
    }
    _UNIT_BASE_MAP = {
        'F': {'quantity': 'capacitance', 'component_hint': 'capacitor', 'unit': 'F'},
        'V': {'quantity': 'voltage', 'component_hint': 'battery', 'unit': 'V'},
        'A': {'quantity': 'current', 'component_hint': 'current_source', 'unit': 'A'},
        'OHM': {'quantity': 'resistance', 'component_hint': 'resistor', 'unit': 'Ω'},
        'H': {'quantity': 'inductance', 'component_hint': 'inductor', 'unit': 'H'},
        'C': {'quantity': 'charge', 'unit': 'C'},
        'N': {'quantity': 'force', 'unit': 'N'},
        'KG': {'quantity': 'mass', 'unit': 'kg'},
        'G': {'quantity': 'mass', 'unit': 'g'},
        'M': {'quantity': 'distance', 'unit': 'm'},
        'CM': {'quantity': 'distance', 'unit': 'cm'},
        'MM': {'quantity': 'distance', 'unit': 'mm'},
        'S': {'quantity': 'time', 'unit': 's'},
        'HZ': {'quantity': 'frequency', 'unit': 'Hz'},
        'J': {'quantity': 'energy', 'unit': 'J'},
        'W': {'quantity': 'power', 'unit': 'W'},
        'PA': {'quantity': 'pressure', 'unit': 'Pa'}
    }
    _QUANTITY_KEYWORDS = {
        'potential difference': {'quantity': 'voltage', 'component_hint': 'battery'},
        'voltage': {'quantity': 'voltage'},
        'charge': {'quantity': 'charge'},
        'force': {'quantity': 'force'},
        'mass': {'quantity': 'mass'},
        'distance': {'quantity': 'distance'},
        'separation': {'quantity': 'distance'},
        'speed': {'quantity': 'speed'},
        'velocity': {'quantity': 'speed'},
        'acceleration': {'quantity': 'acceleration'},
        'current': {'quantity': 'current'},
        'capacitance': {'quantity': 'capacitance', 'component_hint': 'capacitor'},
        'resistance': {'quantity': 'resistance', 'component_hint': 'resistor'},
        'electric field': {'quantity': 'electric_field'}
    }
    _TEXT_ASSIGNMENT_PATTERN = re.compile(
        r'(?P<symbol>[A-Za-z][A-Za-z0-9₀-₉]*)\s*=\s*(?P<value>[-+]?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-zΩωμµ]+)',
        re.IGNORECASE
    )
    _TEXT_QUANTITY_PATTERN = re.compile(
        r'(?P<label>[A-Za-z][A-Za-z\s-]{1,40}?)\s+of\s+(?P<value>[-+]?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-zΩωμµ]+)',
        re.IGNORECASE
    )

    def __init__(self, config: PipelineConfig):
        """
        Initialize Unified Diagram Pipeline

        Args:
            config: Pipeline configuration
        """
        self.config = config

        print("="*80)
        print("🚀 UNIFIED DIAGRAM PIPELINE v4.0 (Advanced + Open-Source NLP)")
        print("="*80)
        print()

        # Track which advanced features are active
        self.active_features = []
        self._nlp_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._nlp_cache_max_entries = 32  # simple LRU cache for NLP outputs
        self._request_counter = 0
        self._ontology_keyword_index = self._build_ontology_keyword_index()
        self.logger: Optional[PipelineLogger] = None
        self.progress: Optional[ConsoleProgressLogger] = None

        if getattr(self.config, 'property_graph_persist_to_disk', False):
            Path(self.config.property_graph_dump_dir).mkdir(parents=True, exist_ok=True)

        # Initialize all phases
        print("Initializing pipeline phases...\n")

        # Phase 1: AI Analysis (Original) - NOW supports offline mode
        self.ai_analyzer = UniversalAIAnalyzer(
            api_key=config.api_key,  # Can be None for offline mode
            api_base_url=config.api_base_url,
            api_model=config.api_model,
            timeout=config.api_timeout,
            use_local_fallback=config.use_local_fallback
        )
        print("✓ Phase 1: UniversalAIAnalyzer")

        # Phase 2: Scene Building (Original)
        self.scene_builder = UniversalSceneBuilder(
            domains_path=config.domains_path
        )
        print("✓ Phase 2: UniversalSceneBuilder")

        # Phase 4: Validation (Original)
        self.validator = UniversalValidator(
            mode=config.validation_mode,
            domains_path=config.domains_path
        )
        print("✓ Phase 4: UniversalValidator")

        # Phase 5: Layout (Original)
        self.layout_engine = UniversalLayoutEngine(
            width=config.canvas_width,
            height=config.canvas_height
        )
        print("✓ Phase 5: UniversalLayoutEngine")

        # Phase 6: Rendering (Original)
        self.renderer = UniversalRenderer(
            width=config.canvas_width,
            height=config.canvas_height,
            domains_path=config.domains_path
        )
        print("✓ Phase 6: UniversalRenderer")

        # NEW: Phase 5.5 - Spatial Validation (Architecture Fix)
        self.spatial_validator = SpatialValidator(
            canvas_width=config.canvas_width,
            canvas_height=config.canvas_height
        )
        self.active_features.append("Spatial Validation")
        print("✓ Phase 5.5: Spatial Validator [ACTIVE]")

        # NEW: Phase 5.6 - Intelligent Label Placement (Architecture Fix)
        self.label_placer = IntelligentLabelPlacer(
            canvas_width=config.canvas_width,
            canvas_height=config.canvas_height
        )
        self.active_features.append("Intelligent Label Placement")
        print("✓ Phase 5.6: Intelligent Label Placer [ACTIVE]")

        # NEW: Phase 0 - Property Graph
        self.property_graph = None
        if config.enable_property_graph and PROPERTY_GRAPH_AVAILABLE:
            self.property_graph = PropertyGraph()
            self.active_features.append("Property Graph")
            print("✓ Phase 0: PropertyGraph [ACTIVE]")
        elif config.enable_property_graph:
            print("⚠ Phase 0: PropertyGraph [REQUESTED BUT NOT AVAILABLE]")

        # NEW: Phase 0.5 - NLP Tools (with error handling)
        self.nlp_tools = {}
        if config.enable_nlp_enrichment:
            if 'openie' in config.nlp_tools and OPENIE_AVAILABLE:
                try:
                    self.nlp_tools['openie'] = OpenIEExtractor()
                    self.active_features.append("OpenIE")
                    print("✓ Phase 0.5: OpenIE [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: OpenIE [FAILED] - {type(e).__name__}")

            if 'stanza' in config.nlp_tools and STANZA_AVAILABLE:
                try:
                    self.nlp_tools['stanza'] = StanzaEnhancer()
                    self.active_features.append("Stanza")
                    print("✓ Phase 0.5: Stanza [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: Stanza [FAILED] - {type(e).__name__}: Model files required")

            if 'dygie' in config.nlp_tools and DYGIE_AVAILABLE:
                try:
                    self.nlp_tools['dygie'] = DyGIEExtractor()
                    self.active_features.append("DyGIE++")
                    print("✓ Phase 0.5: DyGIE++ [ACTIVE]")
                except Exception as e:
                    # DyGIE++ is optional - silently skip if not available
                    pass

            if 'scibert' in config.nlp_tools and SCIBERT_AVAILABLE:
                try:
                    self.nlp_tools['scibert'] = SciBERTEmbedder()
                    self.active_features.append("SciBERT")
                    print("✓ Phase 0.5: SciBERT [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: SciBERT [FAILED] - {type(e).__name__}: Model download required")

            if 'chemdataextractor' in config.nlp_tools and CHEMDATAEXTRACTOR_AVAILABLE:
                try:
                    self.nlp_tools['chemdataextractor'] = ChemDataExtractorParser()
                    self.active_features.append("ChemDataExtractor")
                    print("✓ Phase 0.5: ChemDataExtractor [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: ChemDataExtractor [FAILED] - {type(e).__name__}")

            if 'mathbert' in config.nlp_tools and MATHBERT_AVAILABLE:
                try:
                    self.nlp_tools['mathbert'] = MathBERTExtractor()
                    self.active_features.append("MathBERT")
                    print("✓ Phase 0.5: MathBERT [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: MathBERT [FAILED] - {type(e).__name__}")

            if 'amr' in config.nlp_tools and AMR_AVAILABLE:
                try:
                    self.nlp_tools['amr'] = AMRParser()
                    self.active_features.append("AMR Parser")
                    print("✓ Phase 0.5: AMR Parser [ACTIVE]")
                except Exception as e:
                    print(f"⚠ Phase 0.5: AMR Parser [FAILED] - {type(e).__name__}")

        # NEW: Diagram Planner (Complexity + Strategy)
        self.diagram_planner = None
        if config.enable_complexity_assessment or config.enable_strategic_planning:
            if DIAGRAM_PLANNER_AVAILABLE:
                self.diagram_planner = DiagramPlanner()
                self.active_features.append("Diagram Planner")
                print("✓ Phase 1+2: DiagramPlanner [ACTIVE]")
            else:
                print("⚠ Diagram Planner [REQUESTED BUT NOT AVAILABLE]")

        # NEW: LLM Planner (LLM-based planning)
        self.llm_planner = None
        if config.enable_llm_planning and LLM_PLANNER_AVAILABLE:
            self.llm_planner = LLMDiagramPlanner(
                local_model=config.llm_planner_local_model,
                api_model=config.llm_planner_api_model,
                ollama_base_url=config.llm_planner_ollama_url
            )
            self.active_features.append("LLM Planner")
            print("✓ Phase 1+2: LLM Diagram Planner [ACTIVE]")
        elif config.enable_llm_planning:
            print("⚠ LLM Planner [REQUESTED BUT NOT AVAILABLE]")

        # NEW: Model Orchestrator
        self.model_orchestrator = None
        if config.enable_model_orchestration and MODEL_ORCHESTRATOR_AVAILABLE:
            self.model_orchestrator = ModelOrchestrator()
            self.active_features.append("Model Orchestrator")
            print("✓ Model Orchestrator [ACTIVE]")

        # NEW: Primitive Library (Roadmap Layer 5) - MUST INITIALIZE BEFORE Domain Module Registry
        self.primitive_library = None
        try:
            from core.primitive_library import PrimitiveLibrary
            if self.config.enable_primitive_library:
                self.primitive_library = PrimitiveLibrary(
                    backend=self.config.primitive_library_backend,
                    host=self.config.primitive_library_host.split(':')[0]
                    if ':' in self.config.primitive_library_host else self.config.primitive_library_host,
                    port=int(self.config.primitive_library_host.split(':')[1])
                    if ':' in self.config.primitive_library_host else 19530
                )
                stats = self.primitive_library.get_stats()
                self.active_features.append(f"Primitive Library ({stats['backend']})")
                print(f"✓ Primitive Library: {stats['backend']} backend with {stats.get('total_primitives', 0)} primitives [ACTIVE]")
            else:
                self.primitive_library = PrimitiveLibrary(backend="memory")
                stats = self.primitive_library.get_stats()
                print(f"✓ Primitive Library: memory backend with {stats.get('total_primitives', 0)} primitives [ACTIVE]")
        except Exception as exc:
            print(f"⚠️  Primitive Library initialization failed: {exc}")
            self.primitive_library = None

        # NEW: Domain Module Registry - Load domain-specific builders (SchemDraw, RDKit, etc.)
        self.domain_module_registry = None
        if self.config.enable_domain_modules:  # FIXED: Use config directly instead of getattr with False default
            try:
                print("⏳ Loading domain-specific builders (SchemDraw, PySketcher, RDKit, Cytoscape)...", flush=True)
                self.domain_module_registry = DomainModuleRegistry(
                    primitive_library=self.primitive_library,
                    auto_register=True  # Auto-load all available domain modules
                )
                registered_modules = self.domain_module_registry.list_modules()
                self.active_features.append(f"Domain Modules ({len(registered_modules)})")
                print(f"✓ Domain Module Registry [ACTIVE - {len(registered_modules)} modules loaded]")
            except Exception as exc:
                print(f"⚠️  Domain Module Registry initialization failed: {exc}")

        # NEW: Ontology Manager
        self.ontology_manager = None
        if config.enable_ontology_validation and ONTOLOGY_AVAILABLE:
            # Will be initialized per-problem based on domain
            self.active_features.append("Ontology Validation")
            print("✓ Phase 3: Ontology Validation [ACTIVE]")

        # NEW: Z3 Layout Solver
        self.z3_solver = None
        if config.enable_z3_optimization and Z3_AVAILABLE:
            self.z3_solver = Z3LayoutSolver()
            self.active_features.append("Z3 Optimization")
            print("✓ Phase 5: Z3 Layout Solver [ACTIVE]")

        # NEW: LLM Auditor
        self.auditor = None
        if config.enable_llm_auditing and AUDITOR_AVAILABLE:
            self.auditor = DiagramAuditor(
                backend=config.auditor_backend,
                api_key=config.auditor_api_key
            )
            self.active_features.append("LLM Auditor")
            print("✓ Phase 7: LLM Auditor [ACTIVE]")

        # NEW: Diagram Validator (structural/quality)
        self.diagram_validator = None
        if DIAGRAM_VALIDATOR_AVAILABLE:
            self.diagram_validator = DiagramValidator()
            self.active_features.append("Structural Validator")
            print("✓ Phase 7: DiagramValidator [ACTIVE]")

        # NEW: VLM Validator (visual-semantic) - Try BLIP-2, fallback to STUB
        self.vlm_validator = None
        if self.config.enable_ai_validation and VLM_VALIDATOR_AVAILABLE:
            # Try to load BLIP-2 first (best option for local validation)
            try:
                print("⏳ Initializing VLM Validator with BLIP-2...", flush=True)
                self.vlm_validator = VLMValidator(config=VLMConfig(
                    provider=VLMProvider.BLIP2,
                    model_name="Salesforce/blip2-opt-2.7b",
                    device="cpu"  # Use CPU for compatibility (can be changed to "cuda" if GPU available)
                ))
                self.active_features.append("VLM Validator (BLIP-2)")
                print("✓ Phase 7: VLMValidator [ACTIVE - BLIP-2]")
            except Exception as e:
                # BLIP-2 failed, try GPT-4 Vision if API key available
                if hasattr(self.config, 'api_key') and self.config.api_key:
                    try:
                        print("⚠️  BLIP-2 failed, trying GPT-4 Vision...", flush=True)
                        self.vlm_validator = VLMValidator(config=VLMConfig(
                            provider=VLMProvider.GPT4_VISION,
                            model_name="gpt-4-vision-preview",
                            api_key=self.config.api_key
                        ))
                        self.active_features.append("VLM Validator (GPT-4V)")
                        print("✓ Phase 7: VLMValidator [ACTIVE - GPT-4V]")
                    except Exception as e2:
                        print(f"⚠️  GPT-4V failed: {e2}")
                        print("   Falling back to STUB mode")
                        self.vlm_validator = VLMValidator(config=VLMConfig(
                            provider=VLMProvider.STUB,
                            model_name="stub"
                        ))
                        self.active_features.append("VLM Validator (STUB)")
                        print("✓ Phase 7: VLMValidator [ACTIVE - STUB MODE]")
                else:
                    # No API key, fallback to STUB
                    print(f"⚠️  BLIP-2 initialization failed: {e}")
                    print("   Falling back to STUB mode (install transformers & torch for BLIP-2)")
                    self.vlm_validator = VLMValidator(config=VLMConfig(
                        provider=VLMProvider.STUB,
                        model_name="stub"
                    ))
                    self.active_features.append("VLM Validator (STUB)")
                    print("✓ Phase 7: VLMValidator [ACTIVE - STUB MODE]")

        # NEW: DeepSeek Client (Roadmap: 3 API calls)
        self.deepseek_client = None
        if (self.config.enable_deepseek_enrichment or
                self.config.enable_deepseek_audit or
                self.config.enable_deepseek_validation):
            try:
                from core.deepseek_llm_adapter import DeepSeekClient
                self.deepseek_client = DeepSeekClient(
                    api_key=self.config.deepseek_api_key,
                    base_url=self.config.deepseek_base_url,
                    model=self.config.deepseek_model
                )
                features = []
                if self.config.enable_deepseek_enrichment:
                    features.append("Enrichment")
                if self.config.enable_deepseek_audit:
                    features.append("Audit")
                if self.config.enable_deepseek_validation:
                    features.append("Validation")
                self.active_features.append(f"DeepSeek ({', '.join(features)})")
                print(f"✓ DeepSeek API: {', '.join(features)} [ACTIVE]")
            except Exception as exc:
                print(f"⚠️  DeepSeek initialization failed: {exc}")
                self.deepseek_client = None

        # Initialize logger if enabled
        if config.enable_logging:
            self.logger = PipelineLogger(
                log_dir=config.log_dir,
                log_level=config.log_level
            )
            self.progress = ConsoleProgressLogger()
            self.active_features.append("Request/Response Logging")
            print("✓ Pipeline Logger [ACTIVE]")
        else:
            self.logger = None
            self.progress = None

        print()
        print("=" * 80)
        print("✅ UNIFIED PIPELINE INITIALIZED")
        if self.active_features:
            print(f"   Advanced Features: {', '.join(self.active_features)}", flush=True)
        print("=" * 80)
        print()

        # Warmup NLP models at startup to avoid cold start on first request
        if self.nlp_tools and config.enable_nlp_warmup:
            self._warmup_nlp_models()

    def _warmup_nlp_models(self):
        """
        Warmup NLP models by running dummy inference to force lazy loading.
        This eliminates the 160+ second cold start on first request.

        Called during server startup if config.enable_nlp_warmup is True.
        """
        if not self.nlp_tools:
            return

        print()
        print("=" * 80, flush=True)
        print("⏳ WARMING UP NLP MODELS (First-time model loading ~2-3 minutes)", flush=True)
        print("=" * 80, flush=True)
        print()

        dummy_text = "A simple circuit with a battery and resistor."
        start_warmup = time.time()
        warmup_times = {}

        for tool_name, tool in self.nlp_tools.items():
            try:
                print(f"  🔄 Preloading {tool_name}...", flush=True)
                start_tool = time.time()

                # Force model loading by running inference with dummy text
                if tool_name == 'openie' and hasattr(tool, 'extract'):
                    tool.extract(dummy_text)
                elif tool_name == 'stanza' and hasattr(tool, 'analyze'):
                    tool.analyze(dummy_text)
                elif tool_name == 'scibert' and hasattr(tool, 'embed'):
                    tool.embed(dummy_text)
                elif tool_name == 'chemdataextractor' and hasattr(tool, 'parse'):
                    tool.parse(dummy_text)
                elif tool_name == 'mathbert' and hasattr(tool, 'extract'):
                    # MathBERT is the slowest - takes 160+ seconds on first load
                    print(f"     ⏱️  MathBERT initialization takes 2-3 minutes (loading transformer weights)...", flush=True)
                    tool.extract(dummy_text)
                elif tool_name == 'amr' and hasattr(tool, 'parse'):
                    # AMR can also be slow on first load
                    print(f"     ⏱️  AMR Parser initialization may take 1-2 minutes...", flush=True)
                    tool.parse(dummy_text)
                elif tool_name == 'dygie' and hasattr(tool, 'extract'):
                    tool.extract(dummy_text)
                else:
                    print(f"     ⚠️  Unknown tool interface for {tool_name}", flush=True)
                    continue

                elapsed = time.time() - start_tool
                warmup_times[tool_name] = elapsed
                print(f"  ✅ {tool_name} ready ({elapsed:.1f}s)", flush=True)

            except Exception as e:
                elapsed = time.time() - start_tool
                warmup_times[tool_name] = elapsed
                print(f"  ⚠️  {tool_name} warmup failed after {elapsed:.1f}s: {type(e).__name__}", flush=True)

        total_elapsed = time.time() - start_warmup
        print()
        print("=" * 80, flush=True)
        print(f"✅ NLP MODELS WARMED UP ({total_elapsed:.1f}s total)", flush=True)
        print("=" * 80, flush=True)
        print()
        print("Warmup timing breakdown:", flush=True)
        for tool_name, elapsed in sorted(warmup_times.items(), key=lambda x: x[1], reverse=True):
            percentage = (elapsed / total_elapsed * 100) if total_elapsed > 0 else 0
            print(f"  - {tool_name}: {elapsed:.1f}s ({percentage:.1f}%)", flush=True)
        print()
        print("=" * 80, flush=True)
        print()

        # Internal: simple per-request NLP cache helpers

    def _make_nlp_cache_key(self, text: str) -> str:
        """Create cache key from text + active tools"""
        if not text:
            return ""
        tool_names = ",".join(sorted(self.nlp_tools.keys())) if self.nlp_tools else "none"
        return f"{hash(text)}::{tool_names}"

    def _get_cached_nlp_results(self, cache_key: Optional[str]) -> Optional[Dict[str, Any]]:
        """Return a deep copy of cached NLP results if available"""
        if not cache_key or cache_key not in self._nlp_cache:
            return None
        cached_value = copy.deepcopy(self._nlp_cache[cache_key])
        # refresh LRU order
        self._nlp_cache.move_to_end(cache_key)
        for value in cached_value.values():
            value['cached'] = True
        return cached_value

    def _store_nlp_results_in_cache(self, cache_key: Optional[str], results: Dict[str, Any]) -> None:
        """Store NLP results in cache with LRU eviction"""
        if not cache_key or not results:
            return
        snapshot = copy.deepcopy(results)
        self._nlp_cache[cache_key] = snapshot
        self._nlp_cache.move_to_end(cache_key)
        while len(self._nlp_cache) > self._nlp_cache_max_entries:
            self._nlp_cache.popitem(last=False)

    def generate(self, problem_text: str) -> DiagramResult:
        """
        Generate physics diagram from problem text

        This is THE ONLY method for diagram generation.
        NOW with advanced features integrated into the flow:

        0. NLP ENRICHMENT (OpenIE, Stanza, DyGIE++, SciBERT) [NEW]
        0.5. PROPERTY GRAPH CONSTRUCTION [NEW]
        1. PROBLEM UNDERSTANDING (UniversalAIAnalyzer) + COMPLEXITY ASSESSMENT [NEW]
        2. SCENE GRAPH GENERATION (SceneGraphGenerator) + STRATEGIC PLANNING [NEW]
        3. SCHEMA VALIDATION (jsonschema) + ONTOLOGY VALIDATION [NEW]
        4. PHYSICS VALIDATION (UniversalValidator)
        5. LAYOUT OPTIMIZATION (UniversalLayoutEngine) + Z3 OPTIMIZATION [NEW]
        6. RENDERING (UniversalRenderer)
        7. POST-VALIDATION + LLM AUDITING [NEW]

        Args:
            problem_text: Physics problem description

        Returns:
            DiagramResult with SVG and all artifacts including advanced features

        Raises:
            IncompleteSpecsError: If AI cannot extract complete specs
            jsonschema.ValidationError: If the generated scene graph is invalid
        """

        # Log initial request
        if self.logger:
            self.logger.log_request(problem_text, {
                'canvas_width': self.config.canvas_width,
                'canvas_height': self.config.canvas_height,
                'validation_mode': self.config.validation_mode,
                'active_features': self.active_features
            })

        trace = {
            'pipeline_version': '4.0-advanced',
            'stages': [],
            'active_features': self.active_features
        }

        request_id = self._next_request_id()
        trace['request_id'] = request_id

        # Initialize comprehensive pipeline tracer
        tracer = PipelineTracer(request_id=request_id, output_dir="logs")

        # Track advanced pipeline results
        nlp_results = {}
        complexity_score = None
        selected_strategy = None
        ontology_validation = None
        audit_report = None
        domain_module_outputs: List[Dict[str, Any]] = []
        structural_report = None
        domain_rule_report = None
        vlm_description = None
        current_property_graph = None

        print("\n")
        print("╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "    UNIFIED DIAGRAM GENERATION - V4.0 (ADVANCED)".center(78) + "║")
        print("║" + "    REQUEST ID: {:<60}".format(request_id) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝")
        print()

        domain = None
        try:
            # Phase 0: NLP Enrichment (NEW)
            nlp_cache_key = self._make_nlp_cache_key(problem_text) if self.nlp_tools else None
            cached_nlp = self._get_cached_nlp_results(nlp_cache_key) if self.nlp_tools else None

            if self.nlp_tools:
                stage_start_time = time.time()

                # Start tracer for NLP phase
                tracer.start_component("NLP Enrichment", "Phase 0", {
                    'tools': list(self.nlp_tools.keys()),
                    'problem_length': len(problem_text)
                })
                tracer.log_input(problem_text, "problem_text")

                if self.logger:
                    self.logger.start_phase("NLP Enrichment", 0, "Extract entities, relations, and scientific concepts")
                    self.logger.log_phase_input(problem_text, f"Problem text ({len(problem_text)} chars)")
                if self.progress:
                    self.progress.start_phase("NLP Enrichment", 0)
                print("┌─ PHASE 0: NLP ENRICHMENT ─────────────────────────────────────┐")

                if cached_nlp:
                    nlp_results = cached_nlp
                    print(f"  ♻️  Using cached NLP outputs from {len(nlp_results)} tools", flush=True)
                else:
                    # Log text complexity metrics
                    text_length = len(problem_text)
                    formula_chars = sum(1 for c in problem_text if c in 'μ₁₂₃₄₅₆₇₈₉₀×÷±√∫∑∏')
                    special_chars = sum(1 for c in problem_text if not c.isalnum() and not c.isspace())
                    print(f"  📊 Text Complexity: {text_length} chars, {formula_chars} formula chars, {special_chars} special chars", flush=True)
                    

                    # Run each NLP tool with error handling to prevent hangs
                    if 'openie' in self.nlp_tools:
                        print("  🔄 OpenIE: Starting extraction...", flush=True)
                        start_tool = time.time()
                        try:
                            openie_result = self.nlp_tools['openie'].extract(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['openie'] = {
                                'provenance': 'openie',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'triples': [(t.subject, t.relation, t.object) for t in openie_result.triples],  # FIXED: Store ALL triples
                                'raw_result': openie_result  # ADDED: Store full result object
                            }
                            print(f"  ✅ OpenIE: Extracted {len(openie_result.triples)} triples in {elapsed:.0f}ms", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  OpenIE: Failed after {elapsed:.0f}ms - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'stanza' in self.nlp_tools:
                        print("  🔄 Stanza: Starting NLP analysis...", flush=True)
                        start_tool = time.time()
                        try:
                            stanza_result = self.nlp_tools['stanza'].analyze(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['stanza'] = {
                                'provenance': 'stanza',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'entities': stanza_result.get('entities', []),  # FIXED: Store ALL entities
                                'dependencies': stanza_result.get('dependencies', []),  # ADDED: Store dependency relations
                                'raw_result': stanza_result  # ADDED: Store full result
                            }
                            entity_count = len(stanza_result.get('entities', []))
                            dep_count = len(stanza_result.get('dependencies', []))
                            print(f"  ✅ Stanza: Found {entity_count} entities, {dep_count} dependencies in {elapsed:.0f}ms", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  Stanza: Failed after {elapsed:.0f}ms - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'scibert' in self.nlp_tools:
                        print("  🔄 SciBERT: Starting embedding generation...", flush=True)
                        start_tool = time.time()
                        try:
                            scibert_result = self.nlp_tools['scibert'].embed(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            embedding_dim = len(scibert_result[0]) if isinstance(scibert_result, list) and scibert_result else (
                                len(scibert_result) if hasattr(scibert_result, '__len__') else 0
                            )
                            embedding_sample = None
                            try:
                                if hasattr(scibert_result, 'tolist'):
                                    vector = scibert_result.tolist()
                                    embedding_sample = vector[:10] if isinstance(vector, list) else None
                                elif isinstance(scibert_result, list):
                                    embedding_sample = scibert_result[0][:10] if scibert_result and hasattr(scibert_result[0], '__getitem__') else None
                            except Exception:
                                embedding_sample = None
                            nlp_results['scibert'] = {
                                'provenance': 'scibert',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'embedding_dim': embedding_dim,
                                'embedding_sample': embedding_sample
                            }
                            print(f"  ✅ SciBERT: Generated embeddings (dim={embedding_dim}) in {elapsed:.0f}ms", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  SciBERT: Failed after {elapsed:.0f}ms - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'chemdataextractor' in self.nlp_tools:
                        print("  🔄 ChemDataExtractor: Starting chemical entity extraction...", flush=True)
                        start_tool = time.time()
                        try:
                            chem_result = self.nlp_tools['chemdataextractor'].parse(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['chemdataextractor'] = {
                                'provenance': 'chemdataextractor',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'formulas': chem_result.formulas[:5],
                                'reactions': len(chem_result.reactions),
                                'properties': list(chem_result.properties.keys())[:5]
                            }
                            print(f"  ✅ ChemDataExtractor: Found {len(chem_result.formulas)} formulas, {len(chem_result.reactions)} reactions in {elapsed:.0f}ms", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  ChemDataExtractor: Failed after {elapsed:.0f}ms - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'mathbert' in self.nlp_tools:
                        print("  🔄 MathBERT: Starting mathematical expression extraction...", flush=True)
                        print("     ⏱️  Note: MathBERT can take 60-180+ seconds for complex text with formulas", flush=True)
                        start_tool = time.time()
                        try:
                            math_result = self.nlp_tools['mathbert'].extract(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['mathbert'] = {
                                'provenance': 'mathbert',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'variables': list(math_result.variables)[:10],
                                'expressions': len(math_result.expressions),
                                'constants': dict(list(math_result.constants.items())[:5])
                            }
                            print(f"  ✅ MathBERT: Found {len(math_result.variables)} variables, {len(math_result.expressions)} expressions in {elapsed:.0f}ms ({elapsed/1000:.1f}s)", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  MathBERT: Failed after {elapsed:.0f}ms ({elapsed/1000:.1f}s) - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'amr' in self.nlp_tools:
                        print("  🔄 AMR Parser: Starting Abstract Meaning Representation parsing...", flush=True)
                        print("     ⏱️  Note: AMR Parser can take 60-120+ seconds for complex dependency graphs", flush=True)
                        start_tool = time.time()
                        try:
                            amr_result = self.nlp_tools['amr'].parse(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['amr'] = {
                                'provenance': 'amr',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'concepts': list(amr_result.concepts)[:10],
                                'entities': dict(list(amr_result.entities.items())[:5]),
                                'relations': amr_result.relations[:5]
                            }
                            print(f"  ✅ AMR: Extracted {len(amr_result.concepts)} concepts, {len(amr_result.relations)} relations in {elapsed:.0f}ms ({elapsed/1000:.1f}s)", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  AMR: Failed after {elapsed:.0f}ms ({elapsed/1000:.1f}s) - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    if 'dygie' in self.nlp_tools:
                        print("  🔄 DyGIE++: Starting entity and relation extraction...", flush=True)
                        start_tool = time.time()
                        try:
                            dygie_result = self.nlp_tools['dygie'].extract(problem_text)
                            elapsed = (time.time() - start_tool) * 1000
                            nlp_results['dygie'] = {
                                'provenance': 'dygie',
                                'runtime_ms': elapsed,
                                'cached': False,
                                'entities': dygie_result.entities,  # FIXED: Store ALL entities
                                'relations': dygie_result.relations,  # FIXED: Store ALL relations
                                'raw_result': dygie_result  # ADDED: Store full result object
                            }
                            print(f"  ✅ DyGIE++: Extracted {len(dygie_result.entities)} entities, {len(dygie_result.relations)} relations in {elapsed:.0f}ms", flush=True)
                        except Exception as e:
                            elapsed = (time.time() - start_tool) * 1000
                            print(f"  ⚠️  DyGIE++: Failed after {elapsed:.0f}ms - {type(e).__name__}: {str(e)[:50]}", flush=True)

                    # Cache for future identical prompts
                    self._store_nlp_results_in_cache(nlp_cache_key, nlp_results)

                    # Log summary of NLP enrichment with timing breakdown
                    total_nlp_time = sum(result.get('runtime_ms', 0) for result in nlp_results.values())
                    print()
                    print("  📊 NLP Enrichment Summary:", flush=True)
                    print(f"     Total time: {total_nlp_time:.0f}ms ({total_nlp_time/1000:.1f}s)", flush=True)
                    print(f"     Tools executed: {len(nlp_results)}", flush=True)
                    if nlp_results:
                        print(f"     Timing breakdown:", flush=True)
                        for tool_name, result in sorted(nlp_results.items(), key=lambda x: x[1].get('runtime_ms', 0), reverse=True):
                            tool_time = result.get('runtime_ms', 0)
                            percentage = (tool_time / total_nlp_time * 100) if total_nlp_time > 0 else 0
                            print(f"       - {tool_name}: {tool_time:.0f}ms ({percentage:.1f}%)", flush=True)

                print("└───────────────────────────────────────────────────────────────┘\n")

                # Complete tracer for NLP phase
                tracer.log_output(nlp_results, "nlp_results")
                tracer.log_transformation("NLP Extraction", {
                    'tools_used': list(nlp_results.keys()),
                    'total_time_ms': total_nlp_time,
                    'cached': cached_nlp is not None
                })
                tracer.complete_component()

                if self.logger:
                    self.logger.log_phase_output(nlp_results, f"Extracted data using {len(nlp_results)} NLP tools")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'NLP Enrichment',
                    'duration': time.time() - stage_start_time,
                    'output': {'tools_used': list(nlp_results.keys())}
                })

            # Phase 0.5: Property Graph Construction (ENHANCED - Multi-source integration)
            if self.property_graph is not None:
                stage_start_time = time.time()

                # Start tracer for Property Graph phase
                tracer.start_component("Property Graph Construction", "Phase 0.5", {
                    'nlp_tools_used': list(nlp_results.keys()) if nlp_results else []
                })
                tracer.log_input(nlp_results, "nlp_results")

                if self.logger:
                    self.logger.start_phase("Property Graph Construction", 1, "Build knowledge graph from NLP results")
                    self.logger.log_phase_input(nlp_results, "NLP extraction results")
                if self.progress:
                    self.progress.start_phase("Property Graph", 1)
                print("┌─ PHASE 0.5: PROPERTY GRAPH CONSTRUCTION (Multi-source) ───────┐")

                # ✅ FIX 1: Use self.property_graph (instance variable) instead of local variable
                # Reset property graph for this problem
                self.property_graph = PropertyGraph()

                # Counter for tracking sources
                sources_used = []

                # Source 0: Direct text parsing for canonical quantities/components
                text_measurements = self._extract_quantities_from_text(problem_text)
                if text_measurements:
                    sources_used.append('text_pattern')
                    for measurement in text_measurements:
                        quantity_id = measurement['quantity_id']
                        text_metadata = {
                            'sources': ['text_pattern'],
                            'raw_text': measurement['raw_text'],
                            'confidence': measurement.get('confidence', 0.95)
                        }

                        if not self.property_graph.has_node(quantity_id):
                            quantity_node = GraphNode(
                                id=quantity_id,
                                type=NodeType.QUANTITY,
                                label=measurement['quantity_label'],
                                properties={
                                    'quantity_type': measurement['quantity_type'],
                                    'value': measurement['value'],
                                    'value_si': measurement['value_si'],
                                    'unit': measurement['unit_display'],
                                    'unit_base': measurement.get('unit_base'),
                                    'symbol': measurement.get('symbol')
                                },
                                metadata=text_metadata
                            )
                            self.property_graph.add_node(quantity_node)

                        component_id = measurement.get('component_id')
                        if component_id:
                            if not self.property_graph.has_node(component_id):
                                component_node = GraphNode(
                                    id=component_id,
                                    type=NodeType.COMPONENT,
                                    label=measurement['component_label'],
                                    properties={
                                        'component_type': measurement['component_type'],
                                        'symbol': measurement.get('symbol')
                                    },
                                    metadata=text_metadata
                                )
                                self.property_graph.add_node(component_node)

                            self.property_graph.add_edge(GraphEdge(
                                source=component_id,
                                target=quantity_id,
                                type=EdgeType.HAS_VALUE,
                                label=f"{measurement['quantity_type']} value",
                                metadata={'source': 'text_pattern'},
                                properties={'unit': measurement['unit_display'], 'raw': measurement['raw_text']}
                            ))

                        unit_base = measurement.get('unit_base')
                        if unit_base:
                            unit_node_id = f"unit_{unit_base.lower()}"
                            if not self.property_graph.has_node(unit_node_id):
                                unit_node = GraphNode(
                                    id=unit_node_id,
                                    type=NodeType.CONCEPT,
                                    label=unit_base,
                                    properties={'unit': unit_base},
                                    metadata={'sources': ['text_pattern']}
                                )
                                self.property_graph.add_node(unit_node)

                            self.property_graph.add_edge(GraphEdge(
                                source=quantity_id,
                                target=unit_node_id,
                                type=EdgeType.HAS_UNIT,
                                label='has_unit',
                                metadata={'source': 'text_pattern'}
                            ))

                # ✅ FIX 2: Integrate ALL NLP tool outputs (not just OpenIE)

                # Source 1: OpenIE - Extract subject-relation-object triples
                if 'openie' in nlp_results:
                    sources_used.append('OpenIE')
                    for subject, relation, obj in nlp_results['openie']['triples']:
                        # Add nodes (check if already exists to avoid duplicates)
                        if not self.property_graph.has_node(subject):
                            subj_node = GraphNode(id=subject, type=NodeType.OBJECT, label=subject)
                            self.property_graph.add_node(subj_node)
                            # Trace entity addition
                            tracer.log_entity_added(subject, {
                                'source': 'OpenIE',
                                'type': 'OBJECT',
                                'label': subject,
                                'relation_role': 'subject',
                                'relation': relation
                            })
                        if not self.property_graph.has_node(obj):
                            obj_node = GraphNode(id=obj, type=NodeType.OBJECT, label=obj)
                            self.property_graph.add_node(obj_node)
                            # Trace entity addition
                            tracer.log_entity_added(obj, {
                                'source': 'OpenIE',
                                'type': 'OBJECT',
                                'label': obj,
                                'relation_role': 'object',
                                'relation': relation
                            })

                        # Add edge
                        edge = GraphEdge(
                            source=subject,
                            target=obj,
                            type=EdgeType.RELATED_TO,
                            label=relation,
                            metadata={'source': 'openie'}
                        )
                        self.property_graph.add_edge(edge)

                # Source 2: Stanza - Add NER entities as nodes + dependency relations as edges
                if 'stanza' in nlp_results and 'entities' in nlp_results['stanza']:
                    sources_used.append('Stanza')
                    for entity in nlp_results['stanza']['entities']:
                        entity_text = entity.get('text', entity) if isinstance(entity, dict) else entity
                        entity_type = entity.get('type', 'OBJECT') if isinstance(entity, dict) else 'OBJECT'

                        if not self.property_graph.has_node(entity_text):
                            # Map entity type to NodeType
                            node_type = NodeType.OBJECT  # Default
                            if 'QUANTITY' in entity_type.upper():
                                node_type = NodeType.QUANTITY
                            elif 'FORCE' in entity_type.upper():
                                node_type = NodeType.FORCE

                            node = GraphNode(
                                id=entity_text,
                                type=node_type,
                                label=entity_text,
                                properties={'ner_type': entity_type},
                                metadata={'source': 'stanza'}
                            )
                            self.property_graph.add_node(node)

                    # ADDED: Add Stanza dependency relations as edges
                    if 'dependencies' in nlp_results['stanza']:
                        for dep in nlp_results['stanza']['dependencies']:
                            if isinstance(dep, dict):
                                head = dep.get('head')
                                dependent = dep.get('dependent')
                                relation = dep.get('relation', 'depends_on')

                                if head and dependent:
                                    # Ensure nodes exist (create if needed)
                                    if not self.property_graph.has_node(head):
                                        self.property_graph.add_node(GraphNode(
                                            id=head, type=NodeType.OBJECT, label=head,
                                            metadata={'source': 'stanza_dep'}
                                        ))
                                    if not self.property_graph.has_node(dependent):
                                        self.property_graph.add_node(GraphNode(
                                            id=dependent, type=NodeType.OBJECT, label=dependent,
                                            metadata={'source': 'stanza_dep'}
                                        ))

                                    # Add edge
                                    edge = GraphEdge(
                                        source=dependent,
                                        target=head,
                                        type=EdgeType.RELATED_TO,
                                        label=relation,
                                        metadata={'source': 'stanza_dep', 'relation_type': 'dependency'}
                                    )
                                    self.property_graph.add_edge(edge)

                # Source 3: ChemDataExtractor - Add chemical entities
                if 'chemdataextractor' in nlp_results:
                    sources_used.append('ChemDataExtractor')
                    if 'formulas' in nlp_results['chemdataextractor']:
                        for formula in nlp_results['chemdataextractor']['formulas']:
                            formula_text = formula if isinstance(formula, str) else str(formula)
                            if not self.property_graph.has_node(formula_text):
                                node = GraphNode(
                                    id=formula_text,
                                    type=NodeType.OBJECT,
                                    label=formula_text,
                                    properties={'type': 'chemical'},
                                    metadata={'source': 'chemdataextractor'}
                                )
                                self.property_graph.add_node(node)

                # Source 4: MathBERT - Add mathematical entities
                if 'mathbert' in nlp_results:
                    sources_used.append('MathBERT')
                    if 'variables' in nlp_results['mathbert']:
                        for variable in nlp_results['mathbert']['variables']:
                            if not self.property_graph.has_node(variable):
                                node = GraphNode(
                                    id=variable,
                                    type=NodeType.PARAMETER,
                                    label=variable,
                                    properties={'type': 'variable'},
                                    metadata={'source': 'mathbert'}
                                )
                                self.property_graph.add_node(node)

                # Source 5: AMR - Add semantic concepts and relations
                if 'amr' in nlp_results:
                    sources_used.append('AMR')
                    if 'concepts' in nlp_results['amr']:
                        for concept in nlp_results['amr']['concepts']:
                            if not self.property_graph.has_node(concept):
                                node = GraphNode(
                                    id=concept,
                                    type=NodeType.CONCEPT,
                                    label=concept,
                                    metadata={'source': 'amr'}
                                )
                                self.property_graph.add_node(node)

                    # Add AMR relations as edges
                    if 'relations' in nlp_results['amr']:
                        for rel in nlp_results['amr']['relations']:
                            if isinstance(rel, (list, tuple)) and len(rel) >= 3:
                                subj, relation, obj = rel[0], rel[1], rel[2]
                                # Ensure nodes exist
                                if self.property_graph.has_node(subj) and self.property_graph.has_node(obj):
                                    edge = GraphEdge(
                                        source=subj,
                                        target=obj,
                                        type=EdgeType.RELATED_TO,
                                        label=relation,
                                        metadata={'source': 'amr'}
                                    )
                                    self.property_graph.add_edge(edge)

                # Source 6: SciBERT - Add scientific entities if available
                if 'scibert' in nlp_results and 'entities' in nlp_results['scibert']:
                    sources_used.append('SciBERT')
                    for entity in nlp_results['scibert']['entities']:
                        entity_text = entity.get('text', entity) if isinstance(entity, dict) else entity
                        if not self.property_graph.has_node(entity_text):
                            node = GraphNode(
                                id=entity_text,
                                type=NodeType.OBJECT,
                                label=entity_text,
                                properties={'scientific': True},
                                metadata={'source': 'scibert'}
                            )
                            self.property_graph.add_node(node)

                # Source 7: DyGIE++ - Add entities and relations if available
                if 'dygie' in nlp_results:
                    sources_used.append('DyGIE++')
                    if 'entities' in nlp_results['dygie']:
                        for entity in nlp_results['dygie']['entities']:
                            entity_text = entity.get('text', entity) if isinstance(entity, dict) else entity
                            entity_type = entity.get('type', 'OBJECT') if isinstance(entity, dict) else 'OBJECT'

                            if not self.property_graph.has_node(entity_text):
                                node = GraphNode(
                                    id=entity_text,
                                    type=NodeType.OBJECT,
                                    label=entity_text,
                                    properties={'entity_type': entity_type},
                                    metadata={'source': 'dygie'}
                                )
                                self.property_graph.add_node(node)

                    # ADDED: Add DyGIE++ relations as edges
                    if 'relations' in nlp_results['dygie']:
                        for rel in nlp_results['dygie']['relations']:
                            if isinstance(rel, dict):
                                subj = rel.get('subject') or rel.get('head')
                                obj = rel.get('object') or rel.get('tail')
                                rel_type = rel.get('type', 'related_to')

                                if subj and obj:
                                    # Ensure nodes exist
                                    if not self.property_graph.has_node(subj):
                                        self.property_graph.add_node(GraphNode(
                                            id=subj, type=NodeType.OBJECT, label=subj,
                                            metadata={'source': 'dygie_rel'}
                                        ))
                                    if not self.property_graph.has_node(obj):
                                        self.property_graph.add_node(GraphNode(
                                            id=obj, type=NodeType.OBJECT, label=obj,
                                            metadata={'source': 'dygie_rel'}
                                        ))

                                    # Map relation type to EdgeType
                                    edge_type = EdgeType.RELATED_TO
                                    if 'part' in rel_type.lower():
                                        edge_type = EdgeType.PART_OF
                                    elif 'cause' in rel_type.lower():
                                        edge_type = EdgeType.CAUSES
                                    elif 'contain' in rel_type.lower():
                                        edge_type = EdgeType.CONTAINS

                                    # Add edge
                                    edge = GraphEdge(
                                        source=subj,
                                        target=obj,
                                        type=edge_type,
                                        label=rel_type,
                                        metadata={'source': 'dygie', 'relation_type': 'scientific'}
                                    )
                                    self.property_graph.add_edge(edge)

                # Get graph statistics
                all_nodes = self.property_graph.get_all_nodes()
                all_edges = self.property_graph.get_edges()
                connected_components = self.property_graph.get_connected_components()

                # Count node types
                node_type_counts = {}
                for node in all_nodes:
                    node_type = node.type.value if hasattr(node.type, 'value') else str(node.type)
                    node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

                # Count edge types
                edge_type_counts = {}
                for edge in all_edges:
                    edge_type = edge.type.value if hasattr(edge.type, 'value') else str(edge.type)
                    edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1

                print(f"  ✅ Built multi-source knowledge graph:", flush=True)
                print(f"     • Sources: {', '.join(sources_used) if sources_used else 'none'}", flush=True)
                print(f"     • Nodes: {len(all_nodes)} ({', '.join(f'{k}:{v}' for k, v in node_type_counts.items())})", flush=True)
                print(f"     • Edges: {len(all_edges)} ({', '.join(f'{k}:{v}' for k, v in edge_type_counts.items())})", flush=True)
                print(f"     • Connected components: {len(connected_components)}", flush=True)

                ontology_enrichment_summary = self._enrich_property_graph_with_ontologies(self.property_graph)
                gap_summary = self._run_property_graph_gap_queries(self.property_graph)

                if gap_summary.get('missing_units', {}).get('count'):
                    print(f"     • ⚠ Quantities missing unit: {gap_summary['missing_units']['count']}", flush=True)
                if gap_summary.get('dielectric_missing_kappa', {}).get('count'):
                    print(f"     • ⚠ Dielectrics missing κ: {gap_summary['dielectric_missing_kappa']['count']}", flush=True)

                # ✅ FIX 3: Rich output (full graph structure, not just counts)
                graph_output = {
                    'request_id': request_id,
                    'summary': {
                        'node_count': len(all_nodes),
                        'edge_count': len(all_edges),
                        'connected_components': len(connected_components),
                        'sources_used': sources_used
                    },
                    'node_types': node_type_counts,
                    'edge_types': edge_type_counts,
                    'nodes': [node.to_dict() for node in all_nodes[:10]],  # First 10 nodes
                    'edges': [edge.to_dict() for edge in all_edges[:10]],  # First 10 edges
                }
                if ontology_enrichment_summary:
                    graph_output['ontology_tags'] = ontology_enrichment_summary
                if gap_summary:
                    graph_output['gap_analysis'] = gap_summary

                persistence_details = self._persist_property_graph(self.property_graph, request_id=request_id)
                graph_output.update(persistence_details)

                disk_info = persistence_details.get('disk_persistence')
                if disk_info and disk_info.get('status') == 'success':
                    print(f"  💾 Graph snapshot: {disk_info['path']}", flush=True)
                elif disk_info and disk_info.get('status') == 'error':
                    print(f"  ⚠️  Disk persistence failed: {disk_info.get('error')}", flush=True)

                graphdb_info = persistence_details.get('graphdb_persistence')
                if graphdb_info:
                    status = graphdb_info.get('status')
                    if status == 'success':
                        print(f"  🗄  Graph DB sync: {graphdb_info.get('backend')} ({graphdb_info.get('nodes_synced')} nodes)", flush=True)
                    else:
                        print(f"  ⚠️  Graph DB sync skipped: {graphdb_info.get('reason', 'unknown reason')}", flush=True)

                print("└───────────────────────────────────────────────────────────────┘\n")

                # Complete tracer for Property Graph phase
                tracer.log_output(graph_output, "property_graph")
                tracer.track_entity_flow("Property Graph Construction", [
                    {'id': node[0], 'label': node[1].get('label', ''), 'type': node[1].get('type', '')}
                    for node in all_nodes
                ])
                tracer.log_transformation("Property Graph Construction", {
                    'sources_used': sources_used,
                    'total_nodes': len(all_nodes),
                    'total_edges': len(all_edges),
                    'node_types': list(graph_output.get('node_types', {}).keys()),
                    'edge_types': list(graph_output.get('edge_types', {}).keys())
                })
                tracer.complete_component()

                if self.logger:
                    self.logger.log_phase_output(graph_output, f"Built graph with {len(all_nodes)} nodes from {len(sources_used)} sources")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'Property Graph Construction',
                    'duration': time.time() - stage_start_time,
                    'output': graph_output
                })
                current_property_graph = self.property_graph

            # Phase 0.6: DeepSeek Enrichment (Roadmap API Call #1)
            enrichment_result = None
            if self.deepseek_client and self.config.enable_deepseek_enrichment and self.property_graph:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("DeepSeek Enrichment", 1, "Validate and enrich entities with LLM")
                if self.progress:
                    self.progress.start_phase("DeepSeek Enrichment", 1)
                print("┌─ PHASE 0.6: DEEPSEEK ENRICHMENT (Roadmap Call #1) ────────────┐")

                try:
                    # Get all nodes from property graph
                    all_nodes = list(self.property_graph.get_all_nodes())

                    # Call DeepSeek for enrichment
                    enrichment_result = self.deepseek_client.enrich_entities(
                        entities=all_nodes,
                        context=problem_text,
                        domain=None  # Will be determined in Phase 1
                    )

                    if 'error' not in enrichment_result:
                        print(f"  ✅ DeepSeek enriched {len(enrichment_result.get('validated_entities', []))} entities", flush=True)
                        if enrichment_result.get('missing_entities'):
                            print(f"  ℹ️  Identified {len(enrichment_result['missing_entities'])} missing entities", flush=True)
                        if enrichment_result.get('corrections'):
                            print(f"  ✏️  Made {len(enrichment_result['corrections'])} corrections", flush=True)
                        if enrichment_result.get('warnings'):
                            print(f"  ⚠️  {len(enrichment_result['warnings'])} warnings", flush=True)

                        # Report cost
                        cost = enrichment_result.get('cost_usd', 0)
                        print(f"  💰 API cost: ${cost:.4f}", flush=True)
                    else:
                        print(f"  ⚠️  Enrichment failed: {enrichment_result['error']}", flush=True)

                except Exception as e:
                    print(f"  ⚠️  DeepSeek enrichment error: {type(e).__name__}: {str(e)[:100]}", flush=True)
                    enrichment_result = {'error': str(e)}

                print("└───────────────────────────────────────────────────────────────┘\n")

                if self.logger:
                    self.logger.log_phase_output(enrichment_result, "DeepSeek entity enrichment")
                    self.logger.end_phase("success" if 'error' not in enrichment_result else "warning")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'DeepSeek Enrichment',
                    'duration': time.time() - stage_start_time,
                    'output': {
                        'validated_entities': len(enrichment_result.get('validated_entities', [])) if enrichment_result else 0,
                        'missing_entities': len(enrichment_result.get('missing_entities', [])) if enrichment_result else 0,
                        'corrections': len(enrichment_result.get('corrections', [])) if enrichment_result else 0,
                        'cost_usd': enrichment_result.get('cost_usd', 0) if enrichment_result else 0
                    }
                })

            # Phase 1: Diagram Planning (NEW: Property Graph-Driven Architecture)
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Diagram Planning (Property Graph-Driven)", 2, "Create diagram plan from property graph")
                self.logger.log_phase_input(problem_text, "Original request + Property graph")
            if self.progress:
                self.progress.start_phase("Diagram Planning", 2)

            print("┌─ PHASE 1: DIAGRAM PLANNING (Property Graph-Driven) ───────────┐")

            # NEW ARCHITECTURE: Plan from property graph WITHOUT LLM extraction
            diagram_plan = None
            specs = None
            domain = None

            if self.diagram_planner and self.property_graph:
                # Try to infer domain from property graph
                domain_hint = self._infer_domain_from_graph(self.property_graph)

                # Use NEW property graph-driven planner
                diagram_plan = self.diagram_planner.plan_from_property_graph(
                    property_graph=self.property_graph,
                    problem_text=problem_text,
                    domain=domain_hint
                )

                complexity_score = diagram_plan.complexity_score

                print(f"  ✅ Property Graph-Driven Planning Complete:", flush=True)
                print(f"     • Entities: {len(diagram_plan.extracted_entities)}", flush=True)
                print(f"     • Relations: {len(diagram_plan.extracted_relations)}", flush=True)
                print(f"     • Constraints: {len(diagram_plan.global_constraints)}", flush=True)
                print(f"     • Complexity: {complexity_score:.2f}", flush=True)
                print(f"     • Strategy: {diagram_plan.strategy.value}", flush=True)
                print(f"     • Solver: {diagram_plan.layout_hints.get('solver', 'heuristic')}", flush=True)
                print(f"     • Z3 Used: {diagram_plan.layout_hints.get('z3_used', False)}", flush=True)

                # Convert DiagramPlan to CanonicalProblemSpec (for backward compatibility)
                specs = self._diagram_plan_to_canonical_spec(diagram_plan)
                domain = specs.domain if specs.domain else PhysicsDomain.MECHANICS
                resolved_domain = domain.value if domain else domain_hint
                domain_module_outputs = self._build_domain_modules(
                    resolved_domain,
                    diagram_plan,
                    specs,
                    current_property_graph
                )
                if domain_module_outputs:
                    specs.diagram_plan_metadata.setdefault('domain_modules', domain_module_outputs)

            else:
                # FALLBACK: Use old LLM extraction if property graph unavailable
                print("  ⚠️  Property graph unavailable, falling back to LLM extraction")
                specs = self.ai_analyzer.analyze(problem_text)
                domain = specs.domain

                # Assess complexity from specs
                if self.diagram_planner:
                    complexity_score = self.diagram_planner.assess_complexity(specs)
                else:
                    complexity_score = 0.5  # Default medium complexity

                print(f"  Domain: {domain.value}", flush=True)
                print(f"  Objects: {len(specs.objects)}", flush=True)
                print(f"  Constraints: {len(specs.constraints)}", flush=True)

            print("└───────────────────────────────────────────────────────────────┘\n")

            phase1_output = {
                'planning_mode': 'property_graph_driven' if diagram_plan else 'llm_extraction',
                'domain': domain.value if hasattr(domain, 'value') else str(domain),
                'entity_count': len(diagram_plan.extracted_entities) if diagram_plan else len(specs.objects),
                'relation_count': len(diagram_plan.extracted_relations) if diagram_plan else 0,
                'constraint_count': len(diagram_plan.global_constraints) if diagram_plan else len(specs.constraints),
                'complexity_score': complexity_score,
                'z3_used': diagram_plan.layout_hints.get('z3_used', False) if diagram_plan else False,
                'sympy_used': diagram_plan.layout_hints.get('sympy_used', False) if diagram_plan else False
            }
            if self.logger:
                self.logger.log_phase_output(phase1_output, f"Planning mode: {phase1_output['planning_mode']}")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Diagram Planning',
                'duration': time.time() - stage_start_time,
                'output': phase1_output
            })

            # Phase 2: Scene Synthesis (Enhanced with Strategic Planning)
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Scene Synthesis + Strategic Planning", 3, "Build scene graph and select strategy")
                self.logger.log_phase_input(specs, f"Problem specs with {len(specs.objects)} objects")
            if self.progress:
                self.progress.start_phase("Scene Synthesis", 3)
            print("┌─ PHASE 2: SCENE SYNTHESIS + STRATEGIC PLANNING ───────────────┐")

            # NEW: Strategic Planning
            if self.diagram_planner and complexity_score is not None:
                strategy = self.diagram_planner.select_strategy(specs, complexity_score)
                selected_strategy = strategy.value
                print(f"  Selected Strategy: {selected_strategy}", flush=True)

            # NEW: LLM-based Planning (if enabled)
            llm_plan_result = None
            if self.llm_planner:
                try:
                    print("  LLM Planning: Generating diagram plan...", flush=True)
                    llm_plan = self.llm_planner.generate_plan(
                        description=problem_text,
                        domain=domain.value if domain else (diagram_plan.metadata.get('domain_hint') if diagram_plan else 'general'),
                        use_local=True,
                        deepseek_client=self.deepseek_client,
                        verify_with_deepseek=getattr(self.config, 'enable_deepseek_audit', False)
                    )
                    llm_plan_result = llm_plan.to_dict()
                    llm_plan_result['verifier'] = 'deepseek' if self.deepseek_client else ('api' if self.llm_planner.api_client else 'none')
                    print(f"  LLM Plan: {len(llm_plan.entities)} entities, {len(llm_plan.relationships)} relationships", flush=True)
                except Exception as e:
                    print(f"  LLM Planning failed: {e}", flush=True)
                    llm_plan_result = {'error': str(e)}

            # NEW: Query primitive library for relevant components
            retrieved_primitives = []
            if self.primitive_library and diagram_plan:
                print("  🔍 Primitive Library: Searching for reusable components...", flush=True)

                # Search based on extracted entities
                for entity in diagram_plan.extracted_entities[:10]:  # Top 10 entities
                    entity_label = entity.label if hasattr(entity, 'label') else str(entity)
                    entity_type = entity.type if hasattr(entity, 'type') else 'object'

                    # Semantic search query
                    query_text = f"{domain_hint if domain_hint else 'physics'} {entity_label} {entity_type}"
                    results = self.primitive_library.query(
                        text=query_text,
                        top_k=2,
                        category=None,  # Could map domain_hint to PrimitiveCategory if needed
                        min_score=0.0
                    )

                    if results:
                        retrieved_primitives.extend(results[:1])  # Take top result

                if retrieved_primitives:
                    print(f"  ✅ Found {len(retrieved_primitives)} reusable primitive(s)", flush=True)
                else:
                    print(f"  ℹ️  No matching primitives found (will use procedural generation)", flush=True)

            # Pass NLP context, property graph, strategy, and primitives to scene builder
            scene = self.scene_builder.build(
                specs,
                nlp_context={
                    'entities': nlp_results.get('stanza', {}).get('entities', []) if nlp_results else [],
                    'triples': nlp_results.get('openie', {}).get('triples', []) if nlp_results else [],
                    'embeddings': nlp_results.get('scibert', {}).get('embeddings', []) if nlp_results else [],
                    'primitives': retrieved_primitives  # ADDED: Pass retrieved primitives
                } if nlp_results else {'primitives': retrieved_primitives},
                property_graph=current_property_graph if current_property_graph else None,
                strategy=selected_strategy if self.diagram_planner else "DIRECT",
                diagram_plan=diagram_plan if diagram_plan else getattr(specs, 'diagram_plan', None)
            )
            if domain_module_outputs:
                scene.metadata.setdefault('domain_modules', domain_module_outputs)
            print(f"  Scene Objects: {len(scene.objects)}", flush=True)
            print("└───────────────────────────────────────────────────────────────┘\n")
            phase2_output = {
                'object_count': len(scene.objects),
                'selected_strategy': selected_strategy,
                'domain_modules': len(domain_module_outputs)
            }
            if diagram_plan:
                phase2_output['diagram_plan'] = {
                    'entities': len(diagram_plan.extracted_entities),
                    'relations': len(diagram_plan.extracted_relations),
                    'constraints': len(diagram_plan.global_constraints),
                    'solver': diagram_plan.layout_hints.get('solver', 'unknown') if hasattr(diagram_plan, 'layout_hints') else 'unknown'
                }
            if self.logger:
                self.logger.log_phase_output(phase2_output, f"Scene with {len(scene.objects)} objects")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Scene Synthesis',
                'duration': time.time() - stage_start_time,
                'output': phase2_output
            })

            # Phase 2.5: Structural Plan vs Scene Validation
            if diagram_plan and self.config.enable_structural_validation:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("Structural Consistency", 3, "Compare plan vs scene")
                    self.logger.log_phase_input({'entities': len(diagram_plan.extracted_entities)}, "Diagram Plan")
                structural_comparison = compare_plan_scene(diagram_plan, scene)
                structural_report = structural_comparison.to_dict()
                missing = len(structural_report['missing_in_scene'])
                relation_gaps = len(structural_report['relation_gaps'])
                print("┌─ PHASE 2.5: STRUCTURAL CONSISTENCY ──────────────────────────┐")
                print(f"  Structural score: {structural_report['score']:.2f}", flush=True)
                print(f"  Missing in scene: {missing}", flush=True)
                if missing:
                    print(f"    IDs: {', '.join(structural_report['missing_in_scene'][:3])}", flush=True)
                if relation_gaps:
                    print(f"  Relation gaps: {relation_gaps}", flush=True)
                print("└───────────────────────────────────────────────────────────────┘\n")
                if self.logger:
                    self.logger.log_phase_output(structural_report, "Structural comparison report")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'Structural Consistency',
                    'duration': time.time() - stage_start_time,
                    'output': structural_report
                })

            # Phase 3: Ontology Validation (NEW)
            if ONTOLOGY_AVAILABLE and self.config.enable_ontology_validation:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("Ontology Validation", 4, "Validate semantic consistency")
                    self.logger.log_phase_input(specs, f"Specs with {len(specs.objects)} objects")
                if self.progress:
                    self.progress.start_phase("Ontology Validation", 4)
                print("┌─ PHASE 3: ONTOLOGY VALIDATION ────────────────────────────────┐")

                # Map domain to ontology domain
                ontology_domain_map = {
                    'physics': Domain.PHYSICS,
                    'chemistry': Domain.CHEMISTRY,
                    'biology': Domain.BIOLOGY
                }
                ont_domain = ontology_domain_map.get(domain.value.lower(), Domain.PHYSICS)

                try:
                    ontology_mgr = OntologyManager(domain=ont_domain)
                    ontology_source = "property_graph" if current_property_graph else "specs"
                    ontology_input_stats = {}

                    if current_property_graph:
                        ontology_mgr.from_property_graph(current_property_graph)
                        ontology_input_stats = {
                            'nodes': len(current_property_graph.get_all_nodes()),
                            'edges': len(current_property_graph.get_edges())
                        }
                    else:
                        for obj in specs.objects:
                            obj_id = obj.get('id') if isinstance(obj, dict) else getattr(obj, 'id', None)
                            if not obj_id:
                                continue
                            class_uri = f"{ont_domain.value.lower()}:Object"
                            ontology_mgr.add_instance(obj_id, class_uri)
                        ontology_input_stats = {
                            'nodes': len(specs.objects),
                            'edges': 0
                        }

                    validation_result = ontology_mgr.validate()
                    self.ontology_manager = ontology_mgr
                    ontology_validation = {
                        'source': ontology_source,
                        'input_stats': ontology_input_stats,
                        'consistent': validation_result.is_valid,
                        'errors': validation_result.errors,
                        'warnings': validation_result.warnings,
                        'inferences': len(validation_result.inferences)
                    }
                    print(f"  Ontology Source: {ontology_source} ({ontology_input_stats.get('nodes', 0)} nodes)", flush=True)
                    print(f"  Ontology Consistent: {validation_result.is_valid}", flush=True)
                    if validation_result.errors:
                        print(f"  ⚠ Errors: {len(validation_result.errors)}", flush=True)
                    if validation_result.inferences:
                        print(f"  ↪ Inferences: {len(validation_result.inferences)}", flush=True)

                except ImportError as e:
                    print(f"  ⚠️  RDFLib not available - skipping ontology validation", flush=True)
                    print(f"     Install with: pip install rdflib owlrl", flush=True)
                    ontology_validation = {
                        'consistent': None,
                        'errors': [f'RDFLib not installed: {str(e)}'],
                        'warnings': ['Ontology validation skipped - RDFLib not available']
                    }

                print("└───────────────────────────────────────────────────────────────┘\n")
                if self.logger:
                    self.logger.log_phase_output(ontology_validation, f"Consistent: {ontology_validation.get('consistent', 'N/A')}")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'Ontology Validation',
                    'duration': time.time() - stage_start_time,
                    'output': ontology_validation
                })

            # Phase 4: Physics Validation
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Physics Validation", 5, "Validate physics constraints and relationships")
                self.logger.log_phase_input(scene, f"Scene with {len(scene.objects)} objects")
            if self.progress:
                self.progress.start_phase("Physics Validation", 5)
            print("┌─ PHASE 4: PHYSICS VALIDATION ─────────────────────────────────────┐")
            report, scene = self.validator.validate(scene, specs)
            print("└───────────────────────────────────────────────────────────────────┘\n")
            phase4_output = {
                'errors': len(report.errors),
                'warnings': len(report.warnings)
            }
            if self.logger:
                self.logger.log_phase_output(phase4_output, f"Errors: {len(report.errors)}, Warnings: {len(report.warnings)}")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Physics Validation',
                'duration': time.time() - stage_start_time,
                'output': phase4_output
            })

            if not report.is_valid and self.config.validation_mode == 'strict':
                raise Exception(f"Validation failed in strict mode: {report.errors}")

            if self.config.enable_domain_rule_validation:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("Domain Rule Validation", 5, "Run Kirchhoff/Newton/Geometry checks")
                    self.logger.log_phase_input({'domain': domain.value if domain else 'unknown'}, "Domain context")
                domain_rule_report = run_domain_rules(domain.value if domain else None, scene, specs)
                errors = domain_rule_report['errors']
                warnings = domain_rule_report['warnings']
                print("┌─ PHASE 4.5: DOMAIN RULE VALIDATION ─────────────────────────┐")
                print(f"  Errors: {errors}, Warnings: {warnings}", flush=True)
                if errors:
                    for entry in domain_rule_report['checks']:
                        if not entry['passed'] and entry['severity'] == 'error':
                            print(f"    ❌ {entry['name']}: {entry['details']}", flush=True)
                if warnings:
                    for entry in domain_rule_report['checks']:
                        if not entry['passed'] and entry['severity'] == 'warning':
                            print(f"    ⚠️  {entry['name']}: {entry['details']}", flush=True)
                print("└───────────────────────────────────────────────────────────────┘\n")
                if self.logger:
                    self.logger.log_phase_output(domain_rule_report, "Domain rule evaluation")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'Domain Rule Validation',
                    'duration': time.time() - stage_start_time,
                    'output': domain_rule_report
                })

            # Pre-Layout Validation
            # ...

            # Phase 5: Layout Optimization (Model Orchestrator + Z3/SymPy)
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Layout Optimization + Z3/SymPy", 6, "Compute optimal object positions")
                self.logger.log_phase_input(scene, f"Scene with {len(scene.objects)} unpositioned objects")
            if self.progress:
                self.progress.start_phase("Layout Optimization", 6)
            print("┌─ PHASE 5: LAYOUT OPTIMIZATION + Z3 ───────────────────────────┐")

            plan_for_layout = diagram_plan
            if plan_for_layout is None and self.diagram_planner:
                try:
                    plan_for_layout = self.diagram_planner.plan(specs)
                except Exception as e:
                    if self.logger:
                        self.logger.log_phase_detail(f"Fallback plan generation failed: {e}")
                    plan_for_layout = None

            orchestrated_model = ModelType.HEURISTIC
            orchestrator_meta = {}
            if self.model_orchestrator and plan_for_layout:
                try:
                    orchestrated_model = self.model_orchestrator.select_model(specs, plan_for_layout)
                    orchestrator_meta = {
                        'model': orchestrated_model.value,
                        'complexity': plan_for_layout.complexity_score
                    }
                except Exception as e:
                    orchestrator_meta = {'model': 'heuristic', 'error': str(e)}
                    orchestrated_model = ModelType.HEURISTIC
            if orchestrator_meta:
                print(f"  Model Orchestrator Strategy: {orchestrated_model.value} (complexity {orchestrator_meta.get('complexity', 0):.2f})", flush=True)

            z3_used = False
            sympy_used = False
            pre_positions = 0
            solver_notes = []

            if plan_for_layout:
                if orchestrated_model in (ModelType.CONSTRAINT_SOLVER, ModelType.HYBRID):
                    positions_applied, z3_success = self._apply_z3_layout(plan_for_layout, scene)
                    pre_positions += positions_applied
                    z3_used = z3_success
                    solver_notes.append('z3' if z3_success else 'z3_failed')

                    if orchestrated_model == ModelType.HYBRID and (not z3_success) and self.config.enable_sympy_solver:
                        positions_applied, sympy_success = self._apply_sympy_layout(plan_for_layout, scene)
                        pre_positions += positions_applied
                        sympy_used = sympy_success
                        solver_notes.append('sympy' if sympy_success else 'sympy_failed')

                elif orchestrated_model == ModelType.SYMBOLIC_PHYSICS and self.config.enable_sympy_solver:
                    positions_applied, sympy_success = self._apply_sympy_layout(plan_for_layout, scene)
                    pre_positions += positions_applied
                    sympy_used = sympy_success
                    solver_notes.append('sympy' if sympy_success else 'sympy_failed')

            if pre_positions:
                print(f"  ⚙️  Pre-layout solver positioned {pre_positions} objects ({', '.join(solver_notes)})", flush=True)

            # Use standard layout engine for final positioning
            positioned_scene = self.layout_engine.solve(scene, specs)
            print(f"  Positioned Objects: {len(positioned_scene.objects)}", flush=True)
            print("└───────────────────────────────────────────────────────────────┘\n")
            phase5_output = {
                'object_count': len(positioned_scene.objects),
                'z3_used': z3_used,
                'sympy_used': sympy_used,
                'pre_solver_positions': pre_positions,
                'model_strategy': orchestrated_model.value,
                'model_orchestrator': orchestrator_meta
            }
            if self.logger:
                self.logger.log_phase_output(phase5_output, f"Positioned {len(positioned_scene.objects)} objects")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Layout Optimization',
                'duration': time.time() - stage_start_time,
                'output': phase5_output
            })

            # NEW Phase 5.5: Intelligent Label Placement
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Intelligent Label Placement", 7, "Optimize label positions to avoid overlaps")
                self.logger.log_phase_input(positioned_scene, "Positioned scene")
            if self.progress:
                self.progress.start_phase("Label Placement", 7)
            print("┌─ PHASE 5.5: INTELLIGENT LABEL PLACEMENT ──────────────────────┐")
            positioned_scene = self.label_placer.place_labels(positioned_scene)
            print("└───────────────────────────────────────────────────────────────┘\n")
            if self.logger:
                self.logger.log_phase_output({}, "Labels placed")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Label Placement',
                'duration': time.time() - stage_start_time,
                'output': {}
            })

            # NEW Phase 5.6: Spatial Validation
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Spatial Validation", 8, "Check for overlaps and positioning errors")
                self.logger.log_phase_input(positioned_scene, "Final positioned scene")
            if self.progress:
                self.progress.start_phase("Spatial Validation", 8)
            print("┌─ PHASE 5.6: SPATIAL VALIDATION ───────────────────────────────┐")
            spatial_report = self.spatial_validator.validate(positioned_scene)
            print(f"  {spatial_report.summary()}", flush=True)

            if spatial_report.has_errors():
                print(f"  ❌ Found {len(spatial_report.errors)} spatial errors:", flush=True)
                for i, error in enumerate(spatial_report.errors[:3], 1):
                    print(f"     {i}. {error}", flush=True)
                if len(spatial_report.errors) > 3:
                    print(f"     ... and {len(spatial_report.errors) - 3} more", flush=True)

                # In strict mode, fail on spatial errors
                if self.config.validation_mode == 'strict':
                    raise Exception(f"Spatial validation failed: {spatial_report.errors}")

            if spatial_report.has_warnings():
                print(f"  ⚠️  Found {len(spatial_report.warnings)} spatial warnings:", flush=True)
                for i, warning in enumerate(spatial_report.warnings[:2], 1):
                    print(f"     {i}. {warning}", flush=True)
                if len(spatial_report.warnings) > 2:
                    print(f"     ... and {len(spatial_report.warnings) - 2} more", flush=True)

            print("└───────────────────────────────────────────────────────────────┘\n")
            spatial_output = {
                'errors': len(spatial_report.errors),
                'warnings': len(spatial_report.warnings),
                'is_valid': spatial_report.is_valid()
            }
            if self.logger:
                self.logger.log_phase_output(spatial_output, f"Errors: {len(spatial_report.errors)}, Warnings: {len(spatial_report.warnings)}")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Spatial Validation',
                'duration': time.time() - stage_start_time,
                'output': spatial_output
            })

            # Phase 6: Rendering
            stage_start_time = time.time()
            if self.logger:
                self.logger.start_phase("Rendering", 9, "Generate SVG output")
                self.logger.log_phase_input(positioned_scene, f"Positioned scene with {len(positioned_scene.objects)} objects")
            if self.progress:
                self.progress.start_phase("Rendering", 9)
            print("┌─ PHASE 6: RENDERING ──────────────────────────────────────────────┐")
            svg = self.renderer.render(positioned_scene, specs)
            print("└───────────────────────────────────────────────────────────────────┘\n")
            phase6_output = {'svg_size': len(svg)}
            if self.logger:
                self.logger.log_phase_output(phase6_output, f"SVG generated ({len(svg):,} bytes)")
                self.logger.end_phase("success")
            if self.progress:
                self.progress.end_phase(True)
            trace['stages'].append({
                'name': 'Rendering',
                'duration': time.time() - stage_start_time,
                'output': phase6_output
            })

            print("✅ UNIVERSAL RENDERER COMPLETE")
            print(f"   SVG size: {len(svg):,} bytes", flush=True)
            print(f"   Domain: {domain.value if domain else 'unknown'}", flush=True)

            # Phase 6.5: Validation Refinement Loop (NEW)
            run_validation_loop = any([
                self.diagram_validator,
                self.vlm_validator,
                (self.deepseek_client and self.config.enable_deepseek_validation),
                self.config.enable_structural_validation,
                self.config.enable_domain_rule_validation
            ])
            validation_results = {}
            if run_validation_loop:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("Validation Refinement", 7, "Iterative quality improvement")
                    self.logger.log_phase_input({'svg_size': len(svg)}, "SVG and scene")
                if self.progress:
                    self.progress.start_phase("Refinement", 7)
                print("\n┌─ PHASE 6.5: VALIDATION REFINEMENT ─────────────────────────────┐")

                try:
                    validation_results, svg = self._post_validate(
                        svg,
                        positioned_scene,
                        specs,
                        problem_text,
                        diagram_plan,
                        domain_rule_report
                    )
                    vlm_description = validation_results.get('vlm_description')

                    # Log refinement iterations
                    print(f"  Refinement Iterations: {validation_results['refinement_iterations']}", flush=True)
                    print(f"  Overall Confidence: {validation_results['overall_confidence']:.2f}", flush=True)
                    print(f"  Issues Found: {len(validation_results['issues'])}", flush=True)

                    refinement_output = {
                        'refinement_iterations': validation_results['refinement_iterations'],
                        'overall_confidence': validation_results['overall_confidence'],
                        'issue_count': len(validation_results['issues']),
                        'suggestions': len(validation_results.get('suggestions', []))
                    }

                    print("└───────────────────────────────────────────────────────────────────┘\n")

                    if self.logger:
                        self.logger.log_phase_output(refinement_output,
                            f"Refined {validation_results['refinement_iterations']} times")
                        self.logger.end_phase("success")
                    if self.progress:
                        self.progress.end_phase(True)

                    trace['stages'].append({
                        'name': 'Validation Refinement',
                        'duration': time.time() - stage_start_time,
                        'output': refinement_output
                    })

                except Exception as e:
                    print(f"  ⚠️  Refinement skipped: {e}", flush=True)
                    print("└───────────────────────────────────────────────────────────────────┘\n")
                    if self.logger:
                        self.logger.log_phase_detail(f"Refinement error: {e}")
                        self.logger.end_phase("skipped")
                    if self.progress:
                        self.progress.end_phase(True)

            # Phase 7: LLM Auditing (NEW)
            if self.auditor:
                stage_start_time = time.time()
                if self.logger:
                    self.logger.start_phase("LLM Quality Auditing", 10, "Audit diagram quality with LLM")
                    self.logger.log_phase_input({'specs': specs, 'svg_size': len(svg)}, "Specs and SVG")
                if self.progress:
                    self.progress.start_phase("LLM Auditing", 10)
                print("\n┌─ PHASE 7: LLM QUALITY AUDITING ───────────────────────────────┐")

                try:
                    audit_result = self.auditor.audit(
                        specs,
                        svg_output=svg,
                        structural_report=structural_report,
                        domain_rule_report=domain_rule_report,
                        validation_results=validation_results,
                        vlm_description=vlm_description
                    )
                    audit_report = {
                        'overall_score': audit_result.overall_score,
                        'issue_count': len(audit_result.issues),
                        'critical_issues': [i for i in audit_result.issues if i.severity == 'CRITICAL'],
                        'suggestions': audit_result.suggestions[:3]  # Top 3
                    }
                    print(f"  Overall Score: {audit_result.overall_score:.1f}/10", flush=True)
                    print(f"  Issues Found: {len(audit_result.issues)}", flush=True)
                    if audit_result.suggestions:
                        print(f"  Suggestions: {len(audit_result.suggestions)}", flush=True)

                except Exception as e:
                    print(f"  Auditing skipped: {e}", flush=True)
                    audit_report = {'error': str(e)}

                print("└───────────────────────────────────────────────────────────────┘\n")
                if self.logger:
                    self.logger.log_phase_output(audit_report, f"Audit completed")
                    self.logger.end_phase("success")
                if self.progress:
                    self.progress.end_phase(True)
                trace['stages'].append({
                    'name': 'LLM Auditing',
                    'duration': time.time() - stage_start_time,
                    'output': audit_report
                })

            # Summary
            print("\n" + "="*80)
            print("✅ DIAGRAM GENERATION COMPLETE")
            print("="*80)
            print(f"   Request ID: {request_id}", flush=True)
            print(f"   Domain: {domain.value if domain else 'unknown'}", flush=True)
            print(f"   SVG Size: {len(svg):,} bytes", flush=True)
            if complexity_score:
                print(f"   Complexity: {complexity_score:.2f}", flush=True)
            if selected_strategy:
                print(f"   Strategy: {selected_strategy}", flush=True)
            if self.active_features:
                print(f"   Advanced Features: {len(self.active_features)} active", flush=True)
            print("="*80)

            # Log final response
            if self.logger:
                self.logger.log_response(
                    success=True,
                    result={
                        'svg_size': len(svg),
                        'domain': domain.value if domain else 'unknown',
                        'total_objects': len(positioned_scene.objects),
                        'complexity_score': complexity_score,
                        'selected_strategy': selected_strategy
                    }
                )

            result_metadata = self._compose_result_metadata(
                trace=trace,
                domain=domain,
                scene=positioned_scene,
                features=self.active_features,
                request_id=request_id,
                structural_report=structural_report,
                domain_rule_report=domain_rule_report,
                validation_results=validation_results,
                ontology_validation=ontology_validation,
                audit_report=audit_report,
                vlm_description=vlm_description
            )

            # Return complete result with ALL advanced artifacts
            return DiagramResult(
                svg=svg,
                scene=positioned_scene,
                specs=specs,
                validation_report=report,
                quality_report=None,
                # NEW: Advanced pipeline artifacts
                property_graph=current_property_graph,
                nlp_results=nlp_results if nlp_results else None,
                complexity_score=complexity_score,
                selected_strategy=selected_strategy,
                llm_plan=llm_plan_result,
                diagram_plan=diagram_plan.to_dict() if diagram_plan else None,
                domain_module_outputs=domain_module_outputs if domain_module_outputs else None,
                ontology_validation=ontology_validation,
                audit_report=audit_report,
                # Metadata
                metadata=result_metadata
            )

        except Exception as e:
            # Log error
            if self.logger:
                self.logger.log_error(e, {
                    'domain': domain.value if domain else 'unknown',
                    'phase': 'generation'
                })
                self.logger.log_response(
                    success=False,
                    error=str(e)
                )
            # Re-raise the exception
            raise

        finally:
            # Export comprehensive trace
            tracer.print_summary()
            trace_file = tracer.export_trace()
            print(f"\n📊 Detailed trace exported to: {trace_file}")

            # Keep original trace for compatibility
            with open('generation_trace.json', 'w') as f:
                json.dump(trace, f, indent=2)

    def _post_validate(self,
                       svg: str,
                       scene: Scene,
                       spec: CanonicalProblemSpec,
                       problem_text: str,
                       diagram_plan: Optional[Any] = None,
                       domain_rule_report: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], str]:
        """Phase 7: AI-based quality validation with refinement loop"""

        max_iterations = max(1, getattr(self.config, 'auto_refinement_max_iterations', 1))
        min_score = getattr(self.config, 'auto_refinement_min_score', 0.85)

        validation_results: Dict[str, Any] = {
            'structural': None,
            'structural_history': [],
            'domain_rules': domain_rule_report,
            'domain_rule_history': [],
            'visual_semantic': None,
            'semantic_fidelity': None,
            'overall_confidence': 0.0,
            'issues': [],
            'suggestions': [],
            'refinement_trace': []
        }

        svg_output = svg
        for iteration in range(max_iterations):
            iteration_info = {'iteration': iteration + 1, 'fixes': 0}
            structural_snapshot = None
            if diagram_plan and self.config.enable_structural_validation:
                structural_snapshot = compare_plan_scene(diagram_plan, scene).to_dict()
                validation_results['structural'] = structural_snapshot
                validation_results['structural_history'].append(structural_snapshot)
                iteration_info['structural_score'] = structural_snapshot['score']
            domain_snapshot = None
            if self.config.enable_domain_rule_validation:
                domain_snapshot = run_domain_rules(spec.domain.value if spec.domain else None, scene, spec)
                validation_results['domain_rules'] = domain_snapshot
                validation_results['domain_rule_history'].append(domain_snapshot)

            quality_score = None
            aggregated_issues: List[str] = []
            if self.diagram_validator:
                try:
                    quality_score = self.diagram_validator.validate(scene)
                    validation_results['structural_validator'] = {
                        'overall_score': quality_score.overall_score,
                        'layout_score': quality_score.layout_score,
                        'connectivity_score': quality_score.connectivity_score,
                        'style_score': quality_score.style_score,
                        'physics_score': quality_score.physics_score,
                        'issues': [str(i) for i in quality_score.issues]
                    }
                    validation_results['overall_confidence'] = max(validation_results['overall_confidence'],
                                                                   quality_score.overall_score)
                    aggregated_issues.extend([str(issue) for issue in quality_score.issues])
                except Exception as exc:
                    if self.logger:
                        self.logger.log_phase_detail(f"Validator error: {exc}")

            if structural_snapshot:
                aggregated_issues.extend([f"missing:{obj_id}" for obj_id in structural_snapshot['missing_in_scene']])
                aggregated_issues.extend([f"label_mismatch:{entry}" for entry in structural_snapshot['label_mismatches']])
            if domain_snapshot:
                for check in domain_snapshot['checks']:
                    if not check['passed']:
                        prefix = 'domain_error' if check['severity'] == 'error' else 'domain_warning'
                        aggregated_issues.append(f"{prefix}:{check['name']}")

            if not aggregated_issues:
                break

            fixes_applied = self._fix_validation_issues(scene, aggregated_issues)
            iteration_info['fixes'] = fixes_applied
            validation_results['refinement_trace'].append(iteration_info)
            validation_results['refinement_iterations'] = len(validation_results['refinement_trace'])

            if fixes_applied == 0:
                break

            svg_output = self.renderer.render(scene, spec)
            if quality_score and quality_score.overall_score >= min_score:
                break

        # VLM validation
        vlm_description = None
        if self.vlm_validator and svg_output:
            try:
                vlm_result = self.vlm_validator.validate_diagram(svg_output, problem_text, {
                    'object_count': len(scene.objects)
                })
                vlm_description = vlm_result.description
                validation_results['visual_semantic'] = {
                    'confidence': vlm_result.confidence,
                    'discrepancies': vlm_result.discrepancies,
                    'description': vlm_description
                }
            except Exception as exc:
                if self.logger:
                    self.logger.log_phase_detail(f"VLM validation error: {exc}")

        validation_results['vlm_description'] = vlm_description

        # DeepSeek semantic fidelity
        if self.deepseek_client and self.config.enable_deepseek_validation and svg_output:
            try:
                if not vlm_description:
                    vlm_description = f"SVG diagram with {len(scene.objects)} objects"
                fidelity_result = self.deepseek_client.validate_semantic_fidelity(
                    original_request=problem_text,
                    diagram_description=vlm_description,
                    svg_output=svg_output
                )
                validation_results['semantic_fidelity'] = fidelity_result
            except Exception as exc:
                if self.logger:
                    self.logger.log_phase_detail(f"DeepSeek validation error: {exc}")

        validation_results.setdefault('refinement_iterations', len(validation_results['refinement_trace']))
        return validation_results, svg_output

    def _fix_validation_issues(self, scene: Scene, issues: List) -> int:
        """Fix common validation issues (helper method)"""
        fixed = 0

        for issue in issues:
            issue_str = str(issue).lower()

            # Fix overlapping objects
            if 'overlap' in issue_str:
                # Simple fix: add small offset to overlapping objects
                for i, obj in enumerate(scene.objects):
                    if obj.position and i > 0:
                        obj.position.x += (i % 3) * 10  # Slight offset
                        obj.position.y += (i // 3) * 10
                fixed += 1

            # Fix unreadable labels
            elif 'label' in issue_str and 'unreadable' in issue_str:
                # Increase label offset
                for obj in scene.objects:
                    if obj.label_position:
                        obj.label_position.y -= 10  # Move label up
                fixed += 1

        return fixed

    def _next_request_id(self) -> str:
        """Generate monotonic request identifier"""
        self._request_counter += 1
        timestamp = int(time.time() * 1000)
        return f"req_{timestamp}_{self._request_counter}"

    @staticmethod
    def _compose_result_metadata(
        *,
        trace: Dict[str, Any],
        domain: Optional[PhysicsDomain],
        scene: Scene,
        features: List[str],
        request_id: str,
        structural_report: Optional[Dict[str, Any]] = None,
        domain_rule_report: Optional[Dict[str, Any]] = None,
        validation_results: Optional[Dict[str, Any]] = None,
        ontology_validation: Optional[Dict[str, Any]] = None,
        audit_report: Optional[Dict[str, Any]] = None,
        vlm_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compose rich metadata payload for DiagramResult"""
        metadata: Dict[str, Any] = {
            'trace': trace,
            'domain': domain.value if isinstance(domain, PhysicsDomain) else (domain or 'unknown'),
            'total_objects': len(scene.objects),
            'advanced_features_used': features,
            'request_id': request_id
        }

        if structural_report:
            metadata['structural_report'] = structural_report
        if domain_rule_report:
            metadata['domain_rule_report'] = domain_rule_report
        if validation_results:
            metadata['validation_results'] = validation_results
        if ontology_validation:
            metadata['ontology_validation'] = ontology_validation
        if audit_report:
            metadata['audit_report'] = audit_report
        if vlm_description:
            metadata['vlm_description'] = vlm_description

        return metadata

    def _persist_property_graph(self, property_graph: Optional['PropertyGraph'], request_id: str) -> Dict[str, Any]:
        """Persist property graph to disk and optional graph database"""
        result: Dict[str, Any] = {}
        if not property_graph:
            return result

        if getattr(self.config, 'property_graph_persist_to_disk', False):
            disk_info: Dict[str, Any] = {'status': 'skipped'}
            try:
                dump_dir = Path(getattr(self.config, 'property_graph_dump_dir', self.config.output_dir))
                dump_dir.mkdir(parents=True, exist_ok=True)
                output_path = dump_dir / f"{request_id}_property_graph.json"
                property_graph.to_json(str(output_path))
                disk_info = {
                    'status': 'success',
                    'path': str(output_path)
                }
            except Exception as exc:
                disk_info = {
                    'status': 'error',
                    'error': str(exc)
                }
            result['disk_persistence'] = disk_info

        backend = getattr(self.config, 'property_graph_graphdb_backend', None)
        uri = getattr(self.config, 'property_graph_graphdb_uri', None)

        if backend and uri:
            backend = backend.lower()
            if backend == 'neo4j':
                graphdb_info = self._persist_graph_to_neo4j(property_graph, request_id)
            elif backend == 'arango':
                graphdb_info = self._persist_graph_to_arango(property_graph, request_id)
            else:
                graphdb_info = {
                    'status': 'skipped',
                    'reason': f'Unknown backend "{backend}"'
                }
            result['graphdb_persistence'] = graphdb_info

        return result

    def _persist_graph_to_neo4j(self, property_graph: 'PropertyGraph', request_id: str) -> Dict[str, Any]:
        """Persist graph to Neo4j if driver is available"""
        if not NEO4J_AVAILABLE:
            return {'status': 'skipped', 'reason': 'neo4j driver not installed'}

        uri = self.config.property_graph_graphdb_uri
        username = self.config.property_graph_graphdb_username
        password = self.config.property_graph_graphdb_password
        database = self.config.property_graph_graphdb_database

        auth = None
        if username:
            auth = (username, password or "")

        driver = None
        try:
            driver = GraphDatabase.driver(uri, auth=auth)

            def _clear_existing(tx):
                tx.run(
                    "MATCH (n:DiagramNode {request_id: $request_id}) DETACH DELETE n",
                    request_id=request_id
                )

            def _merge_node(tx, node: 'GraphNode'):
                tx.run(
                    """
                    MERGE (n:DiagramNode {request_id: $request_id, node_id: $node_id})
                    SET n += $props
                    """,
                    request_id=request_id,
                    node_id=node.id,
                    props={
                        'label': node.label,
                        'type': node.type.value if hasattr(node.type, 'value') else str(node.type),
                        'properties': node.properties,
                        'metadata': node.metadata
                    }
                )

            def _merge_edge(tx, edge: 'GraphEdge'):
                tx.run(
                    """
                    MATCH (source:DiagramNode {request_id: $request_id, node_id: $source_id})
                    MATCH (target:DiagramNode {request_id: $request_id, node_id: $target_id})
                    MERGE (source)-[r:DIAGRAM_RELATION {
                        request_id: $request_id,
                        relation_id: $relation_id
                    }]->(target)
                    SET r += $props
                    """,
                    request_id=request_id,
                    source_id=edge.source,
                    target_id=edge.target,
                    relation_id=f"{edge.source}->{edge.target}:{edge.label}",
                    props={
                        'type': edge.type.value if hasattr(edge.type, 'value') else str(edge.type),
                        'label': edge.label,
                        'properties': edge.properties,
                        'metadata': edge.metadata,
                        'confidence': edge.confidence
                    }
                )

            with driver.session(database=database) if database else driver.session() as session:
                session.write_transaction(_clear_existing)
                for node in property_graph.get_all_nodes():
                    session.write_transaction(_merge_node, node)
                for edge in property_graph.get_edges():
                    session.write_transaction(_merge_edge, edge)

            return {
                'status': 'success',
                'backend': 'neo4j',
                'nodes_synced': len(property_graph.get_all_nodes()),
                'edges_synced': len(property_graph.get_edges())
            }
        except Exception as exc:
            return {
                'status': 'error',
                'backend': 'neo4j',
                'reason': str(exc)
            }
        finally:
            if driver:
                driver.close()

    def _persist_graph_to_arango(self, property_graph: 'PropertyGraph', request_id: str) -> Dict[str, Any]:
        """Persist graph to ArangoDB if python-arango is available"""
        if not ARANGO_AVAILABLE:
            return {'status': 'skipped', 'reason': 'python-arango not installed'}

        uri = self.config.property_graph_graphdb_uri
        username = self.config.property_graph_graphdb_username
        password = self.config.property_graph_graphdb_password
        database = self.config.property_graph_graphdb_database or "_system"
        collection_base = getattr(self.config, 'property_graph_graphdb_collection', 'diagram_property_graphs')

        try:
            client = ArangoClient(hosts=uri)
            db = client.db(database, username=username, password=password, verify=True)

            vertex_collection_name = f"{collection_base}_nodes"
            edge_collection_name = f"{collection_base}_edges"

            if not db.has_collection(vertex_collection_name):
                db.create_collection(vertex_collection_name)
            if not db.has_collection(edge_collection_name):
                db.create_collection(edge_collection_name, edge=True)

            vertex_coll = db.collection(vertex_collection_name)
            edge_coll = db.collection(edge_collection_name)

            node_count = 0
            edge_count = 0

            for node in property_graph.get_all_nodes():
                doc_key = f"{request_id}_{node.id}"
                vertex_coll.insert({
                    '_key': doc_key,
                    'request_id': request_id,
                    'original_id': node.id,
                    'label': node.label,
                    'type': node.type.value if hasattr(node.type, 'value') else str(node.type),
                    'properties': node.properties,
                    'metadata': node.metadata
                }, overwrite=True)
                node_count += 1

            for idx, edge in enumerate(property_graph.get_edges()):
                edge_key = f"{request_id}_{idx}"
                edge_coll.insert({
                    '_key': edge_key,
                    '_from': f"{vertex_collection_name}/{request_id}_{edge.source}",
                    '_to': f"{vertex_collection_name}/{request_id}_{edge.target}",
                    'request_id': request_id,
                    'type': edge.type.value if hasattr(edge.type, 'value') else str(edge.type),
                    'label': edge.label,
                    'properties': edge.properties,
                    'metadata': edge.metadata,
                    'confidence': edge.confidence
                }, overwrite=True)
                edge_count += 1

            return {
                'status': 'success',
                'backend': 'arango',
                'nodes_synced': node_count,
                'edges_synced': edge_count
            }
        except Exception as exc:
            return {
                'status': 'error',
                'backend': 'arango',
                'reason': str(exc)
            }

    def _build_ontology_keyword_index(self) -> Dict[str, Dict[str, str]]:
        """Build lightweight keyword -> ontology URI map for enrichment"""
        return {
            'force': {'namespace': 'physh', 'uri': 'https://physh.aps.org/terms/force', 'label': 'Force'},
            'electric field': {'namespace': 'physh', 'uri': 'https://physh.aps.org/terms/electric_field', 'label': 'Electric Field'},
            'dielectric': {'namespace': 'physh', 'uri': 'https://physh.aps.org/terms/dielectrics', 'label': 'Dielectric Material'},
            'capacitor': {'namespace': 'physh', 'uri': 'https://physh.aps.org/terms/capacitors', 'label': 'Capacitor'},
            'benzene': {'namespace': 'chebi', 'uri': 'CHEBI:16716', 'label': 'Benzene'},
            'ethanol': {'namespace': 'chebi', 'uri': 'CHEBI:16236', 'label': 'Ethanol'},
            'sodium chloride': {'namespace': 'chebi', 'uri': 'CHEBI:26710', 'label': 'Sodium chloride'},
            'glucose': {'namespace': 'go', 'uri': 'GO:0006006', 'label': 'Glucose metabolic process'},
            'photosynthesis': {'namespace': 'go', 'uri': 'GO:0015979', 'label': 'Photosynthesis'},
            'chlorophyll': {'namespace': 'go', 'uri': 'GO:0015995', 'label': 'Chlorophyll biosynthetic process'}
        }

    def _enrich_property_graph_with_ontologies(self, property_graph: Optional['PropertyGraph']) -> Dict[str, int]:
        """Annotate property graph nodes with ontology metadata"""
        if not property_graph or not self._ontology_keyword_index:
            return {}
        enrichment_counts: Dict[str, int] = {}

        for node in property_graph.get_all_nodes():
            label_lower = node.label.lower()
            matched_entries = []
            for keyword, info in self._ontology_keyword_index.items():
                if keyword in label_lower:
                    matched_entries.append(info)

            if not matched_entries:
                continue

            existing = node.metadata.get('ontologies', [])
            for entry in matched_entries:
                if not any(o.get('uri') == entry['uri'] for o in existing):
                    existing.append({
                        'namespace': entry['namespace'],
                        'uri': entry['uri'],
                        'label': entry['label']
                    })
                    enrichment_counts[entry['namespace']] = enrichment_counts.get(entry['namespace'], 0) + 1

            node.metadata['ontologies'] = existing
            if hasattr(property_graph, 'merge_node_metadata'):
                property_graph.merge_node_metadata(node.id, {'ontologies': existing})

        return enrichment_counts

    def _run_property_graph_gap_queries(self, property_graph: Optional['PropertyGraph']) -> Dict[str, Any]:
        """Run predefined gap analysis queries against property graph"""
        if not property_graph or not hasattr(property_graph, 'find_nodes_missing_property'):
            return {}

        gap_report: Dict[str, Any] = {}

        missing_units = property_graph.find_nodes_missing_property('unit', node_type=NodeType.QUANTITY)
        if missing_units:
            gap_report['missing_units'] = {
                'count': len(missing_units),
                'nodes': [node.id for node in missing_units]
            }

        dielectric_missing = property_graph.find_nodes_missing_property('kappa', label_contains='dielectric')
        if dielectric_missing:
            gap_report['dielectric_missing_kappa'] = {
                'count': len(dielectric_missing),
                'nodes': [node.id for node in dielectric_missing]
            }

        return gap_report

    def _infer_domain_from_graph(self, property_graph) -> Optional[str]:
        """
        Infer domain from property graph node labels and types

        Returns domain hint string (e.g., 'electronics', 'mechanics')
        """
        from core.property_graph import PropertyGraph

        # Collect all node labels
        all_nodes = property_graph.get_all_nodes()
        labels = [node.label.lower() for node in all_nodes]
        combined_text = ' '.join(labels)

        # Domain indicators
        electronics_keywords = ['battery', 'resistor', 'capacitor', 'inductor', 'switch',
                              'circuit', 'voltage', 'current', 'led', 'transistor', 'diode']
        mechanics_keywords = ['mass', 'spring', 'pulley', 'force', 'weight', 'friction',
                            'acceleration', 'velocity', 'block', 'rope', 'incline']
        chemistry_keywords = ['molecule', 'atom', 'bond', 'reaction', 'element', 'compound',
                            'ion', 'formula', 'chemical']
        biology_keywords = ['cell', 'organ', 'tissue', 'protein', 'dna', 'membrane',
                          'enzyme', 'nucleus', 'mitochondria']
        geometry_keywords = ['triangle', 'circle', 'angle', 'line', 'point', 'polygon',
                           'rectangle', 'square']

        # Count domain indicators
        electronics_score = sum(1 for kw in electronics_keywords if kw in combined_text)
        mechanics_score = sum(1 for kw in mechanics_keywords if kw in combined_text)
        chemistry_score = sum(1 for kw in chemistry_keywords if kw in combined_text)
        biology_score = sum(1 for kw in biology_keywords if kw in combined_text)
        geometry_score = sum(1 for kw in geometry_keywords if kw in combined_text)

        # Select domain with highest score
        scores = {
            'electronics': electronics_score,
            'mechanics': mechanics_score,
            'chemistry': chemistry_score,
            'biology': biology_score,
            'geometry': geometry_score
        }

        max_domain = max(scores.items(), key=lambda x: x[1])

        if max_domain[1] > 0:
            return max_domain[0]
        else:
            return None  # Unknown domain

    def _extract_quantities_from_text(self, text: Optional[str]) -> List[Dict[str, Any]]:
        """Parse raw text for canonical quantities and linked components."""

        if not text:
            return []

        measurements: List[Dict[str, Any]] = []
        seen_keys = set()

        def _register(entry: Dict[str, Any]) -> None:
            key = (entry['quantity_id'], entry['value'], entry.get('unit_base'))
            if key in seen_keys:
                return
            seen_keys.add(key)
            measurements.append(entry)

        # Explicit symbolic assignments (e.g., "C₁ = 2.00 μF")
        for match in self._TEXT_ASSIGNMENT_PATTERN.finditer(text):
            unit_info = self._parse_unit_token(match.group('unit'))
            if not unit_info:
                continue

            try:
                raw_value = float(match.group('value'))
            except ValueError:
                continue

            symbol = self._normalize_symbol_token(match.group('symbol'))
            if not symbol:
                continue

            quantity_type = unit_info.get('quantity', 'quantity')
            slug = self._slugify(symbol)
            quantity_id = f"{quantity_type}_{slug}"
            component_hint = unit_info.get('component_hint')

            component_id = None
            component_label = None
            component_type = None
            if component_hint:
                component_id = f"{component_hint}_{slug}"
                pretty_symbol = symbol.upper()
                component_label = f"{component_hint.replace('_', ' ').title()} {pretty_symbol}".strip()
                component_type = component_hint

            entry = {
                'symbol': symbol,
                'raw_text': match.group(0).strip(),
                'quantity_type': quantity_type,
                'quantity_label': f"{quantity_type.replace('_', ' ').title()} {symbol.upper()}".strip(),
                'quantity_id': quantity_id,
                'component_id': component_id,
                'component_label': component_label or (component_id or symbol.upper()),
                'component_type': component_type,
                'unit_display': unit_info.get('unit_display', match.group('unit').strip()),
                'unit_base': unit_info.get('base_unit'),
                'value': raw_value,
                'value_si': raw_value * unit_info.get('scale', 1.0),
                'confidence': 0.97
            }
            _register(entry)

        # Narrative quantities (e.g., "potential difference of 300 V")
        for match in self._TEXT_QUANTITY_PATTERN.finditer(text):
            label = match.group('label').strip()
            normalized_label = re.sub(r'^(?:a|an|the)\s+', '', label, flags=re.IGNORECASE).lower()
            keyword_info = self._match_quantity_keyword(normalized_label)
            if not keyword_info:
                continue

            unit_info = self._parse_unit_token(match.group('unit'))
            if not unit_info:
                continue

            try:
                raw_value = float(match.group('value'))
            except ValueError:
                continue

            quantity_type = keyword_info.get('quantity') or unit_info.get('quantity') or 'quantity'
            slug = self._slugify(normalized_label)
            quantity_id = f"{quantity_type}_{slug}"

            component_hint = keyword_info.get('component_hint') or unit_info.get('component_hint')
            component_id = None
            component_label = None
            component_type = None
            if component_hint:
                component_id = f"{component_hint}_{slug}"
                component_label = component_hint.replace('_', ' ').title()
                component_type = component_hint

            entry = {
                'symbol': normalized_label,
                'raw_text': match.group(0).strip(),
                'quantity_type': quantity_type,
                'quantity_label': normalized_label.replace('_', ' ').title(),
                'quantity_id': quantity_id,
                'component_id': component_id,
                'component_label': component_label or normalized_label.title(),
                'component_type': component_type,
                'unit_display': unit_info.get('unit_display', match.group('unit').strip()),
                'unit_base': unit_info.get('base_unit'),
                'value': raw_value,
                'value_si': raw_value * unit_info.get('scale', 1.0),
                'confidence': 0.9
            }
            _register(entry)

        return measurements

    def _normalize_symbol_token(self, token: Optional[str]) -> str:
        if not token:
            return ''
        normalized = token.translate(self._SUBSCRIPT_TRANSLATION)
        normalized = re.sub(r'\s+', '', normalized)
        return normalized.strip()

    def _parse_unit_token(self, unit_token: Optional[str]) -> Optional[Dict[str, Any]]:
        if not unit_token:
            return None

        cleaned = unit_token.strip()
        if not cleaned:
            return None

        normalized = cleaned.replace('µ', 'μ')
        normalized = normalized.replace('μ', 'U')
        normalized = normalized.replace('Ω', 'OHM').replace('Ω', 'OHM')
        normalized = re.sub(r'\s+', '', normalized)
        normalized = normalized.upper()

        if normalized in self._UNIT_BASE_MAP:
            info = self._UNIT_BASE_MAP[normalized].copy()
            info.update({'base_unit': normalized, 'scale': 1.0, 'unit_display': cleaned})
            return info

        if len(normalized) > 1 and normalized[0] in self._UNIT_PREFIX_SCALES:
            prefix = normalized[0]
            remainder = normalized[1:]
            if remainder in self._UNIT_BASE_MAP:
                info = self._UNIT_BASE_MAP[remainder].copy()
                info.update({
                    'base_unit': remainder,
                    'scale': self._UNIT_PREFIX_SCALES[prefix],
                    'prefix': prefix,
                    'unit_display': cleaned
                })
                return info

        return None

    def _slugify(self, value: str) -> str:
        slug = re.sub(r'[^a-z0-9]+', '_', value.lower())
        slug = slug.strip('_')
        return slug or 'value'

    def _match_quantity_keyword(self, label: str) -> Optional[Dict[str, Any]]:
        lookup = label.strip()
        if lookup in self._QUANTITY_KEYWORDS:
            return self._QUANTITY_KEYWORDS[lookup]

        for keyword, info in self._QUANTITY_KEYWORDS.items():
            if keyword in lookup:
                return info

        return None

    def _diagram_plan_to_canonical_spec(self, diagram_plan) -> CanonicalProblemSpec:
        """
        Convert DiagramPlan to CanonicalProblemSpec for backward compatibility

        This allows the rest of the pipeline to work with the new property-graph-driven
        planning while maintaining compatibility with existing scene builder and
        renderer code.
        """
        from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain

        # Extract domain from metadata or infer from entities
        domain_hint = diagram_plan.metadata.get('domain_hint') if hasattr(diagram_plan, 'metadata') else None

        if domain_hint:
            # Map domain hint string to PhysicsDomain enum
            domain_map = {
                'electronics': PhysicsDomain.CURRENT_ELECTRICITY,
                'mechanics': PhysicsDomain.MECHANICS,
                'chemistry': PhysicsDomain.THERMODYNAMICS,  # Approximate
                'biology': PhysicsDomain.MECHANICS,  # Approximate
                'geometry': PhysicsDomain.MECHANICS  # Approximate
            }
            domain = domain_map.get(domain_hint, PhysicsDomain.MECHANICS)
        else:
            domain = PhysicsDomain.MECHANICS  # Default

        layout_hints = getattr(diagram_plan, 'layout_hints', {}) if diagram_plan else {}
        style_hints = getattr(diagram_plan, 'style_hints', {}) if diagram_plan else {}
        positions = layout_hints.get('positions', {}) if isinstance(layout_hints, dict) else {}

        # Convert extracted entities to objects
        objects = []
        if hasattr(diagram_plan, 'extracted_entities'):
            for entity in diagram_plan.extracted_entities:
                entity_id = entity['id']
                obj = {
                    'id': entity_id,
                    'type': entity['type'],
                    'label': entity['label'],
                    'properties': entity.get('properties', {}),
                    'primitive_hint': entity.get('primitive_hint')
                }
                if entity_id in positions:
                    coords = positions[entity_id]
                    if isinstance(coords, dict):
                        obj['layout_hint'] = coords
                    else:
                        obj['layout_hint'] = {
                            'x': coords[0],
                            'y': coords[1],
                            'anchor': 'center'
                        }
                if entity_id in style_hints:
                    obj['style_hint'] = style_hints[entity_id]
                objects.append(obj)

        # Convert extracted relations to relationships
        relationships = []
        if hasattr(diagram_plan, 'extracted_relations'):
            for relation in diagram_plan.extracted_relations:
                rel = {
                    'source': relation['source_id'],
                    'target': relation['target_id'],
                    'type': relation['type'],
                    'label': relation.get('label', '')
                }
                relationships.append(rel)

        # Convert constraints
        constraints = []
        if hasattr(diagram_plan, 'global_constraints'):
            for constraint in diagram_plan.global_constraints:
                cons = {
                    'type': constraint.type,
                    'objects': constraint.objects,
                    'parameters': constraint.parameters,
                    'priority': constraint.priority.value if hasattr(constraint.priority, 'value') else str(constraint.priority)
                }
                constraints.append(cons)

        # Create CanonicalProblemSpec
        spec = CanonicalProblemSpec(
            domain=domain,
            problem_type='diagram_generation',
            problem_text=diagram_plan.metadata.get('original_request', '') if hasattr(diagram_plan, 'metadata') else '',
            objects=objects,
            relationships=relationships,
            constraints=constraints,
            complexity_score=diagram_plan.complexity_score if hasattr(diagram_plan, 'complexity_score') else 0.0
        )

        # Store reference to diagram plan for access by other components
        spec.diagram_plan = diagram_plan
        spec.diagram_plan_metadata = {
            'layout_hints': layout_hints,
            'style_hints': style_hints,
            'planning_trace': getattr(diagram_plan, 'planning_trace', []),
            'strategy': diagram_plan.strategy.value if hasattr(diagram_plan, 'strategy') else None
        }
        if not spec.geometry:
            spec.geometry = {}
        spec.geometry.setdefault('layout_hints', layout_hints)
        spec.geometry.setdefault('style_hints', style_hints)

        return spec

    def _apply_z3_layout(self, plan, scene) -> Tuple[int, bool]:
        """Apply Z3 layout positions using existing solver"""
        if not self.z3_solver or not plan or not plan.global_constraints:
            return 0, False
        try:
            object_dims = self._compute_object_dimensions(scene)
            solution = self.z3_solver.solve_layout(plan, object_dims)
            if solution and getattr(solution, 'satisfiable', False):
                self._apply_positions_to_scene(scene, solution.positions)
                return len(solution.positions), True
        except Exception as exc:
            if self.logger:
                self.logger.log_phase_detail(f"Z3 layout error: {exc}")
        return 0, False

    def _apply_sympy_layout(self, plan, scene) -> Tuple[int, bool]:
        """Apply SymPy-based layout if available"""
        if not self.config.enable_sympy_solver or not plan:
            return 0, False
        try:
            from core.sympy_solver import SymPyLayoutSolver
        except ImportError:
            return 0, False

        constraint_payload = self._convert_constraints_for_sympy(plan)
        if not constraint_payload:
            return 0, False

        try:
            solver = SymPyLayoutSolver()
            solution = solver.solve_geometric_constraints(
                constraints=constraint_payload,
                object_ids=[obj.id for obj in scene.objects]
            )
            positions = self._sympy_solution_to_positions(solution)
            if positions:
                self._apply_positions_to_scene(scene, positions)
                return len(positions), solution.satisfiable
        except Exception as exc:
            if self.logger:
                self.logger.log_phase_detail(f"SymPy layout error: {exc}")
        return 0, False

    def _compute_object_dimensions(self, scene: Scene) -> Dict[str, Tuple[float, float]]:
        """Estimate object dimensions for solver usage"""
        dimensions: Dict[str, Tuple[float, float]] = {}
        for obj in scene.objects:
            obj_type = getattr(obj, 'type', getattr(obj, 'primitive_type', None))
            width = obj.properties.get('width')
            height = obj.properties.get('height')
            if width is None or height is None:
                if obj_type == PrimitiveType.CIRCLE or (isinstance(obj_type, str) and 'circle' in obj_type.lower()):
                    radius = obj.properties.get('radius', 50)
                    width = height = radius * 2
                elif obj_type == PrimitiveType.RECTANGLE or (isinstance(obj_type, str) and 'rect' in obj_type.lower()):
                    width = obj.properties.get('width', 120)
                    height = obj.properties.get('height', 80)
                else:
                    width = 100
                    height = 100
            dimensions[obj.id] = (float(width), float(height))
        return dimensions

    def _apply_positions_to_scene(self, scene: Scene, positions: Dict[str, Tuple[float, float]]) -> None:
        """Apply computed positions to scene objects"""
        for obj_id, coords in (positions or {}).items():
            obj = next((o for o in scene.objects if o.id == obj_id), None)
            if not obj:
                continue
            if isinstance(coords, dict):
                x = coords.get('x')
                y = coords.get('y')
            else:
                x, y = coords
            if x is None or y is None:
                continue
            obj.position = Position(x=float(x), y=float(y)).to_dict()

    def _convert_constraints_for_sympy(self, plan) -> List[Dict[str, Any]]:
        """Convert DiagramPlan constraints + hints into SymPy-friendly format"""
        constraints: List[Dict[str, Any]] = []
        for constraint in getattr(plan, 'global_constraints', []) or []:
            ctype = str(getattr(constraint, 'type', '')).lower()
            objs = list(getattr(constraint, 'objects', []) or [])
            params = getattr(constraint, 'parameters', {}) or {}

            if ctype == 'distance' and len(objs) >= 2:
                distance = params.get('distance') or params.get('value') or 100.0
                constraints.append({
                    'type': 'DISTANCE',
                    'object1': objs[0],
                    'object2': objs[1],
                    'distance': float(distance)
                })
            elif ctype in ('alignment_horizontal', 'aligned_h') and len(objs) >= 2:
                constraints.append({
                    'type': 'ALIGN_HORIZONTAL',
                    'object1': objs[0],
                    'object2': objs[1]
                })
            elif ctype in ('alignment_vertical', 'aligned_v') and len(objs) >= 2:
                constraints.append({
                    'type': 'ALIGN_VERTICAL',
                    'object1': objs[0],
                    'object2': objs[1]
                })

        # Include fixed layout hints if provided
        hints = getattr(plan, 'layout_hints', {}) or {}
        for obj_id, coords in hints.get('positions', {}).items():
            if isinstance(coords, dict):
                x = coords.get('x')
                y = coords.get('y')
            elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                x, y = coords[0], coords[1]
            else:
                continue
            if x is None or y is None:
                continue
            constraints.append({
                'type': 'FIXED_POSITION',
                'object': obj_id,
                'x': float(x),
                'y': float(y)
            })

        return constraints

    def _sympy_solution_to_positions(self, solution) -> Dict[str, Tuple[float, float]]:
        """Convert SymPy solution variables into position tuples"""
        positions: Dict[str, List[Optional[float]]] = {}
        for var_name, value in getattr(solution, 'variables', {}).items():
            if not isinstance(var_name, str):
                continue
            if not isinstance(value, (int, float)):
                continue
            if var_name.endswith('_x'):
                obj_id = var_name[:-2]
                positions.setdefault(obj_id, [None, None])[0] = float(value)
            elif var_name.endswith('_y'):
                obj_id = var_name[:-2]
                positions.setdefault(obj_id, [None, None])[1] = float(value)

        finalized: Dict[str, Tuple[float, float]] = {}
        for obj_id, (x, y) in positions.items():
            if x is not None and y is not None:
                finalized[obj_id] = (x, y)
        return finalized

    def _build_domain_modules(self, domain: Optional[str], diagram_plan, spec, property_graph) -> List[Dict[str, Any]]:
        """Invoke pluggable domain modules and return serialized artifacts"""
        if not self.domain_module_registry or not diagram_plan or not domain:
            return []
        artifacts = self.domain_module_registry.build_artifacts(
            domain=domain,
            diagram_plan=diagram_plan,
            spec=spec,
            property_graph=property_graph
        )
        return [artifact.to_dict() for artifact in artifacts]
