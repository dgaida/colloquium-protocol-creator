"""
Unit tests for the pipeline orchestrators and CLIs.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.colloquium import orchestrator as colloquium_orchestrator
from academic_doc_generator.core.types import (
    ColloquiumWorkflowConfig,
    ProjectWorkflowConfig,
)
from academic_doc_generator.project import orchestrator as project_orchestrator
from academic_doc_generator.review import orchestrator as review_orchestrator

# ============================================================================
# Tests for colloquium_pipeline/orchestrator.py
# ============================================================================


class TestColloquiumOrchestrator:
    """Tests for colloquium pipeline orchestrator."""

    @patch("academic_doc_generator.colloquium.orchestrator.llm")
    @patch("academic_doc_generator.colloquium.orchestrator.latex")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf_form_filler")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf")
    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_run_pipeline_basic(
        self, mock_web, mock_pdf_proc, mock_email, mock_form, mock_latex, mock_llm
    ):
        """Test basic pipeline execution."""
        # Setup mocks
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test question?"}]},
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Test summary",
            {
                "author": "Test Author",
                "sid": "12345",
                "title": "Test Title",
                "first_examiner": "Prof. Test",
                "second_examiner": "Dr. Test",
                "first_examiner_christian": "Test",
                "first_examiner_family": "Examiner",
                "bachelor_master": "Bachelor",
            },
        )
        mock_latex.concatenate_comments.return_value = "Seite 1: Test question?"
        mock_latex.compile_latex_to_pdf.return_value = "/test/output.pdf"
        mock_form.fill_form.return_value = "/test/form.pdf"
        mock_web.return_value = "/test/web.md"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_colloquium_email.return_value = "Registration Email Text"
        mock_email_gen.save_email_to_markdown.return_value = "/test/email.md"
        mock_email.EmailGenerator.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ColloquiumWorkflowConfig(
                pdf_path=Path("test.pdf"),
                date="20.01.2026",
                time="14:00",
                llm_client=mock_client,
                groq_free=False,
                output_folder=Path(tmpdir),
                compile_pdf=True,
                location_type="campus",
                room="3.217",
            )
            result = colloquium_orchestrator.run_pipeline(config)

            assert result.tex_path.endswith("bewertung_brief_12345.tex")
            assert result.pdf_path == "/test/output.pdf"
            assert result.email_path == "/test/email.md"
            assert result.metadata_path == "/test/web.md"

            # Verify calls
            mock_llm.rewrite_comments_in_pdf.assert_called_once()
            mock_llm.detect_language.assert_called_once()
            mock_llm.get_summary_and_metadata_of_pdf.assert_called_once()
            mock_latex.create_formal_letter_tex.assert_called_once()
            mock_latex.compile_latex_to_pdf.assert_called_once()

    @patch("academic_doc_generator.colloquium.orchestrator.llm")
    @patch("academic_doc_generator.colloquium.orchestrator.latex")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf_form_filler")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf")
    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_run_pipeline_no_compile(
        self, mock_web, mock_pdf_proc, mock_email, mock_form, mock_latex, mock_llm
    ):
        """Test pipeline without PDF compilation."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {
                "author": "Test",
                "sid": "12345",
                "first_examiner": "Prof",
                "second_examiner": "Dr",
                "first_examiner_christian": "A",
                "first_examiner_family": "B",
                "bachelor_master": "Bachelor",
                "title": "Title",
            },
        )
        mock_latex.concatenate_comments.return_value = "Test"
        mock_form.fill_form.return_value = "/test/form.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_colloquium_email.return_value = "Email"
        mock_email_gen.save_email_to_markdown.return_value = "/test/email.md"
        mock_email.EmailGenerator.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ColloquiumWorkflowConfig(
                pdf_path=Path("test.pdf"),
                date="20.01.2026",
                time="14:00",
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=False,
                location_type="campus",
                room="3.217",
            )
            result = colloquium_orchestrator.run_pipeline(config)

            assert result.tex_path.endswith(".tex")
            assert result.pdf_path == ""  # No PDF compilation
            mock_latex.compile_latex_to_pdf.assert_not_called()

    @patch("academic_doc_generator.colloquium.orchestrator.llm")
    @patch("academic_doc_generator.colloquium.orchestrator.latex")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf_form_filler")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf")
    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_run_pipeline_many_quelle_comments(
        self, mock_web, mock_pdf_proc, mock_email, mock_form, mock_latex, mock_llm
    ):
        """Test pipeline with many 'Quelle' comments."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 5, "language": 0, "ignore": 0},  # Many source comments
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {
                "author": "Test",
                "sid": "12345",
                "first_examiner": "Prof",
                "second_examiner": "Dr",
                "first_examiner_christian": "A",
                "first_examiner_family": "B",
                "bachelor_master": "Bachelor",
                "title": "Title",
            },
        )
        mock_latex.concatenate_comments.return_value = "Test"
        mock_form.fill_form.return_value = "/test/form.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_colloquium_email.return_value = "Email"
        mock_email_gen.save_email_to_markdown.return_value = "/test/email.md"
        mock_email.EmailGenerator.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ColloquiumWorkflowConfig(
                pdf_path=Path("test.pdf"),
                date="20.01.2026",
                time="14:00",
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=False,
                location_type="campus",
                room="3.217",
            )
            colloquium_orchestrator.run_pipeline(config)

            # Check that summary was modified
            create_call = mock_latex.create_formal_letter_tex.call_args
            assert "Häufig fehlen Quellenangaben" in create_call.kwargs["summary"]

    @patch("academic_doc_generator.colloquium.orchestrator.llm")
    @patch("academic_doc_generator.colloquium.orchestrator.latex")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf_form_filler")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf")
    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_run_pipeline_many_language_comments(
        self, mock_web, mock_pdf_proc, mock_email, mock_form, mock_latex, mock_llm
    ):
        """Test pipeline with many language comments."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 0, "language": 6, "ignore": 0},  # Many language comments
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {
                "author": "Test",
                "sid": "12345",
                "first_examiner": "Prof",
                "second_examiner": "Dr",
                "first_examiner_christian": "A",
                "first_examiner_family": "B",
                "bachelor_master": "Bachelor",
                "title": "Title",
            },
        )
        mock_latex.concatenate_comments.return_value = "Test"
        mock_form.fill_form.return_value = "/test/form.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_colloquium_email.return_value = "Email"
        mock_email_gen.save_email_to_markdown.return_value = "/test/email.md"
        mock_email.EmailGenerator.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ColloquiumWorkflowConfig(
                pdf_path=Path("test.pdf"),
                date="20.01.2026",
                time="14:00",
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=False,
                location_type="campus",
                room="3.217",
            )
            colloquium_orchestrator.run_pipeline(config)

            # Check that summary was modified
            create_call = mock_latex.create_formal_letter_tex.call_args
            assert "Viele sprachliche Fehler" in create_call.kwargs["summary"]

    @patch("academic_doc_generator.colloquium.orchestrator.LLMClient")
    @patch("academic_doc_generator.colloquium.orchestrator.llm")
    @patch("academic_doc_generator.colloquium.orchestrator.latex")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf_form_filler")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator")
    @patch("academic_doc_generator.colloquium.orchestrator.pdf")
    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_run_pipeline_auto_client(
        self,
        mock_web,
        mock_pdf_proc,
        mock_email,
        mock_form,
        mock_latex,
        mock_llm,
        mock_client_class,
    ):
        """Test pipeline with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client

        mock_llm.rewrite_comments_in_pdf.return_value = (
            {},
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {
                "author": "Test",
                "sid": "12345",
                "first_examiner": "Prof",
                "second_examiner": "Dr",
                "first_examiner_christian": "A",
                "first_examiner_family": "B",
                "bachelor_master": "Bachelor",
                "title": "Title",
            },
        )
        mock_latex.concatenate_comments.return_value = ""
        mock_form.fill_form.return_value = "/test/form.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_colloquium_email.return_value = "Email"
        mock_email_gen.save_email_to_markdown.return_value = "/test/email.md"
        mock_email.EmailGenerator.return_value = mock_email_gen

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ColloquiumWorkflowConfig(
                pdf_path=Path("test.pdf"),
                date="20.01.2026",
                time="14:00",
                llm_client=None,  # Should auto-create
                output_folder=Path(tmpdir),
                compile_pdf=False,
                location_type="campus",
                room="3.217",
            )
            colloquium_orchestrator.run_pipeline(config)

            mock_client_class.assert_called_once()


# ============================================================================
# Tests for project_pipeline/orchestrator.py
# ============================================================================


class TestProjectOrchestrator:
    """Tests for project pipeline orchestrator."""

    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
    @patch("academic_doc_generator.project.orchestrator.EmailGenerator")
    @patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
    @patch("academic_doc_generator.project.orchestrator.pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    def test_run_project_pipeline_basic(
        self,
        mock_web,
        mock_pdf_proc,
        mock_outlook,
        mock_email,
        mock_compile,
        mock_create,
        mock_feedback,
        mock_gender,
        mock_extract,
    ):
        """Test basic project pipeline execution."""
        mock_extract.return_value = {
            "stud_name": "Test Student",
            "student_first_name": "Test",
            "sid": "99999",
            "title": "Test Project",
            "first_examiner": "Prof. Test",
            "first_examiner_christian": "Test",
            "first_examiner_family": "Examiner",
            "work_type": "Praxisprojekt",
            "student_email": "test@th-koeln.de",
        }
        mock_gender.return_value = "Herr"
        mock_feedback.return_value = "- Feedback item"
        mock_compile.return_value = "/test/output.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_final_mark_email.return_value = "Email"
        mock_email_gen.generate_student_feedback_email.return_value = "Student Email"
        mock_email_gen.save_email_to_markdown.side_effect = [
            "/test/email.md",
            "/test/student_email.md",
        ]
        mock_email.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ProjectWorkflowConfig(
                pdf_path=Path("test.pdf"),
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=True,
            )
            result = project_orchestrator.run_project_pipeline(config)

            assert result.tex_path.endswith("bewertung_projekt_99999.tex")
            assert result.pdf_path == "/test/output.pdf"
            assert result.service_email_path == "/test/email.md"
            assert result.student_email_path == "/test/student_email.md"

            mock_extract.assert_called_once()
            mock_gender.assert_called_once_with("Test", mock_client)
            mock_feedback.assert_called_once()
            mock_create.assert_called_once()
            mock_compile.assert_called_once()

    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.EmailGenerator")
    @patch("academic_doc_generator.project.orchestrator.pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    def test_run_project_pipeline_no_compile(
        self,
        mock_web,
        mock_pdf_proc,
        mock_email,
        mock_create,
        mock_feedback,
        mock_gender,
        mock_extract,
    ):
        """Test project pipeline without compilation."""
        mock_extract.return_value = {
            "stud_name": "Test",
            "student_first_name": "Test",
            "sid": "12345",
            "title": "Test",
            "first_examiner": "Prof",
            "first_examiner_christian": "A",
            "first_examiner_family": "B",
            "work_type": "Praxisprojekt",
        }
        mock_gender.return_value = "Frau"
        mock_feedback.return_value = "Feedback"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_final_mark_email.return_value = "Email"
        mock_email_gen.generate_student_feedback_email.return_value = "Student Email"
        mock_email_gen.save_email_to_markdown.side_effect = [
            "/test/email.md",
            "/test/student_email.md",
        ]
        mock_email.return_value = mock_email_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ProjectWorkflowConfig(
                pdf_path=Path("test.pdf"),
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=False,
            )
            result = project_orchestrator.run_project_pipeline(config)

            assert result.tex_path.endswith(".tex")
            assert result.pdf_path == ""
            assert result.service_email_path == "/test/email.md"
            assert result.student_email_path == "/test/student_email.md"

    @patch("academic_doc_generator.project.orchestrator.LLMClient")
    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    def test_run_project_pipeline_auto_client(
        self,
        mock_web,
        mock_pdf_proc,
        mock_create,
        mock_feedback,
        mock_gender,
        mock_extract,
        mock_client_class,
    ):
        """Test project pipeline with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client

        mock_extract.return_value = {
            "stud_name": "Test",
            "student_first_name": "Test",
            "sid": "12345",
            "title": "Test",
            "first_examiner": "Prof",
            "first_examiner_christian": "A",
            "first_examiner_family": "B",
            "work_type": "Praxisprojekt",
        }
        mock_gender.return_value = "Herr"
        mock_feedback.return_value = "Feedback"

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ProjectWorkflowConfig(
                pdf_path=Path("test.pdf"),
                llm_client=None,
                output_folder=Path(tmpdir),
                compile_pdf=False,
            )
            project_orchestrator.run_project_pipeline(config)

            mock_client_class.assert_called_once()


# ============================================================================
# Tests for review_pipeline/orchestrator.py
# ============================================================================


class TestReviewOrchestrator:
    """Tests for review pipeline orchestrator."""

    @patch("academic_doc_generator.review.orchestrator.extract_text_with_positions")
    @patch("academic_doc_generator.review.orchestrator.extract_annotations_with_positions")
    @patch("academic_doc_generator.review.orchestrator.PdfReader")
    @patch("academic_doc_generator.review.orchestrator.find_annotation_context_with_lines")
    @patch("academic_doc_generator.review.orchestrator.rewrite_comments_markdown")
    @patch("academic_doc_generator.review.orchestrator.create_review_markdown")
    def test_run_review_pipeline_basic(
        self,
        mock_create,
        mock_rewrite,
        mock_context,
        mock_reader,
        mock_annot,
        mock_text,
    ):
        """Test basic review pipeline execution."""
        mock_text.return_value = {0: [{"text": "test", "bbox": (0, 0, 10, 10)}]}
        mock_annot.return_value = ({0: [{"comment": "test"}]}, {"quelle": 0})

        mock_page = MagicMock()
        mock_page.mediabox.top = 792.0
        mock_reader.return_value.pages = [mock_page]

        mock_context.return_value = {1: [{"comment": "test", "line": 10}]}
        mock_rewrite.return_value = {1: [{"rewritten": "Test", "line": 10, "page": 1}]}

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = review_orchestrator.run_review_pipeline(
                "test.pdf",
                llm_client=mock_client,
                groq_free=False,
                output_folder=tmpdir,
            )

            assert md_path.endswith(".md")
            assert "review_comments_" in md_path

            mock_text.assert_called_once()
            mock_annot.assert_called_once()
            mock_context.assert_called_once()
            mock_rewrite.assert_called_once()
            mock_create.assert_called_once()

    @patch("academic_doc_generator.review.orchestrator.LLMClient")
    @patch("academic_doc_generator.review.orchestrator.extract_text_with_positions")
    @patch("academic_doc_generator.review.orchestrator.extract_annotations_with_positions")
    @patch("academic_doc_generator.review.orchestrator.PdfReader")
    @patch("academic_doc_generator.review.orchestrator.find_annotation_context_with_lines")
    @patch("academic_doc_generator.review.orchestrator.rewrite_comments_markdown")
    @patch("academic_doc_generator.review.orchestrator.create_review_markdown")
    def test_run_review_pipeline_auto_client(
        self,
        mock_create,
        mock_rewrite,
        mock_context,
        mock_reader,
        mock_annot,
        mock_text,
        mock_client_class,
    ):
        """Test review pipeline with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client

        mock_text.return_value = {}
        mock_annot.return_value = ({}, {"quelle": 0})
        mock_reader.return_value.pages = []
        mock_context.return_value = {}
        mock_rewrite.return_value = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            review_orchestrator.run_review_pipeline(
                "test.pdf", llm_client=None, output_folder=tmpdir
            )

            mock_client_class.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
