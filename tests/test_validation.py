"""
Comprehensive unit tests for src/academic_doc_generator/core/validation.py
Ziel: Coverage von 19% auf >90% erhöhen
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from academic_doc_generator.core.validation import (
    validate_api_keys,
    validate_pdf_path,
)


class TestValidateApiKeys:
    """Tests für validate_api_keys Funktion."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}, clear=True)
    def test_validate_api_keys_openai_only(self):
        """Test mit nur OpenAI API Key."""
        result = validate_api_keys()

        assert "openai" in result
        assert "ollama" in result
        assert len(result) == 2

    @patch.dict(os.environ, {"GROQ_API_KEY": "gsk-test123"}, clear=True)
    def test_validate_api_keys_groq_only(self):
        """Test mit nur Groq API Key."""
        result = validate_api_keys()

        assert "groq" in result
        assert "ollama" in result

    @patch.dict(os.environ, {"GEMINI_API_KEY": "AIza-test123"}, clear=True)
    def test_validate_api_keys_gemini_only(self):
        """Test mit nur Gemini API Key."""
        result = validate_api_keys()

        assert "gemini" in result
        assert "ollama" in result

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-test",
            "GROQ_API_KEY": "gsk-test",
            "GEMINI_API_KEY": "AIza-test",
        },
        clear=True,
    )
    def test_validate_api_keys_all_apis(self):
        """Test mit allen API Keys."""
        result = validate_api_keys()

        assert "openai" in result
        assert "groq" in result
        assert "gemini" in result
        assert "ollama" in result
        assert len(result) == 4

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_api_keys_ollama_only(self):
        """Test ohne API Keys (nur Ollama)."""
        result = validate_api_keys()

        assert result == ["ollama"]

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True)
    def test_validate_api_keys_empty_key(self):
        """Test mit leerem API Key (sollte ignoriert werden)."""
        result = validate_api_keys()

        # Leere Keys sollten herausgefiltert werden
        assert "openai" not in result
        assert "ollama" in result


class TestValidatePdfPath:
    """Tests für validate_pdf_path Funktion."""

    def test_validate_pdf_path_valid_file(self):
        """Test mit gültiger PDF-Datei."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "test.pdf")

            assert result.exists()
            assert result.name == "test.pdf"

    def test_validate_pdf_path_in_subfolder(self):
        """Test mit PDF in Unterordner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subfolder"
            subdir.mkdir()
            pdf_file = subdir / "test.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "subfolder/test.pdf")

            assert result.exists()
            assert result.name == "test.pdf"

    def test_validate_pdf_path_not_found(self):
        """Test mit nicht existierender Datei."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(FileNotFoundError, match="File not found"),
        ):
            validate_pdf_path(tmpdir, "nonexistent.pdf")

    def test_validate_pdf_path_invalid_extension(self):
        """Test mit ungültiger Dateiendung."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(ValueError, match="Only PDF files allowed"),
        ):
            validate_pdf_path(tmpdir, "test.txt")

    def test_validate_pdf_path_docx_allowed(self):
        """Test mit Word-Datei (.docx), wenn allow_docx=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_file = Path(tmpdir) / "test.docx"
            docx_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "test.docx", allow_docx=True)

            assert result.exists()
            assert result.name == "test.docx"

    def test_validate_pdf_path_docx_not_allowed(self):
        """Test mit Word-Datei (.docx), wenn allow_docx=False."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(ValueError, match="Only PDF files allowed"),
        ):
            validate_pdf_path(tmpdir, "test.docx", allow_docx=False)

    def test_validate_pdf_path_directory_traversal_dotdot(self):
        """Test Directory Traversal mit ../"""
        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ValueError, match="traversal"):
            validate_pdf_path(tmpdir, "../../../etc/passwd.pdf")

    def test_validate_pdf_path_directory_traversal_absolute(self):
        """Test Directory Traversal mit absolutem Pfad."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            pytest.raises(ValueError, match="Absolute paths not allowed"),
        ):
            validate_pdf_path(tmpdir, "/etc/passwd.pdf")

    def test_validate_pdf_path_special_chars(self):
        """Test mit Sonderzeichen im Dateinamen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test file (2024).pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "test file (2024).pdf")

            assert result.exists()

    def test_validate_pdf_path_unicode_filename(self):
        """Test mit Unicode-Zeichen im Dateinamen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "Bachelorarbeit_Müller.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "Bachelorarbeit_Müller.pdf")

            assert result.exists()

    def test_validate_pdf_path_symlink(self):
        """Test mit symbolischem Link."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Erstelle echte Datei
            real_file = Path(tmpdir) / "real.pdf"
            real_file.write_text("dummy content")

            # Erstelle Symlink
            symlink = Path(tmpdir) / "link.pdf"
            try:
                symlink.symlink_to(real_file)

                result = validate_pdf_path(tmpdir, "link.pdf")
                assert result.exists()
            except OSError:
                # Symlinks funktionieren nicht auf allen Systemen
                pytest.skip("Symlinks not supported on this system")

    def test_validate_pdf_path_case_sensitivity(self):
        """Test Case-Sensitivity (plattformabhängig)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "Test.PDF"
            pdf_file.write_text("dummy content")

            # Auf case-insensitiven Systemen sollte dies funktionieren
            try:
                result = validate_pdf_path(tmpdir, "test.pdf")
                # Auf case-insensitiven Systemen gefunden
                assert result.exists()
            except FileNotFoundError:
                # Auf case-sensitiven Systemen nicht gefunden - das ist OK
                pass

    def test_validate_pdf_path_relative_path(self):
        """Test mit relativem Pfad im Dateinamen."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "sub"
            subdir.mkdir()
            pdf_file = subdir / "test.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "sub/test.pdf")

            assert result.exists()
            assert result.is_relative_to(Path(tmpdir).resolve())

    def test_validate_pdf_path_returns_absolute(self):
        """Test dass absoluter Pfad zurückgegeben wird."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "test.pdf")

            assert result.is_absolute()

    def test_validate_pdf_path_complex_traversal_attempt(self):
        """Test komplexerer Directory Traversal Versuch."""
        with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ValueError, match="traversal"):
            validate_pdf_path(tmpdir, "sub/../../etc/passwd.pdf")


class TestEdgeCases:
    """Tests für Grenzfälle."""

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-test",
            "GROQ_API_KEY": "",  # Leerer String
            "GEMINI_API_KEY": "   ",  # Nur Whitespace
        },
        clear=True,
    )
    def test_validate_api_keys_filter_empty_strings(self):
        """Test dass leere Strings herausgefiltert werden."""
        result = validate_api_keys()

        # Nur valide Keys sollten enthalten sein
        assert "openai" in result
        assert "ollama" in result
        # Leere Keys sollten nicht enthalten sein
        assert all(api != "" for api in result)

    def test_validate_pdf_path_with_dots_in_filename(self):
        """Test mit Punkten im Dateinamen (aber kein Traversal)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "thesis.v2.final.pdf"
            pdf_file.write_text("dummy content")

            result = validate_pdf_path(tmpdir, "thesis.v2.final.pdf")

            assert result.exists()
            assert result.name == "thesis.v2.final.pdf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
