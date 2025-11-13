"""
Debug script to track position changes through the pipeline
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# Create test problem
problem = """
A parallel-plate capacitor has three dielectric regions:
- Left half: dielectric constant κ₁ = 2.5
- Right top half: dielectric constant κ₂ = 4.0
- Right bottom half: dielectric constant κ₃ = 1.5
"""

# Configure pipeline - minimal features for debugging
config = PipelineConfig()
config.output_dir = "output_test"
config.validation_mode = "warn"
config.nlp_tools = []  # Disable to reduce noise
config.enable_property_graph = False
config.enable_nlp_enrichment = False
config.enable_z3_optimization = False
config.enable_llm_planning = False
config.enable_llm_auditing = False
config.enable_ontology_validation = False
config.enable_model_orchestration = False

pipeline = UnifiedDiagramPipeline(config)

# Get components
analyzer = pipeline.ai_analyzer
scene_builder = pipeline.scene_builder
layout_engine = pipeline.layout_engine

# Phase 1: Analyze
print("\n" + "="*80)
print("PHASE 1: ANALYSIS")
print("="*80)
spec = analyzer.analyze(problem)

# Phase 2: Build Scene
print("\n" + "="*80)
print("PHASE 2: SCENE BUILDING")
print("="*80)
scene = scene_builder.build_scene(spec)

print("\nPositions BEFORE layout engine:")
for obj in scene.objects:
    if 'plate' in obj.id or 'dielectric' in obj.id:
        pos = obj.position if obj.position else "None"
        print(f"  {obj.id}: {pos}")

# Phase 3: Layout
print("\n" + "="*80)
print("PHASE 3: LAYOUT ENGINE")
print("="*80)
scene = layout_engine.solve(scene, spec)

print("\nPositions AFTER layout engine:")
for obj in scene.objects:
    if 'plate' in obj.id or 'dielectric' in obj.id:
        if obj.position:
            print(f"  {obj.id}: x={obj.position.get('x', 0):.1f}, y={obj.position.get('y', 0):.1f}")
        else:
            print(f"  {obj.id}: None")

print("\n" + "="*80)
print("DONE")
print("="*80)
