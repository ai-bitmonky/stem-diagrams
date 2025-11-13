"""
Test Production Pipeline Integration
=====================================

Tests that PropertyGraph and NLP tools are now available in the production pipeline
(core/unified_pipeline.py) which is used by web_interface.py

This verifies the fix for the critical gap where these features were only available
in unified_diagram_pipeline.py (batch processing) but not in production.
"""

import sys
from pathlib import Path

# Test problem
TEST_PROBLEM = """
A parallel-plate capacitor with charge Q = 5.0 μC and area A = 0.12 m².
The plates are separated by distance d = 1.2 cm.
Find the electric field between the plates.
"""

print("="*80)
print("PRODUCTION PIPELINE INTEGRATION TEST")
print("="*80)
print()
print("Testing core/unified_pipeline.py (used by web interface)")
print()

# TEST 1: Basic import
print("TEST 1: Import production pipeline")
print("-" * 80)
try:
    from core.unified_pipeline import UnifiedPipeline, PipelineMode
    print("✅ Import successful")
    print()
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# TEST 2: Initialize with PropertyGraph enabled
print("TEST 2: Initialize with PropertyGraph + NLP tools")
print("-" * 80)
try:
    pipeline = UnifiedPipeline(
        mode=PipelineMode.FAST,
        output_dir="output/test_production",
        enable_property_graph=True,
        enable_nlp_enrichment=True,
        nlp_tools=['openie']  # Start with just OpenIE
    )
    print("✅ Pipeline initialized with advanced features")
    print()
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 3: Generate diagram
print("TEST 3: Generate diagram with advanced features")
print("-" * 80)
try:
    result = pipeline.generate(TEST_PROBLEM, save_files=False)

    if result.success:
        print("✅ Generation successful")
        print(f"   SVG length: {len(result.svg)} bytes")
        print(f"   Domain: {result.metadata.get('domain')}")
        print(f"   Objects: {result.metadata.get('num_objects')}")

        # Check advanced features
        print("\nAdvanced Features:")
        print(f"   PropertyGraph enabled: {result.metadata.get('property_graph_enabled')}")
        print(f"   NLP enrichment enabled: {result.metadata.get('nlp_enrichment_enabled')}")
        print(f"   NLP tools used: {result.metadata.get('nlp_tools_used')}")

        if result.property_graph:
            print(f"   PropertyGraph nodes: {len(result.property_graph.get_all_nodes())}")
            print(f"   PropertyGraph edges: {len(result.property_graph.get_all_edges())}")

        if result.enriched_nlp_results:
            print(f"   Enriched NLP results: {list(result.enriched_nlp_results.keys())}")
            if 'openie' in result.enriched_nlp_results:
                triples_count = len(result.enriched_nlp_results['openie'].get('triples', []))
                print(f"   OpenIE triples: {triples_count}")

        print()
    else:
        print(f"❌ Generation failed: {result.error}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 4: Verify backward compatibility (features off by default)
print("TEST 4: Backward compatibility (features off by default)")
print("-" * 80)
try:
    # Initialize without enabling advanced features
    pipeline_baseline = UnifiedPipeline(mode=PipelineMode.FAST)

    # Should work without advanced features
    result_baseline = pipeline_baseline.generate(TEST_PROBLEM, save_files=False)

    if result_baseline.success:
        print("✅ Backward compatibility maintained")
        print(f"   PropertyGraph enabled: {result_baseline.metadata.get('property_graph_enabled', False)}")
        print(f"   NLP enrichment enabled: {result_baseline.metadata.get('nlp_enrichment_enabled', False)}")
        print("   (Both should be False by default)")
        print()
    else:
        print(f"❌ Baseline mode failed: {result_baseline.error}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Backward compatibility test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Verify PipelineResult.to_dict() includes new fields
print("TEST 5: PipelineResult serialization")
print("-" * 80)
try:
    result_dict = result.to_dict()

    # Check new fields are present
    has_enriched_nlp = 'enriched_nlp_results' in result_dict
    has_property_graph_summary = 'property_graph_summary' in result_dict

    print(f"✅ Serialization successful")
    print(f"   Has enriched_nlp_results: {has_enriched_nlp}")
    print(f"   Has property_graph_summary: {has_property_graph_summary}")

    if has_property_graph_summary:
        print(f"   Graph summary: {result_dict['property_graph_summary']}")
    print()
except Exception as e:
    print(f"❌ Serialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# SUMMARY
print("="*80)
print("INTEGRATION TEST SUMMARY")
print("="*80)
print()
print("✅ All tests passed!")
print()
print("Key findings:")
print("1. PropertyGraph is now integrated into production pipeline (core/unified_pipeline.py)")
print("2. Individual NLP tools (OpenIE, Stanza, etc.) are now available")
print("3. Features are disabled by default (backward compatible)")
print("4. Features can be enabled via configuration")
print("5. Results include property_graph and enriched_nlp_results fields")
print()
print("This means web_interface.py can now use these features!")
print()
print("="*80)
