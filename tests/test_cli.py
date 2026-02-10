"""
Unit tests for src/academic_doc_generator/cli.py
"""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator import cli


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
                "--zoom-code",
                "test123",
            ]
        )

        assert args.location_type == "online"
        assert args.zoom_link == "https://zoom.us/j/123"
        assert args.zcode == "test123"

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

        args = parser.parse_args(["project", "test.pdf", "--api", "openai", "--model", "gpt-4o"])

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

    @patch("academic_doc_generator.cli.main.run_from_config")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_with_config(self, mock_validate, mock_run_config):
        """Test main mit Config-Argument."""
        mock_validate.return_value = ["openai"]
        test_args = ["academic-doc-generator", "--config", "config.json"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_config.assert_called_once_with("config.json")

    @patch("academic_doc_generator.cli.main.Path")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_list_templates_found(self, mock_validate, mock_path_class):
        """Test --list-templates mit vorhandenen Templates."""
        mock_validate.return_value = ["openai"]
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.glob.return_value = [
            Path("config_templates/config_colloquium_campus.json"),
            Path("config_templates/config_project_template.json"),
        ]
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args), patch("sys.stdout", new=StringIO()) as fake_out:
            cli.main()
            output = fake_out.getvalue()

            assert "config_colloquium_campus.json" in output
            assert "config_project_template.json" in output

    @patch("academic_doc_generator.cli.main.Path")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_list_templates_not_found(self, mock_validate, mock_path_class):
        """Test --list-templates wenn Ordner nicht existiert."""
        mock_validate.return_value = ["openai"]
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()

            assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.main.Path")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_list_templates_no_files(self, mock_validate, mock_path_class):
        """Test --list-templates wenn keine Templates vorhanden."""
        mock_validate.return_value = ["openai"]
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        test_args = ["academic-doc-generator", "--list-templates"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()

            assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.run_colloquium_direct")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_colloquium_subcommand(self, mock_validate, mock_run_colloquium):
        """Test main mit Colloquium Subcommand."""
        mock_validate.return_value = ["openai"]
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

    @patch("academic_doc_generator.cli.handlers.run_project_direct")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_project_subcommand(self, mock_validate, mock_run_project):
        """Test main mit Project Subcommand."""
        mock_validate.return_value = ["openai"]
        test_args = ["academic-doc-generator", "project", "project.pdf"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_project.assert_called_once()

    @patch("academic_doc_generator.cli.handlers.run_review_direct")
    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_review_subcommand(self, mock_validate, mock_run_review):
        """Test main mit Review Subcommand."""
        mock_validate.return_value = ["openai"]
        test_args = ["academic-doc-generator", "review", "paper.pdf"]

        with patch.object(sys, "argv", test_args):
            cli.main()

        mock_run_review.assert_called_once()

    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_no_subcommand(self, mock_validate):
        """Test main ohne Subcommand zeigt Hilfe."""
        mock_validate.return_value = ["openai"]
        test_args = ["academic-doc-generator"]

        with patch.object(sys, "argv", test_args), patch("sys.stdout", new=StringIO()) as fake_out:
            cli.main()
            output = fake_out.getvalue()

            # Sollte Hilfe-Text enthalten
            assert "Tipp" in output or "usage" in output.lower()


class TestEntryPoints:
    """Tests für Entry-Point-Funktionen."""

    @patch("academic_doc_generator.cli.main.main")
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

    @patch("academic_doc_generator.cli.main.main")
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
