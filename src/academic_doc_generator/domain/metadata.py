"""Generation of web-compatible metadata files for student projects."""

import os
from datetime import datetime
from typing import Dict, Optional
from ..core.types import LLMClientProtocol
from ..core.prompts import PromptTemplate, build_prompt


def get_initials(name: str) -> str:
    """Generate initials for a name (e.g., 'Max Mustermann' -> 'M. M.')."""
    if not name or name in ["Unknown Author", "Unknown", "Unbekannt"]:
        return "U. A."
    # Replace hyphens with spaces to treat as separate parts
    name_clean = name.replace("-", " ")
    parts = name_clean.split()
    initials = [p[0].upper() + "." for p in parts if p]
    return " ".join(initials)


def get_author_slug(name: str) -> str:
    """Generate a short slug from the author's name."""
    if not name or name in ["Unknown Author", "Unknown", "Unbekannt"]:
        return "unkn"
    # Replace hyphens with spaces
    name_clean = name.replace("-", " ")
    parts = name_clean.split()
    if len(parts) >= 2:
        first = parts[0][:2].lower()
        last = parts[-1][:2].lower()
        return first + last
    elif len(parts) == 1:
        return parts[0][:4].lower()
    return "unkn"


def summarize_for_web(pages_text: Dict[int, str], llm_client: LLMClientProtocol) -> str:
    """Generate a concise, English summary suitable for publication on a website."""
    # Use first 10 pages as in the original script
    text_to_summarize = "\n\n".join(
        [pages_text.get(i, "") for i in sorted(pages_text.keys())[:10]]
    )

    prompt = build_prompt(PromptTemplate.SUMMARIZE_FOR_WEB, text=text_to_summarize)
    messages = [{"role": "user", "content": prompt}]
    return llm_client.chat_completion(messages).strip()


def generate_metadata_file(
    output_folder: str,
    title: str,
    author: str,
    pages_text: Dict[int, str],
    llm_client: LLMClientProtocol,
    work_type: str,  # e.g., "Bachelorthesis", "Masterthesis", "Praxisprojekt"
    semester: str,
    date_str: Optional[str] = None,
) -> str:
    """Create a Jekyll-style Markdown file with frontmatter for a student project.

    Args:
        output_folder: Folder where the .md file will be saved.
        title: Title of the work.
        author: Full name of the student.
        pages_text: Extracted text from the PDF.
        llm_client: LLM client for summary generation.
        work_type: String indicating the type of work.
        semester: Semester name (e.g., "Wintersemester 24/25").
        date_str: Date of the work (YYYY-MM-DD). Defaults to today.

    Returns:
        Path to the generated .md file.
    """
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    summary = summarize_for_web(pages_text, llm_client)
    initials = get_initials(author)
    author_slug = get_author_slug(author)

    # Clean up summary: replace full author name with initials if it appears
    if author and author not in ["Unknown Author", "Unknown", "Unbekannt"]:
        summary = summary.replace(author, initials)

    # Create .md filename
    # format: {year}_{semester_slug}_{type_slug}_{author_slug}.md
    year = date_str[:4]

    # Try to make a slug from semester
    sem_slug = (
        semester.lower()
        .replace(" ", "")
        .replace("/", "")
        .replace("wintersemester", "ws")
        .replace("sommersemester", "ss")
    )

    type_slug = work_type[:2].lower()

    md_filename = f"{year}_{sem_slug}_{type_slug}_{author_slug}.md"
    md_path = os.path.join(output_folder, md_filename)

    content = f"""---
title: "{title}"
author: "{initials}"
date: "{date_str}"
excerpt: |
  {summary}
collection: student_projects
type: "{work_type}"
semester: "{semester}"
---

{summary}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    return md_path
