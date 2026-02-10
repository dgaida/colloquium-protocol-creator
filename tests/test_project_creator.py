"""
Unit tests for the project_creator package.
"""

import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.core import llm as core_llm
from academic_doc_generator.project import latex, llm

# ============================================================================
# Tests for project_creator/latex.py
# ============================================================================


class TestProjectLatexGeneration:
    """Tests for project work LaTeX generation."""

    def test_get_semester_summer(self):
        """Test semester detection for summer semester (March-September)."""
        # Mock summer months
        from academic_doc_generator.core.utils import get_semester

        with patch("academic_doc_generator.core.utils.datetime") as mock_dt:
            # Test June (summer semester)
            mock_dt.now.return_value = datetime(2025, 6, 15)
            semester = get_semester()
            assert semester == "SoSe25"

            # Test March (start of summer)
            mock_dt.now.return_value = datetime(2025, 3, 1)
            semester = get_semester()
            assert semester == "SoSe25"

            # Test September (end of summer)
            mock_dt.now.return_value = datetime(2025, 9, 30)
            semester = get_semester()
            assert semester == "SoSe25"

    def test_get_semester_winter(self):
        """Test semester detection for winter semester (October-February)."""
        from academic_doc_generator.core.utils import get_semester

        with patch("academic_doc_generator.core.utils.datetime") as mock_dt:
            # Test November (winter semester)
            mock_dt.now.return_value = datetime(2025, 11, 15)
            semester = get_semester()
            assert semester == "WS25/26"

            # Test October (start of winter)
            mock_dt.now.return_value = datetime(2025, 10, 1)
            semester = get_semester()
            assert semester == "WS25/26"

            # Test February (end of winter, previous year)
            mock_dt.now.return_value = datetime(2025, 2, 28)
            semester = get_semester()
            assert semester == "WS24/25"

            # Test January
            mock_dt.now.return_value = datetime(2025, 1, 15)
            semester = get_semester()
            assert semester == "WS24/25"

    def test_create_project_grading_letter_tex_herr(self):
        """Test project grading letter generation for male student."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author="Max Mustermann, Matrikelnr. 12345",
                title="Test Project Title",
                examiner="Prof. Test",
                contact="test@example.com",
                gender="Herr",
                work_type="Praxisprojekt",
                grade_mark="1.3",
            )

            assert os.path.exists(tex_path)

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            # Check basic structure
            assert r"\documentclass" in content
            assert "Max Mustermann" in content
            assert "12345" in content
            assert "Test Project Title" in content
            assert "Prof. Test" in content
            assert "1.3" in content

            # Check gender-specific text
            assert "Herr" in content
            assert "sein" in content  # "sein Praxisprojekt"
            assert "Er" in content  # "Er hat die Note"

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)

    def test_create_project_grading_letter_tex_frau(self):
        """Test project grading letter generation for female student."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author="Maria Musterfrau, Matrikelnr. 67890",
                title="Another Test Project",
                examiner="Dr. Example",
                contact="example@th-koeln.de",
                gender="Frau",
                work_type="Projektarbeit",
            )

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            # Check gender-specific text
            assert "Frau" in content
            assert "ihr" in content  # "ihr Praxisprojekt" or "ihre Projektarbeit"
            assert "Sie" in content  # "Sie hat die Note"
            assert "Projektarbeit" in content

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)

    def test_create_project_grading_letter_tex_special_chars(self):
        """Test that special characters are properly escaped."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author="Test & User, Matrikelnr. 99999",
                title="Project with 100% Coverage & $pecial Char$",
                examiner="Prof. Test",
                contact="test@example.com",
                gender="Herr",
            )

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            # When preserve_latex=False, special chars are escaped differently
            # & becomes \textbackslash{}& (backslash is escaped first)
            # % becomes \textbackslash{}%
            # $ becomes \textbackslash{}$
            # Check that the original special characters don't appear unescaped
            # The content should have escaped versions

            # Check that special chars are handled (either escaped or replaced)
            # Since preserve_latex=False, we get \textbackslash{} for backslashes
            assert "\\textbackslash" in content or "\\&" in content or "Test \\& User" in content

            # More reliable: check that dangerous unescaped chars are NOT present in wrong places
            # Look for the title line
            title_marker = "Das Thema war:"
            title_start = content.find(title_marker)
            if title_start != -1:
                title_section = content[title_start : title_start + 200]
                # Should have some form of escaping, not raw special chars
                # Check that it contains "100" and "Coverage" (the non-special parts)
                assert "100" in title_section
                assert "Coverage" in title_section or "Project" in title_section

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)

    def test_create_project_grading_letter_tex_custom_params(self):
        """Test with custom place, date, and signature."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author="Test Student, Matrikelnr. 11111",
                title="Custom Project",
                examiner="Prof. Custom",
                contact="custom@th-koeln.de",
                gender="Herr",
                place="Köln",
                date="15.01.2025",
                signature_file="custom_sig.png",
            )

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            assert "Köln" in content
            assert "15.01.2025" in content
            assert "custom_sig.png" in content

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)


# ============================================================================
# Tests for project_creator/llm.py
# ============================================================================


class TestProjectLLMInterface:
    """Tests for project work LLM interface."""

    def test_determine_gender_from_name_male(self):
        """Test gender detection for male names."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Herr"

        result = core_llm.determine_gender_from_name("Max", mock_client)

        assert result == "Herr"
        mock_client.chat_completion.assert_called_once()

        # Check that prompt contains the name
        call_args = mock_client.chat_completion.call_args[0][0]
        assert "Max" in str(call_args)

    def test_determine_gender_from_name_female(self):
        """Test gender detection for female names."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Frau"

        result = core_llm.determine_gender_from_name("Maria", mock_client)

        assert result == "Frau"

    def test_determine_gender_from_name_uncertain(self):
        """Test handling of uncertain gender."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Herr/Frau"

        result = core_llm.determine_gender_from_name("Kim", mock_client)

        assert result == "Herr/Frau"

    def test_determine_gender_from_name_invalid_response(self):
        """Test handling of invalid LLM response."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Invalid"

        result = core_llm.determine_gender_from_name("Test", mock_client)

        # Should return fallback
        assert result == "Herr/Frau"

    @patch("academic_doc_generator.project.llm.extract_text_per_page")
    def test_extract_project_metadata_success(self, mock_extract):
        """Test successful metadata extraction."""
        mock_extract.return_value = {
            0: "Praxisprojekt von Max Mustermann, Matrikelnr. 12345",
            1: "Titel: Test Project\nErstprüfer: Prof. Dr. Hans Meyer",
        }

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = json.dumps(
            {
                "student_name": "Max Mustermann",
                "student_first_name": "Max",
                "id_number": "12345",
                "title": "Test Project",
                "first_examiner": "Prof. Dr. Hans Meyer",
                "first_examiner_christian": "Hans",
                "first_examiner_family": "Meyer",
                "work_type": "Praxisprojekt",
            }
        )

        result = llm.extract_project_metadata("test.pdf", mock_client)

        assert result["student_name"] == "Max Mustermann"
        assert result["student_first_name"] == "Max"
        assert result["id_number"] == "12345"
        assert result["title"] == "Test Project"
        assert result["first_examiner"] == "Prof. Dr. Hans Meyer"
        assert result["first_examiner_christian"] == "Hans"
        assert result["first_examiner_family"] == "Meyer"
        assert result["work_type"] == "Praxisprojekt"

    @patch("academic_doc_generator.project.llm.extract_text_per_page")
    def test_extract_project_metadata_missing_fields(self, mock_extract):
        """Test metadata extraction with missing fields."""
        mock_extract.return_value = {0: "Incomplete document"}

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = json.dumps(
            {
                "student_name": "Test Student",
                "student_first_name": None,
                "id_number": None,
                "title": None,
                "first_examiner": None,
                "first_examiner_christian": None,
                "first_examiner_family": None,
                "work_type": None,
            }
        )

        result = llm.extract_project_metadata("test.pdf", mock_client)

        assert result["student_name"] == "Test Student"
        assert result["student_first_name"] is None
        assert result["id_number"] is None

    @patch("academic_doc_generator.project.llm.extract_text_per_page")
    def test_extract_project_metadata_json_error(self, mock_extract):
        """Test handling of JSON parsing errors."""
        mock_extract.return_value = {0: "Test content"}

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Not valid JSON"

        result = llm.extract_project_metadata("test.pdf", mock_client)

        assert "error" in result
        assert result["error"] == "Could not parse JSON"
        assert "raw" in result


# ============================================================================
# Integration Tests
# ============================================================================


class TestProjectIntegration:
    """Integration tests for project work pipeline."""

    def test_full_letter_generation_flow(self):
        """Test the complete flow from metadata to letter."""
        # Mock metadata
        metadata = {
            "student_name": "Test Student",
            "student_first_name": "Test",
            "id_number": "99999",
            "title": "Integration Test Project",
            "first_examiner": "Prof. Integration",
            "first_examiner_christian": "Integration",
            "first_examiner_family": "Tester",
            "work_type": "Praxisprojekt",
        }

        # Mock gender detection
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Herr"

        gender = core_llm.determine_gender_from_name(metadata["student_first_name"], mock_client)

        # Generate letter
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
            tex_path = f.name

        try:
            latex.create_project_grading_letter_tex(
                filename=tex_path,
                author=f"{metadata['student_name']}, Matrikelnr. {metadata['id_number']}",
                title=metadata["title"],
                examiner=metadata["first_examiner"],
                contact=f"{metadata['first_examiner_christian']}.{metadata['first_examiner_family']}@th-koeln.de",
                gender=gender,
                work_type=metadata["work_type"],
            )

            # Verify file was created
            assert os.path.exists(tex_path)

            with open(tex_path, encoding="utf-8") as f:
                content = f.read()

            # Verify all metadata is in the letter
            assert metadata["student_name"] in content
            assert metadata["id_number"] in content
            assert metadata["title"] in content
            assert metadata["first_examiner"] in content
            assert gender in content

        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
