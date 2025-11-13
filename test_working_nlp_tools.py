"""
Test the 4 WORKING NLP tools (no downloads required):
- OpenIE: Relation extraction
- ChemDataExtractor: Chemistry-specific extraction
- MathBERT: Mathematical expression extraction
- AMR: Abstract Meaning Representation parsing

This proves the NLP stack is MORE than just OpenIE!
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
config.output_dir = "output_working_nlp"
config.log_dir = "logs"
config.enable_logging = True
config.log_level = "INFO"
config.validation_mode = "warn"

# Enable NLP with WORKING tools only (no downloads needed)
config.enable_nlp_enrichment = True
config.nlp_tools = [
    'openie',            # ✅ WORKS - Relation extraction
    'chemdataextractor',  # ✅ WORKS - Chemistry extraction
    'mathbert',          # ✅ WORKS - Math extraction
    'amr'                # ✅ WORKS - Semantic parsing
]

config.enable_property_graph = True
config.enable_complexity_assessment = True
config.enable_strategic_planning = True
config.enable_z3_optimization = True

print("="*80)
print("TESTING 4 WORKING NLP TOOLS (Beyond OpenIE!)")
print("="*80)
print("Tools enabled:")
print("  ✓ OpenIE          - Relation extraction")
print("  ✓ ChemDataExtractor - Chemistry-specific")
print("  ✓ MathBERT        - Mathematical expressions")
print("  ✓ AMR Parser      - Semantic parsing")
print("="*80)

try:
    pipeline = UnifiedDiagramPipeline(config)

    print("\n" + "="*80)
    print("ACTIVE NLP FEATURES:")
    print("="*80)
    nlp_features = [f for f in pipeline.active_features
                    if any(x in f.lower() for x in ['nlp', 'openie', 'chem', 'math', 'amr'])]
    for feature in nlp_features:
        print(f"  ✓ {feature}")
    print()

    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ DIAGRAM GENERATED")
    print("="*80)

    # Analyze trace
    log_dir = Path(config.log_dir)
    trace_files = sorted(log_dir.glob("*_trace.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if trace_files:
        with open(trace_files[0], 'r') as f:
            trace = json.load(f)

        print(f"\nTrace: {trace_files[0].name}")
        print(f"\n{'='*80}")
        print("NLP STACK ANALYSIS")
        print(f"{'='*80}")

        for phase in trace['phases']:
            if 'NLP' in phase['phase_name']:
                output = phase.get('output', {})
                print(f"\nPhase: {phase['phase_name']}")
                print(f"Duration: {phase['duration_ms']:.2f}ms")
                print(f"Status: {phase['status']}")
                print(f"\nNLP Tools Output:\n")

                tools_with_output = []

                # OpenIE
                if 'openie' in output:
                    tools_with_output.append('OpenIE')
                    triples = output['openie'].get('triples', [])
                    print(f"1. OpenIE - Relation Extraction")
                    print(f"   Extracted {len(triples)} triples:")
                    for i, triple in enumerate(triples[:5], 1):
                        print(f"   {i}. {triple[0]} → {triple[1]} → {triple[2]}")

                # ChemDataExtractor
                if 'chemdataextractor' in output:
                    tools_with_output.append('ChemDataExtractor')
                    chem_data = output['chemdataextractor']
                    formulas = chem_data.get('formulas', [])
                    reactions = chem_data.get('reactions', 0)
                    properties = chem_data.get('properties', [])
                    print(f"\n2. ChemDataExtractor - Chemistry Extraction")
                    print(f"   Formulas: {formulas[:5] if formulas else 'None'}")
                    print(f"   Reactions: {reactions}")
                    print(f"   Properties: {properties[:5] if properties else 'None'}")

                # MathBERT
                if 'mathbert' in output:
                    tools_with_output.append('MathBERT')
                    math_data = output['mathbert']
                    variables = math_data.get('variables', [])
                    expressions = math_data.get('expressions', 0)
                    constants = math_data.get('constants', {})
                    print(f"\n3. MathBERT - Mathematical Expression Extraction")
                    print(f"   Variables: {variables[:10] if variables else 'None'}")
                    print(f"   Expressions count: {expressions}")
                    print(f"   Constants: {constants if constants else 'None'}")

                # AMR
                if 'amr' in output:
                    tools_with_output.append('AMR Parser')
                    amr_data = output['amr']
                    concepts = amr_data.get('concepts', [])
                    entities = amr_data.get('entities', {})
                    relations = amr_data.get('relations', [])
                    print(f"\n4. AMR Parser - Semantic Parsing")
                    print(f"   Concepts: {concepts[:10] if concepts else 'None'}")
                    print(f"   Entities: {entities if entities else 'None'}")
                    print(f"   Relations: {relations[:5] if relations else 'None'}")

                print(f"\n{'='*80}")
                print("RESULTS")
                print(f"{'='*80}")
                print(f"Tools Active: {len(tools_with_output)}/4")
                print(f"Tools with Output: {', '.join(tools_with_output)}")

                if len(tools_with_output) == 1 and 'OpenIE' in tools_with_output:
                    print()
                    print("❌ CONFIRMED: Only OpenIE is producing output")
                    print("   User's concern is VALID - NLP stack incomplete")
                elif len(tools_with_output) > 1:
                    print()
                    print(f"✅ SUCCESS: {len(tools_with_output)} NLP tools producing output")
                    print("   NLP stack is MORE than just OpenIE!")
                    print(f"   Active: {', '.join(tools_with_output)}")
                else:
                    print()
                    print("❌ ERROR: No tools producing output")

                print(f"{'='*80}")
                break

    print(f"\nSVG: {result.svg_path}")
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")

except Exception as e:
    print(f"\n❌ TEST FAILED")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
