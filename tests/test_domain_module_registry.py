from types import SimpleNamespace

from core.domain_modules import DomainModuleRegistry


def make_fake_plan(domain="electronics"):
    plan = SimpleNamespace()
    plan.extracted_entities = [
        {'id': 'battery1', 'type': 'battery', 'label': 'Battery'},
        {'id': 'res1', 'type': 'resistor', 'label': 'R1'},
    ]
    plan.extracted_relations = [
        {'source_id': 'battery1', 'target_id': 'res1', 'type': 'SERIES_CONNECTION'}
    ]
    plan.global_constraints = []
    plan.metadata = {'domain_hint': domain}
    plan.strategy = SimpleNamespace(value='constraint_based')
    plan.complexity_score = 0.2
    return plan


def test_domain_module_registry_returns_artifacts_for_electronics():
    registry = DomainModuleRegistry(auto_register=True)
    plan = make_fake_plan()
    artifacts = registry.build_artifacts('electronics', plan)
    assert artifacts, "No domain module artifacts returned for electronics"
    artifact_formats = {artifact.format for artifact in artifacts}
    assert 'svg' in artifact_formats or 'text' in artifact_formats
    svg_artifacts = [artifact for artifact in artifacts if artifact.format == 'svg']
    if svg_artifacts:
        assert svg_artifacts[0].metadata.get('primitive_matches', 0) >= 1


def test_domain_module_registry_handles_unknown_domain():
    registry = DomainModuleRegistry(auto_register=True)
    plan = make_fake_plan()
    artifacts = registry.build_artifacts('unknown_domain', plan)
    assert artifacts == []
