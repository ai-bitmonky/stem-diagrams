"""
Test script to verify the FULL NLP STACK is operational
This addresses the gap identified: only OpenIE was active, but the roadmap
calls for a layered stack: spaCy + Stanza + SciBERT + OpenIE + AMR + ontology enrichment
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import os
from pathlib import Path
import json

# Test problem - electrostatics
problem = """
A parallel-plate capacitor has charge q and plate area A.
The plates are separated by distance x.
The electric field E between the plates is uniform.
The capacitance C depends on the dielectric constant κ.
"""

# Configure pipeline with FULL NLP STACK ENABLED
config = PipelineConfig()
config.output_dir = "output_full_nlp"
config.log_dir = "logs"
config.enable_logging = True
config.log_level = "INFO"
config.validation_mode = "warn"

# ============================================================================
# ENABLE FULL NLP STACK (All tools)
# ============================================================================
config.enable_nlp_enrichment = True  # ✅ ENABLED!
config.nlp_tools = [
    'openie',           # OpenIE relation extraction
    'stanza',           # Scientific NER, dependency parsing
    'dygie',            # DyGIE++ entity/relation extraction
    'scibert',          # SciBERT embeddings
    'chemdataextractor', # Chemistry extraction
    'mathbert',         # Math expression extraction
    'amr'               # AMR semantic parsing
]

# Enable other features
config.enable_property_graph = True
config.enable_complexity_assessment = True
config.enable_strategic_planning = True
config.enable_z3_optimization = True
config.enable_ontology_validation = False  # Disabled for now
config.enable_llm_planning = False
config.enable_llm_auditing = False

print("="*80)
print("TESTING FULL NLP STACK")
print("="*80)
print(f"NLP Enrichment: {'ENABLED' if config.enable_nlp_enrichment else 'DISABLED'}")
print(f"NLP Tools: {', '.join(config.nlp_tools)}")
print("="*80)

# Run pipeline
pipeline = UnifiedDiagramPipeline(config)

print("\n" + "="*80)
print("ACTIVE FEATURES:")
print("="*80)
for feature in pipeline.active_features:
    print(f"  ✓ {feature}")
print()

try:
    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ TEST PASSED - Diagram generated successfully!")
    print("="*80)

    # Check log files
    log_dir = Path(config.log_dir)
    if log_dir.exists():
        trace_files = sorted(log_dir.glob("*_trace.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        if trace_files:
            print(f"\n✅ Trace file created: {trace_files[0]}")

            # Verify trace contains ALL NLP tools output
            with open(trace_files[0], 'r') as f:
                trace = json.load(f)

            print(f"\n{'='*80}")
            print("NLP STACK VERIFICATION")
            print(f"{'='*80}")

            nlp_phase = None
            for phase in trace['phases']:
                if 'NLP' in phase['phase_name']:
                    nlp_phase = phase
                    break

            if nlp_phase:
                output = nlp_phase.get('output', {})
                print(f"Phase: {nlp_phase['phase_name']}")
                print(f"Duration: {nlp_phase['duration_ms']:.2f}ms")
                print(f"Status: {nlp_phase['status']}")
                print()

                # Check each NLP tool
                tools_found = []
                tools_missing = []

                if 'openie' in output:
                    tools_found.append('OpenIE')
                    triples = output['openie'].get('triples', [])
                    print(f"  ✅ OpenIE: {len(triples)} triples extracted")
                    for triple in triples[:3]:
                        print(f"     - {triple}")
                else:
                    tools_missing.append('OpenIE')
                    print(f"  ❌ OpenIE: NO OUTPUT")

                if 'stanza' in output:
                    tools_found.append('Stanza')
                    entities = output['stanza'].get('entities', [])
                    print(f"  ✅ Stanza: {len(entities)} entities extracted")
                    for entity in entities[:3]:
                        print(f"     - {entity}")
                else:
                    tools_missing.append('Stanza')
                    print(f"  ❌ Stanza: NO OUTPUT")

                if 'dygie' in output:
                    tools_found.append('DyGIE++')
                    print(f"  ✅ DyGIE++: Output present")
                else:
                    tools_missing.append('DyGIE++')
                    print(f"  ❌ DyGIE++: NO OUTPUT")

                if 'scibert' in output:
                    tools_found.append('SciBERT')
                    embedding_dim = output['scibert'].get('embedding_dim', 0)
                    print(f"  ✅ SciBERT: {embedding_dim}-dimensional embeddings")
                else:
                    tools_missing.append('SciBERT')
                    print(f"  ❌ SciBERT: NO OUTPUT")

                if 'chemdataextractor' in output:
                    tools_found.append('ChemDataExtractor')
                    formulas = output['chemdataextractor'].get('formulas', [])
                    print(f"  ✅ ChemDataExtractor: {len(formulas)} formulas extracted")
                else:
                    tools_missing.append('ChemDataExtractor')
                    print(f"  ❌ ChemDataExtractor: NO OUTPUT")

                if 'mathbert' in output:
                    tools_found.append('MathBERT')
                    variables = output['mathbert'].get('variables', [])
                    expressions = output['mathbert'].get('expressions', 0)
                    print(f"  ✅ MathBERT: {len(variables)} variables, {expressions} expressions")
                    if variables:
                        print(f"     Variables: {', '.join(variables[:5])}")
                else:
                    tools_missing.append('MathBERT')
                    print(f"  ❌ MathBERT: NO OUTPUT")

                if 'amr' in output:
                    tools_found.append('AMR Parser')
                    concepts = output['amr'].get('concepts', [])
                    relations = output['amr'].get('relations', [])
                    print(f"  ✅ AMR Parser: {len(concepts)} concepts, {len(relations)} relations")
                else:
                    tools_missing.append('AMR Parser')
                    print(f"  ❌ AMR Parser: NO OUTPUT")

                print()
                print(f"{'='*80}")
                print("SUMMARY")
                print(f"{'='*80}")
                print(f"Tools Active: {len(tools_found)}/7")
                print(f"Tools Found: {', '.join(tools_found) if tools_found else 'NONE'}")
                if tools_missing:
                    print(f"Tools Missing: {', '.join(tools_missing)}")
                    print()
                    print("❌ NLP STACK INCOMPLETE - NOT ALL TOOLS PRODUCED OUTPUT")
                else:
                    print()
                    print("✅ FULL NLP STACK OPERATIONAL - ALL TOOLS PRODUCED OUTPUT")
                print(f"{'='*80}")

            else:
                print("❌ NLP Enrichment phase not found in trace!")

    print(f"\nSVG saved to: {result.svg_path}")
    print("="*80)

except Exception as e:
    print(f"\n❌ TEST FAILED with error:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
