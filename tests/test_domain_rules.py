from core.domain_rules import run_domain_rules
from core.problem_spec import CanonicalProblemSpec, PhysicsDomain
from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType, PrimitiveType


def _make_circuit_scene(closed: bool = True) -> Scene:
    scene = Scene()
    scene.objects = [
        SceneObject(id="battery1", type=PrimitiveType.BATTERY_SYMBOL),
        SceneObject(id="resistor1", type=PrimitiveType.RESISTOR_SYMBOL),
        SceneObject(id="switch1", type=PrimitiveType.LINE),
    ]
    if closed:
        scene.constraints.extend([
            Constraint(type=ConstraintType.CONNECTED, objects=["battery1", "resistor1"]),
            Constraint(type=ConstraintType.CONNECTED, objects=["resistor1", "switch1"]),
            Constraint(type=ConstraintType.CONNECTED, objects=["switch1", "battery1"]),
        ])
    else:
        scene.constraints.extend([
            Constraint(type=ConstraintType.CONNECTED, objects=["battery1", "resistor1"]),
            Constraint(type=ConstraintType.CONNECTED, objects=["resistor1", "switch1"]),
        ])
    return scene


def _make_circuit_spec() -> CanonicalProblemSpec:
    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.CURRENT_ELECTRICITY,
        problem_type="circuit",
        problem_text="Battery feeding resistor and switch",
        relationships=[
            {"source": "battery1", "target": "resistor1", "type": "connected_to"},
            {"source": "resistor1", "target": "switch1", "type": "connected_to"},
        ]
    )
    return spec


def test_kirchhoff_detects_closed_loop():
    scene = _make_circuit_scene(closed=True)
    spec = _make_circuit_spec()
    report = run_domain_rules("current_electricity", scene, spec)
    kirchhoff = next(item for item in report['checks'] if item['name'] == 'Kirchhoff Loop')
    assert kirchhoff['passed'] is True, kirchhoff
    assert report['errors'] == 0


def test_kirchhoff_flags_open_loop():
    scene = _make_circuit_scene(closed=False)
    spec = _make_circuit_spec()
    report = run_domain_rules("current_electricity", scene, spec)
    kirchhoff = next(item for item in report['checks'] if item['name'] == 'Kirchhoff Loop')
    assert kirchhoff['passed'] is False
    assert 'closed loop' in kirchhoff['details'].lower() or 'connections' in kirchhoff['details'].lower()
    assert report['errors'] >= 1


def test_newton_force_equilibrium_uses_vector_sum():
    scene = Scene()
    mass = SceneObject(id="m1", type=PrimitiveType.MASS)
    # Balanced forces along x-axis
    f_left = SceneObject(
        id="F_left",
        type=PrimitiveType.ARROW,
        properties={'target': 'm1', 'components': {'x': -5, 'y': 0}, 'magnitude': 5}
    )
    f_right = SceneObject(
        id="F_right",
        type=PrimitiveType.ARROW,
        properties={'target': 'm1', 'components': {'x': 5, 'y': 0}, 'magnitude': 5}
    )
    scene.objects = [mass, f_left, f_right]

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="forces",
        problem_text="Block with opposing forces"
    )

    report = run_domain_rules("mechanics", scene, spec)
    newton = next(item for item in report['checks'] if item['name'] == 'Newton Force Equilibrium')
    assert newton['passed'] is True

    # Remove counter-force to trigger failure
    scene.objects = [mass, f_left]
    report = run_domain_rules("mechanics", scene, spec)
    newton = next(item for item in report['checks'] if item['name'] == 'Newton Force Equilibrium')
    assert newton['passed'] is False
    assert 'residual' in newton['details'].lower()


def test_conservation_laws_energy_balance():
    scene = Scene()
    # Initial state with kinetic energy
    initial = SceneObject(
        id="ball_initial",
        type=PrimitiveType.MASS,
        properties={'kinetic_energy': 100.0, 'potential_energy': 0.0}
    )
    # Final state with potential energy (conservation)
    final = SceneObject(
        id="ball_final",
        type=PrimitiveType.MASS,
        properties={'kinetic_energy': 0.0, 'potential_energy': 100.0}
    )
    scene.objects = [initial, final]

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="energy",
        problem_text="Ball falling and bouncing"
    )

    report = run_domain_rules("mechanics", scene, spec)
    conservation = next(item for item in report['checks'] if item['name'] == 'Conservation Laws')
    assert conservation['passed'] is True

    # Test violation: energy not conserved
    final.properties['potential_energy'] = 50.0  # Lost 50J
    report = run_domain_rules("mechanics", scene, spec)
    conservation = next(item for item in report['checks'] if item['name'] == 'Conservation Laws')
    assert conservation['passed'] is False
    assert 'diff' in conservation['details'].lower()


def test_lens_equation_validator():
    scene = Scene()
    # Lens with f=10cm, do=30cm, di should be 15cm (1/10 = 1/30 + 1/15)
    lens = SceneObject(
        id="lens1",
        type=PrimitiveType.LINE,
        properties={
            'focal_length': 10.0,
            'object_distance': 30.0,
            'image_distance': 15.0
        }
    )
    scene.objects = [lens]

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.OPTICS,
        problem_type="lens",
        problem_text="Converging lens image formation"
    )

    report = run_domain_rules("optics", scene, spec)
    lens_check = next(item for item in report['checks'] if item['name'] == 'Lens Equation')
    assert lens_check['passed'] is True

    # Test violation: wrong image distance
    lens.properties['image_distance'] = 20.0  # Incorrect
    report = run_domain_rules("optics", scene, spec)
    lens_check = next(item for item in report['checks'] if item['name'] == 'Lens Equation')
    assert lens_check['passed'] is False
    assert 'expected' in lens_check['details'].lower()


def test_chemical_equation_balancer():
    scene = Scene()
    # 2H2 + O2 -> 2H2O (balanced)
    h2_1 = SceneObject(
        id="H2_reactant1",
        type=PrimitiveType.CIRCLE,
        properties={'atoms': {'H': 2}, 'coefficient': 2, 'label': 'reactant'}
    )
    o2 = SceneObject(
        id="O2_reactant",
        type=PrimitiveType.CIRCLE,
        properties={'atoms': {'O': 2}, 'coefficient': 1, 'label': 'reactant'}
    )
    h2o = SceneObject(
        id="H2O_product",
        type=PrimitiveType.CIRCLE,
        properties={'atoms': {'H': 2, 'O': 1}, 'coefficient': 2, 'label': 'product'}
    )
    scene.objects = [h2_1, o2, h2o]

    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.UNKNOWN,  # Using UNKNOWN since CHEMISTRY not in PhysicsDomain enum
        problem_type="reaction",
        problem_text="Water formation from hydrogen and oxygen"
    )

    report = run_domain_rules("chemistry", scene, spec)
    chem_check = next(item for item in report['checks'] if item['name'] == 'Chemical Balance')
    assert chem_check['passed'] is True

    # Test imbalance: wrong coefficients
    h2o.properties['coefficient'] = 1  # Only 1 H2O instead of 2
    report = run_domain_rules("chemistry", scene, spec)
    chem_check = next(item for item in report['checks'] if item['name'] == 'Chemical Balance')
    assert chem_check['passed'] is False
    assert 'imbalance' in chem_check['details'].lower()
