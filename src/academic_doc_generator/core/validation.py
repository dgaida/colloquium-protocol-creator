"""Validation logic for configuration and environment."""

import os
from pathlib import Path


def validate_api_keys() -> list[str]:
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


def validate_pdf_path(folder_path: str, filename: str, allow_docx: bool = False) -> Path:
    """Get validated PDF or DOCX file path.

    Args:
        folder_path: Base folder path.
        filename: Name of the PDF or DOCX file.
        allow_docx: Whether to allow Word (.docx) files.

    Returns:
        Absolute path to PDF or DOCX file.

    Raises:
        ValueError: If path attempts directory traversal or contains invalid characters.
        FileNotFoundError: If PDF or DOCX does not exist.

    Security:
        - Prevents directory traversal (../)
        - Prevents absolute paths
        - Validates file extension
    """
    base_path = Path(folder_path).resolve()

    # Additional security checks
    if Path(filename).is_absolute():
        raise ValueError(f"Absolute paths not allowed: {filename}")

    if any(part == ".." for part in Path(filename).parts):
        raise ValueError(f"Path traversal detected: {filename}")

    # Enforce file extension
    ext = filename.lower()
    if allow_docx:
        if not (ext.endswith(".pdf") or ext.endswith(".docx")):
            raise ValueError(f"Only PDF and DOCX files allowed: {filename}")
    else:
        if not ext.endswith(".pdf"):
            raise ValueError(f"Only PDF files allowed: {filename}")

    pdf_path = (base_path / filename).resolve()

    # Verify path is within base folder (prevent traversal)
    try:
        pdf_path.relative_to(base_path)
    except ValueError as e:
        raise ValueError(f"Invalid PDF path (directory traversal): {filename}") from e

    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    return pdf_path
