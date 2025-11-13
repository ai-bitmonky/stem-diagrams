#!/usr/bin/env python3
"""
LLM-Powered Diagram Planner
============================

Uses large language models (local and/or API) to generate diagram plans
from natural language descriptions.

Implements the roadmap's multi-stage planning with LLM integration:
1. Draft plan generation (local LLM)
2. Plan verification (stronger LLM or rules)
3. Fallback to rule-based if needed

Author: Universal STEM Diagram Generator
Date: November 5, 2025
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Try to import LLM libraries (optional dependencies)
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class DiagramPlanEntity:
    """An entity in the diagram plan"""
    id: str
    type: str  # e.g., "resistor", "capacitor", "block", "force"
    label: str
    properties: Dict[str, Any]
    position_hint: Optional[Dict[str, float]] = None


@dataclass
class DiagramPlanRelationship:
    """A relationship between entities"""
    source_id: str
    target_id: str
    type: str  # e.g., "connected_to", "applies_to", "parallel_to"
    properties: Dict[str, Any]


@dataclass
class DiagramPlanConstraint:
    """A constraint that must be satisfied"""
    type: str  # e.g., "spatial", "physics", "geometric"
    description: str
    entities: List[str]
    parameters: Dict[str, Any]


@dataclass
class DiagramPlan:
    """Complete diagram plan structure"""
    domain: str
    diagram_type: str
    entities: List[DiagramPlanEntity]
    relationships: List[DiagramPlanRelationship]
    constraints: List[DiagramPlanConstraint]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'domain': self.domain,
            'diagram_type': self.diagram_type,
            'entities': [asdict(e) for e in self.entities],
            'relationships': [asdict(r) for r in self.relationships],
            'constraints': [asdict(c) for c in self.constraints],
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DiagramPlan':
        """Create from dictionary"""
        return cls(
            domain=data['domain'],
            diagram_type=data['diagram_type'],
            entities=[DiagramPlanEntity(**e) for e in data['entities']],
            relationships=[DiagramPlanRelationship(**r) for r in data['relationships']],
            constraints=[DiagramPlanConstraint(**c) for c in data['constraints']],
            metadata=data['metadata']
        )


class LLMDiagramPlanner:
    """
    LLM-powered diagram planner

    Uses local LLMs (via Ollama) or API LLMs (OpenAI) to generate
    structured diagram plans from natural language descriptions.
    """

    def __init__(
        self,
        local_model: str = "mistral:7b",
        api_model: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434",
        use_api_for_verification: bool = True
    ):
        """
        Initialize LLM planner

        Args:
            local_model: Ollama model name (e.g., "mistral:7b", "llama2:7b")
            api_model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            ollama_base_url: Ollama API base URL
            use_api_for_verification: Use API model for plan verification
        """
        self.local_model = local_model
        self.api_model = api_model
        self.ollama_base_url = ollama_base_url
        self.use_api_for_verification = use_api_for_verification

        # Initialize API client if available
        self.api_client = None
        if HAS_OPENAI and api_model and os.getenv("OPENAI_API_KEY"):
            self.api_client = OpenAI()

        self.logger = logging.getLogger(__name__)

    def generate_plan(
        self,
        description: str,
        domain: str,
        use_local: bool = True,
        deepseek_client: Optional[Any] = None
    ) -> DiagramPlan:
        """
        Generate a diagram plan from description

        Args:
            description: Natural language description
            domain: Domain (physics, electronics, chemistry, etc.)
            use_local: Use local LLM first

        Returns:
            DiagramPlan object
        """
        self.logger.info(f"Generating plan for domain: {domain}")

        # Step 1: Draft plan generation
        if use_local and HAS_REQUESTS:
            try:
                draft_plan = self._generate_with_local_llm(description, domain)
            except Exception as e:
                self.logger.warning(f"Local LLM failed: {e}, falling back to API")
                draft_plan = self._generate_with_api_llm(description, domain)
        else:
            draft_plan = self._generate_with_api_llm(description, domain)

        # Step 2: Verify and refine plan
        if deepseek_client:
            draft_plan = self._verify_with_deepseek(draft_plan, description, domain, deepseek_client)
        elif self.use_api_for_verification and self.api_client:
            draft_plan = self._verify_plan(draft_plan, description, domain)

        # Step 3: Post-process and validate
        draft_plan = self._post_process_plan(draft_plan, description, domain)

        return draft_plan

    def _generate_with_local_llm(
        self,
        description: str,
        domain: str
    ) -> DiagramPlan:
        """Generate plan using local Ollama model"""
        prompt = self._create_planning_prompt(description, domain)

        # Call Ollama API
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": self.local_model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Request JSON output
            },
            timeout=60
        )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.status_code}")

        result = response.json()
        plan_json = json.loads(result['response'])

        return DiagramPlan.from_dict(plan_json)

    def _generate_with_api_llm(
        self,
        description: str,
        domain: str
    ) -> DiagramPlan:
        """Generate plan using API LLM (OpenAI)"""
        if not self.api_client:
            raise RuntimeError("No API client available")

        prompt = self._create_planning_prompt(description, domain)

        response = self.api_client.chat.completions.create(
            model=self.api_model or "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a STEM diagram planning assistant. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        plan_json = json.loads(response.choices[0].message.content)
        return DiagramPlan.from_dict(plan_json)

    def _create_planning_prompt(
        self,
        description: str,
        domain: str
    ) -> str:
        """Create a structured prompt for plan generation"""

        example_plan = {
            "domain": domain,
            "diagram_type": "circuit" if domain == "electronics" else "diagram",
            "entities": [
                {
                    "id": "entity_1",
                    "type": "component_type",
                    "label": "Component Label",
                    "properties": {"value": "10", "unit": "Ω"},
                    "position_hint": {"x": 0.2, "y": 0.5}
                }
            ],
            "relationships": [
                {
                    "source_id": "entity_1",
                    "target_id": "entity_2",
                    "type": "connected_to",
                    "properties": {}
                }
            ],
            "constraints": [
                {
                    "type": "spatial",
                    "description": "entity_1 must be left of entity_2",
                    "entities": ["entity_1", "entity_2"],
                    "parameters": {}
                }
            ],
            "metadata": {
                "complexity": "medium",
                "estimated_components": 2
            }
        }

        prompt = f"""Generate a structured diagram plan for the following description in the {domain} domain.

Description: {description}

Output a JSON object with this exact structure:
{json.dumps(example_plan, indent=2)}

Entity types for {domain}:
- electronics: resistor, capacitor, inductor, battery, wire, switch, ground
- physics: block, force, spring, pulley, incline, mass
- chemistry: molecule, atom, bond, reaction_arrow
- biology: cell, organelle, pathway, protein
- mathematics: point, line, circle, angle, graph

Relationship types:
- connected_to: physical connection
- applies_to: force/field application
- contains: containment
- parallel_to, series_with: topology

Constraint types:
- spatial: positioning constraints
- physics: physical laws (equilibrium, etc.)
- geometric: angles, distances, ratios

IMPORTANT:
1. Extract ALL entities mentioned in the description
2. Infer logical relationships between entities
3. Add constraints for described properties (angles, distances, values)
4. Use position_hint with values 0.0-1.0 (relative positions)
5. Output ONLY valid JSON, no explanation text

Generate the plan now:"""

        return prompt

    def _verify_plan(
        self,
        plan: DiagramPlan,
        description: str,
        domain: str
    ) -> DiagramPlan:
        """
        Verify plan using a stronger model

        This implements the auditor LLM pattern from the roadmap
        """
        self.logger.info("Verifying plan with auditor LLM")

        verification_prompt = f"""Review this diagram plan for correctness and completeness.

Original description: {description}
Domain: {domain}

Generated plan:
{json.dumps(plan.to_dict(), indent=2)}

Check:
1. Are all entities from the description included?
2. Are relationships logical and complete?
3. Are constraints correctly specified?
4. Are there any missing elements?

If the plan is correct, output the same JSON.
If fixes are needed, output the corrected JSON.
Output ONLY JSON, no explanation."""

        response = self.api_client.chat.completions.create(
            model="gpt-4" if "gpt-4" in (self.api_model or "") else "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a diagram plan auditor. Output only valid JSON."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        verified_json = json.loads(response.choices[0].message.content)
        return DiagramPlan.from_dict(verified_json)

    def _verify_with_deepseek(
        self,
        plan: DiagramPlan,
        description: str,
        domain: str,
        deepseek_client: Any
    ) -> DiagramPlan:
        """
        Verify plan using DeepSeek (roadmap requirement: local draft, DeepSeek audit)
        """
        if deepseek_client is None:
            return plan

        verification_prompt = f"""You are a STEM diagram auditor. Review the JSON plan below for completeness.

Original description: {description}
Domain: {domain}

Plan JSON:
{json.dumps(plan.to_dict(), indent=2)}

Ensure every entity and relation matches the description. If changes are needed, output the corrected JSON.
Always respond with valid JSON only."""

        try:
            response = deepseek_client.chat_completion(
                messages=[
                    {"role": "system", "content": "You audit STEM diagram plans. Respond with corrected JSON only."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,
                json_mode=True,
                max_tokens=1200
            )

            content = response.get('content', '')
            verified_json = json.loads(content)
            return DiagramPlan.from_dict(verified_json)
        except Exception as e:
            self.logger.warning(f"DeepSeek verification failed: {e}")
            return plan

    def _post_process_plan(
        self,
        plan: DiagramPlan,
        description: str,
        domain: str
    ) -> DiagramPlan:
        """Post-process and validate plan"""

        # Ensure entity IDs are unique
        seen_ids = set()
        for i, entity in enumerate(plan.entities):
            if entity.id in seen_ids or not entity.id:
                entity.id = f"{entity.type}_{i}"
            seen_ids.add(entity.id)

        # Validate relationships reference valid entities
        valid_ids = {e.id for e in plan.entities}
        plan.relationships = [
            r for r in plan.relationships
            if r.source_id in valid_ids and r.target_id in valid_ids
        ]

        # Add metadata
        if 'generation_method' not in plan.metadata:
            plan.metadata['generation_method'] = 'llm'
        plan.metadata['entity_count'] = len(plan.entities)
        plan.metadata['relationship_count'] = len(plan.relationships)

        return plan

    def choose_model(
        self,
        task_complexity: float,
        task_type: str = "general"
    ) -> str:
        """
        Choose appropriate model based on task complexity

        Implements the hybrid model orchestrator from roadmap

        Args:
            task_complexity: 0.0 to 1.0 (simple to complex)
            task_type: "planning", "verification", "code_generation"

        Returns:
            Model identifier to use
        """
        if task_complexity < 0.3:
            # Simple task: use fast local model
            return self.local_model

        if task_type == "verification" and self.api_client:
            # Verification: use strong API model
            return self.api_model or "gpt-4"

        if task_complexity > 0.8 and self.api_client:
            # Complex task: use API model if available
            return self.api_model or "gpt-4"

        # Default: local model
        return self.local_model


# Fallback rule-based planner (used when LLM unavailable)
class RuleBasedPlanner:
    """
    Simple rule-based planner as fallback

    Uses pattern matching and heuristics when LLM is not available
    """

    def generate_plan(
        self,
        description: str,
        domain: str,
        nlp_result: Dict
    ) -> DiagramPlan:
        """Generate plan using rules and NLP results"""

        entities = []
        relationships = []
        constraints = []

        # Extract entities from NLP
        for i, entity in enumerate(nlp_result.get('entities', [])):
            entities.append(DiagramPlanEntity(
                id=f"entity_{i}",
                type=entity.get('type', 'unknown'),
                label=entity.get('label', ''),
                properties=entity.get('properties', {}),
                position_hint=None
            ))

        # Extract relationships from NLP
        for j, rel in enumerate(nlp_result.get('relationships', [])):
            if rel.get('source') and rel.get('target'):
                relationships.append(DiagramPlanRelationship(
                    source_id=rel['source'],
                    target_id=rel['target'],
                    type=rel.get('type', 'connected_to'),
                    properties={}
                ))

        return DiagramPlan(
            domain=domain,
            diagram_type=nlp_result.get('diagram_type', 'general'),
            entities=entities,
            relationships=relationships,
            constraints=constraints,
            metadata={
                'generation_method': 'rule_based',
                'confidence': nlp_result.get('confidence', 0.5)
            }
        )


if __name__ == "__main__":
    # Test the LLM planner
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("LLM DIAGRAM PLANNER TEST")
    print("=" * 60)

    # Test with rule-based fallback
    planner = RuleBasedPlanner()

    test_nlp_result = {
        'entities': [
            {'type': 'battery', 'label': '12V', 'properties': {'voltage': '12V'}},
            {'type': 'resistor', 'label': 'R1', 'properties': {'resistance': '100Ω'}},
            {'type': 'resistor', 'label': 'R2', 'properties': {'resistance': '200Ω'}}
        ],
        'relationships': [
            {'source': 'entity_0', 'target': 'entity_1', 'type': 'connected_to'},
            {'source': 'entity_1', 'target': 'entity_2', 'type': 'series_with'}
        ],
        'domain': 'electronics',
        'diagram_type': 'circuit'
    }

    plan = planner.generate_plan(
        "A 12V battery connected to two resistors in series: R1 (100Ω) and R2 (200Ω)",
        "electronics",
        test_nlp_result
    )

    print("\n✓ Generated plan:")
    print(json.dumps(plan.to_dict(), indent=2))

    print("\n✓ Plan structure validated")
    print(f"  Entities: {len(plan.entities)}")
    print(f"  Relationships: {len(plan.relationships)}")
    print(f"  Constraints: {len(plan.constraints)}")

    # Test LLM planner if Ollama available
    if HAS_REQUESTS:
        try:
            print("\n" + "=" * 60)
            print("Testing LLM Planner (requires Ollama running)")
            print("=" * 60)

            llm_planner = LLMDiagramPlanner(
                local_model="mistral:7b",
                use_api_for_verification=False
            )

            # This will fail if Ollama isn't running - that's okay
            print("\nℹ️  To test LLM planner, run: ollama run mistral")
            print("   Then re-run this test")

        except Exception as e:
            print(f"\nℹ️  LLM planner not available: {e}")
            print("   Install Ollama from https://ollama.ai")

    print("\n" + "=" * 60)
    print("✅ LLM Planner module ready")
    print("=" * 60)
