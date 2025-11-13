from types import SimpleNamespace

from core.problem_spec import CanonicalProblemSpec, PhysicsDomain
from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType, PrimitiveType
from core.universal_layout_engine import UniversalLayoutEngine


def test_layout_engine_handles_missing_solvers_gracefully():
    engine = UniversalLayoutEngine(width=400, height=300)
    # Force solvers to be unavailable regardless of environment
    engine.z3_solver = None
    engine.sympy_solver = None
    engine.cassowary_solver_cls = None
    engine._solver_warning_cache.clear()

    scene = Scene()
    scene.objects = [
        SceneObject(id="a", type=PrimitiveType.RECTANGLE, position={'x': 0, 'y': 0}),
        SceneObject(id="b", type=PrimitiveType.RECTANGLE, position={'x': 50, 'y': 0}),
    ]
    scene.constraints = [
        Constraint(type=ConstraintType.DISTANCE, objects=["a", "b"], value=100),
        Constraint(type=ConstraintType.ALIGNED_H, objects=["a", "b"]),
    ]

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="layout",
        problem_text="two blocks"
    )
    spec.diagram_plan = SimpleNamespace(global_constraints=[{'type': 'distance'}])

    applied = engine._apply_advanced_constraint_solvers(scene, spec)
    assert applied == []
    assert 'Z3' in engine._solver_warning_cache
    assert 'SymPy' in engine._solver_warning_cache
    assert 'Cassowary' in engine._solver_warning_cache
