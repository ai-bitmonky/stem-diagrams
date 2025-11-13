"""
Test which NLP tools work without requiring downloads
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import json
from pathlib import Path

problem = """
A parallel-plate capacitor has charge q and plate area A.
The plates are separated by distance x.
The electric field E between the plates is uniform.
The capacitance C depends on the dielectric constant κ.
"""

# Test with tools that don't require downloads
config = PipelineConfig()
config.output_dir = "output_nlp_test"
config.log_dir = "logs"
config.enable_logging = True
config.log_level = "INFO"
config.validation_mode = "warn"

# Enable NLP with selective tools (skip Stanza for now due to model download requirement)
config.enable_nlp_enrichment = True
config.nlp_tools = [
    'openie',           # Should work (rule-based)
    'dygie',            # Should work if model available
    'scibert',          # Should work if transformers installed
    'chemdataextractor', # Should work (rule-based)
    'mathbert',         # Should work if model available
    'amr'               # Should work if model available
]
# Skip 'stanza' for now - requires model download

config.enable_property_graph = True
config.enable_complexity_assessment = True
config.enable_strategic_planning = True
config.enable_z3_optimization = True

print("="*80)
print("TESTING AVAILABLE NLP TOOLS (excluding Stanza)")
print("="*80)
print(f"Testing tools: {', '.join(config.nlp_tools)}")
print("="*80)

try:
    pipeline = UnifiedDiagramPipeline(config)

    print("\n" + "="*80)
    print("ACTIVE NLP FEATURES:")
    print("="*80)
    for feature in pipeline.active_features:
        if any(tool in feature.lower() for tool in ['nlp', 'openie', 'dygie', 'scibert', 'chem', 'math', 'amr']):
            print(f"  ✓ {feature}")
    print()

    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ TEST COMPLETED")
    print("="*80)

    # Check trace
    log_dir = Path(config.log_dir)
    trace_files = sorted(log_dir.glob("*_trace.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if trace_files:
        with open(trace_files[0], 'r') as f:
            trace = json.load(f)

        print(f"\nTrace file: {trace_files[0]}")
        print(f"\n{'='*80}")
        print("NLP PHASE ANALYSIS")
        print(f"{'='*80}")

        for phase in trace['phases']:
            if 'NLP' in phase['phase_name']:
                output = phase.get('output', {})
                print(f"\nPhase: {phase['phase_name']}")
                print(f"Duration: {phase['duration_ms']:.2f}ms")
                print(f"Status: {phase['status']}")
                print(f"\nTools that produced output:")

                tool_count = 0
                for tool_name, tool_output in output.items():
                    tool_count += 1
                    print(f"\n  ✅ {tool_name.upper()}")

                    if tool_name == 'openie':
                        triples = tool_output.get('triples', [])
                        print(f"     Triples: {len(triples)}")
                        for triple in triples[:3]:
                            print(f"       - {triple}")

                    elif tool_name == 'dygie':
                        print(f"     Output: {tool_output}")

                    elif tool_name == 'scibert':
                        embedding_dim = tool_output.get('embedding_dim', 0)
                        print(f"     Embedding dimension: {embedding_dim}")

                    elif tool_name == 'chemdataextractor':
                        formulas = tool_output.get('formulas', [])
                        reactions = tool_output.get('reactions', 0)
                        print(f"     Formulas: {len(formulas)}, Reactions: {reactions}")
                        if formulas:
                            print(f"     Formulas found: {formulas[:3]}")

                    elif tool_name == 'mathbert':
                        variables = tool_output.get('variables', [])
                        expressions = tool_output.get('expressions', 0)
                        print(f"     Variables: {len(variables)}, Expressions: {expressions}")
                        if variables:
                            print(f"     Variables: {variables[:5]}")

                    elif tool_name == 'amr':
                        concepts = tool_output.get('concepts', [])
                        relations = tool_output.get('relations', [])
                        print(f"     Concepts: {len(concepts)}, Relations: {len(relations)}")

                print(f"\n{'='*80}")
                print(f"TOTAL TOOLS PRODUCING OUTPUT: {tool_count}")
                print(f"{'='*80}")

                if tool_count == 1 and 'openie' in output:
                    print("\n⚠️  WARNING: Only OpenIE is producing output!")
                    print("This matches the user's concern about incomplete NLP stack.")
                elif tool_count > 1:
                    print(f"\n✅ Multiple NLP tools active: {list(output.keys())}")
                else:
                    print("\n❌ No NLP tools produced output!")

                break

    print(f"\nSVG: {result.svg_path}")

except Exception as e:
    print(f"\n❌ TEST FAILED")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
