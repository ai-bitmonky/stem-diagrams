#!/usr/bin/env python3
"""
Complete Diagram Generation for Question 8
Using Latest Multi-Domain NLP Pipeline + Full Pipeline

Phases:
1. NLP Analysis (completed - load from files)
2. Scene Building
3. Validation
4. Layout
5. Rendering (SVG generation)
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Import pipeline components
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# Question 8 text
QUESTION_8_TEXT = """
A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation 2d = 7.12 mm
is configured as follows: The left half is filled with dielectric κ₁ = 21.0. The right
half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0.
Calculate the total capacitance.
"""

def print_section(title: str, char: str = "="):
    """Print section header"""
    print(f"\n{char * 80}")
    print(f" {title}")
    print(f"{char * 80}")


def main():
    """Main diagram generation"""
    print_section("QUESTION 8 - COMPLETE DIAGRAM GENERATION")

    print("\n📋 PROBLEM TEXT:")
    print(QUESTION_8_TEXT.strip())

    # Load NLP analysis results
    print_section("STEP 1: LOAD NLP ANALYSIS RESULTS", "-")

    nlp_results_path = Path("output/question8_nlp_results/nlp_analysis.json")
    canonical_spec_path = Path("output/question8_nlp_results/canonical_spec.json")
    scene_desc_path = Path("output/question8_nlp_results/scene_description.json")

    if not nlp_results_path.exists():
        print("❌ Error: NLP analysis results not found!")
        print(f"   Expected: {nlp_results_path}")
        print("\n   Please run: python3 generate_question8_with_nlp_v2.py")
        return 1

    with open(nlp_results_path, 'r') as f:
        nlp_results = json.load(f)

    with open(canonical_spec_path, 'r') as f:
        canonical_spec = json.load(f)

    with open(scene_desc_path, 'r') as f:
        scene_desc = json.load(f)

    print("✅ Loaded NLP analysis results:")
    print(f"   Domain: {nlp_results['domain']}")
    print(f"   Entities: {len(nlp_results['entities'])}")
    print(f"   Relationships: {len(nlp_results['relationships'])}")

    # Initialize unified pipeline
    print_section("STEP 2: INITIALIZE UNIFIED DIAGRAM PIPELINE", "-")

    # Create pipeline configuration
    config = PipelineConfig(
        api_key="dummy"  # Not using API for now
    )

    pipeline = UnifiedDiagramPipeline(config)

    print("✅ Pipeline initialized successfully")

    # Generate diagram using full pipeline
    print_section("STEP 3: RUN FULL PIPELINE", "-")

    print("\n🔄 Processing through all phases...")
    print("   Phase 1: NLP Analysis (✅ Already completed)")
    print("   Phase 2: Scene Building...")
    print("   Phase 3: Validation...")
    print("   Phase 4: Layout...")
    print("   Phase 5: Rendering...")

    try:
        # Run full pipeline
        result = pipeline.generate(
            problem_text=QUESTION_8_TEXT,
            domain="electronics",
            problem_id="question_8_capacitor"
        )

        print("\n✅ Pipeline execution complete!")

        # Display results
        print_section("STEP 4: RESULTS", "-")

        if result['success']:
            print("\n✅ DIAGRAM GENERATION SUCCESSFUL!")
            print(f"\n📁 Output Files:")
            print(f"   SVG Diagram: {result['output_path']}")

            # Display statistics
            if 'statistics' in result:
                stats = result['statistics']
                print(f"\n📊 Processing Statistics:")
                print(f"   Total Time: {stats.get('total_time_seconds', 0):.2f}s")
                print(f"   Scene Objects: {stats.get('num_objects', 0)}")
                print(f"   Relationships: {stats.get('num_relationships', 0)}")
                print(f"   Layout Nodes: {stats.get('num_layout_nodes', 0)}")

            # Display scene information
            if 'scene' in result:
                scene = result['scene']
                print(f"\n🎬 Scene Information:")
                print(f"   Scene Type: {scene.scene_type}")
                print(f"   Objects: {len(scene.objects)}")

                # List objects
                print(f"\n   Objects Created:")
                for i, obj in enumerate(scene.objects[:10], 1):
                    obj_type = obj.get('type', 'unknown')
                    obj_id = obj.get('id', 'N/A')
                    print(f"      {i}. {obj_type} (id: {obj_id})")

                if len(scene.objects) > 10:
                    print(f"      ... and {len(scene.objects) - 10} more")

            # Save results summary
            output_dir = Path("output/question8_diagram")
            output_dir.mkdir(parents=True, exist_ok=True)

            summary_file = output_dir / "generation_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)

            print(f"\n   Generation Summary: {summary_file}")

            print("\n🎉 SUCCESS! Diagram generated successfully!")
            print(f"\n   Open the SVG file to view: {result['output_path']}")

        else:
            print("\n❌ DIAGRAM GENERATION FAILED")
            print(f"\n   Error: {result.get('error', 'Unknown error')}")

            if 'phase' in result:
                print(f"   Failed at: Phase {result['phase']}")

            if 'traceback' in result:
                print(f"\n   Traceback:")
                print(result['traceback'])

    except Exception as e:
        print(f"\n❌ Error during pipeline execution:")
        print(f"   {type(e).__name__}: {str(e)}")

        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()

        return 1

    # Final summary
    print_section("COMPLETE", "=")

    print("\n📊 PROCESSING SUMMARY:")
    print("   ✓ Phase 1: NLP Analysis (from cache)")
    print("   ✓ Phase 2: Scene Building")
    print("   ✓ Phase 3: Validation")
    print("   ✓ Phase 4: Layout")
    print("   ✓ Phase 5: Rendering")

    print(f"\n📁 ALL OUTPUT FILES:")
    print(f"   NLP Analysis: output/question8_nlp_results/nlp_analysis.json")
    print(f"   Canonical Spec: output/question8_nlp_results/canonical_spec.json")
    print(f"   Scene Description: output/question8_nlp_results/scene_description.json")
    if result['success']:
        print(f"   SVG Diagram: {result['output_path']}")
        print(f"   Generation Summary: output/question8_diagram/generation_summary.json")

    print("\n✅ Question 8 diagram generation complete!")

    return 0 if result.get('success', False) else 1


if __name__ == "__main__":
    sys.exit(main())
