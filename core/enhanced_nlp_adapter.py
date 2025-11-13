"""
Enhanced NLP Adapter - Integration Layer
=========================================

Adapts EnhancedNLPCoordinator to work with existing UnifiedNLPPipeline interface.

Provides backward compatibility while enabling enhanced text understanding:
- Uses enhanced NLP coordinator for better extraction
- Maintains existing interface format
- Can be dropped in as replacement for baseline NLP

Author: Universal Diagram Generator Team
Date: November 6, 2025
"""

from typing import Dict, List, Any, Optional
import time
import sys
from pathlib import Path

# Handle imports for both package and standalone use
if __name__ == "__main__":
    # Running standalone - add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.enhanced_nlp_coordinator import (
        EnhancedNLPCoordinator,
        create_enhanced_nlp_coordinator
    )
else:
    # Running as package
    from .enhanced_nlp_coordinator import (
        EnhancedNLPCoordinator,
        create_enhanced_nlp_coordinator
    )


class EnhancedNLPAdapter:
    """
    Adapter that makes EnhancedNLPCoordinator compatible with existing pipeline.

    Usage:
        # Instead of baseline NLP:
        nlp_results = baseline_nlp.process(text)

        # Use enhanced NLP:
        enhanced_nlp = EnhancedNLPAdapter()
        nlp_results = enhanced_nlp.process(text)  # Same interface!
    """

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize adapter with enhanced NLP coordinator"""
        self.coordinator = create_enhanced_nlp_coordinator()
        print("✅ Enhanced NLP Adapter initialized")
        print("   - STEM Unit Extractor: Ready")
        print("   - spaCy NER: Ready")
        print("   - Domain Classifier: Ready")

    def process(self, problem_text: str) -> Dict[str, Any]:
        """
        Process text and return results in baseline-compatible format.

        Args:
            problem_text: Problem description text

        Returns:
            Dict with entities, quantities, domain, etc. (compatible with baseline)
        """
        start_time = time.time()

        # Use enhanced coordinator
        result = self.coordinator.process(problem_text)

        # Convert to baseline-compatible format
        baseline_format = {
            'text': result.text,
            'domain': result.domain,
            'domain_confidence': result.domain_confidence,

            # Entities in baseline format
            'entities': [
                {
                    'text': e.text,
                    'label': e.label,
                    'start': e.start_char,
                    'end': e.end_char,
                    'type': self._map_label_to_type(e.label),
                    'confidence': e.confidence
                }
                for e in result.entities
            ],

            # Quantities (enhanced feature!)
            'quantities': [
                {
                    'value': q.value,
                    'unit': q.unit,
                    'text': q.raw_text,
                    'type': q.entity_type,
                    'start': q.start_char,
                    'end': q.end_char
                }
                for q in result.quantities
            ],

            # Additional metadata
            'metadata': {
                **result.metadata,
                'processing_time': time.time() - start_time,
                'nlp_mode': 'enhanced',
                'tools_used': result.metadata.get('tools_used', [])
            },

            # For backward compatibility
            'num_entities': len(result.entities),
            'num_quantities': len(result.quantities),
        }

        return baseline_format

    def _map_label_to_type(self, spacy_label: str) -> str:
        """Map spaCy labels to baseline entity types"""
        mapping = {
            'CARDINAL': 'NUMBER',
            'QUANTITY': 'QUANTITY',
            'PERCENT': 'QUANTITY',
            'MONEY': 'QUANTITY',
            'ORDINAL': 'NUMBER',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'PERSON': 'PERSON',
            'ORG': 'ORGANIZATION',
            'GPE': 'LOCATION',
            'LOC': 'LOCATION',
            'PRODUCT': 'OBJECT',
            'EVENT': 'EVENT',
            'WORK_OF_ART': 'OBJECT',
            'LAW': 'CONCEPT',
            'LANGUAGE': 'CONCEPT',
            'NORP': 'CONCEPT',
            'FAC': 'LOCATION',
        }
        return mapping.get(spacy_label, 'UNKNOWN')


# ============================================================================
# Factory Functions
# ============================================================================

def create_enhanced_nlp_adapter() -> EnhancedNLPAdapter:
    """Factory function to create enhanced NLP adapter"""
    return EnhancedNLPAdapter()


# ============================================================================
# Comparison Helper
# ============================================================================

def compare_nlp_modes(problem_text: str, baseline_nlp=None) -> Dict:
    """
    Compare baseline vs enhanced NLP on a problem.

    Useful for benchmarking and validation.
    """
    print("=" * 70)
    print("NLP MODE COMPARISON")
    print("=" * 70)
    print(f"\nProblem: {problem_text}\n")

    # Enhanced NLP
    enhanced = create_enhanced_nlp_adapter()
    enhanced_result = enhanced.process(problem_text)

    print("ENHANCED NLP:")
    print(f"  Domain: {enhanced_result['domain']} (conf: {enhanced_result['domain_confidence']:.2f})")
    print(f"  Quantities: {enhanced_result['num_quantities']}")
    for q in enhanced_result['quantities']:
        print(f"    - {q['value']} {q['unit']} ({q['type']})")
    print(f"  Entities: {enhanced_result['num_entities']}")
    print(f"  Time: {enhanced_result['metadata']['processing_time']:.3f}s")

    if baseline_nlp:
        baseline_result = baseline_nlp.process(problem_text)
        print("\nBASELINE NLP:")
        print(f"  Domain: {baseline_result.get('domain', 'N/A')}")
        print(f"  Entities: {len(baseline_result.get('entities', []))}")
        print(f"  Time: {baseline_result.get('metadata', {}).get('processing_time', 0):.3f}s")

        # Compare
        print("\nIMPROVEMENTS:")
        enhanced_q = enhanced_result['num_quantities']
        baseline_q = len([e for e in baseline_result.get('entities', [])
                         if e.get('type') == 'QUANTITY'])
        if enhanced_q > baseline_q:
            print(f"  ✅ +{enhanced_q - baseline_q} more quantities extracted")

    print("=" * 70)
    return enhanced_result


if __name__ == "__main__":
    # Test the adapter
    print("=" * 70)
    print("ENHANCED NLP ADAPTER TEST")
    print("=" * 70)

    adapter = create_enhanced_nlp_adapter()

    test_problems = [
        "A 10μF capacitor connected to a 12V battery through a 100Ω resistor",
        "A 5kg block rests on a 30° incline",
        "Apply 20N force to accelerate a 2kg mass"
    ]

    for i, problem in enumerate(test_problems, 1):
        print(f"\n[Test {i}]")
        result = adapter.process(problem)

        print(f"Problem: {problem}")
        print(f"Domain: {result['domain']} (confidence: {result['domain_confidence']:.2f})")
        print(f"Quantities extracted: {result['num_quantities']}")
        for q in result['quantities']:
            print(f"  - {q['value']} {q['unit']} ({q['type']})")
        print(f"Processing time: {result['metadata']['processing_time']:.3f}s")

    print("\n" + "=" * 70)
    print("✅ Enhanced NLP Adapter working!")
    print("   Ready for integration with UnifiedPipeline")
