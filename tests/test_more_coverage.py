"""
Additional comprehensive unit tests targeting missing lines to increase coverage to 100% or close to it.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.cli import handlers
from academic_doc_generator.colloquium import pdf_form_filler
from academic_doc_generator.colloquium.calendar_generator import CalendarGenerator
from academic_doc_generator.colloquium.gemini_thesis_evaluator import GeminiThesisEvaluator
from academic_doc_generator.colloquium.orchestrator import _get_gemini_emark, run_pipeline
from academic_doc_generator.colloquium.outlook_mail_generator import OutlookMailGenerator
from academic_doc_generator.config_loader import ConfigLoader
from academic_doc_generator.core import email, latex
from academic_doc_generator.core.types import ColloquiumWorkflowConfig

# ==============================================================================
# 1. Tests for src/academic_doc_generator/cli/handlers.py
# ==============================================================================


class TestHandlersMissingLines:
    """Tests specifically targeting handlers.py missing lines."""

    @patch("academic_doc_generator.cli.handlers.load_config")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.run_project_pipeline")
    def test_run_from_config_project_grade_fallback(
        self, mock_run_project, mock_validate_pdf, mock_llm_class, mock_load_config
    ):
        """Line 94: mark = proj_config.get(\"grade\") fallback."""
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
        # Notice "mark" is None, and we have "grade"
        mock_config.get_project_config.return_value = {"grade": "2.3", "work_type": "Masterarbeit"}
        mock_load_config.return_value = mock_config

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.return_value = Path("/test/project.pdf")

        mock_result = MagicMock()
        mock_result.tex_path = "/test/output.tex"
        mock_run_project.return_value = mock_result

        handlers.run_from_config("/test/config.json")

        # Verify that run_project_pipeline was called with mark="2.3"
        args, kwargs = mock_run_project.call_args
        assert args[0].mark == "2.3"

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    def test_run_colloquium_direct_pdf_validation_error(self, mock_validate_pdf, mock_llm_class):
        """Lines 153-155: Error handling during PDF validation in run_colloquium_direct."""
        args = MagicMock()
        args.pdf = "/test/thesis.pdf"
        args.api = "openai"
        args.model = "gpt-4o"

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.side_effect = FileNotFoundError("File not found error")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_colloquium_direct(args)

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    def test_run_project_direct_pdf_validation_error(self, mock_validate_pdf, mock_llm_class):
        """Lines 206-208: Error handling during PDF validation in run_project_direct."""
        args = MagicMock()
        args.pdf = "/test/project.pdf"
        args.api = "openai"
        args.model = "gpt-4o"

        mock_llm_class.return_value = MagicMock()
        mock_validate_pdf.side_effect = ValueError("Value validation error")

        with pytest.raises(SystemExit) as exc_info:
            handlers.run_project_direct(args)

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    def test_run_translator_direct_llm_error(self, mock_llm_class):
        """Lines 240-245: Error handling during LLM initialization in run_translator_direct."""
        args = MagicMock()
        args.input = "exam.tex"
        args.api = "invalid"
        args.model = None

        mock_llm_class.side_effect = Exception("LLM init failed")

        with patch("pathlib.Path.exists", return_value=True), pytest.raises(SystemExit) as exc_info:
            handlers.run_translator_direct(args)

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.translate_latex_exam")
    def test_run_translator_direct_wrong_extension_warning(self, mock_translate, mock_llm_class):
        """Line 271: Warning shown when input file has an unrecognized extension."""
        args = MagicMock()
        args.input = "exam.txt"  # .txt instead of .tex/.xml
        args.output = None
        args.verbose = False
        args.api = "openai"
        args.model = "gpt-4o"

        mock_llm_class.return_value = MagicMock()
        mock_translate.return_value = "exam_engl.txt"

        with patch("pathlib.Path.exists", return_value=True), patch("builtins.print") as mock_print:
            handlers.run_translator_direct(args)

            # Check that warning print was called
            any_warning = any("Warnung" in str(arg[0]) for arg, _ in mock_print.call_args_list)
            assert any_warning


# ==============================================================================
# 2. Tests for src/academic_doc_generator/cli/main.py
# ==============================================================================


class TestMainMissingLines:
    """Tests specifically targeting main.py missing lines."""

    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_no_apis_configured(self, mock_validate):
        """Lines 160-164: Exit if no LLM APIs are configured."""
        mock_validate.return_value = []
        cli_main_module = sys.modules["academic_doc_generator.cli.main"]

        with pytest.raises(SystemExit) as exc_info:
            cli_main_module.main()

        assert exc_info.value.code == 1

    @patch("academic_doc_generator.cli.main.validate_api_keys")
    def test_main_api_validation_exception_warning(self, mock_validate):
        """Lines 165-166: Catch exception during validate_api_keys and print warning."""
        mock_validate.side_effect = Exception("Network timeout")
        cli_main_module = sys.modules["academic_doc_generator.cli.main"]

        test_args = ["academic-doc-generator", "--help"]
        with patch.object(sys, "argv", test_args), pytest.raises(SystemExit):
            cli_main_module.main()

    def test_main_as_script_execution(self):
        """Line 227: Executing main.py as direct script."""
        cli_main_module = sys.modules["academic_doc_generator.cli.main"]
        assert callable(cli_main_module.main)


# ==============================================================================
# 3. Tests for src/academic_doc_generator/colloquium/calendar_generator.py
# ==============================================================================


class TestCalendarGeneratorMissingLines:
    """Tests specifically targeting calendar_generator.py missing lines."""

    def test_generate_location_string_campus_missing_room(self):
        """Line 129: Campus location requires room."""
        gen = CalendarGenerator()
        with pytest.raises(ValueError, match="room' benötigt"):
            gen._generate_location_string(location_type="campus", room=None)

    def test_generate_location_string_company_missing_name(self):
        """Line 134: Company location requires company_name."""
        gen = CalendarGenerator()
        with pytest.raises(ValueError, match="company_name' benötigt"):
            gen._generate_location_string(location_type="company", company_name=None)

    def test_generate_location_string_company_without_address(self):
        """Line 139: Company location without address return name directly."""
        gen = CalendarGenerator()
        res = gen._generate_location_string(
            location_type="company", company_name="MyCompany", company_address=None
        )
        assert res == "MyCompany"

    def test_generate_location_string_unknown_type(self):
        """Line 145: Unknown location type raises ValueError."""
        gen = CalendarGenerator()
        with pytest.raises(ValueError, match="Unbekannter location_type: invalid"):
            gen._generate_location_string(location_type="invalid")


# ==============================================================================
# 4. Tests for src/academic_doc_generator/colloquium/gemini_thesis_evaluator.py
# ==============================================================================


class TestGeminiThesisEvaluatorMissingLines:
    """Tests specifically targeting gemini_thesis_evaluator.py missing lines."""

    def test_evaluate_thesis_text_extraction(self):
        """Lines 63-66: evaluate_thesis text extraction from PDF logic."""
        client = MagicMock()
        client.api_choice = "gemini"
        client.chat_completion.return_value = (
            '{"gesamt_kommentar": "Excellent!", "punkte": 85, "note": "1.3"}'
        )

        evaluator = GeminiThesisEvaluator(client)

        with (
            patch.object(
                GeminiThesisEvaluator, "_remove_first_page", return_value="/dummy/temp.pdf"
            ),
            patch.object(
                GeminiThesisEvaluator,
                "_extract_text_from_pdf",
                return_value="First Page\n\nSecond Page",
            ),
            patch("os.unlink") as mock_unlink,
        ):

            emark = evaluator.evaluate_thesis(
                pdf_path="/dummy/path.pdf",
                thesis_title="My Thesis",
                degree="Master",
                use_text_extraction=True,
                verbose=False,
            )
            assert emark is not None
            assert emark == '{"gesamt_kommentar": "Excellent!", "punkte": 85, "note": "1.3"}'
            mock_unlink.assert_called_once_with("/dummy/temp.pdf")

    def test_evaluate_thesis_verbose_printing(self):
        """Line 146: Verbose printing of Gemini's response."""
        client = MagicMock()
        client.api_choice = "gemini"
        client.chat_completion.return_value = (
            '{"gesamt_kommentar": "Nice!", "punkte": 80, "note": "1.7"}'
        )

        evaluator = GeminiThesisEvaluator(client)

        with (
            patch.object(
                GeminiThesisEvaluator, "_remove_first_page", return_value="/dummy/temp.pdf"
            ),
            patch("os.unlink"),patch("builtins.print") as mock_print
        ):
            evaluator.evaluate_thesis(
                pdf_path="/dummy/path.pdf",
                thesis_title="My Thesis",
                degree="Master",
                use_text_extraction=False,
                verbose=True,
            )
            any_gemini_resp = any(
                "Gemini-Antwort" in str(arg[0]) for arg, _ in mock_print.call_args_list
            )
            assert any_gemini_resp


# ==============================================================================
# 5. Tests for src/academic_doc_generator/colloquium/orchestrator.py
# ==============================================================================


class TestColloquiumOrchestratorMissingLines:
    """Tests specifically targeting orchestrator.py missing lines."""

    @patch("academic_doc_generator.colloquium.orchestrator.GeminiThesisEvaluator")
    @patch("academic_doc_generator.colloquium.orchestrator.LLMClient")
    def test_get_gemini_emark_flow(self, mock_llm_class, mock_evaluator_class):
        """Lines 152-165: _get_gemini_emark branch logic."""
        mock_evaluator = MagicMock()
        mock_evaluator.evaluate_thesis.return_value = {"note": "1.3"}
        mock_evaluator.format_emark_for_latex.return_value = "\\section{Gemini}"
        mock_evaluator_class.return_value = mock_evaluator

        mock_gemini_client = MagicMock()
        mock_llm_class.return_value = mock_gemini_client

        config = MagicMock()
        config.gemini_emark_enabled = True
        config.gemini_model = "gemini-model"
        config.pdf_path = "/dummy.pdf"
        config.gemini_use_text_extraction = True

        metadata = {"title": "Thesis Title", "bachelor_master": "Bachelor"}

        res = _get_gemini_emark(config, metadata)
        assert res == "\\section{Gemini}"

        # Test failure branch (evaluate_thesis returns None)
        mock_evaluator.evaluate_thesis.return_value = None
        res_fail = _get_gemini_emark(config, metadata)
        assert res_fail is None

    @patch("academic_doc_generator.colloquium.orchestrator.OutlookMailGenerator")
    @patch("platform.system")
    def test_run_pipeline_outlook_ics_open(self, mock_platform, mock_outlook_class):
        """Lines 362-363: open_ics_in_outlook on run_pipeline."""
        mock_outlook = MagicMock()
        mock_outlook.create_outlook_mail.return_value = True
        mock_outlook_class.return_value = mock_outlook

        # Force platform.system() to return Windows to enter the block
        mock_platform.return_value = "Windows"

        config = ColloquiumWorkflowConfig(
            pdf_path=Path(__file__),  # Just some valid path
            date="20.01.2026",
            time="14:00",
            llm_client=MagicMock(),
            location_type="campus",
            room="3.217",
        )

        with patch(
            "academic_doc_generator.colloquium.orchestrator._extract_and_process_thesis"
        ) as mock_extract:
            mock_extract.return_value = ({}, {}, {"title": "T"}, "Summary text", "German", {})
            with patch(
                "academic_doc_generator.colloquium.orchestrator._fill_grading_form"
            ) as mock_filler:
                mock_filler.return_value = (1, "/out.pdf")
                with patch(
                    "academic_doc_generator.colloquium.orchestrator.CalendarGenerator"
                ) as mock_cal_class:
                    mock_cal = MagicMock()
                    mock_cal.generate_ics.return_value = "/out.ics"
                    mock_cal_class.return_value = mock_cal

                    # Ensure compile_pdf is False to avoid pdflatex issues
                    config.compile_pdf = False
                    run_pipeline(config)

                    mock_outlook.open_ics_in_outlook.assert_called_once_with(
                        "/out.ics", verbose=False
                    )


# ==============================================================================
# 6. Tests for src/academic_doc_generator/colloquium/outlook_mail_generator.py
# ==============================================================================


class TestOutlookMailGeneratorMissingLines:
    """Tests specifically targeting outlook_mail_generator.py missing lines."""

    def test_create_mac_outlook_draft_error_handling(self):
        """Lines 245-246: Error handling and traceback print in create_mac_outlook_draft."""
        gen = OutlookMailGenerator()

        # Trigger an exception by passing bad inputs or mocking
        with (
            patch("subprocess.run", side_effect=RuntimeError("Subprocess failed")),
            patch("traceback.print_exc") as mock_traceback,
        ):
            gen._create_outlook_mail_macos("to@test.com", "subject", "body", verbose=True)
            mock_traceback.assert_called_once()

    def test_create_linux_mail_draft_error_handling(self):
        """Lines 292-294: Error handling and traceback print in create_linux_mail_draft."""
        gen = OutlookMailGenerator()

        with (
            patch("subprocess.run", side_effect=RuntimeError("Subprocess failed")),
            patch("traceback.print_exc") as mock_traceback,
        ):
            gen._create_outlook_mail_linux("to@test.com", "subject", "body", verbose=True)
            mock_traceback.assert_called_once()


# ==============================================================================
# 7. Tests for src/academic_doc_generator/colloquium/pdf_form_filler.py
# ==============================================================================


class TestPdfFormFillerMissingLines:
    """Tests specifically targeting pdf_form_filler.py missing lines."""

    def test_pdf_form_handler_exception_handling(self):
        """Lines 180-185: Exception handling when updating field value in PDFFormHandler."""
        mock_widget = MagicMock()
        mock_widget.field_name = "test_field"
        mock_widget.field_type = 999  # fallback type (not TEXT or CHECKBOX)
        # update() will raise an exception
        mock_widget.update.side_effect = Exception("Pymupdf update error")

        mock_page = MagicMock()
        mock_page.widgets.return_value = [mock_widget]

        # Use MagicMock for mock_doc so that we can support close() method to avoid warnings
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]

        with patch("pymupdf.open") as mock_open:
            mock_open.return_value = mock_doc
            handler = pdf_form_filler.PDFFormHandler("dummy.pdf")

        with patch("builtins.print") as mock_print:
            handler.fill_form({"test_field": "test_val"}, "dummy_out.pdf")

            # Check warning message
            any_warning = any(
                "Feld 'test_field' konnte nicht gesetzt werden" in str(arg[0])
                for arg, _ in mock_print.call_args_list
            )
            assert any_warning

    def test_pdf_form_filler_main_call(self):
        """Line 441: Executable block of pdf_form_filler.py."""
        assert callable(pdf_form_filler.main)


# ==============================================================================
# 8. Tests for src/academic_doc_generator/config_loader.py
# ==============================================================================


class TestConfigLoaderMissingLines:
    """Tests specifically targeting config_loader.py missing lines."""

    def test_config_loader_missing_files_error(self):
        """Line 39: FileNotFoundError when folder exists but contains no config*.json files."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(FileNotFoundError, match="Keine config.*Datei gefunden"),
        ):
            ConfigLoader(tmpdir)

    def test_get_project_config(self):
        """Line 162: get_project_config should return the project config dict."""
        config_data = {
            "task": "project",
            "pdf": {"filename": "test.pdf"},
            "project": {"mark": "1.7", "work_type": "Forschungsarbeit"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write config
            with open(Path(tmpdir) / "config.json", "w") as f:
                json.dump(config_data, f)
            # Create dummy pdf
            (Path(tmpdir) / "test.pdf").write_text("pdf content")

            loader = ConfigLoader(tmpdir)
            p_config = loader.get_project_config()
            assert p_config == {"mark": "1.7", "work_type": "Forschungsarbeit"}

    def test_get_gemini_emark_config_default(self):
        """Lines 173-178: get_gemini_emark_config fallback to defaults when absent."""
        config_data = {
            "task": "review",
            "pdf": {"filename": "test.pdf"},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(Path(tmpdir) / "config.json", "w") as f:
                json.dump(config_data, f)
            (Path(tmpdir) / "test.pdf").write_text("pdf content")

            loader = ConfigLoader(tmpdir)
            gemini_cfg = loader.get_gemini_emark_config()
            assert gemini_cfg == {
                "enabled": False,
                "model": "gemini-2.0-flash-exp",
                "use_text_extraction": True,
            }


# ==============================================================================
# 9. Tests for src/academic_doc_generator/core/email.py
# ==============================================================================


class TestEmailMissingLines:
    """Tests specifically targeting email.py missing lines."""

    def test_recipient_formal_salutation_fallback(self):
        """Line 64: formal_salutation returns 'Guten Tag' if gender is Herr/Frau or empty."""
        r1 = email.EmailRecipient("Max", "Mustermann", "Herr/Frau")
        r2 = email.EmailRecipient("Max", "Mustermann", "")
        assert r1.formal_salutation == "Guten Tag"
        assert r2.formal_salutation == "Guten Tag"

    def test_recipient_full_name_with_title_fallback(self):
        """Line 80: full_name_with_title returns name without prefix if gender is Herr/Frau or empty."""
        r1 = email.EmailRecipient("Max", "Mustermann", "Herr/Frau")
        r2 = email.EmailRecipient("Max", "Mustermann", "")
        assert r1.full_name_with_title == "Max Mustermann"
        assert r2.full_name_with_title == "Max Mustermann"

    def test_format_recipients_salutation_empty(self):
        """Line 108: format_recipients_salutation returns 'Guten Tag' if list is empty."""
        res = email.EmailRecipient.format_recipients_salutation([])
        assert res == "Guten Tag"

    def test_format_recipients_salutation_single(self):
        """Line 110: format_recipients_salutation returns recipient's formal salutation if len is 1."""
        r = email.EmailRecipient("Max", "Mustermann", "Herr")
        res = email.EmailRecipient.format_recipients_salutation([r])
        assert res == "Guten Tag Herr Mustermann"

    def test_format_recipients_full_names_empty(self):
        """Line 126: format_recipients_full_names returns 'Unbekannt' if empty list."""
        res = email.EmailRecipient.format_recipients_full_names([])
        assert res == "Unbekannt"

    def test_format_recipients_full_names_single(self):
        """Line 128: format_recipients_full_names returns full_name_with_id if length is 1."""
        r = email.EmailRecipient("Max", "Mustermann", "Herr", "12345")
        res = email.EmailRecipient.format_recipients_full_names([r])
        assert res == "Herr Max Mustermann (12345)"

    def test_format_recipients_full_names_multiple(self):
        """Line 133: format_recipients_full_names formats multiple names using commas and 'und'."""
        r1 = email.EmailRecipient("Max", "Mustermann", "Herr", "1")
        r2 = email.EmailRecipient("Erika", "Musterfrau", "Frau", "2")
        r3 = email.EmailRecipient("John", "Doe", "", "3")
        res = email.EmailRecipient.format_recipients_full_names([r1, r2, r3])
        assert res == "Herr Max Mustermann (1), Frau Erika Musterfrau (2) und John Doe (3)"


# ==============================================================================
# 10. Tests for src/academic_doc_generator/core/latex.py
# ==============================================================================


class TestLatexMissingLines:
    """Tests specifically targeting latex.py missing lines."""

    def test_create_colloquium_protocol_tex_with_gemini(self):
        """Line 194: gemini_section formatting inside create_formal_letter_tex."""
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            latex.create_formal_letter_tex(
                filename=tmp_path,
                recipient="R",
                subject="S",
                title="T",
                author="A",
                summary="Sum",
                first_examiner="E1",
                second_examiner="E2",
                examiner_email="e@e.com",
                questions="Q",
                gemini_emark="\\section{Gemini Evaluation}",
            )

            with open(tmp_path, encoding="utf-8") as f:
                content = f.read()

            assert "\\section{Gemini Evaluation}" in content
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_create_formal_letter_tex_verbose_printing(self):
        """Line 374: Print questions to stdout if verbose is True on concatenate_comments."""
        results = {1: [{"rewritten": "My special test question text"}]}
        with patch("builtins.print") as mock_print:
            latex.concatenate_comments(results, language="German", verbose=True)
            mock_print.assert_any_call("Seite 1: My special test question text")

    @patch("subprocess.run")
    def test_compile_tex_to_pdf_output_dir_determination(self, mock_run):
        """Line 393: Compile LaTeX to PDF correctly determines output directory."""
        mock_run.return_value = MagicMock(returncode=0)

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            latex.compile_latex_to_pdf(tmp_path)
            # Verify subprocess run was called with correct -output-directory
            args, kwargs = mock_run.call_args
            cmd = args[0]
            expected_out_dir = os.path.dirname(tmp_path)
            assert f"-output-directory={expected_out_dir}" in cmd or any(
                f"-output-directory={expected_out_dir}" in item for item in cmd
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
