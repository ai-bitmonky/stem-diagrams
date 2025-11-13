"""
Generate Diagrams for Batch 2 Questions (6-10)
Using unified_diagram_pipeline.py - Production Pipeline

Date: November 10, 2025
"""

import os
import sys
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# Batch 2 Questions
QUESTIONS = [
    {
        "id": 6,
        "topic": "Capacitance - Dielectric Insertion",
        "text": """A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed symmetrically
between the plates. What is the magnitude of the electric field in the dielectric after insertion?"""
    },
    {
        "id": 7,
        "topic": "Capacitance - Charge Redistribution",
        "text": """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"""
    },
    {
        "id": 8,
        "topic": "Capacitance - Multiple Dielectrics",
        "text": """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation 2d = 7.12 mm
is configured as follows: The left half is filled with dielectric κ₁ = 21.0. The right half is divided
into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0. Calculate the total capacitance.
[Left half: uniform κ₁; Right half: top quarter κ₂, bottom quarter κ₃]"""
    },
    {
        "id": 9,
        "topic": "Capacitance - Variable Capacitor",
        "text": """Capacitor 3 in a circuit is a variable capacitor (its capacitance C₃ can be varied).
The circuit shows the electric potential V₁ across capacitor 1 versus C₃. The horizontal scale
is set by C₃ₛ = 12.0 μF. Electric potential V₁ approaches an asymptote of 10 V as C₃ → ∞.
Circuit Configuration: C₁ is in series with the parallel combination of C₂ and C₃.
Determine: (a) The electric potential V across the battery (b) The capacitance C₁ (c) The capacitance C₂"""
    },
    {
        "id": 10,
        "topic": "Capacitance - Safety Engineering",
        "text": """As a safety engineer, you must evaluate the practice of storing flammable conducting liquids
in nonconducting containers. The company has been using a squat, cylindrical plastic container of
radius r = 0.20 m and filling it to height h = 10 cm. The exterior surface of the container commonly
acquires a negative charge density of magnitude 2.0 μC/m² (approximately uniform). The liquid is conducting.
Given: Container radius r = 0.20 m, Liquid height h = 0.10 m, Surface charge density σ = 2.0 μC/m²,
Capacitance C = 35 pF, Minimum spark energy E_min = 10 mJ.
Determine: (a) How much negative charge is induced in the center of the liquid's bulk?
(b) What is the potential energy in that effective capacitor?
(c) Can a spark ignite the liquid if the spark energy equals the stored potential energy?"""
    }
]

def main():
    """Generate diagrams for all Batch 2 questions"""

    print("=" * 80)
    print("BATCH 2 DIAGRAM GENERATION")
    print("Using: unified_diagram_pipeline.py (Production Pipeline)")
    print("=" * 80)
    print()

    # Get API key (optional - can run offline without it)
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("⚠️  No DEEPSEEK_API_KEY found - will use local analyzer")
        print()

    # Create configuration with ALL advanced features enabled
    config = PipelineConfig(
        api_key=api_key,  # None = offline mode with local fallback
        validation_mode="standard",

        # Original features
        enable_layout_optimization=True,
        enable_domain_embellishments=True,
        enable_ai_validation=False,  # Disable VLM for speed

        # Advanced features
        enable_property_graph=True,  # Re-enabled - bugs fixed
        enable_nlp_enrichment=True,  # Re-enabled - bugs fixed
        enable_complexity_assessment=True,  # Re-enabled - bugs fixed
        enable_strategic_planning=True,  # Re-enabled - bugs fixed
        enable_ontology_validation=True,  # Re-enabled - graceful fallback if RDFLib missing
        enable_z3_optimization=False,  # Disable - Z3 not installed
        enable_llm_auditing=False,  # Disable for speed

        # NLP tools (use OpenIE for speed)
        nlp_tools=['openie'],

        # Auditor backend
        auditor_backend='mock'
    )

    # Create pipeline
    print("Initializing pipeline...")
    try:
        pipeline = UnifiedDiagramPipeline(config)
        print()
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        sys.exit(1)

    # Create output directory
    output_dir = "output/batch_2_generated"
    os.makedirs(output_dir, exist_ok=True)

    # Generate diagrams for each question
    results = []
    for i, question in enumerate(QUESTIONS, 1):
        print("\n" + "=" * 80)
        print(f"QUESTION {question['id']} ({i}/5)")
        print("=" * 80)
        print(f"Topic: {question['topic']}")
        print(f"Text: {question['text'][:100]}...")
        print()

        try:
            # Generate diagram
            result = pipeline.generate(question['text'])

            # Save outputs
            base_name = f"question_{question['id']}"

            # Save SVG
            svg_path = os.path.join(output_dir, f"{base_name}.svg")
            result.save_svg(svg_path)

            # Save scene JSON
            scene_path = os.path.join(output_dir, f"{base_name}_scene.json")
            result.save_scene(scene_path)

            # Save metadata
            import json
            metadata_path = os.path.join(output_dir, f"{base_name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump({
                    'question_id': question['id'],
                    'topic': question['topic'],
                    'success': True,
                    'complexity_score': result.complexity_score,
                    'selected_strategy': result.selected_strategy,
                    'ontology_validation': result.ontology_validation,
                    'property_graph_nodes': len(result.property_graph.get_all_nodes()) if result.property_graph else 0,
                    'property_graph_edges': len(result.property_graph.get_edges()) if result.property_graph else 0,
                    'nlp_tools_used': list(result.nlp_results.keys()) if result.nlp_results else []
                }, f, indent=2)

            results.append({
                'question_id': question['id'],
                'success': True,
                'svg_path': svg_path,
                'scene_path': scene_path,
                'metadata_path': metadata_path
            })

            print(f"\n✅ Question {question['id']} complete!")
            print(f"   SVG: {svg_path}")
            print(f"   Scene: {scene_path}")
            print(f"   Metadata: {metadata_path}")

            if result.complexity_score:
                print(f"   Complexity: {result.complexity_score:.2f}")
            if result.selected_strategy:
                print(f"   Strategy: {result.selected_strategy}")
            if result.property_graph:
                nodes = len(result.property_graph.get_all_nodes())
                edges = len(result.property_graph.get_edges())
                print(f"   Property Graph: {nodes} nodes, {edges} edges")

        except Exception as e:
            print(f"\n❌ Question {question['id']} FAILED: {e}")
            import traceback
            traceback.print_exc()

            results.append({
                'question_id': question['id'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print("\n" + "=" * 80)
    print("BATCH 2 GENERATION COMPLETE")
    print("=" * 80)

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\n✅ Successful: {successful}/5")
    if failed > 0:
        print(f"❌ Failed: {failed}/5")

    print(f"\nOutput directory: {output_dir}")
    print()

    # Save summary
    summary_path = os.path.join(output_dir, "generation_summary.json")
    import json
    with open(summary_path, 'w') as f:
        json.dump({
            'batch': 2,
            'total_questions': len(QUESTIONS),
            'successful': successful,
            'failed': failed,
            'results': results,
            'pipeline': 'unified_diagram_pipeline.py',
            'features': {
                'property_graph': True,
                'nlp_enrichment': True,
                'complexity_assessment': True,
                'strategic_planning': True,
                'ontology_validation': True,
                'z3_optimization': True
            }
        }, f, indent=2)

    print(f"Summary saved: {summary_path}")
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
