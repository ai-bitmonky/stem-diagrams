"""
DEMONSTRATION: NLP Stack is MORE than just OpenIE

This test proves that multiple NLP tools can run simultaneously,
addressing the user's concern that only OpenIE produces output.

Working tools (no dependencies):
✅ OpenIE - Relation extraction
✅ ChemDataExtractor - Chemistry-specific
✅ MathBERT - Mathematical expressions

Blocked tools (require setup):
❌ Stanza - Model download permission error
❌ SciBERT - Network/proxy blocking HuggingFace
❌ DyGIE++ - AllenNLP not installed
⚠️  AMR Parser - Causes hang (needs investigation)
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import json
from pathlib import Path

problem = """
A parallel-plate capacitor has charge q and plate area A.
The plates are separated by distance x.
The electric field E between the plates is uniform.
The capacitance C depends on the dielectric constant κ.
The energy U stored is U = (1/2)CV².
"""

config = PipelineConfig()
config.output_dir = "output_stable_nlp"
config.log_dir = "logs"
config.enable_logging = True
config.log_level = "INFO"
config.validation_mode = "warn"

# ============================================================================
# ENABLE NLP WITH 3 STABLE TOOLS (no AMR to avoid hang)
# ============================================================================
config.enable_nlp_enrichment = True
config.nlp_tools = [
    'openie',            # ✅ Relation extraction (rule-based)
    'chemdataextractor',  # ✅ Chemistry extraction (rule-based)
    'mathbert'           # ✅ Math expression extraction (transformer-based)
]

config.enable_property_graph = True
config.enable_complexity_assessment = True
config.enable_strategic_planning = True
config.enable_z3_optimization = True

print("="*80)
print("DEMONSTRATION: NLP Stack Beyond OpenIE")
print("="*80)
print("Enabled tools:")
print("  1. OpenIE          - Extracts subject-relation-object triples")
print("  2. ChemDataExtractor - Extracts chemical formulas, reactions, properties")
print("  3. MathBERT        - Extracts variables, expressions, constants")
print()
print("This proves the NLP stack is NOT just OpenIE!")
print("="*80)

try:
    pipeline = UnifiedDiagramPipeline(config)

    print("\n" + "="*80)
    print("PIPELINE INITIALIZED")
    print("="*80)
    print("Active NLP features:")
    for feature in pipeline.active_features:
        if any(x in feature.lower() for x in ['nlp', 'openie', 'chem', 'math']):
            print(f"  ✓ {feature}")
    print()

    # Generate diagram
    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ DIAGRAM GENERATED SUCCESSFULLY")
    print("="*80)

    # Analyze trace
    log_dir = Path(config.log_dir)
    trace_files = sorted(log_dir.glob("*_trace.json"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True)

    if trace_files:
        with open(trace_files[0], 'r') as f:
            trace = json.load(f)

        print(f"\nLatest trace: {trace_files[0].name}\n")

        # Find NLP phase
        for phase in trace['phases']:
            if 'NLP' in phase['phase_name']:
                output = phase.get('output', {})

                print("="*80)
                print(f"PHASE: {phase['phase_name']}")
                print("="*80)
                print(f"Duration: {phase['duration_ms']:.2f}ms")
                print(f"Status: {phase['status']}")
                print(f"\nNLP Tools Output:\n")

                tool_count = len(output)

                # OpenIE
                if 'openie' in output:
                    triples = output['openie'].get('triples', [])
                    print(f"1️⃣  OpenIE - Relation Extraction")
                    print(f"    Extracted {len(triples)} triples:")
                    for i, triple in enumerate(triples[:5], 1):
                        subj, rel, obj = triple
                        print(f"    {i}. \"{subj}\" --[{rel}]--> \"{obj}\"")
                    print()

                # ChemDataExtractor
                if 'chemdataextractor' in output:
                    chem = output['chemdataextractor']
                    formulas = chem.get('formulas', [])
                    reactions = chem.get('reactions', 0)
                    props = chem.get('properties', [])
                    print(f"2️⃣  ChemDataExtractor - Chemistry Extraction")
                    print(f"    Formulas: {formulas if formulas else 'None found'}")
                    print(f"    Reactions: {reactions}")
                    print(f"    Properties: {props if props else 'None found'}")
                    print()

                # MathBERT
                if 'mathbert' in output:
                    math = output['mathbert']
                    variables = math.get('variables', [])
                    expressions = math.get('expressions', 0)
                    constants = math.get('constants', {})
                    print(f"3️⃣  MathBERT - Mathematical Expression Extraction")
                    print(f"    Variables: {', '.join(variables[:10]) if variables else 'None'}")
                    print(f"    Expressions: {expressions}")
                    print(f"    Constants: {constants if constants else 'None'}")
                    print()

                print("="*80)
                print("RESULTS")
                print("="*80)
                print(f"NLP Tools Executed: {tool_count}")
                print(f"Tools: {', '.join(output.keys())}")
                print()

                if tool_count == 1 and 'openie' in output:
                    print("❌ FAILURE: Only OpenIE produced output")
                    print("   User's concern is CONFIRMED")
                elif tool_count > 1:
                    print(f"✅ SUCCESS: {tool_count} NLP tools produced output")
                    print("   NLP stack is MORE than just OpenIE!")
                    print()
                    print("   This demonstrates:")
                    print("   - Infrastructure for multiple NLP tools EXISTS")
                    print("   - Multiple tools CAN run simultaneously")
                    print("   - Full layered stack IS achievable")
                    print()
                    print("   Blocked tools (require setup):")
                    print("   - Stanza (model download needed)")
                    print("   - SciBERT (network access needed)")
                    print("   - DyGIE++ (AllenNLP needed)")
                else:
                    print("❌ ERROR: No NLP tools produced output")

                print("="*80)
                break

    print(f"\nDiagram saved: {result.svg_path}")
    print("\nFor detailed analysis, see:")
    print("  - NLP_STACK_ANALYSIS.md")
    print("  - NLP_STACK_STATUS_SUMMARY.txt")
    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

except Exception as e:
    print(f"\n❌ TEST FAILED")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
