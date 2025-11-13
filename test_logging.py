"""
Test script to verify pipeline logging integration
"""

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import os
from pathlib import Path

# Simple test problem
problem = """
A parallel-plate capacitor has charge q and plate area A.
The plates are separated by distance x.
"""

# Configure pipeline with logging enabled
config = PipelineConfig()
config.output_dir = "output_test"
config.log_dir = "logs"  # Log files will be created here
config.enable_logging = True  # Enable logging
config.log_level = "INFO"
config.validation_mode = "warn"

# Disable advanced features for faster test
config.nlp_tools = []
config.enable_property_graph = False
config.enable_nlp_enrichment = False
config.enable_z3_optimization = False
config.enable_llm_planning = False
config.enable_llm_auditing = False
config.enable_ontology_validation = False

print("="*80)
print("Testing Pipeline Logging Integration")
print("="*80)

# Run pipeline
pipeline = UnifiedDiagramPipeline(config)

try:
    result = pipeline.generate(problem)

    print("\n" + "="*80)
    print("✅ TEST PASSED - Diagram generated successfully!")
    print("="*80)

    # Check that log files were created
    log_dir = Path(config.log_dir)
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        trace_files = list(log_dir.glob("*_trace.json"))

        print(f"\n📋 Log Files Created:")
        print(f"   - Log files: {len(log_files)}")
        print(f"   - Trace files: {len(trace_files)}")

        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"\n📄 Latest log file: {latest_log}")
            print(f"   Size: {latest_log.stat().st_size:,} bytes")

        if trace_files:
            latest_trace = max(trace_files, key=lambda p: p.stat().st_mtime)
            print(f"\n📄 Latest trace file: {latest_trace}")
            print(f"   Size: {latest_trace.stat().st_size:,} bytes")

            # Show trace summary
            import json
            with open(latest_trace, 'r') as f:
                trace = json.load(f)
                print(f"\n📊 Trace Summary:")
                print(f"   Request ID: {trace.get('request_id', 'N/A')}")
                print(f"   Status: {trace.get('status', 'N/A')}")
                print(f"   Total Duration: {trace.get('total_duration_ms', 0):.0f}ms")
                print(f"   Phases Completed: {len(trace.get('phases', []))}")

                for phase in trace.get('phases', []):
                    duration = phase.get('duration_ms', 0)
                    print(f"      - {phase.get('phase_name', 'Unknown')}: {duration:.0f}ms")
    else:
        print(f"\n⚠️  Log directory not found: {log_dir}")

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

    # Even on error, check if error was logged
    log_dir = Path(config.log_dir)
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
            print(f"\n📄 Error log file: {latest_log}")
            print(f"   Check this file for error details")

print("\n" + "="*80)
