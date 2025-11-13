# Diagram Planning & Reasoning - Gap Analysis & Roadmap
**Date:** November 9, 2025
**Status:** Gap Documented, Architecture Defined

---

## Executive Summary

**Current State:** Direct pipeline from specs to rendering (no planning layer)
**Roadmap Promise:** Multi-stage planning with constraint solving and symbolic reasoning
**Gap:** 90% of planning and reasoning features missing

This document provides:
1. Analysis of current implementation vs. roadmap promises
2. Detailed architecture for missing planning layer
3. Constraint solver and symbolic engine integration design
4. Implementation roadmap with phases and timelines

---

## Current Implementation vs. Roadmap

### ✅ What Exists (10% of Roadmap)

**Current Pipeline** ([unified_diagram_pipeline.py](unified_diagram_pipeline.py:197))
```python
def generate(problem_text: str) -> DiagramResult:
    # Phase 1: Problem Understanding (AI Analyzer)
    specs = self.ai_analyzer.analyze(problem_text)

    # Phase 2: Scene Synthesis (direct scene building)
    scene = self.scene_builder.build(specs)

    # Phase 4: Physics Validation
    report, scene = self.validator.validate(scene, specs)

    # Phase 5: Layout (heuristic placement)
    self.layout_engine.optimize_layout(scene, specs)

    # Phase 6: Rendering
    svg = self.renderer.render(scene, specs, style)
```

**Layout Engine** ([core/universal_layout_engine.py](core/universal_layout_engine.py:112))
```python
def optimize_layout(self, scene, spec):
    domain = spec.domain

    # Domain-specific heuristics
    if domain == PhysicsDomain.MECHANICS:
        self._place_mechanics(scene, spec)
    elif domain == PhysicsDomain.CURRENT_ELECTRICITY:
        self._place_circuit(scene, spec)
    # ... etc

    # Hardcoded placement rules
    # No constraint solving
    # Physics-domain only
```

**Limitations:**
- ❌ No planning phase
- ❌ Goes directly from specs to scene
- ❌ Heuristic layout only (hardcoded rules)
- ❌ No constraint solver
- ❌ No symbolic reasoning
- ❌ No auditor/validator LLM
- ❌ No complexity-driven model orchestration

---

### ❌ What's Missing (90% of Roadmap)

#### 1. DiagramPlanner (NOT Implemented)

**Promised Architecture:**
```python
class DiagramPlanner:
    """Multi-stage diagram planning with constraint solving"""

    def plan(self, specs: CanonicalProblemSpec) -> DiagramPlan:
        # Stage 1: Decomposition
        subproblems = self.decompose(specs)

        # Stage 2: Strategy Selection
        strategy = self.select_strategy(specs)

        # Stage 3: Constraint Formulation
        constraints = self.formulate_constraints(specs, strategy)

        # Stage 4: Constraint Solving (Z3)
        solution = self.solve_constraints(constraints)

        # Stage 5: Plan Synthesis
        plan = self.synthesize_plan(solution, strategy)

        return plan
```

**Current State:** ❌ Not implemented - direct scene building

**Gap:**
- No problem decomposition
- No strategy selection
- No constraint formulation
- No plan synthesis
- No multi-stage reasoning

---

#### 2. Auditor LLM (NOT Implemented)

**Promised:**
```python
class DiagramAuditor:
    """LLM-based diagram quality auditor"""

    def audit(self, scene: Scene, specs: CanonicalProblemSpec) -> AuditReport:
        # Generate critique using LLM
        critique = self.llm.critique(scene, specs)

        # Identify issues
        issues = self.extract_issues(critique)

        # Suggest corrections
        corrections = self.suggest_corrections(issues)

        return AuditReport(
            issues=issues,
            corrections=corrections,
            confidence=critique.confidence
        )
```

**Current State:** ❌ Only rule-based validation (UniversalValidator)

**Gap:**
- No LLM-based quality review
- No semantic critique
- No correction suggestions
- No iterative refinement

---

#### 3. Complexity-Driven Model Orchestration (NOT Implemented)

**Promised:**
```python
class ModelOrchestrator:
    """Dynamically select models based on problem complexity"""

    def select_model(self, specs: CanonicalProblemSpec) -> Model:
        complexity = self.assess_complexity(specs)

        if complexity < 0.3:
            return FastHeuristicModel()  # Simple problems
        elif complexity < 0.7:
            return ConstraintSolverModel()  # Medium complexity
        else:
            return HybridReasoningModel()  # Complex problems
```

**Current State:** ❌ Single heuristic approach for all problems

**Gap:**
- No complexity assessment
- No model selection
- No dynamic optimization
- One-size-fits-all approach

---

#### 4. Constraint Solvers (NOT Implemented)

**Promised Tools:**

**Z3 (SMT Solver):**
```python
from z3 import *

class Z3LayoutSolver:
    """Use Z3 for optimal layout under constraints"""

    def solve_layout(self, objects, constraints):
        # Define variables
        positions = {obj.id: (Real(f'{obj.id}_x'), Real(f'{obj.id}_y'))
                    for obj in objects}

        solver = Solver()

        # Add constraints
        for obj in objects:
            x, y = positions[obj.id]
            # Canvas bounds
            solver.add(And(x >= 0, x <= 800, y >= 0, y <= 600))

        # No overlap constraints
        for obj1, obj2 in combinations(objects, 2):
            x1, y1 = positions[obj1.id]
            x2, y2 = positions[obj2.id]
            solver.add(Or(
                x1 + obj1.width <= x2,
                x2 + obj2.width <= x1,
                y1 + obj1.height <= y2,
                y2 + obj2.height <= y1
            ))

        # Alignment constraints
        # Distance constraints
        # ... etc

        if solver.check() == sat:
            model = solver.model()
            # Extract solution
            return {obj.id: (model[x].as_long(), model[y].as_long())
                    for obj, (x, y) in positions.items()}
```

**Current State:** ❌ No constraint solver - hardcoded heuristics

**Gap:**
- No SMT solving
- No optimization under constraints
- No guarantee of constraint satisfaction
- Manual positioning rules

---

#### 5. Symbolic Physics Engines (NOT Implemented)

**Promised - SymPy Integration:**
```python
from sympy import symbols, solve, Eq
from sympy.physics.mechanics import *

class SymbolicPhysicsEngine:
    """Solve physics problems symbolically"""

    def solve_kinematics(self, problem):
        # Define symbols
        v0, v, a, t, s = symbols('v0 v a t s')

        # Kinematic equations
        eqs = [
            Eq(v, v0 + a*t),
            Eq(s, v0*t + a*t**2/2),
            Eq(v**2, v0**2 + 2*a*s)
        ]

        # Solve for unknowns
        solution = solve(eqs, [v, t, s])
        return solution

    def solve_forces(self, fbd: FreeBodyDiagram):
        # Symbolic force balance
        F_x, F_y = symbols('F_x F_y')

        # ΣF = 0 for equilibrium
        sum_x = sum(f.magnitude * cos(f.angle) for f in fbd.forces)
        sum_y = sum(f.magnitude * sin(f.angle) for f in fbd.forces)

        solution = solve([Eq(sum_x, 0), Eq(sum_y, 0)])
        return solution
```

**Current State:** ❌ Hardcoded force calculations only

**Gap:**
- No symbolic solving
- No equation manipulation
- No physics law application
- Numeric-only calculations

---

#### 6. Geometry Engines (NOT Implemented)

**Promised - Shapely/Computational Geometry:**
```python
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import unary_union

class GeometryEngine:
    """Computational geometry for diagram layout"""

    def check_overlap(self, obj1, obj2):
        poly1 = self.to_polygon(obj1)
        poly2 = self.to_polygon(obj2)
        return poly1.intersects(poly2)

    def find_non_overlapping_position(self, obj, existing_objects):
        # Use spatial indexing and collision detection
        for x in range(0, canvas_width, 10):
            for y in range(0, canvas_height, 10):
                candidate = self.place_at(obj, x, y)
                if not any(self.check_overlap(candidate, existing)
                          for existing in existing_objects):
                    return (x, y)
        return None

    def optimize_packing(self, objects):
        # 2D bin packing algorithm
        packed = []
        for obj in sorted(objects, key=lambda o: o.area, reverse=True):
            pos = self.find_best_position(obj, packed)
            packed.append(self.place_at(obj, *pos))
        return packed
```

**Current State:** ❌ Simple bounding box checks only

**Gap:**
- No computational geometry
- No spatial indexing
- No packing algorithms
- No collision detection

---

## Architecture Comparison

### Current (Heuristic Only)

```
CanonicalProblemSpec
    ↓
SceneBuilder (direct)
  - Domain-specific rules
  - Hardcoded positioning
    ↓
UniversalLayoutEngine
  - if/else domain checks
  - Heuristic placement
  - No optimization
    ↓
Scene (with positions)
    ↓
Renderer
```

**Strengths:**
- Fast (< 0.1s)
- Simple to understand
- Works for basic cases

**Limitations:**
- No guarantee of correctness
- Cannot handle complex constraints
- Domain-specific code duplication
- No optimization
- Brittle (breaks on edge cases)

---

### Promised (Planning & Reasoning)

```
CanonicalProblemSpec
    ↓
┌────────────────────────────────────┐
│ DiagramPlanner                     │
│  ├─ Complexity Assessment          │
│  ├─ Problem Decomposition          │
│  ├─ Strategy Selection             │
│  └─ Constraint Formulation         │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│ Constraint Solver (Z3)             │
│  - SMT solving                     │
│  - Optimal layout                  │
│  - Constraint satisfaction         │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│ Symbolic Physics Engine (SymPy)    │
│  - Equation solving                │
│  - Force balance                   │
│  - Kinematic analysis              │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│ Geometry Engine (Shapely)          │
│  - Collision detection             │
│  - Spatial optimization            │
│  - Packing algorithms              │
└────────────────────────────────────┘
    ↓
DiagramPlan (with optimized layout)
    ↓
┌────────────────────────────────────┐
│ Auditor LLM                        │
│  - Quality critique                │
│  - Semantic validation             │
│  - Correction suggestions          │
└────────────────────────────────────┘
    ↓
Scene (validated & optimized)
    ↓
Renderer
```

**Strengths:**
- Formal correctness guarantees (Z3)
- Handles complex constraints
- Domain-agnostic (reusable)
- Optimal solutions
- Semantic understanding (LLM)
- Self-correcting (auditor)

**Limitations:**
- Slower (1-10s depending on complexity)
- Requires external dependencies (Z3, SymPy)
- More complex to implement
- Higher computational cost

---

## Implementation Roadmap

### Phase 1: DiagramPlanner Foundation (6-8 weeks)

**Goal:** Implement basic diagram planning layer

**Tasks:**
1. Create DiagramPlanner class
2. Implement complexity assessment
3. Add problem decomposition
4. Design constraint formulation
5. Create DiagramPlan dataclass

**Deliverables:**
- `core/diagram_planner.py` (800 lines)
- `core/diagram_plan.py` (300 lines)
- Planning strategy interfaces
- Unit tests

**Example:**
```python
class DiagramPlanner:
    def plan(self, specs: CanonicalProblemSpec) -> DiagramPlan:
        # Assess complexity
        complexity = self.assess_complexity(specs)

        # Decompose if needed
        if complexity > 0.7:
            subproblems = self.decompose(specs)
        else:
            subproblems = [specs]

        # Select strategy per subproblem
        strategies = [self.select_strategy(sp) for sp in subproblems]

        # Formulate constraints
        constraints = [self.formulate_constraints(sp, strat)
                      for sp, strat in zip(subproblems, strategies)]

        return DiagramPlan(
            subproblems=subproblems,
            strategies=strategies,
            constraints=constraints,
            complexity=complexity
        )
```

---

### Phase 2: Z3 Constraint Solver Integration (4-6 weeks)

**Goal:** Add SMT solving for optimal layout

**Tasks:**
1. Install and configure Z3
2. Implement Z3LayoutSolver
3. Define layout constraints (bounds, overlap, distance, alignment)
4. Integrate with DiagramPlanner
5. Benchmark vs. heuristic approach

**Dependencies:**
```bash
pip install z3-solver
```

**Implementation:**
```python
from z3 import *

class Z3LayoutSolver:
    def solve_layout(self, plan: DiagramPlan) -> LayoutSolution:
        solver = Solver()

        # Create variables for each object
        vars = {}
        for obj in plan.objects:
            vars[obj.id] = {
                'x': Real(f'{obj.id}_x'),
                'y': Real(f'{obj.id}_y'),
                'width': obj.dimensions.width,
                'height': obj.dimensions.height
            }

        # Canvas bounds
        for obj_id, obj_vars in vars.items():
            solver.add(And(
                obj_vars['x'] >= 0,
                obj_vars['y'] >= 0,
                obj_vars['x'] + obj_vars['width'] <= plan.canvas_width,
                obj_vars['y'] + obj_vars['height'] <= plan.canvas_height
            ))

        # No overlap
        for (id1, v1), (id2, v2) in combinations(vars.items(), 2):
            solver.add(Or(
                v1['x'] + v1['width'] <= v2['x'],  # v1 left of v2
                v2['x'] + v2['width'] <= v1['x'],  # v2 left of v1
                v1['y'] + v1['height'] <= v2['y'], # v1 above v2
                v2['y'] + v2['height'] <= v1['y']  # v2 above v1
            ))

        # Apply custom constraints from plan
        for constraint in plan.constraints:
            if constraint.type == 'distance':
                v1 = vars[constraint.obj1]
                v2 = vars[constraint.obj2]
                dist_x = v2['x'] - v1['x']
                dist_y = v2['y'] - v1['y']
                solver.add(dist_x**2 + dist_y**2 == constraint.value**2)

            elif constraint.type == 'alignment_horizontal':
                objs = [vars[oid] for oid in constraint.objects]
                for v1, v2 in zip(objs, objs[1:]):
                    solver.add(v1['y'] == v2['y'])

            # ... more constraint types

        # Solve
        if solver.check() == sat:
            model = solver.model()
            solution = {}
            for obj_id, obj_vars in vars.items():
                solution[obj_id] = {
                    'x': model[obj_vars['x']].as_long(),
                    'y': model[obj_vars['y']].as_long()
                }
            return LayoutSolution(positions=solution, satisfiable=True)
        else:
            return LayoutSolution(positions={}, satisfiable=False)
```

---

### Phase 3: SymPy Symbolic Physics (4-6 weeks)

**Goal:** Symbolic equation solving for physics

**Tasks:**
1. Install SymPy
2. Implement SymbolicPhysicsEngine
3. Add kinematic solvers
4. Add force balance solvers
5. Integrate with physics domain builder

**Dependencies:**
```bash
pip install sympy
```

**Implementation:**
```python
from sympy import *
from sympy.physics.mechanics import *

class SymbolicPhysicsEngine:
    def solve_force_balance(self, forces: List[Force]) -> Dict:
        """Solve ΣF = 0 symbolically"""
        # Sum forces in x and y
        F_x = sum(f.magnitude * cos(radians(f.angle)) for f in forces)
        F_y = sum(f.magnitude * sin(radians(f.angle)) for f in forces)

        # Find unknowns
        unknowns = [f.magnitude for f in forces if f.magnitude is None]

        # Solve equilibrium equations
        solution = solve([Eq(F_x, 0), Eq(F_y, 0)], unknowns)

        return solution

    def solve_kinematics(self, initial_conditions, target):
        """Solve kinematic equations symbolically"""
        # Define symbols
        v0, v, a, t, s = symbols('v0 v a t s')

        # Kinematic equations
        eq1 = Eq(v, v0 + a*t)
        eq2 = Eq(s, v0*t + Rational(1,2)*a*t**2)
        eq3 = Eq(v**2, v0**2 + 2*a*s)

        # Apply initial conditions
        subs_dict = initial_conditions

        # Solve for target variable
        solution = solve([eq1, eq2, eq3], target, dict=True)

        return solution[0][target].subs(subs_dict)
```

---

### Phase 4: Geometry Engine (3-4 weeks)

**Goal:** Computational geometry for layout

**Tasks:**
1. Install Shapely
2. Implement GeometryEngine
3. Add collision detection
4. Add spatial indexing
5. Add packing algorithms

**Dependencies:**
```bash
pip install shapely rtree
```

**Implementation:**
```python
from shapely.geometry import Point, Polygon, box
from shapely.strtree import STRtree
from shapely.ops import unary_union

class GeometryEngine:
    def __init__(self):
        self.spatial_index = None

    def build_spatial_index(self, objects):
        """Build R-tree spatial index"""
        geometries = [self.to_geometry(obj) for obj in objects]
        self.spatial_index = STRtree(geometries)

    def to_geometry(self, obj):
        """Convert scene object to shapely geometry"""
        return box(
            obj.position.x,
            obj.position.y,
            obj.position.x + obj.dimensions.width,
            obj.position.y + obj.dimensions.height
        )

    def check_overlap(self, obj1, obj2):
        g1 = self.to_geometry(obj1)
        g2 = self.to_geometry(obj2)
        return g1.intersects(g2)

    def find_non_overlapping_position(self, obj, existing_objects, canvas):
        """Find valid position using spatial index"""
        if not existing_objects:
            return (canvas.width / 2, canvas.height / 2)

        self.build_spatial_index(existing_objects)

        # Try positions in a grid
        step = 20
        for x in range(0, canvas.width - obj.width, step):
            for y in range(0, canvas.height - obj.height, step):
                candidate = self.place_at(obj, x, y)
                candidate_geom = self.to_geometry(candidate)

                # Quick spatial index check
                nearby = self.spatial_index.query(candidate_geom)
                if not any(candidate_geom.intersects(g) for g in nearby):
                    return (x, y)

        return None

    def pack_objects(self, objects, canvas):
        """2D bin packing for optimal space usage"""
        # Sort by area (largest first)
        sorted_objs = sorted(objects,
                           key=lambda o: o.width * o.height,
                           reverse=True)

        packed = []
        for obj in sorted_objs:
            pos = self.find_non_overlapping_position(obj, packed, canvas)
            if pos:
                packed.append(self.place_at(obj, *pos))

        return packed
```

---

### Phase 5: Auditor LLM (5-7 weeks)

**Goal:** LLM-based diagram quality review

**Tasks:**
1. Design auditor prompts
2. Implement DiagramAuditor class
3. Add critique generation
4. Add issue extraction
5. Add correction suggestions
6. Implement iterative refinement loop

**Dependencies:**
```bash
pip install openai anthropic  # or local LLM
```

**Implementation:**
```python
from anthropic import Anthropic

class DiagramAuditor:
    def __init__(self):
        self.client = Anthropic()

    def audit(self, scene: Scene, specs: CanonicalProblemSpec) -> AuditReport:
        # Generate scene description
        description = self.describe_scene(scene)

        # Create audit prompt
        prompt = f"""You are a physics diagram quality auditor.

Problem: {specs.problem_text}

Generated Diagram:
{description}

Please critique this diagram:
1. Are all components from the problem present?
2. Are the spatial relationships correct?
3. Are the forces correctly represented?
4. Are there any physics errors?
5. Is the layout clear and unambiguous?

Provide specific issues and corrections."""

        # Get LLM critique
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )

        critique_text = response.content[0].text

        # Parse critique
        issues = self.extract_issues(critique_text)
        corrections = self.suggest_corrections(issues)

        return AuditReport(
            issues=issues,
            corrections=corrections,
            critique=critique_text,
            confidence=self.assess_confidence(critique_text)
        )

    def describe_scene(self, scene: Scene) -> str:
        """Generate textual description of scene"""
        desc = f"Canvas: {scene.width}x{scene.height}px\n\n"
        desc += "Objects:\n"
        for obj in scene.objects:
            desc += f"  - {obj.id} ({obj.type}) at ({obj.x}, {obj.y})\n"
        desc += "\nRelationships:\n"
        for rel in scene.relationships:
            desc += f"  - {rel.subject} {rel.type} {rel.object}\n"
        return desc
```

---

### Phase 6: Model Orchestration (3-4 weeks)

**Goal:** Complexity-driven model selection

**Tasks:**
1. Implement complexity assessment
2. Design model selection strategy
3. Create model interfaces
4. Implement fallback mechanisms
5. Add performance monitoring

**Implementation:**
```python
class ModelOrchestrator:
    def __init__(self):
        self.models = {
            'heuristic': HeuristicLayoutModel(),
            'constraint': Z3LayoutSolver(),
            'hybrid': HybridReasoningModel()
        }

    def assess_complexity(self, specs: CanonicalProblemSpec) -> float:
        """Assess problem complexity (0-1)"""
        score = 0.0

        # Object count
        score += min(len(specs.objects) / 20, 0.3)

        # Constraint complexity
        score += min(len(specs.constraints) / 10, 0.3)

        # Relationship complexity
        score += min(len(specs.relationships) / 15, 0.2)

        # Domain complexity
        if specs.domain in [PhysicsDomain.THERMODYNAMICS, PhysicsDomain.OPTICS]:
            score += 0.2

        return min(score, 1.0)

    def select_model(self, specs: CanonicalProblemSpec) -> LayoutModel:
        complexity = self.assess_complexity(specs)

        if complexity < 0.3:
            # Simple problem - use fast heuristic
            return self.models['heuristic']
        elif complexity < 0.7:
            # Medium complexity - use constraint solver
            return self.models['constraint']
        else:
            # Complex problem - use hybrid reasoning
            return self.models['hybrid']

    def generate_with_fallback(self, specs):
        """Try models in order of decreasing sophistication"""
        models = ['hybrid', 'constraint', 'heuristic']

        for model_name in models:
            try:
                model = self.models[model_name]
                result = model.generate(specs)
                if result.is_valid():
                    return result
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue

        raise Exception("All models failed")
```

---

### Phase 7: Full Integration (4-6 weeks)

**Goal:** Unified planning & reasoning pipeline

**Tasks:**
1. Integrate all components
2. Create unified API
3. Add caching and optimization
4. Comprehensive testing
5. Performance benchmarking

**Final Architecture:**
```python
class UnifiedDiagramPipeline:
    def __init__(self):
        self.planner = DiagramPlanner()
        self.orchestrator = ModelOrchestrator()
        self.z3_solver = Z3LayoutSolver()
        self.sympy_engine = SymbolicPhysicsEngine()
        self.geometry = GeometryEngine()
        self.auditor = DiagramAuditor()

    def generate(self, problem_text):
        # Phase 1: Understanding
        specs = self.ai_analyzer.analyze(problem_text)

        # Phase 2: Planning (NEW)
        plan = self.planner.plan(specs)

        # Phase 3: Model Selection (NEW)
        model = self.orchestrator.select_model(specs)

        # Phase 4: Constraint Solving (NEW)
        if plan.complexity > 0.5:
            layout = self.z3_solver.solve_layout(plan)
        else:
            layout = self.heuristic_layout(plan)

        # Phase 5: Symbolic Physics (NEW)
        if specs.domain == PhysicsDomain.MECHANICS:
            physics_solution = self.sympy_engine.solve_forces(specs)
            layout = self.apply_physics_solution(layout, physics_solution)

        # Phase 6: Geometry Optimization (NEW)
        layout = self.geometry.optimize_packing(layout)

        # Phase 7: Scene Building
        scene = self.build_scene(layout, specs)

        # Phase 8: Auditing (NEW)
        audit = self.auditor.audit(scene, specs)

        # Phase 9: Refinement (NEW)
        if audit.has_issues():
            scene = self.refine_scene(scene, audit.corrections)

        # Phase 10: Rendering
        svg = self.renderer.render(scene)

        return DiagramResult(svg=svg, scene=scene, audit=audit)
```

---

## Files to Create

### Core Planning

1. **core/diagram_planner.py** (800 lines)
   - DiagramPlanner class
   - Complexity assessment
   - Problem decomposition
   - Strategy selection
   - Constraint formulation

2. **core/diagram_plan.py** (300 lines)
   - DiagramPlan dataclass
   - Subproblem definitions
   - Strategy representations
   - Constraint schemas

3. **core/model_orchestrator.py** (600 lines)
   - ModelOrchestrator class
   - Complexity scoring
   - Model selection logic
   - Fallback mechanisms

### Constraint Solving

4. **core/solvers/z3_layout_solver.py** (700 lines)
   - Z3LayoutSolver class
   - Constraint encoding
   - SMT solving
   - Solution extraction

5. **core/solvers/constraint_formulator.py** (500 lines)
   - Constraint formulation helpers
   - Domain-specific constraints
   - Optimization objectives

### Symbolic Reasoning

6. **core/symbolic/physics_engine.py** (800 lines)
   - SymbolicPhysicsEngine class
   - Kinematic solvers
   - Force balance solvers
   - Energy analysis

7. **core/symbolic/geometry_engine.py** (600 lines)
   - GeometryEngine class
   - Collision detection
   - Spatial indexing
   - Packing algorithms

### Quality Auditing

8. **core/auditor/diagram_auditor.py** (700 lines)
   - DiagramAuditor class
   - LLM integration
   - Issue extraction
   - Correction suggestions

9. **core/auditor/refinement_loop.py** (400 lines)
   - Iterative refinement
   - Feedback incorporation
   - Convergence criteria

### Testing

10. **tests/test_planner.py** (600 lines)
11. **tests/test_z3_solver.py** (500 lines)
12. **tests/test_symbolic_engine.py** (400 lines)
13. **tests/test_auditor.py** (500 lines)

---

## Dependencies

```txt
# Current
spacy>=3.7.0

# Phase 2: Z3 Solver
z3-solver>=4.12.0

# Phase 3: Symbolic Physics
sympy>=1.12.0

# Phase 4: Geometry
shapely>=2.0.0
rtree>=1.1.0

# Phase 5: Auditor LLM
anthropic>=0.7.0  # or openai, etc.

# Phase 6: Optimization
scipy>=1.11.0
networkx>=3.2.0
```

---

## Timeline & Effort

| Phase | Duration | Effort | Dependencies |
|-------|----------|--------|--------------|
| Phase 1: DiagramPlanner | 6-8 weeks | 180-240 hours | None |
| Phase 2: Z3 Solver | 4-6 weeks | 120-180 hours | Phase 1, z3-solver |
| Phase 3: SymPy Engine | 4-6 weeks | 120-180 hours | Phase 1, sympy |
| Phase 4: Geometry Engine | 3-4 weeks | 90-120 hours | shapely, rtree |
| Phase 5: Auditor LLM | 5-7 weeks | 150-210 hours | Phase 1, LLM API |
| Phase 6: Orchestration | 3-4 weeks | 90-120 hours | All phases |
| Phase 7: Integration | 4-6 weeks | 120-180 hours | All phases |
| **TOTAL** | **29-41 weeks** | **870-1230 hours** | |

**Estimated completion:** 7-10 months (with 1 full-time developer)

---

## Priority Recommendation

**High Priority (Next 3 months):**
1. ✅ DiagramPlanner Foundation (Phase 1)
   - Enables all other phases
   - Immediate architectural benefit
   - Clear separation of concerns

2. ✅ Z3 Solver Integration (Phase 2)
   - Biggest quality improvement
   - Formal correctness guarantees
   - Handles complex constraints

**Medium Priority (3-6 months):**
3. SymPy Symbolic Physics (Phase 3)
   - Physics domain benefit
   - Equation solving capability

4. Geometry Engine (Phase 4)
   - Better collision detection
   - Optimal packing

**Lower Priority (6+ months):**
5. Auditor LLM (Phase 5)
   - Requires mature base system
   - Expensive (LLM API costs)
   - Incremental improvement

6. Model Orchestration (Phase 6)
   - Only valuable after multiple models exist

---

## Current Workarounds

Until planning & reasoning is implemented:

1. **Heuristic Layout** (implemented)
   - Domain-specific placement rules
   - Works for simple cases
   - Fast but limited

2. **UniversalValidator** (implemented)
   - Rule-based validation
   - Physics constraint checking
   - No symbolic solving

3. **Manual Constraint Handling** (implemented)
   - Hardcoded constraint logic
   - Works for common cases
   - Not general-purpose

---

## Testing Strategy

### Benchmark Problems

Create test suite with:
- 50 simple layout problems
- 50 medium complexity (constraints)
- 30 complex (many constraints)
- 20 edge cases

### Metrics

1. **Layout Quality:**
   - Constraint satisfaction rate
   - Overlap percentage
   - Visual clarity score (human eval)

2. **Solving Performance:**
   - Solve time (Z3)
   - Memory usage
   - Success rate

3. **End-to-End:**
   - Diagram correctness
   - Audit score
   - Processing time

---

## Summary

**Current State:**
- ✅ Heuristic layout working (10% of roadmap)
- ✅ Domain-specific rules
- ✅ Fast but limited
- ❌ No planning layer
- ❌ No constraint solving
- ❌ No symbolic reasoning
- ❌ No auditor

**Gap:**
- ❌ 90% of planning features missing
- ❌ All reasoning engines (Z3, SymPy, Shapely)
- ❌ Auditor LLM
- ❌ Model orchestration
- ❌ Formal correctness

**Roadmap:**
- 7 phases over 7-10 months
- 870-1230 hours of development
- Clear priorities
- Incremental value delivery

**Recommendation:**
Start with Phase 1 (DiagramPlanner) and Phase 2 (Z3 Solver) as they provide the most immediate benefit and enable all other features.

---

**Status:** Gap Documented, Architecture Designed
**Next Action:** Prioritize and begin Phase 1 (DiagramPlanner)
**Timeline:** 7-10 months for full implementation
**Effort:** ~1000 hours total
