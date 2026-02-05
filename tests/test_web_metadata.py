"""
Unit tests for src/academic_doc_generator/core/web_metadata.py
"""

import os
import tempfile
from unittest.mock import MagicMock
from academic_doc_generator.core import web_metadata


def test_get_initials():
    """Test generation of initials."""
    assert web_metadata.get_initials("Max Mustermann") == "M. M."
    assert web_metadata.get_initials("Max-Moritz Mustermann") == "M. M. M."
    assert web_metadata.get_initials("Max Moritz Mustermann") == "M. M. M."
    assert web_metadata.get_initials(None) == "U. A."
    assert web_metadata.get_initials("Unknown Author") == "U. A."


def test_get_author_slug():
    """Test generation of author slugs."""
    assert web_metadata.get_author_slug("Max Mustermann") == "mamu"
    assert web_metadata.get_author_slug("Max-Moritz Mustermann") == "mamu"
    assert web_metadata.get_author_slug("Mustermann") == "must"
    assert web_metadata.get_author_slug(None) == "unkn"


def test_generate_web_metadata_file():
    """Test generation of web metadata Markdown file."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "This is a test summary for the web."

    pages_text = {0: "Page 1 content", 1: "Page 2 content"}

    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = web_metadata.generate_web_metadata_file(
            output_folder=tmpdir,
            title="Test Thesis",
            author="Max Mustermann",
            pages_text=pages_text,
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="Wintersemester 24/25",
            date_str="2025-01-20",
        )

        assert os.path.exists(md_path)
        assert md_path.endswith("2025_ws2425_ba_mamu.md")

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'title: "Test Thesis"' in content
        assert 'author: "M. M."' in content
        assert 'date: "2025-01-20"' in content
        assert "This is a test summary for the web." in content
        assert 'type: "Bachelorthesis"' in content
        assert 'semester: "Wintersemester 24/25"' in content
