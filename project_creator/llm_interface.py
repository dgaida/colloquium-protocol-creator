# project_creator/llm_interface.py
"""LLM interface for extracting project work metadata and determining gender."""

import json
from typing import Dict
from llm_client import LLMClient
from colloquium_creator.pdf_processing import extract_text_per_page


def determine_gender_from_name(first_name: str, llm_client: LLMClient) -> str:
    """Determine the formal German address (Herr/Frau) from a first name using LLM.

    Args:
        first_name: First/given name of the person.
        llm_client: LLMClient instance for API access.

    Returns:
        str: Either "Herr" or "Frau" based on the name.
    """
    prompt = f"""
Based on the following German or international first name, determine whether 
the person should be addressed as "Herr" (Mr.) or "Frau" (Ms./Mrs.) in a 
formal German letter.

First name: {first_name}

Respond with ONLY one word: either "Herr" or "Frau".
If uncertain, respond with "Herr/Frau".
"""

    messages = [{"role": "user", "content": prompt}]
    result = llm_client.chat_completion(messages)

    # Ensure valid output
    if result not in ["Herr", "Frau", "Herr/Frau"]:
        return "Herr/Frau"

    return result


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
            - "student_name": Full name of the student
            - "student_first_name": First name only (for gender detection)
            - "matriculation_number": Student's matriculation number
            - "title": Title of the project work
            - "first_examiner": Name of the first examiner
            - "first_examiner_christian": Christian name of examiner
            - "first_examiner_family": Family name of examiner
            - "work_type": Type of work (e.g., "Praxisprojekt")
    """
    # Extract text from first two pages
    pages_text = extract_text_per_page(pdf_path, max_pages=2)
    sample_text = "\n\n".join([pages_text.get(i, "") for i in sorted(pages_text.keys())])

    prompt = f"""
You are given the first pages of a project work (Praxisprojekt) submitted 
at TH Köln University. Extract the following information if available:

- Student's full name (Autor/Author)
- Student's first name only (Vorname)
- Matriculation number (Matrikelnr.)
- Title of the project work
- First examiner (Erstprüfer/Betreuer)
- Christian name of first examiner
- Family name of first examiner
- Type of work (e.g., "Praxisprojekt", "Projektarbeit")

Return the result as a valid JSON object with keys:
"student_name", "student_first_name", "matriculation_number", "title", 
"first_examiner", "first_examiner_christian", "first_examiner_family", 
"work_type".

If something is missing, use null as the value.
Do not include any extra text, only valid JSON.

Document text:
{sample_text}
"""

    messages = [{"role": "user", "content": prompt}]
    content = llm_client.chat_completion(messages)

    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        metadata = {"error": "Could not parse JSON", "raw": content}

    return metadata
