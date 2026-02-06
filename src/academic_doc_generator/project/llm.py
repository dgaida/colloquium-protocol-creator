# project_creator/llm.py
"""LLM interface for extracting project work metadata."""

import json
from typing import Dict
from llm_client import LLMClient
from ..core.pdf import extract_text_per_page
from ..core.prompts import PromptTemplate, build_prompt


def extract_project_metadata(pdf_path: str, llm_client: LLMClient) -> Dict[str, str]:
    """Extract metadata from a project work PDF (title page).

    This function reads the first two pages of the PDF and uses an LLM to
    extract relevant information such as student name, matriculation number,
    project title, examiner name, and work type.

    Args:
        pdf_path: Path to the project work PDF file.
        llm_client: LLMClient instance for API access.

    Returns:
        dict: Dictionary containing extracted metadata with keys:
            - "stud_name": Full name of the student
            - "student_first_name": First name only (for gender detection)
            - "stud_id": Student's matriculation number
            - "title": Title of the project work
            - "first_examiner": Name of the first examiner
            - "first_examiner_christian": Christian name of examiner
            - "first_examiner_family": Family name of examiner
            - "work_type": Type of work (e.g., "Praxisprojekt")
    """
    # Extract text from first two pages
    pages_text = extract_text_per_page(pdf_path, max_pages=2)
    sample_text = "\n\n".join(
        [pages_text.get(i, "") for i in sorted(pages_text.keys())]
    )

    prompt = build_prompt(PromptTemplate.EXTRACT_PROJECT_METADATA, text=sample_text)

    messages = [{"role": "user", "content": prompt}]
    content = llm_client.chat_completion(messages)

    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        metadata = {"error": "Could not parse JSON", "raw": content}

    return metadata
