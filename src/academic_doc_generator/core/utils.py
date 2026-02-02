"""Core utility functions for academic-doc-generator."""

from typing import Tuple


def split_student_name(full_name: str) -> Tuple[str, str]:
    """Split a student's full name into first and last name.

    Handles formats like "Last, First" or "First Last".

    Args:
        full_name: The complete name string.

    Returns:
        Tuple of (first_name, last_name).
    """
    if not full_name:
        return "Student", "Name"

    if "," in full_name:
        last_name, first_name = full_name.split(",", 1)
        return first_name.strip(), last_name.strip()

    parts = full_name.split()
    if len(parts) > 1:
        first_name = " ".join(parts[:-1])
        last_name = parts[-1]
        return first_name, last_name

    return full_name, "Name"
