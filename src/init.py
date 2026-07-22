"""
Anti-Manipulation Guardrails Project
MSc Individual Project: Testing defensive prompt engineering strategies
against emotional manipulation of LLMs
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@university.ac.uk"

from .attack_generator import AttackGenerator, AttackPrompt
from .defense_strategies import DefenseStrategies
from .evaluator import ResponseEvaluator
from .experiment_runner import ExperimentRunner

__all__ = [
    'AttackGenerator',
    'AttackPrompt',
    'DefenseStrategies',
    'ResponseEvaluator',
    'ExperimentRunner'
]