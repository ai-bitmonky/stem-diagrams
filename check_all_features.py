#!/usr/bin/env python3
"""Check if all implemented features are actually enabled and running"""

import json
from pathlib import Path

# Read latest trace
trace_file = Path('logs/req_20251111_231007_trace.json')
with open(trace_file) as f:
    trace = json.load(f)

print('='*80)
print('COMPREHENSIVE FEATURE VERIFICATION')
print('='*80)
print()

issues = []
working = []

# 1. Check NLP Stack
print('1. NLP Stack (spaCy/Stanza/SciBERT/OpenIE/AMR)')
nlp_phase = next((p for p in trace['phases'] if 'NLP' in p['phase_name']), None)
if nlp_phase:
    output = nlp_phase.get('output', {})
    if output and 'openie' in output:
        print('   ✅ NLP phase active, OpenIE running')
        working.append('NLP Integration (P1.1)')
    else:
        print('   ⚠️  NLP phase exists but minimal output')
        issues.append('NLP tools may not be fully enabled')
else:
    print('   ❌ NLP phase missing')
    issues.append('NLP phase not in pipeline')

# 2. Check Property Graph
print('\n2. Property Graph (multi-source understanding)')
pg_phase = next((p for p in trace['phases'] if 'Property Graph' in p['phase_name']), None)
if pg_phase:
    output = pg_phase.get('output', {})
    nodes = output.get('nodes', 0)
    edges = output.get('edges', 0)
    if nodes > 0:
        print(f'   ✅ Property Graph built: {nodes} nodes, {edges} edges')
        working.append('Property Graph (P1.2)')
    else:
        print('   ⚠️  Property Graph empty')
        issues.append('Property Graph not populating')
else:
    print('   ❌ Property Graph phase missing')
    issues.append('Property Graph not instantiated')

# 3. Check DiagramPlanner
print('\n3. DiagramPlanner (strategic planning + complexity)')
complexity_phase = next((p for p in trace['phases'] if 'Complexity' in p['phase_name']), None)
planning_phase = next((p for p in trace['phases'] if 'Strategic Planning' in p['phase_name']), None)

planner_active = False
if complexity_phase:
    output = complexity_phase.get('output', {})
    complexity = output.get('complexity_score')
    if complexity is not None:
        print(f'   ✅ Complexity assessment: {complexity}')
        planner_active = True
    else:
        print('   ❌ Complexity score is None')
        issues.append('DiagramPlanner not calculating complexity')

if planning_phase:
    output = planning_phase.get('output', {})
    strategy = output.get('selected_strategy')
    if strategy and str(strategy).upper() != 'NONE':
        print(f'   ✅ Strategy selected: {strategy}')
        planner_active = True
    else:
        print('   ❌ Strategy is None (defaults to DIRECT)')
        issues.append('DiagramPlanner not selecting strategy')

if planner_active:
    working.append('DiagramPlanner (P2.3)')
else:
    issues.append('DiagramPlanner NOT INITIALIZED')

# 4. Check Model Orchestrator
print('\n4. Model Orchestrator (intelligent LLM routing)')
print('   ⚠️  Cannot verify from trace (infrastructure only)')
print('   Need to check initialization logs')

# 5. Check Z3 Solver
print('\n5. Z3 Solver (constraint-based layout)')
layout_phase = next((p for p in trace['phases'] if 'Layout' in p['phase_name'] or 'Z3' in p['phase_name']), None)
if layout_phase:
    output = layout_phase.get('output', {})
    z3_used = output.get('z3_used', False)
    if z3_used:
        print('   ✅ Z3 Solver USED successfully')
        working.append('Z3 Solver (P2.1)')
    else:
        print('   ⚠️  Z3 Solver attempted but not used')
        print('   (This is OK for simple problems)')
else:
    print('   ❌ Layout phase missing Z3 info')

# 6. Check Validation Refinement
print('\n6. Validation Refinement Loop (auto-fixes)')
validation_phases = [p for p in trace['phases'] if 'Validation' in p['phase_name']]
refinement_found = False
for vphase in validation_phases:
    output = vphase.get('output', {})
    if 'refinement_iterations' in output:
        iters = output['refinement_iterations']
        print(f'   ✅ Refinement loop: {iters} iterations')
        working.append('Validation Refinement (P2.2)')
        refinement_found = True
        break

if not refinement_found:
    print('   ❌ No refinement loop detected')
    issues.append('Validation refinement NOT RUNNING')

# 7. Check SymPy Verifier
print('\n7. SymPy Geometry Verifier (symbolic constraint checking)')
print('   ⚠️  Cannot verify from trace')
print('   Need to check if instantiated in pipeline')

print()
print('='*80)
print('SUMMARY')
print('='*80)
print()
print(f'✅ Working Features: {len(working)}')
for feature in working:
    print(f'   • {feature}')

print()
print(f'❌ Issues Found: {len(issues)}')
for issue in issues:
    print(f'   • {issue}')

print()
print('='*80)
print('ROOT CAUSE ANALYSIS')
print('='*80)
print()

if 'DiagramPlanner NOT INITIALIZED' in issues:
    print('🔍 CRITICAL: DiagramPlanner is not initialized')
    print()
    print('This is preventing:')
    print('  • Complexity assessment')
    print('  • Strategy selection (HIERARCHICAL/CONSTRAINT_FIRST)')
    print('  • Proper Z3 solver usage')
    print()
    print('Likely causes:')
    print('  1. Config: enable_diagram_planning = False')
    print('  2. Import failure (missing dependencies)')
    print('  3. Initialization exception')
    print()
    print('Fix: Check unified_diagram_pipeline.py initialization')

if 'Validation refinement NOT RUNNING' in issues:
    print()
    print('🔍 CRITICAL: Validation refinement loop not running')
    print()
    print('This means:')
    print('  • Diagrams are not being auto-improved')
    print('  • Issues are detected but not fixed')
    print()
    print('Fix: Check _post_validate() implementation')

print()
print('='*80)
print('RECOMMENDATIONS')
print('='*80)
print()
print('1. Enable DiagramPlanner in pipeline config')
print('2. Run a new test to generate fresh trace')
print('3. Verify all features are initialized on startup')
print('4. Check for any import or initialization errors')
