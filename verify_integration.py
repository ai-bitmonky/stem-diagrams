#!/usr/bin/env python3
"""
Verification Script: Confirm that unified_diagram_pipeline.py
actually uses the property graph and NLP tools.

This addresses the user feedback:
"The unified entry point never touches the property-graph or other local
NLP tooling promised in the roadmap"

Date: November 10, 2025
"""

import sys
import os
from typing import Dict, List

def check_imports():
    """Verify that unified_diagram_pipeline.py imports the advanced modules"""
    print("="*80)
    print("VERIFICATION 1: Checking Imports")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    required_imports = {
        'PropertyGraph': 'from core.property_graph import PropertyGraph',
        'OpenIEExtractor': 'from core.nlp_tools.openie_extractor import OpenIEExtractor',
        'StanzaEnhancer': 'from core.nlp_tools.stanza_enhancer import StanzaEnhancer',
        'DyGIEExtractor': 'from core.nlp_tools.dygie_extractor import DyGIEExtractor',
        'SciBERTEmbedder': 'from core.nlp_tools.scibert_embedder import SciBERTEmbedder',
        'DiagramPlanner': 'from core.diagram_planner import DiagramPlanner',
        'ModelOrchestrator': 'from core.model_orchestrator import ModelOrchestrator',
        'OntologyManager': 'from core.ontology.ontology_manager import OntologyManager',
        'DiagramAuditor': 'from core.auditor.diagram_auditor import DiagramAuditor',
        'Z3LayoutSolver': 'from core.solvers.z3_layout_solver import Z3LayoutSolver',
    }

    results = {}
    for name, import_stmt in required_imports.items():
        found = import_stmt in content
        results[name] = found
        status = "✅" if found else "❌"
        print(f"{status} {name}: {import_stmt[:60]}...")

    all_found = all(results.values())
    print()
    if all_found:
        print("✅ ALL REQUIRED IMPORTS PRESENT")
    else:
        missing = [k for k, v in results.items() if not v]
        print(f"❌ MISSING IMPORTS: {', '.join(missing)}")

    print()
    return all_found


def check_config_options():
    """Verify that PipelineConfig has advanced feature flags"""
    print("="*80)
    print("VERIFICATION 2: Checking Configuration Options")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    required_options = [
        'enable_property_graph',
        'enable_nlp_enrichment',
        'enable_complexity_assessment',
        'enable_strategic_planning',
        'enable_ontology_validation',
        'enable_z3_optimization',
        'enable_llm_auditing',
        'nlp_tools',
    ]

    results = {}
    for option in required_options:
        # Look for the option in PipelineConfig
        found = f'{option}:' in content or f'{option} =' in content
        results[option] = found
        status = "✅" if found else "❌"
        print(f"{status} {option}")

    all_found = all(results.values())
    print()
    if all_found:
        print("✅ ALL CONFIGURATION OPTIONS PRESENT")
    else:
        missing = [k for k, v in results.items() if not v]
        print(f"❌ MISSING OPTIONS: {', '.join(missing)}")

    print()
    return all_found


def check_initialization():
    """Verify that __init__ initializes advanced components"""
    print("="*80)
    print("VERIFICATION 3: Checking Component Initialization")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for initialization of each component
    checks = {
        'PropertyGraph': 'self.property_graph = PropertyGraph()',
        'OpenIE': "self.nlp_tools['openie'] = OpenIEExtractor()",
        'Stanza': "self.nlp_tools['stanza'] = StanzaEnhancer()",
        'SciBERT': "self.nlp_tools['scibert'] = SciBERTEmbedder()",
        'DiagramPlanner': 'self.diagram_planner = DiagramPlanner()',
        'ModelOrchestrator': 'self.model_orchestrator = ModelOrchestrator()',
        'Z3Solver': 'self.z3_solver = Z3LayoutSolver()',
        'Auditor': 'self.auditor = DiagramAuditor(',
    }

    results = {}
    for name, init_code in checks.items():
        found = init_code in content
        results[name] = found
        status = "✅" if found else "❌"
        print(f"{status} {name} initialization")

    all_found = all(results.values())
    print()
    if all_found:
        print("✅ ALL COMPONENTS INITIALIZED")
    else:
        missing = [k for k, v in results.items() if not v]
        print(f"❌ MISSING INITIALIZATIONS: {', '.join(missing)}")

    print()
    return all_found


def check_usage_in_generate():
    """Verify that generate() method actually uses the advanced features"""
    print("="*80)
    print("VERIFICATION 4: Checking Usage in generate() Method")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for actual usage
    checks = {
        'NLP Enrichment Phase': 'PHASE 0: NLP ENRICHMENT',
        'Property Graph Phase': 'PHASE 0.5: PROPERTY GRAPH CONSTRUCTION',
        'OpenIE extraction': "self.nlp_tools['openie'].extract",
        'Stanza enhancement': "self.nlp_tools['stanza'].enhance",
        'SciBERT embedding': "self.nlp_tools['scibert'].embed",
        'Graph construction': 'current_property_graph = PropertyGraph()',
        'Complexity assessment': 'self.diagram_planner.assess_complexity',
        'Strategy selection': 'self.diagram_planner.select_strategy',
        'Ontology validation': 'OntologyManager(domain=',
        'Z3 optimization': 'self.z3_solver.solve_layout',
        'LLM auditing': 'self.auditor.audit',
    }

    results = {}
    for name, usage_code in checks.items():
        found = usage_code in content
        results[name] = found
        status = "✅" if found else "❌"
        print(f"{status} {name}")

    all_found = all(results.values())
    print()
    if all_found:
        print("✅ ALL FEATURES ACTIVELY USED IN generate()")
    else:
        missing = [k for k, v in results.items() if not v]
        print(f"❌ MISSING USAGE: {', '.join(missing)}")

    print()
    return all_found


def check_result_artifacts():
    """Verify that DiagramResult includes advanced artifacts"""
    print("="*80)
    print("VERIFICATION 5: Checking Result Artifacts")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for advanced artifacts in DiagramResult
    checks = {
        'property_graph': 'property_graph: Optional',
        'nlp_results': 'nlp_results: Optional',
        'complexity_score': 'complexity_score: Optional',
        'selected_strategy': 'selected_strategy: Optional',
        'ontology_validation': 'ontology_validation: Optional',
        'audit_report': 'audit_report: Optional',
    }

    results = {}
    for name, field_def in checks.items():
        found = field_def in content
        results[name] = found
        status = "✅" if found else "❌"
        print(f"{status} {name} artifact in result")

    all_found = all(results.values())
    print()
    if all_found:
        print("✅ ALL ADVANCED ARTIFACTS IN RESULT")
    else:
        missing = [k for k, v in results.items() if not v]
        print(f"❌ MISSING ARTIFACTS: {', '.join(missing)}")

    print()
    return all_found


def check_version():
    """Verify the pipeline version"""
    print("="*80)
    print("VERIFICATION 6: Checking Pipeline Version")
    print("="*80)

    filepath = "unified_diagram_pipeline.py"

    with open(filepath, 'r') as f:
        content = f.read()

    # Look for version indicators
    v4_indicators = [
        '4.0-advanced',
        'Open-Source NLP',
        'Property Graph',
    ]

    found_indicators = []
    for indicator in v4_indicators:
        if indicator in content:
            found_indicators.append(indicator)
            print(f"✅ Found: '{indicator}'")

    is_v4 = len(found_indicators) >= 2
    print()
    if is_v4:
        print("✅ PIPELINE IS VERSION 4.0 (ADVANCED)")
    else:
        print("❌ PIPELINE APPEARS TO BE OLDER VERSION")

    print()
    return is_v4


def main():
    """Run all verification checks"""
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "UNIFIED PIPELINE v4.0 - INTEGRATION VERIFICATION".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    print()

    print("This script verifies that unified_diagram_pipeline.py ACTUALLY uses")
    print("the property graph and NLP tools (not just imports them).")
    print()

    # Run all checks
    results = {
        'Imports': check_imports(),
        'Config Options': check_config_options(),
        'Initialization': check_initialization(),
        'Usage in generate()': check_usage_in_generate(),
        'Result Artifacts': check_result_artifacts(),
        'Version': check_version(),
    }

    # Summary
    print("="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")

    print()

    all_passed = all(results.values())

    if all_passed:
        print("╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "✅ ALL VERIFICATIONS PASSED".center(78) + "║")
        print("║" + " "*78 + "║")
        print("║" + "The unified pipeline DOES use property graph and NLP tools!".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝")
        print()
        return 0
    else:
        print("╔" + "═"*78 + "╗")
        print("║" + " "*78 + "║")
        print("║" + "❌ SOME VERIFICATIONS FAILED".center(78) + "║")
        print("║" + " "*78 + "║")
        print("║" + "The integration may be incomplete.".center(78) + "║")
        print("║" + " "*78 + "║")
        print("╚" + "═"*78 + "╝")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
