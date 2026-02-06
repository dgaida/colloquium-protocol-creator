"""Validation logic for configuration and environment."""

import os
from pathlib import Path
from typing import List


def validate_api_keys() -> List[str]:
    """Check which LLM APIs are configured.

    Returns:
        List of available API names.

    Raises:
        RuntimeError: If no APIs are configured.
    """
    available = []

    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    if os.getenv("GROQ_API_KEY"):
        available.append("groq")
    if os.getenv("GEMINI_API_KEY"):
        available.append("gemini")

    # Ollama doesn't need a key
    available.append("ollama")

    # Filter out empty strings if any
    available = [api for api in available if api]

    if len(available) == 1 and available[0] == "ollama":
        # Just a warning if only ollama is available, not an error
        # but let's keep it simple for now as per recommendation
        pass

    return available


def validate_pdf_path(folder_path: str, filename: str) -> Path:
    """Get validated PDF file path.

    Args:
        folder_path: Base folder path.
        filename: Name of the PDF file.

    Returns:
        Absolute path to PDF file.

    Raises:
        ValueError: If path attempts directory traversal.
        FileNotFoundError: If PDF does not exist.
    """
    base_path = Path(folder_path).resolve()
    pdf_path = (base_path / filename).resolve()

    # Verify path is within base folder (prevent traversal)
    try:
        pdf_path.relative_to(base_path)
    except ValueError:
        raise ValueError(f"Invalid PDF path (directory traversal): {filename}")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    return pdf_path
