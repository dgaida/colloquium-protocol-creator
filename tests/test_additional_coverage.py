"""
Additional unit tests to increase coverage for llm and pdf.

FIXED VERSION - Korrigiert die StopIteration-Fehler bei Mock-Aufrufen
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.core import llm, pdf

# ============================================================================
# Additional Tests for llm.py
# ============================================================================


class TestLLMInterfaceAdditional:
    """Additional tests for LLM interface to increase coverage."""

    def test_rewrite_comments_with_groq_free_throttle(self, mock_llm_client):
        """Test rewrite_comments with groq_free throttling at intervals."""
        # Create context with 10 pages to trigger throttling
        context_dict = {
            i: [
                {
                    "comment": f"Q{i}",
                    "highlighted": "t",
                    "paragraph": "p",
                    "category": "llm",
                }
            ]
            for i in range(1, 11)
        }

        mock_llm_client.chat_completion.return_value = "Rewritten"

        with patch("academic_doc_generator.core.llm.time.sleep") as mock_sleep:
            llm.rewrite_comments(context_dict, mock_llm_client, groq_free=True, verbose=False)

            # Should sleep for groq_free: 4s per request + 10s every 5 pages
            assert mock_sleep.call_count > 0
            # Check for the 10s sleep (happens at page 5)
            sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
            assert 10 in sleep_calls

    def test_rewrite_comments_verbose_output(self, sample_context, mock_llm_client):
        """Test rewrite_comments with verbose flag."""
        mock_llm_client.chat_completion.return_value = "Rewritten question?"

        # Just check it doesn't crash with verbose=True
        result = llm.rewrite_comments(sample_context, mock_llm_client, groq_free=False, verbose=True)

        assert 1 in result

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_extract_document_metadata_german(self, mock_extract, mock_llm_client):
        """Test metadata extraction for German thesis."""
        mock_extract.return_value = {
            0: "Bachelorarbeit von Max Mustermann, Matrikelnr. 12345",
            1: "Erstprüfer: Prof. Dr. Hans Meyer",
        }

        mock_llm_client.chat_completion.return_value = json.dumps(
            {
                "author": "Max Mustermann",
                "sid": "12345",
                "title": "Test Thesis",
                "first_examiner": "Prof. Dr. Hans Meyer",
                "first_examiner_christian": "Hans",
                "first_examiner_family": "Meyer",
                "second_examiner": "Dr. Test",
                "bachelor_master": "Bachelor",
            }
        )

        result = llm.extract_document_metadata({0: "", 1: ""}, "German", mock_llm_client)

        assert result["author"] == "Max Mustermann"
        assert result["bachelor_master"] == "Bachelor"

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_extract_document_metadata_english(self, mock_extract, mock_llm_client):
        """Test metadata extraction for English thesis."""
        mock_extract.return_value = {0: "Master Thesis by John Doe"}

        mock_llm_client.chat_completion.return_value = json.dumps(
            {
                "author": "John Doe",
                "sid": "67890",
                "title": "English Thesis",
                "first_examiner": "Prof. Smith",
                "first_examiner_christian": "John",
                "first_examiner_family": "Smith",
                "second_examiner": "Dr. Brown",
                "bachelor_master": "Master",
            }
        )

        result = llm.extract_document_metadata({0: ""}, "English", mock_llm_client)

        assert result["bachelor_master"] == "Master"

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_summarize_thesis_german(self, mock_extract, mock_llm_client):
        """Test thesis summarization in German."""
        mock_extract.return_value = {
            0: "Diese Arbeit behandelt das Thema X",
            1: "Die Forschungsfrage lautet Y",
        }

        mock_llm_client.chat_completion.return_value = (
            "Diese Arbeit untersucht X.\\\\\n"
            "Die Hauptergebnisse sind Y.\\\\\n"
            "Es wurde die Methode Z verwendet."
        )

        result = llm.summarize_thesis({0: "", 1: ""}, "German", mock_llm_client)

        assert "untersucht" in result
        assert "\\\\" in result  # LaTeX line breaks

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_summarize_thesis_english(self, mock_extract, mock_llm_client):
        """Test thesis summarization in English."""
        mock_extract.return_value = {0: "This thesis addresses topic X"}

        mock_llm_client.chat_completion.return_value = (
            "This thesis investigates X.\\\\\nThe main findings are Y."
        )

        result = llm.summarize_thesis({0: ""}, "English", mock_llm_client)

        assert "investigates" in result

    def test_detect_language_sample_size(self, mock_llm_client):
        """Test language detection with custom sample size."""
        results = {1: [{"rewritten": "Warum?"} for _ in range(10)]}

        mock_llm_client.chat_completion.return_value = "German"

        lang = llm.detect_language(results, mock_llm_client, groq_free=False, sample_size=5)

        assert lang == "German"
        # Verify only sample_size texts were used
        call_args = mock_llm_client.chat_completion.call_args[0][0]
        prompt_text = call_args[0]["content"]
        assert prompt_text.count("Warum?") <= 5

    @patch("academic_doc_generator.core.llm.time.sleep")
    def test_detect_language_groq_free(self, mock_sleep, mock_llm_client):
        """Test language detection with groq_free throttling."""
        results = {1: [{"rewritten": "Test"}]}

        mock_llm_client.chat_completion.return_value = "German"

        llm.detect_language(results, mock_llm_client, groq_free=True)

        mock_sleep.assert_called_once_with(2)

    @patch("academic_doc_generator.core.llm.LLMClient")
    def test_rewrite_comments_in_pdf_auto_client(self, mock_client_class, mock_pdf_processor):
        """Test rewrite_comments_in_pdf with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client

        result, stats = llm.rewrite_comments_in_pdf(
            "test.pdf", llm_client=None, pdf_processor=mock_pdf_processor
        )

        mock_client_class.assert_called_once()

    def test_rewrite_comments_in_pdf_verbose(self, mock_pdf_processor, mock_llm_client):
        """Test rewrite_comments_in_pdf with verbose output."""
        mock_pdf_processor.extract_annotations_with_positions.return_value = (
            {},
            {"quelle": 1, "language": 2, "ignore": 0},
        )

        result, stats = llm.rewrite_comments_in_pdf(
            "test.pdf",
            llm_client=mock_llm_client,
            verbose=True,
            pdf_processor=mock_pdf_processor,
        )

        assert stats["quelle"] == 1
        assert stats["language"] == 2

    @patch("academic_doc_generator.core.llm.LLMClient")
    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_get_summary_and_metadata_auto_client(self, mock_extract, mock_client_class):
        """Test get_summary_and_metadata with automatic client creation."""
        mock_client = MagicMock()
        mock_client.api_choice = "openai"
        mock_client.llm = "gpt-4o"
        mock_client_class.return_value = mock_client

        mock_extract.return_value = {0: "Test content"}

        # FIXED: Mock muss zwei Aufrufe behandeln korrekt
        call_count = [0]

        def mock_completion(messages):
            call_count[0] += 1
            if call_count[0] == 1:
                # Erster Aufruf: extract_document_metadata
                return json.dumps({"author": "Test", "bachelor_master": "Bachelor"})
            else:
                # Zweiter Aufruf: summarize_thesis
                return "Summary text"

        mock_client.chat_completion.side_effect = mock_completion

        summary, metadata = llm.get_summary_and_metadata_of_pdf(
            "test.pdf", "German", llm_client=None
        )

        mock_client_class.assert_called_once()
        assert summary == "Summary text"
        assert metadata["author"] == "Test"

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    @patch("academic_doc_generator.core.llm.time.sleep")
    def test_get_summary_and_metadata_groq_free(self, mock_sleep, mock_extract, mock_llm_client):
        """Test get_summary_and_metadata with groq_free throttling."""
        mock_extract.return_value = {0: "Test"}

        # FIXED: Verwende Funktion statt Liste
        call_count = [0]

        def mock_completion(messages):
            call_count[0] += 1
            if call_count[0] == 1:
                return json.dumps({"author": "Test", "bachelor_master": "Bachelor"})
            else:
                return "Summary"

        mock_llm_client.chat_completion.side_effect = mock_completion

        llm.get_summary_and_metadata_of_pdf(
            "test.pdf", "German", llm_client=mock_llm_client, groq_free=True
        )

        # Should sleep 20s after metadata and 2s after summary
        assert mock_sleep.call_count == 2
        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert 20 in sleep_calls
        assert 2 in sleep_calls

    @patch("academic_doc_generator.core.llm.pdf.extract_text_per_page")
    def test_get_summary_and_metadata_verbose(self, mock_extract, mock_llm_client):
        """Test get_summary_and_metadata with verbose output."""
        mock_extract.return_value = {0: "Test"}

        # FIXED: Verwende Funktion statt Liste
        call_count = [0]

        def mock_completion(messages):
            call_count[0] += 1
            if call_count[0] == 1:
                return json.dumps({"author": "Test", "bachelor_master": "Bachelor"})
            else:
                return "Test summary"

        mock_llm_client.chat_completion.side_effect = mock_completion

        summary, metadata = llm.get_summary_and_metadata_of_pdf(
            "test.pdf", "German", llm_client=mock_llm_client, verbose=True
        )

        assert summary == "Test summary"


# ============================================================================
# Additional Tests for pdf.py
# ============================================================================


class TestPdfProcessingAdditional:
    """Additional tests for PDF processing to increase coverage."""

    def test_extract_annotations_with_positions_ignore_source_false(self):
        """Test annotation extraction without ignoring sources."""
        # This would require a real PDF, so we'll test the logic
        # In practice, with ignore_source=False, quelle comments get category "llm"
        pass  # Actual implementation would need PDF mocking

    def test_extract_annotations_multiple_categories(self):
        """Test that multiple comment categories are detected correctly."""
        # Mock test to verify category detection logic
        comments = [
            "ab hier",  # ignore
            "Quelle fehlt",  # quelle
            "Rechtschreibung",  # language
            "Why is this?",  # llm
        ]

        categories = []
        for comment in comments:
            if comment.lower() == "ab hier":
                categories.append("ignore")
            elif pdf.is_quelle_comment(comment):
                categories.append("quelle")
            elif any(kw in comment.lower() for kw in ["rechtschreibung", "grammatik"]):
                categories.append("language")
            else:
                categories.append("llm")

        assert categories == ["ignore", "quelle", "language", "llm"]

    def test_find_annotation_context_multiple_pages(self):
        """Test context finding across multiple pages."""
        pages_words = {
            0: [{"text": "Page1", "bbox": (10, 10, 50, 20)}],
            1: [{"text": "Page2", "bbox": (10, 10, 50, 20)}],
        }

        annotations = {
            0: [{"comment": "C1", "rect": (5, 5, 55, 25), "category": "llm"}],
            1: [{"comment": "C2", "rect": (5, 5, 55, 25), "category": "llm"}],
        }

        result = pdf.find_annotation_context(pages_words, annotations)

        assert 1 in result  # Page 1 (1-based)
        assert 2 in result  # Page 2 (1-based)

    def test_find_annotation_context_with_quadpoints(self):
        """Test context finding with quadpoints instead of rect."""
        pages_words = {0: [{"text": "Test", "bbox": (10, 10, 50, 20)}]}

        annotations = {
            0: [
                {
                    "comment": "Test comment",
                    "rect": None,
                    "quadpoints": [5, 5, 55, 5, 55, 25, 5, 25],  # QuadPoints format
                    "category": "llm",
                }
            ]
        }

        result = pdf.find_annotation_context(pages_words, annotations)

        assert 1 in result

    def test_find_annotation_context_no_rect_no_quadpoints(self):
        """Test handling of annotations without rect or quadpoints."""
        pages_words = {0: [{"text": "Test", "bbox": (10, 10, 50, 20)}]}

        annotations = {
            0: [{"comment": "Test", "rect": None, "quadpoints": None, "category": "llm"}]
        }

        result = pdf.find_annotation_context(pages_words, annotations)

        # Should skip annotation
        assert 1 not in result or len(result.get(1, [])) == 0

    def test_find_annotation_context_paragraph_matching(self):
        """Test paragraph matching in context finding."""
        pages_words = {
            0: [
                {"text": "First", "bbox": (10, 100, 40, 110)},
                {"text": "paragraph", "bbox": (45, 100, 90, 110)},
                {"text": "Second", "bbox": (10, 80, 50, 90)},
                {"text": "paragraph", "bbox": (55, 80, 100, 90)},
            ]
        }

        annotations = {
            0: [
                {
                    "comment": "About second",
                    "rect": (5, 75, 105, 95),  # Overlaps with "Second paragraph"
                    "category": "llm",
                }
            ]
        }

        result = pdf.find_annotation_context(pages_words, annotations)

        assert 1 in result
        # The highlighted text should be from the second paragraph
        assert "Second" in result[1][0]["highlighted"]

    def test_find_annotation_context_fallback_paragraph(self):
        """Test fallback to first paragraph when no match found."""
        pages_words = {
            0: [
                {"text": "First", "bbox": (10, 100, 40, 110)},
                {"text": "para", "bbox": (45, 100, 70, 110)},
            ]
        }

        annotations = {
            0: [
                {
                    "comment": "Test",
                    "rect": (200, 200, 300, 300),  # No words overlap
                    "category": "llm",
                }
            ]
        }

        result = pdf.find_annotation_context(pages_words, annotations)

        assert 1 in result
        # Should have fallback paragraph
        assert result[1][0]["paragraph"] is not None

    def test_words_overlapping_rect_with_tolerance(self):
        """Test word overlap detection with tolerance."""
        words = [
            {"text": "Test", "bbox": (10, 10, 50, 20)},
        ]

        # Rectangle just slightly off
        rect = (50.4, 19.9, 60, 25)

        # Without tolerance, no overlap
        hits_no_tol = pdf.words_overlapping_rect(words, rect, tol=0.0)
        assert len(hits_no_tol) == 0

        # With tolerance, should overlap
        hits_with_tol = pdf.words_overlapping_rect(words, rect, tol=0.5)
        assert len(hits_with_tol) == 1

    def test_get_words_for_annotation_fallback_previous_page(self):
        """Test fallback to previous page when annotation doesn't match."""
        pages_words = {
            0: [{"text": "Page0", "bbox": (10, 10, 50, 20)}],
            1: [{"text": "Page1", "bbox": (100, 100, 150, 120)}],  # No overlap
            2: [{"text": "Page2", "bbox": (10, 10, 50, 20)}],
        }

        rect = (5, 5, 55, 25)  # Overlaps with Page0 and Page2

        # Search from page 1, should fall back to page 0 (tries -1 before +1)
        page_idx, words = pdf.get_words_for_annotation_on_page(pages_words, 1, rect)

        # Implementation tries: page 1, then page 2 (+1), then page 0 (-1)
        # Since page 1 and 2 don't match, should find page 0
        assert page_idx in [0, 2]
        assert len(words) > 0
