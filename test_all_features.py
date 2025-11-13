"""
Test script to verify ALL features are enabled and active
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import os
from pathlib import Path

# Simple test problem
problem = """
A parallel-plate capacitor has charge q and plate area A.
The plates are separated by distance x.
"""

# Configure pipeline with ALL features enabled
config = PipelineConfig()
config.output_dir = "output_test_all"
config.log_dir = "logs"
config.enable_logging = True
config.log_level = "INFO"
config.validation_mode = "warn"

# ENABLE ALL AVAILABLE FEATURES
config.enable_property_graph = True
config.enable_nlp_enrichment = True  # ✅ ENABLED! Full NLP stack with error handling
config.enable_complexity_assessment = True  # DiagramPlanner Phase 1 ⭐
config.enable_strategic_planning = True  # DiagramPlanner Phase 2 ⭐
config.enable_z3_optimization = True  # ✅ Z3 installed - ENABLED!
config.enable_llm_planning = False  # Disabled for now
config.enable_llm_auditing = False  # Disabled for now
config.enable_ontology_validation = True  # ✅ RDFLib installed - ENABLED!

# All 7 NLP tools enabled (with error handling for tools that fail)
# Working: OpenIE, Stanza ✅, SciBERT ✅, ChemDataExtractor, MathBERT, AMR (6/7)
# Not working: DyGIE++ (Python 3.13 incompatibility)
config.nlp_tools = ['openie', 'stanza', 'dygie', 'scibert', 'chemdataextractor', 'mathbert', 'amr']

print("="*80)
print("Testing ALL FEATURES ENABLED")
print("="*80)

# Run pipeline
pipeline = UnifiedDiagramPipeline(config)

print("\n" + "="*80)
print("INITIALIZATION COMPLETE - Active Features:")
print("="*80)
for feature in pipeline.active_features:
    print(f"  ✓ {feature}")
print()

try:
    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ TEST PASSED - Diagram generated successfully!")
    print("="*80)

    # Check that log files were created
    log_dir = Path(config.log_dir)
    if log_dir.exists():
        log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        trace_files = sorted(log_dir.glob("*_trace.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        if log_files:
            print(f"\n✅ Log file created: {log_files[0]}")
        if trace_files:
            print(f"✅ Trace file created: {trace_files[0]}")

            # Verify trace contains DiagramPlanner output
            import json
            with open(trace_files[0], 'r') as f:
                trace = json.load(f)

            print(f"\n{'='*80}")
            print("TRACE VERIFICATION")
            print(f"{'='*80}")

            for phase in trace['phases']:
                phase_name = phase['phase_name']
                output = phase.get('output', {})

                if 'Complexity' in phase_name:
                    complexity = output.get('complexity_score')
                    print(f"✓ Phase: {phase_name}")
                    print(f"  - Complexity Score: {complexity} (type: {type(complexity).__name__})")
                    if complexity is None:
                        print(f"  ❌ WARNING: Complexity score is None!")

                if 'Strategic Planning' in phase_name or 'Scene Synthesis' in phase_name:
                    strategy = output.get('selected_strategy')
                    print(f"✓ Phase: {phase_name}")
                    print(f"  - Selected Strategy: {strategy}")
                    if strategy is None or str(strategy).upper() == 'NONE':
                        print(f"  ❌ WARNING: Strategy is None!")

                if 'NLP' in phase_name:
                    print(f"✓ Phase: {phase_name}")
                    tool_count = len(output)
                    print(f"  - NLP tools with output: {tool_count}")
                    if tool_count > 0:
                        print(f"  - Tools: {', '.join(output.keys())}")
                        for tool_name in output.keys():
                            print(f"    • {tool_name}")
                    else:
                        print(f"  ❌ WARNING: No NLP tools produced output!")

                if 'Property Graph' in phase_name:
                    nodes = output.get('nodes', 0)
                    edges = output.get('edges', 0)
                    print(f"✓ Phase: {phase_name}")
                    print(f"  - Nodes: {nodes}, Edges: {edges}")

                if 'Z3' in phase_name or 'Layout' in phase_name:
                    z3_used = output.get('z3_used', False)
                    print(f"✓ Phase: {phase_name}")
                    print(f"  - Z3 Used: {z3_used}")

    print(f"\n{'='*80}")
    print("SVG saved to:", result.svg_path)
    print("="*80)

except Exception as e:
    print(f"\n❌ TEST FAILED with error:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
