#!/usr/bin/env python3
"""
Test script to compare SpaCy-based analyzer with current approach on Question 8
"""

import os
import sys
import time
import json
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly to avoid __init__ issues
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load modules
core_path = Path(__file__).parent / "core"
spacy_analyzer_module = load_module("spacy_ai_analyzer", core_path / "spacy_ai_analyzer.py")
universal_analyzer_module = load_module("universal_ai_analyzer", core_path / "universal_ai_analyzer.py")

SpaCyAIAnalyzer = spacy_analyzer_module.SpaCyAIAnalyzer
UniversalAIAnalyzer = universal_analyzer_module.UniversalAIAnalyzer

# Question 8 from batch 2
QUESTION_8 = """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation
2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0.
The right half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0.
Calculate the total capacitance."""


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def print_results(title: str, spec, duration: float):
    """Print analysis results"""
    print(f"\n{title}")
    print(f"Duration: {duration:.2f}s")
    print(f"Domain: {spec.domain}")
    print(f"Objects: {len(spec.objects)}")
    print(f"Relationships: {len(spec.relationships)}")
    print(f"Complexity: {spec.complexity_score:.2f}")
    print(f"Confidence: {getattr(spec, 'confidence', 'N/A')}")

    print("\n📦 Objects:")
    for i, obj in enumerate(spec.objects[:5]):  # Show first 5
        print(f"  {i+1}. {obj.get('id', 'N/A')} ({obj.get('type', 'N/A')})")
        if 'properties' in obj:
            for key, val in list(obj['properties'].items())[:3]:  # Show first 3 properties
                print(f"      {key}: {val}")

    if len(spec.objects) > 5:
        print(f"  ... and {len(spec.objects) - 5} more")

    print("\n🔗 Relationships:")
    for i, rel in enumerate(spec.relationships[:5]):  # Show first 5
        print(f"  {i+1}. {rel.get('type', 'N/A')}: {rel.get('subject', 'N/A')} → {rel.get('target', 'N/A')}")

    if len(spec.relationships) > 5:
        print(f"  ... and {len(spec.relationships) - 5} more")


def compare_results(spec1, spec2, duration1: float, duration2: float):
    """Compare two specs"""
    print_section("COMPARISON SUMMARY")

    print("Metric                    | Current     | SpaCy-LLM   | Improvement")
    print("-" * 70)
    print(f"Processing Time          | {duration1:6.2f}s    | {duration2:6.2f}s    | {((duration1-duration2)/duration1)*100:+.1f}%")
    print(f"Objects Extracted        | {len(spec1.objects):6d}      | {len(spec2.objects):6d}      | {len(spec2.objects)-len(spec1.objects):+d}")
    print(f"Relationships Found      | {len(spec1.relationships):6d}      | {len(spec2.relationships):6d}      | {len(spec2.relationships)-len(spec1.relationships):+d}")
    print(f"Complexity Score         | {spec1.complexity_score:6.2f}      | {spec2.complexity_score:6.2f}      | {spec2.complexity_score-spec1.complexity_score:+.2f}")

    # Accuracy metrics (subjective analysis)
    print("\nQualitative Assessment:")

    # Check for expected entities
    expected_entities = ['capacitor', 'plate', 'dielectric', 'area', 'separation']

    def count_matches(spec, keywords):
        """Count how many expected keywords are found in objects"""
        all_text = ' '.join([
            obj.get('id', '') + ' ' + obj.get('text', '') + ' ' + str(obj.get('properties', {}))
            for obj in spec.objects
        ]).lower()
        return sum(1 for kw in keywords if kw in all_text)

    current_matches = count_matches(spec1, expected_entities)
    spacy_matches = count_matches(spec2, expected_entities)

    print(f"  Expected entities found (/{len(expected_entities)})")
    print(f"    Current:   {current_matches}")
    print(f"    SpaCy-LLM: {spacy_matches}")

    # Winner determination
    print("\n🏆 Winner:")
    scores = {
        'current': 0,
        'spacy': 0
    }

    if len(spec2.objects) > len(spec1.objects):
        scores['spacy'] += 1
        print("  ✓ More objects extracted: SpaCy-LLM")
    elif len(spec1.objects) > len(spec2.objects):
        scores['current'] += 1
        print("  ✓ More objects extracted: Current")

    if len(spec2.relationships) > len(spec1.relationships):
        scores['spacy'] += 1
        print("  ✓ More relationships found: SpaCy-LLM")
    elif len(spec1.relationships) > len(spec2.relationships):
        scores['current'] += 1
        print("  ✓ More relationships found: Current")

    if duration2 < duration1:
        scores['spacy'] += 1
        print("  ✓ Faster processing: SpaCy-LLM")
    else:
        scores['current'] += 1
        print("  ✓ Faster processing: Current")

    if spacy_matches > current_matches:
        scores['spacy'] += 1
        print("  ✓ More expected entities: SpaCy-LLM")
    elif current_matches > spacy_matches:
        scores['current'] += 1
        print("  ✓ More expected entities: Current")

    print(f"\nFinal Score: Current={scores['current']}, SpaCy-LLM={scores['spacy']}")

    if scores['spacy'] > scores['current']:
        print("🎉 SpaCy-LLM approach is BETTER!")
    elif scores['current'] > scores['spacy']:
        print("📊 Current approach is BETTER")
    else:
        print("⚖️  Both approaches are EQUAL")


def main():
    """Main test function"""
    print_section("SpaCy-LLM Analyzer Comparison Test")

    # Get API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY environment variable not set")
        return 1

    print(f"Problem: {QUESTION_8[:100]}...")

    # Test 1: Current approach
    print_section("TEST 1: Current Approach (Direct API)")

    try:
        analyzer1 = UniversalAIAnalyzer(
            api_key=api_key,
            model="deepseek-chat",
            timeout=60,
            max_retries=3
        )

        start_time = time.time()
        spec1 = analyzer1.analyze(QUESTION_8)
        duration1 = time.time() - start_time

        print_results("✅ Current Approach Results:", spec1, duration1)

    except Exception as e:
        print(f"❌ Error with current approach: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 2: SpaCy-LLM approach
    print_section("TEST 2: SpaCy-LLM Approach")

    try:
        analyzer2 = SpaCyAIAnalyzer(
            api_key=api_key,
            model="deepseek-chat",
            enable_caching=True
        )

        start_time = time.time()
        spec2 = analyzer2.analyze(QUESTION_8)
        duration2 = time.time() - start_time

        print_results("✅ SpaCy-LLM Results:", spec2, duration2)

    except Exception as e:
        print(f"❌ Error with SpaCy-LLM approach: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Comparison
    compare_results(spec1, spec2, duration1, duration2)

    # Test caching (run SpaCy analyzer again)
    print_section("TEST 3: Caching Performance")

    start_time = time.time()
    spec2_cached = analyzer2.analyze(QUESTION_8)
    duration_cached = time.time() - start_time

    print(f"First run:   {duration2:.2f}s")
    print(f"Cached run:  {duration_cached:.2f}s")
    print(f"Speed up:    {((duration2 - duration_cached) / duration2) * 100:.1f}%")

    if duration_cached < duration2 * 0.5:
        print("✅ Caching is working effectively!")
    else:
        print("⚠️  Caching might not be working as expected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
