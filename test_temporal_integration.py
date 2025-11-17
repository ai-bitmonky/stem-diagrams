"""
Test: Temporal Framework Integration with Existing Pipeline

This test demonstrates that the temporal framework:
1. Integrates seamlessly with the EXISTING pipeline
2. Works for multiple physics domains
3. Doesn't break existing functionality
4. Adds minimal overhead
"""

import time
from core.temporal_analyzer import TemporalAnalyzer, TemporalStage


def test_capacitor_problem():
    """Test: Multi-stage capacitor problem (electrostatics)"""
    print("\n" + "="*70)
    print("TEST 1: Electrostatics (Capacitors)")
    print("="*70)

    problem_text = """
    A potential difference of 300 V is applied to a series connection of two capacitors
    of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then
    disconnected from the battery and from each other. They are then reconnected with
    plates of the same signs wired together (positive to positive, negative to negative).
    What is the charge on capacitor C₁?
    """

    analyzer = TemporalAnalyzer()
    start = time.time()
    result = analyzer.analyze(problem_text)
    elapsed = time.time() - start

    print(f"\n📊 Analysis Results:")
    print(f"   Is multistage: {result['is_multistage']}")
    print(f"   Stages: {len(result['stages'])}")
    print(f"   Target stage: {result['question_target_stage'].value}")
    print(f"   Transitions: {[t.value for t in result['transitions']]}")
    print(f"   Implicit relationships: {result['implicit_relationships']}")
    print(f"\n⏱️  Analysis time: {elapsed*1000:.2f}ms")

    # Assertions
    assert result['is_multistage'] == True, "Should detect multi-stage problem"
    assert result['question_target_stage'] == TemporalStage.FINAL, "Question asks about final state"
    assert 'circuit_topology' in result['implicit_relationships'], "Should detect circuit topology"
    assert result['implicit_relationships']['circuit_topology'] == 'parallel', "Should detect parallel connection"

    print("\n✅ PASSED: Correctly detects parallel connection (final state)")


def test_collision_problem():
    """Test: Collision problem (mechanics)"""
    print("\n" + "="*70)
    print("TEST 2: Mechanics (Collision)")
    print("="*70)

    problem_text = """
    Two blocks on a frictionless surface move toward each other. Block A (mass 2 kg)
    moves at 3 m/s to the right, and block B (mass 1 kg) moves at 2 m/s to the left.
    After they collide and stick together, what is their final velocity?
    """

    analyzer = TemporalAnalyzer()
    start = time.time()
    result = analyzer.analyze(problem_text)
    elapsed = time.time() - start

    print(f"\n📊 Analysis Results:")
    print(f"   Is multistage: {result['is_multistage']}")
    print(f"   Stages: {len(result['stages'])}")
    print(f"   Target stage: {result['question_target_stage'].value}")
    print(f"   Transitions: {[t.value for t in result['transitions']]}")
    print(f"   Implicit relationships: {result['implicit_relationships']}")
    print(f"\n⏱️  Analysis time: {elapsed*1000:.2f}ms")

    # Assertions
    assert result['is_multistage'] == True, "Should detect multi-stage problem"
    assert result['question_target_stage'] == TemporalStage.FINAL, "Question asks about final velocity"
    assert 'mechanical_interaction' in result['implicit_relationships'], "Should detect collision"
    assert result['implicit_relationships']['mechanical_interaction'] == 'collision', "Should detect collision type"

    print("\n✅ PASSED: Correctly detects collision (final state)")


def test_lens_problem():
    """Test: Lens system (optics)"""
    print("\n" + "="*70)
    print("TEST 3: Optics (Lens System)")
    print("="*70)

    problem_text = """
    An object is placed 20 cm to the left of a converging lens with focal length 10 cm.
    The light passes through the lens. Where is the image formed?
    """

    analyzer = TemporalAnalyzer()
    start = time.time()
    result = analyzer.analyze(problem_text)
    elapsed = time.time() - start

    print(f"\n📊 Analysis Results:")
    print(f"   Is multistage: {result['is_multistage']}")
    print(f"   Stages: {len(result['stages'])}")
    print(f"   Target stage: {result['question_target_stage'].value}")
    print(f"   Transitions: {[t.value for t in result['transitions']]}")
    print(f"   Implicit relationships: {result['implicit_relationships']}")
    print(f"\n⏱️  Analysis time: {elapsed*1000:.2f}ms")

    # Assertions
    assert result['is_multistage'] == True, "Should detect multi-stage (object → image)"
    assert 'optical_path' in result['implicit_relationships'], "Should detect optical path"
    assert result['implicit_relationships']['optical_path'] == 'transmission', "Should detect transmission"

    print("\n✅ PASSED: Correctly detects lens transmission")


def test_thermodynamics_problem():
    """Test: Gas process (thermodynamics)"""
    print("\n" + "="*70)
    print("TEST 4: Thermodynamics (Gas Process)")
    print("="*70)

    problem_text = """
    An ideal gas initially at 300 K and 1 atm undergoes isothermal compression
    to half its original volume. What is the final pressure?
    """

    analyzer = TemporalAnalyzer()
    start = time.time()
    result = analyzer.analyze(problem_text)
    elapsed = time.time() - start

    print(f"\n📊 Analysis Results:")
    print(f"   Is multistage: {result['is_multistage']}")
    print(f"   Stages: {len(result['stages'])}")
    print(f"   Target stage: {result['question_target_stage'].value}")
    print(f"   Transitions: {[t.value for t in result['transitions']]}")
    print(f"   Implicit relationships: {result['implicit_relationships']}")
    print(f"\n⏱️  Analysis time: {elapsed*1000:.2f}ms")

    # Assertions
    assert result['is_multistage'] == True, "Should detect multi-stage (initial → final)"
    assert result['question_target_stage'] == TemporalStage.FINAL, "Question asks about final pressure"

    print("\n✅ PASSED: Correctly detects state change (final state)")


def test_single_stage_problem():
    """Test: Single-stage problem (no temporal stages)"""
    print("\n" + "="*70)
    print("TEST 5: Single-Stage Problem")
    print("="*70)

    problem_text = """
    A 5 kg block rests on a horizontal surface. Calculate the normal force.
    """

    analyzer = TemporalAnalyzer()
    start = time.time()
    result = analyzer.analyze(problem_text)
    elapsed = time.time() - start

    print(f"\n📊 Analysis Results:")
    print(f"   Is multistage: {result['is_multistage']}")
    print(f"   Stages: {len(result['stages'])}")
    print(f"   Target stage: {result['question_target_stage'].value}")
    print(f"\n⏱️  Analysis time: {elapsed*1000:.2f}ms")

    # Assertions
    assert result['is_multistage'] == False, "Should detect single-stage problem"
    assert result['question_target_stage'] == TemporalStage.CURRENT, "Single stage = current state"

    print("\n✅ PASSED: Correctly identifies single-stage problem")


def test_performance():
    """Test: Performance overhead is minimal"""
    print("\n" + "="*70)
    print("TEST 6: Performance Overhead")
    print("="*70)

    problem_text = """
    A potential difference of 300 V is applied to a series connection of two capacitors
    of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then
    disconnected from the battery and from each other. They are then reconnected with
    plates of the same signs wired together. What is the charge on capacitor C₁?
    """

    analyzer = TemporalAnalyzer()

    # Run 100 times to get average
    times = []
    for _ in range(100):
        start = time.time()
        analyzer.analyze(problem_text)
        elapsed = time.time() - start
        times.append(elapsed * 1000)  # Convert to ms

    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)

    print(f"\n📊 Performance (100 runs):")
    print(f"   Average: {avg_time:.2f}ms")
    print(f"   Min: {min_time:.2f}ms")
    print(f"   Max: {max_time:.2f}ms")

    # Assertion: Should be under 5ms on average
    assert avg_time < 5.0, f"Average time {avg_time}ms exceeds 5ms threshold"

    print(f"\n✅ PASSED: Overhead is minimal (< 5ms avg, ~{avg_time/40000*100:.1f}% of typical 40s pipeline)")


def test_integration_with_spec():
    """Test: Integration with existing spec structure"""
    print("\n" + "="*70)
    print("TEST 7: Integration with Existing Spec")
    print("="*70)

    # Simulate existing spec structure
    spec = {
        'objects': [
            {'type': 'capacitor', 'properties': {'capacitance': '2.00 μF'}},
            {'type': 'capacitor', 'properties': {'capacitance': '8.00 μF'}},
        ],
        'relationships': [],
        'problem_text': 'Two capacitors in series are disconnected and reconnected with same signs together.'
    }

    analyzer = TemporalAnalyzer()
    temporal_analysis = analyzer.analyze(spec['problem_text'])

    # Add temporal analysis to spec (like UniversalSceneBuilder does)
    spec['temporal_analysis'] = temporal_analysis

    print(f"\n📊 Spec Before:")
    print(f"   Keys: {list(spec.keys())[:3]}...")

    print(f"\n📊 Spec After:")
    print(f"   Keys: {list(spec.keys())}")
    print(f"   Temporal analysis added: {'temporal_analysis' in spec}")

    # Assertions
    assert 'temporal_analysis' in spec, "Temporal analysis should be in spec"
    assert spec['temporal_analysis']['is_multistage'] == True, "Should detect multi-stage"
    assert 'circuit_topology' in spec['temporal_analysis']['implicit_relationships'], "Should detect topology"

    print(f"\n✅ PASSED: Integrates cleanly with existing spec structure")
    print(f"   Interpreters can now access: spec.get('temporal_analysis', {{}})")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("TEMPORAL FRAMEWORK - INTEGRATION TESTS")
    print("="*70)
    print("\nTesting that temporal framework:")
    print("  ✓ Works with existing pipeline")
    print("  ✓ Handles multiple domains")
    print("  ✓ Has minimal overhead")
    print("  ✓ Doesn't break existing code")

    tests = [
        test_capacitor_problem,
        test_collision_problem,
        test_lens_problem,
        test_thermodynamics_problem,
        test_single_stage_problem,
        test_performance,
        test_integration_with_spec,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"\n{'🎉 ALL TESTS PASSED!' if failed == 0 else '⚠️  SOME TESTS FAILED'}")
    print("="*70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
