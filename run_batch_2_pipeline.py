#!/usr/bin/env python3
"""
Run Unified Advanced Pipeline on Batch 2 Questions
==================================================

This script runs the UNIFIED pipeline (v4.0) with DiagramPlanner and Z3 optimization
on all 5 questions from batch_2_questions.html.

NOW USES:
- DiagramPlanner for complexity assessment and strategic planning
- Z3LayoutSolver for SMT-based optimal layout
- Property Graph for knowledge representation
- Open-Source NLP tools (OpenIE, Stanza, SciBERT)

Author: Universal STEM Diagram Generator
Date: November 10, 2025
Version: 2.0 (with DiagramPlanner + Z3)
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import UNIFIED Pipeline (v4.0) - NOW with DiagramPlanner and Z3
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# ============================================
# BATCH 2 QUESTIONS (Questions 6-10)
# ============================================

QUESTIONS = [
    {
        "id": 6,
        "topic": "Capacitance",
        "difficulty": "HARD",
        "text": """A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed
symmetrically between the plates. What is the magnitude of the electric field in the
dielectric after insertion?"""
    },
    {
        "id": 7,
        "topic": "Capacitance",
        "difficulty": "HARD",
        "text": """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"""
    },
    {
        "id": 8,
        "topic": "Capacitance",
        "difficulty": "MEDIUM",
        "text": """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation 2d = 7.12 mm
is configured as follows: The left half is filled with dielectric κ₁ = 21.0. The right half is
divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0. Calculate the total
capacitance."""
    },
    {
        "id": 9,
        "topic": "Capacitance",
        "difficulty": "MEDIUM",
        "text": """Capacitor 3 in the circuit is a variable capacitor (its capacitance C₃ can be varied).
The electric potential V₁ across capacitor 1 versus C₃ shows that V₁ approaches an asymptote
of 10 V as C₃ → ∞. The horizontal scale is set by C₃ₛ = 12.0 μF. Circuit Configuration: C₁ is
in series with the parallel combination of C₂ and C₃. Determine: (a) The electric potential V
across the battery (b) The capacitance C₁ (c) The capacitance C₂"""
    },
    {
        "id": 10,
        "topic": "Capacitance",
        "difficulty": "HARD",
        "text": """A cylindrical plastic container of radius r = 0.20 m filled with conducting liquid to
height h = 10 cm. The exterior surface of the container acquires a negative charge density of
magnitude 2.0 μC/m². The liquid is conducting. Given: Container radius r = 0.20 m, Liquid height
h = 0.10 m, Surface charge density σ = 2.0 × 10⁻⁶ C/m², Capacitance of liquid's central portion
C = 35 pF, Minimum spark energy to ignite E_min = 10 mJ. Determine: (a) How much negative charge
is induced in the center of the liquid's bulk? (b) What is the potential energy associated with
the negative charge? (c) Can a spark ignite the liquid?"""
    }
]

# ============================================
# UNIFIED PIPELINE RUNNER (v4.0 with DiagramPlanner + Z3)
# ============================================

class UnifiedPipelineRunner:
    """Runs complete unified advanced pipeline on physics problems"""

    def __init__(self, api_key: str):
        """
        Initialize unified pipeline with ALL advanced features including:
        - DiagramPlanner (complexity assessment + strategic planning)
        - Z3LayoutSolver (SMT-based optimal layout)
        - Property Graph (knowledge representation)
        - NLP Tools (OpenIE, Stanza, SciBERT)

        Args:
            api_key: DeepSeek API key
        """
        print("=" * 80)
        print("INITIALIZING UNIFIED PIPELINE v4.0")
        print("  ✓ DiagramPlanner for complexity & strategy")
        print("  ✓ Z3LayoutSolver for SMT optimization")
        print("  ✓ Property Graph for knowledge representation")
        print("  ✓ Open-Source NLP tools")
        print("=" * 80)

        # Create configuration with ALL advanced features enabled
        config = PipelineConfig(
            api_key=api_key,
            validation_mode="standard",  # Don't fail on warnings
            enable_layout_optimization=True,
            enable_domain_embellishments=True,
            # CRITICAL: Enable DiagramPlanner and Z3
            enable_property_graph=True,
            enable_nlp_enrichment=True,
            enable_complexity_assessment=True,  # Uses DiagramPlanner
            enable_strategic_planning=True,     # Uses DiagramPlanner
            enable_ontology_validation=True,
            enable_z3_optimization=True,        # Uses Z3LayoutSolver
            enable_llm_auditing=True,
            nlp_tools=['openie'],  # Start with just OpenIE (fastest)
            auditor_backend='mock'  # Mock for speed
        )

        # Initialize pipeline
        print("\nInitializing components...")
        self.pipeline = UnifiedDiagramPipeline(config)

        print("\n✅ Unified Pipeline initialized!\n")

    def run_pipeline(self, question_text: str, question_id: int, style: str = "modern"):
        """
        Run complete unified pipeline on a single question

        Args:
            question_text: The problem text
            question_id: Question number
            style: Ignored (unified pipeline handles styling)

        Returns:
            dict: Results including all advanced artifacts (property graph, complexity, etc.)
        """
        print(f"\n{'=' * 80}")
        print(f"PROCESSING QUESTION {question_id}")
        print(f"{'=' * 80}\n")

        start_time = time.time()

        # Run unified pipeline (with all 8 phases including DiagramPlanner + Z3)
        result = self.pipeline.generate(question_text)

        total_time = time.time() - start_time

        # Extract metrics from advanced pipeline
        return {
            'question_id': question_id,
            'svg': result.svg,
            'scene': result.scene,
            'specs': result.specs,
            'validation_report': result.validation_report,
            # Advanced artifacts
            'property_graph': result.property_graph,
            'nlp_results': result.nlp_results,
            'complexity_score': result.complexity_score,
            'selected_strategy': result.selected_strategy,
            'ontology_validation': result.ontology_validation,
            'audit_report': result.audit_report,
            'metadata': result.metadata,
            'timing': {
                'total': total_time
            }
        }

    def save_results(self, result: dict, output_dir: str = "batch_2_unified_output"):
        """Save SVG and metadata to files"""
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        question_id = result['question_id']

        # Save SVG
        svg_path = os.path.join(output_dir, f"question_{question_id}_unified.svg")
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(result['svg'])

        # Save metadata with advanced features
        meta_path = os.path.join(output_dir, f"question_{question_id}_metadata.txt")
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(f"Question {question_id} - Unified Pipeline v4.0 Results\n")
            f.write("=" * 60 + "\n\n")

            # Advanced features used
            if result.get('metadata', {}).get('advanced_features_used'):
                f.write("Advanced Features:\n")
                for feature in result['metadata']['advanced_features_used']:
                    f.write(f"  ✓ {feature}\n")
                f.write("\n")

            # Complexity and Strategy (from DiagramPlanner)
            if result.get('complexity_score'):
                f.write(f"Complexity Score: {result['complexity_score']:.2f}\n")
            if result.get('selected_strategy'):
                f.write(f"Strategy: {result['selected_strategy']}\n")
            f.write("\n")

            # NLP Results
            if result.get('nlp_results'):
                f.write("NLP Enrichment:\n")
                for tool, data in result['nlp_results'].items():
                    f.write(f"  {tool.upper()}:\n")
                    if 'triples' in data:
                        f.write(f"    Triples: {len(data['triples'])}\n")
                    if 'entities' in data:
                        f.write(f"    Entities: {len(data['entities'])}\n")
                f.write("\n")

            # Property Graph
            if result.get('property_graph'):
                pg = result['property_graph']
                nodes = len(pg.get_all_nodes())
                edges = len(pg.get_all_edges())
                f.write(f"Property Graph: {nodes} nodes, {edges} edges\n\n")

            # Ontology Validation
            if result.get('ontology_validation'):
                ov = result['ontology_validation']
                f.write(f"Ontology: {'✓ Consistent' if ov.get('consistent') else '✗ Inconsistent'}\n\n")

            # Validation Report
            val = result['validation_report']
            f.write(f"Validation:\n")
            f.write(f"  Valid: {val.is_valid}\n")
            f.write(f"  Errors: {len(val.errors)}\n")
            f.write(f"  Warnings: {len(val.warnings)}\n\n")

            # Timing
            f.write(f"Timing:\n")
            f.write(f"  Total: {result['timing']['total']:.3f}s\n")

        return svg_path, meta_path

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Run unified pipeline v4.0 on all Batch 2 questions"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "UNIFIED PIPELINE v4.0 - BATCH 2 QUESTIONS" + " " * 27 + "║")
    print("║" + " " * 22 + "Questions 6-10 (Capacitance)" + " " * 29 + "║")
    print("║" + " " * 8 + "DiagramPlanner + Z3 + Property Graph + NLP" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")

    # Get API key
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("\n❌ Error: DEEPSEEK_API_KEY environment variable not set")
        print("   Please set it with: export DEEPSEEK_API_KEY='your-key-here'")
        return

    # Initialize pipeline
    try:
        runner = UnifiedPipelineRunner(api_key)
    except Exception as e:
        print(f"\n❌ Failed to initialize pipeline: {e}")
        import traceback
        traceback.print_exc()
        return

    # Process all questions
    results = []
    for question in QUESTIONS:
        try:
            result = runner.run_pipeline(
                question_text=question['text'],
                question_id=question['id'],
                style='modern'
            )
            results.append(result)

            # Save results
            svg_path, meta_path = runner.save_results(result)
            print(f"\n📁 Saved files:")
            print(f"  • SVG: {svg_path}")
            print(f"  • Metadata: {meta_path}")

        except Exception as e:
            print(f"\n❌ ERROR processing Question {question['id']}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    # Summary Report
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 30 + "BATCH 2 SUMMARY" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")

    if results:
        print(f"\n✅ Successfully processed {len(results)}/{len(QUESTIONS)} questions\n")
        print(f"{'Question':<12} {'Complexity':<15} {'Strategy':<20} {'Time':<10}")
        print("-" * 80)

        for result in results:
            q_id = result['question_id']
            complexity = f"{result.get('complexity_score', 0):.2f}" if result.get('complexity_score') else "N/A"
            strategy = result.get('selected_strategy', 'N/A')[:18]
            total_time = result['timing']['total']
            print(f"Question {q_id:<4} {complexity:<15} {strategy:<20} {total_time:.3f}s")

        # Aggregate statistics
        complexities = [r.get('complexity_score', 0) for r in results if r.get('complexity_score')]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        avg_time = sum(r['timing']['total'] for r in results) / len(results)
        total_time = sum(r['timing']['total'] for r in results)

        print("-" * 80)
        print(f"\n📊 Statistics:")
        print(f"  • Average Complexity Score: {avg_complexity:.2f}")
        print(f"  • Average Processing Time: {avg_time:.3f}s")
        print(f"  • Total Processing Time: {total_time:.3f}s")

        # Advanced features summary
        if results[0].get('metadata', {}).get('advanced_features_used'):
            print(f"\n🚀 Advanced Features Used:")
            for feature in results[0]['metadata']['advanced_features_used']:
                print(f"  ✓ {feature}")

        print(f"\n📁 All outputs saved to: batch_2_unified_output/")
        print(f"\n🎉 Batch 2 processing complete with Unified Pipeline v4.0!")
    else:
        print("\n❌ No questions were successfully processed")

    print("\n")

if __name__ == "__main__":
    main()
