import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest
import sys

# We need to mock docling and related before importing the script
for m in [
    'docling', 'docling.datamodel', 'docling.document_converter',
    'docling_core', 'docling_core.types', 'docling_core.types.doc',
    'docling_core.types.doc.page', 'docling_core.types.doc.base',
    'docling_parse', 'docling_parse.pdf_parser', 'llm_client'
]:
    sys.modules[m] = MagicMock()

# Import the modules that the script will use, so we can patch them at the right place
import academic_doc_generator.core.pdf
import academic_doc_generator.project.llm
import academic_doc_generator.core.llm
import academic_doc_generator.core.metadata
import scripts.generate_web_metadata_recursive as script

def test_process_folder_project(tmp_path):
    folder = tmp_path / "project_folder"
    folder.mkdir()
    config_file = "config_dgaida2.github.json"
    config_path = folder / config_file

    config_content = {
      "task": "project",
      "pdf": { "filename": "RAG Chatbot Report.pdf" },
      "project": { "mark": None, "work_type": "Informatikprojekt" },
      "llm": { "model": "openai/gpt-oss-120b" }
    }

    with open(config_path, "w") as f:
        json.dump(config_content, f)

    pdf_path = folder / "RAG Chatbot Report.pdf"
    pdf_path.write_text("%PDF-1.4 dummy")

    with patch('scripts.generate_web_metadata_recursive.pdf.extract_text_per_page') as mock_pdf, \
         patch('scripts.generate_web_metadata_recursive.extract_project_metadata') as mock_extract, \
         patch('scripts.generate_web_metadata_recursive.llm.summarize_thesis') as mock_summarize, \
         patch('scripts.generate_web_metadata_recursive.metadata.generate_metadata_file') as mock_gen_md, \
         patch('scripts.generate_web_metadata_recursive.LLMClient') as mock_llm_client_class:

        mock_pdf.return_value = {0: "Sample text"}
        mock_extract.return_value = {"title": "Test Project", "student_name": "Max Mustermann", "work_type": "Informatikprojekt", "students": []}
        mock_summarize.return_value = "Summary text"
        mock_gen_md.return_value = "generated.md"

        mock_llm_client = MagicMock()
        mock_llm_client.chat_completion.return_value = "German"
        mock_llm_client_class.return_value = mock_llm_client

        script.process_folder(str(folder), config_file)

        mock_extract.assert_called_once()
        mock_summarize.assert_called_once()
        mock_gen_md.assert_called_once()

        # Verify it used current date
        args, kwargs = mock_gen_md.call_args
        assert kwargs['date_str'] == datetime.now().strftime("%Y-%m-%d")

def test_process_folder_colloquium_missing_date(tmp_path):
    folder = tmp_path / "colloquium_folder"
    folder.mkdir()
    config_file = "config_colloquium.json"
    config_path = folder / config_file

    config_content = {
      "task": "colloquium",
      "pdf": { "filename": "thesis.pdf" },
      "llm": { "model": "gpt-4" }
    }

    with open(config_path, "w") as f:
        json.dump(config_content, f)

    pdf_path = folder / "thesis.pdf"
    pdf_path.write_text("%PDF-1.4 dummy")

    with patch('scripts.generate_web_metadata_recursive.LLMClient') as mock_llm_client_class:
        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client

        with patch('scripts.generate_web_metadata_recursive.llm.get_summary_and_metadata_of_pdf') as mock_get:
            script.process_folder(str(folder), config_file)
            mock_get.assert_not_called()
