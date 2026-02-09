"""
Comprehensive unit tests for src/academic_doc_generator/exam_translator/cli.py
Ziel: Coverage von 0% auf >90% erhöhen
"""

import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.exam_translator import cli


class TestExamTranslatorMain:
    """Tests für exam_translator_main Funktion."""

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_basic(self, mock_translate, mock_llm_class):
        """Test grundlegende Funktionalität."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_client.api_choice = "openai"
            mock_client.llm = "gpt-4o"
            mock_llm_class.return_value = mock_client

            mock_translate.return_value = tex_file.replace(".tex", "_engl.tex")

            test_args = ["exam-translator", tex_file]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            mock_llm_class.assert_called_once()
            mock_translate.assert_called_once()

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_with_output(self, mock_translate, mock_llm_class):
        """Test mit spezifiziertem Output-Pfad."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_llm_class.return_value = mock_client
            mock_translate.return_value = "/output/translated.tex"

            test_args = ["exam-translator", tex_file, "-o", "/output/translated.tex"]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            call_args = mock_translate.call_args
            assert call_args.kwargs["output_path"] == "/output/translated.tex"

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_with_api_choice(self, mock_translate, mock_llm_class):
        """Test mit API-Wahl."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_client.api_choice = "groq"
            mock_client.llm = "llama"
            mock_llm_class.return_value = mock_client

            mock_translate.return_value = tex_file.replace(".tex", "_engl.tex")

            test_args = ["exam-translator", tex_file, "--api", "groq"]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            mock_llm_class.assert_called_once_with(api_choice="groq", llm=None)

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_with_model(self, mock_translate, mock_llm_class):
        """Test mit spezifiziertem Modell."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_llm_class.return_value = mock_client
            mock_translate.return_value = tex_file.replace(".tex", "_engl.tex")

            test_args = ["exam-translator", tex_file, "--model", "gpt-4o-mini"]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            mock_llm_class.assert_called_once_with(api_choice=None, llm="gpt-4o-mini")

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_verbose(self, mock_translate, mock_llm_class):
        """Test mit verbose Flag."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_llm_class.return_value = mock_client
            mock_translate.return_value = tex_file.replace(".tex", "_engl.tex")

            test_args = ["exam-translator", tex_file, "-v"]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            call_args = mock_translate.call_args
            assert call_args.kwargs["verbose"] is True

        finally:
            Path(tex_file).unlink(missing_ok=True)

    def test_exam_translator_main_file_not_found(self):
        """Test mit nicht existierender Datei."""
        test_args = ["exam-translator", "/nonexistent/file.tex"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                cli.exam_translator_main()

            assert exc_info.value.code == 1

    def test_exam_translator_main_non_tex_file(self):
        """Test mit Nicht-.tex Datei (Warnung)."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", mode="w", delete=False) as f:
            f.write("dummy")
            pdf_file = f.name

        try:
            test_args = ["exam-translator", pdf_file]

            with patch.object(sys, "argv", test_args), patch(
                "academic_doc_generator.exam_translator.cli.LLMClient"
            ) as mock_llm, patch(
                "academic_doc_generator.exam_translator.cli.translate_latex_exam"
            ) as mock_translate:
                mock_llm.return_value = MagicMock()
                mock_translate.return_value = pdf_file.replace(
                    ".pdf", "_engl.pdf"
                )

                with patch("sys.stdout", new=StringIO()) as fake_out:
                    cli.exam_translator_main()
                    output = fake_out.getvalue()

                # Sollte Warnung ausgeben
                assert "Warnung" in output or "keine .tex Endung" in output

        finally:
            Path(pdf_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    def test_exam_translator_main_llm_init_error(self, mock_llm_class):
        """Test mit LLM-Initialisierungsfehler."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_llm_class.side_effect = Exception("API key missing")

            test_args = ["exam-translator", tex_file]

            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    cli.exam_translator_main()

                assert exc_info.value.code == 1

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_translation_value_error(
        self, mock_translate, mock_llm_class
    ):
        """Test mit ValueError während der Übersetzung."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_llm_class.return_value = mock_client
            mock_translate.side_effect = ValueError("Invalid LaTeX structure")

            test_args = ["exam-translator", tex_file]

            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    cli.exam_translator_main()

                assert exc_info.value.code == 1

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_unexpected_error(
        self, mock_translate, mock_llm_class
    ):
        """Test mit unerwartetem Fehler."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_llm_class.return_value = mock_client
            mock_translate.side_effect = RuntimeError("Unexpected error")

            test_args = ["exam-translator", tex_file]

            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    cli.exam_translator_main()

                assert exc_info.value.code == 1

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_success_output(self, mock_translate, mock_llm_class):
        """Test erfolgreiche Übersetzung mit Output-Überprüfung."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_client.api_choice = "openai"
            mock_client.llm = "gpt-4o"
            mock_llm_class.return_value = mock_client

            output_file = tex_file.replace(".tex", "_engl.tex")
            mock_translate.return_value = output_file

            test_args = ["exam-translator", tex_file]

            with patch.object(sys, "argv", test_args):
                with patch("sys.stdout", new=StringIO()) as fake_out:
                    cli.exam_translator_main()
                    output = fake_out.getvalue()

                # Überprüfe Success-Message
                assert "Übersetzung erfolgreich" in output
                assert tex_file in output
                assert output_file in output

        finally:
            Path(tex_file).unlink(missing_ok=True)

    @patch("academic_doc_generator.exam_translator.cli.LLMClient")
    @patch("academic_doc_generator.exam_translator.cli.translate_latex_exam")
    def test_exam_translator_main_all_options(self, mock_translate, mock_llm_class):
        """Test mit allen Optionen kombiniert."""
        with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False) as f:
            f.write("\\documentclass{exam}")
            tex_file = f.name

        try:
            mock_client = MagicMock()
            mock_client.api_choice = "groq"
            mock_client.llm = "llama3"
            mock_llm_class.return_value = mock_client

            mock_translate.return_value = "/output/result.tex"

            test_args = [
                "exam-translator",
                tex_file,
                "-o",
                "/output/result.tex",
                "--api",
                "groq",
                "--model",
                "llama3",
                "-v",
            ]

            with patch.object(sys, "argv", test_args):
                cli.exam_translator_main()

            # Verify LLM was created with correct params
            mock_llm_class.assert_called_once_with(api_choice="groq", llm="llama3")

            # Verify translate was called with correct params
            call_kwargs = mock_translate.call_args.kwargs
            assert call_kwargs["output_path"] == "/output/result.tex"
            assert call_kwargs["verbose"] is True

        finally:
            Path(tex_file).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
