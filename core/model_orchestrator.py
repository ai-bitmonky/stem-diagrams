"""
Model Orchestrator - Complexity-Driven Model Selection
Phase 6B of Planning & Reasoning Roadmap

Orchestrates different models and solvers based on problem complexity:
- Heuristic layout for simple problems (fast)
- Constraint-based layout for medium complexity
- Hybrid approaches for complex problems
- Automatic fallback mechanisms
- Performance monitoring

Architecture:
    Problem → Complexity Assessment → Model Selection → Execution → Result
"""

from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

from core.universal_ai_analyzer import CanonicalProblemSpec, PhysicsDomain
from core.diagram_planner import DiagramPlanner
from core.diagram_plan import DiagramPlan, PlanningStrategy


class ModelType(Enum):
    """Types of models available for diagram generation"""
    HEURISTIC = "heuristic"  # Fast rule-based layout
    CONSTRAINT_SOLVER = "constraint_solver"  # Z3-based optimization
    SYMBOLIC_PHYSICS = "symbolic_physics"  # SymPy equation solving
    GEOMETRY_OPTIMIZER = "geometry_optimizer"  # Shapely packing
    HYBRID = "hybrid"  # Combination of above
    FALLBACK = "fallback"  # Simple fallback


@dataclass
class ModelPerformance:
    """Performance metrics for a model"""
    model_type: ModelType
    success_count: int = 0
    failure_count: int = 0
    total_time: float = 0.0
    average_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def update(self, success: bool, execution_time: float) -> None:
        """Update performance metrics"""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.total_time += execution_time

        total = self.success_count + self.failure_count
        self.average_time = self.total_time / total if total > 0 else 0.0


@dataclass
class OrchestratorResult:
    """Result from model orchestration"""
    success: bool
    model_used: ModelType
    execution_time: float
    result_data: Any = None
    fallback_used: bool = False
    attempts: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'model_used': self.model_used.value if isinstance(self.model_used, ModelType) else self.model_used,
            'execution_time': self.execution_time,
            'fallback_used': self.fallback_used,
            'attempt_count': len(self.attempts),
            'metadata': self.metadata
        }


class ModelOrchestrator:
    """
    Orchestrates model selection and execution based on problem complexity

    Strategies:
    1. Assess problem complexity
    2. Select appropriate model(s)
    3. Execute with fallback
    4. Monitor performance
    5. Adapt based on history
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize model orchestrator

        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_fallback = self.config.get('enable_fallback', True)
        self.max_attempts = self.config.get('max_attempts', 3)
        self.complexity_thresholds = self.config.get('complexity_thresholds', {
            'simple': 0.3,
            'medium': 0.6,
            'complex': 1.0
        })

        # Performance tracking
        self.performance: Dict[ModelType, ModelPerformance] = {
            model_type: ModelPerformance(model_type=model_type)
            for model_type in ModelType
        }

        # Model availability flags
        self._check_model_availability()

    def _check_model_availability(self) -> None:
        """Check which models are available"""
        self.models_available = {
            ModelType.HEURISTIC: True,  # Always available
            ModelType.FALLBACK: True,  # Always available
        }

        # Check Z3
        try:
            from core.solvers.z3_layout_solver import check_z3_availability
            self.models_available[ModelType.CONSTRAINT_SOLVER] = check_z3_availability()
        except ImportError:
            self.models_available[ModelType.CONSTRAINT_SOLVER] = False

        # Check SymPy
        try:
            from core.symbolic.physics_engine import check_sympy_availability
            self.models_available[ModelType.SYMBOLIC_PHYSICS] = check_sympy_availability()
        except ImportError:
            self.models_available[ModelType.SYMBOLIC_PHYSICS] = False

        # Check Shapely
        try:
            from core.symbolic.geometry_engine import check_shapely_availability
            self.models_available[ModelType.GEOMETRY_OPTIMIZER] = check_shapely_availability()
        except ImportError:
            self.models_available[ModelType.GEOMETRY_OPTIMIZER] = False

        # Hybrid available if at least one advanced model is available
        self.models_available[ModelType.HYBRID] = any([
            self.models_available.get(ModelType.CONSTRAINT_SOLVER, False),
            self.models_available.get(ModelType.SYMBOLIC_PHYSICS, False),
            self.models_available.get(ModelType.GEOMETRY_OPTIMIZER, False)
        ])

    # ========== Complexity Assessment ==========

    def assess_complexity(self, spec: CanonicalProblemSpec) -> float:
        """
        Assess problem complexity (0-1 scale)

        Args:
            spec: Problem specification

        Returns:
            Complexity score (0.0 = simple, 1.0 = very complex)
        """
        # Use DiagramPlanner's complexity assessment
        planner = DiagramPlanner()
        return planner.assess_complexity(spec)

    def classify_complexity(self, complexity_score: float) -> str:
        """
        Classify complexity into categories

        Args:
            complexity_score: Complexity score (0-1)

        Returns:
            'simple', 'medium', or 'complex'
        """
        if complexity_score < self.complexity_thresholds['simple']:
            return 'simple'
        elif complexity_score < self.complexity_thresholds['medium']:
            return 'medium'
        else:
            return 'complex'

    # ========== Model Selection ==========

    def select_model(self, spec: CanonicalProblemSpec, plan: Optional[DiagramPlan] = None) -> ModelType:
        """
        Select appropriate model based on problem characteristics

        Args:
            spec: Problem specification
            plan: Optional DiagramPlan (if already created)

        Returns:
            Selected ModelType

        Strategy:
        - Simple problems (complexity < 0.3) → HEURISTIC
        - Medium complexity (0.3-0.6) → CONSTRAINT_SOLVER or SYMBOLIC_PHYSICS
        - High complexity (> 0.6) → HYBRID
        - Falls back based on availability
        """
        # Get complexity
        if plan:
            complexity = plan.complexity_score
        else:
            complexity = self.assess_complexity(spec)

        complexity_class = self.classify_complexity(complexity)

        # Simple problems
        if complexity_class == 'simple':
            return ModelType.HEURISTIC

        # Medium complexity
        elif complexity_class == 'medium':
            # For physics, prefer symbolic solver
            domain_str = spec.domain.value if hasattr(spec.domain, 'value') else str(spec.domain).lower()

            if domain_str in ['mechanics', 'electrostatics'] and self.models_available.get(ModelType.SYMBOLIC_PHYSICS):
                return ModelType.SYMBOLIC_PHYSICS

            # For layout-heavy problems, prefer constraint solver
            elif self.models_available.get(ModelType.CONSTRAINT_SOLVER):
                return ModelType.CONSTRAINT_SOLVER

            # Fallback to heuristic
            else:
                return ModelType.HEURISTIC

        # Complex problems
        else:
            # Try hybrid if available
            if self.models_available.get(ModelType.HYBRID):
                return ModelType.HYBRID

            # Otherwise constraint solver
            elif self.models_available.get(ModelType.CONSTRAINT_SOLVER):
                return ModelType.CONSTRAINT_SOLVER

            # Last resort heuristic
            else:
                return ModelType.HEURISTIC

    # ========== Model Execution ==========

    def execute_model(self,
                     model_type: ModelType,
                     spec: CanonicalProblemSpec,
                     plan: DiagramPlan,
                     **kwargs) -> Tuple[bool, Any, float]:
        """
        Execute a specific model

        Args:
            model_type: Type of model to execute
            spec: Problem specification
            plan: Diagram plan
            **kwargs: Additional arguments for the model

        Returns:
            (success, result, execution_time) tuple

        Raises:
            ValueError: If model type is unknown or unavailable
        """
        if not self.models_available.get(model_type, False):
            raise ValueError(f"Model {model_type} is not available")

        start_time = time.time()

        try:
            if model_type == ModelType.HEURISTIC:
                result = self._execute_heuristic(spec, plan, **kwargs)

            elif model_type == ModelType.CONSTRAINT_SOLVER:
                result = self._execute_constraint_solver(spec, plan, **kwargs)

            elif model_type == ModelType.SYMBOLIC_PHYSICS:
                result = self._execute_symbolic_physics(spec, plan, **kwargs)

            elif model_type == ModelType.GEOMETRY_OPTIMIZER:
                result = self._execute_geometry_optimizer(spec, plan, **kwargs)

            elif model_type == ModelType.HYBRID:
                result = self._execute_hybrid(spec, plan, **kwargs)

            elif model_type == ModelType.FALLBACK:
                result = self._execute_fallback(spec, plan, **kwargs)

            else:
                raise ValueError(f"Unknown model type: {model_type}")

            execution_time = time.time() - start_time
            return (True, result, execution_time)

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Model {model_type} failed: {e}")
            return (False, None, execution_time)

    def _execute_heuristic(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute heuristic layout model"""
        # Simple heuristic placement
        # This would call existing heuristic layout engine
        return {'method': 'heuristic', 'plan': plan}

    def _execute_constraint_solver(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute Z3 constraint solver"""
        from core.solvers.z3_layout_solver import Z3LayoutSolver

        # Get object dimensions
        object_dimensions = kwargs.get('object_dimensions', {})

        # Solve
        solver = Z3LayoutSolver(verbose=False)
        solution = solver.solve_layout(plan, object_dimensions)

        return solution

    def _execute_symbolic_physics(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute SymPy symbolic physics solver"""
        from core.symbolic.physics_engine import SymbolicPhysicsEngine

        engine = SymbolicPhysicsEngine(verbose=False)

        # This would extract forces and solve
        # For now, return placeholder
        return {'method': 'symbolic_physics', 'engine': engine}

    def _execute_geometry_optimizer(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute Shapely geometry optimizer"""
        from core.symbolic.geometry_engine import GeometryEngine

        engine = GeometryEngine(verbose=False)

        # This would do packing/optimization
        return {'method': 'geometry', 'engine': engine}

    def _execute_hybrid(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute hybrid approach"""
        # Try constraint solver first, then geometry optimization
        results = {}

        # Try constraint solver
        if self.models_available.get(ModelType.CONSTRAINT_SOLVER):
            try:
                success, result, _ = self.execute_model(
                    ModelType.CONSTRAINT_SOLVER, spec, plan, **kwargs
                )
                if success:
                    results['constraint_solver'] = result
            except:
                pass

        # Try geometry optimizer
        if self.models_available.get(ModelType.GEOMETRY_OPTIMIZER):
            try:
                success, result, _ = self.execute_model(
                    ModelType.GEOMETRY_OPTIMIZER, spec, plan, **kwargs
                )
                if success:
                    results['geometry'] = result
            except:
                pass

        return results if results else None

    def _execute_fallback(self, spec: CanonicalProblemSpec, plan: DiagramPlan, **kwargs) -> Any:
        """Execute fallback model (always succeeds)"""
        # Very simple fallback layout
        return {'method': 'fallback', 'plan': plan}

    # ========== Orchestration with Fallback ==========

    def generate_with_fallback(self,
                              spec: CanonicalProblemSpec,
                              plan: Optional[DiagramPlan] = None,
                              **kwargs) -> OrchestratorResult:
        """
        Generate diagram with automatic fallback

        Args:
            spec: Problem specification
            plan: Optional pre-computed plan
            **kwargs: Additional arguments

        Returns:
            OrchestratorResult with execution details

        Strategy:
        1. Select primary model based on complexity
        2. Try primary model
        3. If fails and fallback enabled, try simpler models
        4. Record performance metrics
        """
        start_time = time.time()

        # Create plan if not provided
        if plan is None:
            planner = DiagramPlanner()
            plan = planner.plan(spec)

        # Select primary model
        primary_model = self.select_model(spec, plan)

        # Define fallback chain
        fallback_chain = self._get_fallback_chain(primary_model)

        attempts = []
        result_data = None
        model_used = None
        fallback_used = False

        # Try models in fallback chain
        for model_type in fallback_chain[:self.max_attempts]:
            if not self.models_available.get(model_type, False):
                continue

            # Execute model
            success, result, exec_time = self.execute_model(model_type, spec, plan, **kwargs)

            # Record attempt
            attempts.append({
                'model': model_type.value,
                'success': success,
                'time': exec_time
            })

            # Update performance
            self.performance[model_type].update(success, exec_time)

            if success:
                result_data = result
                model_used = model_type
                fallback_used = (model_type != primary_model)
                break

        total_time = time.time() - start_time

        return OrchestratorResult(
            success=(result_data is not None),
            model_used=model_used or ModelType.FALLBACK,
            execution_time=total_time,
            result_data=result_data,
            fallback_used=fallback_used,
            attempts=attempts,
            metadata={
                'primary_model': primary_model.value,
                'complexity': plan.complexity_score,
                'plan_strategy': plan.strategy.value if hasattr(plan.strategy, 'value') else str(plan.strategy)
            }
        )

    def _get_fallback_chain(self, primary_model: ModelType) -> List[ModelType]:
        """
        Get fallback chain for a primary model

        Args:
            primary_model: Primary model to start with

        Returns:
            List of models to try in order

        Example:
            HYBRID → CONSTRAINT_SOLVER → GEOMETRY_OPTIMIZER → HEURISTIC → FALLBACK
        """
        if primary_model == ModelType.HYBRID:
            return [
                ModelType.HYBRID,
                ModelType.CONSTRAINT_SOLVER,
                ModelType.GEOMETRY_OPTIMIZER,
                ModelType.HEURISTIC,
                ModelType.FALLBACK
            ]
        elif primary_model == ModelType.CONSTRAINT_SOLVER:
            return [
                ModelType.CONSTRAINT_SOLVER,
                ModelType.HEURISTIC,
                ModelType.FALLBACK
            ]
        elif primary_model == ModelType.SYMBOLIC_PHYSICS:
            return [
                ModelType.SYMBOLIC_PHYSICS,
                ModelType.HEURISTIC,
                ModelType.FALLBACK
            ]
        elif primary_model == ModelType.GEOMETRY_OPTIMIZER:
            return [
                ModelType.GEOMETRY_OPTIMIZER,
                ModelType.HEURISTIC,
                ModelType.FALLBACK
            ]
        else:  # HEURISTIC or FALLBACK
            return [
                ModelType.HEURISTIC,
                ModelType.FALLBACK
            ]

    # ========== Performance Monitoring ==========

    def get_performance_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all models"""
        stats = {}

        for model_type, perf in self.performance.items():
            if perf.success_count + perf.failure_count > 0:
                stats[model_type.value] = {
                    'success_count': perf.success_count,
                    'failure_count': perf.failure_count,
                    'success_rate': perf.success_rate,
                    'average_time': perf.average_time,
                    'total_time': perf.total_time
                }

        return stats

    def get_best_model(self) -> Tuple[ModelType, float]:
        """
        Get best performing model

        Returns:
            (model_type, success_rate) tuple
        """
        best_model = ModelType.FALLBACK
        best_rate = 0.0

        for model_type, perf in self.performance.items():
            if perf.success_rate > best_rate:
                best_rate = perf.success_rate
                best_model = model_type

        return (best_model, best_rate)

    def reset_performance_stats(self) -> None:
        """Reset all performance statistics"""
        for model_type in self.performance:
            self.performance[model_type] = ModelPerformance(model_type=model_type)

    # ========== Utility Methods ==========

    def get_available_models(self) -> List[ModelType]:
        """Get list of available models"""
        return [model_type for model_type, available in self.models_available.items() if available]

    def __repr__(self) -> str:
        """String representation"""
        available = [m.value for m, a in self.models_available.items() if a]
        return f"ModelOrchestrator(available_models={available})"


# ========== Convenience Functions ==========

def select_best_model_for(spec: CanonicalProblemSpec) -> ModelType:
    """
    Select best model for a specification

    Args:
        spec: Problem specification

    Returns:
        Recommended ModelType
    """
    orchestrator = ModelOrchestrator()
    return orchestrator.select_model(spec)


def execute_with_fallback(spec: CanonicalProblemSpec, **kwargs) -> OrchestratorResult:
    """
    Execute diagram generation with automatic fallback

    Args:
        spec: Problem specification
        **kwargs: Additional arguments

    Returns:
        OrchestratorResult

    Example:
        >>> result = execute_with_fallback(spec)
        >>> if result.success:
        ...     print(f"Used {result.model_used} in {result.execution_time:.3f}s")
    """
    orchestrator = ModelOrchestrator()
    return orchestrator.generate_with_fallback(spec, **kwargs)
