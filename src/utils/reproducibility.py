"""
src/utils/reproducibility.py
Experiment reproducibility utility: seed initialization and metadata logging.
"""

import os
import sys
import json
import random
import platform
import datetime
import numpy as np

def set_seed(seed: int = 42):
    """Sets deterministic random seeds across libraries."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

def get_system_metadata() -> dict:
    """Collects verifiable platform and environment metadata."""
    gpu_info = "None (CPU)"
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info = torch.cuda.get_device_name(0)
    except Exception:
        pass

    return {
        "timestamp_iso": datetime.datetime.now().isoformat(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor(),
        "gpu_device": gpu_info,
        "carla_target_version": "0.9.16"
    }

def save_experiment_metadata(output_path: str, extra_info: dict = None):
    """Saves comprehensive experiment provenance metadata to JSON."""
    meta = get_system_metadata()
    if extra_info:
        meta.update(extra_info)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4)
