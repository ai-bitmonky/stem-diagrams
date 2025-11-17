"""
Test Local AI Analyzer with Pattern-Based Extraction
====================================================

Tests the enhanced LocalAIAnalyzer with integrated PatternBasedExtractor
to verify that objects are extracted with correct properties.
"""

from core.local_ai_analyzer import LocalAIAnalyzer

# Test problems
problems = [
    ("Q7 - Series Capacitors", """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other."""),

    ("Q8 - Multi-Region Capacitor", """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation
2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0.
The right half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0."""),

    ("Q6 - Capacitor with Dielectric", """A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected."""),
]

def main():
    print("=" * 80)
    print("TESTING LOCAL AI ANALYZER WITH PATTERN-BASED EXTRACTION")
    print("=" * 80)
    print()

    try:
        analyzer = LocalAIAnalyzer(verbose=True)
        print()

        for name, problem in problems:
            print("\n" + "=" * 80)
            print(f"TEST: {name}")
            print("=" * 80)
            print(f"Problem: {problem[:80]}...\n")

            try:
                spec = analyzer.analyze(problem)

                print(f"\n✅ ANALYSIS COMPLETE")
                print(f"   Domain: {spec.domain.value}")
                print(f"   Objects: {len(spec.objects)}")
                print(f"   Confidence: {spec.confidence:.2f}")
                print()

                if spec.objects:
                    print("   EXTRACTED OBJECTS:")
                    for obj in spec.objects:
                        props = obj.get('properties', {})
                        props_str = ', '.join(f"{k}={v}" for k, v in props.items()) if props else "no properties"
                        print(f"     • {obj['id']} ({obj['type']}): {props_str}")
                else:
                    print("   ❌ NO OBJECTS EXTRACTED!")

            except Exception as e:
                print(f"\n❌ FAILED: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("TESTING COMPLETE")
        print("=" * 80)

    except ImportError as e:
        print(f"\n❌ Cannot run test: {e}")
        print("   Make sure spaCy is installed: pip install spacy")
        print("   Download model: python -m spacy download en_core_web_sm")

if __name__ == "__main__":
    main()
