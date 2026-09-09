"""
experiments/scenarios/dynamic_scenario.py
Dynamic degradation scenario definitions for experiments.
"""

from src.evaluation.scenarios import DynamicScenarioEngine

def get_default_scenario_engine():
    """Factory function returning configured dynamic scenario engine."""
    return DynamicScenarioEngine()
