"""
Enhanced Diagram Generator - Complete Phase 2+ Implementation
=============================================================

This is the enhanced version that integrates:
- Advanced scene building with physics rules
- Intelligent layout engine
- Enhanced component rendering
- Validation and refinement
- Better NLP interpretation

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

import spacy
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from core.universal_scene_format import UniversalScene
from core.universal_svg_renderer import UniversalSVGRenderer
from core.advanced_scene_builder import build_advanced_scene


class EnhancedNLPPipeline:
    """
    Enhanced NLP Pipeline with better entity and relationship extraction
    """

    def __init__(self):
        print("🚀 Initializing Enhanced NLP Pipeline...")
        self.nlp = spacy.load("en_core_web_sm")
        print("✅ Enhanced pipeline ready\n")

    def process(self, text: str) -> Dict[str, Any]:
        """Process text with enhanced extraction"""
        start_time = time.time()

        doc = self.nlp(text)

        # Enhanced domain classification
        domain = self._classify_domain_enhanced(doc, text)

        # Enhanced entity extraction
        entities = self._extract_entities_enhanced(doc, text)

        # Enhanced relationship extraction
        relationships = self._extract_relationships_enhanced(doc, entities, text)

        metadata = {
            'num_entities': len(entities),
            'num_relationships': len(relationships),
            'processing_time': time.time() - start_time,
            'sentence_count': len(list(doc.sents)),
            'token_count': len(doc)
        }

        return {
            'domain': domain,
            'entities': entities,
            'relationships': relationships,
            'metadata': metadata,
            'raw_text': text
        }

    def _classify_domain_enhanced(self, doc, text: str) -> str:
        """Enhanced domain classification"""
        text_lower = text.lower()

        # More sophisticated domain detection
        domain_scores = {
            'electronics': 0,
            'chemistry': 0,
            'biology': 0,
            'mathematics': 0,
            'physics': 0
        }

        # Electronics keywords with weights
        electronics_kw = {
            'circuit': 3, 'capacitor': 3, 'resistor': 3, 'voltage': 2,
            'current': 2, 'battery': 2, 'inductor': 2, 'dielectric': 2,
            'charge': 1, 'potential': 1, 'electric': 1
        }

        for kw, weight in electronics_kw.items():
            if kw in text_lower:
                domain_scores['electronics'] += weight

        # Physics keywords
        physics_kw = {
            'force': 2, 'mass': 2, 'acceleration': 2, 'friction': 2,
            'velocity': 2, 'energy': 1, 'momentum': 1
        }

        for kw, weight in physics_kw.items():
            if kw in text_lower:
                domain_scores['physics'] += weight

        # Chemistry keywords
        chemistry_kw = {
            'atom': 2, 'molecule': 2, 'bond': 2, 'reaction': 2,
            'element': 1, 'compound': 1
        }

        for kw, weight in chemistry_kw.items():
            if kw in text_lower:
                domain_scores['chemistry'] += weight

        # Return domain with highest score
        max_score = max(domain_scores.values())
        if max_score > 0:
            return max(domain_scores, key=domain_scores.get)
        return 'physics'

    def _extract_entities_enhanced(self, doc, text: str) -> List[Dict]:
        """Enhanced entity extraction"""
        entities = []

        # spaCy NER
        for ent in doc.ents:
            if ent.label_ in ['CARDINAL', 'QUANTITY', 'PRODUCT', 'ORDINAL']:
                entity = {
                    'id': f"entity_{len(entities)}",
                    'type': ent.label_,
                    'text': ent.text,
                    'properties': {
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': 0.85,
                        'method': 'spacy_ner'
                    }
                }
                entities.append(entity)

        # Enhanced regex patterns for scientific values
        import re

        # Pattern for values with units
        value_unit_pattern = r'(\d+\.?\d*)\s*(V|A|Ω|F|H|W|J|N|m|kg|s|μF|mF|pF|nF|mA|μA|kΩ|MΩ|cm|mm|km|μC|nC|pC|mJ)'
        matches = re.finditer(value_unit_pattern, text)

        for match in matches:
            entity = {
                'id': f"entity_{len(entities)}",
                'type': 'MEASUREMENT',
                'text': match.group(0),
                'properties': {
                    'value': float(match.group(1)),
                    'unit': match.group(2),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.95,
                    'method': 'regex_enhanced'
                }
            }
            entities.append(entity)

        return entities

    def _extract_relationships_enhanced(self, doc, entities: List[Dict],
                                       text: str) -> List[Dict]:
        """Enhanced relationship extraction"""
        relationships = []

        # Proximity-based relationships
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:i+3]:
                rel = {
                    'type': 'RELATED_TO',
                    'subject': ent1['text'],
                    'target': ent2['text'],
                    'properties': {
                        'confidence': 0.5,
                        'method': 'proximity'
                    }
                }
                relationships.append(rel)

        # Pattern-based relationships (e.g., A = B)
        import re
        equals_pattern = r'([A-Za-z_]\d?)\s*=\s*([^,\.]+)'
        matches = re.finditer(equals_pattern, text)

        for match in matches:
            rel = {
                'type': 'EQUALS',
                'subject': match.group(1),
                'target': match.group(2).strip(),
                'properties': {
                    'confidence': 0.95,
                    'method': 'pattern_match'
                }
            }
            relationships.append(rel)

        return relationships


class EnhancedDiagramGenerator:
    """
    Enhanced Diagram Generator with all Phase 2+ features
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize enhanced components
        self.nlp_pipeline = EnhancedNLPPipeline()
        self.svg_renderer = UniversalSVGRenderer()

        print("✅ Enhanced Diagram Generator initialized\n")

    def generate(self, problem_text: str, output_filename: Optional[str] = None,
                save_files: bool = True) -> Dict[str, Any]:
        """
        Generate diagram using enhanced pipeline

        This uses:
        - Enhanced NLP analysis
        - Advanced scene building with physics rules
        - Intelligent layout
        - Professional rendering
        """
        print("=" * 70)
        print("ENHANCED DIAGRAM GENERATOR (Phase 2+)")
        print("=" * 70)
        print(f"\n📋 Problem: {problem_text[:100]}...\n")

        start_time = time.time()
        result = {'success': False, 'error': None}

        try:
            # Step 1: Enhanced NLP Analysis
            print("Step 1: Enhanced NLP Analysis...")
            nlp_results = self.nlp_pipeline.process(problem_text)
            print(f"  ✅ Domain: {nlp_results['domain']} (enhanced classification)")
            print(f"  ✅ Entities: {nlp_results['metadata']['num_entities']} (with measurements)")
            print(f"  ✅ Relationships: {nlp_results['metadata']['num_relationships']}")
            print(f"  ✅ Processing time: {nlp_results['metadata']['processing_time']:.3f}s\n")

            # Step 2: Advanced Scene Building
            print("Step 2: Advanced Scene Building (with physics rules)...")
            scene = build_advanced_scene(nlp_results, problem_text, nlp_results['domain'])
            print(f"  ✅ Scene created: {scene.title}")
            print(f"  ✅ Objects: {len(scene.objects)} (intelligently positioned)")
            print(f"  ✅ Relationships: {len(scene.relationships)} (validated)")
            print(f"  ✅ Annotations: {len(scene.annotations)} (informative)")

            # Check for validation warnings
            if 'validation_warnings' in scene.metadata:
                print(f"  ⚠️  Validation warnings: {len(scene.metadata['validation_warnings'])}")

            print()

            # Step 3: Enhanced SVG Rendering
            print("Step 3: Enhanced SVG Rendering...")
            svg_output = self.svg_renderer.render(scene)
            print(f"  ✅ SVG generated ({len(svg_output)} characters)\n")

            # Step 4: Save files
            files_saved = {}
            if save_files:
                print("Step 4: Saving files...")

                if not output_filename:
                    filename_base = f"diagram_{hash(problem_text) % 10000:04d}"
                else:
                    filename_base = output_filename

                # Save SVG
                svg_path = self.output_dir / f"{filename_base}.svg"
                with open(svg_path, 'w') as f:
                    f.write(svg_output)
                files_saved['svg'] = str(svg_path)
                print(f"  ✅ SVG: {svg_path}")

                # Save scene JSON
                json_path = self.output_dir / f"{filename_base}_scene.json"
                scene.save(str(json_path))
                files_saved['scene_json'] = str(json_path)
                print(f"  ✅ Scene: {json_path}")

                # Save NLP results
                nlp_path = self.output_dir / f"{filename_base}_nlp.json"
                with open(nlp_path, 'w') as f:
                    json.dump(nlp_results, f, indent=2)
                files_saved['nlp_results'] = str(nlp_path)
                print(f"  ✅ NLP: {nlp_path}\n")

            total_time = time.time() - start_time

            result = {
                'success': True,
                'svg': svg_output,
                'scene': scene,
                'scene_json': scene.to_json(),
                'nlp_results': nlp_results,
                'metadata': {
                    'total_time': total_time,
                    'nlp_time': nlp_results['metadata']['processing_time'],
                    'domain': nlp_results['domain'],
                    'num_objects': len(scene.objects),
                    'num_relationships': len(scene.relationships),
                    'num_annotations': len(scene.annotations),
                    'validation_warnings': scene.metadata.get('validation_warnings', [])
                },
                'files': files_saved if save_files else {}
            }

            print("=" * 70)
            print(f"✅ SUCCESS! Enhanced diagram generated in {total_time:.3f}s")
            print("=" * 70)

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        return result


if __name__ == "__main__":
    print("=" * 70)
    print("ENHANCED DIAGRAM GENERATOR - TEST")
    print("=" * 70 + "\n")

    # Initialize enhanced generator
    generator = EnhancedDiagramGenerator(output_dir="output/enhanced_test")

    # Test with a complex capacitor problem
    test_problem = """A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"""

    result = generator.generate(test_problem, "test_enhanced_circuit")

    if result['success']:
        print(f"\n✅ Test PASSED")
        print(f"   Domain: {result['metadata']['domain']}")
        print(f"   Objects: {result['metadata']['num_objects']}")
        print(f"   Relationships: {result['metadata']['num_relationships']}")
        print(f"   Annotations: {result['metadata']['num_annotations']}")
        print(f"   Processing time: {result['metadata']['total_time']:.3f}s")
    else:
        print(f"\n❌ Test FAILED: {result['error']}")

    print("\n" + "=" * 70)
    print("Enhanced pipeline test complete!")
    print("=" * 70)
