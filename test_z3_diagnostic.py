"""
Diagnostic test for Z3 constraint solving
"""
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

# Configure with Z3 enabled and minimal other features
config = PipelineConfig(
    output_dir='output_z3_diagnostic',
    enable_property_graph=False,  # Disable for speed
    enable_complexity_assessment=True,  # Required for DiagramPlanner
    enable_strategic_planning=True,  # Required for DiagramPlanner
    enable_z3_optimization=True,  # ENABLED
    enable_ontology_validation=False,  # Disable for speed
    enable_nlp_enrichment=False,  # Disable for speed
    enable_logging=True  # Enable logging to see details
)

# Simple physics problem that should have constraints
problem = 'A block of mass 5 kg rests on a table. Draw a free body diagram.'

print("="*80)
print("Z3 Constraint Solving Diagnostic Test")
print("="*80)
print()

# Create pipeline
pipeline = UnifiedDiagramPipeline(config)

print()
print("Checking initialization:")
print(f"  z3_solver initialized: {pipeline.z3_solver is not None}")
print(f"  diagram_planner initialized: {pipeline.diagram_planner is not None}")
print()

print("="*80)
print("Generating diagram...")
print("="*80)
print()

# Generate diagram
result = pipeline.generate(problem)

print()
print("="*80)
print("RESULT")
print("="*80)
print(f"Status: {result.status}")
print(f"SVG Path: {result.svg_path}")
print(f"Trace Path: {result.trace_path}")
print()

# Check the trace for z3_used
if result.trace_path:
    import json
    with open(result.trace_path, 'r') as f:
        trace = json.load(f)

    # Find Z3 phase
    for phase in trace.get('phases', []):
        phase_name = phase.get('phase_name', '')
        if 'layout' in phase_name.lower() or 'z3' in phase_name.lower():
            print(f"Found phase: {phase_name}")
            output = phase.get('output', {})
            print(f"  z3_used: {output.get('z3_used')}")

            # Check logs for debug info
            logs = phase.get('logs', [])
            if logs:
                print(f"  Phase logs:")
                for log in logs:
                    print(f"    - {log}")
            else:
                print(f"  No phase logs (this is suspicious!)")
            break
    else:
        print("No Z3/Layout phase found in trace")

print()
print("="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
