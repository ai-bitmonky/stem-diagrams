"""
Domain-specific interpreters for rich scene generation
"""

# New Universal Pipeline interpreters
from .capacitor_interpreter import CapacitorInterpreter
from .optics_interpreter import OpticsInterpreter
from .mechanics_interpreter import MechanicsInterpreter

# Legacy interpreters (if available)
try:
    from .domain_interpreters import (
        ElectrostaticsInterpreter,
        SceneInterpreterFactory
    )
    _has_legacy = True
except ImportError:
    _has_legacy = False

__all__ = [
    'CapacitorInterpreter',
    'OpticsInterpreter',
    'MechanicsInterpreter'
]

if _has_legacy:
    __all__.extend([
        'ElectrostaticsInterpreter',
        'SceneInterpreterFactory'
    ])
