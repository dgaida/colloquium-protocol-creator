"""
Unit tests for the pipeline orchestrators and CLIs.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch, call
from colloquium_pipeline import orchestrator as colloquium_orchestrator
from colloquium_pipeline import cli as colloquium_cli
from project_pipeline import orchestrator as project_orchestrator
from project_pipeline import cli as project_cli
from review_pipeline import orchestrator as review_orchestrator


# ============================================================================
# Tests for colloquium_pipeline/orchestrator.py
# ============================================================================

class TestColloquiumOrchestrator:
    """Tests for colloquium pipeline orchestrator."""

    @patch('colloquium_pipeline.orchestrator.llm_interface')
    @patch('colloquium_pipeline.orchestrator.latex_generation')
    def test_run_pipeline_basic(self, mock_latex, mock_llm):
        """Test basic pipeline execution."""
        # Setup mocks
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test question?"}]},
            {"quelle": 0, "language": 0, "ignore": 0}
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Test summary",
            {
                "author": "Test Author",
                "matriculation_number": "12345",
                "title": "Test Title",
                "first_examiner": "Prof. Test",
                "second_examiner": "Dr. Test",
                "first_examiner_christian": "Test",
                "first_examiner_family": "Examiner",
                "bachelor_master": "Bachelor"
            }
        )
        mock_latex.concatenate_comments.return_value = "Seite 1: Test question?"
        mock_latex.compile_latex_to_pdf.return_value = "/test/output.pdf"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tex, pdf = colloquium_orchestrator.run_pipeline(
                "test.pdf",
                llm_client=mock_client,
                groq_free=False,
                output_folder=tmpdir,
                compile_pdf=True
            )
            
            assert tex.endswith("bewertung_brief_12345.tex")
            assert pdf == "/test/output.pdf"
            
            # Verify calls
            mock_llm.rewrite_comments_in_pdf.assert_called_once()
            mock_llm.detect_language.assert_called_once()
            mock_llm.get_summary_and_metadata_of_pdf.assert_called_once()
            mock_latex.create_formal_letter_tex.assert_called_once()
            mock_latex.compile_latex_to_pdf.assert_called_once()

    @patch('colloquium_pipeline.orchestrator.llm_interface')
    @patch('colloquium_pipeline.orchestrator.latex_generation')
    def test_run_pipeline_no_compile(self, mock_latex, mock_llm):
        """Test pipeline without PDF compilation."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 0, "language": 0, "ignore": 0}
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {"author": "Test", "matriculation_number": "12345",
             "first_examiner": "Prof", "second_examiner": "Dr",
             "first_examiner_christian": "A", "first_examiner_family": "B",
             "bachelor_master": "Bachelor", "title": "Title"}
        )
        mock_latex.concatenate_comments.return_value = "Test"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tex, pdf = colloquium_orchestrator.run_pipeline(
                "test.pdf",
                llm_client=mock_client,
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            assert tex.endswith(".tex")
            assert pdf == ""  # No PDF compilation
            mock_latex.compile_latex_to_pdf.assert_not_called()

    @patch('colloquium_pipeline.orchestrator.llm_interface')
    @patch('colloquium_pipeline.orchestrator.latex_generation')
    def test_run_pipeline_many_quelle_comments(self, mock_latex, mock_llm):
        """Test pipeline with many 'Quelle' comments."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 5, "language": 0, "ignore": 0}  # Many source comments
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {"author": "Test", "matriculation_number": "12345",
             "first_examiner": "Prof", "second_examiner": "Dr",
             "first_examiner_christian": "A", "first_examiner_family": "B",
             "bachelor_master": "Bachelor", "title": "Title"}
        )
        mock_latex.concatenate_comments.return_value = "Test"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            colloquium_orchestrator.run_pipeline(
                "test.pdf",
                llm_client=mock_client,
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            # Check that summary was modified
            create_call = mock_latex.create_formal_letter_tex.call_args
            assert "Häufig fehlen Quellenangaben" in create_call.kwargs["summary"]

    @patch('colloquium_pipeline.orchestrator.llm_interface')
    @patch('colloquium_pipeline.orchestrator.latex_generation')
    def test_run_pipeline_many_language_comments(self, mock_latex, mock_llm):
        """Test pipeline with many language comments."""
        mock_llm.rewrite_comments_in_pdf.return_value = (
            {1: [{"rewritten": "Test"}]},
            {"quelle": 0, "language": 6, "ignore": 0}  # Many language comments
        )
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {"author": "Test", "matriculation_number": "12345",
             "first_examiner": "Prof", "second_examiner": "Dr",
             "first_examiner_christian": "A", "first_examiner_family": "B",
             "bachelor_master": "Bachelor", "title": "Title"}
        )
        mock_latex.concatenate_comments.return_value = "Test"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            colloquium_orchestrator.run_pipeline(
                "test.pdf",
                llm_client=mock_client,
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            # Check that summary was modified
            create_call = mock_latex.create_formal_letter_tex.call_args
            assert "Viele sprachliche Fehler" in create_call.kwargs["summary"]

    @patch('colloquium_pipeline.orchestrator.LLMClient')
    @patch('colloquium_pipeline.orchestrator.llm_interface')
    @patch('colloquium_pipeline.orchestrator.latex_generation')
    def test_run_pipeline_auto_client(self, mock_latex, mock_llm, mock_client_class):
        """Test pipeline with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client
        
        mock_llm.rewrite_comments_in_pdf.return_value = ({}, {"quelle": 0, "language": 0, "ignore": 0})
        mock_llm.detect_language.return_value = "German"
        mock_llm.get_summary_and_metadata_of_pdf.return_value = (
            "Summary",
            {"author": "Test", "matriculation_number": "12345",
             "first_examiner": "Prof", "second_examiner": "Dr",
             "first_examiner_christian": "A", "first_examiner_family": "B",
             "bachelor_master": "Bachelor", "title": "Title"}
        )
        mock_latex.concatenate_comments.return_value = ""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            colloquium_orchestrator.run_pipeline(
                "test.pdf",
                llm_client=None,  # Should auto-create
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            mock_client_class.assert_called_once()


# ============================================================================
# Tests for colloquium_pipeline/cli.py
# ============================================================================

class TestColloquiumCLI:
    """Tests for colloquium pipeline CLI."""

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_basic(self, mock_run, mock_client_class):
        """Test basic CLI execution."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client
        
        mock_run.return_value = ("/test.tex", "/test.pdf")
        
        colloquium_cli.main(["test.pdf"])
        
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["compile_pdf"] is True
        assert call_kwargs["groq_free"] is False

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_with_api_choice(self, mock_run, mock_client_class):
        """Test CLI with API choice."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/test.tex", "")
        
        colloquium_cli.main(["test.pdf", "--api", "groq"])
        
        mock_client_class.assert_called_once_with(api_choice="groq", llm=None)

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_with_model(self, mock_run, mock_client_class):
        """Test CLI with model specification."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/test.tex", "")
        
        colloquium_cli.main(["test.pdf", "--model", "gpt-4o"])
        
        mock_client_class.assert_called_once_with(api_choice=None, llm="gpt-4o")

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_groq_free(self, mock_run, mock_client_class):
        """Test CLI with groq-free flag."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/test.tex", "")
        
        colloquium_cli.main(["test.pdf", "--groq-free"])
        
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["groq_free"] is True

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_no_compile(self, mock_run, mock_client_class):
        """Test CLI with no-compile flag."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/test.tex", "")
        
        colloquium_cli.main(["test.pdf", "--no-compile"])
        
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["compile_pdf"] is False

    @patch('colloquium_pipeline.cli.LLMClient')
    @patch('colloquium_pipeline.cli.run_pipeline')
    def test_cli_custom_output(self, mock_run, mock_client_class):
        """Test CLI with custom output folder."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/custom/test.tex", "")
        
        colloquium_cli.main(["test.pdf", "--out", "/custom"])
        
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["output_folder"] == "/custom"

    @patch('colloquium_pipeline.cli.LLMClient')
    def test_cli_client_error(self, mock_client_class):
        """Test CLI handling of client initialization error."""
        mock_client_class.side_effect = Exception("API key not found")
        
        # Should not raise, just print error
        colloquium_cli.main(["test.pdf"])


# ============================================================================
# Tests for project_pipeline/orchestrator.py
# ============================================================================

class TestProjectOrchestrator:
    """Tests for project pipeline orchestrator."""

    @patch('project_pipeline.orchestrator.extract_project_metadata')
    @patch('project_pipeline.orchestrator.determine_gender_from_name')
    @patch('project_pipeline.orchestrator.create_project_grading_letter_tex')
    @patch('project_pipeline.orchestrator.compile_latex_to_pdf')
    def test_run_project_pipeline_basic(self, mock_compile, mock_create, 
                                       mock_gender, mock_extract):
        """Test basic project pipeline execution."""
        mock_extract.return_value = {
            "student_name": "Test Student",
            "student_first_name": "Test",
            "matriculation_number": "99999",
            "title": "Test Project",
            "first_examiner": "Prof. Test",
            "first_examiner_christian": "Test",
            "first_examiner_family": "Examiner",
            "work_type": "Praxisprojekt"
        }
        mock_gender.return_value = "Herr"
        mock_compile.return_value = "/test/output.pdf"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tex, pdf = project_orchestrator.run_project_pipeline(
                "test.pdf",
                llm_client=mock_client,
                output_folder=tmpdir,
                compile_pdf=True
            )
            
            assert tex.endswith("projektarbeit_brief_99999.tex")
            assert pdf == "/test/output.pdf"
            
            mock_extract.assert_called_once()
            mock_gender.assert_called_once_with("Test", mock_client)
            mock_create.assert_called_once()
            mock_compile.assert_called_once()

    @patch('project_pipeline.orchestrator.extract_project_metadata')
    @patch('project_pipeline.orchestrator.determine_gender_from_name')
    @patch('project_pipeline.orchestrator.create_project_grading_letter_tex')
    def test_run_project_pipeline_no_compile(self, mock_create, mock_gender, mock_extract):
        """Test project pipeline without compilation."""
        mock_extract.return_value = {
            "student_name": "Test",
            "student_first_name": "Test",
            "matriculation_number": "12345",
            "title": "Test",
            "first_examiner": "Prof",
            "first_examiner_christian": "A",
            "first_examiner_family": "B",
            "work_type": "Praxisprojekt"
        }
        mock_gender.return_value = "Frau"
        
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tex, pdf = project_orchestrator.run_project_pipeline(
                "test.pdf",
                llm_client=mock_client,
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            assert tex.endswith(".tex")
            assert pdf == ""

    @patch('project_pipeline.orchestrator.LLMClient')
    @patch('project_pipeline.orchestrator.extract_project_metadata')
    @patch('project_pipeline.orchestrator.determine_gender_from_name')
    @patch('project_pipeline.orchestrator.create_project_grading_letter_tex')
    def test_run_project_pipeline_auto_client(self, mock_create, mock_gender,
                                             mock_extract, mock_client_class):
        """Test project pipeline with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client
        
        mock_extract.return_value = {
            "student_name": "Test",
            "student_first_name": "Test",
            "matriculation_number": "12345",
            "title": "Test",
            "first_examiner": "Prof",
            "first_examiner_christian": "A",
            "first_examiner_family": "B",
            "work_type": "Praxisprojekt"
        }
        mock_gender.return_value = "Herr"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_orchestrator.run_project_pipeline(
                "test.pdf",
                llm_client=None,
                output_folder=tmpdir,
                compile_pdf=False
            )
            
            mock_client_class.assert_called_once()


# ============================================================================
# Tests for project_pipeline/cli.py
# ============================================================================

class TestProjectCLI:
    """Tests for project pipeline CLI."""

    @patch('project_pipeline.cli.LLMClient')
    @patch('project_pipeline.cli.run_project_pipeline')
    def test_cli_basic(self, mock_run, mock_client_class):
        """Test basic project CLI execution."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client
        
        mock_run.return_value = ("/test.tex", "/test.pdf")
        
        project_cli.main(["test.pdf"])
        
        mock_run.assert_called_once()

    @patch('project_pipeline.cli.LLMClient')
    @patch('project_pipeline.cli.run_project_pipeline')
    def test_cli_custom_signature(self, mock_run, mock_client_class):
        """Test project CLI with custom signature."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_run.return_value = ("/test.tex", "")
        
        project_cli.main(["test.pdf", "--signature", "my_sig.png"])
        
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["signature_file"] == "my_sig.png"


# ============================================================================
# Tests for review_pipeline/orchestrator.py
# ============================================================================

class TestReviewOrchestrator:
    """Tests for review pipeline orchestrator."""

    @patch('review_pipeline.orchestrator.extract_text_with_positions')
    @patch('review_pipeline.orchestrator.extract_annotations_with_positions')
    @patch('review_pipeline.orchestrator.PdfReader')
    @patch('review_pipeline.orchestrator.find_annotation_context_with_lines')
    @patch('review_pipeline.orchestrator.rewrite_comments_markdown')
    @patch('review_pipeline.orchestrator.create_review_markdown')
    def test_run_review_pipeline_basic(self, mock_create, mock_rewrite,
                                      mock_context, mock_reader,
                                      mock_annot, mock_text):
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
                output_folder=tmpdir
            )
            
            assert md_path.endswith(".md")
            assert "review_comments_" in md_path
            
            mock_text.assert_called_once()
            mock_annot.assert_called_once()
            mock_context.assert_called_once()
            mock_rewrite.assert_called_once()
            mock_create.assert_called_once()

    @patch('review_pipeline.orchestrator.LLMClient')
    @patch('review_pipeline.orchestrator.extract_text_with_positions')
    @patch('review_pipeline.orchestrator.extract_annotations_with_positions')
    @patch('review_pipeline.orchestrator.PdfReader')
    @patch('review_pipeline.orchestrator.find_annotation_context_with_lines')
    @patch('review_pipeline.orchestrator.rewrite_comments_markdown')
    @patch('review_pipeline.orchestrator.create_review_markdown')
    def test_run_review_pipeline_auto_client(self, mock_create, mock_rewrite,
                                            mock_context, mock_reader,
                                            mock_annot, mock_text,
                                            mock_client_class):
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
                "test.pdf",
                llm_client=None,
                output_folder=tmpdir
            )
            
            mock_client_class.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
