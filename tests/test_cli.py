"""
Unit tests for src/academic_doc_generator/cli.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from io import StringIO

from academic_doc_generator import cli


class TestRunFromConfig:
    """Tests für run_from_config Funktion."""

    @patch("academic_doc_generator.cli.load_config")
    @patch("academic_doc_generator.cli.LLMClient")
    def test_run_colloquium_from_config(self, mock_llm_client_class, mock_load_config):
        """Test Ausführung eines Kolloquiums via Config."""
        # Mock Config
        mock_config = MagicMock()
        mock_config.get_task.return_value = "colloquium"
        mock_config.get_llm_config.return_value = {
            "api_choice": "openai",
            "model": "gpt-4o",
            "groq_free": False,
        }
        mock_config.get_output_config.return_value = {
            "folder": "/tmp/output",
            "compile_pdf": True,
            "fill_form_only": False,
        }
        mock_config.get_pdf_path.return_value = "/tmp/test.pdf"
        mock_config.get_colloquium_config.return_value = {
            "date": "20.01.2026",
            "time": "14:00",
            "location_type": "campus",
            "room": "3.217",
        }
        mock_load_config.return_value = mock_config

        # Mock LLMClient
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_llm_client_class.return_value = mock_client

        # Mock run_pipeline
        with patch("academic_doc_generator.cli.run_pipeline") as mock_run_pipeline:
            mock_run_pipeline.return_value = (
                "/tmp/test.tex",
                "/tmp/test.pdf",
                "/tmp/email.md",
            )

            cli.run_from_config("config.json")

            # Verify calls
            mock_load_config.assert_called_once_with("config.json")
            mock_llm_client_class.assert_called_once_with(
                api_choice="openai", llm="gpt-4o"
            )
            mock_run_pipeline.assert_called_once()

            # Check run_pipeline arguments
            call_kwargs = mock_run_pipeline.call_args.kwargs
            assert call_kwargs["pdf_path"] == "/tmp/test.pdf"
            assert call_kwargs["date_colloquium"] == "20.01.2026"
            assert call_kwargs["uhrzeit_colloquium"] == "14:00"
            assert call_kwargs["location_type"] == "campus"
            assert call_kwargs["room"] == "3.217"

    @patch("academic_doc_generator.cli.load_config")
    @patch("academic_doc_generator.cli.LLMClient")
    def test_run_project_from_config(self, mock_llm_client_class, mock_load_config):
        """Test Ausführung eines Projekts via Config."""
        mock_config = MagicMock()
        mock_config.get_task.return_value = "project"
        mock_config.get_llm_config.return_value = {"api_choice": "groq", "model": None}
        mock_config.get_output_config.return_value = {
            "folder": "/tmp/output",
            "compile_pdf": True,
            "signature_file": "sig.png",
        }
        mock_config.get_pdf_path.return_value = "/tmp/project.pdf"
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.api_choice = "groq"
        mock_client.llm = "llama-3.3-70b-versatile"
        mock_llm_client_class.return_value = mock_client

        with patch(
            "academic_doc_generator.cli.run_project_pipeline"
        ) as mock_run_pipeline:
            mock_run_pipeline.return_value = ("/tmp/project.tex", "/tmp/project.pdf")

            cli.run_from_config("config.json")

            mock_run_pipeline.assert_called_once()
            call_kwargs = mock_run_pipeline.call_args.kwargs
            assert call_kwargs["pdf_path"] == "/tmp/project.pdf"
            assert call_kwargs["signature_file"] == "sig.png"

    @patch("academic_doc_generator.cli.load_config")
    @patch("academic_doc_generator.cli.LLMClient")
    def test_run_review_from_config(self, mock_llm_client_class, mock_load_config):
        """Test Ausführung eines Reviews via Config."""
        mock_config = MagicMock()
        mock_config.get_task.return_value = "review"
        mock_config.get_llm_config.return_value = {
            "api_choice": None,
            "model": None,
            "groq_free": True,
        }
        mock_config.get_output_config.return_value = {"folder": "/tmp/output"}
        mock_config.get_pdf_path.return_value = "/tmp/paper.pdf"
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_llm_client_class.return_value = mock_client

        with patch(
            "academic_doc_generator.cli.run_review_pipeline"
        ) as mock_run_pipeline:
            mock_run_pipeline.return_value = "/tmp/review.md"

            cli.run_from_config("config.json")

            mock_run_pipeline.assert_called_once()
            call_kwargs = mock_run_pipeline.call_args.kwargs
            assert call_kwargs["groq_free"] is True

    @patch("academic_doc_generator.cli.load_config")
    def test_run_from_config_file_not_found(self, mock_load_config):
        """Test Fehlerbehandlung bei nicht existierender Config."""
        mock_load_config.side_effect = FileNotFoundError("Config not found")

        with pytest.raises(SystemExit) as exc_info:
            cli.run_from_config("nonexistent.json")

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.load_config")
    def test_run_from_config_invalid_config(self, mock_load_config):
        """Test Fehlerbehandlung bei ungültiger Config."""
        mock_load_config.side_effect = ValueError("Invalid task")

        with pytest.raises(SystemExit) as exc_info:
            cli.run_from_config("invalid.json")

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.load_config")
    @patch("academic_doc_generator.cli.LLMClient")
    def test_run_from_config_llm_error(self, mock_llm_client_class, mock_load_config):
        """Test Fehlerbehandlung bei LLM-Client-Fehler."""
        mock_config = MagicMock()
        mock_config.get_llm_config.return_value = {}
        mock_load_config.return_value = mock_config

        mock_llm_client_class.side_effect = Exception("API key missing")

        with pytest.raises(SystemExit) as exc_info:
            cli.run_from_config("config.json")

        assert exc_info.value.code == 1


class TestRunColloquiumDirect:
    """Tests für run_colloquium_direct Funktion."""

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_pipeline")
    def test_run_colloquium_direct_campus(self, mock_pipeline, mock_llm_class):
        """Test direkte Ausführung eines Campus-Kolloquiums."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_llm_class.return_value = mock_client

        mock_pipeline.return_value = ("/tmp/test.tex", "/tmp/test.pdf", "/tmp/email.md")

        args = MagicMock()
        args.pdf = "test.pdf"
        args.date = "20.01.2026"
        args.time = "14:00"
        args.location_type = "campus"
        args.room = "3.217"
        args.company_name = None
        args.company_address = None
        args.zoom_link = None
        args.zoom_passcode = None
        args.api = "openai"
        args.model = "gpt-4o"
        args.groq_free = False
        args.out = "/tmp/output"
        args.no_compile = False

        cli.run_colloquium_direct(args)

        mock_llm_class.assert_called_once_with(api_choice="openai", llm="gpt-4o")
        mock_pipeline.assert_called_once()

        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["pdf_path"] == "test.pdf"
        assert call_kwargs["date_colloquium"] == "20.01.2026"
        assert call_kwargs["compile_pdf"] is True
        assert call_kwargs["location_type"] == "campus"

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_pipeline")
    def test_run_colloquium_direct_online(self, mock_pipeline, mock_llm_class):
        """Test direkte Ausführung eines Online-Kolloquiums."""
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        mock_pipeline.return_value = ("/tmp/test.tex", "", "/tmp/email.md")

        args = MagicMock()
        args.pdf = "test.pdf"
        args.date = "30.01.2026"
        args.time = "15:30"
        args.location_type = "online"
        args.zoom_link = "https://zoom.us/j/123"
        args.zoom_passcode = "test123"
        args.room = None
        args.company_name = None
        args.company_address = None
        args.api = None
        args.model = None
        args.groq_free = True
        args.out = None
        args.no_compile = True

        cli.run_colloquium_direct(args)

        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["location_type"] == "online"
        assert call_kwargs["zoom_link"] == "https://zoom.us/j/123"
        assert call_kwargs["groq_free"] is True
        assert call_kwargs["compile_pdf"] is False

    @patch("academic_doc_generator.cli.LLMClient")
    def test_run_colloquium_direct_llm_error(self, mock_llm_class):
        """Test Fehlerbehandlung bei LLM-Fehler."""
        mock_llm_class.side_effect = Exception("API error")

        args = MagicMock()
        args.api = "openai"
        args.model = "gpt-4o"

        with pytest.raises(SystemExit) as exc_info:
            cli.run_colloquium_direct(args)

        assert exc_info.value.code == 1


class TestRunProjectDirect:
    """Tests für run_project_direct Funktion."""

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_project_pipeline")
    def test_run_project_direct_basic(self, mock_pipeline, mock_llm_class):
        """Test direkte Ausführung eines Projekts."""
        mock_client = MagicMock()
        mock_client.api_choice = "groq"
        mock_client.llm = "llama-3.3-70b-versatile"
        mock_llm_class.return_value = mock_client

        mock_pipeline.return_value = ("/tmp/project.tex", "/tmp/project.pdf")

        args = MagicMock()
        args.pdf = "project.pdf"
        args.api = "groq"
        args.model = None
        args.out = "/tmp/out"
        args.no_compile = False
        args.signature = "sig.png"

        cli.run_project_direct(args)

        mock_pipeline.assert_called_once()
        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["pdf_path"] == "project.pdf"
        assert call_kwargs["signature_file"] == "sig.png"
        assert call_kwargs["compile_pdf"] is True

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_project_pipeline")
    def test_run_project_direct_no_compile(self, mock_pipeline, mock_llm_class):
        """Test Projekt ohne Kompilierung."""
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        mock_pipeline.return_value = ("/tmp/project.tex", "")

        args = MagicMock()
        args.pdf = "project.pdf"
        args.api = None
        args.model = None
        args.out = None
        args.no_compile = True
        args.signature = "signature.png"

        cli.run_project_direct(args)

        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["compile_pdf"] is False


class TestRunReviewDirect:
    """Tests für run_review_direct Funktion."""

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_review_pipeline")
    def test_run_review_direct_basic(self, mock_pipeline, mock_llm_class):
        """Test direkte Ausführung eines Reviews."""
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        mock_pipeline.return_value = "/tmp/review.md"

        args = MagicMock()
        args.pdf = "paper.pdf"
        args.api = "openai"
        args.model = "gpt-4o"
        args.groq_free = False
        args.out = "/tmp/out"

        cli.run_review_direct(args)

        mock_pipeline.assert_called_once()
        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["pdf_path"] == "paper.pdf"
        assert call_kwargs["groq_free"] is False

    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_review_pipeline")
    def test_run_review_direct_groq_free(self, mock_pipeline, mock_llm_class):
        """Test Review mit Groq Free Tier."""
        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client
        mock_pipeline.return_value = "/tmp/review.md"

        args = MagicMock()
        args.pdf = "paper.pdf"
        args.api = "groq"
        args.model = None
        args.groq_free = True
        args.out = None

        cli.run_review_direct(args)

        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["groq_free"] is True


class TestCreateParser:
    """Tests für create_parser Funktion."""

    def test_create_parser_structure(self):
        """Test Parser-Struktur."""
        parser = cli.create_parser()

        assert parser.prog == "academic-doc-generator"

        # Check global arguments
        actions = {action.dest: action for action in parser._actions}
        assert "config" in actions
        assert "list_templates" in actions

    def test_parser_colloquium_subcommand(self):
        """Test Colloquium Subcommand."""
        parser = cli.create_parser()

        args = parser.parse_args(
            [
                "colloquium",
                "test.pdf",
                "--date",
                "20.01.2026",
                "--time",
                "14:00",
                "--room",
                "3.217",
            ]
        )

        assert args.command == "colloquium"
        assert args.pdf == "test.pdf"
        assert args.date == "20.01.2026"
        assert args.time == "14:00"
        assert args.room == "3.217"
        assert args.location_type == "campus"  # default

    def test_parser_colloquium_online(self):
        """Test Online-Kolloquium Argumente."""
        parser = cli.create_parser()

        args = parser.parse_args(
            [
                "colloquium",
                "test.pdf",
                "--date",
                "30.01.2026",
                "--time",
                "15:30",
                "--location-type",
                "online",
                "--zoom-link",
                "https://zoom.us/j/123",
                "--zoom-passcode",
                "test123",
            ]
        )

        assert args.location_type == "online"
        assert args.zoom_link == "https://zoom.us/j/123"
        assert args.zoom_passcode == "test123"

    def test_parser_colloquium_company(self):
        """Test Firmen-Kolloquium Argumente."""
        parser = cli.create_parser()

        args = parser.parse_args(
            [
                "colloquium",
                "test.pdf",
                "--date",
                "25.01.2026",
                "--time",
                "10:00",
                "--location-type",
                "company",
                "--company-name",
                "Beispiel GmbH",
                "--company-address",
                "Musterstraße 42",
            ]
        )

        assert args.location_type == "company"
        assert args.company_name == "Beispiel GmbH"
        assert args.company_address == "Musterstraße 42"

    def test_parser_project_subcommand(self):
        """Test Project Subcommand."""
        parser = cli.create_parser()

        args = parser.parse_args(["project", "project.pdf", "--signature", "sig.png"])

        assert args.command == "project"
        assert args.pdf == "project.pdf"
        assert args.signature == "sig.png"

    def test_parser_review_subcommand(self):
        """Test Review Subcommand."""
        parser = cli.create_parser()

        args = parser.parse_args(["review", "paper.pdf", "--groq-free"])

        assert args.command == "review"
        assert args.pdf == "paper.pdf"
        assert args.groq_free is True

    def test_parser_llm_options(self):
        """Test LLM-Optionen."""
        parser = cli.create_parser()

        args = parser.parse_args(
            ["project", "test.pdf", "--api", "openai", "--model", "gpt-4o"]
        )

        assert args.api == "openai"
        assert args.model == "gpt-4o"

    def test_parser_output_options(self):
        """Test Output-Optionen."""
        parser = cli.create_parser()

        args = parser.parse_args(
            [
                "colloquium",
                "test.pdf",
                "--date",
                "20.01.2026",
                "--time",
                "14:00",
                "--out",
                "/tmp/output",
                "--no-compile",
            ]
        )

        assert args.out == "/tmp/output"
        assert args.no_compile is True


class TestMain:
    """Tests für main Funktion."""

    @patch("academic_doc_generator.cli.run_from_config")
    def test_main_with_config(self, mock_run_config):
        """Test main mit Config-Argument."""
        test_args = ["academic-doc-generator", "--config", "config.json"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_config.assert_called_once_with("config.json")

    @patch("academic_doc_generator.cli.Path")
    def test_main_list_templates_found(self, mock_path_class):
        """Test --list-templates mit vorhandenen Templates."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.glob.return_value = [
            Path("config_templates/config_colloquium_campus.json"),
            Path("config_templates/config_project_template.json"),
        ]
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                cli.main()
                output = fake_out.getvalue()

                assert "config_colloquium_campus.json" in output
                assert "config_project_template.json" in output

    @patch("academic_doc_generator.cli.Path")
    def test_main_list_templates_not_found(self, mock_path_class):
        """Test --list-templates wenn Ordner nicht existiert."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()

            assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.Path")
    def test_main_list_templates_no_files(self, mock_path_class):
        """Test --list-templates wenn keine Templates vorhanden."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.glob.return_value = []
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()

            assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.run_colloquium_direct")
    def test_main_colloquium_subcommand(self, mock_run_colloquium):
        """Test main mit Colloquium Subcommand."""
        test_args = [
            "academic-doc-generator",
            "colloquium",
            "test.pdf",
            "--date",
            "20.01.2026",
            "--time",
            "14:00",
            "--room",
            "3.217",
        ]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_colloquium.assert_called_once()

    @patch("academic_doc_generator.cli.run_project_direct")
    def test_main_project_subcommand(self, mock_run_project):
        """Test main mit Project Subcommand."""
        test_args = ["academic-doc-generator", "project", "project.pdf"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_project.assert_called_once()

    @patch("academic_doc_generator.cli.run_review_direct")
    def test_main_review_subcommand(self, mock_run_review):
        """Test main mit Review Subcommand."""
        test_args = ["academic-doc-generator", "review", "paper.pdf"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_review.assert_called_once()

    def test_main_no_subcommand(self):
        """Test main ohne Subcommand zeigt Hilfe."""
        test_args = ["academic-doc-generator"]

        with patch.object(sys, "argv", test_args):
            with patch("sys.stdout", new=StringIO()) as fake_out:
                cli.main()
                output = fake_out.getvalue()

                # Sollte Hilfe-Text enthalten
                assert "Tipp" in output or "usage" in output.lower()


class TestEntryPoints:
    """Tests für Entry-Point-Funktionen."""

    @patch("academic_doc_generator.cli.main")
    def test_colloquium_main_entry_point(self, mock_main):
        """Test colloquium_main Entry Point."""
        original_argv = sys.argv.copy()
        sys.argv = [
            "colloquium-protocol-creator",
            "test.pdf",
            "--date",
            "20.01.2026",
            "--time",
            "14:00",
        ]

        try:
            cli.colloquium_main()

            # Verify argv was modified correctly
            assert sys.argv[0] == "academic-doc-generator"
            assert sys.argv[1] == "colloquium"
            assert "test.pdf" in sys.argv

            mock_main.assert_called_once()
        finally:
            sys.argv = original_argv

    @patch("academic_doc_generator.cli.main")
    def test_project_main_entry_point(self, mock_main):
        """Test project_main Entry Point."""
        original_argv = sys.argv.copy()
        sys.argv = ["project-grading-letter", "project.pdf"]

        try:
            cli.project_main()

            assert sys.argv[0] == "academic-doc-generator"
            assert sys.argv[1] == "project"
            assert "project.pdf" in sys.argv

            mock_main.assert_called_once()
        finally:
            sys.argv = original_argv


class TestIntegration:
    """Integrationstests für CLI."""

    @patch("academic_doc_generator.cli.run_pipeline")
    @patch("academic_doc_generator.cli.LLMClient")
    def test_full_colloquium_flow(self, mock_llm_class, mock_pipeline):
        """Test kompletter Colloquium-Workflow."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_llm_class.return_value = mock_client

        mock_pipeline.return_value = (
            "/tmp/bewertung_brief_12345.tex",
            "/tmp/bewertung_brief_12345.pdf",
            "/tmp/email.md",
        )

        test_args = [
            "academic-doc-generator",
            "colloquium",
            "thesis.pdf",
            "--date",
            "20.01.2026",
            "--time",
            "14:00",
            "--location-type",
            "campus",
            "--room",
            "3.217",
            "--api",
            "openai",
            "--model",
            "gpt-4o",
        ]

        with patch.object(sys, "argv", test_args):
            cli.main()

        # Verify complete workflow
        mock_llm_class.assert_called_once()
        mock_pipeline.assert_called_once()

        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["pdf_path"] == "thesis.pdf"
        assert call_kwargs["date_colloquium"] == "20.01.2026"
        assert call_kwargs["uhrzeit_colloquium"] == "14:00"
        assert call_kwargs["location_type"] == "campus"
        assert call_kwargs["room"] == "3.217"

    @patch("academic_doc_generator.cli.load_config")
    @patch("academic_doc_generator.cli.LLMClient")
    @patch("academic_doc_generator.cli.run_pipeline")
    def test_config_based_workflow(
        self, mock_pipeline, mock_llm_class, mock_load_config
    ):
        """Test Config-basierter Workflow."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get_task.return_value = "colloquium"
        mock_config.get_llm_config.return_value = {
            "api_choice": None,
            "model": None,
            "groq_free": False,
        }
        mock_config.get_output_config.return_value = {
            "folder": None,
            "compile_pdf": True,
            "fill_form_only": False,
        }
        mock_config.get_pdf_path.return_value = "test.pdf"
        mock_config.get_colloquium_config.return_value = {
            "date": "20.01.2026",
            "time": "14:00",
            "location_type": "campus",
            "room": "3.217",
        }
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_llm_class.return_value = mock_client

        mock_pipeline.return_value = ("/tmp/test.tex", "/tmp/test.pdf", "/tmp/email.md")

        # Run with config
        test_args = ["academic-doc-generator", "--config", "config.json"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        # Verify workflow
        mock_load_config.assert_called_once_with("config.json")
        mock_llm_class.assert_called_once()
        mock_pipeline.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
