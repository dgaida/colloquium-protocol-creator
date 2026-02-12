"""
Comprehensive unit tests for src/academic_doc_generator/cli/handlers.py
Ziel: Coverage von 11% auf >90% erhöhen
"""

from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.cli import handlers


class TestRunFromConfig:
    """Tests für run_from_config Funktion."""

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_pipeline")
    def test_run_from_config_colloquium_success(
        self, mock_run_pipeline, mock_validate_pdf, mock_llm_class, mock_load_config
    ):
        """Test erfolgreiche Colloquium-Konfiguration."""
        # Setup mock config
        mock_config = MagicMock()
        mock_config.folder_path = Path("/test/folder")
        mock_config.get_task.return_value = "colloquium"
        mock_config.config = {
            "pdf": {"filename": "test.pdf"},
        }
        mock_config.get_llm_config.return_value = {
            "api_choice": "openai",
            "model": "gpt-4o",
            "groq_free": False,
        }
        mock_config.get_output_config.return_value = {
            "folder": "/output",
            "compile_pdf": True,
            "fill_form_only": False,
        }
        mock_config.get_colloquium_config.return_value = {
            "date": "20.01.2026",
            "time": "14:00",
            "location_type": "campus",
            "room": "3.217",
        }
        mock_config.get_gemini_emark_config.return_value = {
            "enabled": False,
            "model": "gemini-2.0-flash-exp",
        }
        mock_load_config.return_value = mock_config

        # Setup LLM client
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_llm_class.return_value = mock_client

        # Setup PDF validation
        mock_validate_pdf.return_value = Path("/test/folder/test.pdf")

        # Setup pipeline result
        mock_result = MagicMock()
        mock_result.get_task.return_value = "colloquium"
        mock_result.tex_path = "/output/test.tex"
        mock_result.pdf_path = "/output/test.pdf"
        mock_result.email_path = "/output/email.md"
        mock_result.metadata_path = "/output/metadata.md"
        mock_run_pipeline.return_value = mock_result

        # Execute
        handlers.run_from_config("/test/config.json")

        # Verify
        mock_load_config.assert_called_once_with("/test/config.json")
        mock_llm_class.assert_called_once()
        mock_validate_pdf.assert_called_once()
        mock_run_pipeline.assert_called_once()

    @patch("academic_doc_generator.cli.handlers.load_config")
    def test_run_from_config_load_error(self, mock_load_config):
        """Test Fehlerbehandlung beim Laden der Config."""
        mock_load_config.side_effect = FileNotFoundError("Config not found")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_from_config("/nonexistent/config.json")

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    def test_run_from_config_llm_error(self, mock_llm_class, mock_load_config):
        """Test Fehlerbehandlung bei LLM-Initialisierung."""
        mock_config = MagicMock()
        mock_config.get_task.return_value = "colloquium"
        mock_config.get_llm_config.return_value = {}
        mock_load_config.return_value = mock_config

        mock_llm_class.side_effect = Exception("LLM init failed")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_from_config("/test/config.json")

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    def test_run_from_config_pdf_validation_error(
        self, mock_validate_pdf, mock_llm_class, mock_load_config
    ):
        """Test Fehlerbehandlung bei PDF-Validierung."""
        mock_config = MagicMock()
        mock_config.folder_path = Path("/test")
        mock_config.get_task.return_value = "colloquium"
        mock_config.config = {"pdf": {"filename": "test.pdf"}}
        mock_config.get_llm_config.return_value = {}
        mock_load_config.return_value = mock_config

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.side_effect = FileNotFoundError("PDF not found")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_from_config("/test/config.json")

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_project_pipeline")
    def test_run_from_config_project(
        self, mock_run_project, mock_validate_pdf, mock_llm_class, mock_load_config
    ):
        """Test Projekt-Konfiguration."""
        mock_config = MagicMock()
        mock_config.folder_path = Path("/test")
        mock_config.get_task.return_value = "project"
        mock_config.config = {"pdf": {"filename": "project.pdf"}}
        mock_config.get_llm_config.return_value = {}
        mock_config.get_output_config.return_value = {
            "folder": None,
            "compile_pdf": True,
            "signature_file": "signature.png",
            "create_feedback_mail": True,
        }
        mock_config.get_project_config.return_value = {"mark": "1.3"}
        mock_load_config.return_value = mock_config

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.return_value = Path("/test/project.pdf")

        mock_result = MagicMock()
        mock_result.tex_path = "/test/output.tex"
        mock_run_project.return_value = mock_result

        handlers.run_from_config("/test/config.json")

        mock_run_project.assert_called_once()

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_review_pipeline")
    def test_run_from_config_review(
        self, mock_run_review, mock_validate_pdf, mock_llm_class, mock_load_config
    ):
        """Test Review-Konfiguration."""
        mock_config = MagicMock()
        mock_config.folder_path = Path("/test")
        mock_config.get_task.return_value = "review"
        mock_config.config = {"pdf": {"filename": "paper.pdf"}}
        mock_config.get_llm_config.return_value = {"groq_free": True}
        mock_config.get_output_config.return_value = {"folder": "/output"}
        mock_load_config.return_value = mock_config

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.return_value = Path("/test/paper.pdf")
        mock_run_review.return_value = "/output/review.md"

        handlers.run_from_config("/test/config.json")

        mock_run_review.assert_called_once()


class TestRunColloquiumDirect:
    """Tests für run_colloquium_direct Funktion."""

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_pipeline")
    def test_run_colloquium_direct_success(
        self, mock_run_pipeline, mock_validate_pdf, mock_llm_class
    ):
        """Test erfolgreiche direkte Colloquium-Ausführung."""
        args = Namespace(
            pdf="/test/thesis.pdf",
            date="20.01.2026",
            time="14:00",
            location_type="campus",
            room="3.217",
            api="openai",
            model="gpt-4o",
            groq_free=False,
            gemini_eval=False,
            gemini_model="gemini-2.0-flash-exp",
            gemini_upload_pdf=False,
            out="/output",
            no_compile=False,
            company_name=None,
            company_address=None,
            zoom_link=None,
            zcode=None,
        )

        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_llm_class.return_value = mock_client

        mock_validate_pdf.return_value = Path("/test/thesis.pdf")

        mock_result = MagicMock()
        mock_result.tex_path = "/output/test.tex"
        mock_result.pdf_path = "/output/test.pdf"
        mock_result.email_path = "/output/email.md"
        mock_result.metadata_path = "/output/metadata.md"
        mock_run_pipeline.return_value = mock_result

        handlers.run_colloquium_direct(args)

        mock_llm_class.assert_called_once()
        mock_run_pipeline.assert_called_once()

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    def test_run_colloquium_direct_llm_error(self, mock_llm_class):
        """Test LLM-Initialisierungsfehler."""
        args = Namespace(
            pdf="/test/thesis.pdf",
            date="20.01.2026",
            time="14:00",
            location_type="campus",
            room="3.217",
            api="invalid",
            model=None,
        )

        mock_llm_class.side_effect = Exception("Invalid API")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_colloquium_direct(args)

        assert exc_info.value.code == 1


class TestRunProjectDirect:
    """Tests für run_project_direct Funktion."""

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_project_pipeline")
    def test_run_project_direct_success(self, mock_run_project, mock_validate_pdf, mock_llm_class):
        """Test erfolgreiche direkte Projekt-Ausführung."""
        args = Namespace(
            pdf="/test/project.pdf",
            api="groq",
            model="llama",
            out="/output",
            no_compile=False,
            signature="signature.png",
            mark="1.3",
            create_feedback_mail=True,
        )

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.return_value = Path("/test/project.pdf")

        mock_result = MagicMock()
        mock_result.tex_path = "/output/test.tex"
        mock_run_project.return_value = mock_result

        handlers.run_project_direct(args)

        mock_run_project.assert_called_once()


class TestRunReviewDirect:
    """Tests für run_review_direct Funktion."""

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.run_review_pipeline")
    def test_run_review_direct_success(self, mock_run_review, mock_llm_class):
        """Test erfolgreiche direkte Review-Ausführung."""
        args = Namespace(
            pdf="/test/paper.pdf",
            api="openai",
            model="gpt-4o",
            groq_free=False,
            out="/output",
        )

        mock_llm_class.return_value = MagicMock()
        mock_run_review.return_value = "/output/review.md"

        handlers.run_review_direct(args)

        mock_run_review.assert_called_once_with(
            pdf_path="/test/paper.pdf",
            llm_client=mock_llm_class.return_value,
            groq_free=False,
            output_folder="/output",
        )
