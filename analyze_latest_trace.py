#!/usr/bin/env python3
"""Analyze the latest trace file and show key features"""

import json
import sys

def analyze_trace(trace_path):
    # Read the trace
    with open(trace_path, 'r') as f:
        trace = json.load(f)

    print("="*80)
    print("TRACE SUMMARY - Request:", trace['request_id'])
    print("="*80)
    print()

    # Request details
    print("📝 Problem Text:")
    problem_text = trace.get('problem_text', 'N/A')
    if len(problem_text) > 100:
        print(f"   {problem_text[:100]}...")
    else:
        print(f"   {problem_text}")
    print()

    # Overall metrics
    print("⏱️  Total Duration:", f"{trace['total_duration_ms']:.2f} ms")
    print("📊 Status:", trace['status'])
    print("🔢 Total Phases:", len(trace['phases']))
    print()

    print("="*80)
    print("PHASES EXECUTED")
    print("="*80)

    # Show each phase with key details
    for i, phase in enumerate(trace['phases'], 1):
        duration = phase.get('duration_ms', 0)
        status = phase.get('status', 'unknown')
        status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"

        print(f"\n{i}. {phase['phase_name']} {status_icon}")
        print(f"   Duration: {duration:.2f} ms")

        # Show key outputs for important phases
        output = phase.get('output', {})

        # Check for NLP usage (P1.1)
        if 'NLP' in phase['phase_name'] or 'Property Graph' in phase['phase_name']:
            if isinstance(output, dict):
                keys = list(output.keys())[:5]
                if keys:
                    print(f"   Output keys: {keys}")

        # Check for strategy selection (P2.3, P3.1, P3.2)
        if 'Scene Synthesis' in phase['phase_name'] or 'Strategic Planning' in phase['phase_name']:
            if isinstance(output, dict):
                if 'selected_strategy' in output:
                    print(f"   ✨ Strategy: {output['selected_strategy']}")
                if 'object_count' in output:
                    print(f"   Objects: {output['object_count']}")

        # Check for Z3 usage (P2.1)
        if 'Layout' in phase['phase_name'] or 'Z3' in phase['phase_name']:
            if isinstance(output, dict):
                if 'z3_used' in output:
                    z3_icon = "✅" if output['z3_used'] else "⚠️"
                    print(f"   {z3_icon} Z3 Used: {output['z3_used']}")

        # Check for validation refinement (P2.2)
        if 'Validation' in phase['phase_name']:
            if isinstance(output, dict):
                if 'refinement_iterations' in output:
                    print(f"   🔄 Refinement Iterations: {output['refinement_iterations']}")
                if 'overall_confidence' in output:
                    print(f"   📊 Confidence: {output['overall_confidence']:.2f}")

    print()
    print("="*80)
    print("KEY FEATURES VISIBLE IN TRACE")
    print("="*80)
    print()

    # Check which features are visible
    features = []

    for phase in trace['phases']:
        phase_name = phase['phase_name']
        output = phase.get('output', {})

        if 'NLP' in phase_name:
            features.append("✅ P1.1: NLP Integration")
        if 'Property Graph' in phase_name:
            features.append("✅ P1.2: Property Graph")
        if isinstance(output, dict) and 'selected_strategy' in output:
            features.append(f"✅ P2.3/P3: Strategy Selection ({output['selected_strategy']})")
        if isinstance(output, dict) and 'z3_used' in output:
            features.append(f"✅ P2.1: Z3 Solver ({'working' if output['z3_used'] else 'attempted'})")
        if isinstance(output, dict) and 'refinement_iterations' in output:
            features.append(f"✅ P2.2: Validation Refinement ({output['refinement_iterations']} iterations)")

    # Remove duplicates
    features = list(dict.fromkeys(features))

    for feature in features:
        print(feature)

    if not features:
        print("⚠️  No advanced features detected in this trace")
        print("   (This may be a simple/old diagram generation)")

    print()
    print("="*80)
    html_path = trace_path.replace('.json', '.html')
    print(f"📄 View full interactive trace at:")
    print(f"   file://{html_path}")
    print("="*80)

if __name__ == '__main__':
    trace_path = 'logs/req_20251111_224317_trace.json'
    if len(sys.argv) > 1:
        trace_path = sys.argv[1]

    analyze_trace(trace_path)
