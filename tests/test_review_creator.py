"""
Unit tests for the review_creator package - FIXED VERSION
"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from academic_doc_generator.review import md_generator


# ============================================================================
# Tests for review_creator/md_generator.py
# ============================================================================


class TestMdGenerator:
    """Tests for peer review markdown generation."""

    def test_estimate_line_number_top_of_page(self):
        """Test line number estimation at top of page."""
        page_height = 792.0  # Standard US Letter height in points

        # Top of page (y close to page_height)
        line_num = md_generator.estimate_line_number(
            y_coord=780.0, page_height=page_height, line_height=12.0
        )
        assert line_num == 2  # Near top = line 1 or 2

    def test_estimate_line_number_middle_of_page(self):
        """Test line number estimation in middle of page."""
        page_height = 792.0

        # Middle of page
        line_num = md_generator.estimate_line_number(
            y_coord=400.0, page_height=page_height, line_height=12.0
        )
        assert 30 < line_num < 40  # Approximately line 33

    def test_estimate_line_number_bottom_of_page(self):
        """Test line number estimation at bottom of page."""
        page_height = 792.0

        # Bottom of page (y close to 0)
        line_num = md_generator.estimate_line_number(
            y_coord=50.0, page_height=page_height, line_height=12.0
        )
        assert line_num > 60  # Near bottom = high line number

    def test_estimate_line_number_custom_line_height(self):
        """Test line number estimation with custom line height."""
        page_height = 792.0

        # Same y-coord but different line heights should give different results
        line_num_12pt = md_generator.estimate_line_number(
            y_coord=400.0, page_height=page_height, line_height=12.0
        )
        line_num_24pt = md_generator.estimate_line_number(
            y_coord=400.0, page_height=page_height, line_height=24.0
        )

        # Larger line height = fewer lines
        assert line_num_24pt < line_num_12pt

    def test_estimate_line_number_minimum(self):
        """Test that line number is at least 1."""
        page_height = 792.0

        # Even at very top
        line_num = md_generator.estimate_line_number(
            y_coord=800.0,  # Above page height
            page_height=page_height,
            line_height=12.0,
        )
        assert line_num >= 1

    def test_find_line_number_from_text_found(self):
        """Test finding printed line number from words."""
        words = [
            {"text": "42", "bbox": (10, 100, 20, 110)},  # Line number at left margin
            {"text": "Some", "bbox": (50, 100, 80, 110)},
            {"text": "text", "bbox": (85, 100, 110, 110)},
        ]
        # Annotation overlaps vertically with line 42
        annot_bbox = (45, 95, 115, 115)

        line_num = md_generator.find_line_number_from_text(
            words, annot_bbox, x_threshold=20.0
        )

        assert line_num == 42

    def test_find_line_number_from_text_not_found(self):
        """Test when no line number is found."""
        words = [
            {"text": "Some", "bbox": (50, 100, 80, 110)},
            {"text": "text", "bbox": (85, 100, 110, 110)},
        ]
        annot_bbox = (45, 95, 115, 115)

        line_num = md_generator.find_line_number_from_text(
            words, annot_bbox, x_threshold=20.0
        )

        assert line_num == -1

    def test_find_line_number_from_text_wrong_position(self):
        """Test that numbers not at left margin are ignored."""
        words = [
            {"text": "42", "bbox": (100, 100, 110, 110)},  # Not at margin
            {"text": "Some", "bbox": (50, 100, 80, 110)},
        ]
        annot_bbox = (45, 95, 115, 115)

        line_num = md_generator.find_line_number_from_text(
            words, annot_bbox, x_threshold=20.0
        )

        assert line_num == -1

    def test_find_line_number_from_text_non_digit(self):
        """Test that non-numeric text at margin is ignored."""
        words = [
            {"text": "ABC", "bbox": (10, 100, 20, 110)},  # Not a number
            {"text": "Some", "bbox": (50, 100, 80, 110)},
        ]
        annot_bbox = (45, 95, 115, 115)

        line_num = md_generator.find_line_number_from_text(
            words, annot_bbox, x_threshold=20.0
        )

        assert line_num == -1

    def test_find_annotation_context_with_lines(self):
        """Test annotation context extraction with line numbers."""
        # Place line number at a y-coordinate that will be found
        pages_words = {
            0: [
                {"text": "25", "bbox": (10, 500, 20, 510)},
                {"text": "Important", "bbox": (50, 500, 120, 510)},
                {"text": "text", "bbox": (125, 500, 160, 510)},
            ]
        }

        annotations = {
            0: [
                {
                    "comment": "Why is this important?",
                    "rect": (45, 495, 165, 515),  # Overlaps with y=500-510
                    "category": "llm",
                }
            ]
        }

        page_heights = {0: 792.0}

        result = md_generator.find_annotation_context_with_lines(
            pages_words, annotations, page_heights
        )

        assert 1 in result  # Page 1 (1-based)
        assert len(result[1]) == 1
        assert result[1][0]["comment"] == "Why is this important?"
        assert result[1][0]["line"] == 25  # Should find the line number from text
        assert result[1][0]["category"] == "llm"

    def test_find_annotation_context_with_lines_fallback(self):
        """Test fallback to geometric estimation when no line number found."""
        pages_words = {
            0: [
                {"text": "Important", "bbox": (50, 100, 120, 110)},
                {"text": "text", "bbox": (125, 100, 160, 110)},
            ]
        }

        annotations = {
            0: [
                {"comment": "Check this", "rect": (45, 95, 165, 115), "category": "llm"}
            ]
        }

        page_heights = {0: 792.0}

        result = md_generator.find_annotation_context_with_lines(
            pages_words, annotations, page_heights
        )

        assert 1 in result
        assert result[1][0]["line"] > 0  # Should have estimated a line number

    def test_find_annotation_context_with_lines_no_rect(self):
        """Test handling of annotations without rectangles."""
        pages_words = {0: []}
        annotations = {
            0: [{"comment": "Test comment", "rect": None, "category": "llm"}]
        }
        page_heights = {0: 792.0}

        result = md_generator.find_annotation_context_with_lines(
            pages_words, annotations, page_heights
        )

        # Should skip annotation without rect
        assert 1 not in result or len(result.get(1, [])) == 0

    def test_rewrite_comments_markdown_llm_category(self):
        """Test rewriting comments for LLM category."""
        context_dict = {
            1: [
                {
                    "comment": "Why?",
                    "paragraph": "Some paragraph",
                    "highlighted": "important text",
                    "category": "llm",
                    "line": 42,
                }
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = (
            "Could you please explain the rationale behind this approach?"
        )

        result = md_generator.rewrite_comments_markdown(
            context_dict, mock_client, groq_free=False
        )

        assert 1 in result
        assert len(result[1]) == 1
        assert (
            result[1][0]["rewritten"]
            == "Could you please explain the rationale behind this approach?"
        )
        assert result[1][0]["line"] == 42
        assert result[1][0]["page"] == 1
        mock_client.chat_completion.assert_called_once()

    def test_rewrite_comments_markdown_skip_non_llm(self):
        """Test that non-LLM categories are skipped."""
        context_dict = {
            1: [
                {
                    "comment": "Quelle?",
                    "paragraph": "",
                    "highlighted": "",
                    "category": "quelle",
                    "line": 10,
                },
                {
                    "comment": "Rechtschreibung",
                    "paragraph": "",
                    "highlighted": "",
                    "category": "language",
                    "line": 20,
                },
            ]
        }

        mock_client = MagicMock()

        result = md_generator.rewrite_comments_markdown(
            context_dict, mock_client, groq_free=False
        )

        # Should not have any results since both are non-LLM
        assert 1 not in result or len(result.get(1, [])) == 0
        mock_client.chat_completion.assert_not_called()

    def test_rewrite_comments_markdown_multiple_pages(self):
        """Test rewriting comments across multiple pages."""
        context_dict = {
            1: [
                {
                    "comment": "First question",
                    "paragraph": "para1",
                    "highlighted": "text1",
                    "category": "llm",
                    "line": 10,
                }
            ],
            2: [
                {
                    "comment": "Second question",
                    "paragraph": "para2",
                    "highlighted": "text2",
                    "category": "llm",
                    "line": 25,
                }
            ],
        }

        mock_client = MagicMock()
        mock_client.chat_completion.side_effect = [
            "Rewritten first question?",
            "Rewritten second question?",
        ]

        result = md_generator.rewrite_comments_markdown(
            context_dict, mock_client, groq_free=False
        )

        assert 1 in result
        assert 2 in result
        assert result[1][0]["page"] == 1
        assert result[2][0]["page"] == 2
        assert mock_client.chat_completion.call_count == 2

    @patch("review_creator.md_generator.time.sleep")
    def test_rewrite_comments_markdown_groq_free_throttle(self, mock_sleep):
        """Test that groq_free applies throttling."""
        context_dict = {
            1: [
                {
                    "comment": "Test",
                    "paragraph": "",
                    "highlighted": "",
                    "category": "llm",
                    "line": 1,
                }
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Rewritten"

        md_generator.rewrite_comments_markdown(
            context_dict, mock_client, groq_free=True
        )

        # Should not sleep for just 1 comment (sleep happens at intervals of 5)
        mock_sleep.assert_not_called()

    def test_create_review_markdown_single_page(self):
        """Test creating markdown review with single page."""
        rewritten = {
            1: [{"rewritten": "Please clarify this point.", "line": 42, "page": 1}]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            md_path = f.name

        try:
            md_generator.create_review_markdown(rewritten, md_path)

            assert os.path.exists(md_path)

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "# Peer Review" in content
            assert "Dear authors," in content
            assert "Page 1, Line 42: Please clarify this point." in content

        finally:
            if os.path.exists(md_path):
                os.unlink(md_path)

    def test_create_review_markdown_multiple_comments(self):
        """Test creating markdown review with multiple comments."""
        rewritten = {
            1: [
                {"rewritten": "First comment.", "line": 10, "page": 1},
                {"rewritten": "Second comment.", "line": 20, "page": 1},
            ],
            2: [{"rewritten": "Third comment.", "line": 5, "page": 2}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            md_path = f.name

        try:
            md_generator.create_review_markdown(rewritten, md_path)

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "Page 1, Line 10: First comment." in content
            assert "Page 1, Line 20: Second comment." in content
            assert "Page 2, Line 5: Third comment." in content

        finally:
            if os.path.exists(md_path):
                os.unlink(md_path)

    def test_create_review_markdown_empty(self):
        """Test creating markdown review with no comments."""
        rewritten = {}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            md_path = f.name

        try:
            md_generator.create_review_markdown(rewritten, md_path)

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Should still have header structure
            assert "# Peer Review" in content
            assert "Dear authors," in content

        finally:
            if os.path.exists(md_path):
                os.unlink(md_path)


# ============================================================================
# Integration Tests
# ============================================================================


class TestReviewIntegration:
    """Integration tests for review pipeline."""

    def test_full_review_flow(self):
        """Test complete flow from annotations to markdown review."""
        # Mock annotation data - place line number at y=700 to get line 15 geometrically
        # Line 15 with 12pt line height from top: 15 * 12 = 180 points from top
        # So y = 792 - 180 = 612
        # Let's use a y-coordinate that gives us approximately line 15
        y_for_line_15 = 792.0 - (15 * 12)  # = 612

        pages_words = {
            0: [
                {"text": "15", "bbox": (10, y_for_line_15, 20, y_for_line_15 + 10)},
                {"text": "This", "bbox": (50, y_for_line_15, 80, y_for_line_15 + 10)},
                {"text": "needs", "bbox": (85, y_for_line_15, 120, y_for_line_15 + 10)},
                {
                    "text": "review",
                    "bbox": (125, y_for_line_15, 170, y_for_line_15 + 10),
                },
            ]
        }

        annotations = {
            0: [
                {
                    "comment": "unclear",
                    "rect": (45, y_for_line_15 - 5, 175, y_for_line_15 + 15),
                    "category": "llm",
                }
            ]
        }

        page_heights = {0: 792.0}

        # Step 1: Find context with lines
        context = md_generator.find_annotation_context_with_lines(
            pages_words, annotations, page_heights
        )

        assert 1 in context
        assert context[1][0]["line"] == 15

        # Step 2: Rewrite comments
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = (
            "This section requires further clarification."
        )

        rewritten = md_generator.rewrite_comments_markdown(
            context, mock_client, groq_free=False
        )

        assert 1 in rewritten
        assert rewritten[1][0]["line"] == 15

        # Step 3: Create markdown
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            md_path = f.name

        try:
            md_generator.create_review_markdown(rewritten, md_path)

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert (
                "Page 1, Line 15: This section requires further clarification."
                in content
            )

        finally:
            if os.path.exists(md_path):
                os.unlink(md_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
