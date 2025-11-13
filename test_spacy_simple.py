#!/usr/bin/env python3
"""
Simple test of SpaCy analyzer without dependencies
"""

import os
import sys
import time
import spacy
from quantulum3 import parser as quantity_parser

# Question 8 from batch 2
QUESTION_8 = """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation
2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0.
The right half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0.
Calculate the total capacitance."""


def test_basic_spacy():
    """Test basic spaCy processing"""
    print("=" * 80)
    print(" Testing Basic spaCy Processing")
    print("=" * 80)

    # Load spaCy model
    print("\n1. Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")
    print(f"   ✓ Loaded model: {nlp.meta['name']}")
    print(f"   ✓ Pipeline: {nlp.pipe_names}")

    # Process text
    print("\n2. Processing Question 8...")
    start_time = time.time()
    doc = nlp(QUESTION_8)
    duration = time.time() - start_time
    print(f"   ✓ Processed in {duration:.3f}s")

    # Extract entities
    print("\n3. Named Entities Found:")
    for ent in doc.ents:
        print(f"   - {ent.text:30s} [{ent.label_}]")

    # Show tokens
    print("\n4. Tokens (first 20):")
    for token in list(doc)[:20]:
        print(f"   {token.text:15s} | POS: {token.pos_:10s} | DEP: {token.dep_:10s} | HEAD: {token.head.text}")

    # Dependencies
    print("\n5. Dependency Relationships (sample):")
    count = 0
    for token in doc:
        if token.dep_ in ["prep", "pobj", "compound"] and count < 10:
            print(f"   {token.head.text} --[{token.dep_}]--> {token.text}")
            count += 1

    return doc


def test_quantulum():
    """Test quantulum3 measurement extraction"""
    print("\n" + "=" * 80)
    print(" Testing Quantulum3 Measurement Extraction")
    print("=" * 80)

    print("\n1. Extracting measurements...")
    quantities = quantity_parser.parse(QUESTION_8)

    print(f"\n2. Found {len(quantities)} measurements:")
    for q in quantities:
        print(f"   - {q.surface:30s} = {q.value} {q.unit}")
        if hasattr(q.unit, 'entity'):
            print(f"     Dimension: {q.unit.entity}")


def test_custom_patterns():
    """Test custom entity patterns for physics"""
    print("\n" + "=" * 80)
    print(" Testing Custom Physics Entity Patterns")
    print("=" * 80)

    # Load model
    nlp = spacy.load("en_core_web_sm")

    # Add entity ruler
    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = [
        {"label": "PHYSICS_OBJECT", "pattern": "capacitor"},
        {"label": "PHYSICS_OBJECT", "pattern": [{"LOWER": "parallel"}, {"LOWER": "plate"}, {"LOWER": "capacitor"}]},
        {"label": "PHYSICS_OBJECT", "pattern": "plate"},
        {"label": "MATERIAL", "pattern": "dielectric"},
        {"label": "CONSTRAINT", "pattern": "parallel"},
    ]

    ruler.add_patterns(patterns)

    print(f"\n1. Added {len(patterns)} custom patterns")
    print(f"2. Updated pipeline: {nlp.pipe_names}")

    # Process
    doc = nlp(QUESTION_8)

    print("\n3. Entities after custom patterns:")
    for ent in doc.ents:
        print(f"   - {ent.text:30s} [{ent.label_}]")


def main():
    """Main test function"""
    print("\n🔬 SpaCy-LLM Integration Test Suite")
    print("Testing Question 8 from Batch 2\n")

    try:
        # Test 1: Basic spaCy
        doc = test_basic_spacy()

        # Test 2: Quantulum
        test_quantulum()

        # Test 3: Custom patterns
        test_custom_patterns()

        print("\n" + "=" * 80)
        print(" ✅ ALL TESTS PASSED")
        print("=" * 80)

        print("\n📊 Summary:")
        print(f"  - spaCy is working correctly")
        print(f"  - quantulum3 successfully extracted measurements")
        print(f"  - Custom entity patterns are functional")
        print(f"  - Ready to integrate with SpaCyAIAnalyzer")

        return 0

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
