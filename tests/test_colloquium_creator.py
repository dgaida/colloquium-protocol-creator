"""
Unit tests for the colloquium-protocol-creator package.
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock
from colloquium_creator import pdf_processing, llm_interface, latex_generation, utils


# ============================================================================
# Tests for pdf_processing.py
# ============================================================================

class TestPdfProcessing:
    """Tests for PDF processing functions."""

    def test_is_quelle_comment_valid(self):
        """Test that valid 'Quelle' comments are detected."""
        assert pdf_processing.is_quelle_comment("Quelle")
        assert pdf_processing.is_quelle_comment("Quelle?")
        assert pdf_processing.is_quelle_comment("Quelle fehlt")
        assert pdf_processing.is_quelle_comment("quelle")
        assert pdf_processing.is_quelle_comment("  Quelle  ")
        assert pdf_processing.is_quelle_comment("source")
        assert pdf_processing.is_quelle_comment("Source?")
        assert pdf_processing.is_quelle_comment("source missing")

    def test_is_quelle_comment_invalid(self):
        """Test that invalid 'Quelle' comments are not detected."""
        # Too long
        assert not pdf_processing.is_quelle_comment("Quelle fehlt hier an dieser Stelle komplett")
        # Doesn't contain keyword
        assert not pdf_processing.is_quelle_comment("Why?")
        assert not pdf_processing.is_quelle_comment("Explain this")
        # Keyword not as whole word
        assert not pdf_processing.is_quelle_comment("Consequent")

    def test_is_quelle_comment_custom_length(self):
        """Test custom max_length parameter."""
        comment = "Quelle fehlt hier"  # 17 chars
        assert pdf_processing.is_quelle_comment(comment, max_length=20)
        assert not pdf_processing.is_quelle_comment(comment, max_length=15)

    def test_words_overlapping_rect(self):
        """Test word-rectangle overlap detection."""
        words = [
            {"text": "Hello", "bbox": (10, 10, 50, 20)},
            {"text": "World", "bbox": (60, 10, 100, 20)},
            {"text": "Far", "bbox": (200, 10, 250, 20)},
        ]
        
        # Rectangle overlapping first word
        rect = (5, 5, 55, 25)
        hits = pdf_processing.words_overlapping_rect(words, rect)
        assert len(hits) == 1
        assert hits[0]["text"] == "Hello"
        
        # Rectangle overlapping first two words
        rect = (5, 5, 105, 25)
        hits = pdf_processing.words_overlapping_rect(words, rect)
        assert len(hits) == 2
        assert hits[0]["text"] == "Hello"
        assert hits[1]["text"] == "World"
        
        # Rectangle not overlapping anything
        rect = (300, 300, 400, 400)
        hits = pdf_processing.words_overlapping_rect(words, rect)
        assert len(hits) == 0

    def test_rect_overlap(self):
        """Test bounding box overlap detection."""
        word_bbox = (10, 10, 50, 20)
        
        # Overlapping
        assert pdf_processing.rect_overlap(word_bbox, (5, 5, 55, 25))
        assert pdf_processing.rect_overlap(word_bbox, (40, 15, 60, 25))
        
        # Not overlapping
        assert not pdf_processing.rect_overlap(word_bbox, (60, 10, 100, 20))
        assert not pdf_processing.rect_overlap(word_bbox, (10, 30, 50, 40))

    def test_get_words_for_annotation_on_page(self):
        """Test finding words for annotation with page fallback."""
        pages_words = {
            0: [{"text": "Page0", "bbox": (10, 10, 50, 20)}],
            1: [{"text": "Page1", "bbox": (10, 10, 50, 20)}],
            2: [{"text": "Page2", "bbox": (10, 10, 50, 20)}],
        }
        
        rect = (5, 5, 55, 25)
        
        # Find on same page
        page_idx, words = pdf_processing.get_words_for_annotation_on_page(
            pages_words, 1, rect
        )
        assert page_idx == 1
        assert len(words) == 1
        assert words[0]["text"] == "Page1"
        
        # Test fallback to next page
        pages_words_mod = {
            0: [{"text": "Page0", "bbox": (100, 100, 150, 120)}],  # No overlap
            1: [{"text": "Page1", "bbox": (10, 10, 50, 20)}],
        }
        page_idx, words = pdf_processing.get_words_for_annotation_on_page(
            pages_words_mod, 0, rect
        )
        assert page_idx == 1
        assert words[0]["text"] == "Page1"


# ============================================================================
# Tests for llm_interface.py
# ============================================================================

class TestLLMInterface:
    """Tests for LLM interface functions."""

    def test_rewrite_comments_skips_ignored(self):
        """Test that ignored comments are not included in output."""
        context_dict = {
            1: [
                {"comment": "ab hier", "highlighted": "text", "paragraph": "para", "category": "ignore"},
                {"comment": "Why?", "highlighted": "text", "paragraph": "para", "category": "llm"},
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Rewritten question"

        result = llm_interface.rewrite_comments(context_dict, mock_client, groq_free=False)

        # Should only have one result (the "llm" category)
        assert 1 in result
        assert len(result[1]) == 1
        assert result[1][0]["category"] == "llm"

    def test_rewrite_comments_skips_quelle(self):
        """Test that 'Quelle' comments are kept but not rewritten."""
        context_dict = {
            1: [
                {"comment": "Quelle?", "highlighted": "text", "paragraph": "para", "category": "quelle"},
            ]
        }
        
        mock_client = MagicMock()

        result = llm_interface.rewrite_comments(context_dict, mock_client, groq_free=False)

        # Should be in output but not rewritten
        assert 1 in result
        assert len(result[1]) == 1
        assert result[1][0]["category"] == "quelle"
        assert result[1][0]["rewritten"] is None
        assert result[1][0]["original"] == "Quelle?"

        # Client should not have been called
        mock_client.assert_not_called()

    def test_rewrite_comments_skips_language(self):
        """Test that language comments are kept but not rewritten."""
        context_dict = {
            1: [
                {"comment": "Rechtschreibung", "highlighted": "text", "paragraph": "para", "category": "language"},
            ]
        }

        mock_client = MagicMock()

        result = llm_interface.rewrite_comments(context_dict, mock_client, groq_free=False)
            
        assert 1 in result
        assert result[1][0]["category"] == "language"
        assert result[1][0]["rewritten"] is None
        mock_client.chat_completion.assert_not_called()

    def test_rewrite_comments_processes_llm(self):
        """Test that LLM comments are rewritten."""
        context_dict = {
            1: [
                {"comment": "Why?", "highlighted": "some text", "paragraph": "full para", "category": "llm"},
            ]
        }
        
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Why is this approach used?"

        result = llm_interface.rewrite_comments(context_dict, mock_client, groq_free=False)

        assert 1 in result
        assert result[1][0]["category"] == "llm"
        assert result[1][0]["rewritten"] is not None
        assert "Why is this approach used?" in result[1][0]["rewritten"]
        mock_client.chat_completion.assert_called_once()

    def test_detect_language_german(self):
        """Test language detection for German."""
        results = {
            1: [
                {"rewritten": "Warum wurde diese Methode gewählt?"},
                {"rewritten": "Können Sie das näher erläutern?"},
            ]
        }
        
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "German"

        lang = llm_interface.detect_language(results, mock_client, groq_free=False)

        assert lang == "German"

    def test_detect_language_english(self):
        """Test language detection for English."""
        results = {
            1: [
                {"rewritten": "Why was this method chosen?"},
                {"rewritten": "Can you explain this further?"},
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "English"

        lang = llm_interface.detect_language(results, mock_client, groq_free=False)
            
        assert lang == "English"


# ============================================================================
# Tests for latex_generation.py
# ============================================================================

class TestLatexGeneration:
    """Tests for LaTeX generation functions."""

    def test_escape_for_latex_special_chars(self):
        """Test LaTeX special character escaping."""
        assert latex_generation.escape_for_latex("100% done") == r"100\% done"
        assert latex_generation.escape_for_latex("A & B") == r"A \& B"
        assert latex_generation.escape_for_latex("$5") == r"\$5"
        assert latex_generation.escape_for_latex("C#") == r"C\#"
        assert latex_generation.escape_for_latex("file_name") == r"file\_name"

    def test_escape_for_latex_german_ss(self):
        """Test German sharp s handling."""
        assert r"{\ss}" in latex_generation.escape_for_latex("Straße")
        assert r"{\ss}" in latex_generation.escape_for_latex("außen")

    def test_escape_for_latex_dashes(self):
        """Test dash normalization."""
        # Various Unicode dashes should be normalized
        text_with_dashes = "test–dash—test"  # en-dash and em-dash
        result = latex_generation.escape_for_latex(text_with_dashes, preserve_latex=True)
        assert "{-}" in result

    def test_escape_for_latex_preserve_latex_commands(self):
        """Test that LaTeX commands are preserved when preserve_latex=True."""
        text = r"Some text with \textbf{bold} and \emph{italic}"
        result = latex_generation.escape_for_latex(text, preserve_latex=True)
        assert r"\textbf" in result
        assert r"\emph" in result

    def test_return_seite_page(self):
        """Test page/Seite translation."""
        assert latex_generation.return_seite_page("German") == "Seite"
        assert latex_generation.return_seite_page("german") == "Seite"
        assert latex_generation.return_seite_page("English") == "page"
        assert latex_generation.return_seite_page("english") == "page"

    def test_concatenate_comments(self):
        """Test comment concatenation for LaTeX."""
        results = {
            1: [
                {"rewritten": "First question?"},
                {"rewritten": "Second question?"},
            ],
            2: [
                {"rewritten": "Third question?"},
            ]
        }
        
        output = latex_generation.concatenate_comments(results, "German", verbose=False)
        
        assert "Seite 1: First question?" in output
        assert "Seite 1: Second question?" in output
        assert "Seite 2: Third question?" in output
        assert "\\\\" in output  # LaTeX line breaks

    def test_create_formal_letter_tex(self):
        """Test LaTeX letter generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            tex_path = f.name
        
        try:
            latex_generation.create_formal_letter_tex(
                filename=tex_path,
                recipient="Test Recipient",
                subject="Test Subject",
                title="Test Thesis Title",
                author="Test Author, Matr.-Nr. 12345",
                summary="This is a test summary.",
                first_examiner="Prof. Test",
                second_examiner="Dr. Test2",
                first_examiner_mail="test@example.com",
                questions="Seite 1: Test question?"
            )
            
            assert os.path.exists(tex_path)
            
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            assert "Test Recipient" in content
            assert "Test Subject" in content
            assert "Test Thesis Title" in content
            assert "Test Author" in content
            assert "This is a test summary" in content
            assert "Test question?" in content
            assert r"\documentclass" in content
            
        finally:
            if os.path.exists(tex_path):
                os.unlink(tex_path)


# ============================================================================
# Tests for utils.py
# ============================================================================

class TestUtils:
    """Tests for utility functions."""

    def test_find_latest_tex_no_files(self):
        """Test finding latest tex when no files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = utils.find_latest_tex(tmpdir)
            assert result is None

    def test_find_latest_tex_single_file(self):
        """Test finding latest tex with one file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "bewertung_brief_12345.tex")
            with open(tex_path, 'w') as f:
                f.write("test")
            
            result = utils.find_latest_tex(tmpdir)
            assert result == tex_path

    def test_find_latest_tex_multiple_files(self):
        """Test finding latest tex with multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first file
            tex_path1 = os.path.join(tmpdir, "bewertung_brief_12345.tex")
            with open(tex_path1, 'w') as f:
                f.write("test1")
            
            # Wait a bit and create second file (newer)
            import time
            time.sleep(0.01)
            
            tex_path2 = os.path.join(tmpdir, "bewertung_brief_67890.tex")
            with open(tex_path2, 'w') as f:
                f.write("test2")
            
            result = utils.find_latest_tex(tmpdir)
            assert result == tex_path2

    def test_find_latest_tex_custom_pattern(self):
        """Test finding latest tex with custom pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # File matching default pattern
            tex_path1 = os.path.join(tmpdir, "bewertung_brief_12345.tex")
            with open(tex_path1, 'w') as f:
                f.write("test1")
            
            # File matching custom pattern
            tex_path2 = os.path.join(tmpdir, "review_12345.tex")
            with open(tex_path2, 'w') as f:
                f.write("test2")
            
            result = utils.find_latest_tex(tmpdir, pattern="review_*.tex")
            assert result == tex_path2


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_annotation_categorization_flow(self):
        """Test the complete flow of annotation categorization."""
        # This is a mock test - real test would need actual PDF
        annotations = {
            0: [
                {"comment": "ab hier", "category": "ignore"},
                {"comment": "Quelle?", "category": "quelle"},
                {"comment": "Rechtschreibung", "category": "language"},
                {"comment": "Why?", "category": "llm"},
            ]
        }
        
        stats = {"quelle": 1, "language": 1, "ignore": 1}
        
        # Verify categories are set correctly
        assert annotations[0][0]["category"] == "ignore"
        assert annotations[0][1]["category"] == "quelle"
        assert annotations[0][2]["category"] == "language"
        assert annotations[0][3]["category"] == "llm"
        
        # Verify stats
        assert stats["quelle"] == 1
        assert stats["language"] == 1
        assert stats["ignore"] == 1


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
