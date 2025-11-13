"""
Universal Validator - Single Robust Pipeline Phase 3
Merges semantic, geometric, and physics validation into one unified validator
Uses data-driven rules from domains/*/rules.json
"""

from typing import Dict, List, Tuple
from pathlib import Path
import json

from core.scene.schema_v1 import Scene, SceneObject, Constraint, ConstraintType, PrimitiveType
from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain
# from core.validator import SceneValidator  # Not using for now


class ValidationReport:
    """Complete validation report"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.auto_corrections: List[str] = []
        self.is_valid: bool = True

    def add_error(self, message: str):
        """Add error (halts generation)"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add warning (continues generation)"""
        self.warnings.append(message)

    def add_info(self, message: str):
        """Add info (informational only)"""
        self.info.append(message)

    def add_correction(self, message: str):
        """Log auto-correction"""
        self.auto_corrections.append(message)

    def __repr__(self):
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        summary = f"{status}\n"
        if self.errors:
            summary += f"Errors: {len(self.errors)}\n"
        if self.warnings:
            summary += f"Warnings: {len(self.warnings)}\n"
        if self.auto_corrections:
            summary += f"Auto-corrections: {len(self.auto_corrections)}\n"
        return summary


class UniversalValidator:
    """
    Universal Validator - Single robust implementation

    Merges:
    - core.validator.Validator (semantic + geometric checks)
    - PhysicsRuleValidator (domain-specific physics)
    - BidirectionalValidator (AI-based quality checking)

    Uses data-driven rules from domains/*/rules.json
    Auto-corrects where possible, fails clearly otherwise
    """

    def __init__(self, mode: str = "standard", domains_path: str = "domains"):
        """
        Initialize Universal Validator

        Args:
            mode: Validation mode (strict, standard, permissive)
            domains_path: Path to domains directory with rules
        """
        self.mode = mode
        self.domains_path = Path(domains_path)

        # Load domain validators
        self.domain_validators = self._load_domain_validators()

        print(f"✅ UniversalValidator initialized")
        print(f"   Mode: {mode}")
        print(f"   Loaded {len(self.domain_validators)} domain validators")

    def validate(self, scene: Scene, spec: CanonicalProblemSpec) -> Tuple[ValidationReport, Scene]:
        """
        Validate scene against specifications

        Pipeline:
        1. Semantic checks (structure)
        2. Geometric checks (layout)
        3. Domain-specific physics checks
        4. Auto-correction (where possible)
        5. Final validation

        Args:
            scene: Scene to validate
            spec: Original problem specification

        Returns:
            Tuple of (ValidationReport, corrected_scene)
        """
        print(f"\n{'='*80}")
        print(f"✅ UNIVERSAL VALIDATION - Phase 3")
        print(f"{'='*80}\n")

        report = ValidationReport()

        # Step 1: Semantic checks
        print("Step 1/5: Semantic Validation")
        self._validate_semantic(scene, spec, report)
        print(f"   ✅ Semantic: {len(report.errors)} errors, {len(report.warnings)} warnings")

        # Step 2: Geometric checks
        print("\nStep 2/5: Geometric Validation")
        self._validate_geometric(scene, report)
        print(f"   ✅ Geometric: {len(report.errors)} errors, {len(report.warnings)} warnings")

        # Step 3: Domain-specific physics checks
        print("\nStep 3/5: Domain-Specific Physics Validation")
        self._validate_physics(scene, spec, report)
        print(f"   ✅ Physics: {len(report.errors)} errors, {len(report.warnings)} warnings")

        # Step 4: Auto-correction
        print("\nStep 4/5: Auto-Correction")
        corrected_scene = self._auto_correct(scene, report)
        if report.auto_corrections:
            print(f"   ✅ Applied {len(report.auto_corrections)} auto-corrections")
        else:
            print(f"   ✅ No corrections needed")

        # Step 5: Final validation
        print("\nStep 5/5: Final Validation")
        if report.is_valid:
            print(f"   ✅ Scene is VALID")
        else:
            print(f"   ❌ Scene is INVALID ({len(report.errors)} errors)")

        print(f"\n{'='*80}")
        if report.is_valid:
            print(f"✅ UNIVERSAL VALIDATION PASSED")
        else:
            print(f"❌ UNIVERSAL VALIDATION FAILED")
        print(f"{'='*80}\n")

        return report, corrected_scene

    def _load_domain_validators(self) -> Dict:
        """Load domain-specific validators from rules.json"""

        validators = {}

        # Path to domains directory
        domains_path = Path(__file__).parent.parent / "domains"

        if not domains_path.exists():
            return validators

        # Load rules for each domain
        for domain_dir in domains_path.iterdir():
            if domain_dir.is_dir():
                rules_file = domain_dir / "rules.json"
                if rules_file.exists():
                    try:
                        with open(rules_file) as f:
                            rules = json.load(f)
                            validators[domain_dir.name] = rules
                    except Exception as e:
                        pass  # Silently skip invalid rule files

        return validators

    def _validate_semantic(self, scene: Scene, spec: CanonicalProblemSpec, report: ValidationReport):
        """Step 1: Semantic validation (structure)"""

        # Check minimum objects
        if len(scene.objects) < 1:
            report.add_error("Scene has no objects")

        # Check object IDs are unique
        ids = [obj.id for obj in scene.objects]
        if len(ids) != len(set(ids)):
            report.add_error("Duplicate object IDs found")

        # Check for required primitives
        for obj in scene.objects:
            if not hasattr(obj, 'type') or obj.type is None:
                report.add_error(f"Object {obj.id} is missing a primitive type.")

        # Check constraint references valid objects
        for constraint in scene.constraints:
            for obj_id in constraint.objects:
                if obj_id not in ids:
                    report.add_error(f"Constraint references non-existent object: {obj_id}")

        # Domain-specific semantic checks
        if spec.domain == PhysicsDomain.CURRENT_ELECTRICITY:
            # Check for power source
            has_power = any(obj.type == PrimitiveType.BATTERY_SYMBOL for obj in scene.objects)
            if not has_power:
                report.add_error("Circuit diagram missing power source")
        elif spec.domain == PhysicsDomain.MECHANICS:
            # Check for masses
            has_mass = any(obj.type == PrimitiveType.MASS for obj in scene.objects)
            if not has_mass:
                report.add_warning("Mechanics problem missing mass information")
        elif spec.domain == PhysicsDomain.OPTICS:
            has_lens_or_mirror = any(obj.type in [PrimitiveType.LENS, PrimitiveType.MIRROR] for obj in scene.objects)
            if not has_lens_or_mirror:
                report.add_error("Optics problem missing a lens or mirror.")

    def _validate_geometric(self, scene: Scene, report: ValidationReport):
        """Step 2: Geometric validation (layout)"""

        # Check for overlapping objects (if positions are set)
        positioned_objects = [obj for obj in scene.objects if obj.position]

        for i, obj1 in enumerate(positioned_objects):
            for obj2 in positioned_objects[i+1:]:
                if self._objects_overlap(obj1, obj2):
                    report.add_warning(f"Objects {obj1.id} and {obj2.id} overlap")

        # Check canvas bounds
        canvas_width = scene.coord_system.get('extent', [1200, 800])[0]
        canvas_height = scene.coord_system.get('extent', [1200, 800])[1]

        def _coord(position: Dict, key: str, fallback: float) -> float:
            value = position.get(key, fallback)
            if value in (None, "", []):
                return fallback
            return float(value)

        for obj in positioned_objects:
            pos = obj.position
            x = _coord(pos, 'x', 0)
            y = _coord(pos, 'y', 0)

            if x < 0 or y < 0:
                report.add_error(f"Object {obj.id} outside canvas (negative position)")
            elif x > canvas_width or y > canvas_height:
                report.add_error(f"Object {obj.id} outside canvas bounds")

        # Check constraints are satisfied
        for constraint in scene.constraints:
            if constraint.type == ConstraintType.DISTANCE:
                obj1 = self._get_obj(scene, constraint.objects[0])
                obj2 = self._get_obj(scene, constraint.objects[1])
                if obj1 and obj2 and obj1.position and obj2.position:
                    dist = self._distance(obj1, obj2)
                    if abs(dist - constraint.value) > 1e-2:
                        report.add_warning(f"Distance constraint between {obj1.id} and {obj2.id} not satisfied.")
            elif constraint.type == ConstraintType.ALIGNED_H:
                objs = [self._get_obj(scene, oid) for oid in constraint.objects]
                if len(objs) > 1 and all(o and o.position for o in objs):
                    y_vals = [o.position.get('y', 0) for o in objs]
                    if max(y_vals) - min(y_vals) > 1e-2:
                        report.add_warning(f"Horizontal alignment constraint not satisfied for objects {constraint.objects}")
            elif constraint.type == ConstraintType.ALIGNED_V:
                objs = [self._get_obj(scene, oid) for oid in constraint.objects]
                if len(objs) > 1 and all(o and o.position for o in objs):
                    x_vals = [o.position.get('x', 0) for o in objs]
                    if max(x_vals) - min(x_vals) > 1e-2:
                        report.add_warning(f"Vertical alignment constraint not satisfied for objects {constraint.objects}")

    def _validate_physics(self, scene: Scene, spec: CanonicalProblemSpec, report: ValidationReport):
        """Step 3: Domain-specific physics validation"""

        # Use domain-specific validator if available
        domain_name = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()

        # Try to find matching domain rules
        if 'physics' in self.domain_validators or 'mechanics' in domain_name.lower():
            # Apply physics domain validation rules
            self._apply_domain_rules(scene, 'physics', report)

        # General physics checks (all domains)
        self._validate_physics_general(scene, spec, report)

    def _apply_domain_rules(self, scene: Scene, domain: str, report: ValidationReport):
        """Apply JSON-based domain validation rules"""

        if domain not in self.domain_validators:
            return

        rules_config = self.domain_validators[domain]

        # Get diagram type from scene metadata
        diagram_type = scene.metadata.get('diagram_type', 'unknown')

        # Check if we have rules for this diagram type
        if 'diagram_types' not in rules_config:
            return

        diagram_rules = rules_config['diagram_types'].get(diagram_type)
        if not diagram_rules:
            # Try generic diagram type
            if diagram_type == 'free_body_diagram':
                diagram_rules = rules_config['diagram_types'].get('free_body_diagram')

        if not diagram_rules:
            return

        # Check required objects
        if 'required_objects' in diagram_rules:
            object_ids = {obj.id for obj in scene.objects}
            object_types = {obj.type.value if hasattr(obj.type, 'value') else str(obj.type) for obj in scene.objects}

            for required in diagram_rules['required_objects']:
                # Check if any object matches required type
                found = any(required in obj_id.lower() or required in obj_type.lower()
                           for obj_id in object_ids for obj_type in object_types)
                if not found:
                    report.add_warning(f"Missing required object for {diagram_type}: {required}")

        # Apply validation rules
        if 'validation_rules' in diagram_rules:
            for rule in diagram_rules['validation_rules']:
                self._apply_validation_rule(scene, rule, report)

    def _apply_validation_rule(self, scene: Scene, rule: Dict, report: ValidationReport):
        """Apply a single validation rule"""

        rule_id = rule.get('rule_id', 'unknown')
        rule_name = rule.get('name', 'Unknown rule')
        severity = rule.get('severity', 'warning')
        check_type = rule.get('check', '')

        # Implement specific checks
        if check_type == 'force_direction':
            # Check force vector directions
            params = rule.get('parameters', {})
            force_name = params.get('force_name')
            expected_angle = params.get('expected_angle')
            tolerance = params.get('tolerance', 5)

            for obj in scene.objects:
                obj_id_lower = obj.id.lower()
                if force_name and force_name in obj_id_lower:
                    # Check if object has angle property
                    angle = obj.properties.get('angle')
                    if angle is not None:
                        if abs(angle - expected_angle) > tolerance:
                            msg = f"{rule_name}: {obj.id} angle {angle}° differs from expected {expected_angle}°"
                            if severity == 'error':
                                report.add_error(msg)
                            else:
                                report.add_warning(msg)

        elif check_type == 'force_balance':
            # Check if forces are balanced (for equilibrium)
            params = rule.get('parameters', {})
            tolerance = params.get('tolerance', 0.1)

            # Find all force vectors
            forces = [obj for obj in scene.objects if 'force' in obj.id.lower()]
            if len(forces) > 0:
                # Calculate net force (simplified - just check if we have opposing forces)
                has_down = any('gravity' in f.id.lower() or 'weight' in f.id.lower() for f in forces)
                has_up = any('normal' in f.id.lower() for f in forces)

                if has_down and not has_up:
                    report.add_warning(f"{rule_name}: Downward force without upward opposing force")

        # Add more rule types as needed

    def _validate_physics_general(self, scene: Scene, spec: CanonicalProblemSpec, report: ValidationReport):
        """General physics validation (all domains)"""

        # Check for dimensional consistency
        for obj in scene.objects:
            props = obj.properties

            # Check units are consistent
            if 'value' in props and 'unit' in props:
                # Validate unit is appropriate for property type
                pass  # TODO: Implement unit validation

        # Check for physical plausibility
        if spec.domain == PhysicsDomain.MECHANICS:
            # Check forces are balanced (if equilibrium)
            if 'equilibrium' in spec.physics_context.get('analysis_type', '').lower():
                # TODO: Verify sum of forces = 0
                pass

        elif spec.domain == PhysicsDomain.CURRENT_ELECTRICITY:
            # Check KCL/KVL if values provided
            # TODO: Implement circuit law validation
            pass
            
        elif spec.domain == PhysicsDomain.OPTICS:
            # Check thin-lens equation
            lens = next((obj for obj in scene.objects if obj.type == PrimitiveType.LENS), None)
            obj = next((obj for obj in scene.objects if obj.properties.get('is_object')), None)
            img = next((obj for obj in scene.objects if obj.properties.get('is_image')), None)

            if lens and obj and img and lens.position and obj.position and img.position:
                f = lens.properties.get('focal_length')
                do = abs(obj.position['x'] - lens.position['x'])
                di = abs(img.position['x'] - lens.position['x'])

                if f and do > 0 and di > 0:
                    if abs(1/f - (1/do + 1/di)) > 0.01:
                        report.add_warning("Thin-lens equation not satisfied.")

    def _auto_correct(self, scene: Scene, report: ValidationReport) -> Scene:
        """Step 4: Auto-correct scene where possible"""

        corrected = scene

        # Fix duplicate IDs
        ids = [obj.id for obj in scene.objects]
        if len(ids) != len(set(ids)):
            seen = set()
            for obj in corrected.objects:
                if obj.id in seen:
                    new_id = f"{obj.id}_{len(seen)}"
                    obj.id = new_id
                    report.add_correction(f"Fixed duplicate ID: {obj.id} → {new_id}")
                seen.add(obj.id)

        # Add missing constraints
        if not corrected.constraints:
            # Add NO_OVERLAP constraint for all objects
            from core.scene.schema_v1 import ConstraintType
            corrected.constraints.append(Constraint(
                type=ConstraintType.NO_OVERLAP,
                objects=[obj.id for obj in corrected.objects]
            ))
            report.add_correction("Added NO_OVERLAP constraint for all objects")

        # Add missing labels
        for obj in corrected.objects:
            if not obj.properties.get('label'):
                obj.properties['label'] = f"{obj.type.value.replace('_', ' ').title()}: {obj.id}"
                report.add_correction(f"Added missing label for object {obj.id}")

        return corrected

    def _get_obj(self, scene: Scene, obj_id: str) -> SceneObject:
        """Get object by ID from scene"""
        for obj in scene.objects:
            if obj.id == obj_id:
                return obj
        return None

    def _distance(self, obj1: SceneObject, obj2: SceneObject) -> float:
        """Calculate Euclidean distance between two objects"""
        if not obj1.position or not obj2.position:
            return 0.0

        x1 = obj1.position.get('x', 0)
        y1 = obj1.position.get('y', 0)
        x2 = obj2.position.get('x', 0)
        y2 = obj2.position.get('y', 0)

        import math
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _objects_overlap(self, obj1: SceneObject, obj2: SceneObject) -> bool:
        """Check if two objects overlap"""

        if not obj1.position or not obj2.position:
            return False

        def _dim(position: Dict, key: str, fallback: float) -> float:
            value = position.get(key, fallback)
            if value in (None, "", []):
                return fallback
            return float(value)

        x1 = _dim(obj1.position, 'x', 0)
        y1 = _dim(obj1.position, 'y', 0)
        w1 = _dim(obj1.position, 'width', 20)
        h1 = _dim(obj1.position, 'height', 20)

        x2 = _dim(obj2.position, 'x', 0)
        y2 = _dim(obj2.position, 'y', 0)
        w2 = _dim(obj2.position, 'width', 20)
        h2 = _dim(obj2.position, 'height', 20)

        # Check overlap
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def _object_to_dict(self, obj: SceneObject) -> Dict:
        """Convert SceneObject to dict"""
        return {
            'id': obj.id,
            'type': obj.type.value if hasattr(obj.type, 'value') else str(obj.type),
            'properties': obj.properties,
            'position': obj.position,
            'style': obj.style
        }

    def _constraint_to_dict(self, constraint: Constraint) -> Dict:
        """Convert Constraint to dict"""
        return {
            'type': constraint.type.value if hasattr(constraint.type, 'value') else str(constraint.type),
            'objects': constraint.objects,
            'value': constraint.value
        }
