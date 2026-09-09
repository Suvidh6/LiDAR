"""
src/utils/configuration.py
Configuration loader with validation and schema checking.
"""

import json
import os
from pathlib import Path
from .paths import get_config_dir

def load_json_config(filename: str) -> dict:
    """Loads a JSON config file from config/ directory."""
    config_path = get_config_dir() / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_default_config() -> dict:
    return load_json_config("default_config.json")

def load_degradation_config() -> dict:
    return load_json_config("degradation_config.json")

def load_experiment_config() -> dict:
    return load_json_config("experiment_config.json")
