"""
Diagram Planner - Multi-Stage Diagram Planning
Phase 1B of Planning & Reasoning Roadmap

Implements diagram planning with:
1. Complexity assessment
2. Problem decomposition
3. Strategy selection
4. Constraint formulation
5. Plan synthesis

Architecture:
    CanonicalProblemSpec → DiagramPlanner → DiagramPlan → Solver/Builder
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math

from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain
from core.diagram_plan import (
    DiagramPlan, PlanningStrategy, LayoutObjective, ConstraintPriority,
    LayoutConstraint, Subproblem,
    create_no_overlap_constraint, create_bounds_constraint,
    create_distance_constraint, create_alignment_constraint
)


class DiagramPlanner:
    """
    Multi-stage diagram planner

    Takes a CanonicalProblemSpec and produces a DiagramPlan with:
    - Complexity assessment
    - Strategy selection
    - Constraint formulation
    - Subproblem decomposition (if needed)
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize diagram planner

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}

        # Configuration parameters
        self.complexity_threshold_decompose = self.config.get('complexity_threshold_decompose', 0.7)
        self.complexity_threshold_advanced = self.config.get('complexity_threshold_advanced', 0.5)
        self.default_canvas_size = self.config.get('default_canvas_size', (1200, 800))
        self.default_margins = self.config.get('default_margins', [40, 40, 40, 40])

    # ========== Main Planning Method ==========

    def plan(self, spec: CanonicalProblemSpec) -> DiagramPlan:
        """
        Create a diagram plan from specifications

        Args:
            spec: CanonicalProblemSpec to plan for

        Returns:
            DiagramPlan with planning decisions and constraints

        Workflow:
        1. Assess complexity
        2. Decompose if needed
        3. Select strategy
        4. Formulate constraints
        5. Synthesize plan
        """
        # Initialize plan
        plan = DiagramPlan(
            original_spec=spec,
            complexity_score=0.0,
            strategy=PlanningStrategy.HEURISTIC,
            canvas_width=self.default_canvas_size[0],
            canvas_height=self.default_canvas_size[1],
            margins=self.default_margins.copy()
        )

        # Step 1: Assess complexity
        complexity = self.assess_complexity(spec)
        plan.complexity_score = complexity
        plan.log_planning_step('complexity_assessment', {
            'complexity_score': complexity,
            'object_count': len(spec.objects),
            'relationship_count': len(spec.relationships),
            'constraint_count': len(spec.constraints)
        })

        # Step 2: Decompose if complex
        if complexity >= self.complexity_threshold_decompose:
            subproblems = self.decompose(spec)
            for sp in subproblems:
                plan.add_subproblem(sp)
            plan.log_planning_step('decomposition', {
                'subproblem_count': len(subproblems),
                'subproblem_ids': [sp.id for sp in subproblems]
            })
        else:
            # Create single subproblem
            subproblem = Subproblem(
                id='main',
                description=spec.problem_text[:100] if spec.problem_text else 'Main problem',
                specs=spec,
                complexity=complexity
            )
            plan.add_subproblem(subproblem)

        # Step 3: Select strategy
        strategy = self.select_strategy(spec, complexity)
        plan.strategy = strategy
        plan.log_planning_step('strategy_selection', {
            'strategy': strategy.value,
            'reasoning': self._explain_strategy_choice(complexity, spec)
        })

        # Step 4: Select objectives
        objectives = self.select_objectives(spec)
        plan.objectives = objectives
        plan.log_planning_step('objective_selection', {
            'objectives': [obj.value for obj in objectives]
        })

        # Step 5: Formulate constraints
        constraints = self.formulate_constraints(spec, strategy)
        for constraint in constraints:
            plan.add_global_constraint(constraint)
        plan.log_planning_step('constraint_formulation', {
            'global_constraint_count': len(constraints),
            'constraint_types': list(set(c.type for c in constraints))
        })

        # Step 6: Add domain-specific constraints
        domain_constraints = self.add_domain_constraints(spec)
        for constraint in domain_constraints:
            plan.add_global_constraint(constraint)
        plan.log_planning_step('domain_constraints', {
            'domain': spec.domain.value if hasattr(spec.domain, 'value') else spec.domain,
            'constraint_count': len(domain_constraints)
        })

        # Step 7: Set layout hints
        plan.layout_hints = self.generate_layout_hints(spec)
        plan.log_planning_step('layout_hints', plan.layout_hints)

        return plan

    # ========== Complexity Assessment ==========

    def assess_complexity(self, spec: CanonicalProblemSpec) -> float:
        """
        Assess problem complexity (0-1 scale)

        Factors:
        - Number of objects
        - Number of relationships
        - Number of constraints
        - Domain complexity
        - Geometry complexity

        Returns:
            Complexity score (0.0 = simple, 1.0 = very complex)
        """
        score = 0.0

        # Object count contribution (0-0.3)
        object_count = len(spec.objects)
        object_score = min(object_count / 20.0, 1.0) * 0.3
        score += object_score

        # Relationship count contribution (0-0.2)
        relationship_count = len(spec.relationships)
        relationship_score = min(relationship_count / 15.0, 1.0) * 0.2
        score += relationship_score

        # Constraint count contribution (0-0.2)
        constraint_count = len(spec.constraints)
        constraint_score = min(constraint_count / 10.0, 1.0) * 0.2
        score += constraint_score

        # Domain complexity contribution (0-0.2)
        domain_complexity = self._get_domain_complexity(spec.domain)
        score += domain_complexity

        # Geometry complexity contribution (0-0.1)
        geometry = spec.geometry
        if geometry:
            if geometry.get('shape') in ['complex', '3d', 'irregular']:
                score += 0.1
            elif geometry.get('shape') in ['circle', 'rectangle', 'square']:
                score += 0.03
            else:
                score += 0.05

        # Cap at 1.0
        return min(score, 1.0)

    def _get_domain_complexity(self, domain: Any) -> float:
        """Get complexity score for domain"""
        # Convert to string if enum
        domain_str = domain.value if hasattr(domain, 'value') else str(domain).lower()

        complexity_map = {
            'mechanics': 0.1,
            'electrostatics': 0.12,
            'current_electricity': 0.15,
            'magnetism': 0.15,
            'optics': 0.18,
            'thermodynamics': 0.2,
            'waves': 0.17,
            'modern_physics': 0.2,
            'unknown': 0.05
        }

        return complexity_map.get(domain_str, 0.1)

    # ========== Problem Decomposition ==========

    def decompose(self, spec: CanonicalProblemSpec) -> List[Subproblem]:
        """
        Decompose complex problem into subproblems

        Strategies:
        - Spatial decomposition (by location/region)
        - Hierarchical decomposition (by structure)
        - Temporal decomposition (by sequence)
        - Domain decomposition (by physics domain)

        Args:
            spec: Problem specification

        Returns:
            List of subproblems
        """
        subproblems = []

        # Check if already has subproblems
        if spec.subproblems and len(spec.subproblems) > 0:
            for i, sub_spec in enumerate(spec.subproblems):
                subproblems.append(Subproblem(
                    id=f"subproblem_{i}",
                    description=f"Subproblem {i}",
                    specs=sub_spec if isinstance(sub_spec, CanonicalProblemSpec) else spec,
                    complexity=self.assess_complexity(sub_spec) if isinstance(sub_spec, CanonicalProblemSpec) else 0.5
                ))
            return subproblems

        # Try spatial decomposition based on relationships
        spatial_groups = self._decompose_by_connectivity(spec)

        if len(spatial_groups) > 1:
            # Create subproblem for each spatial group
            for i, group in enumerate(spatial_groups):
                sub_spec = self._create_subspecs(spec, group)
                subproblems.append(Subproblem(
                    id=f"spatial_{i}",
                    description=f"Spatial region {i}",
                    specs=sub_spec,
                    complexity=self.assess_complexity(sub_spec)
                ))
        else:
            # Fallback: Create single subproblem
            subproblems.append(Subproblem(
                id="main",
                description=spec.problem_text[:100] if spec.problem_text else "Main problem",
                specs=spec,
                complexity=self.assess_complexity(spec)
            ))

        return subproblems

    def _decompose_by_connectivity(self, spec: CanonicalProblemSpec) -> List[List[str]]:
        """Decompose objects into connected groups"""
        # Build adjacency list from relationships
        adjacency: Dict[str, List[str]] = {}
        all_objects = set()

        for obj in spec.objects:
            obj_id = obj.get('id', '')
            if obj_id:
                all_objects.add(obj_id)
                adjacency[obj_id] = []

        for rel in spec.relationships:
            subject = rel.get('subject', '')
            target = rel.get('target', '')
            if subject and target:
                if subject not in adjacency:
                    adjacency[subject] = []
                if target not in adjacency:
                    adjacency[target] = []
                adjacency[subject].append(target)
                adjacency[target].append(subject)

        # Find connected components
        visited = set()
        groups = []

        def dfs(node: str, group: List[str]):
            visited.add(node)
            group.append(node)
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, group)

        for obj_id in all_objects:
            if obj_id not in visited:
                group: List[str] = []
                dfs(obj_id, group)
                if group:
                    groups.append(group)

        return groups

    def _create_subspecs(self, spec: CanonicalProblemSpec, object_ids: List[str]) -> CanonicalProblemSpec:
        """Create subspecification for a subset of objects"""
        from copy import deepcopy

        sub_spec = CanonicalProblemSpec(
            domain=spec.domain,
            problem_type=spec.problem_type,
            problem_text=spec.problem_text,
            objects=[obj for obj in spec.objects if obj.get('id', '') in object_ids],
            relationships=[rel for rel in spec.relationships
                          if rel.get('subject', '') in object_ids or rel.get('target', '') in object_ids],
            constraints=[cons for cons in spec.constraints
                        if any(obj_id in object_ids for obj_id in cons.get('objects', []))],
            environment=deepcopy(spec.environment),
            physics_context=deepcopy(spec.physics_context),
            geometry=deepcopy(spec.geometry)
        )

        return sub_spec

    # ========== Strategy Selection ==========

    def select_strategy(self, spec: CanonicalProblemSpec, complexity: float) -> PlanningStrategy:
        """
        Select planning strategy based on complexity and domain

        Args:
            spec: Problem specification
            complexity: Complexity score

        Returns:
            Selected PlanningStrategy
        """
        # Check for explicit constraints first - if present, use constraint-based approach
        # regardless of complexity (even simple problems benefit from Z3 if they have constraints)
        num_constraints = len(spec.constraints) if hasattr(spec, 'constraints') and spec.constraints else 0

        # If problem has multiple objects with constraints, prefer constraint-based approach
        if num_constraints >= 3 or (num_constraints >= 1 and len(spec.objects) >= 3):
            domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()
            if domain_str in ['mechanics', 'electrostatics'] and len(spec.objects) < 10:
                return PlanningStrategy.SYMBOLIC_PHYSICS
            else:
                return PlanningStrategy.CONSTRAINT_BASED

        # Simple problems with few/no constraints → Heuristic
        if complexity < 0.15:  # Lowered threshold from 0.3 to 0.15
            return PlanningStrategy.HEURISTIC

        # Medium complexity → Constraint-based
        elif complexity < 0.6:
            # For physics problems, use symbolic if applicable
            domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()
            if domain_str in ['mechanics', 'electrostatics'] and len(spec.objects) < 10:
                return PlanningStrategy.SYMBOLIC_PHYSICS
            else:
                return PlanningStrategy.CONSTRAINT_BASED

        # High complexity → Hybrid
        else:
            return PlanningStrategy.HYBRID

    def _explain_strategy_choice(self, complexity: float, spec: CanonicalProblemSpec) -> str:
        """Explain why a strategy was chosen"""
        # Check constraint count (matching select_strategy logic)
        num_constraints = len(spec.constraints) if hasattr(spec, 'constraints') and spec.constraints else 0

        # Explain constraint-driven choice
        if num_constraints >= 3 or (num_constraints >= 1 and len(spec.objects) >= 3):
            domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()
            if domain_str in ['mechanics', 'electrostatics']:
                return f"Problem has {num_constraints} constraints - using symbolic physics approach"
            return f"Problem has {num_constraints} constraints - using constraint-based Z3 solver"

        # Explain complexity-driven choice
        if complexity < 0.15:
            return "Low complexity with few constraints - heuristic approach sufficient"
        elif complexity < 0.6:
            domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()
            if domain_str in ['mechanics', 'electrostatics']:
                return "Medium complexity physics problem - symbolic approach"
            return "Medium complexity - constraint-based approach"
        else:
            return "High complexity - hybrid approach combining multiple methods"

    # ========== Objective Selection ==========

    def select_objectives(self, spec: CanonicalProblemSpec) -> List[LayoutObjective]:
        """
        Select optimization objectives based on problem

        Args:
            spec: Problem specification

        Returns:
            List of LayoutObjective
        """
        objectives = []

        # Always minimize overlap
        objectives.append(LayoutObjective.MINIMIZE_OVERLAP)

        # Maximize clarity for complex problems
        if len(spec.objects) > 5:
            objectives.append(LayoutObjective.MAXIMIZE_CLARITY)

        # Check for symmetry in geometry
        geometry = spec.geometry
        if geometry and geometry.get('symmetry'):
            objectives.append(LayoutObjective.MAXIMIZE_SYMMETRY)

        # Balance composition for diagrams with many objects
        if len(spec.objects) > 8:
            objectives.append(LayoutObjective.BALANCE_COMPOSITION)

        return objectives

    # ========== Constraint Formulation ==========

    def formulate_constraints(self, spec: CanonicalProblemSpec, strategy: PlanningStrategy) -> List[LayoutConstraint]:
        """
        Formulate layout constraints

        Args:
            spec: Problem specification
            strategy: Selected planning strategy

        Returns:
            List of LayoutConstraint
        """
        constraints = []

        # 1. Canvas bounds constraints (REQUIRED)
        canvas_width = self.default_canvas_size[0]
        canvas_height = self.default_canvas_size[1]
        margins = self.default_margins

        for obj in spec.objects:
            obj_id = obj.get('id', '')
            if obj_id:
                constraint = create_bounds_constraint(
                    obj_id,
                    min_x=margins[3],  # left margin
                    max_x=canvas_width - margins[1],  # right margin
                    min_y=margins[0],  # top margin
                    max_y=canvas_height - margins[2],  # bottom margin
                    priority=ConstraintPriority.REQUIRED
                )
                constraints.append(constraint)

        # 2. No overlap constraint (REQUIRED)
        object_ids = [obj.get('id', '') for obj in spec.objects if obj.get('id')]
        if len(object_ids) > 1:
            no_overlap = create_no_overlap_constraint(
                object_ids,
                margin=10.0,
                priority=ConstraintPriority.REQUIRED
            )
            constraints.append(no_overlap)

        # 3. Distance constraints from relationships
        for rel in spec.relationships:
            subject = rel.get('subject', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', '').lower()

            if subject and target:
                # Connected objects should be close
                if 'connect' in rel_type or 'adjacent' in rel_type:
                    constraint = create_distance_constraint(
                        subject, target,
                        distance=100.0,  # pixels
                        priority=ConstraintPriority.HIGH
                    )
                    constraints.append(constraint)

        # 4. Geometry constraints
        geometry = spec.geometry
        if geometry:
            geom_constraints = self._formulate_geometry_constraints(spec, geometry)
            constraints.extend(geom_constraints)

        # 5. Explicit constraints from spec
        for cons in spec.constraints:
            layout_constraint = self._convert_spec_constraint(cons)
            if layout_constraint:
                constraints.append(layout_constraint)

        return constraints

    def _formulate_geometry_constraints(self, spec: CanonicalProblemSpec, geometry: Dict) -> List[LayoutConstraint]:
        """Formulate constraints based on geometry"""
        constraints = []

        shape = geometry.get('shape', '')
        object_ids = [obj.get('id', '') for obj in spec.objects if obj.get('id')]

        # Square arrangement
        if shape == 'square' and len(object_ids) == 4:
            # Objects should be at corners of square
            alignment_constraint = create_alignment_constraint(
                [object_ids[0], object_ids[1]],
                axis='horizontal',
                priority=ConstraintPriority.HIGH
            )
            constraints.append(alignment_constraint)

        # Linear arrangement
        elif shape == 'linear':
            alignment_constraint = create_alignment_constraint(
                object_ids,
                axis='horizontal',
                priority=ConstraintPriority.HIGH
            )
            constraints.append(alignment_constraint)

        return constraints

    def _convert_spec_constraint(self, cons: Dict) -> Optional[LayoutConstraint]:
        """Convert a specification constraint to a layout constraint"""
        cons_type = cons.get('type', '')
        objects = cons.get('objects', [])

        if not objects:
            return None

        # Map constraint types
        if cons_type in ['no_overlap', 'distance', 'alignment_horizontal', 'alignment_vertical', 'symmetry']:
            return LayoutConstraint(
                type=cons_type,
                objects=objects,
                parameters=cons.get('parameters', {}),
                priority=ConstraintPriority.MEDIUM
            )

        return None

    # ========== Domain-Specific Constraints ==========

    def add_domain_constraints(self, spec: CanonicalProblemSpec) -> List[LayoutConstraint]:
        """
        Add domain-specific layout constraints

        Args:
            spec: Problem specification

        Returns:
            List of domain-specific constraints
        """
        domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()

        if domain_str == 'mechanics':
            return self._add_mechanics_constraints(spec)
        elif domain_str in ['electrostatics', 'current_electricity']:
            return self._add_electrostatics_constraints(spec)
        else:
            return []

    def _add_mechanics_constraints(self, spec: CanonicalProblemSpec) -> List[LayoutConstraint]:
        """Add constraints specific to mechanics problems"""
        constraints = []

        # Find body and force objects
        body_ids = []
        force_ids = []

        for obj in spec.objects:
            obj_type = obj.get('type', '').lower()
            obj_id = obj.get('id', '')

            if 'body' in obj_type or 'mass' in obj_type or 'block' in obj_type:
                body_ids.append(obj_id)
            elif 'force' in obj_type:
                force_ids.append(obj_id)

        # Forces should be near the body they act on
        for force_id in force_ids:
            for rel in spec.relationships:
                if rel.get('subject') == force_id:
                    target = rel.get('target', '')
                    if target in body_ids:
                        constraint = create_distance_constraint(
                            force_id, target,
                            distance=80.0,
                            priority=ConstraintPriority.HIGH
                        )
                        constraints.append(constraint)

        return constraints

    def _add_electrostatics_constraints(self, spec: CanonicalProblemSpec) -> List[LayoutConstraint]:
        """Add constraints specific to electrostatics problems"""
        constraints = []

        # Charges should have minimum separation
        charge_ids = []
        for obj in spec.objects:
            obj_type = obj.get('type', '').lower()
            if 'charge' in obj_type or 'particle' in obj_type:
                charge_ids.append(obj.get('id', ''))

        # Add minimum distance between charges
        for i, charge1 in enumerate(charge_ids):
            for charge2 in charge_ids[i + 1:]:
                if charge1 and charge2:
                    constraint = create_distance_constraint(
                        charge1, charge2,
                        distance=120.0,
                        priority=ConstraintPriority.HIGH
                    )
                    constraints.append(constraint)

        return constraints

    # ========== Layout Hints ==========

    def generate_layout_hints(self, spec: CanonicalProblemSpec) -> Dict[str, Any]:
        """
        Generate layout hints for the layout engine

        Args:
            spec: Problem specification

        Returns:
            Dict of layout hints
        """
        hints = {}

        domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()

        # Domain-specific hints
        if domain_str == 'mechanics':
            hints['preferred_orientation'] = 'horizontal'
            hints['gravity_direction'] = 'down'
            hints['body_position'] = 'center'

        elif domain_str in ['electrostatics', 'current_electricity']:
            hints['preferred_orientation'] = 'symmetric'
            hints['charge_spacing'] = 'equal'

        # Geometry hints
        geometry = spec.geometry
        if geometry:
            hints['geometry_shape'] = geometry.get('shape', 'free')
            if 'symmetry' in geometry:
                hints['symmetry_axis'] = geometry.get('symmetry')

        # Object count hints
        object_count = len(spec.objects)
        if object_count <= 3:
            hints['layout_style'] = 'simple'
        elif object_count <= 8:
            hints['layout_style'] = 'moderate'
        else:
            hints['layout_style'] = 'complex'

        return hints

    # ========== Property Graph-Driven Planning (NEW - Roadmap Compliant) ==========

    def plan_from_property_graph(self,
                                 property_graph,  # PropertyGraph type
                                 problem_text: str,
                                 domain: Optional[str] = None) -> DiagramPlan:
        """
        Create diagram plan FROM property graph (roadmap-compliant architecture)

        This is the NEW primary planning method that implements the 5-stage pipeline:
        1. EntityExtractor: Extract drawable entities from graph
        2. RelationMapper: Map graph edges to visual relations
        3. ConstraintGenerator: Generate layout constraints
        4. LayoutPlanner: Solve constraints with Z3/SymPy
        5. StyleAssigner: Assign visual styles

        Args:
            property_graph: PropertyGraph built from NLP tools
            problem_text: Original request (for context)
            domain: Optional domain hint (electronics, mechanics, etc.)

        Returns:
            DiagramPlan ready for rendering (without LLM extraction)
        """
        from core.property_graph import PropertyGraph, NodeType, EdgeType

        print(f"\n{'─'*70}")
        print(f"🧠 PROPERTY GRAPH-DRIVEN PLANNING (5-Stage Pipeline)")
        print(f"{'─'*70}\n")

        # Initialize plan
        plan = DiagramPlan(
            original_spec=None,  # No LLM-extracted spec needed
            complexity_score=0.0,
            strategy=PlanningStrategy.CONSTRAINT_BASED,
            canvas_width=self.default_canvas_size[0],
            canvas_height=self.default_canvas_size[1],
            margins=self.default_margins.copy()
        )

        # Store metadata
        plan.metadata = {
            'planning_mode': 'property_graph_driven',
            'original_request': problem_text,
            'domain_hint': domain
        }

        # STAGE 1: EntityExtractor
        print("Stage 1/5: Entity Extraction")
        entities = self._extract_entities_from_graph(property_graph, domain)
        plan.extracted_entities = entities
        plan.log_planning_step('entity_extraction', {
            'entity_count': len(entities),
            'types': list(set(e.get('type', 'unknown') for e in entities))
        })
        print(f"  ✅ Extracted {len(entities)} drawable entities\n")

        # STAGE 2: RelationMapper
        print("Stage 2/5: Relation Mapping")
        relations = self._map_relations_from_graph(property_graph, entities)
        plan.extracted_relations = relations
        plan.log_planning_step('relation_mapping', {
            'relation_count': len(relations),
            'types': list(set(r.get('type', 'unknown') for r in relations))
        })
        print(f"  ✅ Mapped {len(relations)} relations\n")

        # STAGE 3: ConstraintGenerator
        print("Stage 3/5: Constraint Generation")
        constraints = self._generate_constraints_from_graph(entities, relations, domain)
        for constraint in constraints:
            plan.add_global_constraint(constraint)
        plan.log_planning_step('constraint_generation', {
            'constraint_count': len(constraints),
            'types': list(set(c.type for c in constraints))
        })
        print(f"  ✅ Generated {len(constraints)} layout constraints\n")

        # STAGE 4: LayoutPlanner
        print("Stage 4/5: Layout Planning (Constraint Solving)")
        layout_hints = self._plan_layout_with_solver(entities, constraints, domain)
        plan.layout_hints = layout_hints
        plan.log_planning_step('layout_planning', {
            'solver_used': layout_hints.get('solver', 'heuristic'),
            'positions_assigned': len(layout_hints.get('positions', {})),
            'z3_used': layout_hints.get('z3_used', False),
            'sympy_used': layout_hints.get('sympy_used', False)
        })
        print(f"  ✅ Layout planned using {layout_hints.get('solver', 'heuristic')} solver\n")

        # STAGE 5: StyleAssigner
        print("Stage 5/5: Style Assignment")
        styles = self._assign_styles_from_graph(entities, domain)
        plan.style_hints = styles
        plan.log_planning_step('style_assignment', {
            'styles_assigned': len(styles)
        })
        print(f"  ✅ Assigned styles for {len(styles)} entities\n")

        # Assess complexity from generated plan
        plan.complexity_score = self._assess_complexity_from_graph_plan(
            entities, relations, constraints
        )
        print(f"Plan Complexity: {plan.complexity_score:.2f}")
        print(f"{'─'*70}\n")

        return plan

    def _extract_entities_from_graph(self, property_graph, domain: Optional[str]) -> List[Dict]:
        """
        STAGE 1: Extract drawable entities from property graph

        Filters out abstract concepts and non-visual nodes, keeping only
        entities that should be rendered in the diagram.
        """
        from core.property_graph import NodeType

        entities = []
        all_nodes = property_graph.get_all_nodes()

        for node in all_nodes:
            # Skip non-visual concepts
            if not self._is_drawable_node(node):
                continue

            # Convert GraphNode to entity dict
            entity = {
                'id': node.id,
                'type': node.type.value if hasattr(node.type, 'value') else str(node.type),
                'label': node.label,
                'properties': node.properties.copy() if node.properties else {},
                'primitive_hint': self._get_primitive_hint_from_node(node, domain),
                'source': node.metadata.get('source', 'unknown') if node.metadata else 'unknown'
            }

            entities.append(entity)

        return entities

    def _is_drawable_node(self, node) -> bool:
        """Check if a graph node represents a drawable entity"""
        from core.property_graph import NodeType
        import re

        # Skip abstract concepts
        abstract_types = {NodeType.CONCEPT, NodeType.LAW, NodeType.PROCESS, NodeType.EVENT}
        if hasattr(node.type, 'value'):
            if node.type in abstract_types:
                return False
        else:
            node_type_str = str(node.type).lower()
            if any(abs_type in node_type_str for abs_type in ['concept', 'law', 'process', 'event']):
                return False

        label_lower = node.label.lower()

        # Skip pure spatial descriptors (unless they modify a component)
        spatial_only = ['left', 'right', 'top', 'bottom', 'half', 'side', 'region']
        if any(spatial in label_lower for spatial in spatial_only):
            # Check if it's ONLY a spatial descriptor (e.g., "left half" vs. "left plate")
            words = label_lower.split()
            if len(words) <= 2 and all(any(sp in w for sp in spatial_only) for w in words):
                return False

        # Skip pure measurements (e.g., "12 mm", "100 ohm", "5 V")
        if re.match(r'^[\d.]+\s*(mm|cm|m|km|v|a|ω|ohm|f|h|s|hz)', label_lower):
            return False

        # Skip pure symbols/variables without context (e.g., "κ₃", "ε₀")
        if re.match(r'^[α-ωΑ-Ω][₀-₉]*$', node.label):
            return False

        # Skip coordinating words and conjunctions
        if label_lower in ['and', 'or', 'with', 'in', 'on', 'at', 'to', 'from', 'as', 'is', 'be']:
            return False

        # Check if label suggests physical object
        physical_indicators = [
            # Electronics & Electromagnetism
            'battery', 'resistor', 'capacitor', 'inductor', 'switch', 'wire', 'led',
            'transistor', 'diode', 'voltage', 'current', 'circuit',
            'plate', 'dielectric', 'electrode', 'conductor', 'insulator',
            'coil', 'solenoid', 'transformer', 'fuse', 'ground',
            # Mechanics
            'mass', 'block', 'spring', 'pulley', 'rope', 'force', 'weight',
            'wheel', 'axle', 'lever', 'incline', 'pendulum', 'cart',
            'surface', 'floor', 'wall', 'ceiling',
            # Chemistry
            'molecule', 'atom', 'bond', 'element', 'compound', 'ion',
            'electron', 'proton', 'neutron', 'nucleus',
            # Biology
            'cell', 'organ', 'tissue', 'protein', 'dna', 'membrane',
            'enzyme', 'receptor', 'channel',
            # Math/Geometry
            'point', 'line', 'angle', 'triangle', 'circle', 'rectangle',
            'vector', 'ray', 'segment', 'plane',
            # Optics
            'lens', 'mirror', 'prism', 'ray', 'beam', 'light',
            'source', 'screen', 'aperture'
        ]

        return any(indicator in label_lower for indicator in physical_indicators)

    def _get_primitive_hint_from_node(self, node, domain: Optional[str]) -> Optional[str]:
        """Get primitive library query hint from node"""
        label_lower = node.label.lower()

        # Electronics & Electromagnetism
        if 'battery' in label_lower:
            return 'battery_symbol'
        elif 'resistor' in label_lower:
            return 'resistor_zigzag'
        elif 'capacitor' in label_lower:
            return 'capacitor_parallel_plates'
        elif 'switch' in label_lower:
            return 'switch_spst'
        elif 'dielectric' in label_lower:
            return 'dielectric_material'
        elif 'plate' in label_lower:
            return 'conductor_plate'
        elif 'wire' in label_lower or 'conductor' in label_lower:
            return 'wire'

        # Mechanics
        elif 'spring' in label_lower:
            return 'spring_coil'
        elif 'pulley' in label_lower:
            return 'pulley_wheel'
        elif 'mass' in label_lower or 'block' in label_lower:
            return 'mass_block'

        # Optics
        elif 'lens' in label_lower:
            return 'lens'
        elif 'mirror' in label_lower:
            return 'mirror'

        # Default: use label as hint
        return label_lower.replace(' ', '_')

    def _map_relations_from_graph(self, property_graph, entities: List[Dict]) -> List[Dict]:
        """
        STAGE 2: Map graph edges to visual relations

        Converts property graph edges into diagram relations that will be
        rendered as connections, arrows, etc.
        """
        from core.property_graph import EdgeType

        relations = []
        entity_ids = {e['id'] for e in entities}
        all_edges = property_graph.get_edges()

        for edge in all_edges:
            # Only include relations between drawable entities
            if edge.source not in entity_ids or edge.target not in entity_ids:
                continue

            # Convert EdgeType to visual relation type
            visual_type = self._map_edge_type_to_visual(edge.type, edge.label)

            relation = {
                'source_id': edge.source,
                'target_id': edge.target,
                'type': visual_type,
                'label': edge.label,
                'properties': edge.metadata.copy() if edge.metadata else {},
                'edge_type': edge.type.value if hasattr(edge.type, 'value') else str(edge.type)
            }

            relations.append(relation)

        # Infer implicit relations (e.g., series connections, force directions)
        implicit_relations = self._infer_implicit_relations_from_graph(entities, relations)
        relations.extend(implicit_relations)

        return relations

    def _map_edge_type_to_visual(self, edge_type, label: str) -> str:
        """Map graph edge type to visual relation type"""
        from core.property_graph import EdgeType

        edge_type_value = edge_type.value if hasattr(edge_type, 'value') else str(edge_type)

        # Electrical connections
        if 'connected' in edge_type_value.lower() or 'connected' in label.lower():
            if 'series' in label.lower():
                return 'SERIES_CONNECTION'
            elif 'parallel' in label.lower():
                return 'PARALLEL_CONNECTION'
            else:
                return 'WIRE_CONNECTION'

        # Mechanical connections
        elif 'attached' in edge_type_value.lower() or 'attached' in label.lower():
            return 'MECHANICAL_ATTACHMENT'

        # Force relations
        elif 'acts' in edge_type_value.lower() or 'force' in label.lower():
            return 'FORCE_ARROW'

        # Spatial relations
        elif any(spatial in edge_type_value.lower() for spatial in ['above', 'below', 'left', 'right']):
            return 'SPATIAL_RELATION'

        # Default
        return 'CONNECTION'

    def _infer_implicit_relations_from_graph(self, entities: List[Dict], relations: List[Dict]) -> List[Dict]:
        """Infer implicit relations not explicitly in graph"""
        implicit = []

        # Example: Infer series connections in circuits
        # If A connects to B and B connects to C, and they're all in series, add A→C relation
        # This is domain-specific logic that can be expanded

        return implicit

    def _generate_constraints_from_graph(self, entities: List[Dict],
                                        relations: List[Dict],
                                        domain: Optional[str]) -> List[LayoutConstraint]:
        """
        STAGE 3: Generate layout constraints from entities and relations

        Creates geometric, spatial, and domain-specific constraints that will
        guide the layout solver.
        """
        constraints = []

        # 1. Geometric constraints from relations
        for rel in relations:
            rel_type = rel['type']
            source_id = rel['source_id']
            target_id = rel['target_id']

            if rel_type in ['WIRE_CONNECTION', 'SERIES_CONNECTION']:
                # Connected entities should be close
                constraints.append(create_distance_constraint(
                    source_id, target_id,
                    distance=100.0,  # Average of min/max
                    priority=ConstraintPriority.HIGH
                ))

            elif rel_type == 'SERIES_CONNECTION':
                # Series connections should be aligned
                constraints.append(create_alignment_constraint(
                    source_id, target_id,
                    axis='horizontal',
                    priority=ConstraintPriority.HIGH
                ))

            elif rel_type == 'FORCE_ARROW':
                # Force should point away from source
                constraints.append(LayoutConstraint(
                    type='directional',
                    objects=[source_id, target_id],
                    parameters={'direction': 'away'},
                    priority=ConstraintPriority.HIGH
                ))

        # 2. Domain-specific constraints
        if domain and 'electr' in domain.lower():
            # Closed loop constraint for circuits
            if self._forms_closed_loop_from_relations(relations):
                loop_entities = self._get_loop_entities_from_relations(relations)
                constraints.append(LayoutConstraint(
                    type='closed_loop',
                    objects=loop_entities,
                    parameters={'domain_rule': 'Kirchhoff'},
                    priority=ConstraintPriority.REQUIRED
                ))

        # 3. No-overlap constraints (all entity pairs)
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                constraints.append(create_no_overlap_constraint(e1['id'], e2['id']))

        # 4. Bounds constraints (all entities within canvas)
        for entity in entities:
            constraints.append(create_bounds_constraint(
                entity['id'], 0, 0,
                self.default_canvas_size[0],
                self.default_canvas_size[1]
            ))

        return constraints

    def _forms_closed_loop_from_relations(self, relations: List[Dict]) -> bool:
        """Check if relations form a closed loop"""
        if len(relations) < 3:
            return False

        # Build adjacency graph
        graph = {}
        for rel in relations:
            source = rel['source_id']
            target = rel['target_id']
            if source not in graph:
                graph[source] = []
            if target not in graph:
                graph[target] = []
            graph[source].append(target)
            graph[target].append(source)

        # Check if any node has degree >= 2 (suggests loop)
        for node, neighbors in graph.items():
            if len(neighbors) >= 2:
                return True

        return False

    def _get_loop_entities_from_relations(self, relations: List[Dict]) -> List[str]:
        """Get entity IDs that form the loop"""
        entity_ids = set()
        for rel in relations:
            entity_ids.add(rel['source_id'])
            entity_ids.add(rel['target_id'])
        return list(entity_ids)

    def _plan_layout_with_solver(self, entities: List[Dict],
                                 constraints: List[LayoutConstraint],
                                 domain: Optional[str]) -> Dict[str, Any]:
        """
        STAGE 4: Plan layout using constraint solving (Z3/SymPy/heuristic)

        This is where Z3 or SymPy actually gets used for constraint-based layout.
        """
        layout = {
            'solver': 'heuristic',
            'positions': {},
            'constraints_satisfied': [],
            'z3_used': False,
            'sympy_used': False
        }

        # Determine solver based on complexity and constraint types
        num_entities = len(entities)
        has_complex_constraints = any(
            c.type in ['closed_loop', 'directional', 'alignment']
            for c in constraints
        )

        if num_entities <= 5 and not has_complex_constraints:
            # Simple heuristic layout
            solver_type = 'heuristic'
        elif num_entities <= 15 or has_complex_constraints:
            # Use Z3 SMT solver
            solver_type = 'z3'
        else:
            # Use SymPy for symbolic solving
            solver_type = 'sympy'

        layout['solver'] = solver_type

        if solver_type == 'z3':
            try:
                from core.z3_layout_solver import Z3LayoutSolver
                z3_solver = Z3LayoutSolver()

                solution = z3_solver.solve_layout(entities, constraints)

                if solution and hasattr(solution, 'positions'):
                    layout['positions'] = solution.positions
                    layout['constraints_satisfied'] = getattr(solution, 'satisfied_constraints', [])
                    layout['z3_used'] = True
                else:
                    # Fallback to heuristic
                    layout['positions'] = self._heuristic_layout_from_graph(entities, constraints)
                    layout['solver'] = 'heuristic_fallback'
            except Exception as e:
                print(f"    ⚠️  Z3 solver failed: {e}, falling back to heuristic")
                layout['positions'] = self._heuristic_layout_from_graph(entities, constraints)
                layout['solver'] = 'heuristic_fallback'

        elif solver_type == 'sympy':
            try:
                from core.sympy_solver import SymPyLayoutSolver
                sympy_solver = SymPyLayoutSolver()

                solution = sympy_solver.solve_geometric_layout(entities, constraints)

                if solution and hasattr(solution, 'positions'):
                    layout['positions'] = solution.positions
                    layout['sympy_used'] = True
                else:
                    layout['positions'] = self._heuristic_layout_from_graph(entities, constraints)
                    layout['solver'] = 'heuristic_fallback'
            except Exception as e:
                print(f"    ⚠️  SymPy solver failed: {e}, falling back to heuristic")
                layout['positions'] = self._heuristic_layout_from_graph(entities, constraints)
                layout['solver'] = 'heuristic_fallback'

        else:
            # Heuristic layout
            layout['positions'] = self._heuristic_layout_from_graph(entities, constraints)

        return layout

    def _heuristic_layout_from_graph(self, entities: List[Dict],
                                     constraints: List[LayoutConstraint]) -> Dict[str, Tuple[float, float]]:
        """Simple heuristic layout (fallback)"""
        positions = {}

        # Simple grid layout
        grid_cols = math.ceil(math.sqrt(len(entities)))
        spacing = 150

        for idx, entity in enumerate(entities):
            row = idx // grid_cols
            col = idx % grid_cols

            x = 100 + col * spacing
            y = 100 + row * spacing

            positions[entity['id']] = (x, y)

        return positions

    def _assign_styles_from_graph(self, entities: List[Dict],
                                  domain: Optional[str]) -> Dict[str, Dict]:
        """
        STAGE 5: Assign visual styles based on entity types and domain

        Determines colors, sizes, shapes, symbols for each entity.
        """
        styles = {}

        for entity in entities:
            entity_type = entity.get('type', 'object')
            label_lower = entity.get('label', '').lower()

            # Base style
            style = {
                'color': self._get_color_for_entity_type(entity_type, domain),
                'size': self._get_size_for_entity_type(entity_type),
                'shape': self._get_shape_for_entity_type(entity_type),
                'stroke_width': 2,
                'font_size': 14,
                'font_family': 'Arial, sans-serif'
            }

            # Domain-specific symbol overrides
            if domain and 'electr' in domain.lower():
                if 'battery' in label_lower:
                    style['symbol'] = 'battery_symbol'
                    style['color'] = '#2ecc71'  # Green
                elif 'resistor' in label_lower:
                    style['symbol'] = 'resistor_zigzag'
                    style['color'] = '#e67e22'  # Orange
                elif 'capacitor' in label_lower:
                    style['symbol'] = 'capacitor_parallel'
                    style['color'] = '#3498db'  # Blue
                elif 'switch' in label_lower:
                    style['symbol'] = 'switch_spst'
                    style['color'] = '#95a5a6'  # Gray

            elif domain and 'mech' in domain.lower():
                if 'spring' in label_lower:
                    style['symbol'] = 'spring_coil'
                    style['color'] = '#9b59b6'  # Purple
                elif 'mass' in label_lower or 'block' in label_lower:
                    style['symbol'] = 'mass_block'
                    style['color'] = '#34495e'  # Dark gray
                    style['shape'] = 'rectangle'

            styles[entity['id']] = style

        return styles

    def _get_color_for_entity_type(self, entity_type: str, domain: Optional[str]) -> str:
        """Get color based on entity type"""
        color_map = {
            'object': '#3498db',      # Blue
            'component': '#e74c3c',   # Red
            'force': '#e67e22',       # Orange
            'quantity': '#9b59b6',    # Purple
            'parameter': '#1abc9c',   # Teal
        }
        return color_map.get(entity_type, '#34495e')  # Default dark gray

    def _get_size_for_entity_type(self, entity_type: str) -> int:
        """Get size based on entity type"""
        size_map = {
            'object': 60,
            'component': 50,
            'force': 80,
            'quantity': 40,
            'parameter': 30
        }
        return size_map.get(entity_type, 50)

    def _get_shape_for_entity_type(self, entity_type: str) -> str:
        """Get shape based on entity type"""
        shape_map = {
            'object': 'rectangle',
            'component': 'circle',
            'force': 'arrow',
            'quantity': 'ellipse',
            'parameter': 'circle'
        }
        return shape_map.get(entity_type, 'rectangle')

    def _assess_complexity_from_graph_plan(self, entities: List[Dict],
                                           relations: List[Dict],
                                           constraints: List[LayoutConstraint]) -> float:
        """Assess complexity from graph-based plan"""
        score = 0.0

        # Entity count (0-0.3)
        score += min(len(entities) / 20.0, 1.0) * 0.3

        # Relation count (0-0.3)
        score += min(len(relations) / 15.0, 1.0) * 0.3

        # Constraint count (0-0.2)
        score += min(len(constraints) / 10.0, 1.0) * 0.2

        # Constraint complexity (0-0.2)
        complex_constraint_types = {'closed_loop', 'directional', 'alignment', 'symmetry'}
        complex_count = sum(1 for c in constraints if c.type in complex_constraint_types)
        score += min(complex_count / 5.0, 1.0) * 0.2

        return min(score, 1.0)

    # ========== Utility Methods ==========

    def __repr__(self) -> str:
        """String representation"""
        return f"DiagramPlanner(config={self.config})"
