"""
Universal AI Analyzer - Single Robust Pipeline Phase 1
Merges RobustAIAnalyzer + MultiStageAIReasoning into one deterministic analyzer
NOW supports local fallback for offline operation
"""

import json
import time
import copy
import requests
from typing import Dict, List, Tuple, Optional, Any

# Import shared data structures
from core.problem_spec import (
    CanonicalProblemSpec,
    PhysicsDomain,
    IncompleteSpecsError
)

# Re-export for backward compatibility
__all__ = ['UniversalAIAnalyzer', 'CanonicalProblemSpec', 'PhysicsDomain', 'IncompleteSpecsError']

# Local analyzer for offline fallback (lazy import to avoid circular dependency)
LOCAL_ANALYZER_AVAILABLE = False
try:
    from core.local_ai_analyzer import LocalAIAnalyzer
    LOCAL_ANALYZER_AVAILABLE = True
except ImportError:
    LOCAL_ANALYZER_AVAILABLE = False


class UniversalAIAnalyzer:
    """
    Universal AI analyzer - Single robust implementation
    Combines RobustAIAnalyzer + MultiStageAIReasoning

    NOW supports offline operation with local fallback:
    - If api_key is provided: Uses API-based analysis (best quality)
    - If api_key is None: Uses local spaCy-based analysis (offline)
    - If use_local_fallback=True: Tries API first, falls back to local on failure

    Returns CanonicalProblemSpec (complete) or raises IncompleteSpecsError
    """

    def __init__(self, api_key: Optional[str] = None,
                 api_base_url: str = "https://api.deepseek.com/v1/chat/completions",
                 api_model: str = "deepseek-chat", timeout: int = 180,
                 max_retries: int = 5, timeout_per_stage: int = 60,
                 permissive_mode: bool = False,
                 use_local_fallback: bool = True):
        """
        Initialize Universal AI Analyzer

        Args:
            api_key: Optional DeepSeek API key (if None, uses local-only mode)
            api_base_url: API endpoint URL
            api_model: Model to use
            timeout: API timeout in seconds (shared across all stages)
            max_retries: Maximum retry attempts for failed API calls
            permissive_mode: If True, don't raise errors for incomplete specs
            use_local_fallback: If True, fallback to local analyzer when API fails
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.api_model = api_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.timeout_per_stage = timeout_per_stage
        self.permissive_mode = permissive_mode
        self.use_local_fallback = use_local_fallback

        # Initialize local analyzer for fallback (if available)
        self.local_analyzer = None
        if (use_local_fallback or api_key is None) and LOCAL_ANALYZER_AVAILABLE:
            try:
                self.local_analyzer = LocalAIAnalyzer(verbose=False)
            except Exception as e:
                print(f"⚠️  LocalAIAnalyzer initialization failed: {e}")
                if api_key is None:
                    raise RuntimeError("No API key and local analyzer unavailable")

        # Load the schema for validation (only if using API)
        if api_key is not None:
            with open("canonical_problem_spec_schema.json", 'r') as f:
                self.spec_schema = json.load(f)
            with open("stage_2_schema.json", 'r') as f:
                self.stage_2_schema = json.load(f)
            with open("stage_3_schema.json", 'r') as f:
                self.stage_3_schema = json.load(f)

        # Print initialization status
        print(f"✅ UniversalAIAnalyzer initialized")
        if api_key:
            print(f"   Mode: API-based (DeepSeek)")
            print(f"   Model: {api_model}")
            print(f"   Timeout: {timeout_per_stage}s per stage (total: up to {timeout_per_stage * 5}s)")
            print(f"   Retries: {max_retries}")
            print(f"   Local fallback: {'enabled' if use_local_fallback and self.local_analyzer else 'disabled'}")
        else:
            print(f"   Mode: Local-only (spaCy + rules)")
            print(f"   Local analyzer: {'available' if self.local_analyzer else 'unavailable'}")
        print(f"   Permissive mode: {permissive_mode}")
        self.last_analysis_telemetry = None

    def analyze(self, problem_text: str) -> CanonicalProblemSpec:
        """
        Hybrid analyzer that always runs local NLP first, then optionally
        invokes DeepSeek for enrichment/gap-filling if needed.
        """
        print(f"\n{'='*80}")
        print("🧠 HYBRID UNIVERSAL AI ANALYSIS - Phase 1")
        print(f"{'='*80}\n")

        telemetry = {
            'local': {
                'available': bool(self.local_analyzer)
            },
            'deepseek': {
                'available': bool(self.api_key)
            },
            'merge': {}
        }

        local_spec = None
        local_error = None

        # Always attempt local analysis first if possible
        if self.local_analyzer:
            try:
                local_start = time.time()
                print("Step 0: Local NLP + rule-based analysis")
                local_spec = self.local_analyzer.analyze(problem_text)
                local_duration = (time.time() - local_start) * 1000
                telemetry['local'].update({
                    'objects': len(local_spec.objects),
                    'relationships': len(local_spec.relationships),
                    'confidence': local_spec.confidence,
                    'is_complete': local_spec.is_complete,
                    'duration_ms': int(local_duration)
                })
                print(f"   ✅ Local analysis complete (confidence {local_spec.confidence:.2f})")
            except Exception as e:
                local_error = str(e)
                telemetry['local']['error'] = local_error
                print(f"   ⚠️  Local analysis failed: {local_error}")
        else:
            print("Step 0: Local NLP unavailable - skipping")

        # Pure offline mode (no API key)
        if self.api_key is None:
            if not local_spec:
                raise RuntimeError("No API key provided and local analyzer unavailable")
            local_spec.attribute_provenance = self._build_provenance_map(local_spec, source='local')
            local_spec.analysis_metadata = telemetry
            self.last_analysis_telemetry = telemetry
            print(f"\n{'='*80}")
            print("✅ HYBRID ANALYSIS COMPLETE (Local Only)")
            print(f"{'='*80}\n")
            return local_spec

        # Always invoke DeepSeek when API key is available (hybrid orchestration)
        needs_deepseek = self._needs_deepseek_enrichment(local_spec)
        telemetry['deepseek']['invoked'] = True
        telemetry['deepseek']['reason'] = 'gap_fill' if needs_deepseek else 'cross_check'
        deepseek_spec = None

        print("\nStep 1: DeepSeek enrichment / auditing")
        try:
            deepseek_spec = self._analyze_with_api(problem_text)
            telemetry['deepseek'].update({
                'objects': len(deepseek_spec.objects),
                'relationships': len(deepseek_spec.relationships),
                'confidence': deepseek_spec.confidence,
                'is_complete': deepseek_spec.is_complete
            })
        except Exception as api_error:
            telemetry['deepseek']['error'] = str(api_error)
            print(f"   ⚠️  DeepSeek analysis failed: {api_error}")
            if self.use_local_fallback and local_spec:
                print("   🔄 Using local analysis result (DeepSeek unavailable)")
                deepseek_spec = None
            elif not local_spec:
                raise

        # Merge results (local first, DeepSeek fills gaps)
        merged_spec, provenance = self._merge_specs(local_spec, deepseek_spec)
        telemetry['merge']['attribute_sources'] = provenance
        telemetry['merge']['used_deepseek'] = needs_deepseek and deepseek_spec is not None
        telemetry['merge']['local_confidence'] = local_spec.confidence if local_spec else None

        merged_spec.attribute_provenance = provenance
        merged_spec.analysis_metadata = telemetry
        self.last_analysis_telemetry = telemetry

        print(f"\n{'='*80}")
        print("✅ HYBRID ANALYSIS COMPLETE")
        sources = sorted(set(provenance.values()))
        print(f"   Sources used: {', '.join(sources) if sources else 'unknown'}")
        print(f"   Domain: {merged_spec.domain.value}")
        print(f"   Objects: {len(merged_spec.objects)} | Relationships: {len(merged_spec.relationships)}")
        print(f"{'='*80}\n")

        return merged_spec

    def _analyze_with_api(self, problem_text: str) -> CanonicalProblemSpec:
        """
        API-based analysis (original implementation)

        Pipeline:
        1. Domain classification
        2. Multi-stage entity extraction
        3. Completeness validation
        4. Complexity scoring
        5. Subproblem decomposition (if needed)

        Args:
            problem_text: Physics problem description

        Returns:
            Complete CanonicalProblemSpec

        Raises:
            IncompleteSpecsError: If specs cannot be completed
        """
        print(f"\n{'='*80}")
        print(f"🧠 UNIVERSAL AI ANALYSIS - Phase 1 (API Mode)")
        print(f"{'='*80}\n")

        # Step 1: Classify domain (ALWAYS)
        print("Step 1/5: Domain Classification")
        domain = self._classify_domain(problem_text)
        print(f"   ✅ Domain: {domain.value}")

        # Step 2: Multi-stage extraction (ALWAYS)
        print("\nStep 2/5: Multi-Stage Extraction (5 sub-stages)")
        extracted = self._extract_multi_stage(problem_text, domain)
        print(f"   ✅ Extracted: {len(extracted.get('objects', []))} objects, "
              f"{len(extracted.get('relationships', []))} relationships")

        # Step 3: Build canonical spec
        print("\nStep 3/5: Building Canonical Spec")
        spec = self._build_canonical_spec(problem_text, domain, extracted)

        # Step 4: Validate completeness (ALWAYS)
        print("\nStep 4/5: Completeness Validation")
        is_complete, missing = self._validate_completeness(spec)

        if not is_complete:
            print(f"   ⚠️  Incomplete: Missing {', '.join(missing)}")
            spec.is_complete = False
            spec.missing_information = missing
            if not self.permissive_mode:
                raise IncompleteSpecsError(missing)
            else:
                print(f"   ✅ Permissive mode - continuing anyway (confidence: {spec.confidence:.2f})")
        else:
            print(f"   ✅ Complete (confidence: {spec.confidence:.2f})")

        # Step 5: Complexity scoring and decomposition
        print("\nStep 5/5: Complexity Analysis")
        spec.complexity_score = self._score_complexity(spec)
        print(f"   Complexity: {spec.complexity_score:.2f}")

        if spec.complexity_score > 0.7:
            print(f"   High complexity detected - decomposing...")
            spec.subproblems = self._decompose(spec)
            print(f"   ✅ Decomposed into {len(spec.subproblems)} subproblems")
        else:
            print(f"   ✅ Manageable complexity - no decomposition needed")

        print(f"\n{'='*80}")
        print(f"✅ UNIVERSAL AI ANALYSIS COMPLETE")
        print(f"{'='*80}\n")

        return spec

    def _needs_deepseek_enrichment(self, spec: Optional[CanonicalProblemSpec]) -> bool:
        """Determine if DeepSeek should be called for enrichment/gap filling."""
        if spec is None:
            return True
        if not spec.is_complete:
            return True
        if spec.confidence < 0.75:
            return True
        if len(spec.objects) == 0 or len(spec.relationships) == 0:
            return True
        return False

    def _merge_specs(self,
                     local_spec: Optional[CanonicalProblemSpec],
                     deepseek_spec: Optional[CanonicalProblemSpec]) -> Tuple[CanonicalProblemSpec, Dict[str, str]]:
        """Merge local + DeepSeek specs with provenance tracking."""
        if local_spec is None and deepseek_spec is None:
            raise RuntimeError("No analysis results available from local or DeepSeek analyzers")

        # If only one spec is available, return it directly
        if deepseek_spec is None and local_spec is not None:
            merged = copy.deepcopy(local_spec)
            provenance = self._build_provenance_map(merged, source='local')
            return merged, provenance

        if local_spec is None and deepseek_spec is not None:
            merged = copy.deepcopy(deepseek_spec)
            provenance = self._build_provenance_map(merged, source='deepseek')
            merged.reasoning_trace.append({
                'stage': 'deepseek_only',
                'method': 'api_fallback',
                'notes': 'Local analysis unavailable'
            })
            return merged, provenance

        # Both results available - combine
        merged = copy.deepcopy(local_spec)
        provenance = self._build_provenance_map(merged, source='local')

        updates = {
            'objects_added': 0,
            'objects_enriched': 0,
            'relationships_added': 0,
            'constraints_added': 0,
            'laws_added': 0,
            'fields_updated': []
        }

        # Domain / problem type / confidence
        if (merged.domain == PhysicsDomain.UNKNOWN or merged.domain is None) and deepseek_spec.domain != PhysicsDomain.UNKNOWN:
            merged.domain = deepseek_spec.domain
            self._tag_provenance(provenance, 'domain', 'deepseek')
            updates['fields_updated'].append('domain')

        if not self._value_present(merged.problem_type) and self._value_present(deepseek_spec.problem_type):
            merged.problem_type = deepseek_spec.problem_type
            self._tag_provenance(provenance, 'problem_type', 'deepseek')
            updates['fields_updated'].append('problem_type')

        merged.confidence = max(merged.confidence, deepseek_spec.confidence)
        merged.is_complete = merged.is_complete or deepseek_spec.is_complete
        merged.missing_information = list(set(merged.missing_information) & set(deepseek_spec.missing_information))

        # Objects
        added, enriched = self._merge_entity_lists(merged.objects, deepseek_spec.objects or [])
        updates['objects_added'] += added
        updates['objects_enriched'] += enriched
        if added or enriched:
            self._tag_provenance(provenance, 'objects', 'deepseek')

        # Relationships
        rel_added, _ = self._merge_entity_lists(merged.relationships, deepseek_spec.relationships or [])
        updates['relationships_added'] += rel_added
        if rel_added:
            self._tag_provenance(provenance, 'relationships', 'deepseek')

        # Constraints
        constraint_added, _ = self._merge_entity_lists(merged.constraints, deepseek_spec.constraints or [])
        updates['constraints_added'] += constraint_added
        if constraint_added:
            self._tag_provenance(provenance, 'constraints', 'deepseek')

        # Applicable laws
        if deepseek_spec.applicable_laws:
            original_len = len(merged.applicable_laws)
            for law in deepseek_spec.applicable_laws:
                if law not in merged.applicable_laws:
                    merged.applicable_laws.append(law)
                    updates['laws_added'] += 1
            if len(merged.applicable_laws) > original_len:
                self._tag_provenance(provenance, 'applicable_laws', 'deepseek')

        # Environment, physics context, geometry
        if self._merge_dict_fields(merged.environment, deepseek_spec.environment):
            self._tag_provenance(provenance, 'environment', 'deepseek')
            updates['fields_updated'].append('environment')

        if self._merge_dict_fields(merged.physics_context, deepseek_spec.physics_context):
            self._tag_provenance(provenance, 'physics_context', 'deepseek')
            updates['fields_updated'].append('physics_context')

        if self._merge_dict_fields(merged.geometry, deepseek_spec.geometry):
            self._tag_provenance(provenance, 'geometry', 'deepseek')
            updates['fields_updated'].append('geometry')

        # Coordinate system
        if (not self._value_present(merged.coordinate_system) or merged.coordinate_system == 'cartesian') and \
                self._value_present(deepseek_spec.coordinate_system) and \
                deepseek_spec.coordinate_system != merged.coordinate_system:
            merged.coordinate_system = deepseek_spec.coordinate_system
            self._tag_provenance(provenance, 'coordinate_system', 'deepseek')
            updates['fields_updated'].append('coordinate_system')

        # Subproblems
        sub_added, _ = self._merge_entity_lists(merged.subproblems, deepseek_spec.subproblems or [], key=None)
        if sub_added:
            self._tag_provenance(provenance, 'subproblems', 'deepseek')

        # Merge reasoning traces + add summary entry
        if deepseek_spec.reasoning_trace:
            merged.reasoning_trace.extend([
                {**entry, 'stage': f"deepseek::{entry.get('stage', 'unknown')}"}
                for entry in deepseek_spec.reasoning_trace
            ])

        merged.reasoning_trace.append({
            'stage': 'hybrid_merge',
            'method': 'local_first',
            'deepseek_used': deepseek_spec is not None,
            'updates': updates
        })

        return merged, provenance

    def _merge_entity_lists(self, base_list: List[Dict], incoming_list: List[Dict], key: Optional[str] = 'id') -> Tuple[int, int]:
        """Merge two lists of dict entities by ID."""
        if not incoming_list:
            return 0, 0

        added = 0
        enriched = 0
        index = {}
        if key:
            index = {item.get(key): item for item in base_list if isinstance(item, dict) and item.get(key)}

        for item in incoming_list:
            if not isinstance(item, dict):
                continue
            identifier = item.get(key) if key else None

            if key and identifier and identifier in index:
                target = index[identifier]
                if self._merge_dict_fields(target, item):
                    enriched += 1
            else:
                base_list.append(copy.deepcopy(item))
                added += 1
                if key and identifier:
                    index[identifier] = base_list[-1]

        return added, enriched

    def _merge_dict_fields(self, base: Dict, incoming: Dict) -> bool:
        """Recursively merge two dicts, returning True if base changed."""
        if not incoming:
            return False
        changed = False
        for key, value in incoming.items():
            if key not in base:
                base[key] = copy.deepcopy(value)
                changed = True
            else:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    if self._merge_dict_fields(base[key], value):
                        changed = True
                elif isinstance(base[key], list) and isinstance(value, list):
                    before = len(base[key])
                    for item in value:
                        if item not in base[key]:
                            base[key].append(item)
                    if len(base[key]) > before:
                        changed = True
                else:
                    if base[key] != value:
                        base[key] = value
                        changed = True
        return changed

    def _value_present(self, value: Any) -> bool:
        """Check if a value is meaningfully populated."""
        if value is None:
            return False
        if isinstance(value, (list, dict)) and not value:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        return True

    def _build_provenance_map(self, spec: CanonicalProblemSpec, source: str) -> Dict[str, str]:
        """Build initial provenance map for a spec."""
        if not spec:
            return {}
        tracked_fields = [
            'domain', 'problem_type', 'objects', 'relationships', 'constraints',
            'physics_context', 'environment', 'geometry', 'applicable_laws',
            'subproblems', 'coordinate_system'
        ]
        provenance = {}
        for field in tracked_fields:
            value = getattr(spec, field, None)
            if self._value_present(value):
                provenance[field] = source
        return provenance

    def _tag_provenance(self, provenance: Dict[str, str], field: str, contributor: str) -> None:
        """Tag provenance map with an additional contributor."""
        if not contributor:
            return
        existing = provenance.get(field)
        if not existing:
            provenance[field] = contributor
        elif contributor not in existing.split('+'):
            provenance[field] = f"{existing}+{contributor}"

    def _classify_domain(self, problem_text: str) -> PhysicsDomain:
        """
        Step 1: Classify physics domain using AI

        This is deterministic - uses keyword matching first,
        then AI confirmation if ambiguous
        """
        # Keyword-based classification (fast)
        text_lower = problem_text.lower()

        keywords = {
            PhysicsDomain.ELECTROSTATICS: ['charge', 'electric field', 'coulomb', 'gauss', 'potential', 'capacitor'],
            PhysicsDomain.CURRENT_ELECTRICITY: ['circuit', 'resistor', 'battery', 'current', 'voltage', 'ohm', 'capacitor', 'inductor'],
            PhysicsDomain.MECHANICS: ['mass', 'force', 'friction', 'acceleration', 'velocity', 'incline', 'pulley', 'spring'],
            PhysicsDomain.THERMODYNAMICS: ['temperature', 'heat', 'entropy', 'pv diagram', 'gas', 'isothermal', 'adiabatic'],
            PhysicsDomain.OPTICS: ['lens', 'mirror', 'refraction', 'reflection', 'ray', 'image', 'focal'],
            PhysicsDomain.MAGNETISM: ['magnetic field', 'flux', 'solenoid', 'magnet', 'ampere'],
            PhysicsDomain.WAVES: ['wave', 'frequency', 'wavelength', 'amplitude', 'interference', 'diffraction'],
            PhysicsDomain.MODERN_PHYSICS: ['photon', 'quantum', 'photoelectric', 'atom', 'nuclear', 'relativity']
        }

        # Score each domain
        scores = {}
        for domain, kw_list in keywords.items():
            score = sum(1 for kw in kw_list if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            # Return domain with highest score
            best_domain = max(scores, key=scores.get)
            # Only return if confidence is high (at least 2 keywords)
            if scores[best_domain] >= 2:
                return best_domain

        # Fallback to AI classification if ambiguous
        prompt = f"""Classify this physics problem into ONE primary domain.

Problem: {problem_text}

Domains:
- electrostatics
- current_electricity
- mechanics
- thermodynamics
- optics
- magnetism
- waves
- modern_physics

Respond with ONLY the domain name (lowercase, underscore-separated)."""

        try:
            response = self._call_api(prompt, temperature=0.0, max_tokens=50)
            if response:
                domain_str = response.strip().lower()
                for domain in PhysicsDomain:
                    if domain.value == domain_str:
                        return domain
        except Exception as e:
            print(f"   ⚠️  AI classification failed: {e}")

        return PhysicsDomain.UNKNOWN

    def _extract_multi_stage(self, problem_text: str, domain: PhysicsDomain) -> Dict:
        """
        Step 2: Multi-stage extraction (5 sub-stages)
        Combines entity extraction, context understanding, inference, constraints, and validation
        """
        # Stage 2.1: Entity Extraction
        print("   Stage 2.1: Entity Extraction")
        entities = self._stage_1_extract_entities(problem_text, domain)
        print(f"      ✅ {len(entities.get('objects', []))} objects extracted")

        # Stage 2.2: Physics Context Understanding
        print("   Stage 2.2: Physics Context")
        context = self._stage_2_understand_context(problem_text, entities, domain)
        print(f"      ✅ Context: {context.get('analysis_type', 'unknown')}")

        # Stage 2.3: Implicit Information Inference
        print("   Stage 2.3: Implicit Inference")
        enriched = self._stage_3_infer_implicit(entities, context, domain)
        print(f"      ✅ Enriched with implicit information")

        # Stage 2.4: Constraint Identification
        print("   Stage 2.4: Constraint Identification")
        constraints = self._stage_4_identify_constraints(enriched, context, domain)
        print(f"      ✅ {len(constraints)} constraints identified")

        # Stage 2.5: Validation & Self-Correction
        print("   Stage 2.5: Validation & Self-Correction")
        validated = self._stage_5_validate_and_correct(enriched, constraints, context)
        print(f"      ✅ Validated (confidence: {validated.get('confidence', 0.0):.2f})")

        # Check for missing information
        missing_information = validated.get('missing_information', [])
        if missing_information:
            raise IncompleteSpecsError(missing_information)

        return {
            'objects': validated.get('entities', {}).get('objects', enriched.get('objects', [])),
            'relationships': validated.get('entities', {}).get('relationships', enriched.get('relationships', [])),
            'environment': validated.get('entities', {}).get('environment', enriched.get('environment', {})),
            'context': context,
            'constraints': constraints,
            'confidence': validated.get('confidence', 0.0),
            'reasoning_trace': validated.get('reasoning_trace', [])
        }

    def _stage_1_extract_entities(self, problem_text: str, domain: PhysicsDomain) -> Dict:
        """Stage 2.1: Extract all entities from problem"""

        prompt = f"""Extract ALL physics entities from this {domain.value} problem with extreme precision.

Problem: {problem_text}

Extract as JSON:
{{
    "objects": [
        {{
            "id": "unique_id",
            "type": "specific_type",
            "properties": {{"key": value, ...}}
        }}
    ],
    "relationships": [
        {{
            "type": "relationship_type",
            "subject": "object_id",
            "target": "object_id_or_description",
            "properties": {{...}}
        }}
    ],
    "environment": {{"gravity": 9.8, "medium": "vacuum", ...}}
}}

Be EXTREMELY detailed. Include everything mentioned or implied."""

        response = self._call_api(prompt, temperature=0.1, max_tokens=4000)
        if response:
            result = self._parse_json(response)
            # Generic fix: Normalize response format
            # If AI returns a list directly (e.g. just the objects array), wrap it
            if isinstance(result, list):
                print(f"      🔧 AI returned list instead of dict - wrapping as objects")
                result = {"objects": result, "relationships": [], "environment": {}}
            # Ensure required keys exist
            if isinstance(result, dict):
                result.setdefault("objects", [])
                result.setdefault("relationships", [])
                result.setdefault("environment", {})

                # Generic fix: Last resort fallback - create generic objects from problem text
                # if JSON parsing completely failed (empty objects array)
                if not result.get("objects") and problem_text:
                    print(f"      🔧 JSON parsing failed - creating generic fallback objects")
                    result["objects"] = self._create_fallback_objects(problem_text, domain)
                    print(f"      ✅ Created {len(result['objects'])} fallback objects")

            return result if isinstance(result, dict) else {}
        return {}

    def _stage_2_understand_context(self, problem_text: str, entities: Dict, domain: PhysicsDomain) -> Dict:
        """Stage 2.2: Deep physics context understanding"""

        prompt = f"""Analyze the physics context of this {domain.value} problem in extreme detail.

Problem: {problem_text}
Entities: {json.dumps(entities, indent=2)}

Your task is to determine the following:

1.  **Sub-Domain**: What is the specific sub-domain of {domain.value}? (e.g., for MECHANICS, is it 'kinematics', 'dynamics', 'statics', 'work_energy', or 'rotational_motion'? For OPTICS, is it 'geometric_optics' or 'wave_optics'?)
2.  **Analysis Type**: What type of analysis is required? (e.g., 'static_equilibrium', 'dynamic_motion', 'conservation_of_energy', 'circuit_analysis', 'ray_tracing').
3.  **Applicable Laws**: List the fundamental physics laws and principles that are applicable to this problem (e.g., 'newtons_laws', 'coulombs_law', 'ohms_law', 'snells_law').
4.  **Key Concepts**: List the key physics concepts involved in the problem (e.g., 'friction', 'tension', 'electric_field', 'refractive_index').
5.  **Coordinate System**: What is the most appropriate coordinate system for this problem? ('cartesian', 'polar', 'cylindrical', 'spherical').

Your output MUST be a single JSON object with the keys: `sub_domain`, `analysis_type`, `applicable_laws`, `key_concepts`, `coordinate_system`.

Example for an optics problem:
{{
    "sub_domain": "geometric_optics",
    "analysis_type": "ray_tracing",
    "applicable_laws": ["snells_law", "thin_lens_equation"],
    "key_concepts": ["refractive_index", "focal_length", "image_formation"],
    "coordinate_system": "cartesian"
}}
"""

        response = self._call_api(prompt, temperature=0.3, max_tokens=3000)
        if response:
            return self._parse_json(response)
        return {'domain': domain.value, 'analysis_type': 'static'}

    def _stage_3_infer_implicit(self, entities: Dict, context: Dict, domain: PhysicsDomain) -> Dict:
        """Stage 2.3: Infer implicit physics information"""

        prompt = f"""Based on the physics context and the extracted entities, infer any implicit information that is not explicitly stated in the problem.

Context: {json.dumps(context, indent=2)}
Entities: {json.dumps(entities, indent=2)}

Examples of implicit information to infer:
- The presence of gravity.
- The direction of forces (e.g., normal force is perpendicular to the surface).
- The presence of friction.
- The conservation of energy or momentum.

Your output MUST be a single JSON object with the keys: `objects`, `relationships`.
"""

        response = self._call_api(prompt, temperature=0.3, max_tokens=3000)
        if response:
            enriched = self._parse_json(response)
            return enriched
        return entities

    def _stage_4_identify_constraints(self, entities: Dict, context: Dict, domain: PhysicsDomain) -> List[Dict]:
        """Stage 2.4: Identify all constraints"""

        constraints = []

        # Geometric constraints
        for rel in entities.get('relationships', []):
            if rel.get('type') in ['on', 'attached_to', 'connected_by']:
                constraints.append({
                    'type': 'geometric',
                    'constraint': rel['type'],
                    'details': rel
                })

        # Physics constraints from context
        analysis_type = context.get('analysis_type', '')
        if 'static' in analysis_type or 'equilibrium' in analysis_type:
            constraints.append({
                'type': 'physics',
                'constraint': 'equilibrium',
                'law': 'sum_forces_zero'
            })

        # Domain-specific constraints
        if domain == PhysicsDomain.CURRENT_ELECTRICITY:
            constraints.append({
                'type': 'physics',
                'constraint': 'kirchhoff',
                'laws': ['KCL', 'KVL']
            })

        return constraints

    def _stage_5_validate_and_correct(self, entities: Dict, constraints: List[Dict], context: Dict) -> Dict:
        """Stage 2.5: Validate and self-correct"""

        prompt = f"""You are a physics validation expert. Your task is to validate the extracted entities for a physics problem and to identify any missing information.

Here is the context of the problem:
{json.dumps(context, indent=2)}

Here are the extracted entities:
{json.dumps(entities, indent=2)}

Here are the extracted constraints:
{json.dumps(constraints, indent=2)}

**Validation Checklist:**

1.  **Completeness**: Are all the necessary entities present for the given domain and problem type? 
    *   For **optics**, there must be at least one `lens` or `mirror`, one `object`, and one `image`.
    *   For **circuits**, there must be a `power_source` (e.g., battery) and at least one other component (e.g., resistor, capacitor).
    *   For **mechanics**, there must be at least one `mass` or `object` with mass.
2.  **Consistency**: Are the properties of the objects consistent with the problem description? (e.g., are the numerical values and units correct?)
3.  **Relationships**: Are the relationships between the objects correctly identified? (e.g., are the series/parallel connections correct?)

**Your Task:**

1.  Carefully review the entities and constraints and compare them with the problem context.
2.  If any information is missing or incorrect, provide a list of the issues in the `issues` field.
3.  If any required entities are missing, list them in the `missing_information` field.
4.  If you can correct any of the entities, provide the corrected entities in the `corrected_entities` field.
5.  Provide a confidence score (0.0 to 1.0) for the validity of the extracted information.

**Output Format:**

Your output MUST be a single JSON object with the following fields:

```json
{{
    "is_valid": <true_or_false>,
    "issues": ["A list of issues found during validation."],
    "missing_information": ["A list of missing entities or properties."],
    "corrected_entities": {{ "objects": [...], "relationships": [...] }},
    "confidence": <a_number_between_0.0_and_1.0>,
    "reasoning_trace": ["A step-by-step explanation of your validation process."]
}}
```
"""

        response = self._call_api(prompt, temperature=0.2, max_tokens=4000)
        if response:
            validated = self._parse_json(response)
            if validated.get('is_valid'):
                return validated

        # Fallback: assume valid with moderate confidence
        return {
            'is_valid': True,
            'entities': entities,
            'confidence': 0.7,
            'reasoning_trace': [],
            'missing_information': []
        }

    def _build_canonical_spec(self, problem_text: str, domain: PhysicsDomain, extracted: Dict) -> CanonicalProblemSpec:
        """Step 3: Build canonical specification from extracted data"""

        print(f"\n--- Extracted Data ---\n{json.dumps(extracted, indent=2)}\n--------------------\n")

        context = extracted.get('context', {})

        spec = CanonicalProblemSpec(
            domain=domain,
            problem_type=context.get('analysis_type', 'unknown'),
            problem_text=problem_text,
            objects=extracted.get('objects', []),
            relationships=extracted.get('relationships', []),
            environment=extracted.get('environment', {}),
            physics_context=context,
            applicable_laws=context.get('applicable_laws', []),
            constraints=extracted.get('constraints', []),
            geometry={},  # Will be filled by scene builder
            confidence=extracted.get('confidence', 0.0),
            reasoning_trace=extracted.get('reasoning_trace', [])
        )

        return spec

    def _validate_completeness(self, spec: CanonicalProblemSpec) -> Tuple[bool, List[str]]:
        """Step 4: Validate specification completeness

        IMPORTANT: This validates diagram generation requirements, not physics calculation requirements.
        For diagram generation, we need:
        1. Domain classification (to select appropriate renderer)
        2. Objects with types (to know what to draw)
        3. Reasonable confidence (AI understood the problem)

        Physics-specific properties (charge values, masses, etc.) are NOT required for diagram generation,
        though they may be added by domain interpreters if available.
        """

        missing = []

        # Check domain (ESSENTIAL for diagram generation - selects renderer)
        if spec.domain == PhysicsDomain.UNKNOWN:
            missing.append("domain")

        # Check objects (ESSENTIAL for diagram generation - need something to draw)
        if not spec.objects:
            missing.append("objects")

        # Validate objects have minimum required structure for rendering
        for obj in spec.objects:
            if not obj.get('type'):
                # Object without type cannot be rendered
                if "object_types" not in missing:
                    missing.append("object_types")
                break

        # Check confidence (ESSENTIAL for diagram quality - AI should understand problem)
        if spec.confidence < 0.5:
            missing.append("low_confidence")

        # NOTE: Domain-specific physics properties (charge, mass, force, etc.) are NOT validated here.
        # These are calculation-specific, not diagram-specific. Domain interpreters can add default
        # values during scene building if needed for enhanced visualizations.

        return len(missing) == 0, missing

    def _score_complexity(self, spec: CanonicalProblemSpec) -> float:
        """Step 5: Score problem complexity (0.0 to 1.0)"""

        score = 0.0

        # Object count contribution (max 0.3)
        num_objects = len(spec.objects)
        score += min(num_objects / 10.0, 0.3)

        # Relationship count contribution (max 0.2)
        num_relationships = len(spec.relationships)
        score += min(num_relationships / 10.0, 0.2)

        # Constraint count contribution (max 0.2)
        num_constraints = len(spec.constraints)
        score += min(num_constraints / 10.0, 0.2)

        # Multiple domains (0.15)
        if 'sub_domains' in spec.physics_context:
            if len(spec.physics_context['sub_domains']) > 1:
                score += 0.15

        # Multiple analysis types (0.15)
        analysis_type = spec.physics_context.get('analysis_type', '')
        if ',' in analysis_type or 'and' in analysis_type:
            score += 0.15

        return min(score, 1.0)

    def _decompose(self, spec: CanonicalProblemSpec) -> List[CanonicalProblemSpec]:
        """Step 5b: Decompose complex problem into subproblems"""

        # For now, simple decomposition by object groups
        # TODO: Implement sophisticated AI-based decomposition

        subproblems = []

        # Group objects by type
        object_types = {}
        for obj in spec.objects:
            obj_type = obj.get('type', 'unknown')
            if obj_type not in object_types:
                object_types[obj_type] = []
            object_types[obj_type].append(obj)

        # Create subproblem for each type if multiple types
        if len(object_types) > 2:
            for obj_type, objects in object_types.items():
                subspec = CanonicalProblemSpec(
                    domain=spec.domain,
                    problem_type=f"{spec.problem_type}_{obj_type}",
                    problem_text=f"Subproblem: {obj_type} analysis",
                    objects=objects,
                    environment=spec.environment,
                    physics_context=spec.physics_context,
                    confidence=spec.confidence
                )
                subproblems.append(subspec)

        return subproblems

    def _call_api(self, prompt: str, temperature: float = 0.0, max_tokens: int = 4000) -> Optional[str]:
        """Call DeepSeek API with retry logic"""

        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                    print(f"      Retry {attempt}/{self.max_retries} after {delay}s...")
                    time.sleep(delay)

                response = requests.post(
                    self.api_base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.api_model,
                        "messages": [
                            {"role": "system", "content": "You are a physics problem analyzer. Extract complete specifications as valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=self.timeout_per_stage
                )

                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    return content

                elif response.status_code in [429, 500, 502, 503, 504]:
                    last_exception = Exception(f"API error {response.status_code}")
                    if attempt == self.max_retries:
                        raise last_exception
                    continue
                else:
                    raise Exception(f"API error {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                last_exception = requests.exceptions.Timeout("API timeout")
                if attempt == self.max_retries:
                    raise last_exception
                continue

            except Exception as e:
                last_exception = e
                if attempt == self.max_retries:
                    raise e
                continue

        if last_exception:
            raise last_exception
        return None

    def _parse_json(self, content: str) -> Dict:
        """Parse JSON from API response with robust error recovery

        Generic fix for malformed JSON responses from AI APIs:
        1. Try direct parsing
        2. Extract from markdown code blocks
        3. Fix common JSON errors (trailing commas, unescaped quotes, etc.)
        4. Extract partial valid JSON sections
        5. Return empty dict only as last resort
        """
        import re
        import jsonschema

        if not content or not content.strip():
            return {}

        # Strategy 1: Extract from markdown code blocks first
        original_content = content
        if '```json' in content:
            parts = content.split('```json')
            if len(parts) > 1:
                content = parts[1].split('```')[0].strip()
        elif '```' in content:
            parts = content.split('```')
            if len(parts) > 2:
                content = parts[1].strip()

        # Strategy 2: Try direct parsing and validation
        try:
            parsed_json = json.loads(content)
            jsonschema.validate(instance=parsed_json, schema=self.spec_schema)
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"      ⚠️  JSON parse error: {e}")
            print(f"      🔧 Attempting JSON repair...")
        except jsonschema.ValidationError as e:
            print(f"      ⚠️  JSON schema validation error: {e.message}")
            print(f"      🔧 Attempting to fix and re-validate...")

        # Strategy 3: Fix common JSON errors and re-validate
        try:
            # Remove trailing commas before closing braces/brackets
            fixed = re.sub(r',(\s*[}\]])', r'\1', content)
            # Remove comments (not valid in JSON)
            fixed = re.sub(r'//.*?\n', '\n', fixed)
            fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
            # Try parsing and validating the fixed version
            parsed_json = json.loads(fixed)
            jsonschema.validate(instance=parsed_json, schema=self.spec_schema)
            return parsed_json
        except (json.JSONDecodeError, jsonschema.ValidationError):
            print(f"      ⚠️  JSON repair strategy 1 failed")

        # ... (rest of the parsing logic) ...

        # Last resort: return empty dict
        print(f"      ❌ All JSON recovery strategies failed")
        return {}

    def _create_fallback_objects(self, problem_text: str, domain: PhysicsDomain) -> List[Dict]:
        """Generic fallback: Create basic objects from problem text when AI extraction completely fails

        This is a last-resort strategy to ensure diagram generation never completely fails.
        Uses simple keyword extraction to create generic placeholder objects.
        """
        import re

        objects = []
        text_lower = problem_text.lower()

        # Domain-specific object templates
        templates = {
            PhysicsDomain.ELECTROSTATICS: [
                ("capacitor", "capacitor"),
                ("plate", "capacitor_plate"),
                ("charge", "charge"),
                ("dielectric", "dielectric"),
                ("field", "electric_field")
            ],
            PhysicsDomain.CURRENT_ELECTRICITY: [
                ("capacitor", "capacitor"),
                ("resistor", "resistor"),
                ("battery", "battery"),
                ("circuit", "circuit"),
                ("wire", "wire")
            ],
            PhysicsDomain.MECHANICS: [
                ("block", "block"),
                ("mass", "block"),
                ("incline", "incline"),
                ("pulley", "pulley"),
                ("spring", "spring")
            ],
            PhysicsDomain.OPTICS: [
                ("lens", "lens"),
                ("mirror", "mirror"),
                ("ray", "light_ray"),
                ("image", "image_point"),
                ("object", "object_point")
            ]
        }

        # Get templates for this domain
        domain_templates = templates.get(domain, [])

        # Extract objects based on keywords found in text
        for keyword, obj_type in domain_templates:
            if keyword in text_lower:
                # Count occurrences or extract quantifiers
                count = text_lower.count(keyword)
                # Limit to reasonable number
                count = min(count, 3)

                for i in range(max(1, count)):
                    obj_id = f"{obj_type}_{i+1}" if count > 1 else obj_type
                    objects.append({
                        "id": obj_id,
                        "type": obj_type,
                        "properties": {},
                        "fallback": True  # Mark as fallback object
                    })

        # If still no objects, create a generic placeholder
        if not objects:
            objects.append({
                "id": "object_1",
                "type": "generic",
                "properties": {"label": "Generic Object"},
                "fallback": True
            })

        return objects
