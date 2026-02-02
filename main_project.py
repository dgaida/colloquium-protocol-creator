# main_project.py
"""Example script for generating project work grading letters."""

import os
from academic_doc_generator import cli

if __name__ == "__main__":
    # Change folder to match your project work folder containing config*.json
    folder = os.path.join("..", "Projektarbeiten", "2025_SoSe", "xy")

    mycfgloader = cli.run_from_config(folder)
