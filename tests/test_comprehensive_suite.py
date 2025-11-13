"""
Comprehensive Test Suite
========================

Complete test suite covering:
- Unit tests for all core components
- Integration tests for full pipeline
- Regression tests for known issues
- Performance benchmarks
- Quality assurance tests

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

import unittest
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.universal_scene_format import (
    UniversalScene, SceneObject, Relationship, Annotation,
    ObjectType, RelationType, Position, Dimensions, Style,
    DiagramDomain, DiagramType
)
from core.universal_svg_renderer import UniversalSVGRenderer, ComponentLibrary
from core.advanced_scene_builder import PhysicsRuleEngine, AdvancedSceneBuilder
from enhanced_diagram_generator import EnhancedNLPPipeline, EnhancedDiagramGenerator
from core.enhanced_component_library import EnhancedComponentLibrary, ComponentStyle
from core.intelligent_layout_engine import IntelligentLayoutEngine
from core.validation_refinement import DiagramValidator, DiagramRefiner


class TestUniversalSceneFormat(unittest.TestCase):
    """Unit tests for universal scene format"""

    def test_scene_creation(self):
        """Test basic scene creation"""
        scene = UniversalScene(
            scene_id="test_001",
            domain=DiagramDomain.ELECTRONICS,
            diagram_type=DiagramType.CIRCUIT_DIAGRAM,
            title="Test Circuit"
        )
        self.assertEqual(scene.scene_id, "test_001")
        self.assertEqual(scene.domain, DiagramDomain.ELECTRONICS)
        self.assertEqual(len(scene.objects), 0)

    def test_add_object(self):
        """Test adding objects to scene"""
        scene = UniversalScene(scene_id="test_002")
        obj = SceneObject(
            id="R1",
            object_type=ObjectType.RESISTOR,
            position=Position(100, 100, 0),
            dimensions=Dimensions(width=80, height=40)
        )
        scene.add_object(obj)
        self.assertEqual(len(scene.objects), 1)
        self.assertEqual(scene.objects[0].id, "R1")

    def test_add_relationship(self):
        """Test adding relationships"""
        scene = UniversalScene(scene_id="test_003")
        rel = Relationship(
            id="wire1",
            relation_type=RelationType.CONNECTED_TO,
            source_id="obj1",
            target_id="obj2"
        )
        scene.add_relationship(rel)
        self.assertEqual(len(scene.relationships), 1)

    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        scene = UniversalScene(scene_id="test_004")
        obj = SceneObject(
            id="C1",
            object_type=ObjectType.CAPACITOR,
            position=Position(200, 200, 0),
            dimensions=Dimensions(width=80, height=60)
        )
        scene.add_object(obj)

        # Serialize
        json_str = scene.to_json()
        self.assertIn("test_004", json_str)
        self.assertIn("C1", json_str)

        # Deserialize
        scene_dict = scene.to_dict()
        loaded_scene = UniversalScene.from_dict(scene_dict)
        self.assertEqual(loaded_scene.scene_id, "test_004")
        self.assertEqual(len(loaded_scene.objects), 1)


class TestSVGRenderer(unittest.TestCase):
    """Unit tests for SVG renderer"""

    def setUp(self):
        self.renderer = UniversalSVGRenderer()
        self.scene = UniversalScene(scene_id="test_svg", title="Test SVG")

    def test_render_empty_scene(self):
        """Test rendering empty scene"""
        svg = self.renderer.render(self.scene)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn("Test SVG", svg)

    def test_render_resistor(self):
        """Test rendering resistor"""
        obj = SceneObject(
            id="R1",
            object_type=ObjectType.RESISTOR,
            position=Position(300, 300, 0),
            dimensions=Dimensions(width=120, height=30),
            label="10kΩ"
        )
        self.scene.add_object(obj)
        svg = self.renderer.render(self.scene)
        self.assertIn("10kΩ", svg)

    def test_render_capacitor(self):
        """Test rendering capacitor"""
        obj = SceneObject(
            id="C1",
            object_type=ObjectType.CAPACITOR,
            position=Position(300, 300, 0),
            dimensions=Dimensions(width=80, height=60),
            label="100μF"
        )
        self.scene.add_object(obj)
        svg = self.renderer.render(self.scene)
        self.assertIn("100μF", svg)


class TestAdvancedSceneBuilder(unittest.TestCase):
    """Unit tests for advanced scene builder"""

    def test_physics_rule_engine(self):
        """Test physics rule engine"""
        engine = PhysicsRuleEngine()
        components = [
            {'label': 'series connection'},
            {'label': 'capacitor'}
        ]
        topology = engine.infer_circuit_topology(components)
        self.assertEqual(topology, 'series')

    def test_capacitor_spacing(self):
        """Test capacitor spacing calculation"""
        engine = PhysicsRuleEngine()
        spacing = engine.calculate_capacitor_spacing(3, 1000)
        self.assertGreater(spacing, 0)
        self.assertLess(spacing, 500)

    def test_circuit_scene_building(self):
        """Test building circuit scene"""
        builder = AdvancedSceneBuilder()
        nlp_results = {
            'domain': 'electronics',
            'entities': [],
            'relationships': []
        }
        problem = "A circuit with 300V battery and 2.00 μF capacitor"
        scene = builder.build_capacitor_scene(nlp_results, problem)

        self.assertIsNotNone(scene)
        self.assertEqual(scene.domain, DiagramDomain.ELECTRONICS)
        self.assertGreaterEqual(len(scene.objects), 1)


class TestEnhancedNLP(unittest.TestCase):
    """Unit tests for enhanced NLP pipeline"""

    def setUp(self):
        self.nlp = EnhancedNLPPipeline()

    def test_domain_classification(self):
        """Test domain classification"""
        text = "A circuit with a capacitor and resistor connected to a battery"
        result = self.nlp.process(text)
        self.assertEqual(result['domain'], 'electronics')

    def test_entity_extraction(self):
        """Test entity extraction"""
        text = "A 300 V battery connected to a 2.00 μF capacitor"
        result = self.nlp.process(text)
        self.assertGreater(result['metadata']['num_entities'], 0)

    def test_measurement_extraction(self):
        """Test measurement extraction with units"""
        text = "Voltage of 120 V and capacitance of 5.00 μF"
        result = self.nlp.process(text)

        # Should extract measurements
        entities = result['entities']
        measurements = [e for e in entities if e['type'] == 'MEASUREMENT']
        self.assertGreater(len(measurements), 0)


class TestEnhancedComponents(unittest.TestCase):
    """Unit tests for enhanced component library"""

    def test_component_library_styles(self):
        """Test different component styles"""
        styles = ['classic', 'modern', '3d']
        for style_name in styles:
            style = ComponentStyle(style_type=style_name)
            lib = EnhancedComponentLibrary(style)

            resistor = lib.create_enhanced_resistor(200, 100, 80, 30, "10kΩ")
            self.assertIsNotNone(resistor)

    def test_enhanced_capacitor_types(self):
        """Test different capacitor types"""
        lib = EnhancedComponentLibrary()
        types = ['standard', 'electrolytic', 'variable']

        for cap_type in types:
            capacitor = lib.create_enhanced_capacitor(200, 200, 80, 60, "100μF", cap_type)
            self.assertIsNotNone(capacitor)

    def test_chemical_bonds(self):
        """Test chemical bond rendering"""
        lib = EnhancedComponentLibrary()
        bond_types = ['single', 'double', 'triple', 'dashed']

        for bond_type in bond_types:
            bond = lib.create_enhanced_bond(100, 100, 200, 150, bond_type)
            self.assertIsNotNone(bond)


class TestIntelligentLayout(unittest.TestCase):
    """Unit tests for intelligent layout engine"""

    def test_collision_detection(self):
        """Test collision detection"""
        engine = IntelligentLayoutEngine()
        scene = UniversalScene(scene_id="test_layout")

        # Add overlapping objects
        obj1 = SceneObject(
            id="obj1",
            object_type=ObjectType.RESISTOR,
            position=Position(200, 200, 0),
            dimensions=Dimensions(width=80, height=40)
        )
        obj2 = SceneObject(
            id="obj2",
            object_type=ObjectType.CAPACITOR,
            position=Position(210, 205, 0),  # Overlapping
            dimensions=Dimensions(width=80, height=60)
        )
        scene.add_object(obj1)
        scene.add_object(obj2)

        # Optimize layout
        optimized = engine.optimize_layout(scene, enable_collision_avoidance=True)

        # Check objects are separated
        dist = ((optimized.objects[0].position.x - optimized.objects[1].position.x)**2 +
                (optimized.objects[0].position.y - optimized.objects[1].position.y)**2)**0.5
        self.assertGreater(dist, 50)  # Should be at least min_spacing apart

    def test_grid_snapping(self):
        """Test grid snapping"""
        engine = IntelligentLayoutEngine()
        scene = UniversalScene(scene_id="test_grid")

        obj = SceneObject(
            id="obj1",
            object_type=ObjectType.RESISTOR,
            position=Position(203.7, 198.3, 0),  # Non-grid position
            dimensions=Dimensions(width=80, height=40)
        )
        scene.add_object(obj)

        optimized = engine.optimize_layout(scene)

        # Position should be snapped to grid (multiples of grid_size)
        self.assertEqual(optimized.objects[0].position.x % engine.grid_size, 0)
        self.assertEqual(optimized.objects[0].position.y % engine.grid_size, 0)


class TestValidationRefinement(unittest.TestCase):
    """Unit tests for validation and refinement"""

    def test_validation(self):
        """Test diagram validation"""
        validator = DiagramValidator()
        scene = UniversalScene(scene_id="test_validation")

        obj1 = SceneObject(
            id="R1",
            object_type=ObjectType.RESISTOR,
            position=Position(200, 200, 0),
            dimensions=Dimensions(width=80, height=40)
        )
        scene.add_object(obj1)

        quality = validator.validate(scene)
        self.assertIsNotNone(quality)
        self.assertGreaterEqual(quality.overall_score, 0)
        self.assertLessEqual(quality.overall_score, 100)

    def test_refinement(self):
        """Test automatic refinement"""
        refiner = DiagramRefiner()
        scene = UniversalScene(scene_id="test_refine")

        # Add overlapping objects
        obj1 = SceneObject(
            id="R1",
            object_type=ObjectType.RESISTOR,
            position=Position(200, 200, 0),
            dimensions=Dimensions(width=80, height=40)
        )
        obj2 = SceneObject(
            id="C1",
            object_type=ObjectType.CAPACITOR,
            position=Position(205, 202, 0),  # Overlapping
            dimensions=Dimensions(width=80, height=60)
        )
        scene.add_object(obj1)
        scene.add_object(obj2)

        initial_quality = refiner.validator.validate(scene)
        refined_scene, final_quality = refiner.refine(scene)

        # Quality should improve
        self.assertGreater(final_quality.overall_score, initial_quality.overall_score)


class TestEndToEndIntegration(unittest.TestCase):
    """Integration tests for complete pipeline"""

    def test_simple_circuit_generation(self):
        """Test generating a simple circuit diagram"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        problem = "A 9V battery connected to a 100Ω resistor"

        result = generator.generate(problem, "test_simple_circuit", save_files=False)

        self.assertTrue(result['success'])
        self.assertIn('svg', result)
        self.assertIn('scene', result)
        self.assertGreater(len(result['svg']), 100)

    def test_complex_circuit_generation(self):
        """Test generating complex circuit with multiple components"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        problem = "A circuit with 12V battery, 2.00 μF capacitor, and 100Ω resistor in series"

        result = generator.generate(problem, "test_complex_circuit", save_files=False)

        self.assertTrue(result['success'])
        self.assertGreater(result['metadata']['num_objects'], 1)

    def test_batch_processing(self):
        """Test batch processing of multiple problems"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")

        problems = [
            "A 5V battery with 10kΩ resistor",
            "Two capacitors of 1μF and 2μF in series",
            "A simple RC circuit"
        ]

        results = []
        for i, problem in enumerate(problems):
            result = generator.generate(problem, f"test_batch_{i}", save_files=False)
            results.append(result)

        # All should succeed
        success_count = sum(1 for r in results if r['success'])
        self.assertEqual(success_count, len(problems))


class TestPerformance(unittest.TestCase):
    """Performance benchmark tests"""

    def test_generation_speed(self):
        """Test generation speed"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        problem = "A 12V battery connected to a 1000Ω resistor"

        start = time.time()
        result = generator.generate(problem, "test_speed", save_files=False)
        elapsed = time.time() - start

        self.assertTrue(result['success'])
        self.assertLess(elapsed, 1.0)  # Should complete in under 1 second

    def test_large_scene_performance(self):
        """Test performance with large scene"""
        scene = UniversalScene(scene_id="test_large")

        # Add many objects
        for i in range(50):
            obj = SceneObject(
                id=f"obj_{i}",
                object_type=ObjectType.RESISTOR,
                position=Position(100 + i*20, 100 + i*10, 0),
                dimensions=Dimensions(width=80, height=40)
            )
            scene.add_object(obj)

        renderer = UniversalSVGRenderer()

        start = time.time()
        svg = renderer.render(scene)
        elapsed = time.time() - start

        self.assertLess(elapsed, 2.0)  # Should render large scene quickly
        self.assertGreater(len(svg), 1000)


class TestRegressionSuite(unittest.TestCase):
    """Regression tests for known issues"""

    def test_empty_problem_text(self):
        """Test handling of empty problem text"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        result = generator.generate("", "test_empty", save_files=False)

        # Should handle gracefully
        self.assertTrue(result['success'])

    def test_special_characters(self):
        """Test handling of special characters"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        problem = "A circuit with capacitor C₁ = 2.00 μF and C₂ = 8.00 μF"

        result = generator.generate(problem, "test_special_chars", save_files=False)

        self.assertTrue(result['success'])
        # Should preserve special characters
        self.assertIn('μF', result['svg'])

    def test_very_long_problem(self):
        """Test handling of very long problem text"""
        generator = EnhancedDiagramGenerator(output_dir="output/test")
        problem = "A circuit with " + " and ".join([f"{i}Ω resistor" for i in range(100)])

        result = generator.generate(problem, "test_long", save_files=False)

        self.assertTrue(result['success'])


def run_all_tests():
    """Run all tests and generate report"""
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestUniversalSceneFormat,
        TestSVGRenderer,
        TestAdvancedSceneBuilder,
        TestEnhancedNLP,
        TestEnhancedComponents,
        TestIntelligentLayout,
        TestValidationRefinement,
        TestEndToEndIntegration,
        TestPerformance,
        TestRegressionSuite
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time

    # Generate report
    print("\n" + "=" * 70)
    print("TEST REPORT")
    print("=" * 70)
    print(f"\nTotal tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Total time: {elapsed_time:.2f}s")
    print(f"Average time per test: {elapsed_time/result.testsRun:.3f}s")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
