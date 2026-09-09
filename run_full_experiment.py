"""
run_full_experiment.py
Top-level entry point to execute the complete unified multimodal sensor fusion research experiment.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.run_full_experiment import run_all_experiments

if __name__ == "__main__":
    run_all_experiments()
