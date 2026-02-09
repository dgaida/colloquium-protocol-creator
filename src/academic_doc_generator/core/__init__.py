# colloquium_creator/__init__.py
"""
Colloquium Protocol Creator package.

This package contains helpers to:
 - extract text / annotations from PDFs (docling + pypdf),
 - call an LLM (Groq) to rewrite comments and summarize,
 - generate LaTeX letters and compile them.

Public API is organized in submodules.
"""

from . import latex, llm, pdf, utils

__all__ = [
    "pdf",
    "llm",
    "latex",
    "utils",
]
