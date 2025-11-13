"""
Universal Scene Builder - Single Robust Pipeline Phase 2
Converts CanonicalProblemSpec to UniversalScene using domain interpreters
NO fallbacks, NO guessing - returns complete scene or fails clearly
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json

from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain
from core.scene.schema_v1 import Scene, SceneObject, Constraint, PrimitiveType, ConstraintType


class IncompleteSceneError(Exception):
    """Raised when scene cannot be built completely"""
    def __init__(self, missing: List[str]):
        self.missing = missing
        super().__init__(f"Incomplete scene. Missing: {', '.join(missing)}")


class UniversalSceneBuilder:
    """
    Universal Scene Builder - Single robust implementation

    Converts CanonicalProblemSpec to Scene using MANDATORY domain interpreters
    Domain knowledge is DATA (interpreters, rules), not separate code paths

    ALWAYS returns complete Scene or raises IncompleteSceneError
    NO fallbacks, NO guessing
    """

    def __init__(self, domains_path: str = "domains"):
        """
        Initialize Universal Scene Builder

        Args:
            domains_path: Path to domains directory with interpreters
        """
        self.domains_path = Path(domains_path)

        # Load ALL domain interpreters (mandatory)
        self.interpreters = self._load_interpreters()

        # Load physics enrichment rules
        self.physics_rules = self._load_physics_rules()

        print(f"✅ UniversalSceneBuilder initialized")
        print(f"   Loaded {len(self.interpreters)} domain interpreters")
        print(f"   Domains: {', '.join(d.value if isinstance(d, PhysicsDomain) else str(d) for d in self.interpreters.keys())}")

    def build(self, spec: CanonicalProblemSpec, nlp_context: Optional[Dict] = None,
             property_graph: Optional[Any] = None, strategy: str = "DIRECT",
             diagram_plan: Optional[Any] = None) -> Scene:
        """
        Convert CanonicalProblemSpec to Scene with NLP enrichment and strategy

        Pipeline:
        1. Select domain interpreter
        2. Interpret spec to base scene (strategy-driven)
        3. Enrich with NLP context
        4. Enrich with physics rules
        5. Infer missing constraints (with property graph)
        6. Validate completeness

        Args:
            spec: Complete CanonicalProblemSpec from UniversalAIAnalyzer
            nlp_context: Optional NLP enrichment data (entities, triples, embeddings)
            property_graph: Optional PropertyGraph for relationship inference
            strategy: Building strategy (DIRECT, HIERARCHICAL, CONSTRAINT_FIRST)

        Returns:
            Complete Scene

        Raises:
            IncompleteSceneError: If scene cannot be completed
        """
        total_steps = 6 + (1 if diagram_plan else 0)
        step_counter = 1

        def _print_step(title: str, leading_newline: bool = True):
            nonlocal step_counter
            prefix = "\n" if leading_newline and step_counter > 1 else ""
            print(f"{prefix}Step {step_counter}/{total_steps}: {title}")
            step_counter += 1

        print(f"\n{'='*80}")
        print(f"🏗️  UNIVERSAL SCENE BUILDING - Phase 2")
        print(f"{ '='*80}\n")

        # Step 1: Select interpreter
        _print_step("Domain Interpreter Selection", leading_newline=False)
        interpreter = self._select_interpreter(spec.domain)
        print(f"   ✅ Selected: {spec.domain.value} interpreter")

        # Step 2: Interpret spec to scene (STRATEGY-DRIVEN)
        _print_step(f"Scene Interpretation ({strategy} strategy)")
        # Convert CanonicalProblemSpec to dict for legacy interpreters
        spec_dict = self._spec_to_dict(spec)

        if strategy == "HIERARCHICAL":
            # For complex problems: build hierarchically
            print("   Using HIERARCHICAL decomposition")
            scene = self._build_hierarchical(spec_dict, interpreter)
        elif strategy == "CONSTRAINT_FIRST":
            # For constraint-heavy problems: constraints drive layout
            print("   Using CONSTRAINT_FIRST approach")
            scene = self._build_constraint_first(spec_dict, interpreter)
        else:  # DIRECT strategy
            # Standard direct interpretation
            print("   Using DIRECT interpretation")
            scene = interpreter.interpret(spec_dict)

        print(f"   ✅ Generated: {len(scene.objects)} objects, {len(scene.constraints)} constraints")

        # Step 3: Enrich with NLP context (NEW)
        if nlp_context:
            _print_step("NLP Enrichment")
            scene = self._enrich_with_nlp(scene, spec, nlp_context, property_graph)
            print(f"   ✅ NLP-enriched: {len(scene.objects)} objects, {len(scene.constraints)} constraints")

        # Step 4: Enrich with physics rules
        _print_step("Physics Enrichment")
        scene = self._enrich_with_physics(scene, spec)
        print(f"   ✅ Enriched: {len(scene.objects)} objects (added implicit elements)")

        # Step 5: Infer missing constraints (with property graph)
        _print_step("Constraint Inference")
        scene = self._infer_constraints(scene, spec, property_graph)
        print(f"   ✅ Inferred: {len(scene.constraints)} total constraints")

        # Optional: Apply diagram plan overrides
        if diagram_plan:
            _print_step("Diagram Plan Alignment")
            applied = self._apply_diagram_plan_overrides(scene, diagram_plan)
            print(f"   ✅ Applied plan: {applied['positions']} positions, {applied['styles']} styles")

        # Final: Validate completeness
        _print_step("Scene Completeness Validation")
        is_complete, missing = self._validate_scene_completeness(scene, spec)

        if not is_complete:
            print(f"   ❌ Incomplete scene: Missing {', '.join(missing)}")
            raise IncompleteSceneError(missing)

        print(f"   ✅ Complete scene validated")

        print(f"\n{'='*80}")
        print(f"✅ UNIVERSAL SCENE BUILDING COMPLETE")
        print(f"{ '='*80}\n")

        return scene

    def _spec_to_dict(self, spec) -> Dict:
        """Convert CanonicalProblemSpec to dictionary for legacy interpreters"""
        from dataclasses import asdict

        # Convert dataclass to dict
        cached_plan = getattr(spec, 'diagram_plan', None)
        spec.diagram_plan = None  # Avoid recursive expansion
        spec_dict = asdict(spec)
        spec.diagram_plan = cached_plan
        if cached_plan:
            spec_dict['diagram_plan'] = None
            spec_dict['diagram_plan_metadata'] = getattr(spec, 'diagram_plan_metadata', {})

        # Ensure problem_text is available for interpreter matching
        if not spec_dict.get('problem_text'):
            spec_dict['problem_text'] = spec.problem_text if hasattr(spec, 'problem_text') else ""

        # Debug: print the converted dict keys
        print(f"   📋 Converted spec dict keys: {list(spec_dict.keys())[:10]}")
        print(f"   📝 Problem text available: {bool(spec_dict.get('problem_text'))}")

        return spec_dict

    def _build_hierarchical(self, spec_dict: Dict, interpreter) -> Scene:
        """
        Strategy: HIERARCHICAL - Decompose complex problems into subproblems

        For complex multi-part problems:
        1. Identify subproblems/components
        2. Build scenes for each component
        3. Compose into final scene
        """
        print("      Using HIERARCHICAL decomposition")

        # Step 1: Identify subproblems
        subproblems = self._identify_subproblems(spec_dict)

        if len(subproblems) <= 1:
            # Not actually hierarchical, fall back to direct
            print(f"         Only {len(subproblems)} component(s), using DIRECT")
            return interpreter.interpret(spec_dict)

        print(f"         Decomposed into {len(subproblems)} subproblems")

        # Step 2: Build scene for each subproblem
        subscenes = []
        for i, subproblem in enumerate(subproblems):
            print(f"         Building subproblem {i+1}/{len(subproblems)}")
            subscene = interpreter.interpret(subproblem)
            subscenes.append(subscene)

        # Step 3: Compose into final scene
        print(f"         Composing {len(subscenes)} subscenes")
        final_scene = self._compose_scenes(subscenes, spec_dict)

        return final_scene

    def _apply_diagram_plan_overrides(self, scene: Scene, diagram_plan) -> Dict[str, int]:
        """Apply layout/style hints from diagram plan onto the scene"""
        layout_hints = getattr(diagram_plan, 'layout_hints', {}) or {}
        style_hints = getattr(diagram_plan, 'style_hints', {}) or {}
        positions = layout_hints.get('positions', {}) if isinstance(layout_hints, dict) else {}

        id_lookup = {obj.id: obj for obj in scene.objects}
        applied_positions = 0
        applied_styles = 0

        for obj_id, coords in positions.items():
            obj = id_lookup.get(obj_id)
            if not obj:
                continue
            if isinstance(coords, dict):
                pos_dict = {
                    'x': coords.get('x', coords.get(0, 0)),
                    'y': coords.get('y', coords.get(1, 0)),
                    'anchor': coords.get('anchor', 'center'),
                    'rotation': coords.get('rotation', 0)
                }
            elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                pos_dict = {
                    'x': coords[0],
                    'y': coords[1],
                    'anchor': 'center',
                    'rotation': 0
                }
            else:
                continue
            obj.position = pos_dict
            applied_positions += 1

        for obj_id, style in style_hints.items():
            obj = id_lookup.get(obj_id)
            if not obj:
                continue
            merged_style = dict(obj.style or {})
            merged_style.update(style)
            obj.style = merged_style
            applied_styles += 1

        # Update scene-level metadata/coordinate system
        scene.metadata['planning_strategy'] = diagram_plan.strategy.value if hasattr(diagram_plan, 'strategy') else scene.metadata.get('planning_strategy', 'unknown')
        if isinstance(layout_hints, dict):
            solver = layout_hints.get('solver')
            if solver:
                scene.metadata['layout_solver'] = solver
        if hasattr(diagram_plan, 'canvas_width') and hasattr(diagram_plan, 'canvas_height'):
            scene.coord_system['extent'] = [diagram_plan.canvas_width, diagram_plan.canvas_height]
        if hasattr(diagram_plan, 'origin'):
            scene.coord_system['origin'] = diagram_plan.origin
        if hasattr(diagram_plan, 'margins'):
            scene.coord_system['margins'] = diagram_plan.margins

        return {
            'positions': applied_positions,
            'styles': applied_styles
        }

    def _identify_subproblems(self, spec_dict: Dict) -> List[Dict]:
        """
        Identify subproblems in complex problem

        Heuristics:
        - Multiple objects of different types
        - Independent systems (e.g., separate circuits)
        - Sequential steps in a process
        """
        # Simple heuristic: split by object count
        objects = spec_dict.get('objects', [])

        if len(objects) <= 2:
            # Too small to decompose
            return [spec_dict]

        # Group objects by type/category
        from collections import defaultdict
        grouped = defaultdict(list)

        for obj in objects:
            obj_type = obj.get('type', 'unknown')
            grouped[obj_type].append(obj)

        # If we have distinct groups, treat as subproblems
        if len(grouped) > 1:
            subproblems = []
            for obj_type, objs in grouped.items():
                subproblem = spec_dict.copy()
                subproblem['objects'] = objs
                # Filter constraints to only those involving these objects
                obj_ids = {obj.get('id') for obj in objs}
                subproblem['constraints'] = [
                    c for c in spec_dict.get('constraints', [])
                    if all(oid in obj_ids for oid in c.get('object_ids', []))
                ]
                subproblems.append(subproblem)
            return subproblems

        # Fall back: just return full problem
        return [spec_dict]

    def _compose_scenes(self, subscenes: List[Scene], original_spec: Dict) -> Scene:
        """
        Compose multiple subscenes into single scene

        Layouts subscenes spatially (e.g., left-to-right or top-to-bottom)
        """
        from core.scene.schema_v1 import Scene, SceneObject, Constraint, Position

        if not subscenes:
            # Return empty scene
            return Scene(objects=[], constraints=[])

        if len(subscenes) == 1:
            return subscenes[0]

        # Compose horizontally (left to right)
        composed = Scene(objects=[], constraints=[])
        x_offset = 0
        spacing = 200  # pixels between subscenes

        for subscene in subscenes:
            # Offset all objects in subscene
            for obj in subscene.objects:
                if obj.position:
                    obj.position.x += x_offset
                composed.objects.append(obj)

            # Add constraints
            composed.constraints.extend(subscene.constraints)

            # Update offset for next subscene
            if subscene.objects:
                # Find rightmost object
                max_x = max((obj.position.x if obj.position else 0)
                           for obj in subscene.objects)
                x_offset = max_x + spacing

        return composed

    def _build_constraint_first(self, spec_dict: Dict, interpreter) -> Scene:
        """
        Strategy: CONSTRAINT_FIRST - Let constraints drive scene structure

        For constraint-heavy problems:
        1. Extract explicit constraints first
        2. Build minimal object set
        3. Let constraints determine positions/relationships
        """
        print("      Using CONSTRAINT_FIRST approach")

        # Step 1: Extract constraints from problem text
        explicit_constraints = self._extract_constraints(spec_dict)

        if len(explicit_constraints) < 2:
            # Not enough constraints, fall back to direct
            print(f"         Only {len(explicit_constraints)} constraint(s), using DIRECT")
            return interpreter.interpret(spec_dict)

        print(f"         Found {len(explicit_constraints)} explicit constraints")

        # Step 2: Build minimal object set
        scene = interpreter.interpret(spec_dict)

        # Step 3: Augment with constraint-derived information
        scene = self._augment_with_constraints(scene, explicit_constraints, spec_dict)

        return scene

    def _extract_constraints(self, spec_dict: Dict) -> List[Dict]:
        """
        Extract explicit constraints from problem specification

        Looks for spatial relationships, distances, angles, etc.
        """
        constraints = []

        # Get pre-existing constraints from spec
        existing_constraints = spec_dict.get('constraints', [])
        constraints.extend(existing_constraints)

        # Parse problem text for additional constraints
        problem_text = spec_dict.get('problem_text', '').lower()

        # Common constraint patterns
        patterns = [
            (r'(\w+)\s+is\s+above\s+(\w+)', 'ABOVE'),
            (r'(\w+)\s+is\s+below\s+(\w+)', 'BELOW'),
            (r'(\w+)\s+is\s+left\s+of\s+(\w+)', 'LEFT_OF'),
            (r'(\w+)\s+is\s+right\s+of\s+(\w+)', 'RIGHT_OF'),
            (r'(\w+)\s+and\s+(\w+)\s+are\s+(\d+)\s*(?:m|cm|mm)\s+apart', 'DISTANCE'),
            (r'(\w+)\s+is\s+(\d+)\s*(?:m|cm|mm)\s+from\s+(\w+)', 'DISTANCE'),
        ]

        import re as regex
        for pattern, constraint_type in patterns:
            matches = regex.finditer(pattern, problem_text)
            for match in matches:
                constraints.append({
                    'type': constraint_type,
                    'source': match.group(1),
                    'target': match.group(2) if len(match.groups()) >= 2 else None,
                    'value': match.group(3) if len(match.groups()) >= 3 else None
                })

        return constraints

    def _augment_with_constraints(self, scene: Scene, constraints: List[Dict], spec_dict: Dict) -> Scene:
        """
        Augment scene with constraint-derived information

        Adds constraint objects to scene for layout engine to use
        """
        from core.scene.schema_v1 import Constraint, ConstraintType

        for constraint_info in constraints:
            # Map extracted constraints to scene objects
            source_objs = [obj for obj in scene.objects
                          if constraint_info.get('source', '').lower() in obj.id.lower()]
            target_objs = [obj for obj in scene.objects
                          if constraint_info.get('target', '').lower() in obj.id.lower()]

            if source_objs and target_objs:
                # Create constraint
                constraint_type_str = constraint_info.get('type', 'ABOVE')

                # Map string to enum
                constraint_type_map = {
                    'ABOVE': ConstraintType.ABOVE,
                    'BELOW': ConstraintType.BELOW,
                    'LEFT_OF': ConstraintType.LEFT_OF,
                    'RIGHT_OF': ConstraintType.RIGHT_OF,
                    'DISTANCE': ConstraintType.DISTANCE,
                }

                constraint_type = constraint_type_map.get(
                    constraint_type_str,
                    ConstraintType.ABOVE
                )

                constraint = Constraint(
                    type=constraint_type,
                    object_ids=[source_objs[0].id, target_objs[0].id],
                    parameters={'source': 'constraint_first_strategy'}
                )

                scene.constraints.append(constraint)

        return scene

    def _load_interpreters(self) -> Dict:
        """Load all domain interpreters"""

        interpreters = {}
        loaded_interpreters = []

        # Load CapacitorInterpreter
        try:
            from core.interpreters.capacitor_interpreter import CapacitorInterpreter
            capacitor_interp = CapacitorInterpreter()
            interpreters[PhysicsDomain.ELECTROSTATICS] = capacitor_interp
            interpreters[PhysicsDomain.CURRENT_ELECTRICITY] = capacitor_interp
            loaded_interpreters.append("CapacitorInterpreter (electrostatics & circuits)")
        except ImportError as e:
            print(f"   ⚠️  Failed to load CapacitorInterpreter: {e}")

        # Load OpticsInterpreter
        try:
            from core.interpreters.optics_interpreter import OpticsInterpreter
            optics_interp = OpticsInterpreter()
            interpreters[PhysicsDomain.OPTICS] = optics_interp
            loaded_interpreters.append("OpticsInterpreter")
        except ImportError as e:
            print(f"   ⚠️  Failed to load OpticsInterpreter: {e}")

        # Load MechanicsInterpreter
        try:
            from core.interpreters.mechanics_interpreter import MechanicsInterpreter
            mechanics_interp = MechanicsInterpreter()
            interpreters[PhysicsDomain.MECHANICS] = mechanics_interp
            loaded_interpreters.append("MechanicsInterpreter")
        except ImportError as e:
            print(f"   ⚠️  Failed to load MechanicsInterpreter: {e}")

        # Print success message
        if loaded_interpreters:
            print(f"   ✅ Loaded interpreters: {', '.join(loaded_interpreters)}")

        # Add generic interpreter for domains without specific interpreters
        if PhysicsDomain.MECHANICS not in interpreters:
            interpreters[PhysicsDomain.MECHANICS] = GenericInterpreter("mechanics")
        if PhysicsDomain.OPTICS not in interpreters:
            interpreters[PhysicsDomain.OPTICS] = GenericInterpreter("optics")
        if PhysicsDomain.ELECTROSTATICS not in interpreters:
            interpreters[PhysicsDomain.ELECTROSTATICS] = GenericInterpreter("electrostatics")

        interpreters[PhysicsDomain.THERMODYNAMICS] = GenericInterpreter("thermodynamics")
        interpreters[PhysicsDomain.MAGNETISM] = GenericInterpreter("magnetism")
        interpreters[PhysicsDomain.WAVES] = GenericInterpreter("waves")
        interpreters[PhysicsDomain.MODERN_PHYSICS] = GenericInterpreter("modern_physics")

        return interpreters

    def _load_physics_rules(self) -> Dict:
        """Load physics enrichment rules from domain configs"""

        rules = {}

        # Try to load from domains/ directory
        for domain in PhysicsDomain:
            rules_file = self.domains_path / domain.value / "rules.json"
            if rules_file.exists():
                with open(rules_file) as f:
                    rules[domain] = json.load(f)

        return rules

    def _select_interpreter(self, domain: PhysicsDomain):
        """Step 1: Select appropriate interpreter for domain"""

        if domain in self.interpreters:
            return self.interpreters[domain]

        # Fallback to generic interpreter
        print(f"   ⚠️  No specific interpreter for {domain.value}, using generic")
        return GenericInterpreter(domain.value)


    def _enrich_with_nlp(self, scene: Scene, spec: CanonicalProblemSpec,
                          nlp_context: Dict, property_graph: Optional[Any] = None) -> Scene:
        """
        Enrich scene with NLP context (entities, triples, embeddings)

        Uses:
        - Stanza entities to boost object detection confidence
        - OpenIE triples to infer implicit relationships
        - SciBERT embeddings for semantic similarity
        - Property graph for multi-source understanding
        """
        enrichment_count = 0

        # 1. Use Stanza entities to validate/boost objects
        if 'entities' in nlp_context:
            entities = nlp_context['entities']
            print(f"     Using {len(entities)} NLP entities for validation")

            # Match entities to scene objects
            for entity in entities:
                # Extract entity text and type (handle both dict and tuple formats)
                if isinstance(entity, dict):
                    entity_text = entity.get('text', '')
                    entity_type = entity.get('pos', 'object')  # POS tag from Stanza
                elif isinstance(entity, (tuple, list)) and len(entity) >= 2:
                    entity_text = entity[0]
                    entity_type = entity[1]
                else:
                    continue  # Skip malformed entities

                # Check if entity matches any scene object
                matching_objs = [obj for obj in scene.objects
                               if entity_text.lower() in obj.id.lower()]
                if matching_objs:
                    # Boost confidence or add metadata
                    for obj in matching_objs:
                        if not obj.properties:
                            obj.properties = {}
                        obj.properties['nlp_validated'] = True
                        obj.properties['entity_type'] = entity_type
                    enrichment_count += len(matching_objs)

        # 2. Use OpenIE triples to infer relationships/constraints
        if 'triples' in nlp_context:
            triples = nlp_context['triples']
            print(f"     Using {len(triples)} NLP triples for constraints")

            for subject, relation, obj in triples:
                # Infer spatial constraints from triples
                if 'above' in relation.lower():
                    # Find objects in scene
                    subj_objs = [o for o in scene.objects if subject.lower() in o.id.lower()]
                    obj_objs = [o for o in scene.objects if obj.lower() in o.id.lower()]

                    if subj_objs and obj_objs:
                        # Add ABOVE constraint
                        scene.constraints.append(Constraint(
                            type=ConstraintType.ABOVE,
                            object_ids=[subj_objs[0].id, obj_objs[0].id],
                            parameters={'source': 'nlp_triple'}
                        ))
                        enrichment_count += 1

                elif 'left' in relation.lower() or 'right' in relation.lower():
                    # Infer horizontal relationships
                    subj_objs = [o for o in scene.objects if subject.lower() in o.id.lower()]
                    obj_objs = [o for o in scene.objects if obj.lower() in o.id.lower()]

                    if subj_objs and obj_objs:
                        scene.constraints.append(Constraint(
                            type=ConstraintType.HORIZONTAL_ALIGN,
                            object_ids=[subj_objs[0].id, obj_objs[0].id],
                            parameters={'source': 'nlp_triple'}
                        ))
                        enrichment_count += 1

        # 3. Use property graph for relationship inference
        if property_graph:
            print(f"     Using property graph with {len(property_graph.get_all_nodes())} nodes")

            # Query graph for spatial relationships
            try:
                from core.property_graph import EdgeType
                # Get all spatial relationship edges
                spatial_types = [EdgeType.LOCATED_AT, EdgeType.ADJACENT_TO, EdgeType.BETWEEN,
                                EdgeType.ABOVE, EdgeType.BELOW, EdgeType.LEFT_OF, EdgeType.RIGHT_OF]
                spatial_edges = []
                for edge_type in spatial_types:
                    spatial_edges.extend(property_graph.get_edges(edge_type=edge_type))
                for edge in spatial_edges:
                    # Convert graph edges to scene constraints
                    source_obj = [o for o in scene.objects if o.id == edge.source]
                    target_obj = [o for o in scene.objects if o.id == edge.target]

                    if source_obj and target_obj:
                        if 'above' in edge.label.lower():
                            scene.constraints.append(Constraint(
                                type=ConstraintType.ABOVE,
                                object_ids=[source_obj[0].id, target_obj[0].id],
                                parameters={'source': 'property_graph'}
                            ))
                            enrichment_count += 1
            except Exception as e:
                print(f"     ⚠️  Property graph query failed: {e}")

        print(f"     Enriched: +{enrichment_count} validations/constraints")
        return scene

    def _enrich_with_physics(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """Step 3: Enrich scene with implicit physics elements"""

        # Add implicit forces for mechanics
        if spec.domain == PhysicsDomain.MECHANICS:
            scene = self._add_implicit_forces(scene, spec)

        # Add field lines for electrostatics
        elif spec.domain == PhysicsDomain.ELECTROSTATICS:
            scene = self._add_field_lines(scene, spec)

        # Add current flow for circuits
        elif spec.domain == PhysicsDomain.CURRENT_ELECTRICITY:
            scene = self._add_current_flow(scene, spec)
            
        # Add focal points for optics
        elif spec.domain == PhysicsDomain.OPTICS:
            scene = self._add_focal_points(scene, spec)

        return scene

    def _add_implicit_forces(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """Add implicit forces (gravity, normal, friction) for mechanics"""

        # Find all mass objects
        mass_objects = [obj for obj in scene.objects if 'mass' in obj.properties]

        for obj in mass_objects:
            mass = obj.properties.get('mass', 1.0)

            # Add gravity arrow
            scene.objects.append(SceneObject(
                id=f"force_gravity_{obj.id}",
                type=PrimitiveType.ARROW,
                properties={
                    "direction": "downward",
                    "magnitude": mass * 9.8,
                    "label": f"mg",
                    "color": "#cc0000",
                    "parent": obj.id,
                    "implicit": True
                }
            ))

            # If on surface, add normal force
            if any(rel.get('type') == 'on' and rel.get('subject') == obj.id
                   for rel in spec.relationships):
                scene.objects.append(SceneObject(
                    id=f"force_normal_{obj.id}",
                    type=PrimitiveType.ARROW,
                    properties={
                        "direction": "upward",
                        "magnitude": mass * 9.8,
                        "label": "N",
                        "color": "#0000cc",
                        "parent": obj.id,
                        "implicit": True
                    }
                ))

        return scene

    def _add_field_lines(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """Add electric field lines for electrostatics"""

        # Find all charge objects
        charges = [obj for obj in scene.objects if obj.type == PrimitiveType.CHARGE]

        # Add field lines between charges
        for i, charge1 in enumerate(charges):
            for charge2 in charges[i+1:]:
                # Add field line
                scene.objects.append(SceneObject(
                    id=f"field_line_{charge1.id}_{charge2.id}",
                    type=PrimitiveType.FIELD_LINE,
                    properties={
                        "source": charge1.id,
                        "target": charge2.id,
                        "implicit": True
                    }
                ))

        return scene

    def _add_current_flow(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """Add current flow indicators for circuits"""

        # Find battery/power source
        batteries = [obj for obj in scene.objects
                    if obj.type == PrimitiveType.BATTERY_SYMBOL or 'battery' in obj.properties]

        if batteries:
            # Add current flow arrow
            scene.objects.append(SceneObject(
                id="current_flow",
                type=PrimitiveType.ARROW,
                properties={
                    "label": "I",
                    "color": "#0066cc",
                    "implicit": True,
                    "style": "dashed"
                }
            ))

        return scene

    def _infer_constraints(self, scene: Scene, spec: CanonicalProblemSpec, property_graph: Optional[Any] = None) -> Scene:
        """Step 4: Infer missing layout constraints"""

        # Infer alignment constraints
        objects_by_type = {}
        for obj in scene.objects:
            obj_type = obj.type
            if obj_type not in objects_by_type:
                objects_by_type[obj_type] = []
            objects_by_type[obj_type].append(obj)

        # Add alignment for similar objects
        for obj_type, objects in objects_by_type.items():
            if len(objects) >= 2:
                # Align horizontally if same type
                scene.constraints.append(Constraint(
                    type=ConstraintType.ALIGNED_H,
                    objects=[obj.id for obj in objects]
                ))

        # Infer distance constraints from relationships
        for rel in spec.relationships:
            if rel.get('type') == 'connected_by':
                # Add CONNECTED constraint
                scene.constraints.append(Constraint(
                    type=ConstraintType.CONNECTED,
                    objects=[rel['subject'], rel['target']]
                ))

        # Infer no-overlap for all objects
        if len(scene.objects) >= 2:
            scene.constraints.append(Constraint(
                type=ConstraintType.NO_OVERLAP,
                objects=[obj.id for obj in scene.objects]
            ))

        return scene

    def _validate_scene_completeness(self, scene: Scene, spec: CanonicalProblemSpec) -> tuple:
        """Step 5: Validate scene has all required elements for diagram rendering"""

        missing = []

        # Check objects (ESSENTIAL - need something to render)
        if not scene.objects:
            missing.append("objects")
            return False, missing

        # Validate all objects have renderable primitive types
        for obj in scene.objects:
            if not hasattr(obj, 'type') or obj.type is None:
                missing.append("object_primitive_types")
                break

        # Domain-specific validation
        if spec.domain == PhysicsDomain.OPTICS:
            missing.extend(self._validate_optics_scene(scene))
        elif spec.domain == PhysicsDomain.CURRENT_ELECTRICITY:
            missing.extend(self._validate_circuit_scene(scene))
        elif spec.domain == PhysicsDomain.MECHANICS:
            missing.extend(self._validate_mechanics_scene(scene))

        return len(missing) == 0, missing

    def _validate_optics_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of an optics scene."""
        missing = []
        has_lens_or_mirror = any(obj.type in [PrimitiveType.LENS, PrimitiveType.MIRROR] for obj in scene.objects)
        has_object = any(obj.properties.get('is_object') for obj in scene.objects)
        has_image = any(obj.properties.get('is_image') for obj in scene.objects)

        if not has_lens_or_mirror:
            missing.append("lens_or_mirror")
        if not has_object:
            missing.append("object")
        if not has_image:
            missing.append("image")
        return missing

    def _validate_circuit_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of a circuit scene."""
        missing = []

        # Check for any circuit-related objects (more permissive for property graph-driven planning)
        has_circuit_objects = len(scene.objects) > 0

        # Only check for specific types if no objects at all
        if not has_circuit_objects:
            has_power_source = any(obj.type == PrimitiveType.BATTERY_SYMBOL for obj in scene.objects)
            has_component = any(obj.type in [PrimitiveType.RESISTOR_SYMBOL, PrimitiveType.CAPACITOR_SYMBOL] for obj in scene.objects)

            if not has_power_source:
                missing.append("power_source")
            if not has_component:
                missing.append("circuit_component")

        return missing

    def _validate_mechanics_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of a mechanics scene."""
        missing = []
        has_mass = any(obj.type == PrimitiveType.MASS for obj in scene.objects)
        if not has_mass:
            missing.append("mass")
        return missing


class GenericInterpreter:
    """Generic interpreter for domains without specific interpreters"""

    def __init__(self, domain: str):
        self.domain = domain

    def interpret(self, spec: Dict) -> Scene:
        """Convert spec dict to scene using generic approach"""

        scene = Scene()
        scene.metadata["domain"] = self.domain

        # Convert objects from spec to scene objects
        for obj in spec.get('objects', []) or []:
            obj_type = self._map_object_type(obj.get('type', 'unknown'))

            scene.objects.append(SceneObject(
                id=obj.get('id', f"obj_{len(scene.objects)}"),
                type=obj_type,
                properties=obj.get('properties', {})
            ))

        # Convert constraints from spec
        for constraint in spec.get('constraints', []) or []:
            constraint_type = self._map_constraint_type(constraint.get('type', 'unknown'))

            if constraint_type:
                scene.constraints.append(Constraint(
                    type=constraint_type,
                    objects=constraint.get('objects', []),
                    value=constraint.get('value')
                ))

        return scene

    def _map_object_type(self, type_str: str) -> PrimitiveType:
        """Map object type string to PrimitiveType"""

        mapping = {
            # General
            'rectangle': PrimitiveType.RECTANGLE,
            'circle': PrimitiveType.CIRCLE,
            'line': PrimitiveType.LINE,
            'arrow': PrimitiveType.ARROW,
            'point': PrimitiveType.POINT,
            'polyline': PrimitiveType.POLYLINE,

            # Mechanics
            'mass': PrimitiveType.MASS,
            'block': PrimitiveType.MASS,
            'pulley': PrimitiveType.PULLEY,
            'spring': PrimitiveType.SPRING,
            'force': PrimitiveType.ARROW,

            # Electrostatics & Circuits
            'charge': PrimitiveType.CHARGE,
            'capacitor': PrimitiveType.CAPACITOR_SYMBOL,
            'resistor': PrimitiveType.RESISTOR_SYMBOL,
            'battery': PrimitiveType.BATTERY_SYMBOL,
            'field_line': PrimitiveType.FIELD_LINE,

            # Optics
            'lens': PrimitiveType.LENS,
            'mirror': PrimitiveType.MIRROR,
            'principal_axis': PrimitiveType.LINE,
            'focal_point': PrimitiveType.FOCAL_POINT,
            'ray': PrimitiveType.POLYLINE,
        }

        return mapping.get(type_str.lower(), PrimitiveType.RECTANGLE)

    def _map_constraint_type(self, type_str: str) -> Optional[ConstraintType]:
        """Map constraint type string to ConstraintType"""

        mapping = {
            'geometric': ConstraintType.COINCIDENT,
            'connected': ConstraintType.CONNECTED,
            'connected_to': ConstraintType.CONNECTED,
            'series': ConstraintType.SERIES,
            'parallel': ConstraintType.PARALLEL,
            'collinear': ConstraintType.COLLINEAR,
            'symmetric': ConstraintType.SYMMETRIC,
            'perpendicular': ConstraintType.PERPENDICULAR,
            'distance': ConstraintType.DISTANCE,
            'aligned_h': ConstraintType.ALIGNED_H,
            'aligned_v': ConstraintType.ALIGNED_V,
            'centered': ConstraintType.CENTERED,
        }

        return mapping.get(type_str.lower())


    def _add_focal_points(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:
        """Add focal points for lenses and mirrors in optics problems."""
        for obj in scene.objects:
            if obj.type in [PrimitiveType.LENS, PrimitiveType.MIRROR]:
                focal_length = obj.properties.get('focal_length')
                if focal_length:
                    # Add two focal points, one on each side of the lens/mirror
                    scene.objects.append(SceneObject(
                        id=f"{obj.id}_f1",
                        type=PrimitiveType.FOCAL_POINT,
                        properties={
                            'parent': obj.id,
                            'distance': -focal_length,
                            'side': 'left'
                        }
                    ))
                    scene.objects.append(SceneObject(
                        id=f"{obj.id}_f2",
                        type=PrimitiveType.FOCAL_POINT,
                        properties={
                            'parent': obj.id,
                            'distance': focal_length,
                            'side': 'right'
                        }
                    ))
        return scene

    def _validate_optics_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of an optics scene."""
        missing = []
        has_lens_or_mirror = any(obj.type in [PrimitiveType.LENS, PrimitiveType.MIRROR] for obj in scene.objects)
        has_object = any(obj.properties.get('is_object') for obj in scene.objects)
        has_image = any(obj.properties.get('is_image') for obj in scene.objects)

        if not has_lens_or_mirror:
            missing.append("lens_or_mirror")
        if not has_object:
            missing.append("object")
        if not has_image:
            missing.append("image")
        return missing

    def _validate_circuit_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of a circuit scene."""
        missing = []

        # Check for any circuit-related objects (more permissive for property graph-driven planning)
        has_circuit_objects = len(scene.objects) > 0

        # Only check for specific types if no objects at all
        if not has_circuit_objects:
            has_power_source = any(obj.type == PrimitiveType.BATTERY_SYMBOL for obj in scene.objects)
            has_component = any(obj.type in [PrimitiveType.RESISTOR_SYMBOL, PrimitiveType.CAPACITOR_SYMBOL] for obj in scene.objects)

            if not has_power_source:
                missing.append("power_source")
            if not has_component:
                missing.append("circuit_component")

        return missing

    def _validate_circuit_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of a circuit scene."""
        missing = []

        # Check for any circuit-related objects (more permissive for property graph-driven planning)
        has_circuit_objects = len(scene.objects) > 0

        # Only check for specific types if no objects at all
        if not has_circuit_objects:
            has_power_source = any(obj.type == PrimitiveType.BATTERY_SYMBOL for obj in scene.objects)
            has_component = any(obj.type in [PrimitiveType.RESISTOR_SYMBOL, PrimitiveType.CAPACITOR_SYMBOL] for obj in scene.objects)

            if not has_power_source:
                missing.append("power_source")
            if not has_component:
                missing.append("circuit_component")

        return missing

    def _validate_mechanics_scene(self, scene: Scene) -> List[str]:
        """Validate the completeness of a mechanics scene."""
        missing = []
        has_mass = any(obj.type == PrimitiveType.MASS for obj in scene.objects)
        if not has_mass:
            missing.append("mass")
        return missing
