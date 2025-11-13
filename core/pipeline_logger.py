"""
Pipeline Logger - Comprehensive request/response tracing for diagram generation

Provides structured logging with:
- Request/response tracking
- Phase-by-phase input/output logging
- Timing information
- Error tracking
- Hierarchical trace structure
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import traceback as tb


class PipelineLogger:
    """
    Structured logger for pipeline execution tracing

    Logs complete request/response flow with all intermediate states
    """

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize pipeline logger

        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create request-specific log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.request_id = f"req_{timestamp}"
        self.log_file = self.log_dir / f"{self.request_id}.log"

        # Setup logging
        self.logger = logging.getLogger(f"pipeline.{self.request_id}")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # File handler with detailed formatting
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)

        # Console handler with simpler formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        self.logger.addHandler(console_handler)

        # Trace structure
        self.trace = {
            'request_id': self.request_id,
            'timestamp': datetime.now().isoformat(),
            'phases': [],
            'total_duration_ms': 0,
            'status': 'in_progress',
            'error': None
        }

        self.start_time = time.time()
        self.current_phase = None

    def log_request(self, problem_text: str, config: Dict[str, Any]):
        """Log incoming request"""
        self.logger.info("="*80)
        self.logger.info("NEW DIAGRAM GENERATION REQUEST")
        self.logger.info("="*80)
        self.logger.info(f"Request ID: {self.request_id}")
        self.logger.info(f"Problem Text Length: {len(problem_text)} characters")
        self.logger.info("")
        self.logger.info("Problem Text:")
        self.logger.info("-" * 80)
        for line in problem_text.split('\n'):
            self.logger.info(f"  {line}")
        self.logger.info("-" * 80)
        self.logger.info("")
        self.logger.info("Configuration:")
        for key, value in config.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("")

        # Add to trace
        self.trace['input'] = {
            'problem_text': problem_text,
            'config': config,
            'text_length': len(problem_text)
        }

    def start_phase(self, phase_name: str, phase_number: int, description: str = ""):
        """Start a new pipeline phase"""
        phase_info = {
            'phase_number': phase_number,
            'phase_name': phase_name,
            'description': description,
            'start_time': time.time(),
            'duration_ms': 0,
            'input': {},
            'output': {},
            'logs': [],
            'status': 'running'
        }

        self.current_phase = phase_info
        self.trace['phases'].append(phase_info)

        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info(f"PHASE {phase_number}: {phase_name}")
        if description:
            self.logger.info(f"Description: {description}")
        self.logger.info("="*80)

    def log_phase_input(self, input_data: Any, summary: str = ""):
        """Log input to current phase"""
        if not self.current_phase:
            return

        self.logger.info("")
        self.logger.info("Phase Input:")
        self.logger.info("-" * 40)

        if summary:
            self.logger.info(f"Summary: {summary}")

        # Log structured data
        if isinstance(input_data, dict):
            for key, value in input_data.items():
                if isinstance(value, (str, int, float, bool)):
                    self.logger.info(f"  {key}: {value}")
                elif isinstance(value, (list, tuple)):
                    self.logger.info(f"  {key}: [{len(value)} items]")
                else:
                    self.logger.info(f"  {key}: {type(value).__name__}")
        elif isinstance(input_data, (list, tuple)):
            self.logger.info(f"  List with {len(input_data)} items")
        else:
            self.logger.info(f"  Type: {type(input_data).__name__}")

        self.logger.info("-" * 40)

        # Store in trace
        self.current_phase['input'] = self._serialize_data(input_data)

    def log_phase_output(self, output_data: Any, summary: str = ""):
        """Log output from current phase"""
        if not self.current_phase:
            return

        self.logger.info("")
        self.logger.info("Phase Output:")
        self.logger.info("-" * 40)

        if summary:
            self.logger.info(f"Summary: {summary}")

        # Log structured data
        if isinstance(output_data, dict):
            for key, value in output_data.items():
                if isinstance(value, (str, int, float, bool)):
                    self.logger.info(f"  {key}: {value}")
                elif isinstance(value, (list, tuple)):
                    self.logger.info(f"  {key}: [{len(value)} items]")
                else:
                    self.logger.info(f"  {key}: {type(value).__name__}")
        elif isinstance(output_data, (list, tuple)):
            self.logger.info(f"  List with {len(output_data)} items")
        elif hasattr(output_data, '__dict__'):
            self.logger.info(f"  Object: {type(output_data).__name__}")
            for key, value in output_data.__dict__.items():
                if not key.startswith('_'):
                    self.logger.info(f"    {key}: {type(value).__name__}")
        else:
            self.logger.info(f"  Type: {type(output_data).__name__}")

        self.logger.info("-" * 40)

        # Store in trace
        self.current_phase['output'] = self._serialize_data(output_data)

    def log_phase_detail(self, message: str, level: str = "INFO"):
        """Log detail within current phase"""
        log_func = getattr(self.logger, level.lower())
        log_func(f"  {message}")

        if self.current_phase:
            self.current_phase['logs'].append({
                'level': level,
                'message': message,
                'timestamp': time.time()
            })

    def end_phase(self, status: str = "success", error: str = None):
        """End current phase"""
        if not self.current_phase:
            return

        duration = (time.time() - self.current_phase['start_time']) * 1000
        self.current_phase['duration_ms'] = round(duration, 2)
        self.current_phase['status'] = status

        if error:
            self.current_phase['error'] = error
            self.logger.error(f"Phase failed: {error}")

        self.logger.info("")
        self.logger.info(f"Phase completed: {status.upper()}")
        self.logger.info(f"Duration: {self.current_phase['duration_ms']:.2f}ms")
        self.logger.info("="*80)

        self.current_phase = None

    def log_response(self, success: bool, result: Any = None, error: str = None):
        """Log final response"""
        total_duration = (time.time() - self.start_time) * 1000
        self.trace['total_duration_ms'] = round(total_duration, 2)
        self.trace['status'] = 'success' if success else 'error'

        if error:
            self.trace['error'] = error

        if result:
            self.trace['output'] = self._serialize_data(result)

        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("RESPONSE")
        self.logger.info("="*80)
        self.logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        self.logger.info(f"Total Duration: {total_duration:.2f}ms")

        if error:
            self.logger.error(f"Error: {error}")

        if result:
            self.logger.info("")
            self.logger.info("Result Summary:")
            if hasattr(result, '__dict__'):
                for key, value in result.__dict__.items():
                    if not key.startswith('_'):
                        self.logger.info(f"  {key}: {type(value).__name__}")

        self.logger.info("")
        self.logger.info(f"Full trace saved to: {self.log_file}")
        self.logger.info("="*80)

        # Save trace as JSON
        self._save_trace()

    def log_error(self, error: Exception, context: str = ""):
        """Log error with full traceback"""
        error_msg = f"{type(error).__name__}: {str(error)}"
        traceback = tb.format_exc()

        self.logger.error("")
        self.logger.error("="*80)
        self.logger.error("ERROR OCCURRED")
        self.logger.error("="*80)
        if context:
            self.logger.error(f"Context: {context}")
        self.logger.error(f"Error: {error_msg}")
        self.logger.error("")
        self.logger.error("Traceback:")
        for line in traceback.split('\n'):
            self.logger.error(f"  {line}")
        self.logger.error("="*80)

        # Add to current phase if active
        if self.current_phase:
            self.current_phase['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback
            }

    def _serialize_data(self, data: Any) -> Any:
        """Serialize data for JSON storage"""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._serialize_data(item) for item in data[:100]]  # Limit to first 100
        elif isinstance(data, dict):
            return {k: self._serialize_data(v) for k, v in list(data.items())[:100]}
        elif hasattr(data, '__dict__'):
            return {
                '_type': type(data).__name__,
                '_attributes': {k: self._serialize_data(v)
                               for k, v in data.__dict__.items()
                               if not k.startswith('_')}
            }
        else:
            return f"<{type(data).__name__}>"

    def _save_trace(self):
        """Save trace as JSON file"""
        trace_file = self.log_dir / f"{self.request_id}_trace.json"
        with open(trace_file, 'w') as f:
            json.dump(self.trace, f, indent=2, default=str)

        self.logger.info(f"Trace JSON saved to: {trace_file}")

    def get_trace_summary(self) -> str:
        """Get human-readable trace summary"""
        lines = []
        lines.append(f"Request ID: {self.trace['request_id']}")
        lines.append(f"Status: {self.trace['status']}")
        lines.append(f"Total Duration: {self.trace['total_duration_ms']:.2f}ms")
        lines.append("")
        lines.append("Phases:")

        for phase in self.trace['phases']:
            status_icon = "✅" if phase['status'] == 'success' else "❌"
            lines.append(f"  {status_icon} Phase {phase['phase_number']}: {phase['phase_name']}")
            lines.append(f"     Duration: {phase['duration_ms']:.2f}ms")
            if phase.get('error'):
                lines.append(f"     Error: {phase['error']}")

        return '\n'.join(lines)


class ConsoleProgressLogger:
    """
    Console progress logger for real-time feedback

    Provides visual progress indicators during diagram generation
    """

    def __init__(self):
        self.phases = []
        self.current_phase = None
        self.start_time = time.time()

    def start_phase(self, phase_name: str, phase_number: int):
        """Start new phase with visual indicator"""
        phase = {
            'number': phase_number,
            'name': phase_name,
            'start': time.time(),
            'status': 'running'
        }
        self.phases.append(phase)
        self.current_phase = phase

        print(f"\n🔄 [{phase_number}/7] {phase_name}...", end='', flush=True)

    def end_phase(self, success: bool = True):
        """End current phase with status"""
        if not self.current_phase:
            return

        duration = (time.time() - self.current_phase['start']) * 1000
        self.current_phase['duration'] = duration
        self.current_phase['status'] = 'success' if success else 'failed'

        icon = "✅" if success else "❌"
        print(f" {icon} ({duration:.0f}ms)")

        self.current_phase = None

    def complete(self, success: bool = True):
        """Show completion summary"""
        total_duration = (time.time() - self.start_time) * 1000

        print("\n" + "="*60)
        if success:
            print("✅ Diagram generation completed successfully!")
        else:
            print("❌ Diagram generation failed")
        print(f"⏱️  Total time: {total_duration:.0f}ms")
        print("="*60)
