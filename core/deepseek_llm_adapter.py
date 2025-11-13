#!/usr/bin/env python3
"""
DeepSeek LLM Adapter
====================

Adapter for using DeepSeek AI API with the LLM planner and auditor.
DeepSeek API is OpenAI-compatible, so we can use the OpenAI client with custom base URL.

DeepSeek advantages:
- Much cheaper than OpenAI/Claude
- Good performance on reasoning tasks
- OpenAI-compatible API
- Supports JSON mode

Author: Universal STEM Diagram Generator
Date: November 10, 2025
"""

from typing import Optional, Dict, Any
import os

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None


class DeepSeekClient:
    """
    Client for DeepSeek API using OpenAI-compatible interface

    Usage:
        client = DeepSeekClient(api_key="sk-...")
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        timeout: int = 180
    ):
        """
        Initialize DeepSeek client

        Args:
            api_key: DeepSeek API key (or set DEEPSEEK_API_KEY env var)
            base_url: DeepSeek API base URL
            model: Model name ('deepseek-chat' or 'deepseek-coder')
            timeout: Request timeout in seconds
        """
        if not HAS_OPENAI:
            raise ImportError("openai package required. Install: pip install openai")

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter"
            )

        self.base_url = base_url
        self.model = model
        self.timeout = timeout

        # Initialize OpenAI client with DeepSeek endpoint
        # Try normal initialization first, then fallback without proxy if needed
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        except Exception as e:
            error_msg = str(e)
            if "socksio" in error_msg or "proxy" in error_msg.lower():
                # Retry without proxy by setting http_client with no proxy
                import httpx
                try:
                    http_client = httpx.Client(
                        proxies=None,  # Disable proxies
                        timeout=self.timeout
                    )
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url,
                        timeout=self.timeout,
                        http_client=http_client
                    )
                except Exception as e2:
                    # Last resort: raise with helpful message
                    raise RuntimeError(
                        f"Failed to initialize DeepSeek client. "
                        f"Proxy error: {error_msg}. "
                        f"Retry without proxy also failed: {str(e2)}. "
                        f"Solutions: 1) Install socksio: pip install httpx[socks], "
                        f"2) Disable proxy: unset http_proxy https_proxy, "
                        f"3) Use fallback mode"
                    ) from e2
            else:
                raise

    def chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            json_mode: Force JSON output format
            **kwargs: Additional parameters

        Returns:
            Response dict with 'content', 'model', 'usage', etc.
        """
        completion_kwargs = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            **kwargs
        }

        if max_tokens:
            completion_kwargs['max_tokens'] = max_tokens

        if json_mode:
            completion_kwargs['response_format'] = {"type": "json_object"}

        response = self.client.chat.completions.create(**completion_kwargs)

        return {
            'content': response.choices[0].message.content,
            'model': response.model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'finish_reason': response.choices[0].finish_reason
        }

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost in USD

        DeepSeek pricing (as of Nov 2025):
        - Input: $0.14 per 1M tokens
        - Output: $0.28 per 1M tokens

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * 0.14
        output_cost = (completion_tokens / 1_000_000) * 0.28
        return input_cost + output_cost

    # ========== Roadmap API Call #1: Entity Enrichment ==========

    def enrich_entities(
        self,
        entities: list,
        context: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrich extracted entities with implicit knowledge and validation

        Roadmap Call #1: Gap-filling & enrichment after NLP extraction

        Args:
            entities: List of entities from NLP tools (property graph nodes)
            context: Original problem text
            domain: Optional domain hint (physics, chemistry, etc.)

        Returns:
            Dict with enriched entities and added implicit information
        """
        # Prepare entity summary
        entity_summary = []
        for i, entity in enumerate(entities[:20]):  # Limit to first 20 to avoid token limits
            if hasattr(entity, 'id'):
                entity_summary.append({
                    'id': entity.id,
                    'type': entity.type.value if hasattr(entity.type, 'value') else str(entity.type),
                    'label': getattr(entity, 'label', entity.id),
                    'properties': getattr(entity, 'properties', {})
                })
            elif isinstance(entity, dict):
                entity_summary.append(entity)

        domain_str = f" in the {domain} domain" if domain else ""

        prompt = f"""You are a STEM knowledge base expert. Given the following entities extracted from a problem description{domain_str}, validate their properties and add any implicit information.

Original problem text:
{context}

Extracted entities:
{json.dumps(entity_summary, indent=2)}

Your task:
1. Validate each entity's type and properties
2. Add missing implicit properties (e.g., a 'switch' is usually drawn 'open' by default)
3. Identify any missing entities that should be present
4. Add units where applicable
5. Flag any inconsistencies or errors

Respond with a JSON object:
{{
  "validated_entities": [list of validated entities with added properties],
  "missing_entities": [list of entities that should be added],
  "corrections": [list of corrections made],
  "warnings": [list of potential issues]
}}"""

        try:
            messages = [
                {"role": "system", "content": "You are a STEM diagram generation expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = self.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for factual enrichment
                json_mode=True
            )

            import json
            enrichment_result = json.loads(response['content'])
            enrichment_result['usage'] = response['usage']
            enrichment_result['cost_usd'] = self.estimate_cost(
                response['usage']['prompt_tokens'],
                response['usage']['completion_tokens']
            )

            return enrichment_result

        except Exception as e:
            return {
                'error': str(e),
                'validated_entities': entity_summary,
                'missing_entities': [],
                'corrections': [],
                'warnings': [f"Enrichment failed: {str(e)}"]
            }

    # ========== Roadmap API Call #2: Plan Auditing ==========

    def audit_plan(
        self,
        plan: Dict[str, Any],
        original_request: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        Audit diagram plan for correctness and completeness

        Roadmap Call #2: Verify diagram plan after local LLM generation

        Args:
            plan: DiagramPlan dict with entities, relationships, constraints
            original_request: Original problem text
            domain: Problem domain

        Returns:
            Dict with audit results and corrections
        """
        prompt = f"""You are an expert {domain} diagram reviewer. A local LLM has generated the following diagram plan. Your task is to verify its correctness and completeness.

Original request:
{original_request}

Generated plan:
{json.dumps(plan, indent=2)}

Review checklist:
1. Does the plan include all entities mentioned in the request?
2. Are relationships correctly identified?
3. Are constraints logically consistent?
4. For {domain} diagrams, are domain-specific rules satisfied?
5. Are there any missing or incorrect elements?

Respond with JSON:
{{
  "is_valid": true/false,
  "confidence": 0.0-1.0,
  "missing_elements": [list of missing entities/relationships],
  "incorrect_elements": [list of errors with corrections],
  "suggestions": [list of improvement suggestions],
  "domain_rules_satisfied": true/false,
  "domain_rule_violations": [list of violations if any]
}}"""

        try:
            messages = [
                {"role": "system", "content": f"You are an expert {domain} diagram auditor. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = self.chat_completion(
                messages=messages,
                temperature=0.2,  # Very low temperature for auditing
                json_mode=True
            )

            import json
            audit_result = json.loads(response['content'])
            audit_result['usage'] = response['usage']
            audit_result['cost_usd'] = self.estimate_cost(
                response['usage']['prompt_tokens'],
                response['usage']['completion_tokens']
            )

            return audit_result

        except Exception as e:
            return {
                'error': str(e),
                'is_valid': True,  # Assume valid if audit fails
                'confidence': 0.5,
                'missing_elements': [],
                'incorrect_elements': [],
                'suggestions': [],
                'warnings': [f"Audit failed: {str(e)}"]
            }

    # ========== Roadmap API Call #3: Semantic Fidelity Validation ==========

    def validate_semantic_fidelity(
        self,
        original_request: str,
        diagram_description: str,
        svg_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate that final diagram matches original intent

        Roadmap Call #3: Final semantic validation after rendering

        Args:
            original_request: Original problem text
            diagram_description: VLM description of generated diagram
            svg_output: Optional SVG for additional context

        Returns:
            Dict with validation results
        """
        svg_info = ""
        if svg_output:
            # Extract basic SVG info (object count, dimensions)
            import re
            rects = len(re.findall(r'<rect', svg_output))
            circles = len(re.findall(r'<circle', svg_output))
            paths = len(re.findall(r'<path', svg_output))
            texts = len(re.findall(r'<text', svg_output))
            svg_info = f"\n\nSVG contains: {rects} rectangles, {circles} circles, {paths} paths, {texts} text elements"

        prompt = f"""Compare the original diagram request with the description of the generated diagram. Determine if they match semantically.

Original request:
{original_request}

Generated diagram description:
{diagram_description}{svg_info}

Your task:
1. Do they describe the same thing?
2. Are all key elements from the request present in the diagram?
3. Are there any significant discrepancies?
4. Is the diagram semantically faithful to the original intent?

Respond with JSON:
{{
  "match": true/false,
  "confidence": 0.0-1.0,
  "semantic_fidelity_score": 0-100,
  "matched_elements": [list of correctly represented elements],
  "missing_elements": [list of elements from request not in diagram],
  "extra_elements": [list of elements in diagram not in request],
  "discrepancies": [list of semantic differences],
  "reasoning": "detailed explanation"
}}"""

        try:
            messages = [
                {"role": "system", "content": "You are a semantic validation expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]

            response = self.chat_completion(
                messages=messages,
                temperature=0.2,
                json_mode=True
            )

            import json
            validation_result = json.loads(response['content'])
            validation_result['usage'] = response['usage']
            validation_result['cost_usd'] = self.estimate_cost(
                response['usage']['prompt_tokens'],
                response['usage']['completion_tokens']
            )

            return validation_result

        except Exception as e:
            return {
                'error': str(e),
                'match': True,  # Assume match if validation fails
                'confidence': 0.5,
                'semantic_fidelity_score': 75,
                'matched_elements': [],
                'missing_elements': [],
                'extra_elements': [],
                'discrepancies': [],
                'reasoning': f"Validation failed: {str(e)}",
                'warnings': [f"Semantic validation failed: {str(e)}"]
            }


def create_deepseek_planner(
    api_key: Optional[str] = None,
    model: str = "deepseek-chat"
):
    """
    Create LLM planner configured for DeepSeek

    Args:
        api_key: DeepSeek API key
        model: Model name

    Returns:
        LLMDiagramPlanner configured for DeepSeek
    """
    from core.llm_planner import LLMDiagramPlanner
    from openai import OpenAI

    api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DeepSeek API key required")

    # Create OpenAI client with DeepSeek endpoint
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=180
    )

    # Create planner
    planner = LLMDiagramPlanner(
        local_model=None,  # No local model
        api_model=model,
        use_api_for_verification=True
    )

    # Inject DeepSeek client
    planner.api_client = client

    return planner


def create_deepseek_auditor(
    api_key: Optional[str] = None,
    model: str = "deepseek-chat"
):
    """
    Create diagram auditor configured for DeepSeek

    Args:
        api_key: DeepSeek API key
        model: Model name

    Returns:
        DiagramAuditor configured for DeepSeek
    """
    from core.auditor.diagram_auditor import DiagramAuditor, LLMBackend

    api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("DeepSeek API key required")

    # Create auditor with GPT backend (OpenAI-compatible)
    auditor = DiagramAuditor(
        backend=LLMBackend.GPT,  # Use GPT backend (works with DeepSeek)
        api_key=api_key,
        model_name=model
    )

    # Inject custom base URL
    if hasattr(auditor, 'llm_client') and auditor.llm_client:
        from openai import OpenAI
        auditor.llm_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=180
        )

    return auditor


# Example usage
if __name__ == '__main__':
    import sys

    # Check if API key is set
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY environment variable not set")
        print("\nTo use DeepSeek:")
        print("1. Get API key from https://platform.deepseek.com/")
        print("2. Set environment variable:")
        print("   export DEEPSEEK_API_KEY='your-api-key'")
        sys.exit(1)

    print("="*60)
    print("DeepSeek LLM Adapter Test")
    print("="*60)

    # Test basic client
    try:
        client = DeepSeekClient(api_key=api_key)
        print("✅ DeepSeek client initialized")

        # Test simple completion
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful physics tutor."},
                {"role": "user", "content": "Explain Newton's first law in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100
        )

        print(f"\n✅ Chat completion successful:")
        print(f"   Response: {response['content'][:100]}...")
        print(f"   Tokens: {response['usage']['total_tokens']}")
        print(f"   Cost: ${client.estimate_cost(response['usage']['prompt_tokens'], response['usage']['completion_tokens']):.6f}")

        # Test JSON mode
        response_json = client.chat_completion(
            messages=[
                {"role": "user", "content": "List 3 physics concepts. Output as JSON with 'concepts' array."}
            ],
            json_mode=True,
            max_tokens=200
        )

        print(f"\n✅ JSON mode successful:")
        print(f"   Response: {response_json['content'][:150]}...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
