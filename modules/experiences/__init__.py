"""
Módulo de Experiencias Unificadas

Este módulo implementa el sistema de experiencias que integra múltiples elementos
de diferentes sistemas en flujos cohesivos con requisitos compuestos y recompensas combinadas.
"""

from .engine import ExperienceEngine
from .validator import CompositeValidator

__all__ = [
    'ExperienceEngine',
    'CompositeValidator'
]