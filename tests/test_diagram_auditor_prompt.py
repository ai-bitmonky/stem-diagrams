from core.auditor.diagram_auditor import DiagramAuditor, LLMBackend
from core.problem_spec import CanonicalProblemSpec, PhysicsDomain


def test_audit_prompt_includes_telemetry_sections():
    spec = CanonicalProblemSpec(
        domain=PhysicsDomain.MECHANICS,
        problem_type="mechanics",
        problem_text="Block on incline"
    )
    auditor = DiagramAuditor(backend=LLMBackend.MOCK)

    prompt = auditor.generate_audit_prompt(
        spec,
        vlm_description="VLM sees a block with two arrows.",
        structural_report={'score': 0.85, 'missing_in_scene': [], 'relation_gaps': []},
        domain_rule_report={'errors': 1, 'warnings': 0},
        validation_results={'overall_confidence': 0.92, 'refinement_iterations': 1,
                            'semantic_fidelity': {'match': True, 'reasoning': 'All elements present'}},
        svg_excerpt="<svg>...</svg>"
    )

    assert "Vision-Language Model Summary" in prompt
    assert "Structural Validator" in prompt
    assert "Domain Rule Engine" in prompt
    assert "Validation Loop Snapshot" in prompt
    assert "SVG Excerpt" in prompt
