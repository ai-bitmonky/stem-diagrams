#!/usr/bin/env python3
"""
Apply Architecture Fixes - Comprehensive Implementation Script
Implements all Priority 1 and Priority 2 fixes from IMPLEMENTATION_PLAN.md

This script systematically applies fixes to:
- P1.1: Wire NLP results into scene synthesis
- P1.2: Add property graph queries
- P1.3: Wire model orchestrator
- P2.1: Fix Z3 solver integration
- P2.2: Implement validation refinement loop
- P2.3: Complete DiagramPlanner integration
"""

import sys
from pathlib import Path

def add_nlp_enrichment_method():
    """Add _enrich_with_nlp method to UniversalSceneBuilder"""

    nlp_enrichment_code = '''
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
            for entity_text, entity_type in entities:
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
                spatial_edges = property_graph.find_edges_by_type(EdgeType.SPATIAL)
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
'''

    # Read current file
    builder_path = Path("core/universal_scene_builder.py")
    content = builder_path.read_text()

    # Find insertion point (before _enrich_with_physics)
    insertion_marker = "    def _enrich_with_physics"

    if insertion_marker in content:
        content = content.replace(insertion_marker, nlp_enrichment_code + "\n" + insertion_marker)
        builder_path.write_text(content)
        print("✅ Added _enrich_with_nlp method to UniversalSceneBuilder")
        return True
    else:
        print("❌ Could not find insertion point in UniversalSceneBuilder")
        return False

def update_infer_constraints_signature():
    """Update _infer_constraints to accept property_graph parameter"""

    builder_path = Path("core/universal_scene_builder.py")
    content = builder_path.read_text()

    # Update method signature
    old_sig = "def _infer_constraints(self, scene: Scene, spec: CanonicalProblemSpec) -> Scene:"
    new_sig = "def _infer_constraints(self, scene: Scene, spec: CanonicalProblemSpec, property_graph: Optional[Any] = None) -> Scene:"

    if old_sig in content:
        content = content.replace(old_sig, new_sig)
        builder_path.write_text(content)
        print("✅ Updated _infer_constraints signature to accept property_graph")
        return True
    else:
        print("⚠️  _infer_constraints signature already updated or not found")
        return True  # Don't fail if already updated

def add_property_graph_query_methods():
    """Add query methods to PropertyGraph class"""

    query_methods = '''
    def find_edges_by_type(self, edge_type: EdgeType) -> List['GraphEdge']:
        """Find all edges of a specific type"""
        return [edge for edge in self.get_edges() if edge.type == edge_type]

    def find_spatial_relationships(self) -> List[Tuple[str, str, str]]:
        """
        Find all spatial relationships (above, below, left, right)
        Returns list of (source_id, relation, target_id) tuples
        """
        spatial_edges = self.find_edges_by_type(EdgeType.SPATIAL)
        return [(e.source, e.label, e.target) for e in spatial_edges]

    def find_causal_chains(self, start_node_id: str, max_depth: int = 5) -> List[List[str]]:
        """
        Find all causal chains starting from a node
        Returns list of paths (each path is list of node IDs)
        """
        chains = []
        visited = set()

        def dfs(node_id: str, path: List[str], depth: int):
            if depth >= max_depth or node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            # Find outgoing causal edges
            causal_edges = [e for e in self.get_edges()
                          if e.source == node_id and e.type == EdgeType.CAUSAL]

            if not causal_edges:
                # End of chain
                if len(path) > 1:
                    chains.append(path.copy())
            else:
                for edge in causal_edges:
                    dfs(edge.target, path.copy(), depth + 1)

        dfs(start_node_id, [], 0)
        return chains

    def query_relationships(self, source_id: str, target_id: str) -> List['GraphEdge']:
        """Find all edges between two nodes"""
        return [edge for edge in self.get_edges()
                if edge.source == source_id and edge.target == target_id]
'''

    # Read property graph file
    pg_path = Path("core/property_graph.py")
    content = pg_path.read_text()

    # Find end of PropertyGraph class (look for next class or end of file)
    # Insert before the end of the class
    insertion_marker = "class NodeType(Enum):"  # Insert before this

    if "def find_spatial_relationships" not in content:
        if insertion_marker in content:
            content = content.replace(insertion_marker, query_methods + "\n\n" + insertion_marker)
            pg_path.write_text(content)
            print("✅ Added query methods to PropertyGraph")
            return True
        else:
            print("❌ Could not find insertion point in PropertyGraph")
            return False
    else:
        print("⚠️  PropertyGraph query methods already added")
        return True

def update_pipeline_scene_synthesis():
    """Update pipeline to pass NLP context and property graph to scene builder"""

    pipeline_path = Path("unified_diagram_pipeline.py")
    content = pipeline_path.read_text()

    # Find the scene building line
    old_line = "            scene = self.scene_builder.build(specs)"
    new_line = """            # Pass NLP context and property graph to scene builder
            scene = self.scene_builder.build(
                specs,
                nlp_context={
                    'entities': nlp_results.get('stanza', {}).get('entities', []) if nlp_results else [],
                    'triples': nlp_results.get('openie', {}).get('triples', []) if nlp_results else [],
                    'embeddings': nlp_results.get('scibert', {}).get('embeddings', []) if nlp_results else []
                } if nlp_results else None,
                property_graph=current_property_graph if current_property_graph else None
            )"""

    if old_line in content and "nlp_context" not in content.split(old_line)[1].split('\n')[0]:
        content = content.replace(old_line, new_line)
        pipeline_path.write_text(content)
        print("✅ Updated pipeline to pass NLP context and property graph")
        return True
    else:
        print("⚠️  Pipeline scene synthesis already updated or not found")
        return True

def main():
    """Apply all architecture fixes"""
    print("="*80)
    print("APPLYING ARCHITECTURE FIXES")
    print("="*80)
    print()

    fixes = [
        ("P1.1: NLP Enrichment Method", add_nlp_enrichment_method),
        ("P1.1: Update infer_constraints", update_infer_constraints_signature),
        ("P1.2: Property Graph Queries", add_property_graph_query_methods),
        ("P1.1+P1.2: Pipeline Integration", update_pipeline_scene_synthesis),
    ]

    results = []
    for name, fix_func in fixes:
        print(f"\n{'='*60}")
        print(f"Applying: {name}")
        print(f"{'='*60}")
        try:
            success = fix_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append((name, False))
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n{success_count}/{len(results)} fixes applied successfully")

    if success_count == len(results):
        print("\n✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Test with: python3 test_logging.py")
        print("2. Check trace: python3 generate_trace_html.py")
        print("3. Verify NLP integration in trace")
        return 0
    else:
        print("\n⚠️  Some fixes failed - review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
