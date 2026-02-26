"""
Tests for multiple authors support in the project pipeline.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.core.email import EmailRecipient
from academic_doc_generator.project import latex, llm, orchestrator
from academic_doc_generator.core.types import ProjectWorkflowConfig


class TestMultipleAuthors:
    """Tests for multiple authors support."""

    def test_email_recipient_formatting_multiple(self):
        """Test joint salutation and names for multiple recipients."""
        r1 = EmailRecipient(first_name="Max", last_name="Mustermann", gender="Herr", identifier="12345678")
        r2 = EmailRecipient(first_name="Maria", last_name="Musterfrau", gender="Frau", identifier="87654321")

        salutation = EmailRecipient.format_recipients_salutation([r1, r2])
        assert salutation == "Guten Tag Herr Mustermann, guten Tag Frau Musterfrau"

        names = EmailRecipient.format_recipients_full_names([r1, r2])
        assert names == "Herr Max Mustermann (12345678) und Frau Maria Musterfrau (87654321)"

    def test_latex_generation_multiple_authors(self):
        """Test LaTeX generation with multiple authors."""
        students = [
            {"name": "Max Mustermann", "first_name": "Max", "id_number": "11111111", "gender": "Herr"},
            {"name": "Maria Musterfrau", "first_name": "Maria", "id_number": "22222222", "gender": "Frau"}
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author="Mixed", # Should be ignored if students is provided
                title="Joint Project",
                examiner="Prof. Test",
                contact="test@th-koeln.de",
                gender="Herr", # Should be ignored if students is provided
                students=students
            )

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            assert "Max Mustermann" in content
            assert "11111111" in content
            assert "Maria Musterfrau" in content
            assert "22222222" in content
            # Check plural forms
            assert "haben im" in content
            assert "ihr Praxisprojekt" in content
            assert "Sie haben die Note" in content
            # Subject line
            assert "Praxisprojekt Max Mustermann, Maria Musterfrau" in content

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)

    @patch("academic_doc_generator.project.llm.extract_text_per_page")
    def test_extract_project_metadata_multiple(self, mock_extract):
        """Test metadata extraction with multiple authors in JSON."""
        mock_extract.return_value = {0: "Joint work"}

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = json.dumps({
            "students": [
                {"name": "Author One", "first_name": "One", "id_number": "10000001", "email": "one@example.com"},
                {"name": "Author Two", "first_name": "Two", "id_number": "20000002", "email": "two@example.com"}
            ],
            "title": "Group Project",
            "work_type": "Praxisprojekt"
        })

        result = llm.extract_project_metadata("test.pdf", mock_client)

        assert len(result["students"]) == 2
        assert result["students"][0]["name"] == "Author One"
        assert result["students"][1]["name"] == "Author Two"
        # Check backward compatibility fields
        assert result["student_name"] == "Author One"
        assert result["id_number"] == "10000001"

    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.pdf.extract_text_per_page")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    def test_orchestrator_multiple_authors(self, mock_feedback, mock_web, mock_compile, mock_latex, mock_gender, mock_pdf, mock_meta):
        """Test orchestrator pipeline with multiple authors."""
        mock_meta.return_value = {
            "students": [
                {"name": "Student A", "first_name": "A", "id_number": "111"},
                {"name": "Student B", "first_name": "B", "id_number": "222"}
            ],
            "title": "Joint Title",
            "work_type": "WASP"
        }
        mock_pdf.return_value = {0: "text"}
        mock_gender.side_effect = ["Herr", "Frau"]
        mock_compile.return_value = "path/to/pdf"
        mock_feedback.return_value = "- bullet 1\n- bullet 2"

        config = ProjectWorkflowConfig(
            pdf_path="test.pdf",
            output_folder=".",
            compile_pdf=True,
            mark="1.0"
        )

        with patch("academic_doc_generator.project.orchestrator.LLMClient"):
            orchestrator.run_project_pipeline(config)

        # Verify LaTeX call had multiple students
        mock_latex.assert_called_once()
        args, kwargs = mock_latex.call_args
        assert "students" in kwargs
        assert len(kwargs["students"]) == 2
        assert kwargs["students"][0]["gender"] == "Herr"
        assert kwargs["students"][1]["gender"] == "Frau"

        # Verify web metadata call
        mock_web.assert_called_once()
        assert "students" in mock_web.call_args[1]
        assert len(mock_web.call_args[1]["students"]) == 2
