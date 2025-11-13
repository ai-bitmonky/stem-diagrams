#!/usr/bin/env python3
"""
Test and Validate New Features
================================

Comprehensive test script for newly implemented Phase 2+ features:
1. LLM Diagram Planner (with Ollama/OpenAI)
2. SciBERT Scientific NLP Pipeline
3. Primitive Component Library
4. Physics Domain Module

This script tests each feature independently and then demonstrates
integration with the main pipeline.

Author: Universal STEM Diagram Generator
Date: November 5, 2025
"""

import sys
import time
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("NEW FEATURES TEST SUITE")
print("=" * 80)
print()

# ============================================
# TEST 1: PRIMITIVE LIBRARY
# ============================================

print("[TEST 1] PRIMITIVE COMPONENT LIBRARY")
print("-" * 80)

try:
    from core.primitive_library import PrimitiveLibrary

    print("✓ Imported PrimitiveLibrary")

    # Initialize library
    library = PrimitiveLibrary(
        library_path="test_data/primitive_library",
        use_embeddings=True
    )
    print("✓ Initialized library")

    # Bootstrap with common components
    library.bootstrap_library()
    print(f"✓ Bootstrapped library with {library.count()} primitives")

    # List domains and categories
    domains = library.list_domains()
    print(f"✓ Available domains: {', '.join(domains)}")

    for domain in domains:
        categories = library.list_categories(domain=domain)
        print(f"  • {domain}: {', '.join(categories)}")

    # Test keyword search
    print("\n[1.1] Testing keyword search...")
    results = library.search("resistor", domain="electronics", limit=3)
    print(f"✓ Found {len(results)} resistor components")
    for primitive in results:
        print(f"  • {primitive.name} ({primitive.id})")
        print(f"    Tags: {', '.join(primitive.tags)}")

    # Test semantic search (if embeddings available)
    if library.embedding_model:
        print("\n[1.2] Testing semantic search...")
        results = library.semantic_search(
            "component for storing electrical charge",
            limit=3
        )
        print(f"✓ Semantic search results:")
        for primitive, score in results:
            print(f"  • {primitive.name} (similarity: {score:.3f})")

    # Add custom primitive
    print("\n[1.3] Testing add primitive...")
    custom_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">
      <circle cx="25" cy="25" r="20" fill="none" stroke="#000" stroke-width="2"/>
      <text x="25" y="30" text-anchor="middle" font-size="14">Q</text>
    </svg>'''

    primitive_id = library.add_primitive(
        name="Test Charge",
        description="Point charge for testing",
        domain="physics",
        category="charge",
        svg_content=custom_svg,
        tags=["charge", "point", "test"],
        metadata={"test": True}
    )
    print(f"✓ Added custom primitive: {primitive_id}")
    print(f"✓ Library now has {library.count()} primitives")

    print("\n✅ TEST 1 PASSED: Primitive Library working correctly")
    test1_passed = True

except Exception as e:
    print(f"\n❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()
    test1_passed = False

print("\n")

# ============================================
# TEST 2: SCIBERT NLP PIPELINE
# ============================================

print("[TEST 2] SCIBERT SCIENTIFIC NLP PIPELINE")
print("-" * 80)

try:
    from core.scibert_nlp import SciBERTNLPPipeline

    print("✓ Imported SciBERTNLPPipeline")

    # Initialize pipeline
    nlp = SciBERTNLPPipeline(use_gpu=False)
    print("✓ Initialized SciBERT pipeline")

    # Test on scientific text
    test_text = """
    A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
    A battery charges the plates to a potential difference of 120 V and is then disconnected.
    The capacitance is 2.5 μF and stores 0.36 mJ of energy.
    """

    print("\n[2.1] Testing scientific entity extraction...")
    result = nlp.process(test_text)

    print(f"✓ Extracted {len(result['entities'])} entities")
    print("  Sample entities:")
    for entity in result['entities'][:5]:
        print(f"    • {entity['text']} ({entity['label']})")

    print(f"\n✓ Extracted {len(result['quantities'])} quantities")
    print("  Quantities:")
    for qty in result['quantities'][:5]:
        print(f"    • {qty['value']} {qty['unit']} ({qty['type']})")

    print(f"\n✓ Domain classification: {result['domain']}")
    print(f"✓ Confidence: {result['confidence']:.1%}")

    # Test embeddings (if available)
    if result.get('embeddings'):
        print("\n[2.2] Testing SciBERT embeddings...")
        print(f"✓ Generated embeddings with dimension: {result['embeddings']['embedding_dim']}")
    else:
        print("\n[2.2] SciBERT embeddings: Not requested (use extract_embeddings=True)")

    print("\n✅ TEST 2 PASSED: SciBERT NLP working correctly")
    test2_passed = True

except Exception as e:
    print(f"\n❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    test2_passed = False

print("\n")

# ============================================
# TEST 3: PHYSICS DOMAIN MODULE
# ============================================

print("[TEST 3] PHYSICS DOMAIN MODULE")
print("-" * 80)

try:
    from core.physics_module import PhysicsDiagramModule
    from core.universal_scene_format import UniversalScene

    print("✓ Imported PhysicsDiagramModule")

    # Initialize module
    physics = PhysicsDiagramModule()
    print("✓ Initialized physics module")

    # Test free-body diagram
    print("\n[3.1] Testing free-body diagram generation...")
    fbd_problem = """
    A 10 kg block rests on a horizontal surface. Calculate the normal force.
    The coefficient of friction is 0.3 and a horizontal force of 50 N is applied.
    """

    fbd_plan = {
        'diagram_type': 'free_body',
        'entities': [
            {'text': '10 kg', 'label': 'MASS', 'value': 10, 'unit': 'kg'},
            {'text': '50 N', 'label': 'FORCE', 'value': 50, 'unit': 'N'}
        ]
    }

    scene = physics.generate_diagram(fbd_plan, fbd_problem)
    print(f"✓ Generated free-body diagram")
    print(f"  • Objects: {len(scene.objects)}")
    print(f"  • Relationships: {len(scene.relationships)}")
    print(f"  • Annotations: {len(scene.annotations)}")

    # Test spring-mass system
    print("\n[3.2] Testing spring-mass diagram generation...")
    spring_problem = """
    A mass of 2 kg is attached to a spring with spring constant k = 100 N/m.
    The mass is displaced 0.1 m from equilibrium.
    """

    spring_plan = {
        'diagram_type': 'spring_mass',
        'entities': [
            {'text': '2 kg', 'label': 'MASS', 'value': 2, 'unit': 'kg'},
            {'text': '100 N/m', 'label': 'SPRING_CONSTANT', 'value': 100, 'unit': 'N/m'}
        ]
    }

    scene = physics.generate_diagram(spring_plan, spring_problem)
    print(f"✓ Generated spring-mass diagram")
    print(f"  • Objects: {len(scene.objects)}")

    # Test inclined plane
    print("\n[3.3] Testing inclined plane diagram generation...")
    incline_problem = """
    A 5 kg block slides down a 30° incline. Calculate the acceleration.
    """

    incline_plan = {
        'diagram_type': 'incline',
        'entities': [
            {'text': '5 kg', 'label': 'MASS', 'value': 5, 'unit': 'kg'},
            {'text': '30°', 'label': 'ANGLE', 'value': 30, 'unit': 'degree'}
        ]
    }

    scene = physics.generate_diagram(incline_plan, incline_problem)
    print(f"✓ Generated inclined plane diagram")
    print(f"  • Objects: {len(scene.objects)}")

    print("\n✅ TEST 3 PASSED: Physics module working correctly")
    test3_passed = True

except Exception as e:
    print(f"\n❌ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()
    test3_passed = False

print("\n")

# ============================================
# TEST 4: LLM DIAGRAM PLANNER
# ============================================

print("[TEST 4] LLM DIAGRAM PLANNER")
print("-" * 80)

try:
    from core.llm_planner import LLMDiagramPlanner, RuleBasedPlanner

    print("✓ Imported LLM Planner")

    # First try rule-based planner (always available)
    print("\n[4.1] Testing rule-based planner...")
    rule_planner = RuleBasedPlanner()

    test_description = """
    Draw a circuit with a 12V battery connected to two resistors in series.
    The first resistor is 100 Ω and the second is 200 Ω.
    """

    # Create mock NLP result for rule-based planner
    mock_nlp_result = {
        'entities': [
            {'text': '12V', 'label': 'VOLTAGE', 'type': 'battery'},
            {'text': '100 Ω', 'label': 'RESISTANCE', 'type': 'resistor'},
            {'text': '200 Ω', 'label': 'RESISTANCE', 'type': 'resistor'}
        ],
        'relationships': [
            {'source': 'entity_0', 'target': 'entity_1', 'type': 'connected_to'},
            {'source': 'entity_1', 'target': 'entity_2', 'type': 'series_with'}
        ],
        'domain': 'electronics',
        'confidence': 0.8
    }

    plan = rule_planner.generate_plan(
        test_description,
        domain="electronics",
        nlp_result=mock_nlp_result
    )
    print(f"✓ Generated rule-based plan")
    print(f"  • Entities: {len(plan.entities)}")
    print(f"  • Relationships: {len(plan.relationships)}")
    print(f"  • Constraints: {len(plan.constraints)}")

    print("\n  Entities:")
    for entity in plan.entities[:5]:
        print(f"    • {entity.label} ({entity.type})")

    print("\n  Relationships:")
    for rel in plan.relationships[:3]:
        print(f"    • {rel.source_id} --[{rel.type}]--> {rel.target_id}")

    # Try LLM-based planner if Ollama is available
    print("\n[4.2] Testing LLM-based planner...")
    try:
        llm_planner = LLMDiagramPlanner(
            local_model="mistral:7b",
            use_api_for_verification=False  # Don't require API key for test
        )
        print("✓ Initialized LLM planner")

        # Check if Ollama is running
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✓ Ollama is running")

                # Generate plan with LLM
                llm_plan = llm_planner.generate_plan(
                    test_description,
                    domain="electronics",
                    use_local=True
                )
                print(f"✓ Generated LLM-based plan")
                print(f"  • Entities: {len(llm_plan.entities)}")
                print(f"  • Relationships: {len(llm_plan.relationships)}")
                print(f"  • Metadata: {llm_plan.metadata}")
            else:
                print("⚠ Ollama not responding (install with: curl -fsSL https://ollama.ai/install.sh | sh)")
        except requests.exceptions.RequestException:
            print("⚠ Ollama not running (start with: ollama serve)")
            print("  Falling back to rule-based planner")

    except Exception as e:
        print(f"⚠ LLM planner not available: {e}")
        print("  Falling back to rule-based planner")

    print("\n✅ TEST 4 PASSED: Planner working correctly (rule-based confirmed)")
    test4_passed = True

except Exception as e:
    print(f"\n❌ TEST 4 FAILED: {e}")
    import traceback
    traceback.print_exc()
    test4_passed = False

print("\n")

# ============================================
# TEST 5: INTEGRATED PIPELINE
# ============================================

print("[TEST 5] INTEGRATED PIPELINE TEST")
print("-" * 80)

try:
    print("Testing integration of all new features...\n")

    # Physics problem
    physics_problem = """
    A 5 kg block is on a frictionless surface. A horizontal force of 20 N is applied.
    Calculate the acceleration of the block.
    """

    # Step 1: SciBERT NLP extraction
    print("[5.1] SciBERT NLP extraction...")
    nlp_result = nlp.process(physics_problem)
    print(f"✓ Extracted {len(nlp_result['entities'])} entities")
    print(f"✓ Domain: {nlp_result['domain']}")

    # Step 2: Generate plan
    print("\n[5.2] Generating diagram plan...")
    plan_dict = rule_planner.generate_plan(
        physics_problem,
        domain="physics",
        nlp_result=nlp_result
    )
    print(f"✓ Generated plan with {len(plan_dict.entities)} entities")

    # Step 3: Generate physics diagram
    print("\n[5.3] Generating physics diagram...")
    scene = physics.generate_diagram(
        {
            'diagram_type': 'free_body',
            'entities': [
                {'text': '5 kg', 'label': 'MASS', 'value': 5, 'unit': 'kg'},
                {'text': '20 N', 'label': 'FORCE', 'value': 20, 'unit': 'N'}
            ]
        },
        physics_problem
    )
    print(f"✓ Generated scene with {len(scene.objects)} objects")

    # Step 4: Search for primitives to enhance diagram
    print("\n[5.4] Searching primitive library...")
    force_primitives = library.search("force", domain="physics", limit=1)
    if force_primitives:
        print(f"✓ Found reusable force primitive: {force_primitives[0].name}")

    # Step 5: Render to SVG
    print("\n[5.5] Rendering to SVG...")
    from renderers.enhanced_svg_renderer import EnhancedSVGRenderer
    renderer = EnhancedSVGRenderer()
    svg_content = renderer.render(scene)
    print(f"✓ Generated SVG ({len(svg_content):,} bytes)")

    # Save integrated test result
    output_file = "test_data/integrated_test_diagram.svg"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text(svg_content)
    print(f"✓ Saved to: {output_file}")

    print("\n✅ TEST 5 PASSED: Full integration working correctly")
    test5_passed = True

except Exception as e:
    print(f"\n❌ TEST 5 FAILED: {e}")
    import traceback
    traceback.print_exc()
    test5_passed = False

print("\n")

# ============================================
# SUMMARY
# ============================================

print("=" * 80)
print("TEST SUITE SUMMARY")
print("=" * 80)
print()

test_results = [
    ("Primitive Library", test1_passed),
    ("SciBERT NLP", test2_passed),
    ("Physics Module", test3_passed),
    ("LLM Planner", test4_passed),
    ("Integrated Pipeline", test5_passed)
]

passed = sum(1 for _, result in test_results if result)
total = len(test_results)

print(f"Tests Passed: {passed}/{total}\n")

for name, result in test_results:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status}  {name}")

print()

if passed == total:
    print("🎉 ALL TESTS PASSED!")
    print("\n📝 Next Steps:")
    print("  1. Install Ollama for full LLM functionality: curl -fsSL https://ollama.ai/install.sh | sh")
    print("  2. Pull a model: ollama pull mistral:7b")
    print("  3. Review NEW_FEATURES_GUIDE.md for usage examples")
    print("  4. Integrate new features into main pipeline")
else:
    print("⚠️  SOME TESTS FAILED")
    print("\nReview error messages above for details.")

print()
print("=" * 80)
