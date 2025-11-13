from types import SimpleNamespace

from core.scene.schema_v1 import Scene, SceneObject, PrimitiveType
from core.validation.structural_validator import compare_plan_scene


def test_structural_validator_detects_missing_objects():
    plan = SimpleNamespace()
    plan.extracted_entities = [
        {'id': 'battery1', 'label': 'Battery'},
        {'id': 'res1', 'label': 'R1'}
    ]
    plan.extracted_relations = []

    scene = Scene()
    scene.objects = [
        SceneObject(id='battery1', type=PrimitiveType.BATTERY_SYMBOL, properties={'label': 'Battery'})
    ]

    report = compare_plan_scene(plan, scene)
    assert 'res1' in report.missing_in_scene
    assert report.score < 1.0
