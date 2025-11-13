"""
Ontology Module
Phase 5A of Advanced NLP Roadmap

Semantic knowledge representation with OWL/RDF ontologies.
"""

from core.ontology.ontology_manager import (
    OntologyManager,
    Domain,
    ValidationLevel,
    OntologyTriple,
    ValidationResult,
    check_rdflib_availability,
    create_physics_ontology,
    create_chemistry_ontology,
    create_biology_ontology,
    validate_diagram_semantics
)

__all__ = [
    'OntologyManager',
    'Domain',
    'ValidationLevel',
    'OntologyTriple',
    'ValidationResult',
    'check_rdflib_availability',
    'create_physics_ontology',
    'create_chemistry_ontology',
    'create_biology_ontology',
    'validate_diagram_semantics'
]
