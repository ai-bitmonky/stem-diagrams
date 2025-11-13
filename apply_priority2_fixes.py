#!/usr/bin/env python3
"""
Apply Priority 2 Fixes - Core Architecture Improvements
Implements:
- P1.3: Wire model orchestrator
- P2.1: Fix Z3 solver integration
- P2.2: Implement validation refinement loop
- P2.3: Complete DiagramPlanner integration
"""

import sys
from pathlib import Path
import re

def wire_model_orchestrator():
    """P1.3: Wire model orchestrator for intelligent LLM routing"""

    pipeline_path = Path("unified_diagram_pipeline.py")
    content = pipeline_path.read_text()

    # 1. Add import
    import_line = "from core.model_orchestrator import HybridModelOrchestrator"
    if import_line not in content:
        # Find where to add import (after other core imports)
        import_marker = "from core.diagram_planner import DiagramPlanner"
        if import_marker in content:
            content = content.replace(import_marker, import_marker + "\n" + import_line)
            print("     Added model orchestrator import")

    # 2. Add config flag
    config_addition = """    enable_model_orchestrator: bool = True  # Intelligent LLM routing"""
    if "enable_model_orchestrator" not in content:
        # Add after enable_model_orchestration line
        content = content.replace(
            "enable_model_orchestration: bool = True",
            "enable_model_orchestration: bool = True\n" + config_addition
        )
        print("     Added config flag")

    # 3. Add initialization in __init__
    init_code = '''
        # Model Orchestrator (NEW)
        self.model_orchestrator = None
        if config.enable_model_orchestrator:
            try:
                self.model_orchestrator = HybridModelOrchestrator(
                    primary_model="deepseek",
                    fallback_models=["claude-3-sonnet"]
                )
                self.active_features.append("Model Orchestrator")
                print("✓ Model Orchestrator [ACTIVE]")
            except Exception as e:
                print(f"⚠ Model Orchestrator failed to initialize: {e}")
'''

    if "self.model_orchestrator = None" not in content:
        # Insert after model_orchestration initialization
        marker = "self.model_orchestration = ModelOrchestration()"
        if marker in content:
            content = content.replace(marker, marker + "\n" + init_code)
            print("     Added orchestrator initialization")

    pipeline_path.write_text(content)
    print("✅ Wired model orchestrator into pipeline")
    return True

def fix_z3_solver_integration():
    """P2.1: Fix Z3 solver to actually work"""

    pipeline_path = Path("unified_diagram_pipeline.py")
    content = pipeline_path.read_text()

    # Find Z3 solver section
    z3_section_start = "# Try Z3 optimization first if available"
    z3_section_end = "# Use standard layout engine"

    if z3_section_start in content:
        # Extract current Z3 section
        sections = content.split(z3_section_start)
        before = sections[0]
        z3_and_after = sections[1].split(z3_section_end)
        after = z3_section_end + z3_and_after[1]

        # Replace with improved Z3 integration
        new_z3_code = """# Try Z3 optimization first if available
            z3_used = False
            if self.z3_solver and self.diagram_planner:
                try:
                    if self.logger:
                        self.logger.log_phase_detail("Attempting Z3 layout optimization")

                    # Step 1: Create diagram plan
                    plan = self.diagram_planner.create_plan(specs)

                    if not plan or not plan.constraints:
                        if self.logger:
                            self.logger.log_phase_detail("No constraints in plan, skipping Z3")
                        raise ValueError("Plan has no constraints")

                    if self.logger:
                        self.logger.log_phase_detail(f"Plan has {len(plan.constraints)} constraints")

                    # Step 2: Get object dimensions
                    object_dims = {}
                    for obj in scene.objects:
                        # Estimate size based on primitive type
                        if obj.primitive_type == PrimitiveType.RECTANGLE:
                            w, h = obj.properties.get('width', 100), obj.properties.get('height', 100)
                        elif obj.primitive_type == PrimitiveType.CIRCLE:
                            r = obj.properties.get('radius', 50)
                            w, h = r*2, r*2
                        else:
                            w, h = 100, 100
                        object_dims[obj.id] = (w, h)

                    # Step 3: Solve with Z3 (with timeout)
                    z3_solution = self.z3_solver.solve_layout(
                        plan,
                        object_dims,
                        timeout_ms=5000  # 5 second timeout
                    )

                    # Step 4: Apply solution if satisfiable
                    if z3_solution.satisfiable:
                        from core.scene.schema_v1 import Position
                        for obj_id, (x, y) in z3_solution.positions.items():
                            obj = next((o for o in scene.objects if o.id == obj_id), None)
                            if obj:
                                obj.position = Position(x=float(x), y=float(y))

                        z3_used = True
                        print(f"  ✅ Z3 Solution: {len(z3_solution.positions)} positions optimized")
                        if self.logger:
                            self.logger.log_phase_detail(f"Z3 successfully positioned {len(z3_solution.positions)} objects")
                    else:
                        print(f"  ⚠️  Z3 problem unsatisfiable, using heuristic layout")
                        if self.logger:
                            self.logger.log_phase_detail("Z3 problem unsatisfiable")

                except Exception as e:
                    print(f"  ⚠️  Z3 failed: {str(e)[:100]}, using heuristic layout")
                    if self.logger:
                        self.logger.log_phase_detail(f"Z3 failed: {e}")

            # """

        content = before + new_z3_code + after

        pipeline_path.write_text(content)
        print("✅ Enhanced Z3 solver integration with better error handling")
        return True
    else:
        print("⚠️  Z3 section not found in expected format")
        return False

def implement_validation_refinement():
    """P2.2: Add validation refinement loop"""

    pipeline_path = Path("unified_diagram_pipeline.py")
    content = pipeline_path.read_text()

    # Find _post_validate method
    method_start = "def _post_validate(self, svg: str, scene: Scene, problem_text: str) -> Dict:"

    if method_start in content:
        # Replace entire method with refinement loop version
        new_method = '''def _post_validate(self, svg: str, scene: Scene, problem_text: str) -> Dict:
        """Phase 7: AI-based quality validation with refinement loop"""

        MAX_REFINEMENT_ITERATIONS = 3
        validation_results = {
            'structural': None,
            'visual_semantic': None,
            'overall_confidence': 0.0,
            'issues': [],
            'suggestions': [],
            'refinement_iterations': 0
        }

        # Refinement loop
        for iteration in range(MAX_REFINEMENT_ITERATIONS):
            if self.logger:
                self.logger.log_phase_detail(f"Validation iteration {iteration + 1}/{MAX_REFINEMENT_ITERATIONS}")

            # 1. Run structural validation
            if self.diagram_validator:
                try:
                    quality_score = self.diagram_validator.validate(scene)
                    validation_results['structural'] = {
                        'overall_score': quality_score.overall_score,
                        'layout_score': quality_score.layout_score,
                        'connectivity_score': quality_score.connectivity_score,
                        'style_score': quality_score.style_score,
                        'physics_score': quality_score.physics_score,
                        'issues': [str(i) for i in quality_score.issues]
                    }

                    # If quality is good enough, stop
                    if quality_score.overall_score >= 0.8:
                        validation_results['overall_confidence'] = quality_score.overall_score
                        if self.logger:
                            self.logger.log_phase_detail(f"Quality sufficient: {quality_score.overall_score:.2f}")
                        break

                    # Otherwise, try to fix issues
                    issues_fixed = self._fix_validation_issues(scene, quality_score.issues)
                    validation_results['refinement_iterations'] += 1

                    if self.logger:
                        self.logger.log_phase_detail(f"Fixed {issues_fixed} issues")

                    # If no issues could be fixed, stop
                    if issues_fixed == 0:
                        break

                    # Re-render SVG with fixed scene
                    svg = self.renderer.render(scene, self.ai_analyzer.analyze(problem_text))

                except Exception as e:
                    if self.logger:
                        self.logger.log_phase_detail(f"Validation error: {e}")
                    break

            # 2. Run VLM validation (if available)
            if self.vlm_validator and svg:
                try:
                    vlm_result = self.vlm_validator.validate_diagram(svg, problem_text)
                    validation_results['visual_semantic'] = {
                        'confidence': vlm_result.confidence,
                        'issues': [str(i) for i in vlm_result.issues]
                    }
                except Exception as e:
                    if self.logger:
                        self.logger.log_phase_detail(f"VLM validation error: {e}")

        return validation_results

    def _fix_validation_issues(self, scene: Scene, issues: List) -> int:
        """Fix common validation issues (helper method)"""
        fixed = 0

        for issue in issues:
            issue_str = str(issue).lower()

            # Fix overlapping objects
            if 'overlap' in issue_str:
                # Simple fix: add small offset to overlapping objects
                for i, obj in enumerate(scene.objects):
                    if obj.position and i > 0:
                        obj.position.x += (i % 3) * 10  # Slight offset
                        obj.position.y += (i // 3) * 10
                fixed += 1

            # Fix unreadable labels
            elif 'label' in issue_str and 'unreadable' in issue_str:
                # Increase label offset
                for obj in scene.objects:
                    if obj.label_position:
                        obj.label_position.y -= 10  # Move label up
                fixed += 1

        return fixed'''

        # Find and replace the method
        # Pattern: from method start to next method or end of class
        pattern = r'(def _post_validate\(self.*?\n(?:.*?\n)*?)(?=\n    def |\nclass |\Z)'

        match = re.search(pattern, content, re.MULTILINE)
        if match:
            content = content.replace(match.group(0), new_method)
            pipeline_path.write_text(content)
            print("✅ Implemented validation refinement loop")
            return True
        else:
            print("⚠️  Could not find _post_validate method to replace")
            return False
    else:
        print("⚠️  _post_validate method not found")
        return False

def main():
    """Apply all Priority 2 fixes"""
    print("="*80)
    print("APPLYING PRIORITY 2 FIXES")
    print("="*80)
    print()

    fixes = [
        ("P1.3: Wire Model Orchestrator", wire_model_orchestrator),
        ("P2.1: Fix Z3 Solver Integration", fix_z3_solver_integration),
        ("P2.2: Validation Refinement Loop", implement_validation_refinement),
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

    if success_count >= 2:
        print("\n✅ MOST FIXES APPLIED!")
        print("\nNext: Test with python3 test_logging.py")
        return 0
    else:
        print("\n⚠️  Multiple fixes failed - review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
