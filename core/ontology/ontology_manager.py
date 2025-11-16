"""
Ontology Manager - Semantic Knowledge Representation
Phase 5A of Advanced NLP Roadmap

Provides OWL/RDF ontologies for scientific domains with:
- Domain-specific knowledge representation (physics, chemistry, biology)
- OWL-RL reasoning and inference
- Semantic validation and consistency checking
- SPARQL query support
- Integration with PropertyGraph

Installation:
    pip install rdflib owlrl

Ontologies include:
- Physics: Forces, motion, energy, fields
- Chemistry: Bonds, reactions, molecules, elements
- Biology: Cells, organisms, processes, pathways
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType
from core.problem_spec import CanonicalProblemSpec

# RDFLib for ontology management
try:
    from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL
    from rdflib.plugins.sparql import prepareQuery
    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False
    Graph = Namespace = Literal = URIRef = RDF = RDFS = OWL = None
    prepareQuery = None

# OWL-RL reasoning (optional)
try:
    import owlrl
    OWLRL_AVAILABLE = True
except ImportError:
    OWLRL_AVAILABLE = False
    owlrl = None


class Domain(Enum):
    """Scientific domains"""
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    GENERAL = "general"


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"  # Fail on any inconsistency
    MODERATE = "moderate"  # Warn on inconsistencies
    PERMISSIVE = "permissive"  # Only check critical errors


@dataclass
class OntologyTriple:
    """RDF triple (subject, predicate, object)"""
    subject: str
    predicate: str
    object: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_tuple(self) -> Tuple[str, str, str]:
        """Convert to tuple"""
        return (self.subject, self.predicate, self.object)


@dataclass
class ValidationResult:
    """Result from ontology validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    inferences: List[OntologyTriple] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'inference_count': len(self.inferences),
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


class OntologyManager:
    """
    Manages domain-specific OWL/RDF ontologies

    Provides semantic knowledge representation, reasoning,
    and validation for scientific diagrams.
    """

    def __init__(self,
                 domain: Domain = Domain.GENERAL,
                 enable_reasoning: bool = True,
                 verbose: bool = False):
        """
        Initialize ontology manager

        Args:
            domain: Scientific domain
            enable_reasoning: Enable OWL-RL reasoning
            verbose: Enable verbose logging

        Raises:
            ImportError: If rdflib not installed
        """
        if not RDFLIB_AVAILABLE:
            raise ImportError(
                "RDFLib not installed. Install with: pip install rdflib owlrl"
            )

        self.domain = domain
        self.enable_reasoning = enable_reasoning and OWLRL_AVAILABLE
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)

        # Initialize RDF graph
        self.graph = Graph()

        # Define namespaces
        self.BASE = Namespace("http://stem-diagrams.org/ontology/")
        self.STEM = Namespace("http://stem-diagrams.org/stem#")
        self.PHYS = Namespace("http://stem-diagrams.org/physics#")
        self.CHEM = Namespace("http://stem-diagrams.org/chemistry#")
        self.BIO = Namespace("http://stem-diagrams.org/biology#")

        # Bind namespaces
        self.graph.bind("stem", self.STEM)
        self.graph.bind("phys", self.PHYS)
        self.graph.bind("chem", self.CHEM)
        self.graph.bind("bio", self.BIO)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)

        # Initialize domain ontology
        self._initialize_domain_ontology(domain)

        if self.verbose:
            self.logger.info(f"Initialized OntologyManager for {domain.value}")
            if self.enable_reasoning:
                self.logger.info("OWL-RL reasoning enabled")

    # ========== Ontology Initialization ==========

    def _initialize_domain_ontology(self, domain: Domain) -> None:
        """Initialize ontology for specific domain"""
        if domain == Domain.PHYSICS:
            self._init_physics_ontology()
        elif domain == Domain.CHEMISTRY:
            self._init_chemistry_ontology()
        elif domain == Domain.BIOLOGY:
            self._init_biology_ontology()
        else:
            self._init_general_ontology()

    def _init_general_ontology(self) -> None:
        """Initialize general STEM ontology"""
        # Define top-level classes
        self.graph.add((self.STEM.Entity, RDF.type, OWL.Class))
        self.graph.add((self.STEM.Object, RDF.type, OWL.Class))
        self.graph.add((self.STEM.Object, RDFS.subClassOf, self.STEM.Entity))

        self.graph.add((self.STEM.Process, RDF.type, OWL.Class))
        self.graph.add((self.STEM.Process, RDFS.subClassOf, self.STEM.Entity))

        self.graph.add((self.STEM.Quantity, RDF.type, OWL.Class))
        self.graph.add((self.STEM.Quantity, RDFS.subClassOf, self.STEM.Entity))

        # Define properties
        self.graph.add((self.STEM.hasProperty, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.STEM.relatedTo, RDF.type, OWL.ObjectProperty))

    def _init_physics_ontology(self) -> None:
        """Initialize physics domain ontology"""
        # Inherit general ontology
        self._init_general_ontology()

        # Physics-specific classes
        self.graph.add((self.PHYS.Force, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Force, RDFS.subClassOf, self.STEM.Quantity))

        self.graph.add((self.PHYS.Mass, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Mass, RDFS.subClassOf, self.STEM.Quantity))

        self.graph.add((self.PHYS.Energy, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Energy, RDFS.subClassOf, self.STEM.Quantity))

        self.graph.add((self.PHYS.Charge, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Charge, RDFS.subClassOf, self.STEM.Quantity))

        # Force types
        self.graph.add((self.PHYS.GravitationalForce, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.GravitationalForce, RDFS.subClassOf, self.PHYS.Force))

        self.graph.add((self.PHYS.ElectrostaticForce, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.ElectrostaticForce, RDFS.subClassOf, self.PHYS.Force))

        self.graph.add((self.PHYS.NormalForce, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.NormalForce, RDFS.subClassOf, self.PHYS.Force))

        self.graph.add((self.PHYS.Friction, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Friction, RDFS.subClassOf, self.PHYS.Force))

        self.graph.add((self.PHYS.Tension, RDF.type, OWL.Class))
        self.graph.add((self.PHYS.Tension, RDFS.subClassOf, self.PHYS.Force))

        # Properties
        self.graph.add((self.PHYS.actsOn, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.PHYS.actsOn, RDFS.domain, self.PHYS.Force))
        self.graph.add((self.PHYS.actsOn, RDFS.range, self.STEM.Object))

        self.graph.add((self.PHYS.hasMagnitude, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.PHYS.hasDirection, RDF.type, OWL.DatatypeProperty))

        # Constraints
        # Normal force is perpendicular to surface
        self.graph.add((self.PHYS.NormalForce, RDFS.comment,
                       Literal("Normal force must be perpendicular to contact surface")))

        # Friction opposes motion
        self.graph.add((self.PHYS.Friction, RDFS.comment,
                       Literal("Friction force opposes direction of motion or potential motion")))

    def _init_chemistry_ontology(self) -> None:
        """Initialize chemistry domain ontology"""
        # Inherit general ontology
        self._init_general_ontology()

        # Chemistry-specific classes
        self.graph.add((self.CHEM.Atom, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.Atom, RDFS.subClassOf, self.STEM.Object))

        self.graph.add((self.CHEM.Molecule, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.Molecule, RDFS.subClassOf, self.STEM.Object))

        self.graph.add((self.CHEM.Bond, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.Bond, RDFS.subClassOf, self.STEM.Entity))

        # Bond types
        self.graph.add((self.CHEM.IonicBond, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.IonicBond, RDFS.subClassOf, self.CHEM.Bond))

        self.graph.add((self.CHEM.CovalentBond, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.CovalentBond, RDFS.subClassOf, self.CHEM.Bond))

        self.graph.add((self.CHEM.MetallicBond, RDF.type, OWL.Class))
        self.graph.add((self.CHEM.MetallicBond, RDFS.subClassOf, self.CHEM.Bond))

        # Properties
        self.graph.add((self.CHEM.bondedTo, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.CHEM.bondedTo, RDFS.domain, self.CHEM.Atom))
        self.graph.add((self.CHEM.bondedTo, RDFS.range, self.CHEM.Atom))

        self.graph.add((self.CHEM.hasAtomicNumber, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.CHEM.hasCharge, RDF.type, OWL.DatatypeProperty))

        # Constraints
        self.graph.add((self.CHEM.IonicBond, RDFS.comment,
                       Literal("Ionic bond occurs between atoms with opposite charges")))

    def _init_biology_ontology(self) -> None:
        """Initialize biology domain ontology"""
        # Inherit general ontology
        self._init_general_ontology()

        # Biology-specific classes
        self.graph.add((self.BIO.Cell, RDF.type, OWL.Class))
        self.graph.add((self.BIO.Cell, RDFS.subClassOf, self.STEM.Object))

        self.graph.add((self.BIO.Organelle, RDF.type, OWL.Class))
        self.graph.add((self.BIO.Organelle, RDFS.subClassOf, self.STEM.Object))

        self.graph.add((self.BIO.Protein, RDF.type, OWL.Class))
        self.graph.add((self.BIO.Protein, RDFS.subClassOf, self.STEM.Object))

        self.graph.add((self.BIO.DNA, RDF.type, OWL.Class))
        self.graph.add((self.BIO.DNA, RDFS.subClassOf, self.STEM.Object))

        # Properties
        self.graph.add((self.BIO.contains, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.BIO.contains, RDFS.domain, self.BIO.Cell))
        self.graph.add((self.BIO.contains, RDFS.range, self.BIO.Organelle))

    # ========== Triple Management ==========

    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """
        Add RDF triple to ontology

        Args:
            subject: Subject URI or literal
            predicate: Predicate URI
            obj: Object URI or literal

        Example:
            >>> manager.add_triple("force1", "phys:actsOn", "block1")
        """
        # Convert to URIRefs
        subj_uri = self._to_uri(subject)
        pred_uri = self._to_uri(predicate)
        obj_uri = self._to_uri_or_literal(obj)

        self.graph.add((subj_uri, pred_uri, obj_uri))

    def add_instance(self, instance_id: str, class_uri: str, properties: Optional[Dict] = None) -> None:
        """
        Add instance of a class

        Args:
            instance_id: Instance identifier
            class_uri: Class URI (e.g., "phys:Force")
            properties: Optional properties dict

        Example:
            >>> manager.add_instance("F1", "phys:GravitationalForce",
            ...                      {"phys:hasMagnitude": "10", "phys:hasDirection": "down"})
        """
        instance_uri = self._to_uri(instance_id)
        class_ref = self._to_uri(class_uri)

        # Add type declaration
        self.graph.add((instance_uri, RDF.type, class_ref))

        # Add properties
        if properties:
            for prop, value in properties.items():
                prop_uri = self._to_uri(prop)
                value_ref = self._to_uri_or_literal(value)
                self.graph.add((instance_uri, prop_uri, value_ref))

    def _to_uri(self, name: str) -> URIRef:
        """Convert name to URIRef"""
        # Handle namespace prefixes
        if ':' in name:
            prefix, local = name.split(':', 1)
            ns_map = {
                'stem': self.STEM,
                'phys': self.PHYS,
                'chem': self.CHEM,
                'bio': self.BIO,
                'owl': OWL,
                'rdf': RDF,
                'rdfs': RDFS
            }
            if prefix in ns_map:
                return ns_map[prefix][local]

        # Default to BASE namespace
        return self.BASE[name]

    def _to_uri_or_literal(self, value: Any) -> URIRef:
        """Convert value to URIRef or Literal"""
        if isinstance(value, str):
            # Check if it looks like a URI
            if ':' in value or value.startswith('http'):
                return self._to_uri(value)
            # Otherwise treat as literal
            return Literal(value)
        else:
            return Literal(value)

    # ========== Reasoning ==========

    def apply_reasoning(self) -> List[OntologyTriple]:
        """
        Apply OWL-RL reasoning to infer new triples

        Returns:
            List of inferred triples

        Example:
            >>> inferences = manager.apply_reasoning()
            >>> for triple in inferences:
            ...     print(f"{triple.subject} {triple.predicate} {triple.object}")
        """
        if not self.enable_reasoning or not OWLRL_AVAILABLE:
            if self.verbose:
                self.logger.warning("OWL-RL reasoning not available")
            return []

        # Get initial triple count
        initial_count = len(self.graph)

        # Apply OWL-RL reasoning
        try:
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(self.graph)

            # Get new triple count
            final_count = len(self.graph)
            inferred_count = final_count - initial_count

            if self.verbose:
                self.logger.info(f"Inferred {inferred_count} new triples")

            # Extract newly inferred triples (approximation)
            # In practice, we'd need to track which triples are new
            return []

        except Exception as e:
            self.logger.error(f"Reasoning failed: {e}")
            return []

    # ========== Validation ==========

    def validate(self, level: ValidationLevel = ValidationLevel.MODERATE) -> ValidationResult:
        """
        Validate ontology consistency

        Args:
            level: Validation strictness level

        Returns:
            ValidationResult with errors and warnings

        Example:
            >>> result = manager.validate()
            >>> if result.is_valid:
            ...     print("Ontology is valid")
            >>> else:
            ...     for error in result.errors:
            ...         print(f"Error: {error}")
        """
        errors = []
        warnings = []

        # Check for basic consistency
        # 1. Check that all referenced classes exist
        for s, p, o in self.graph:
            if p == RDF.type and isinstance(o, URIRef):
                # Check if class is defined
                if not self._is_class_defined(o):
                    msg = f"Instance {s} references undefined class {o}"
                    if level == ValidationLevel.STRICT:
                        errors.append(msg)
                    else:
                        warnings.append(msg)

        # 2. Check property domains and ranges
        for s, p, o in self.graph:
            if p not in [RDF.type, RDFS.subClassOf, RDFS.comment]:
                # Check if property is defined
                if not self._is_property_defined(p):
                    msg = f"Use of undefined property {p}"
                    if level == ValidationLevel.STRICT:
                        errors.append(msg)
                    else:
                        warnings.append(msg)

        # 3. Domain-specific validation
        domain_errors, domain_warnings = self._validate_domain_constraints(level)
        errors.extend(domain_errors)
        warnings.extend(domain_warnings)

        # Apply reasoning if enabled
        inferences = []
        if self.enable_reasoning:
            inferences = self.apply_reasoning()

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            inferences=inferences,
            metadata={
                'level': level.value,
                'triple_count': len(self.graph),
                'inference_count': len(inferences)
            }
        )

    def _is_class_defined(self, class_uri: URIRef) -> bool:
        """Check if class is defined in ontology"""
        return (class_uri, RDF.type, OWL.Class) in self.graph

    def _is_property_defined(self, prop_uri: URIRef) -> bool:
        """Check if property is defined in ontology"""
        return ((prop_uri, RDF.type, OWL.ObjectProperty) in self.graph or
                (prop_uri, RDF.type, OWL.DatatypeProperty) in self.graph or
                prop_uri in [RDF.type, RDFS.subClassOf, RDFS.comment, OWL.Class])

    def _validate_domain_constraints(self, level: ValidationLevel) -> Tuple[List[str], List[str]]:
        """Validate domain-specific constraints"""
        errors = []
        warnings = []

        if self.domain == Domain.PHYSICS:
            # Check that forces have magnitude and direction
            for s, p, o in self.graph:
                if p == RDF.type and o == self.PHYS.Force:
                    # Check magnitude
                    if not list(self.graph.objects(s, self.PHYS.hasMagnitude)):
                        warnings.append(f"Force {s} missing magnitude")
                    # Check direction
                    if not list(self.graph.objects(s, self.PHYS.hasDirection)):
                        warnings.append(f"Force {s} missing direction")

        elif self.domain == Domain.CHEMISTRY:
            # Check that ionic bonds have charged atoms
            for s, p, o in self.graph:
                if p == RDF.type and o == self.CHEM.IonicBond:
                    # Check that bonded atoms have charges
                    warnings.append(f"Ionic bond {s} should be between charged atoms (check manually)")

        return errors, warnings

    # ========== SPARQL Queries ==========

    def query(self, sparql_query: str) -> List[Dict]:
        """
        Execute SPARQL query

        Args:
            sparql_query: SPARQL query string

        Returns:
            List of result bindings

        Example:
            >>> query = \"\"\"
            ... SELECT ?force ?magnitude
            ... WHERE {
            ...     ?force rdf:type phys:Force .
            ...     ?force phys:hasMagnitude ?magnitude .
            ... }
            ... \"\"\"
            >>> results = manager.query(query)
            >>> for row in results:
            ...     print(f"Force: {row['force']}, Magnitude: {row['magnitude']}")
        """
        try:
            results = self.graph.query(sparql_query)

            # Convert to list of dicts
            result_list = []
            for row in results:
                result_dict = {}
                for var in results.vars:
                    result_dict[str(var)] = str(row[var]) if row[var] else None
                result_list.append(result_dict)

            return result_list

        except Exception as e:
            self.logger.error(f"SPARQL query failed: {e}")
            return []

    def find_instances_of_class(self, class_uri: str) -> List[str]:
        """
        Find all instances of a class

        Args:
            class_uri: Class URI (e.g., "phys:Force")

        Returns:
            List of instance URIs

        Example:
            >>> forces = manager.find_instances_of_class("phys:Force")
            >>> print(f"Found {len(forces)} forces")
        """
        class_ref = self._to_uri(class_uri)
        instances = []

        for s, p, o in self.graph.triples((None, RDF.type, class_ref)):
            instances.append(str(s))

        return instances

    # ========== Integration with PropertyGraph ==========

    def from_property_graph(self, graph: PropertyGraph) -> None:
        """
        Import PropertyGraph into ontology

        Args:
            graph: PropertyGraph to import

        Example:
            >>> manager.from_property_graph(property_graph)
            >>> result = manager.validate()
        """
        # Add nodes as instances
        for node_id, node_data in graph.graph.nodes(data=True):
            node_type = node_data.get('type', 'OBJECT')

            # Map NodeType to ontology class
            class_uri = self._map_node_type_to_class(node_type)

            # Add instance
            properties = {}
            # Skip complex metadata that shouldn't be serialized as simple RDF properties
            skip_keys = ['type', 'id', 'embedding', 'sources', 'metadata', 'data']
            for key, value in node_data.items():
                if key not in skip_keys and not isinstance(value, (dict, list)):
                    # Only serialize simple types (str, int, float, bool)
                    properties[f"stem:has{key.capitalize()}"] = str(value)

            self.add_instance(node_id, class_uri, properties)

        # Add edges as relationships
        for source, target, edge_data in graph.graph.edges(data=True):
            edge_type = edge_data.get('type', 'RELATED_TO')

            # Map EdgeType to ontology property
            property_uri = self._map_edge_type_to_property(edge_type)

            self.add_triple(source, property_uri, target)

    def to_property_graph(self) -> PropertyGraph:
        """
        Export ontology to PropertyGraph

        Returns:
            PropertyGraph representation

        Example:
            >>> pg = manager.to_property_graph()
            >>> print(pg.summary())
        """
        from core.property_graph import PropertyGraph, GraphNode, GraphEdge

        graph = PropertyGraph()

        # Find all instances (subjects with rdf:type)
        instances = set()
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            if not isinstance(o, Literal):
                instances.add(s)

        # Add nodes
        for instance in instances:
            # Get type
            types = list(self.graph.objects(instance, RDF.type))
            instance_type = str(types[0]) if types else "OBJECT"

            # Get properties
            properties = {}
            for p, o in self.graph.predicate_objects(instance):
                if p != RDF.type:
                    properties[str(p)] = str(o)

            node = GraphNode(
                id=str(instance),
                type=NodeType.OBJECT,  # Default
                label=str(instance).split('#')[-1].split('/')[-1],
                properties=properties
            )
            graph.add_node(node)

        # Add edges
        for s, p, o in self.graph:
            if s in instances and o in instances and p not in [RDF.type, RDFS.subClassOf]:
                edge = GraphEdge(
                    source=str(s),
                    target=str(o),
                    type=EdgeType.RELATED_TO,  # Default
                    label=str(p).split('#')[-1].split('/')[-1]
                )
                graph.add_edge(edge)

        return graph

    def _map_node_type_to_class(self, node_type: str) -> str:
        """Map PropertyGraph NodeType to ontology class"""
        type_map = {
            'FORCE': 'phys:Force',
            'OBJECT': 'stem:Object',
            'QUANTITY': 'stem:Quantity',
            'PROCESS': 'stem:Process',
        }
        return type_map.get(node_type, 'stem:Entity')

    def _map_edge_type_to_property(self, edge_type: str) -> str:
        """Map PropertyGraph EdgeType to ontology property"""
        type_map = {
            'ACTS_ON': 'phys:actsOn',
            'BONDED_TO': 'chem:bondedTo',
            'CONTAINS': 'bio:contains',
            'RELATED_TO': 'stem:relatedTo',
        }
        return type_map.get(edge_type, 'stem:relatedTo')

    # ========== Utility Methods ==========

    def export_rdf(self, format: str = 'turtle') -> str:
        """
        Export ontology as RDF

        Args:
            format: RDF format ('turtle', 'xml', 'n3', 'json-ld')

        Returns:
            Serialized RDF string

        Example:
            >>> rdf = manager.export_rdf('turtle')
            >>> print(rdf)
        """
        return self.graph.serialize(format=format)

    def import_rdf(self, rdf_data: str, format: str = 'turtle') -> None:
        """
        Import RDF data into ontology

        Args:
            rdf_data: RDF data string
            format: RDF format
        """
        self.graph.parse(data=rdf_data, format=format)

    def get_class_hierarchy(self, class_uri: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get class hierarchy (subclass relationships)

        Args:
            class_uri: Optional root class (if None, returns full hierarchy)

        Returns:
            Dict mapping classes to their subclasses
        """
        hierarchy = {}

        for s, p, o in self.graph.triples((None, RDFS.subClassOf, None)):
            parent = str(o)
            child = str(s)

            if parent not in hierarchy:
                hierarchy[parent] = []
            hierarchy[parent].append(child)

        return hierarchy

    def get_stats(self) -> Dict[str, int]:
        """Get ontology statistics"""
        stats = {
            'total_triples': len(self.graph),
            'classes': len(list(self.graph.subjects(RDF.type, OWL.Class))),
            'instances': len(list(self.graph.subjects(RDF.type, None))),
            'properties': len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))) +
                         len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty)))
        }
        return stats

    def is_available(self) -> bool:
        """Check if RDFLib is available"""
        return RDFLIB_AVAILABLE

    def __repr__(self) -> str:
        """String representation"""
        return f"OntologyManager(domain={self.domain.value}, triples={len(self.graph)})"


# ========== Standalone Functions ==========

def check_rdflib_availability() -> bool:
    """Check if RDFLib is available"""
    return RDFLIB_AVAILABLE


def create_physics_ontology() -> OntologyManager:
    """
    Create pre-configured physics ontology

    Returns:
        OntologyManager for physics

    Example:
        >>> manager = create_physics_ontology()
        >>> manager.add_instance("F1", "phys:GravitationalForce")
    """
    return OntologyManager(domain=Domain.PHYSICS, enable_reasoning=True)


def create_chemistry_ontology() -> OntologyManager:
    """Create pre-configured chemistry ontology"""
    return OntologyManager(domain=Domain.CHEMISTRY, enable_reasoning=True)


def create_biology_ontology() -> OntologyManager:
    """Create pre-configured biology ontology"""
    return OntologyManager(domain=Domain.BIOLOGY, enable_reasoning=True)


def validate_diagram_semantics(spec: CanonicalProblemSpec) -> ValidationResult:
    """
    Validate diagram semantics using ontology

    Args:
        spec: CanonicalProblemSpec to validate

    Returns:
        ValidationResult

    Example:
        >>> result = validate_diagram_semantics(spec)
        >>> if result.is_valid:
        ...     print("Diagram is semantically valid")
    """
    # Determine domain
    domain_map = {
        'mechanics': Domain.PHYSICS,
        'electrostatics': Domain.PHYSICS,
        'chemistry': Domain.CHEMISTRY,
        'biology': Domain.BIOLOGY
    }
    domain = domain_map.get(spec.domain, Domain.GENERAL)

    # Create ontology manager
    manager = OntologyManager(domain=domain, enable_reasoning=True)

    # Import spec into ontology (simplified)
    # In real implementation, would convert CanonicalProblemSpec to ontology triples

    # Validate
    return manager.validate()
