"""
Pipeline Tracer - Comprehensive Logging and Tracing
====================================================

Provides detailed logging and tracing for every component in the diagram generation pipeline.
Tracks inputs, outputs, transformations, and data flow at each stage.

Author: Universal STEM Diagram Generator
Date: November 17, 2025
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import json
import time
from datetime import datetime
from pathlib import Path


@dataclass
class ComponentTrace:
    """Trace record for a single component execution"""
    component_name: str
    phase: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None

    # Input tracking
    input_summary: Dict[str, Any] = field(default_factory=dict)
    input_sample: Optional[str] = None
    input_count: Optional[int] = None
    input_types: List[str] = field(default_factory=list)

    # Output tracking
    output_summary: Dict[str, Any] = field(default_factory=dict)
    output_sample: Optional[str] = None
    output_count: Optional[int] = None
    output_types: List[str] = field(default_factory=list)

    # Transformation tracking
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    filtered_count: int = 0
    added_count: int = 0
    modified_count: int = 0

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self):
        """Mark component execution as complete"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class PipelineTracer:
    """
    Comprehensive tracing and logging for the entire pipeline

    Features:
    - Component-level input/output tracking
    - Data transformation logging
    - Entity flow tracing
    - Performance metrics
    - Error aggregation
    - JSON export for analysis
    """

    def __init__(self, request_id: str, output_dir: str = "logs"):
        """
        Initialize pipeline tracer

        Args:
            request_id: Unique identifier for this pipeline run
            output_dir: Directory for trace output
        """
        self.request_id = request_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Trace storage
        self.traces: List[ComponentTrace] = []
        self.current_trace: Optional[ComponentTrace] = None

        # Entity flow tracking
        self.entity_flow: List[Dict[str, Any]] = []
        self.entity_lifecycle: Dict[str, List[str]] = {}  # entity_id -> [phase1, phase2, ...]

        # Performance metrics
        self.start_time = time.time()
        self.phase_times: Dict[str, float] = {}

        # Error aggregation
        self.all_errors: List[Dict[str, Any]] = []
        self.all_warnings: List[Dict[str, Any]] = []

    # ========== Component Tracing ==========

    def start_component(self, name: str, phase: str, metadata: Optional[Dict] = None) -> ComponentTrace:
        """
        Start tracing a component

        Args:
            name: Component name
            phase: Pipeline phase
            metadata: Optional metadata

        Returns:
            ComponentTrace object
        """
        trace = ComponentTrace(
            component_name=name,
            phase=phase,
            start_time=time.time(),
            metadata=metadata or {}
        )

        self.current_trace = trace
        self.traces.append(trace)

        print(f"\n{'='*80}")
        print(f"🔍 TRACE START: {name} (Phase: {phase})")
        print(f"{'='*80}")

        return trace

    def log_input(self, data: Any, description: str = "input"):
        """
        Log component input

        Args:
            data: Input data
            description: Description of input
        """
        if not self.current_trace:
            return

        summary = self._summarize_data(data)
        self.current_trace.input_summary[description] = summary

        # Log sample
        sample = self._get_sample(data)
        if sample:
            self.current_trace.input_sample = sample

        # Log count and types
        count, types = self._count_and_types(data)
        self.current_trace.input_count = count
        self.current_trace.input_types = types

        print(f"\n📥 INPUT: {description}")
        print(f"   Type: {type(data).__name__}")
        print(f"   Summary: {json.dumps(summary, indent=2)}")
        if count:
            print(f"   Count: {count}")
        if types:
            print(f"   Types: {types}")

    def log_output(self, data: Any, description: str = "output"):
        """
        Log component output

        Args:
            data: Output data
            description: Description of output
        """
        if not self.current_trace:
            return

        summary = self._summarize_data(data)
        self.current_trace.output_summary[description] = summary

        # Log sample
        sample = self._get_sample(data)
        if sample:
            self.current_trace.output_sample = sample

        # Log count and types
        count, types = self._count_and_types(data)
        self.current_trace.output_count = count
        self.current_trace.output_types = types

        print(f"\n📤 OUTPUT: {description}")
        print(f"   Type: {type(data).__name__}")
        print(f"   Summary: {json.dumps(summary, indent=2)}")
        if count:
            print(f"   Count: {count}")
        if types:
            print(f"   Types: {types}")

    def log_transformation(self, transformation_type: str, details: Dict[str, Any]):
        """
        Log a data transformation

        Args:
            transformation_type: Type of transformation
            details: Transformation details
        """
        if not self.current_trace:
            return

        self.current_trace.transformations.append({
            'type': transformation_type,
            'timestamp': time.time(),
            'details': details
        })

        print(f"\n🔄 TRANSFORMATION: {transformation_type}")
        print(f"   Details: {json.dumps(details, indent=2)}")

    def log_entity_added(self, entity_id: str, entity_data: Dict):
        """Log entity addition"""
        if self.current_trace:
            self.current_trace.added_count += 1

        # Track entity lifecycle
        if entity_id not in self.entity_lifecycle:
            self.entity_lifecycle[entity_id] = []
        self.entity_lifecycle[entity_id].append(f"added_in_{self.current_trace.phase}")

        print(f"   ➕ ADDED: {entity_id}")
        print(f"      Data: {json.dumps(entity_data, indent=6)}")

    def log_entity_filtered(self, entity_id: str, reason: str):
        """Log entity filtering"""
        if self.current_trace:
            self.current_trace.filtered_count += 1

        # Track entity lifecycle
        if entity_id not in self.entity_lifecycle:
            self.entity_lifecycle[entity_id] = []
        self.entity_lifecycle[entity_id].append(f"filtered_in_{self.current_trace.phase}: {reason}")

        print(f"   ❌ FILTERED: {entity_id}")
        print(f"      Reason: {reason}")

    def log_entity_modified(self, entity_id: str, changes: Dict):
        """Log entity modification"""
        if self.current_trace:
            self.current_trace.modified_count += 1

        # Track entity lifecycle
        if entity_id not in self.entity_lifecycle:
            self.entity_lifecycle[entity_id] = []
        self.entity_lifecycle[entity_id].append(f"modified_in_{self.current_trace.phase}")

        print(f"   ✏️  MODIFIED: {entity_id}")
        print(f"      Changes: {json.dumps(changes, indent=6)}")

    def log_error(self, error: str, context: Optional[Dict] = None):
        """
        Log an error

        Args:
            error: Error message
            context: Optional context
        """
        if self.current_trace:
            self.current_trace.errors.append(error)

        error_record = {
            'timestamp': time.time(),
            'component': self.current_trace.component_name if self.current_trace else 'unknown',
            'phase': self.current_trace.phase if self.current_trace else 'unknown',
            'error': error,
            'context': context or {}
        }
        self.all_errors.append(error_record)

        print(f"\n❌ ERROR: {error}")
        if context:
            print(f"   Context: {json.dumps(context, indent=2)}")

    def log_warning(self, warning: str, context: Optional[Dict] = None):
        """
        Log a warning

        Args:
            warning: Warning message
            context: Optional context
        """
        if self.current_trace:
            self.current_trace.warnings.append(warning)

        warning_record = {
            'timestamp': time.time(),
            'component': self.current_trace.component_name if self.current_trace else 'unknown',
            'phase': self.current_trace.phase if self.current_trace else 'unknown',
            'warning': warning,
            'context': context or {}
        }
        self.all_warnings.append(warning_record)

        print(f"\n⚠️  WARNING: {warning}")
        if context:
            print(f"   Context: {json.dumps(context, indent=2)}")

    def complete_component(self):
        """Complete current component trace"""
        if not self.current_trace:
            return

        self.current_trace.complete()

        print(f"\n{'='*80}")
        print(f"✅ TRACE COMPLETE: {self.current_trace.component_name}")
        print(f"   Duration: {self.current_trace.duration_ms:.2f}ms")
        print(f"   Added: {self.current_trace.added_count}")
        print(f"   Filtered: {self.current_trace.filtered_count}")
        print(f"   Modified: {self.current_trace.modified_count}")
        print(f"   Errors: {len(self.current_trace.errors)}")
        print(f"   Warnings: {len(self.current_trace.warnings)}")
        print(f"{'='*80}\n")

        self.current_trace = None

    # ========== Data Analysis Helpers ==========

    def _summarize_data(self, data: Any) -> Dict[str, Any]:
        """Create a summary of data"""
        summary = {
            'type': type(data).__name__
        }

        if isinstance(data, dict):
            summary['keys'] = list(data.keys())
            summary['key_count'] = len(data)
            # Sample values
            sample_keys = list(data.keys())[:3]
            summary['sample'] = {k: str(data[k])[:100] for k in sample_keys}

        elif isinstance(data, (list, tuple)):
            summary['length'] = len(data)
            if data:
                summary['first_item_type'] = type(data[0]).__name__
                summary['sample_items'] = [str(item)[:100] for item in data[:3]]

        elif isinstance(data, str):
            summary['length'] = len(data)
            summary['preview'] = data[:200]

        elif hasattr(data, '__dict__'):
            # Object with attributes
            summary['attributes'] = list(data.__dict__.keys())

        return summary

    def _get_sample(self, data: Any, max_length: int = 200) -> Optional[str]:
        """Get a sample of data"""
        try:
            if isinstance(data, str):
                return data[:max_length]
            elif isinstance(data, (list, tuple)) and data:
                return str(data[0])[:max_length]
            elif isinstance(data, dict):
                first_key = list(data.keys())[0] if data else None
                if first_key:
                    return f"{first_key}: {str(data[first_key])[:max_length]}"
            return str(data)[:max_length]
        except:
            return None

    def _count_and_types(self, data: Any) -> Tuple[Optional[int], List[str]]:
        """Count items and get types"""
        count = None
        types = []

        if isinstance(data, (list, tuple)):
            count = len(data)
            types = list(set(type(item).__name__ for item in data))
        elif isinstance(data, dict):
            count = len(data)
            types = list(set(type(v).__name__ for v in data.values()))

        return count, types

    # ========== Export and Reporting ==========

    def export_trace(self) -> str:
        """
        Export complete trace to JSON

        Returns:
            Path to trace file
        """
        trace_data = {
            'request_id': self.request_id,
            'timestamp': datetime.now().isoformat(),
            'total_duration_ms': (time.time() - self.start_time) * 1000,
            'components': [trace.to_dict() for trace in self.traces],
            'entity_lifecycle': self.entity_lifecycle,
            'entity_flow': self.entity_flow,
            'phase_times': self.phase_times,
            'errors': self.all_errors,
            'warnings': self.all_warnings,
            'summary': {
                'total_components': len(self.traces),
                'total_errors': len(self.all_errors),
                'total_warnings': len(self.all_warnings),
                'total_entities_added': sum(t.added_count for t in self.traces),
                'total_entities_filtered': sum(t.filtered_count for t in self.traces),
                'total_entities_modified': sum(t.modified_count for t in self.traces)
            }
        }

        trace_file = self.output_dir / f"{self.request_id}_detailed_trace.json"
        with open(trace_file, 'w') as f:
            json.dump(trace_data, f, indent=2)

        print(f"\n📊 TRACE EXPORTED: {trace_file}")
        return str(trace_file)

    def print_summary(self):
        """Print execution summary"""
        print(f"\n{'='*80}")
        print(f"📊 PIPELINE EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Request ID: {self.request_id}")
        print(f"Total Duration: {(time.time() - self.start_time) * 1000:.2f}ms")
        print(f"\nComponents Executed: {len(self.traces)}")

        print(f"\n📈 Entity Flow:")
        print(f"   Total Added: {sum(t.added_count for t in self.traces)}")
        print(f"   Total Filtered: {sum(t.filtered_count for t in self.traces)}")
        print(f"   Total Modified: {sum(t.modified_count for t in self.traces)}")

        print(f"\n🔴 Errors: {len(self.all_errors)}")
        for error in self.all_errors[:5]:
            print(f"   - [{error['component']}] {error['error']}")

        print(f"\n🟡 Warnings: {len(self.all_warnings)}")
        for warning in self.all_warnings[:5]:
            print(f"   - [{warning['component']}] {warning['warning']}")

        print(f"\n⏱️  Phase Breakdown:")
        for phase, duration in sorted(self.phase_times.items()):
            print(f"   {phase}: {duration:.2f}ms")

        print(f"{'='*80}\n")

    def track_entity_flow(self, phase: str, entities: List[Dict]):
        """
        Track entity flow through pipeline

        Args:
            phase: Pipeline phase
            entities: List of entities at this phase
        """
        self.entity_flow.append({
            'phase': phase,
            'timestamp': time.time(),
            'entity_count': len(entities),
            'entities': [
                {
                    'id': e.get('id', e.get('label', 'unknown')),
                    'type': e.get('type', 'unknown'),
                    'label': e.get('label', '')[:50]
                }
                for e in entities[:10]  # Sample first 10
            ]
        })

        print(f"\n🌊 ENTITY FLOW ({phase}):")
        print(f"   Total Entities: {len(entities)}")
        print(f"   Sample Entities:")
        for e in entities[:5]:
            print(f"     - {e.get('label', e.get('id', 'unknown'))}")
