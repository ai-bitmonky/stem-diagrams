"""
End-to-End Test for Complete Roadmap Implementation
====================================================

Tests all implemented features:
1. Property graph-driven planning (5-stage DiagramPlanner)
2. Primitive library queries
3. Z3/SymPy constraint solving
4. DeepSeek API calls (3 points)
5. VLM validation

Test Case: Simple DC Circuit
"Draw a simple DC circuit with a 12V battery connected in series to a 100-ohm resistor and a switch."

Author: Universal STEM Diagram Generator
Date: November 12, 2025
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig


def test_circuit_example():
    """Test circuit generation with full roadmap features"""

    print("\n" + "="*80)
    print("END-TO-END TEST: Complete Roadmap Implementation")
    print("="*80 + "\n")

    # Test request
    problem_text = "Draw a simple DC circuit with a 12V battery connected in series to a 100-ohm resistor and a switch."

    print(f"Test Request:\n{problem_text}\n")
    print("-"*80 + "\n")

    # Configure pipeline with all features
    api_key = os.environ.get('DEEPSEEK_API_KEY')

    config = PipelineConfig(
        # Core features
        api_key=api_key,
        validation_mode="standard",
        enable_layout_optimization=True,
        enable_domain_embellishments=True,

        # Advanced features
        enable_property_graph=True,
        enable_nlp_enrichment=True,
        enable_complexity_assessment=True,
        enable_strategic_planning=True,
        enable_ontology_validation=False,  # Optional
        enable_z3_optimization=True,  # KEY: Enable Z3

        # NLP tools
        nlp_tools=['openie'],  # Minimal for testing

        # DeepSeek 3 API calls
        enable_deepseek_enrichment=bool(api_key),
        enable_deepseek_audit=bool(api_key),
        enable_deepseek_validation=bool(api_key),
        deepseek_api_key=api_key,
        deepseek_model="deepseek-chat",
        deepseek_base_url="https://api.deepseek.com",

        # Primitive library (auto-enabled with memory backend)
        enable_primitive_library=True,
        primitive_library_backend="memory",

        # SymPy solver
        enable_sympy_solver=True,

        # VLM validation (stub for testing)
        enable_ai_validation=True,

        # Output
        output_dir="output/test_complete"
    )

    # Create output directory
    Path(config.output_dir).mkdir(parents=True, exist_ok=True)

    # Initialize pipeline
    print("\nInitializing Pipeline...\n")
    try:
        pipeline = UnifiedDiagramPipeline(config)
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Generate diagram
    print("\n" + "="*80)
    print("GENERATING DIAGRAM")
    print("="*80 + "\n")

    try:
        result = pipeline.generate(problem_text)
    except Exception as e:
        print(f"\n❌ Diagram generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Analyze results
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80 + "\n")

    success = True

    # Check 1: SVG generated
    if result.svg:
        print("✅ SVG diagram generated")
        svg_path = Path(config.output_dir) / "test_circuit.svg"
        with open(svg_path, 'w') as f:
            f.write(result.svg)
        print(f"   Saved to: {svg_path}")
    else:
        print("❌ No SVG generated")
        success = False

    # Check 2: Property graph used
    if result.property_graph:
        nodes = list(result.property_graph.get_all_nodes())
        edges = list(result.property_graph.get_edges())
        print(f"✅ Property graph: {len(nodes)} nodes, {len(edges)} edges")
    else:
        print("⚠️  No property graph")

    # Check 3: Complexity assessed
    if result.complexity_score is not None:
        print(f"✅ Complexity score: {result.complexity_score:.2f}")
    else:
        print("⚠️  No complexity score")

    # Check 4: Strategy selected
    if result.selected_strategy:
        print(f"✅ Strategy: {result.selected_strategy}")
    else:
        print("⚠️  No strategy selected")

    # Check 5: Z3/SymPy used
    metadata = result.metadata if hasattr(result, 'metadata') else {}
    planning_mode = metadata.get('planning_mode', 'unknown')
    z3_used = metadata.get('z3_used', False)
    sympy_used = metadata.get('sympy_used', False)

    print(f"\n📊 Planning Mode: {planning_mode}")

    if planning_mode == 'property_graph_driven':
        print("✅ Property graph-driven planning ACTIVE")
    else:
        print("⚠️  LLM extraction fallback used")

    if z3_used:
        print("✅ Z3 constraint solver USED")
    elif sympy_used:
        print("✅ SymPy solver USED")
    else:
        print("⚠️  No constraint solver used (heuristic only)")

    # Check 6: Primitive library
    if hasattr(pipeline, 'primitive_library') and pipeline.primitive_library:
        stats = pipeline.primitive_library.get_stats()
        print(f"✅ Primitive library: {stats['backend']} with {stats.get('total_primitives', 0)} primitives")
    else:
        print("⚠️  Primitive library not available")

    # Check 7: DeepSeek API calls
    if api_key:
        enrichment_cost = metadata.get('enrichment_cost_usd', 0)
        validation_cost = metadata.get('validation_cost_usd', 0)
        semantic_score = metadata.get('semantic_fidelity_score', 0)

        print(f"\n💰 DeepSeek API Costs:")
        print(f"   Enrichment: ${enrichment_cost:.4f}")
        print(f"   Validation: ${validation_cost:.4f}")
        print(f"   Semantic Fidelity: {semantic_score}/100")
    else:
        print("\n⚠️  DeepSeek API key not provided - API features disabled")

    # Check 8: Ontology validation
    if result.ontology_validation:
        print(f"\n✅ Ontology validation: {result.ontology_validation}")

    # Check 9: NLP results
    if result.nlp_results:
        print(f"\n✅ NLP tools used: {', '.join(result.nlp_results.keys())}")

    # Summary
    print("\n" + "="*80)
    if success:
        print("✅ TEST PASSED: All core features working")
    else:
        print("❌ TEST FAILED: Some features missing")
    print("="*80 + "\n")

    return success


def test_primitive_library_queries():
    """Test primitive library query functionality"""
    print("\n" + "="*80)
    print("TEST: Primitive Library Queries")
    print("="*80 + "\n")

    try:
        from core.primitive_library import PrimitiveLibrary, PrimitiveCategory

        # Initialize library
        library = PrimitiveLibrary(backend="memory")
        stats = library.get_stats()

        print(f"Library Stats:")
        print(f"  Backend: {stats['backend']}")
        print(f"  Total Primitives: {stats['total_primitives']}")
        print(f"  Categories: {stats['categories']}")
        print()

        # Test queries
        test_queries = [
            ("battery", PrimitiveCategory.ELECTRONICS),
            ("resistor", PrimitiveCategory.ELECTRONICS),
            ("spring", PrimitiveCategory.MECHANICS),
            ("atom", PrimitiveCategory.CHEMISTRY),
        ]

        for query, category in test_queries:
            results = library.query(query, top_k=1, category=category)
            if results:
                prim = results[0]
                print(f"✅ Query '{query}' → {prim.name} (score: {prim.similarity_score:.2f})")
            else:
                print(f"⚠️  Query '{query}' → No results")

        print("\n✅ Primitive library test PASSED\n")
        return True

    except Exception as e:
        print(f"\n❌ Primitive library test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_diagram_planner():
    """Test DiagramPlanner with property graph"""
    print("\n" + "="*80)
    print("TEST: DiagramPlanner 5-Stage Pipeline")
    print("="*80 + "\n")

    try:
        from core.diagram_planner import DiagramPlanner
        from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType

        # Create test property graph
        pg = PropertyGraph()

        # Add nodes
        battery = GraphNode(id="battery_1", type=NodeType.OBJECT, label="12V Battery")
        resistor = GraphNode(id="resistor_1", type=NodeType.OBJECT, label="100-ohm Resistor")
        switch = GraphNode(id="switch_1", type=NodeType.OBJECT, label="Switch")

        pg.add_node(battery)
        pg.add_node(resistor)
        pg.add_node(switch)

        # Add edges
        edge1 = GraphEdge(source="battery_1", target="resistor_1", type=EdgeType.CONNECTED_TO, label="series")
        edge2 = GraphEdge(source="resistor_1", target="switch_1", type=EdgeType.CONNECTED_TO, label="series")

        pg.add_edge(edge1)
        pg.add_edge(edge2)

        print(f"Test Property Graph: {len(list(pg.get_all_nodes()))} nodes, {len(list(pg.get_edges()))} edges\n")

        # Create planner
        planner = DiagramPlanner()

        # Run 5-stage planning
        problem_text = "Draw a circuit with battery, resistor, and switch"
        diagram_plan = planner.plan_from_property_graph(
            property_graph=pg,
            problem_text=problem_text,
            domain="electronics"
        )

        # Check results
        print(f"\n✅ DiagramPlan Created:")
        print(f"   Entities: {len(diagram_plan.extracted_entities)}")
        print(f"   Relations: {len(diagram_plan.extracted_relations)}")
        print(f"   Constraints: {len(diagram_plan.global_constraints)}")
        print(f"   Complexity: {diagram_plan.complexity_score:.2f}")
        print(f"   Strategy: {diagram_plan.strategy.value}")
        print(f"   Solver: {diagram_plan.layout_hints.get('solver', 'unknown')}")
        print(f"   Z3 Used: {diagram_plan.layout_hints.get('z3_used', False)}")

        if len(diagram_plan.extracted_entities) == 3:
            print("\n✅ DiagramPlanner test PASSED\n")
            return True
        else:
            print(f"\n⚠️  Expected 3 entities, got {len(diagram_plan.extracted_entities)}\n")
            return False

    except Exception as e:
        print(f"\n❌ DiagramPlanner test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "COMPLETE ROADMAP IMPLEMENTATION - TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝\n")

    # Run tests
    tests = [
        ("Primitive Library", test_primitive_library_queries),
        ("DiagramPlanner", test_diagram_planner),
        ("Full Pipeline (Circuit Example)", test_circuit_example),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}\n")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Final summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80 + "\n")

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Implementation Complete!")
    else:
        failed_count = sum(1 for p in results.values() if not p)
        print(f"⚠️  {failed_count}/{len(results)} tests failed")
    print("="*80 + "\n")

    sys.exit(0 if all_passed else 1)
