"""Domain-specific rule engines (Kirchhoff, Newton, geometry)"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import itertools
import math
from typing import Any, Dict, List, Optional, Set

from core.scene.schema_v1 import Scene, PrimitiveType, ConstraintType


@dataclass
class DomainRuleCheck:
    name: str
    passed: bool
    severity: str  # 'warning' or 'error'
    details: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'passed': self.passed,
            'severity': self.severity,
            'details': self.details
        }


def run_domain_rules(domain: Optional[str], scene: Scene, spec: Optional[Any] = None) -> Dict[str, Any]:
    domain = (domain or '').lower()
    checks: List[DomainRuleCheck] = []
    connection_graph = _build_connection_graph(scene, spec)

    if 'electro' in domain or 'current' in domain:
        checks.append(_kirchhoff_loop_check(scene, spec, connection_graph))
        checks.append(_power_source_check(scene, spec, connection_graph))
    if 'mechan' in domain or 'physics' in domain:
        checks.append(_newton_force_balance_check(scene, spec))
        checks.append(_conservation_laws_check(scene, spec))
    if 'optic' in domain or 'light' in domain:
        checks.append(_lens_equation_check(scene, spec))
    if 'chemistry' in domain or 'chemical' in domain:
        checks.append(_chemical_equation_balance_check(scene, spec))
    if 'geometry' in domain or 'math' in domain:
        checks.append(_geometry_triangle_check(spec))

    errors = sum(1 for c in checks if not c.passed and c.severity == 'error')
    warnings = sum(1 for c in checks if not c.passed and c.severity == 'warning')

    return {
        'domain': domain,
        'checks': [c.to_dict() for c in checks],
        'errors': errors,
        'warnings': warnings
    }


def _kirchhoff_loop_check(scene: Scene, spec: Optional[Any], graph: Dict[str, Set[str]]) -> DomainRuleCheck:
    """Ensure there is at least one closed conductive loop with power + load"""
    component_ids = _collect_object_ids(scene, ['resistor', 'capacitor', 'inductor', 'load', 'switch', 'wire'])
    source_ids = _collect_object_ids(scene, ['battery', 'source', 'supply'])
    relevant_nodes = set(component_ids + source_ids)

    has_loop_constraint = any(
        getattr(constraint, 'type', None) and str(constraint.type).lower() == 'closed_loop'
        for constraint in scene.constraints
    )
    has_cycle = _graph_has_cycle(graph, relevant_nodes) if relevant_nodes else False

    passed = bool((has_loop_constraint or has_cycle) and component_ids and source_ids)
    severity = 'warning' if passed else 'error'
    if not source_ids:
        details = "No power source detected in circuit graph"
    elif not component_ids:
        details = "No passive components detected"
    elif has_loop_constraint or has_cycle:
        details = "Closed loop detected"
    else:
        details = "Connections do not form a closed loop"

    return DomainRuleCheck('Kirchhoff Loop', passed, severity, details)


def _power_source_check(scene: Scene, spec: Optional[Any], graph: Dict[str, Set[str]]) -> DomainRuleCheck:
    source_ids = _collect_object_ids(scene, ['battery', 'source', 'supply'])
    connected_sources = [sid for sid in source_ids if graph.get(sid)]
    passed = bool(connected_sources)
    details = (
        f"Power sources connected: {len(connected_sources)}/{len(source_ids)}"
        if source_ids else "No power source objects"
    )
    severity = 'error' if not passed else 'warning'
    return DomainRuleCheck('Power Source Presence', passed, severity, details)


def _newton_force_balance_check(scene: Scene, spec: Optional[Any]) -> DomainRuleCheck:
    masses = [obj for obj in scene.objects if obj.type == PrimitiveType.MASS]
    force_map = _group_forces_by_target(scene)
    has_vector_data = any(force_map.values())

    if not masses:
        return DomainRuleCheck('Newton Force Equilibrium', True, 'warning', 'No mass objects detected')

    if not has_vector_data:
        force_vectors = [obj for obj in scene.objects if obj.type == PrimitiveType.ARROW]
        passed = len(force_vectors) >= len(masses)
        details = f"Vector data unavailable. Masses: {len(masses)}, Forces: {len(force_vectors)}"
        severity = 'warning' if passed else 'error'
        return DomainRuleCheck('Newton Force Equilibrium', passed, severity, details)

    failing: List[str] = []
    for mass in masses:
        vectors = force_map.get(mass.id, [])
        if not vectors:
            failing.append(f"{mass.id}: no forces applied")
            continue
        sum_x = sum(vec['x'] for vec in vectors)
        sum_y = sum(vec['y'] for vec in vectors)
        total_mag = sum(vec['magnitude'] for vec in vectors)
        residual = math.hypot(sum_x, sum_y)
        tolerance = max(1.0, 0.1 * total_mag)
        if residual > tolerance:
            failing.append(f"{mass.id}: residual {residual:.2f} > tol {tolerance:.2f}")

    passed = not failing
    severity = 'warning' if passed else 'error'
    details = "Force equilibrium satisfied" if passed else "; ".join(failing[:3])
    return DomainRuleCheck('Newton Force Equilibrium', passed, severity, details)


def _conservation_laws_check(scene: Scene, spec: Optional[Any]) -> DomainRuleCheck:
    """Check conservation of energy and momentum in mechanics problems"""
    # Extract initial and final state objects
    initial_objects = [obj for obj in scene.objects if 'initial' in (obj.id or '').lower()]
    final_objects = [obj for obj in scene.objects if 'final' in (obj.id or '').lower()]

    if not initial_objects and not final_objects:
        return DomainRuleCheck('Conservation Laws', True, 'warning', 'No initial/final states detected')

    # Check for energy conservation indicators
    has_energy_constraint = any(
        'energy' in str(getattr(c, 'type', '')).lower() or
        any('energy' in str(o).lower() for o in getattr(c, 'objects', []))
        for c in scene.constraints
    )

    # Extract energy values from properties
    initial_energies = []
    final_energies = []

    for obj in initial_objects:
        props = obj.properties or {}
        energy = props.get('energy') or props.get('kinetic_energy') or props.get('potential_energy')
        if energy:
            initial_energies.append(float(energy))

    for obj in final_objects:
        props = obj.properties or {}
        energy = props.get('energy') or props.get('kinetic_energy') or props.get('potential_energy')
        if energy:
            final_energies.append(float(energy))

    if initial_energies and final_energies:
        initial_total = sum(initial_energies)
        final_total = sum(final_energies)
        tolerance = max(1.0, 0.05 * initial_total)  # 5% tolerance
        energy_diff = abs(initial_total - final_total)
        passed = energy_diff <= tolerance
        severity = 'warning' if passed else 'error'
        details = f"Energy: initial={initial_total:.2f}, final={final_total:.2f}, diff={energy_diff:.2f}"
        return DomainRuleCheck('Conservation Laws', passed, severity, details)

    # If no numeric energy data, just check for constraint presence
    passed = has_energy_constraint or bool(initial_objects and final_objects)
    severity = 'warning'
    details = "Conservation constraint present" if has_energy_constraint else "Initial/final states present"
    return DomainRuleCheck('Conservation Laws', passed, severity, details)


def _lens_equation_check(scene: Scene, spec: Optional[Any]) -> DomainRuleCheck:
    """Validate lens equation: 1/f = 1/do + 1/di"""
    # Find lens objects
    lenses = [obj for obj in scene.objects if 'lens' in (obj.type.value if obj.type else '').lower() or
              'lens' in (obj.id or '').lower()]

    if not lenses:
        return DomainRuleCheck('Lens Equation', True, 'warning', 'No lens objects detected')

    violations = []
    for lens in lenses:
        props = lens.properties or {}
        focal_length = props.get('focal_length') or props.get('f')
        object_distance = props.get('object_distance') or props.get('do') or props.get('d_o')
        image_distance = props.get('image_distance') or props.get('di') or props.get('d_i')

        if focal_length and object_distance and image_distance:
            f = float(focal_length)
            do = float(object_distance)
            di = float(image_distance)

            # Check lens equation: 1/f = 1/do + 1/di
            if abs(f) > 0.001 and abs(do) > 0.001:  # Avoid division by zero
                expected_di_inv = (1.0 / f) - (1.0 / do)
                if abs(expected_di_inv) > 0.001:
                    expected_di = 1.0 / expected_di_inv
                    tolerance = max(1.0, 0.05 * abs(expected_di))
                    diff = abs(di - expected_di)

                    if diff > tolerance:
                        violations.append(f"{lens.id}: di={di:.2f} vs expected={expected_di:.2f}")

    passed = not violations
    severity = 'error' if not passed else 'warning'
    details = "Lens equation satisfied" if passed else f"Violations: {'; '.join(violations[:2])}"
    return DomainRuleCheck('Lens Equation', passed, severity, details)


def _chemical_equation_balance_check(scene: Scene, spec: Optional[Any]) -> DomainRuleCheck:
    """Check chemical equation atom balance"""
    # Extract reactant and product molecules
    reactants = [obj for obj in scene.objects if 'reactant' in (obj.id or '').lower() or
                 'reactant' in str(obj.properties.get('label', '')).lower() if obj.properties]
    products = [obj for obj in scene.objects if 'product' in (obj.id or '').lower() or
                'product' in str(obj.properties.get('label', '')).lower() if obj.properties]

    if not reactants and not products:
        return DomainRuleCheck('Chemical Balance', True, 'warning', 'No reactants/products detected')

    # Extract atom counts from properties
    def get_atom_counts(obj):
        props = obj.properties or {}
        atoms = props.get('atoms') or props.get('composition') or props.get('formula')
        if isinstance(atoms, dict):
            return atoms
        return {}

    reactant_atoms = {}
    product_atoms = {}

    for reactant in reactants:
        atoms = get_atom_counts(reactant)
        coeff = float((reactant.properties or {}).get('coefficient', 1))
        for element, count in atoms.items():
            reactant_atoms[element] = reactant_atoms.get(element, 0) + count * coeff

    for product in products:
        atoms = get_atom_counts(product)
        coeff = float((product.properties or {}).get('coefficient', 1))
        for element, count in atoms.items():
            product_atoms[element] = product_atoms.get(element, 0) + count * coeff

    if reactant_atoms and product_atoms:
        all_elements = set(reactant_atoms.keys()) | set(product_atoms.keys())
        imbalances = []

        for element in all_elements:
            r_count = reactant_atoms.get(element, 0)
            p_count = product_atoms.get(element, 0)
            if abs(r_count - p_count) > 0.001:
                imbalances.append(f"{element}: {r_count} → {p_count}")

        passed = not imbalances
        severity = 'error' if not passed else 'warning'
        details = "Equation balanced" if passed else f"Imbalances: {', '.join(imbalances[:3])}"
        return DomainRuleCheck('Chemical Balance', passed, severity, details)

    # If no atom data, just check for presence
    passed = bool(reactants and products)
    severity = 'warning'
    details = f"Reactants: {len(reactants)}, Products: {len(products)}"
    return DomainRuleCheck('Chemical Balance', passed, severity, details)


def _geometry_triangle_check(spec: Optional[Any]) -> DomainRuleCheck:
    if not spec or not getattr(spec, 'geometry', None):
        return DomainRuleCheck('Geometry Constraints', True, 'warning', 'No geometry data provided')
    geometry = spec.geometry or {}
    if geometry.get('shape', '').lower() != 'triangle':
        return DomainRuleCheck('Geometry Constraints', True, 'warning', 'No triangle specified')
    points = geometry.get('points', [])
    passed = len(points) == 3
    severity = 'error' if not passed else 'warning'
    details = f"Triangle points provided: {len(points)}"
    return DomainRuleCheck('Triangle Definition', passed, severity, details)


def _collect_object_ids(scene: Scene, keywords: List[str]) -> List[str]:
    matches: List[str] = []
    for obj in scene.objects:
        obj_id = obj.id.lower() if obj.id else ''
        obj_label = (obj.properties.get('label') or '').lower() if obj.properties else ''
        obj_type = obj.type.value.lower() if obj.type else ''
        if any(keyword in obj_id or keyword in obj_label or keyword in obj_type for keyword in keywords):
            matches.append(obj.id)
    return matches


def _build_connection_graph(scene: Scene, spec: Optional[Any]) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = defaultdict(set)

    def _connect(a: Optional[str], b: Optional[str]):
        if not a or not b or a == b:
            return
        graph[a].add(b)
        graph[b].add(a)

    connect_constraints = {
        ConstraintType.CONNECTED,
        ConstraintType.ADJACENT,
        ConstraintType.STACKED_H,
        ConstraintType.STACKED_V,
        ConstraintType.LEFT_OF,
        ConstraintType.RIGHT_OF
    }
    for constraint in scene.constraints:
        if constraint.type in connect_constraints and constraint.objects:
            for a, b in itertools.combinations(constraint.objects, 2):
                _connect(a, b)

    if spec and getattr(spec, 'relationships', None):
        for rel in spec.relationships:
            rel_type = (rel.get('type') or rel.get('relationship_type') or '').lower()
            if any(token in rel_type for token in ('connect', 'series', 'parallel')):
                source = rel.get('source') or rel.get('subject')
                target = rel.get('target') or rel.get('object')
                _connect(source, target)

    return graph


def _graph_has_cycle(graph: Dict[str, Set[str]], nodes_subset: Optional[Set[str]] = None) -> bool:
    """Detect cycle in undirected graph (optionally induced subgraph)"""
    visited: Set[str] = set()

    def eligible(node: str) -> bool:
        return node in nodes_subset if nodes_subset else True

    def dfs(node: str, parent: Optional[str]) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if not eligible(neighbor):
                continue
            if neighbor not in visited:
                if dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    for start in graph:
        if not eligible(start) or start in visited:
            continue
        if dfs(start, None):
            return True
    return False


def _group_forces_by_target(scene: Scene) -> Dict[str, List[Dict[str, float]]]:
    """Group force vectors (arrows) by their target mass"""
    grouped: Dict[str, List[Dict[str, float]]] = defaultdict(list)
    for obj in scene.objects:
        if obj.type != PrimitiveType.ARROW:
            continue
        props = obj.properties or {}
        target = props.get('target') or props.get('applies_to') or props.get('attached_to')
        if not target:
            for candidate in scene.objects:
                if candidate.id and candidate.id in (obj.id or ""):
                    target = candidate.id
                    break
        vector = _extract_force_vector(props)
        if target and vector:
            grouped[target].append(vector)
    return grouped


def _extract_force_vector(props: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Normalize force vector components from arrow properties"""
    components = props.get('components')
    if isinstance(components, dict) and 'x' in components and 'y' in components:
        return {
            'x': float(components['x']),
            'y': float(components['y']),
            'magnitude': math.hypot(float(components['x']), float(components['y']))
        }
    if 'dx' in props and 'dy' in props:
        dx = float(props['dx'])
        dy = float(props['dy'])
        return {'x': dx, 'y': dy, 'magnitude': math.hypot(dx, dy)}

    magnitude = float(props.get('magnitude') or props.get('value') or props.get('length') or 0)
    direction = props.get('direction')
    angle_degrees = props.get('angle') or props.get('angle_degrees')
    if isinstance(direction, str) and not angle_degrees:
        direction = direction.lower()
        dir_map = {
            'up': 90.0,
            'down': 270.0,
            'left': 180.0,
            'right': 0.0,
            'upward': 90.0,
            'downward': 270.0
        }
        angle_degrees = dir_map.get(direction)
    if angle_degrees is not None:
        angle_rad = math.radians(float(angle_degrees))
        x = magnitude * math.cos(angle_rad)
        y = magnitude * math.sin(angle_rad)
        return {'x': x, 'y': y, 'magnitude': magnitude or math.hypot(x, y)}

    return None
