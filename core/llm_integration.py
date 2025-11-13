"""
LLM Integration Framework
==========================

Priority 1 CRITICAL feature from roadmap.

Provides orchestration for:
1. Local LLM (Mistral, Llama) for diagram planning
2. API LLM (GPT-4, Claude) for verification (optional)
3. Hybrid draft-verify strategy
4. Structured output parsing

Dependencies (to install):
- pip install ollama transformers spacy-llm
- ollama pull mistral:7b (for local LLM)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"  # Local LLM via Ollama
    OPENAI = "openai"  # OpenAI API
    ANTHROPIC = "anthropic"  # Claude API
    HUGGINGFACE = "huggingface"  # HuggingFace models


@dataclass
class LLMConfig:
    """Configuration for LLM"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # For Ollama or custom endpoints


@dataclass
class DiagramPlanLLM:
    """LLM-generated diagram plan"""
    domain: str
    diagram_type: str
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    layout_hints: Dict[str, Any]
    confidence: float
    reasoning: str


class LLMDiagramPlanner:
    """
    LLM-based diagram planning system

    Uses LLM to generate structured diagram plans from natural language.
    Supports local and API-based LLMs with fallback strategies.
    """

    def __init__(
        self,
        primary_config: Optional[LLMConfig] = None,
        verifier_config: Optional[LLMConfig] = None
    ):
        """
        Initialize LLM planner

        Args:
            primary_config: Primary LLM for plan generation (default: local Mistral)
            verifier_config: Optional verifier LLM for quality checking (default: None)
        """
        self.primary_config = primary_config or self._get_default_config()
        self.verifier_config = verifier_config

        self.primary_llm = self._initialize_llm(self.primary_config)
        self.verifier_llm = self._initialize_llm(self.verifier_config) if verifier_config else None

        print(f"✅ LLM Planner initialized")
        print(f"   Primary: {self.primary_config.provider.value}/{self.primary_config.model_name}")
        if self.verifier_llm:
            print(f"   Verifier: {self.verifier_config.provider.value}/{self.verifier_config.model_name}")

    def _get_default_config(self) -> LLMConfig:
        """Get default configuration (local Ollama with Mistral)"""
        return LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="mistral:7b",
            temperature=0.3,  # Lower temp for more deterministic output
            max_tokens=2000,
            base_url="http://localhost:11434"
        )

    def _initialize_llm(self, config: LLMConfig):
        """Initialize LLM based on provider"""
        if config.provider == LLMProvider.OLLAMA:
            return self._init_ollama(config)
        elif config.provider == LLMProvider.OPENAI:
            return self._init_openai(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            return self._init_anthropic(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

    def _init_ollama(self, config: LLMConfig):
        """Initialize Ollama client"""
        try:
            import ollama
            # Test connection
            models = ollama.list()
            if not any(config.model_name in m['name'] for m in models.get('models', [])):
                print(f"⚠️  Model {config.model_name} not found. Run: ollama pull {config.model_name}")
            return ollama
        except ImportError:
            print("❌ Ollama not installed. Run: pip install ollama")
            print("❌ Also install Ollama: https://ollama.ai")
            return None
        except Exception as e:
            print(f"⚠️  Ollama connection failed: {e}")
            return None

    def _init_openai(self, config: LLMConfig):
        """Initialize OpenAI client"""
        try:
            import openai
            openai.api_key = config.api_key
            return openai
        except ImportError:
            print("❌ OpenAI not installed. Run: pip install openai")
            return None

    def _init_anthropic(self, config: LLMConfig):
        """Initialize Anthropic client"""
        try:
            import anthropic
            return anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            print("❌ Anthropic not installed. Run: pip install anthropic")
            return None

    def generate_plan(
        self,
        problem_text: str,
        nlp_results: Optional[Dict] = None,
        use_verifier: bool = False
    ) -> DiagramPlanLLM:
        """
        Generate diagram plan from problem text

        Args:
            problem_text: Natural language problem description
            nlp_results: Optional NLP extraction results to guide LLM
            use_verifier: Whether to use verifier LLM for quality check

        Returns:
            DiagramPlanLLM with structured plan
        """
        # Build prompt
        prompt = self._build_planning_prompt(problem_text, nlp_results)

        # Generate plan with primary LLM
        draft_plan = self._call_llm(self.primary_llm, self.primary_config, prompt)

        if not draft_plan:
            raise ValueError("LLM failed to generate plan")

        # Parse JSON response
        plan = self._parse_llm_response(draft_plan)

        # Verify with secondary LLM if available
        if use_verifier and self.verifier_llm:
            plan = self._verify_plan(plan, problem_text)

        return plan

    def _build_planning_prompt(self, problem_text: str, nlp_results: Optional[Dict]) -> str:
        """Build prompt for LLM diagram planning"""

        # Include NLP context if available
        nlp_context = ""
        if nlp_results:
            entities = nlp_results.get('entities', [])
            domain = nlp_results.get('domain', 'unknown')
            nlp_context = f"""
NLP Analysis:
- Domain: {domain}
- Entities found: {len(entities)}
- Key quantities: {', '.join([e['text'] for e in entities[:5] if e.get('type') == 'MEASUREMENT'])}
"""

        prompt = f"""You are a STEM diagram planning expert. Analyze this problem and create a structured diagram plan.

Problem:
{problem_text}

{nlp_context}

Generate a JSON diagram plan with:
1. domain: "electronics" | "physics" | "chemistry" | "mathematics"
2. diagram_type: specific type (e.g., "circuit_diagram", "free_body_diagram")
3. entities: list of objects to draw with properties
4. relationships: connections between entities
5. layout_hints: positioning and layout suggestions
6. confidence: your confidence score 0.0-1.0
7. reasoning: brief explanation of your plan

Output ONLY valid JSON, no other text.

Example output format:
{{
  "domain": "electronics",
  "diagram_type": "capacitor_circuit",
  "entities": [
    {{"id": "C1", "type": "capacitor", "value": 2.0, "unit": "μF", "position_hint": "left"}},
    {{"id": "C2", "type": "capacitor", "value": 8.0, "unit": "μF", "position_hint": "right"}},
    {{"id": "V1", "type": "battery", "value": 300, "unit": "V", "position_hint": "far_left"}}
  ],
  "relationships": [
    {{"type": "series", "entities": ["C1", "C2"]}},
    {{"type": "connected_to", "source": "V1", "target": "C1"}}
  ],
  "layout_hints": {{
    "orientation": "horizontal",
    "spacing": "medium"
  }},
  "confidence": 0.9,
  "reasoning": "Two capacitors in series with battery - standard series circuit layout"
}}

Now generate the plan:"""

        return prompt

    def _call_llm(self, llm_client, config: LLMConfig, prompt: str) -> Optional[str]:
        """Call LLM with prompt"""
        if llm_client is None:
            print("⚠️  LLM client not available, returning None")
            return None

        try:
            if config.provider == LLMProvider.OLLAMA:
                response = llm_client.generate(
                    model=config.model_name,
                    prompt=prompt,
                    options={
                        'temperature': config.temperature,
                        'num_predict': config.max_tokens
                    }
                )
                return response['response']

            elif config.provider == LLMProvider.OPENAI:
                response = llm_client.chat.completions.create(
                    model=config.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens
                )
                return response.choices[0].message.content

            elif config.provider == LLMProvider.ANTHROPIC:
                message = llm_client.messages.create(
                    model=config.model_name,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text

        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            return None

    def _parse_llm_response(self, response: str) -> DiagramPlanLLM:
        """Parse LLM JSON response into DiagramPlanLLM"""
        try:
            # Extract JSON from response (may have extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]

            data = json.loads(json_str)

            return DiagramPlanLLM(
                domain=data.get('domain', 'unknown'),
                diagram_type=data.get('diagram_type', 'generic'),
                entities=data.get('entities', []),
                relationships=data.get('relationships', []),
                layout_hints=data.get('layout_hints', {}),
                confidence=data.get('confidence', 0.5),
                reasoning=data.get('reasoning', '')
            )

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse LLM JSON: {e}")
            print(f"Response: {response[:200]}...")
            # Return minimal plan
            return DiagramPlanLLM(
                domain="unknown",
                diagram_type="generic",
                entities=[],
                relationships=[],
                layout_hints={},
                confidence=0.0,
                reasoning="Failed to parse LLM response"
            )

    def _verify_plan(self, plan: DiagramPlanLLM, original_text: str) -> DiagramPlanLLM:
        """Verify plan using secondary LLM (TODO: implement)"""
        # TODO: Use verifier LLM to check plan quality
        # For now, just return original plan
        return plan


# Stub for testing without actual LLM
class StubLLMPlanner:
    """Stub LLM planner for testing without actual LLM"""

    def generate_plan(self, problem_text: str, nlp_results: Optional[Dict] = None, use_verifier: bool = False) -> DiagramPlanLLM:
        """Generate stub plan"""
        return DiagramPlanLLM(
            domain="electronics",
            diagram_type="circuit_diagram",
            entities=[
                {"id": "C1", "type": "capacitor", "value": 2.0, "unit": "μF"},
                {"id": "V1", "type": "battery", "value": 300, "unit": "V"}
            ],
            relationships=[
                {"type": "connected_to", "source": "V1", "target": "C1"}
            ],
            layout_hints={"orientation": "horizontal"},
            confidence=0.8,
            reasoning="Stub plan for testing"
        )


if __name__ == "__main__":
    # Test LLM integration
    print("=" * 80)
    print("LLM INTEGRATION TEST")
    print("=" * 80)

    # Try to initialize with Ollama
    try:
        planner = LLMDiagramPlanner()
        print("✅ LLM planner initialized successfully")

        # Test plan generation
        test_problem = "A 5 kg block rests on a 30-degree incline. Draw a free-body diagram."
        print(f"\n📝 Test problem: {test_problem}")

        plan = planner.generate_plan(test_problem)
        print(f"\n📋 Generated plan:")
        print(f"   Domain: {plan.domain}")
        print(f"   Type: {plan.diagram_type}")
        print(f"   Entities: {len(plan.entities)}")
        print(f"   Confidence: {plan.confidence:.2f}")
        print(f"   Reasoning: {plan.reasoning}")

    except Exception as e:
        print(f"⚠️  LLM test failed: {e}")
        print("   Using stub planner instead")
        planner = StubLLMPlanner()
        plan = planner.generate_plan("test")
        print(f"   Stub plan domain: {plan.domain}")
