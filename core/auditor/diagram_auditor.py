"""
Diagram Auditor - LLM-Based Quality Validation
Phase 5B of Advanced NLP Roadmap

Integrates LLMs (Claude, GPT, etc.) for:
- Diagram quality validation
- Error detection and correction
- Scientific accuracy verification
- Iterative diagram refinement

The auditor generates scene descriptions, sends them to LLMs,
and parses critiques to identify issues and suggest corrections.

Installation:
    pip install anthropic openai  # For API access
    # OR use local models via transformers

Supported LLM backends:
- Anthropic Claude (claude-3-opus, claude-3-sonnet)
- OpenAI GPT (gpt-4, gpt-3.5-turbo)
- Local models via transformers (optional)
- Mock backend for testing
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
import json
import textwrap

from core.problem_spec import CanonicalProblemSpec
from core.property_graph import PropertyGraph, GraphNode, GraphEdge

# Optional LLM client libraries
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


class LLMBackend(Enum):
    """Supported LLM backends"""
    CLAUDE = "claude"
    GPT = "gpt"
    DEEPSEEK = "deepseek"  # NEW: Cost-effective DeepSeek API
    LOCAL = "local"
    MOCK = "mock"


class IssueSeverity(Enum):
    """Severity levels for diagram issues"""
    CRITICAL = "critical"  # Scientifically incorrect
    MAJOR = "major"  # Misleading or confusing
    MINOR = "minor"  # Stylistic improvements
    SUGGESTION = "suggestion"  # Optional enhancements


class IssueCategory(Enum):
    """Categories of diagram issues"""
    SCIENTIFIC_ACCURACY = "scientific_accuracy"
    VISUAL_CLARITY = "visual_clarity"
    LABELING = "labeling"
    LAYOUT = "layout"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"


@dataclass
class DiagramIssue:
    """
    Issue identified by the auditor

    Example:
        DiagramIssue(
            category=IssueCategory.SCIENTIFIC_ACCURACY,
            severity=IssueSeverity.CRITICAL,
            description="Force vector direction is incorrect",
            location="Object 'block' force 'F1'",
            suggestion="Reverse the direction of F1 to point left"
        )
    """
    category: IssueCategory
    severity: IssueSeverity
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'location': self.location,
            'suggestion': self.suggestion,
            'confidence': self.confidence,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"[{self.severity.value.upper()}] {self.description} @ {self.location}"


@dataclass
class AuditResult:
    """Result from diagram audit"""
    original_spec: CanonicalProblemSpec
    issues: List[DiagramIssue] = field(default_factory=list)
    overall_score: float = 0.0  # 0-1, higher is better
    critique_text: str = ""
    suggested_corrections: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'overall_score': self.overall_score,
            'issue_count': len(self.issues),
            'issues': [i.to_dict() for i in self.issues],
            'critique_text': self.critique_text,
            'suggested_corrections': self.suggested_corrections,
            'metadata': self.metadata
        }

    def has_critical_issues(self) -> bool:
        """Check if there are critical issues"""
        return any(i.severity == IssueSeverity.CRITICAL for i in self.issues)

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[DiagramIssue]:
        """Get issues of a specific severity"""
        return [i for i in self.issues if i.severity == severity]


@dataclass
class RefinementIteration:
    """Single iteration of diagram refinement"""
    iteration_number: int
    audit_result: AuditResult
    corrections_applied: List[Dict] = field(default_factory=list)
    improved_spec: Optional[CanonicalProblemSpec] = None


class DiagramAuditor:
    """
    LLM-based diagram quality auditor

    Uses LLMs to validate diagram quality, identify errors,
    and suggest corrections for scientific diagrams.
    """

    def __init__(self,
                 backend: LLMBackend = LLMBackend.MOCK,
                 api_key: Optional[str] = None,
                 model_name: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize diagram auditor

        Args:
            backend: LLM backend to use
            api_key: API key for cloud LLMs (Claude, GPT)
            model_name: Specific model name (e.g., 'claude-3-opus-20240229')
            verbose: Enable verbose logging

        Examples:
            >>> # Mock backend for testing
            >>> auditor = DiagramAuditor(backend=LLMBackend.MOCK)

            >>> # Claude backend
            >>> auditor = DiagramAuditor(
            ...     backend=LLMBackend.CLAUDE,
            ...     api_key="sk-...",
            ...     model_name="claude-3-opus-20240229"
            ... )
        """
        self.backend = backend
        self.api_key = api_key
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Default model names
        if model_name is None:
            if backend == LLMBackend.CLAUDE:
                self.model_name = "claude-3-sonnet-20240229"
            elif backend == LLMBackend.GPT:
                self.model_name = "gpt-4-turbo-preview"
            elif backend == LLMBackend.DEEPSEEK:
                self.model_name = "deepseek-chat"
            else:
                self.model_name = "mock"
        else:
            self.model_name = model_name

        # Initialize LLM client
        self.client = None

        if backend == LLMBackend.CLAUDE:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic not installed. Install with: pip install anthropic")
            if not api_key:
                raise ValueError("API key required for Claude backend")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif backend == LLMBackend.GPT:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed. Install with: pip install openai")
            if not api_key:
                raise ValueError("API key required for GPT backend")
            self.client = openai.OpenAI(api_key=api_key)

        elif backend == LLMBackend.DEEPSEEK:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI not installed (required for DeepSeek). Install with: pip install openai")
            if not api_key:
                raise ValueError("API key required for DeepSeek backend")
            # Use OpenAI-compatible client with DeepSeek endpoint
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )

        elif backend == LLMBackend.MOCK:
            if self.verbose:
                self.logger.info("Using mock LLM backend for testing")

        if self.verbose:
            self.logger.info(f"Initialized DiagramAuditor with {backend.value} backend")

    # ========== Scene Description Generation ==========

    def generate_scene_description(self, spec: CanonicalProblemSpec) -> str:
        """
        Generate natural language description of diagram

        Args:
            spec: CanonicalProblemSpec to describe

        Returns:
            Natural language description suitable for LLM

        Example:
            >>> description = auditor.generate_scene_description(spec)
            >>> print(description)
            This is a physics diagram in the mechanics domain.

            Objects:
            - block: A rectangular object at position (100, 200)
            - surface: A rectangular object at position (50, 300)
            ...
        """
        lines = []

        # Header
        lines.append(f"This is a {spec.domain} diagram.")
        problem_desc = getattr(spec, 'text_description', None) or getattr(spec, 'problem_text', None)
        if problem_desc:
            lines.append(f"Problem description: {problem_desc}")
        lines.append("")

        # Objects
        if spec.objects:
            lines.append("Objects:")
            for obj in spec.objects:
                obj_desc = f"- {obj.get('id', 'unknown')}: {obj.get('label', 'unlabeled')}"
                if obj.get('type'):
                    obj_desc += f" (type: {obj['type']})"
                if obj.get('position'):
                    pos = obj['position']
                    obj_desc += f" at position ({pos.get('x', 0)}, {pos.get('y', 0)})"
                if obj.get('properties'):
                    obj_desc += f" with properties {obj['properties']}"
                lines.append(obj_desc)
            lines.append("")

        # Relationships
        if spec.relationships:
            lines.append("Relationships:")
            for rel in spec.relationships:
                rel_desc = f"- {rel.get('source', '?')} --[{rel.get('type', 'related')}]--> {rel.get('target', '?')}"
                if rel.get('properties'):
                    rel_desc += f" (properties: {rel['properties']})"
                lines.append(rel_desc)
            lines.append("")

        # Constraints
        if spec.constraints:
            lines.append("Constraints:")
            for constraint in spec.constraints:
                lines.append(f"- {constraint.get('type', 'unknown')}: {constraint.get('description', 'no description')}")
            lines.append("")

        # Quantities
        quantities = getattr(spec, 'quantities', None)
        if quantities:
            lines.append("Quantities:")
            for qty in quantities:
                qty_desc = f"- {qty.get('name', 'unknown')}: {qty.get('value', '?')}"
                if qty.get('unit'):
                    qty_desc += f" {qty['unit']}"
                lines.append(qty_desc)
            lines.append("")

        return '\n'.join(lines)

    def generate_audit_prompt(
        self,
        spec: CanonicalProblemSpec,
        *,
        vlm_description: Optional[str] = None,
        structural_report: Optional[Dict[str, Any]] = None,
        domain_rule_report: Optional[Dict[str, Any]] = None,
        validation_results: Optional[Dict[str, Any]] = None,
        svg_excerpt: Optional[str] = None
    ) -> str:
        """
        Generate prompt for LLM audit

        Args:
            spec: CanonicalProblemSpec to audit

        Returns:
            Prompt string for LLM
        """
        scene_desc = self.generate_scene_description(spec)

        telemetry_sections: List[str] = []

        if vlm_description:
            telemetry_sections.append("Vision-Language Model Summary:\n" + textwrap.indent(vlm_description.strip(), "  "))

        if structural_report:
            summary = [
                f"- score: {structural_report.get('score', 'n/a')}",
                f"- missing objects: {len(structural_report.get('missing_in_scene', []))}",
                f"- relation gaps: {len(structural_report.get('relation_gaps', []))}"
            ]
            telemetry_sections.append("Structural Validator:\n" + "\n".join("  " + line for line in summary))

        if domain_rule_report:
            summary = [
                f"- errors: {domain_rule_report.get('errors', 0)}",
                f"- warnings: {domain_rule_report.get('warnings', 0)}"
            ]
            telemetry_sections.append("Domain Rule Engine:\n" + "\n".join("  " + line for line in summary))

        if validation_results:
            vf = validation_results.get('semantic_fidelity')
            summary = [
                f"- iterations: {validation_results.get('refinement_iterations', 0)}",
                f"- overall confidence: {validation_results.get('overall_confidence', 'n/a')}"
            ]
            if vf:
                summary.append(f"- semantic fidelity: {vf.get('match', 'n/a')} ({vf.get('reasoning', '')})")
            telemetry_sections.append("Validation Loop Snapshot:\n" + "\n".join("  " + line for line in summary))

        if svg_excerpt:
            telemetry_sections.append("SVG Excerpt (truncated):\n" + textwrap.indent(svg_excerpt.strip(), "  "))

        telemetry_block = ""
        if telemetry_sections:
            telemetry_block = "Diagnostic telemetry from earlier pipeline stages:\n"
            telemetry_block += "\n\n".join(telemetry_sections)
            telemetry_block += "\n\n"

        prompt = f"""You are an expert scientific diagram reviewer specializing in {spec.domain}.

I will provide you with a description of a diagram, and you should critique it for:
1. Scientific accuracy
2. Visual clarity
3. Labeling completeness
4. Layout quality
5. Consistency

{telemetry_block}Here is the diagram description:

{scene_desc}

Please provide a structured critique following this format:

OVERALL SCORE: [0-10, where 10 is perfect]

CRITICAL ISSUES:
- [List any scientifically incorrect elements]

MAJOR ISSUES:
- [List any misleading or confusing elements]

MINOR ISSUES:
- [List any stylistic improvements]

SUGGESTIONS:
- [List any optional enhancements]

For each issue, please specify:
- Category (scientific_accuracy, visual_clarity, labeling, layout, completeness, consistency)
- Location (which object or relationship)
- Specific correction suggestion

Be precise and constructive in your feedback."""

        return prompt

    # ========== LLM Interaction ==========

    def call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt

        Args:
            prompt: Prompt string

        Returns:
            LLM response text
        """
        if self.backend == LLMBackend.CLAUDE:
            return self._call_claude(prompt)
        elif self.backend == LLMBackend.GPT:
            return self._call_gpt(prompt)
        elif self.backend == LLMBackend.DEEPSEEK:
            return self._call_deepseek(prompt)
        elif self.backend == LLMBackend.MOCK:
            return self._call_mock(prompt)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text

        except Exception as e:
            self.logger.error(f"Claude API call failed: {e}")
            return self._generate_fallback_critique()

    def _call_gpt(self, prompt: str) -> str:
        """Call OpenAI GPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert scientific diagram reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"GPT API call failed: {e}")
            return self._generate_fallback_critique()

    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek API (OpenAI-compatible)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert scientific diagram reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048
            )
            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"DeepSeek API call failed: {e}")
            return self._generate_fallback_critique()

    def _call_mock(self, prompt: str) -> str:
        """Mock LLM for testing"""
        return """OVERALL SCORE: 7

CRITICAL ISSUES:
- None identified

MAJOR ISSUES:
- visual_clarity: Some force vectors may overlap. Location: Forces on 'block'. Suggestion: Adjust force vector origins to prevent overlap.

MINOR ISSUES:
- labeling: Consider adding units to all quantities. Location: All quantities. Suggestion: Append units in parentheses.

SUGGESTIONS:
- layout: Could improve spacing between objects for better readability.
- consistency: Ensure all arrows use the same style and thickness."""

    def _generate_fallback_critique(self) -> str:
        """Generate basic critique when LLM fails"""
        return """OVERALL SCORE: 5

MAJOR ISSUES:
- Unable to perform full audit due to LLM unavailability.

SUGGESTIONS:
- Please verify diagram manually or retry with available LLM backend."""

    # ========== Critique Parsing ==========

    def parse_critique(self, critique_text: str, spec: CanonicalProblemSpec) -> AuditResult:
        """
        Parse LLM critique into structured AuditResult

        Args:
            critique_text: Raw critique from LLM
            spec: Original CanonicalProblemSpec

        Returns:
            AuditResult with parsed issues
        """
        issues = []

        # Extract overall score
        overall_score = self._extract_overall_score(critique_text)

        # Parse sections
        critical_issues = self._parse_issue_section(
            critique_text, "CRITICAL ISSUES", IssueSeverity.CRITICAL
        )
        major_issues = self._parse_issue_section(
            critique_text, "MAJOR ISSUES", IssueSeverity.MAJOR
        )
        minor_issues = self._parse_issue_section(
            critique_text, "MINOR ISSUES", IssueSeverity.MINOR
        )
        suggestions = self._parse_issue_section(
            critique_text, "SUGGESTIONS", IssueSeverity.SUGGESTION
        )

        issues.extend(critical_issues)
        issues.extend(major_issues)
        issues.extend(minor_issues)
        issues.extend(suggestions)

        # Generate correction suggestions
        corrections = self._generate_corrections(issues, spec)

        return AuditResult(
            original_spec=spec,
            issues=issues,
            overall_score=overall_score,
            critique_text=critique_text,
            suggested_corrections=corrections,
            metadata={
                'backend': self.backend.value,
                'model': self.model_name,
                'issue_count_by_severity': {
                    'critical': len(critical_issues),
                    'major': len(major_issues),
                    'minor': len(minor_issues),
                    'suggestions': len(suggestions)
                }
            }
        )

    def _extract_overall_score(self, text: str) -> float:
        """Extract overall score from critique"""
        match = re.search(r'OVERALL SCORE:\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            # Normalize to 0-1
            return min(score / 10.0, 1.0)
        return 0.5  # Default middle score

    def _parse_issue_section(self, text: str, section_name: str, severity: IssueSeverity) -> List[DiagramIssue]:
        """Parse a section of issues from critique"""
        issues = []

        # Find section
        pattern = f'{section_name}:(.*?)(?=\\n[A-Z]{{2,}}|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if not match:
            return issues

        section_text = match.group(1)

        # Parse bullet points
        lines = section_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line == '-':
                continue

            # Remove leading dash
            line = re.sub(r'^-\s*', '', line)

            if not line or 'none' in line.lower():
                continue

            # Try to parse structured format: category: description. Location: loc. Suggestion: sug.
            category_match = re.match(r'(\w+):\s*(.+)', line)
            if category_match:
                category_str = category_match.group(1).lower()
                rest = category_match.group(2)

                # Map category string to enum
                category = self._parse_category(category_str)

                # Extract location
                location = None
                location_match = re.search(r'Location:\s*([^.]+)', rest)
                if location_match:
                    location = location_match.group(1).strip()

                # Extract suggestion
                suggestion = None
                suggestion_match = re.search(r'Suggestion:\s*(.+)', rest)
                if suggestion_match:
                    suggestion = suggestion_match.group(1).strip()

                # Description is everything before Location
                description = re.split(r'\.\s*Location:', rest)[0].strip()

                issue = DiagramIssue(
                    category=category,
                    severity=severity,
                    description=description,
                    location=location,
                    suggestion=suggestion,
                    confidence=0.8
                )
                issues.append(issue)

            else:
                # Fallback: treat whole line as description
                issue = DiagramIssue(
                    category=IssueCategory.COMPLETENESS,
                    severity=severity,
                    description=line,
                    confidence=0.6
                )
                issues.append(issue)

        return issues

    def _parse_category(self, category_str: str) -> IssueCategory:
        """Parse category string to enum"""
        category_map = {
            'scientific': IssueCategory.SCIENTIFIC_ACCURACY,
            'scientific_accuracy': IssueCategory.SCIENTIFIC_ACCURACY,
            'accuracy': IssueCategory.SCIENTIFIC_ACCURACY,
            'visual': IssueCategory.VISUAL_CLARITY,
            'visual_clarity': IssueCategory.VISUAL_CLARITY,
            'clarity': IssueCategory.VISUAL_CLARITY,
            'labeling': IssueCategory.LABELING,
            'labels': IssueCategory.LABELING,
            'layout': IssueCategory.LAYOUT,
            'spacing': IssueCategory.LAYOUT,
            'completeness': IssueCategory.COMPLETENESS,
            'complete': IssueCategory.COMPLETENESS,
            'consistency': IssueCategory.CONSISTENCY,
            'consistent': IssueCategory.CONSISTENCY,
        }

        return category_map.get(category_str.lower(), IssueCategory.COMPLETENESS)

    def _generate_corrections(self, issues: List[DiagramIssue], spec: CanonicalProblemSpec) -> List[Dict]:
        """Generate concrete correction actions from issues"""
        corrections = []

        for issue in issues:
            if issue.suggestion and issue.location:
                correction = {
                    'type': issue.category.value,
                    'target': issue.location,
                    'action': issue.suggestion,
                    'priority': self._severity_to_priority(issue.severity)
                }
                corrections.append(correction)

        return corrections

    def _severity_to_priority(self, severity: IssueSeverity) -> int:
        """Convert severity to priority (1=highest)"""
        priority_map = {
            IssueSeverity.CRITICAL: 1,
            IssueSeverity.MAJOR: 2,
            IssueSeverity.MINOR: 3,
            IssueSeverity.SUGGESTION: 4
        }
        return priority_map.get(severity, 4)

    # ========== Main Audit Method ==========

    def audit(
        self,
        spec: CanonicalProblemSpec,
        *,
        svg_output: Optional[str] = None,
        structural_report: Optional[Dict[str, Any]] = None,
        domain_rule_report: Optional[Dict[str, Any]] = None,
        validation_results: Optional[Dict[str, Any]] = None,
        vlm_description: Optional[str] = None
    ) -> AuditResult:
        """
        Audit a diagram specification

        Args:
            spec: CanonicalProblemSpec to audit

        Returns:
            AuditResult with issues and corrections

        Example:
            >>> auditor = DiagramAuditor(backend=LLMBackend.MOCK)
            >>> result = auditor.audit(spec)
            >>> print(f"Score: {result.overall_score:.2f}")
            >>> for issue in result.issues:
            ...     print(issue)
        """
        if self.verbose:
            self.logger.info(f"Auditing diagram for {spec.domain}")

        # Generate prompt
        svg_excerpt = None
        if svg_output:
            svg_excerpt = svg_output[:500]
            if len(svg_output) > 500:
                svg_excerpt += " …"
        prompt = self.generate_audit_prompt(
            spec,
            vlm_description=vlm_description,
            structural_report=structural_report,
            domain_rule_report=domain_rule_report,
            validation_results=validation_results,
            svg_excerpt=svg_excerpt
        )

        # Call LLM
        critique_text = self.call_llm(prompt)

        # Parse critique
        result = self.parse_critique(critique_text, spec)

        if self.verbose:
            self.logger.info(f"Audit complete. Score: {result.overall_score:.2f}, Issues: {len(result.issues)}")

        return result

    # ========== Iterative Refinement ==========

    def refine_iteratively(self,
                          spec: CanonicalProblemSpec,
                          max_iterations: int = 3,
                          min_score: float = 0.8) -> List[RefinementIteration]:
        """
        Iteratively refine diagram until quality threshold reached

        Args:
            spec: Initial CanonicalProblemSpec
            max_iterations: Maximum refinement iterations
            min_score: Minimum acceptable quality score (0-1)

        Returns:
            List of RefinementIteration objects

        Example:
            >>> auditor = DiagramAuditor(backend=LLMBackend.CLAUDE, api_key="...")
            >>> iterations = auditor.refine_iteratively(spec, max_iterations=3)
            >>> for i, iteration in enumerate(iterations):
            ...     print(f"Iteration {i}: Score {iteration.audit_result.overall_score:.2f}")
        """
        iterations = []
        current_spec = spec

        for i in range(max_iterations):
            if self.verbose:
                self.logger.info(f"Refinement iteration {i + 1}/{max_iterations}")

            # Audit current spec
            audit_result = self.audit(current_spec)

            # Apply corrections (simplified - real implementation would modify spec)
            corrections_applied = self._apply_corrections(current_spec, audit_result)

            iteration = RefinementIteration(
                iteration_number=i + 1,
                audit_result=audit_result,
                corrections_applied=corrections_applied,
                improved_spec=current_spec  # In real implementation, this would be modified
            )
            iterations.append(iteration)

            # Check if quality threshold reached
            if audit_result.overall_score >= min_score:
                if self.verbose:
                    self.logger.info(f"Quality threshold reached: {audit_result.overall_score:.2f} >= {min_score}")
                break

            # Check if no more corrections possible
            if not corrections_applied:
                if self.verbose:
                    self.logger.info("No more corrections to apply")
                break

        return iterations

    def _apply_corrections(self, spec: CanonicalProblemSpec, audit_result: AuditResult) -> List[Dict]:
        """
        Apply corrections to spec (placeholder)

        Real implementation would:
        - Parse correction suggestions
        - Modify spec accordingly
        - Validate changes

        Args:
            spec: Spec to modify
            audit_result: Audit with corrections

        Returns:
            List of applied corrections
        """
        # Placeholder: In real implementation, this would modify the spec
        # based on suggested_corrections from audit_result
        applied = []

        for correction in audit_result.suggested_corrections:
            if correction['priority'] <= 2:  # Apply critical and major
                applied.append({
                    'type': correction['type'],
                    'target': correction['target'],
                    'action': correction['action'],
                    'status': 'simulated'  # Real implementation would actually modify
                })

        return applied

    # ========== Utility Methods ==========

    def is_available(self) -> bool:
        """Check if LLM backend is available"""
        if self.backend == LLMBackend.CLAUDE:
            return ANTHROPIC_AVAILABLE and self.client is not None
        elif self.backend == LLMBackend.GPT:
            return OPENAI_AVAILABLE and self.client is not None
        elif self.backend == LLMBackend.MOCK:
            return True
        return False

    def get_issue_summary(self, result: AuditResult) -> Dict[str, int]:
        """Get summary of issues by category"""
        summary = {cat.value: 0 for cat in IssueCategory}
        for issue in result.issues:
            summary[issue.category.value] += 1
        return summary

    def __repr__(self) -> str:
        """String representation"""
        return f"DiagramAuditor(backend={self.backend.value}, model={self.model_name})"


# ========== Standalone Functions ==========

def check_llm_availability() -> Dict[str, bool]:
    """
    Check which LLM backends are available

    Returns:
        Dict mapping backend names to availability

    Example:
        >>> availability = check_llm_availability()
        >>> print(f"Claude: {availability['claude']}")
        >>> print(f"GPT: {availability['gpt']}")
    """
    return {
        'claude': ANTHROPIC_AVAILABLE,
        'gpt': OPENAI_AVAILABLE,
        'mock': True
    }


def quick_audit(spec: CanonicalProblemSpec, backend: str = 'mock') -> AuditResult:
    """
    Quick audit using specified backend

    Args:
        spec: CanonicalProblemSpec to audit
        backend: Backend name ('claude', 'gpt', 'mock')

    Returns:
        AuditResult

    Example:
        >>> result = quick_audit(spec, backend='mock')
        >>> print(f"Score: {result.overall_score:.2f}")
        >>> for issue in result.issues:
        ...     print(f"- {issue.description}")
    """
    backend_enum = LLMBackend(backend.lower())
    auditor = DiagramAuditor(backend=backend_enum, verbose=False)
    return auditor.audit(spec)


def generate_audit_report(result: AuditResult) -> str:
    """
    Generate human-readable audit report

    Args:
        result: AuditResult from audit

    Returns:
        Formatted report string

    Example:
        >>> report = generate_audit_report(result)
        >>> print(report)
    """
    lines = []

    lines.append("=" * 60)
    lines.append("DIAGRAM AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"Overall Score: {result.overall_score:.2f} / 1.00")
    lines.append(f"Total Issues: {len(result.issues)}")
    lines.append("")

    # Group by severity
    for severity in [IssueSeverity.CRITICAL, IssueSeverity.MAJOR, IssueSeverity.MINOR, IssueSeverity.SUGGESTION]:
        issues = result.get_issues_by_severity(severity)
        if issues:
            lines.append(f"{severity.value.upper()} ({len(issues)}):")
            for issue in issues:
                lines.append(f"  - {issue.description}")
                if issue.location:
                    lines.append(f"    Location: {issue.location}")
                if issue.suggestion:
                    lines.append(f"    Suggestion: {issue.suggestion}")
            lines.append("")

    if result.suggested_corrections:
        lines.append(f"Suggested Corrections ({len(result.suggested_corrections)}):")
        for i, correction in enumerate(result.suggested_corrections, 1):
            lines.append(f"  {i}. [{correction['type']}] {correction['action']}")
            lines.append(f"     Target: {correction['target']}")
            lines.append(f"     Priority: {correction['priority']}")
        lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)
