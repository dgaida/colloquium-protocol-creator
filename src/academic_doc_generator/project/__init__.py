# project_creator/__init__.py
"""
Project Work Grading Letter Creator package.

This package creates LaTeX letters for grading project work (Praxisprojekt)
at TH Köln, reusing infrastructure from the colloquium protocol creator.
"""

from . import latex
from . import llm
from . import orchestrator

__all__ = ["latex", "llm", "orchestrator"]
