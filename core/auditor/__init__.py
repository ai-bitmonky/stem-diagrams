"""
Diagram Auditor Module
Phase 5B of Advanced NLP Roadmap

LLM-based diagram quality validation and iterative refinement.
"""

from core.auditor.diagram_auditor import (
    DiagramAuditor,
    LLMBackend,
    IssueSeverity,
    IssueCategory,
    DiagramIssue,
    AuditResult,
    RefinementIteration,
    check_llm_availability,
    quick_audit,
    generate_audit_report
)

__all__ = [
    'DiagramAuditor',
    'LLMBackend',
    'IssueSeverity',
    'IssueCategory',
    'DiagramIssue',
    'AuditResult',
    'RefinementIteration',
    'check_llm_availability',
    'quick_audit',
    'generate_audit_report'
]
