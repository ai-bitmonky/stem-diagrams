"""
Unified Diagram Generator - Production Pipeline
===============================================

This is the complete end-to-end pipeline for generating STEM diagrams from text.

Pipeline Flow:
1. Text Input → NLP Analysis (spaCy + custom extractors)
2. NLP Results → Subject Interpreter (domain-specific)
3. UniversalScene → SVG Renderer (professional output)
4. SVG Output + JSON scene file

Features:
- 100% offline operation
- Multi-domain support (Physics, Chemistry, Biology, Math, Electronics)
- Professional SVG output
- Fast processing (<1 second per diagram)
- Zero API costs

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

import spacy
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import our custom modules
from core.universal_scene_format import UniversalScene
from core.universal_svg_renderer import UniversalSVGRenderer
from core.subject_interpreters import get_interpreter

# Import NLP components
import sys
sys.path.append(str(Path(__file__).parent))


class SimpleNLPPipeline:
    """
    Simplified NLP Pipeline for diagram generation
    Based on the successful Batch 2 implementation
    """

    def __init__(self):
        print("🚀 Initializing NLP Pipeline...")
        self.nlp = spacy.load("en_core_web_sm")
        print("✅ Pipeline ready\n")

    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text and extract entities, relationships, and domain

        Args:
            text: Problem text to analyze

        Returns:
            Dictionary with 'domain', 'entities', 'relationships', 'metadata'
        """
        start_time = time.time()

        # Process with spaCy
        doc = self.nlp(text)

        # Extract domain
        domain = self._classify_domain(doc)

        # Extract entities
        entities = self._extract_entities(doc, domain)

        # Extract relationships
        relationships = self._extract_relationships(doc, entities)

        # Metadata
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
            'metadata': metadata
        }

    def _classify_domain(self, doc) -> str:
        """Classify the domain based on keywords"""
        text_lower = doc.text.lower()

        # Domain keywords
        domains = {
            'electronics': ['circuit', 'capacitor', 'resistor', 'voltage', 'current', 'battery',
                          'inductor', 'diode', 'transistor', 'wire', 'ohm', 'farad'],
            'chemistry': ['atom', 'molecule', 'bond', 'reaction', 'element', 'compound',
                         'ionic', 'covalent', 'chemical', 'electron shell'],
            'biology': ['cell', 'dna', 'protein', 'organism', 'tissue', 'organ',
                       'mitochondria', 'nucleus', 'membrane', 'chromosome'],
            'mathematics': ['equation', 'function', 'graph', 'variable', 'derivative',
                          'integral', 'theorem', 'proof', 'geometric'],
            'physics': ['force', 'mass', 'acceleration', 'energy', 'momentum', 'velocity',
                       'friction', 'gravity', 'newton', 'joule']
        }

        # Count keyword matches
        scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[domain] = score

        # Return domain with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'physics'  # default

    def _extract_entities(self, doc, domain: str) -> List[Dict]:
        """Extract entities using spaCy NER"""
        entities = []

        for ent in doc.ents:
            if ent.label_ in ['CARDINAL', 'QUANTITY', 'PRODUCT']:
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

        return entities

    def _extract_relationships(self, doc, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []

        # Simple proximity-based relationships
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:i+3]:  # Check next 2 entities
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

        return relationships


class UnifiedDiagramGenerator:
    """
    Main class for the unified diagram generation pipeline

    Usage:
        generator = UnifiedDiagramGenerator()
        result = generator.generate(problem_text)
        # result contains SVG string, scene JSON, and metadata
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the diagram generator

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize components
        self.nlp_pipeline = SimpleNLPPipeline()
        self.svg_renderer = UniversalSVGRenderer()

        print("✅ Unified Diagram Generator initialized\n")

    def generate(self, problem_text: str, output_filename: Optional[str] = None,
                save_files: bool = True) -> Dict[str, Any]:
        """
        Generate diagram from problem text

        Args:
            problem_text: The problem text to convert to a diagram
            output_filename: Optional custom filename (without extension)
            save_files: Whether to save SVG and JSON files to disk

        Returns:
            Dictionary containing:
            - 'svg': SVG string
            - 'scene': UniversalScene object
            - 'scene_json': Scene as JSON string
            - 'nlp_results': NLP analysis results
            - 'metadata': Generation metadata
            - 'files': Dict of saved file paths (if save_files=True)
        """
        print("=" * 70)
        print("UNIFIED DIAGRAM GENERATOR")
        print("=" * 70)
        print(f"\n📋 Problem: {problem_text[:100]}...\n")

        start_time = time.time()
        result = {
            'success': False,
            'error': None
        }

        try:
            # Step 1: NLP Analysis
            print("Step 1: NLP Analysis...")
            nlp_results = self.nlp_pipeline.process(problem_text)
            print(f"  ✅ Domain: {nlp_results['domain']}")
            print(f"  ✅ Entities: {nlp_results['metadata']['num_entities']}")
            print(f"  ✅ Relationships: {nlp_results['metadata']['num_relationships']}")
            print(f"  ✅ Processing time: {nlp_results['metadata']['processing_time']:.3f}s\n")

            # Step 2: Interpret to UniversalScene
            print("Step 2: Scene Interpretation...")
            interpreter = get_interpreter(nlp_results['domain'])
            scene = interpreter.interpret(nlp_results, problem_text)
            print(f"  ✅ Scene created: {scene.title}")
            print(f"  ✅ Objects: {len(scene.objects)}")
            print(f"  ✅ Relationships: {len(scene.relationships)}")
            print(f"  ✅ Annotations: {len(scene.annotations)}\n")

            # Step 3: Render to SVG
            print("Step 3: SVG Rendering...")
            svg_output = self.svg_renderer.render(scene)
            print(f"  ✅ SVG generated ({len(svg_output)} characters)\n")

            # Step 4: Save files (if requested)
            files_saved = {}
            if save_files:
                print("Step 4: Saving files...")

                # Generate filename
                if not output_filename:
                    # Use hash of problem text
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

            # Calculate total time
            total_time = time.time() - start_time

            # Build result
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
                    'num_annotations': len(scene.annotations)
                },
                'files': files_saved if save_files else {}
            }

            print("=" * 70)
            print(f"✅ SUCCESS! Diagram generated in {total_time:.3f}s")
            print("=" * 70)

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        return result

    def generate_batch(self, problems: List[Tuple[str, str]],
                      output_subdir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate diagrams for multiple problems

        Args:
            problems: List of (problem_text, output_filename) tuples
            output_subdir: Optional subdirectory within output_dir

        Returns:
            Dictionary with batch processing results
        """
        if output_subdir:
            batch_output_dir = self.output_dir / output_subdir
            batch_output_dir.mkdir(exist_ok=True)
            original_output_dir = self.output_dir
            self.output_dir = batch_output_dir

        print("\n" + "=" * 70)
        print(f"BATCH PROCESSING: {len(problems)} problems")
        print("=" * 70 + "\n")

        results = []
        successful = 0
        failed = 0
        total_time = 0

        for i, (problem_text, filename) in enumerate(problems, 1):
            print(f"\n{'='*70}")
            print(f"PROBLEM {i}/{len(problems)}")
            print(f"{'='*70}")

            result = self.generate(problem_text, filename, save_files=True)

            if result['success']:
                successful += 1
                total_time += result['metadata']['total_time']
            else:
                failed += 1

            results.append({
                'problem_id': i,
                'filename': filename,
                'success': result['success'],
                'error': result.get('error'),
                'metadata': result.get('metadata', {})
            })

        # Restore original output dir
        if output_subdir:
            self.output_dir = original_output_dir

        # Summary
        print("\n" + "=" * 70)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 70)
        print(f"\n✅ Successful: {successful}/{len(problems)}")
        print(f"❌ Failed: {failed}/{len(problems)}")
        print(f"⏱️  Total time: {total_time:.3f}s")
        print(f"⚡ Average time: {total_time/max(successful, 1):.3f}s per diagram")
        print(f"📊 Success rate: {(successful/len(problems)*100):.1f}%\n")

        return {
            'total_problems': len(problems),
            'successful': successful,
            'failed': failed,
            'total_time': total_time,
            'average_time': total_time / max(successful, 1),
            'success_rate': (successful / len(problems)) * 100,
            'results': results
        }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("UNIFIED DIAGRAM GENERATOR - TEST")
    print("=" * 70 + "\n")

    # Initialize generator
    generator = UnifiedDiagramGenerator(output_dir="output/unified_test")

    # Test problems from different domains
    test_problems = [
        (
            "A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor. "
            "Calculate the time constant τ = RC.",
            "test_circuit"
        ),
        (
            "A water molecule (H₂O) consists of one oxygen atom bonded to two hydrogen atoms. "
            "The bond angle is approximately 104.5 degrees.",
            "test_molecule"
        ),
        (
            "A cell with a nucleus, mitochondria, and ribosomes. "
            "The nucleus contains DNA and controls cellular functions.",
            "test_cell"
        ),
        (
            "A mass m = 5 kg rests on a horizontal surface with friction coefficient μ = 0.3. "
            "A force F = 20 N is applied horizontally.",
            "test_physics"
        )
    ]

    # Generate single diagram
    print("\n" + "=" * 70)
    print("TEST 1: Single Diagram Generation")
    print("=" * 70 + "\n")

    result = generator.generate(test_problems[0][0], test_problems[0][1])

    if result['success']:
        print(f"\n✅ Test 1 PASSED")
        print(f"   SVG length: {len(result['svg'])} chars")
        print(f"   Scene objects: {result['metadata']['num_objects']}")
        print(f"   Processing time: {result['metadata']['total_time']:.3f}s")
    else:
        print(f"\n❌ Test 1 FAILED: {result['error']}")

    # Generate batch
    print("\n" + "=" * 70)
    print("TEST 2: Batch Processing")
    print("=" * 70 + "\n")

    batch_result = generator.generate_batch(test_problems, output_subdir="batch_test")

    if batch_result['success_rate'] > 0:
        print(f"\n✅ Test 2 PASSED")
        print(f"   Success rate: {batch_result['success_rate']:.1f}%")
        print(f"   Average time: {batch_result['average_time']:.3f}s")
    else:
        print(f"\n❌ Test 2 FAILED")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
