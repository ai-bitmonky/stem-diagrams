"""
Test Pattern-Based Extraction with Batch 2 Questions
=====================================================

Tests the new pattern-based extractor with questions 7 and 8 from batch 2
to verify that it extracts the correct components and generates accurate diagrams.
"""

from unified_diagram_generator import UnifiedDiagramGenerator

# Test questions
QUESTIONS = [
    {
        'id': 'question_7_test',
        'number': 7,
        'title': 'Series Capacitors Reconnected',
        'text': """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"""
    },
    {
        'id': 'question_8_test',
        'number': 8,
        'title': 'Multi-Region Capacitor',
        'text': """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation
2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0.
The right half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0.
Calculate the total capacitance."""
    }
]

def main():
    print("=" * 80)
    print("TESTING PATTERN-BASED EXTRACTION")
    print("=" * 80)
    print()

    generator = UnifiedDiagramGenerator(output_dir="output/pattern_test")

    for question in QUESTIONS:
        print("\n" + "=" * 80)
        print(f"QUESTION {question['number']}: {question['title']}")
        print("=" * 80)
        print(f"\n{question['text']}\n")

        try:
            result = generator.generate(
                problem_text=question['text'],
                output_filename=question['id'],
                save_files=True
            )

            if result['success']:
                print(f"\n✅ SUCCESS!")
                print(f"   SVG saved to: {result['files']['svg']}")
                print(f"   Objects: {result['metadata']['num_objects']}")
                print(f"   Relationships: {result['metadata']['num_relationships']}")
            else:
                print(f"\n❌ FAILED: {result['error']}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
