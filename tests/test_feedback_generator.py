from unittest.mock import MagicMock, patch

from academic_doc_generator.project.feedback_generator import generate_feedback_summary


class TestFeedbackGenerator:
    @patch("academic_doc_generator.project.feedback_generator.extract_text_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.extract_annotations_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.find_annotation_context")
    def test_generate_feedback_summary_success(self, mock_context, mock_annot, mock_text):
        mock_text.return_value = {}
        mock_annot.return_value = ({}, {"quelle": 0})
        mock_context.return_value = {
            1: [
                {
                    "comment": "Poor structure",
                    "highlighted": "Intro",
                    "category": "llm",
                },
                {
                    "comment": "Good analysis",
                    "highlighted": "Conclusion",
                    "category": "llm",
                },
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.side_effect = [
            "Struktur verbessern.",
            "Gute Analyse.",
            "- Struktur verbessern.\n- Gute Analyse.",
        ]

        summary = generate_feedback_summary("test.pdf", mock_client)

        assert "- Struktur verbessern." in summary
        assert "- Gute Analyse." in summary
        assert mock_client.chat_completion.call_count == 3

    @patch("academic_doc_generator.project.feedback_generator.extract_text_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.extract_annotations_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.find_annotation_context")
    def test_generate_feedback_summary_no_comments(self, mock_context, mock_annot, mock_text):
        mock_text.return_value = {}
        mock_annot.return_value = ({}, {"quelle": 0})
        mock_context.return_value = {}

        mock_client = MagicMock()
        summary = generate_feedback_summary("test.pdf", mock_client)

        assert "Keine spezifischen Anmerkungen" in summary
        mock_client.chat_completion.assert_not_called()

    @patch("academic_doc_generator.project.feedback_generator.extract_text_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.extract_annotations_with_positions")
    @patch("academic_doc_generator.project.feedback_generator.find_annotation_context")
    def test_generate_feedback_summary_with_ignore(self, mock_context, mock_annot, mock_text):
        mock_text.return_value = {}
        mock_annot.return_value = ({}, {"quelle": 0})
        mock_context.return_value = {
            1: [
                {
                    "comment": "Ignore this comment",
                    "highlighted": "Intro",
                    "category": "ignore",
                },
                {
                    "comment": "Good analysis",
                    "highlighted": "Conclusion",
                    "category": "llm",
                },
            ]
        }

        mock_client = MagicMock()
        mock_client.chat_completion.side_effect = [
            "Gute Analyse.",
            "- Gute Analyse.",
        ]

        summary = generate_feedback_summary("test.pdf", mock_client)

        assert "- Gute Analyse." in summary
        # Since "Ignore this comment" is category "ignore", it should be skipped
        # So chat_completion is called only twice (1 for "Good analysis" and 1 for compiling summary)
        assert mock_client.chat_completion.call_count == 2
