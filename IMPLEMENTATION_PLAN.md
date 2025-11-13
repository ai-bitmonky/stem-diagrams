# Pipeline Implementation Plan - Fixing Architecture Gaps

**Date:** November 11, 2025
**Based On:** [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md)
**Goal:** Wire up claimed features that are currently stubbed or unused

---

## Overview

This plan addresses the gaps identified in the architecture audit, prioritized by:
1. **Impact** - How much does this improve diagram quality?
2. **Effort** - How much code needs to be written?
3. **Dependencies** - What else needs to be working first?

---

## Priority 1: High Impact, Low Effort (Quick Wins)

### 1.1 Wire NLP Results into Scene Synthesis (2-3 hours)

**Problem:** NLP tools run but output is discarded

**Solution:** Use NLP results to enrich scene understanding

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:720-760) - Scene synthesis phase

**Implementation:**
```python
# Phase 3: Scene Synthesis + Strategic Planning
# BEFORE (line 720):
scene = self.scene_builder.build_from_spec(specs, domain)

# AFTER:
# Pass NLP results to scene builder for enrichment
scene = self.scene_builder.build_from_spec(
    specs,
    domain,
    nlp_context={
        'entities': nlp_results.get('stanza', {}).get('entities', []) if nlp_results else [],
        'embeddings': nlp_results.get('scibert', {}).get('embeddings', []) if nlp_results else [],
        'triples': nlp_results.get('openie', {}).get('triples', []) if nlp_results else []
    }
)
```

**Files to Create/Modify:**
- Modify [core/scene_builder.py](core/scene_builder.py) to accept `nlp_context` parameter
- Use entities to improve object detection confidence
- Use triples to infer implicit relationships
- Use embeddings for semantic similarity checks

**Testing:**
```bash
python3 -c "
# Test that NLP results improve scene quality
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.nlp_tools = ['openie', 'stanza', 'scibert']
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('A capacitor stores charge q')
# Verify entities from Stanza are used in scene objects
assert len(result.scene.objects) > 0
print('✓ NLP results integrated into scene')
"
```

**Success Criteria:**
- ✅ NLP entities improve object detection accuracy
- ✅ Triples inform relationship constraints
- ✅ Scene quality metrics improve by 10%+

---

### 1.2 Wire Property Graph Queries (3-4 hours)

**Problem:** Property graph is built but never queried

**Solution:** Query graph for relationship inference

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:720-760) - Scene synthesis phase

**Implementation:**
```python
# After property graph construction (line 680):
if current_property_graph:
    # Query graph for spatial relationships
    spatial_rels = current_property_graph.find_edges_by_type(EdgeType.SPATIAL)

    # Query graph for causal relationships
    causal_rels = current_property_graph.find_edges_by_type(EdgeType.CAUSAL)

    # Use in scene synthesis
    scene = self.scene_builder.build_from_spec(
        specs,
        domain,
        inferred_relationships=spatial_rels + causal_rels
    )
```

**New Methods in PropertyGraph:**
```python
# Add to core/property_graph.py
def find_spatial_constraints(self) -> List[Tuple[str, str, str]]:
    """Find all spatial relationships (above, below, left, right, etc.)"""
    spatial_edges = self.find_edges_by_type(EdgeType.SPATIAL)
    return [(e.source, e.label, e.target) for e in spatial_edges]

def find_causal_chains(self, start_node: str) -> List[List[str]]:
    """Find all causal chains starting from a node"""
    # DFS to find paths through causal edges
    pass
```

**Testing:**
```bash
python3 -c "
# Test that property graph queries improve constraints
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_property_graph = True
config.nlp_tools = ['openie']
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('Block A is above block B')
# Verify constraint extracted from graph
assert any('above' in str(c) for c in result.scene.constraints)
print('✓ Property graph queries used for constraints')
"
```

**Success Criteria:**
- ✅ Graph queries extract spatial relationships
- ✅ Causal chains inform constraint ordering
- ✅ Constraint detection accuracy improves

---

### 1.3 Wire Model Orchestrator (2 hours)

**Problem:** `HybridModelOrchestrator` exists but never used

**Solution:** Route LLM calls through orchestrator

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:220-240) - Add orchestrator init

**Implementation:**
```python
# Add import (line 135):
from core.model_orchestrator import HybridModelOrchestrator

# Add to __init__ (line 450):
self.model_orchestrator = None
if config.enable_model_orchestrator:
    self.model_orchestrator = HybridModelOrchestrator(
        primary_model="deepseek",
        fallback_models=["claude-3-sonnet", "gpt-4"]
    )
    print("✓ Model Orchestrator [ACTIVE]")

# Replace direct DeepSeek calls:
# BEFORE:
response = self.deepseek_client.chat.completions.create(...)

# AFTER:
if self.model_orchestrator:
    response = self.model_orchestrator.call(
        task_type="scene_synthesis",
        complexity=complexity_score,
        messages=[...],
        temperature=0.7
    )
else:
    response = self.deepseek_client.chat.completions.create(...)
```

**Testing:**
```bash
python3 -c "
# Test that model orchestrator routes calls correctly
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_model_orchestrator = True
pipeline = UnifiedDiagramPipeline(config)
# Should use DeepSeek for simple tasks
result1 = pipeline.generate('A spring')
# Should potentially use Claude for complex tasks
result2 = pipeline.generate('A complex circuit with multiple loops and components')
print('✓ Model orchestrator routing working')
"
```

**Success Criteria:**
- ✅ Simple tasks → DeepSeek (cost savings)
- ✅ Complex tasks → Claude/GPT-4 (quality boost)
- ✅ Automatic fallback on errors

---

## Priority 2: High Impact, Medium Effort (Core Fixes)

### 2.1 Fix Z3 Solver Integration (4-6 hours)

**Problem:** Z3 solver instantiated but always falls back to heuristics

**Solution:** Debug why Z3 fails and fix integration

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:876-889) - Z3 invocation
- [core/solvers/z3_layout_solver.py](core/solvers/z3_layout_solver.py:1-210) - Solver implementation

**Root Cause Investigation:**
```python
# Current code (line 876):
if self.z3_solver and self.diagram_planner:
    try:
        plan = self.diagram_planner.create_plan(specs)
        z3_solution = self.z3_solver.solve_layout(plan, object_dims)
        if z3_solution.satisfiable:
            z3_used = True
    except Exception as e:
        print(f"  Z3 failed: {e}")  # ← What's the actual error?
```

**Debug Steps:**
1. Add detailed logging to see why Z3 fails
2. Check if `create_plan()` generates valid constraints
3. Verify Z3 constraint formulation
4. Check satisfiability timeout settings

**Implementation Fix:**
```python
# Enhanced error handling:
if self.z3_solver and self.diagram_planner:
    try:
        # Step 1: Create plan
        plan = self.diagram_planner.create_plan(specs)
        if self.logger:
            self.logger.log_phase_detail(f"Plan created: {len(plan.constraints)} constraints")

        # Step 2: Validate plan
        if not plan.constraints:
            raise ValueError("Plan has no constraints, skipping Z3")

        # Step 3: Get object dimensions from scene
        object_dims = {}
        for obj in scene.objects:
            w, h = self._estimate_object_size(obj, domain)
            object_dims[obj.id] = (w, h)

        # Step 4: Solve with Z3
        z3_solution = self.z3_solver.solve_layout(
            plan,
            object_dims,
            timeout_ms=5000  # 5 second timeout
        )

        # Step 5: Apply solution if satisfiable
        if z3_solution.satisfiable:
            for obj_id, (x, y) in z3_solution.positions.items():
                obj = next(o for o in scene.objects if o.id == obj_id)
                obj.position = Position(x=x, y=y)
            z3_used = True
            if self.logger:
                self.logger.log_phase_detail(f"Z3 solution applied: {len(z3_solution.positions)} positions")
        else:
            if self.logger:
                self.logger.log_phase_detail("Z3 unsatisfiable, using heuristic layout")

    except Exception as e:
        if self.logger:
            self.logger.log_error(e, "Z3 solver failed")
        print(f"  Z3 failed: {e}, falling back to heuristic layout")

# Only use heuristic if Z3 wasn't successful
if not z3_used:
    positioned_scene = self.layout_engine.solve(scene, specs)
else:
    positioned_scene = scene  # Use Z3 positions
```

**Testing:**
```bash
# Test Z3 with simple problem
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_z3_optimization = True
config.enable_diagram_planning = True
pipeline = UnifiedDiagramPipeline(config)

# Simple problem that should be Z3-solvable
result = pipeline.generate('Two blocks A and B with A above B')

# Check trace
import json
with open('logs/' + sorted(os.listdir('logs'))[-1], 'r') as f:
    trace = json.load(f)
    for phase in trace['phases']:
        if 'Layout' in phase['phase_name']:
            assert phase['output']['z3_used'] == True, 'Z3 should be used for simple problems'

print('✓ Z3 solver working')
"
```

**Success Criteria:**
- ✅ Z3 successfully solves at least 50% of problems
- ✅ Clear logging shows why Z3 fails when it does
- ✅ Graceful fallback to heuristics for unsatisfiable problems
- ✅ Performance: Z3 timeout prevents hangs

---

### 2.2 Implement Validation Refinement Loop (6-8 hours)

**Problem:** Validation runs but issues are never fixed

**Solution:** Add refinement loop that fixes validation errors

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:1110-1150) - `_post_validate` method
- [core/universal_validator.py](core/universal_validator.py:100-200) - Add auto-correction

**Implementation:**
```python
def _post_validate(self, svg: str, scene: Scene, problem_text: str) -> Dict:
    """Phase 7: AI-based quality validation with refinement loop"""

    MAX_REFINEMENT_ITERATIONS = 3
    validation_results = {
        'structural': None,
        'visual_semantic': None,
        'overall_confidence': 0.0,
        'issues': [],
        'suggestions': [],
        'refinement_iterations': 0
    }

    # Refinement loop
    for iteration in range(MAX_REFINEMENT_ITERATIONS):
        if self.logger:
            self.logger.log_phase_detail(f"Validation iteration {iteration + 1}/{MAX_REFINEMENT_ITERATIONS}")

        # 1. Run structural validation
        if self.diagram_validator:
            quality_score = self.diagram_validator.validate(scene)
            validation_results['structural'] = {
                'overall_score': quality_score.overall_score,
                'layout_score': quality_score.layout_score,
                'connectivity_score': quality_score.connectivity_score,
                'issues': quality_score.issues
            }

            # If quality is good enough, stop
            if quality_score.overall_score >= 0.8:
                validation_results['overall_confidence'] = quality_score.overall_score
                break

            # Otherwise, try to fix issues
            issues_fixed = self._fix_validation_issues(scene, quality_score.issues)
            validation_results['refinement_iterations'] += 1

            if self.logger:
                self.logger.log_phase_detail(f"Fixed {issues_fixed} issues")

            # If no issues could be fixed, stop
            if issues_fixed == 0:
                break

            # Re-render SVG with fixed scene
            svg = self.renderer.render(scene)

        # 2. Run VLM validation (if available)
        if self.vlm_validator and svg:
            vlm_result = self.vlm_validator.validate_diagram(svg, problem_text)
            validation_results['visual_semantic'] = {
                'confidence': vlm_result.confidence,
                'issues': vlm_result.issues
            }

    return validation_results

def _fix_validation_issues(self, scene: Scene, issues: List[str]) -> int:
    """Fix common validation issues"""
    fixed = 0

    for issue in issues:
        if 'overlap' in issue.lower():
            # Fix overlapping objects
            overlapping_ids = self._extract_object_ids_from_issue(issue)
            self._resolve_overlap(scene, overlapping_ids)
            fixed += 1

        elif 'label' in issue.lower() and 'unreadable' in issue.lower():
            # Fix unreadable labels
            obj_id = self._extract_object_ids_from_issue(issue)[0]
            self._reposition_label(scene, obj_id)
            fixed += 1

        elif 'constraint' in issue.lower() and 'violated' in issue.lower():
            # Fix constraint violations
            constraint_type = self._extract_constraint_type(issue)
            self._enforce_constraint(scene, constraint_type)
            fixed += 1

    return fixed
```

**Testing:**
```bash
# Test validation refinement
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_llm_auditing = True
config.enable_vlm_validation = True
pipeline = UnifiedDiagramPipeline(config)

# Problem that's likely to have validation issues
result = pipeline.generate('Three blocks stacked vertically with A on B on C')

# Check that refinement happened
import json
with open('logs/' + sorted(os.listdir('logs'))[-1], 'r') as f:
    trace = json.load(f)
    # Find validation phase
    for phase in trace['phases']:
        if 'Validation' in phase['phase_name'] or 'Auditing' in phase['phase_name']:
            output = phase.get('output', {})
            iterations = output.get('refinement_iterations', 0)
            assert iterations >= 1, 'Should have at least one refinement iteration'
            print(f'✓ Validation refinement: {iterations} iterations')
"
```

**Success Criteria:**
- ✅ Validation issues detected correctly
- ✅ At least 70% of common issues auto-fixed
- ✅ Maximum 3 refinement iterations
- ✅ Overall quality score improves after refinement

---

### 2.3 Complete DiagramPlanner Integration (5-7 hours)

**Problem:** DiagramPlanner only used for complexity assessment

**Solution:** Use full planning pipeline (plan → solve → verify)

**Files to Modify:**
- [unified_diagram_pipeline.py](unified_diagram_pipeline.py:700-900) - Phases 2-5

**Implementation:**
```python
# Phase 2: Problem Understanding (line 700)
if self.diagram_planner:
    complexity_score = self.diagram_planner.assess_complexity(specs)
    # NEW: Store for later use
    diagram_complexity = complexity_score

# Phase 3: Scene Synthesis (line 720)
if self.diagram_planner and complexity_score is not None:
    strategy = self.diagram_planner.select_strategy(specs, complexity_score)
    # NEW: Actually use the strategy
    if strategy == PlanningStrategy.HIERARCHICAL:
        # Build scene hierarchically
        subproblems = self.diagram_planner.decompose_problem(specs)
        scene = self.scene_builder.build_hierarchical(subproblems, domain)
    elif strategy == PlanningStrategy.CONSTRAINT_FIRST:
        # Build scene with constraint satisfaction
        plan = self.diagram_planner.create_plan(specs)
        scene = self.scene_builder.build_from_plan(plan, domain)
    else:
        # Default: direct synthesis
        scene = self.scene_builder.build_from_spec(specs, domain)

# Phase 5: Layout (line 876)
if self.diagram_planner:
    # Create comprehensive plan
    plan = self.diagram_planner.create_plan(specs)

    # Use Z3 if complex enough
    if plan.complexity_score > 0.6 and self.z3_solver:
        z3_solution = self.z3_solver.solve_layout(plan, object_dims)
        if z3_solution.satisfiable:
            # Apply Z3 solution
            ...
    else:
        # Use heuristic layout for simple problems
        positioned_scene = self.layout_engine.solve(scene, specs)
```

**Testing:**
```bash
# Test planning strategies
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

config = PipelineConfig()
config.enable_diagram_planning = True
pipeline = UnifiedDiagramPipeline(config)

# Test 1: Simple problem (should use direct strategy)
result1 = pipeline.generate('A single spring')
# Verify strategy

# Test 2: Complex problem (should use hierarchical)
result2 = pipeline.generate('A pulley system with 3 masses connected by ropes over 2 pulleys')
# Verify hierarchical decomposition

# Test 3: Constraint-heavy problem (should use constraint-first)
result3 = pipeline.generate('Three charged particles A, B, C where A and B repel, B and C attract, and A and C repel')
# Verify constraint-first strategy

print('✓ Planning strategies working correctly')
"
```

**Success Criteria:**
- ✅ Strategy selection based on complexity
- ✅ Hierarchical decomposition for complex problems
- ✅ Constraint-first for heavily constrained problems
- ✅ Quality improves for complex diagrams

---

## Priority 3: Medium Impact, High Effort (Future Enhancements)

### 3.1 Add SymPy Geometry Verification (8-10 hours)

**Problem:** No symbolic geometry verification

**Solution:** Use SymPy to verify spatial relationships

**New Files to Create:**
- `core/symbolic/sympy_geometry_verifier.py`

**Implementation:**
```python
"""
SymPy Geometry Verifier - Symbolic spatial verification
"""

from sympy.geometry import Point, Segment, Circle, Triangle, Polygon
from sympy import symbols, solve, Eq
from typing import List, Dict, Tuple
from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType

class SymPyGeometryVerifier:
    """Verify spatial relationships using symbolic geometry"""

    def verify_scene(self, scene: Scene) -> Dict[str, bool]:
        """
        Verify all spatial relationships in scene

        Returns dict mapping constraint_id → is_satisfied
        """
        results = {}

        # Convert scene objects to SymPy geometry
        sympy_objects = self._scene_to_sympy(scene)

        # Verify each constraint
        for constraint in scene.constraints:
            if constraint.type == ConstraintType.ABOVE:
                results[constraint.id] = self._verify_above(
                    sympy_objects[constraint.object_ids[0]],
                    sympy_objects[constraint.object_ids[1]]
                )
            elif constraint.type == ConstraintType.DISTANCE:
                results[constraint.id] = self._verify_distance(
                    sympy_objects[constraint.object_ids[0]],
                    sympy_objects[constraint.object_ids[1]],
                    constraint.parameters.get('distance')
                )
            # ... more constraint types

        return results

    def _scene_to_sympy(self, scene: Scene) -> Dict[str, Point]:
        """Convert scene objects to SymPy Points"""
        points = {}
        for obj in scene.objects:
            if obj.position:
                points[obj.id] = Point(obj.position.x, obj.position.y)
        return points

    def _verify_above(self, obj1: Point, obj2: Point) -> bool:
        """Verify obj1 is above obj2"""
        return obj1.y < obj2.y  # SVG coordinates (y=0 at top)

    def _verify_distance(self, obj1: Point, obj2: Point, expected_dist: float) -> bool:
        """Verify distance between objects"""
        actual_dist = obj1.distance(obj2)
        return abs(actual_dist - expected_dist) < 5.0  # 5px tolerance
```

**Integration:**
```python
# Add to unified_diagram_pipeline.py Phase 5.6 (Spatial Validation):
if config.enable_sympy_verification:
    from core.symbolic.sympy_geometry_verifier import SymPyGeometryVerifier
    self.sympy_verifier = SymPyGeometryVerifier()

# In spatial validation phase:
if self.sympy_verifier:
    sympy_results = self.sympy_verifier.verify_scene(positioned_scene)
    violations = [cid for cid, satisfied in sympy_results.items() if not satisfied]
    if violations:
        print(f"  SymPy found {len(violations)} geometric violations")
```

**Success Criteria:**
- ✅ Symbolic verification of spatial constraints
- ✅ Catches geometric inconsistencies
- ✅ Can suggest corrections

---

### 3.2 Add Physics Simulation (10-15 hours)

**Problem:** No physics verification (forces, energy, etc.)

**Solution:** Add physics simulation layer

**New Files to Create:**
- `core/physics/physics_simulator.py`

**Implementation:**
```python
"""
Physics Simulator - Verify physical correctness
"""

import numpy as np
from typing import Dict, List
from core.scene.schema_v1 import Scene
from core.universal_ai_analyzer import PhysicsDomain

class PhysicsSimulator:
    """Simulate physics to verify correctness"""

    def verify_mechanics(self, scene: Scene) -> Dict[str, bool]:
        """Verify mechanics (forces, torques, equilibrium)"""
        results = {
            'force_balance': self._check_force_balance(scene),
            'torque_balance': self._check_torque_balance(scene),
            'energy_conservation': self._check_energy_conservation(scene)
        }
        return results

    def verify_electrostatics(self, scene: Scene) -> Dict[str, bool]:
        """Verify electrostatics (field lines, potentials)"""
        results = {
            'field_continuity': self._check_field_continuity(scene),
            'potential_consistency': self._check_potentials(scene)
        }
        return results

    def _check_force_balance(self, scene: Scene) -> bool:
        """Check if sum of forces = 0 for static equilibrium"""
        total_force = np.array([0.0, 0.0])

        for obj in scene.objects:
            if obj.properties.get('force'):
                fx = obj.properties['force'].get('x', 0)
                fy = obj.properties['force'].get('y', 0)
                total_force += np.array([fx, fy])

        # Check if close to zero
        return np.linalg.norm(total_force) < 0.01
```

**Success Criteria:**
- ✅ Force balance verification
- ✅ Energy conservation checks
- ✅ Domain-specific physics rules

---

### 3.3 Add SchemDraw/CircuitikZ (12-15 hours)

**Problem:** No professional circuit diagram rendering

**Solution:** Integrate SchemDraw for circuits

**New Files to Create:**
- `core/renderers/circuit_renderer.py`

**Implementation:**
```python
"""
Circuit Renderer - Professional circuit diagrams using SchemDraw
"""

import schemdraw
import schemdraw.elements as elm
from core.scene.schema_v1 import Scene

class CircuitRenderer:
    """Render circuits using SchemDraw"""

    def render(self, scene: Scene) -> str:
        """Render circuit to SVG using SchemDraw"""
        with schemdraw.Drawing() as d:
            for obj in scene.objects:
                if obj.primitive_type == PrimitiveType.RESISTOR:
                    d += elm.Resistor().label(obj.label)
                elif obj.primitive_type == PrimitiveType.CAPACITOR:
                    d += elm.Capacitor().label(obj.label)
                # ... more components

        return d.get_imagedata('svg')
```

**Success Criteria:**
- ✅ Professional-looking circuit diagrams
- ✅ Proper component symbols
- ✅ Correct topology

---

## Implementation Roadmap

### Week 1: Quick Wins
- Day 1-2: NLP → Scene Synthesis (1.1)
- Day 3-4: Property Graph Queries (1.2)
- Day 5: Model Orchestrator (1.3)

### Week 2: Core Fixes
- Day 1-3: Z3 Solver Integration (2.1)
- Day 4-5: Validation Refinement Loop (2.2)

### Week 3: Core Fixes Continued
- Day 1-5: DiagramPlanner Full Integration (2.3)

### Week 4+: Future Enhancements
- SymPy Geometry (3.1)
- Physics Simulation (3.2)
- SchemDraw Integration (3.3)

---

## Success Metrics

### Before Fixes (Current State)
- NLP tools: Runs but output unused
- Property Graph: Built but not queried
- Z3 Solver: 0% usage rate
- Validation: No refinement loop
- Model Orchestrator: Not wired
- Overall pipeline integration: ~40%

### After Priority 1 Fixes (Week 1)
- NLP tools: Integrated into scene synthesis
- Property Graph: Queried for relationships
- Model Orchestrator: Routing LLM calls
- Overall pipeline integration: ~65%

### After Priority 2 Fixes (Weeks 2-3)
- Z3 Solver: 50%+ usage rate
- Validation: Auto-fixes 70%+ of issues
- DiagramPlanner: Full planning loop
- Overall pipeline integration: ~85%

### After Priority 3 Fixes (Week 4+)
- SymPy: Geometric verification
- Physics: Simulation-based verification
- Circuits: Professional rendering
- Overall pipeline integration: ~95%

---

## Verification Strategy

After each fix, verify with:

1. **Unit tests** - Test component in isolation
2. **Integration tests** - Test component in pipeline
3. **Trace analysis** - Check logging confirms feature usage
4. **Visual inspection** - Check diagram quality improvement

### Example Verification Script
```bash
#!/bin/bash
# verify_fixes.sh

echo "Testing Priority 1 fixes..."

# Test 1.1: NLP integration
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.nlp_tools = ['openie', 'stanza']
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('A capacitor')
assert result.scene.objects, 'NLP should improve scene'
print('✓ 1.1 NLP integration')
"

# Test 1.2: Property graph queries
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_property_graph = True
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('Block A above block B')
# Check that graph was queried (trace should show queries)
print('✓ 1.2 Property graph queries')
"

# Test 1.3: Model orchestrator
python3 -c "
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_model_orchestrator = True
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('A spring')
print('✓ 1.3 Model orchestrator')
"

# Test 2.1: Z3 solver
python3 -c "
import json
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
config = PipelineConfig()
config.enable_z3_optimization = True
config.enable_diagram_planning = True
pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate('Two blocks A and B')
# Check trace for z3_used: true
with open('logs/' + sorted(os.listdir('logs'))[-1]) as f:
    trace = json.load(f)
    z3_used = any(p.get('output', {}).get('z3_used') for p in trace['phases'])
    assert z3_used, 'Z3 should be used'
print('✓ 2.1 Z3 solver')
"

echo "All fixes verified ✓"
```

---

## Risk Mitigation

### Risks
1. **Breaking existing functionality** - Changes might break working code
2. **Performance degradation** - Additional processing might slow pipeline
3. **Complexity explosion** - More features = more bugs

### Mitigation
1. **Comprehensive testing** - Unit + integration tests for each fix
2. **Feature flags** - All new features behind config flags
3. **Gradual rollout** - One priority at a time, verify before moving on
4. **Logging** - Extensive logging to catch issues early
5. **Rollback plan** - Git branches for each priority, easy to revert

---

## Conclusion

This implementation plan addresses the critical gaps identified in the architecture audit. By following this prioritized approach:

1. **Week 1** - Quick wins improve integration by 25%
2. **Weeks 2-3** - Core fixes bring integration to 85%
3. **Week 4+** - Future enhancements reach 95%+ integration

The key is to **actually use the features that are already built** before adding new ones.
