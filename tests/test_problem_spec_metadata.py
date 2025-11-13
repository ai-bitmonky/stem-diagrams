from core.problem_spec import CanonicalProblemSpec, PhysicsDomain
from core.universal_ai_analyzer import UniversalAIAnalyzer


def test_problem_spec_to_dict_includes_provenance_and_metadata():
    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="demo",
        problem_text="A block on an incline"
    )
    spec.attribute_provenance['objects'] = 'local'
    spec.analysis_metadata['local'] = {'objects': 1}

    data = spec.to_dict()
    assert 'attribute_provenance' in data
    assert data['attribute_provenance']['objects'] == 'local'
    assert 'analysis_metadata' in data
    assert data['analysis_metadata']['local']['objects'] == 1
    assert 'diagram_plan_metadata' in data


def test_provenance_helper_merges_sources_without_api_calls():
    analyzer = UniversalAIAnalyzer(api_key="dummy-key", use_local_fallback=False)
    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="demo",
        problem_text="Object connected to spring",
        objects=[{'id': 'obj1', 'type': 'block'}],
        relationships=[]
    )

    provenance = analyzer._build_provenance_map(spec, source='local')
    assert provenance['objects'] == 'local'

    analyzer._tag_provenance(provenance, 'objects', 'deepseek')
    assert provenance['objects'] == 'local+deepseek'
