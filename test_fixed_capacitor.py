"""
Test script for fixed capacitor positioning
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# Create test problem with three-dielectric capacitor
problem = """
A parallel-plate capacitor has three dielectric regions:
- Left half: dielectric constant κ₁ = 2.5
- Right top half: dielectric constant κ₂ = 4.0
- Right bottom half: dielectric constant κ₃ = 1.5
"""

# Configure pipeline - ENABLE ALL ADVANCED FEATURES
config = PipelineConfig()
config.output_dir = "output_test"
config.validation_mode = "warn"  # Warn only, don't fail on validation errors

# ENABLE ALL ADVANCED FEATURES AS REQUESTED
config.nlp_tools = ['spacy']  # Enable NLP tools
config.enable_property_graph = True  # Enable property graph
config.enable_nlp_enrichment = True  # Enable NLP enrichment
config.enable_z3_optimization = False  # Temporarily disabled - Z3 not installed
config.enable_llm_planning = True  # Enable LLM planning
config.enable_llm_auditing = True  # Enable LLM auditing
config.enable_ontology_validation = True  # Enable ontology validation
config.enable_model_orchestration = True  # Enable model orchestration

# Run pipeline
print("="*80)
print("Testing Fixed Capacitor Positioning")
print("="*80)

pipeline = UnifiedDiagramPipeline(config)

try:
    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("TEST RESULT:")
    print("="*80)

    if result:
        print(f"✅ Diagram generated successfully!")

        # Save the SVG
        output_file = "output_test/capacitor_fixed.svg"
        result.save_svg(output_file)

        print(f"\n📊 Scene objects created:")
        for obj in result.scene.objects:
            print(f"   - {obj.id}: {obj.type.value}")
            if obj.position:
                print(f"     Position: x={obj.position.get('x', 0):.1f}, y={obj.position.get('y', 0):.1f}")
                print(f"     Anchor: {obj.position.get('anchor', 'N/A')}")
            else:
                print(f"     Position: NONE (will be auto-placed)")
            if hasattr(obj, 'layer'):
                print(f"     Layer: {obj.layer.name}")
    else:
        print(f"❌ Generation failed!")

    print("="*80)

except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()
