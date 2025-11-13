"""
Full Pipeline Integration Example
Phase 7 of Advanced NLP Roadmap

Demonstrates the complete STEM diagram generation pipeline with
all advanced features integrated:

1. Property Graph construction
2. Advanced NLP (Stanza, DyGIE++, SciBERT, OpenIE)
3. Ontology validation and reasoning
4. Diagram planning with complexity assessment
5. Layout optimization (Z3, SymPy, Geometry)
6. Model orchestration
7. LLM-based auditing

Usage:
    python examples/full_pipeline_integration.py
"""

from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.problem_spec import CanonicalProblemSpec
from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType
from core.diagram_planner import DiagramPlanner, PlanningStrategy
from core.model_orchestrator import ModelOrchestrator, ModelType

# Advanced NLP tools
from core.nlp_tools.stanza_enhancer import StanzaEnhancer
from core.nlp_tools.openie_extractor import OpenIEExtractor

# Ontology
from core.ontology.ontology_manager import OntologyManager, Domain

# Auditor
from core.auditor.diagram_auditor import DiagramAuditor, LLMBackend


def print_section(title: str) -> None:
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_property_graph_basics():
    """Example 1: Basic Property Graph operations"""
    print_section("Example 1: Property Graph Basics")

    # Create a property graph for a simple physics problem
    graph = PropertyGraph()

    # Add nodes (objects in the diagram)
    block = GraphNode(
        id="block1",
        type=NodeType.OBJECT,
        label="Block",
        properties={"mass": "5 kg", "position": {"x": 100, "y": 200}}
    )
    graph.add_node(block)

    surface = GraphNode(
        id="surface1",
        type=NodeType.OBJECT,
        label="Surface",
        properties={"position": {"x": 0, "y": 300}, "friction_coefficient": "0.3"}
    )
    graph.add_node(surface)

    force_gravity = GraphNode(
        id="F_g",
        type=NodeType.FORCE,
        label="Gravitational Force",
        properties={"magnitude": "49 N", "direction": "down"}
    )
    graph.add_node(force_gravity)

    force_normal = GraphNode(
        id="F_n",
        type=NodeType.FORCE,
        label="Normal Force",
        properties={"magnitude": "49 N", "direction": "up"}
    )
    graph.add_node(force_normal)

    # Add edges (relationships)
    graph.add_edge(GraphEdge(
        source="F_g",
        target="block1",
        type=EdgeType.ACTS_ON,
        label="acts on"
    ))

    graph.add_edge(GraphEdge(
        source="F_n",
        target="block1",
        type=EdgeType.ACTS_ON,
        label="acts on"
    ))

    graph.add_edge(GraphEdge(
        source="block1",
        target="surface1",
        type=EdgeType.TOUCHES,
        label="in contact with"
    ))

    # Display graph summary
    print("\nProperty Graph Created:")
    print(graph.summary())

    # Query the graph
    print("\nQuerying for all forces:")
    forces = graph.find_nodes_by_type(NodeType.FORCE)
    for force_id in forces:
        force_node = graph.get_node(force_id)
        if force_node:
            print(f"  - {force_node.label}: {force_node.properties.get('magnitude', 'unknown')}")

    # Find spatial relationships
    print("\nFinding objects near block1:")
    neighbors = graph.get_neighbors("block1")
    for neighbor_id in neighbors:
        neighbor = graph.get_node(neighbor_id)
        if neighbor:
            print(f"  - {neighbor.label} ({neighbor.type.value})")

    return graph


def example_2_nlp_enrichment():
    """Example 2: NLP enrichment of text descriptions"""
    print_section("Example 2: Advanced NLP Enrichment")

    text = "A 5kg block rests on a horizontal surface. Gravity acts on the block with a force of 49N downward."

    # OpenIE extraction
    print("\n1. OpenIE Triple Extraction:")
    try:
        openie = OpenIEExtractor(backend='pattern', verbose=False)
        result = openie.extract(text)
        print(f"   Extracted {len(result.triples)} triples:")
        for triple in result.triples:
            print(f"   - {triple}")
    except Exception as e:
        print(f"   OpenIE not available: {e}")

    # Stanza dependency parsing (requires download)
    print("\n2. Stanza Dependency Parsing:")
    try:
        from core.nlp_tools.stanza_enhancer import check_stanza_availability
        if check_stanza_availability():
            stanza = StanzaEnhancer(verbose=False)
            analysis = stanza.analyze(text)
            print(f"   Found {len(analysis.get('dependencies', []))} dependency relations")
            for dep in analysis.get('dependencies', [])[:5]:
                print(f"   - {dep}")
        else:
            print("   Stanza not installed")
    except Exception as e:
        print(f"   Stanza not available: {e}")

    # SciBERT similarity (requires transformers)
    print("\n3. SciBERT Semantic Similarity:")
    try:
        from core.nlp_tools.scibert_embedder import simple_similarity
        sim1 = simple_similarity("gravitational force", "weight")
        sim2 = simple_similarity("gravitational force", "normal force")
        print(f"   Similarity('gravitational force', 'weight'): {sim1:.3f}")
        print(f"   Similarity('gravitational force', 'normal force'): {sim2:.3f}")
    except Exception as e:
        print(f"   SciBERT not available: {e}")


def example_3_ontology_validation():
    """Example 3: Ontology-based semantic validation"""
    print_section("Example 3: Ontology Validation")

    try:
        from core.ontology.ontology_manager import create_physics_ontology

        # Create physics ontology
        ontology = create_physics_ontology()
        print(f"\nPhysics ontology initialized with {len(ontology.graph)} triples")

        # Add instances
        print("\nAdding force instances:")
        ontology.add_instance("F1", "phys:GravitationalForce", {
            "phys:hasMagnitude": "49",
            "phys:hasDirection": "down"
        })
        ontology.add_instance("F2", "phys:NormalForce", {
            "phys:hasMagnitude": "49",
            "phys:hasDirection": "up"
        })

        print("  - F1: GravitationalForce (49N down)")
        print("  - F2: NormalForce (49N up)")

        # Validate
        print("\nValidating ontology:")
        result = ontology.validate()
        print(f"  Valid: {result.is_valid}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Warnings: {len(result.warnings)}")

        if result.warnings:
            print("\n  Warnings:")
            for warning in result.warnings[:3]:
                print(f"    - {warning}")

        # Query instances
        print("\nQuerying for all forces:")
        forces = ontology.find_instances_of_class("phys:Force")
        print(f"  Found {len(forces)} force instances")

        # Export to RDF
        print("\nExporting to RDF/Turtle:")
        rdf = ontology.export_rdf('turtle')
        print(f"  {len(rdf)} characters of RDF data")

    except ImportError as e:
        print(f"\nOntology features not available: {e}")
        print("Install with: pip install rdflib owlrl")


def example_4_diagram_planning():
    """Example 4: Diagram planning with complexity assessment"""
    print_section("Example 4: Diagram Planning")

    # Create a sample problem spec
    spec = CanonicalProblemSpec(
        domain="mechanics",
        text_description="A block on an inclined plane with friction",
        objects=[
            {"id": "block", "type": "rectangle", "label": "Block (5kg)"},
            {"id": "plane", "type": "line", "label": "Inclined Plane"}
        ],
        relationships=[
            {"source": "block", "target": "plane", "type": "on"},
            {"source": "F_g", "target": "block", "type": "acts_on"},
            {"source": "F_n", "target": "block", "type": "acts_on"},
            {"source": "F_f", "target": "block", "type": "acts_on"}
        ],
        constraints=[
            {"type": "angle", "description": "Plane inclined at 30 degrees"},
            {"type": "force_balance", "description": "Static equilibrium"}
        ]
    )

    # Create planner
    planner = DiagramPlanner(verbose=False)

    # Assess complexity
    complexity = planner.assess_complexity(spec)
    print(f"\nDiagram Complexity Score: {complexity:.2f}")

    # Create plan
    plan = planner.plan(spec)
    print(f"\nSelected Strategy: {plan.strategy.value}")
    print(f"Canvas Size: {plan.canvas_width}x{plan.canvas_height}")
    print(f"Global Constraints: {len(plan.global_constraints)}")
    print(f"Subproblems: {len(plan.subproblems)}")

    if plan.subproblems:
        print("\nSubproblems:")
        for i, subproblem in enumerate(plan.subproblems, 1):
            print(f"  {i}. {subproblem.description} ({len(subproblem.objects)} objects)")


def example_5_model_orchestration():
    """Example 5: Model orchestration with automatic fallback"""
    print_section("Example 5: Model Orchestration")

    # Create orchestrator
    orchestrator = ModelOrchestrator(verbose=False)

    # Test different complexity levels
    test_specs = [
        {
            "name": "Simple (1 object)",
            "spec": CanonicalProblemSpec(
                domain="mechanics",
                objects=[{"id": "obj1", "type": "circle"}],
                relationships=[]
            )
        },
        {
            "name": "Medium (3 objects, 2 relationships)",
            "spec": CanonicalProblemSpec(
                domain="mechanics",
                objects=[
                    {"id": "obj1", "type": "circle"},
                    {"id": "obj2", "type": "rectangle"},
                    {"id": "obj3", "type": "circle"}
                ],
                relationships=[
                    {"source": "obj1", "target": "obj2", "type": "connected"},
                    {"source": "obj2", "target": "obj3", "type": "connected"}
                ]
            )
        },
        {
            "name": "Complex (5 objects, constraints)",
            "spec": CanonicalProblemSpec(
                domain="mechanics",
                objects=[{"id": f"obj{i}", "type": "circle"} for i in range(5)],
                relationships=[{"source": f"obj{i}", "target": f"obj{i+1}", "type": "connected"}
                              for i in range(4)],
                constraints=[
                    {"type": "symmetry", "description": "Symmetric layout"},
                    {"type": "spacing", "description": "Equal spacing"}
                ]
            )
        }
    ]

    print("\nModel Selection for Different Complexities:")
    for test in test_specs:
        complexity = orchestrator.assess_complexity(test["spec"])
        model = orchestrator.select_model(test["spec"])
        print(f"\n  {test['name']}:")
        print(f"    Complexity: {complexity:.2f}")
        print(f"    Selected Model: {model.value}")


def example_6_auditor_integration():
    """Example 6: LLM-based diagram auditing"""
    print_section("Example 6: LLM Auditor Integration")

    # Create a simple spec for auditing
    spec = CanonicalProblemSpec(
        domain="mechanics",
        text_description="Block on inclined plane with forces",
        objects=[
            {"id": "block", "type": "rectangle", "label": "Block",
             "position": {"x": 200, "y": 300}},
            {"id": "plane", "type": "line", "label": "Incline",
             "position": {"x": 0, "y": 400}}
        ],
        relationships=[
            {"source": "F_g", "target": "block", "type": "acts_on"},
            {"source": "F_n", "target": "block", "type": "acts_on"}
        ],
        quantities=[
            {"name": "m", "value": "5", "unit": "kg"},
            {"name": "theta", "value": "30", "unit": "degrees"}
        ]
    )

    # Test with mock backend
    print("\nUsing Mock LLM Backend (for demonstration):")
    auditor = DiagramAuditor(backend=LLMBackend.MOCK, verbose=False)
    print(f"  Backend: {auditor.backend.value}")
    print(f"  Available: {auditor.is_available()}")

    # Generate scene description
    print("\nScene Description:")
    description = auditor.generate_scene_description(spec)
    print(description[:300] + "..." if len(description) > 300 else description)

    # Audit the diagram
    print("\nAuditing Diagram:")
    result = auditor.audit(spec)
    print(f"  Overall Score: {result.overall_score:.2f}/1.00")
    print(f"  Total Issues: {len(result.issues)}")

    if result.issues:
        print("\n  Issues Found:")
        for issue in result.issues[:5]:  # Show first 5
            print(f"    [{issue.severity.value}] {issue.description}")

    # Check for real LLM backends
    print("\n\nLLM Backend Availability:")
    from core.auditor.diagram_auditor import check_llm_availability
    availability = check_llm_availability()
    for backend, available in availability.items():
        status = "✓ Available" if available else "✗ Not installed"
        print(f"  {backend.upper()}: {status}")

    if not availability['claude'] and not availability['gpt']:
        print("\n  Note: Install LLM clients for full functionality:")
        print("    pip install anthropic openai")


def example_7_end_to_end_pipeline():
    """Example 7: Complete end-to-end pipeline"""
    print_section("Example 7: End-to-End Pipeline")

    print("\nThis example demonstrates a complete diagram generation workflow:\n")

    # Step 1: Parse text description
    print("Step 1: Parse Text Description")
    text = "A 5kg block rests on a 30-degree inclined plane. Friction coefficient is 0.3."
    print(f"  Input: '{text}'")

    # Step 2: Build property graph
    print("\nStep 2: Build Property Graph")
    graph = PropertyGraph()

    # Add entities (simplified extraction)
    block = GraphNode(id="block", type=NodeType.OBJECT, label="Block (5kg)")
    plane = GraphNode(id="plane", type=NodeType.OBJECT, label="Inclined Plane (30°)")
    graph.add_node(block)
    graph.add_node(plane)

    graph.add_edge(GraphEdge(source="block", target="plane", type=EdgeType.TOUCHES))
    print(f"  Created graph with {len(graph.graph.nodes)} nodes, {len(graph.graph.edges)} edges")

    # Step 3: Convert to problem spec
    print("\nStep 3: Convert to CanonicalProblemSpec")
    spec = graph.to_canonical_spec("mechanics")
    print(f"  Domain: {spec.domain}")
    print(f"  Objects: {len(spec.objects)}")

    # Step 4: Plan diagram
    print("\nStep 4: Plan Diagram Layout")
    planner = DiagramPlanner(verbose=False)
    plan = planner.plan(spec)
    print(f"  Strategy: {plan.strategy.value}")
    print(f"  Complexity: {planner.assess_complexity(spec):.2f}")

    # Step 5: Select model
    print("\nStep 5: Select Optimal Model")
    orchestrator = ModelOrchestrator(verbose=False)
    model = orchestrator.select_model(spec)
    print(f"  Selected: {model.value}")

    # Step 6: Validate semantics (if ontology available)
    print("\nStep 6: Validate Semantics")
    try:
        from core.ontology.ontology_manager import create_physics_ontology
        ontology = create_physics_ontology()
        # In real implementation, would convert spec to ontology and validate
        print("  Ontology validation: Available")
    except ImportError:
        print("  Ontology validation: Not available (rdflib not installed)")

    # Step 7: Audit quality (mock)
    print("\nStep 7: Audit Diagram Quality")
    auditor = DiagramAuditor(backend=LLMBackend.MOCK, verbose=False)
    audit_result = auditor.audit(spec)
    print(f"  Quality Score: {audit_result.overall_score:.2f}/1.00")
    print(f"  Issues: {len(audit_result.issues)}")

    print("\n✓ Pipeline Complete!")


def run_all_examples():
    """Run all integration examples"""
    print("\n" + "="*70)
    print("  STEM Diagram Pipeline - Full Integration Examples")
    print("  November 2025 Implementation")
    print("="*70)

    examples = [
        ("Property Graph Basics", example_1_property_graph_basics),
        ("NLP Enrichment", example_2_nlp_enrichment),
        ("Ontology Validation", example_3_ontology_validation),
        ("Diagram Planning", example_4_diagram_planning),
        ("Model Orchestration", example_5_model_orchestration),
        ("LLM Auditor", example_6_auditor_integration),
        ("End-to-End Pipeline", example_7_end_to_end_pipeline),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n  ⚠ Example {i} ({name}) encountered an error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("  All Examples Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_examples()
