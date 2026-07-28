import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from academic_doc_generator.cli import handlers
from academic_doc_generator.colloquium import orchestrator, pdf_form_filler
from academic_doc_generator.colloquium.gemini_thesis_evaluator import GeminiThesisEvaluator
from academic_doc_generator.core import llm, pdf
from academic_doc_generator.core.types import ColloquiumWorkflowConfig
from academic_doc_generator.exam_translator import translator

# --- Tests for GeminiThesisEvaluator ---


class TestGeminiThesisEvaluator:
    def test_init_success(self, mock_llm_client):
        mock_llm_client.api_choice = "gemini"
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        assert evaluator.llm_client == mock_llm_client

    def test_init_failure(self, mock_llm_client):
        mock_llm_client.api_choice = "openai"
        with pytest.raises(
            ValueError,
            match="GeminiThesisEvaluator benötigt einen LLMClient mit api_choice='gemini'",
        ):
            GeminiThesisEvaluator(mock_llm_client)

    @patch("academic_doc_generator.colloquium.gemini_thesis_evaluator.PdfReader")
    @patch("academic_doc_generator.colloquium.gemini_thesis_evaluator.PdfWriter")
    def test_remove_first_page(self, mock_writer_cls, mock_reader_cls, mock_llm_client):
        mock_llm_client.api_choice = "gemini"
        evaluator = GeminiThesisEvaluator(mock_llm_client)

        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock(), MagicMock(), MagicMock()]  # 3 pages
        mock_reader_cls.return_value = mock_reader

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_temp_file = MagicMock()
            mock_temp_file.name = "temp.pdf"
            mock_temp.return_value.__enter__.return_value = mock_temp_file

            result = evaluator._remove_first_page("original.pdf")

            assert result == "temp.pdf"
            assert mock_writer.add_page.call_count == 1  # 3 - 2 = 1 (removes first and last)

    def test_create_emark_prompt(self, mock_llm_client):
        mock_llm_client.api_choice = "gemini"
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        prompt = evaluator._create_emark_prompt("Title", "Bachelor")
        assert "Bachelor" in prompt
        assert "Title" in prompt

    @patch.object(GeminiThesisEvaluator, "_remove_first_page")
    @patch("os.unlink")
    def test_evaluate_thesis_success_legacy(self, mock_unlink, mock_remove_page, mock_llm_client):
        mock_llm_client.api_choice = "gemini"
        mock_llm_client.chat_completion_with_files.return_value = "Excellent work"
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        mock_remove_page.return_value = "temp.pdf"

        result = evaluator.evaluate_thesis(
            "test.pdf", "Title", "Bachelor", use_text_extraction=False
        )

        assert result == "Excellent work"
        mock_unlink.assert_called_with("temp.pdf")

    @patch.object(GeminiThesisEvaluator, "_remove_first_page")
    @patch.object(GeminiThesisEvaluator, "_extract_text_from_pdf")
    @patch("os.unlink")
    def test_evaluate_thesis_success_text(
        self, mock_unlink, mock_extract, mock_remove_page, mock_llm_client
    ):
        mock_llm_client.api_choice = "gemini"
        mock_llm_client.chat_completion.return_value = "Excellent work text"
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        mock_remove_page.return_value = "temp.pdf"
        mock_extract.return_value = "Extracted text content"

        result = evaluator.evaluate_thesis(
            "test.pdf", "Title", "Bachelor", use_text_extraction=True
        )

        assert result == "Excellent work text"
        mock_unlink.assert_called_with("temp.pdf")
        assert mock_extract.called
        assert mock_llm_client.chat_completion.called

    @patch.object(GeminiThesisEvaluator, "_remove_first_page")
    @patch.object(GeminiThesisEvaluator, "_extract_text_from_pdf")
    @patch("os.path.exists")
    @patch("os.unlink")
    def test_evaluate_thesis_exception(
        self, mock_unlink, mock_exists, mock_extract, mock_remove_page, mock_llm_client
    ):
        mock_llm_client.api_choice = "gemini"
        # The code will default to text extraction (GeminiThesisEvaluator:111),
        # so we need to mock chat_completion, not chat_completion_with_files.
        mock_llm_client.chat_completion.side_effect = Exception("API Error")
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        mock_remove_page.return_value = "temp.pdf"
        mock_exists.return_value = True

        result = evaluator.evaluate_thesis("test.pdf", "Title", "Bachelor")

        assert result is None
        mock_unlink.assert_called_with("temp.pdf")

    def test_format_emark_for_latex(self, mock_llm_client):
        mock_llm_client.api_choice = "gemini"
        evaluator = GeminiThesisEvaluator(mock_llm_client)
        emark = "```latex\nSome LaTeX code\n```"
        formatted = evaluator.format_emark_for_latex(emark)
        assert "Some LaTeX code" in formatted
        assert "```latex" not in formatted
        assert "Automatische Bewertung" in formatted


# --- Tests for core.pdf ---


class TestCorePdf:
    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    def test_extract_text_with_positions(self, mock_parser_cls):
        mock_parser = MagicMock()
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "Hello"
        mock_cell.rect.r_x0 = 0
        mock_cell.rect.r_y0 = 0
        mock_cell.rect.r_x1 = 10
        mock_cell.rect.r_y1 = 10

        mock_page.iterate_cells.return_value = [mock_cell]
        mock_doc.iterate_pages.return_value = [(1, mock_page)]
        mock_parser.load.return_value = mock_doc
        mock_parser_cls.return_value = mock_parser

        result = pdf.extract_text_with_positions("test.pdf")
        assert result[0][0]["text"] == "Hello"
        assert result[0][0]["bbox"] == (0.0, 0.0, 10.0, 10.0)

    def test_is_quelle_comment(self):
        assert pdf.is_quelle_comment("Quelle?") is True
        assert pdf.is_quelle_comment("Source missing") is True
        assert pdf.is_quelle_comment("Consequent") is False
        assert (
            pdf.is_quelle_comment(
                "This is a very long comment about sources that should be ignored", max_length=10
            )
            is False
        )

    @patch("academic_doc_generator.core.pdf.PdfReader")
    def test_extract_annotations_with_positions(self, mock_reader_cls):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_annot = MagicMock()
        mock_annot.get_object.return_value = {
            "/Subtype": "/Text",
            "/Rect": [0, 0, 10, 10],
            "/Contents": "Quelle?",
        }
        mock_page.__contains__.side_effect = lambda x: x == "/Annots"
        mock_page.__getitem__.side_effect = lambda x: [mock_annot] if x == "/Annots" else None
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        annots, stats = pdf.extract_annotations_with_positions("test.pdf")
        assert annots[0][0]["comment"] == "Quelle?"
        assert annots[0][0]["category"] == "quelle"
        assert stats["quelle"] == 1

        # Test other categories
        mock_annot.get_object.return_value["/Contents"] = "ab hier"
        annots, stats = pdf.extract_annotations_with_positions("test.pdf")
        assert annots[0][0]["category"] == "ignore"

        mock_annot.get_object.return_value["/Contents"] = "Grammatikfehler"
        annots, stats = pdf.extract_annotations_with_positions("test.pdf")
        assert annots[0][0]["category"] == "language"

    def test_words_overlapping_rect(self):
        words = [{"text": "Hello", "bbox": (10, 10, 20, 20)}]
        rect = (5, 5, 25, 25)
        assert len(pdf.words_overlapping_rect(words, rect)) == 1

        rect = (30, 30, 40, 40)
        assert len(pdf.words_overlapping_rect(words, rect)) == 0

    def test_get_words_for_annotation_on_page(self):
        pages_words = {0: [{"text": "Hello", "bbox": (10, 10, 20, 20)}]}
        rect = (5, 5, 25, 25)
        idx, hits = pdf.get_words_for_annotation_on_page(pages_words, 0, rect)
        assert idx == 0
        assert len(hits) == 1

        idx, hits = pdf.get_words_for_annotation_on_page(
            pages_words, 1, rect
        )  # Check neighboring page
        assert idx == 0
        assert len(hits) == 1

    def test_rect_overlap(self):
        assert pdf.rect_overlap((10, 10, 20, 20), (5, 5, 25, 25)) is True
        assert pdf.rect_overlap((10, 10, 20, 20), (25, 25, 30, 30)) is False

    def test_find_annotation_context(self):
        pages_words = {
            0: [
                {"text": "Target", "bbox": (10, 10, 20, 20)},
                {"text": "Other", "bbox": (50, 50, 60, 60)},
            ]
        }
        annotations = {
            0: [{"comment": "Note", "rect": [5, 5, 25, 25], "category": "llm", "quadpoints": None}]
        }

        context = pdf.find_annotation_context(pages_words, annotations)
        assert context[1][0]["highlighted"] == "Target"
        assert "Target" in context[1][0]["paragraph"]

    def test_find_annotation_context_fallback_paragraph(self):
        pages_words = {0: [{"text": "Hello", "bbox": (10, 10, 20, 20)}]}
        # Highlighted text not in full text (somehow)
        annotations = {
            0: [{"comment": "Note", "rect": [5, 5, 25, 25], "category": "llm", "quadpoints": None}]
        }
        with patch("academic_doc_generator.core.pdf.get_words_for_annotation_on_page") as mock_get:
            mock_get.return_value = (0, [{"text": "Missing", "bbox": (10, 10, 20, 20)}])
            context = pdf.find_annotation_context(pages_words, annotations)
            assert context[1][0]["highlighted"] == "Missing"
            assert context[1][0]["paragraph"] == "Hello"  # Fallback to first paragraph

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    def test_extract_text_per_page(self, mock_parser_cls):
        mock_parser = MagicMock()
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "Hello"
        mock_page.iterate_cells.return_value = [mock_cell]
        mock_doc.iterate_pages.return_value = [(1, mock_page), (2, mock_page)]
        mock_parser.load.return_value = mock_doc
        mock_parser_cls.return_value = mock_parser

        result = pdf.extract_text_per_page("test.pdf", max_pages=1)
        assert len(result) == 1
        assert result[0] == "Hello"

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    @patch("pymupdf.open")
    def test_extract_text_with_positions_fallback(self, mock_pymupdf_open, mock_parser_cls):
        # Force docling parser to fail
        mock_parser = MagicMock()
        mock_parser.load.side_effect = MemoryError("Simulated std::bad_alloc")
        mock_parser_cls.return_value = mock_parser

        # Set up pymupdf mock
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.rect.y1 = 800.0
        mock_page.get_text.return_value = [(10.0, 100.0, 50.0, 120.0, "Hello", 0, 0, 0)]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf_open.return_value = mock_doc

        result = pdf.extract_text_with_positions("dummy.pdf")

        assert 0 in result
        assert len(result[0]) == 1
        assert result[0][0]["text"] == "Hello"
        # Expected bbox: (10.0, 800 - 120, 50.0, 800 - 100) -> (10.0, 680.0, 50.0, 700.0)
        assert result[0][0]["bbox"] == (10.0, 680.0, 50.0, 700.0)

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    @patch("pymupdf.open")
    def test_extract_text_per_page_fallback(self, mock_pymupdf_open, mock_parser_cls):
        # Force docling parser to fail
        mock_parser = MagicMock()
        mock_parser.load.side_effect = Exception("Simulated Docling Crash")
        mock_parser_cls.return_value = mock_parser

        # Set up pymupdf mock
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = [(10.0, 100.0, 50.0, 120.0, "Hello", 0, 0, 0)]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf_open.return_value = mock_doc

        result = pdf.extract_text_per_page("dummy.pdf", max_pages=1)

        assert 0 in result
        assert result[0] == "Hello"

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=b"test")
    def test_extract_text_with_positions_invalid_pdf(self, mock_file, mock_exists, mock_parser_cls):
        with patch("pymupdf.open", side_effect=Exception("Simulated pymupdf fail")):
            result = pdf.extract_text_with_positions("dummy.pdf")
            assert result == {}

    @patch("liteparse.LiteParse")
    def test_extract_text_with_positions_liteparse_success(self, mock_liteparse):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.height = 1000

        mock_item_with_words = MagicMock()
        mock_word = MagicMock()
        mock_word.text = "Word1"
        mock_word.x = 10
        mock_word.y = 10
        mock_word.width = 50
        mock_word.height = 20
        mock_item_with_words.words = [mock_word]

        mock_item_no_words_single = MagicMock()
        mock_item_no_words_single.words = []
        mock_item_no_words_single.text = "Single"
        mock_item_no_words_single.x = 100
        mock_item_no_words_single.y = 100
        mock_item_no_words_single.width = 40
        mock_item_no_words_single.height = 20

        mock_item_no_words_multi = MagicMock()
        mock_item_no_words_multi.words = []
        mock_item_no_words_multi.text = "Multi Word Item"
        mock_item_no_words_multi.x = 200
        mock_item_no_words_multi.y = 200
        mock_item_no_words_multi.width = 120
        mock_item_no_words_multi.height = 20

        mock_page.text_items = [
            mock_item_with_words,
            mock_item_no_words_single,
            mock_item_no_words_multi,
        ]
        mock_doc.pages = [mock_page]

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_doc
        mock_liteparse.return_value = mock_parser

        with patch("os.path.exists", return_value=False):
            result = pdf.extract_text_with_positions("dummy.pdf")
            assert 0 in result
            assert result[0][0]["text"] == "Word1"
            assert result[0][1]["text"] == "Single"
            assert result[0][2]["text"] == "Multi"

    @patch("academic_doc_generator.core.pdf.PdfReader")
    def test_extract_annotations_with_positions_disallowed_subtype(self, mock_reader_cls):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_annot = MagicMock()
        mock_annot.get_object.return_value = {
            "/Subtype": "/Link",
            "/Rect": [0, 0, 10, 10],
            "/Contents": "Ignore this link",
        }
        mock_page.__contains__.side_effect = lambda x: x == "/Annots"
        mock_page.__getitem__.side_effect = lambda x: [mock_annot] if x == "/Annots" else None
        mock_reader.pages = [mock_page]
        mock_reader_cls.return_value = mock_reader

        annots, stats = pdf.extract_annotations_with_positions("test.pdf")
        assert len(annots) == 0

    def test_get_words_for_annotation_on_page_no_hits(self):
        pages_words = {0: [{"text": "Hello", "bbox": (10, 10, 20, 20)}]}
        rect = (50, 50, 60, 60)
        idx, hits = pdf.get_words_for_annotation_on_page(pages_words, 0, rect)
        assert idx == 0
        assert hits == []

    def test_find_annotation_context_quadpoints_and_none(self):
        pages_words = {
            0: [
                {"text": "Target", "bbox": (10, 10, 20, 20)},
            ]
        }
        annotations = {
            0: [
                {
                    "comment": "Note1",
                    "rect": None,
                    "category": "llm",
                    "quadpoints": [10, 10, 20, 10, 10, 20, 20, 20],
                },
                {"comment": "Note2", "rect": None, "category": "llm", "quadpoints": None},
            ]
        }
        context = pdf.find_annotation_context(pages_words, annotations)
        assert len(context[1]) == 1
        assert context[1][0]["comment"] == "Note1"
        assert context[1][0]["highlighted"] == "Target"

    @patch("liteparse.LiteParse")
    def test_extract_text_per_page_liteparse_success(self, mock_liteparse):
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.text = "Hello LiteParse Page 1"
        mock_page2 = MagicMock()
        mock_page2.text = "Hello LiteParse Page 2"
        mock_doc.pages = [mock_page1, mock_page2]

        mock_parser = MagicMock()
        mock_parser.parse.return_value = mock_doc
        mock_liteparse.return_value = mock_parser

        with patch("os.path.exists", return_value=False):
            result = pdf.extract_text_per_page("dummy.pdf", max_pages=1)
            assert len(result) == 1
            assert result[0] == "Hello LiteParse Page 1"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", new_callable=mock_open, read_data=b"test"),
            patch("pymupdf.open", side_effect=Exception("Simulated pymupdf fail")),
        ):
            result = pdf.extract_text_per_page("dummy.pdf")
            assert result == {}

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    @patch("os.path.exists", return_value=False)
    def test_extract_text_per_page_all_fail(self, mock_exists, mock_parser_cls):
        mock_parser = MagicMock()
        mock_parser.load.side_effect = Exception("Simulated Docling Crash")
        mock_parser_cls.return_value = mock_parser

        with patch("pymupdf.open", side_effect=Exception("Simulated PyMuPDF Crash")):
            result = pdf.extract_text_per_page("dummy.pdf")
            assert result == {}

    @patch("academic_doc_generator.core.pdf.DoclingPdfParser")
    @patch("pymupdf.open")
    def test_extract_text_per_page_fallback_max_pages(self, mock_pymupdf_open, mock_parser_cls):
        mock_parser = MagicMock()
        mock_parser.load.side_effect = Exception("Simulated Docling Crash")
        mock_parser_cls.return_value = mock_parser

        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = [(10.0, 100.0, 50.0, 120.0, "Hello1", 0, 0, 0)]
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = [(10.0, 100.0, 50.0, 120.0, "Hello2", 0, 0, 0)]
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]
        mock_pymupdf_open.return_value = mock_doc

        result = pdf.extract_text_per_page("dummy.pdf", max_pages=1)

        assert len(result) == 1
        assert result[0] == "Hello1"


# --- Tests for exam_translator.translator ---


class TestExamTranslator:
    def test_mask_unmask_comments(self):
        text = "Line 1\n% Comment\nLine 2"
        masked, cmap = translator.mask_comments(text)
        assert "%%COMMENT_0%%" in masked
        assert cmap["%%COMMENT_0%%"] == "% Comment"

        unmasked = translator.unmask_comments(masked, cmap)
        assert unmasked == text

    def test_split_latex_exam_into_sections(self):
        latex = r"""
\documentclass{exam}
\begin{document}
\begin{questions}
\question Q1
\question Q2
\end{questions}
\end{document}
"""
        preamble, questions, postamble = translator.split_latex_exam_into_sections(latex)
        assert r"\begin{questions}" in preamble
        assert len(questions) == 2
        assert r"\end{questions}" in postamble
        assert questions[0] == r"\question Q1"

    def test_split_latex_exam_no_begin(self):
        with pytest.raises(ValueError, match="Keine \\\\begin{questions} Umgebung gefunden!"):
            translator.split_latex_exam_into_sections("no questions")

    def test_split_latex_exam_no_end(self):
        with pytest.raises(ValueError, match="Keine \\\\end{questions} Umgebung gefunden!"):
            translator.split_latex_exam_into_sections(r"\begin{questions}")

    def test_translate_question(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = r"\question Translated"
        result = translator.translate_question_to_english(r"\question Original", mock_llm_client)
        assert result == r"\question Translated"

    def test_translate_preamble(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Translated Preamble"
        result = translator.translate_preamble_to_english("Original Preamble", mock_llm_client)
        assert result == "Translated Preamble"

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=r"\begin{questions}\question Q1\end{questions}",
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_translate_latex_exam(self, mock_exists, mock_file, mock_llm_client, tmp_path):
        mock_llm_client.chat_completion.return_value = "Translated"
        # Use a real output path in tmp_path
        output_path = tmp_path / "output.tex"
        with patch(
            "academic_doc_generator.exam_translator.translator.split_latex_exam_into_sections"
        ) as mock_split:
            mock_split.return_value = (r"\begin{questions}", [r"\question Q1"], r"\end{questions}")
            result = translator.translate_latex_exam(
                "input.tex", mock_llm_client, output_path=output_path
            )
            assert str(output_path) == result

    @patch("academic_doc_generator.exam_translator.translator.LLMClient")
    def test_translate_latex_exam_file_not_found(self, mock_llm):
        with pytest.raises(FileNotFoundError):
            translator.translate_latex_exam("nonexistent.tex")

    def test_translate_question_verbose(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = r"\question Translated"
        result = translator.translate_question_to_english(
            r"\question Original", mock_llm_client, verbose=True
        )
        assert result == r"\question Translated"

    def test_translate_preamble_verbose(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Translated Preamble"
        result = translator.translate_preamble_to_english(
            "Original Preamble", mock_llm_client, verbose=True
        )
        assert result == "Translated Preamble"


# --- Tests for core.llm ---


class TestCoreLlm:
    def test_rewrite_comments(self, mock_llm_client):
        context = {
            1: [
                {"comment": "Why?", "highlighted": "text", "paragraph": "para", "category": "llm"},
                {
                    "comment": "Quelle?",
                    "highlighted": "text",
                    "paragraph": "para",
                    "category": "quelle",
                },
            ]
        }
        mock_llm_client.chat_completion.return_value = "Rewritten"
        result = llm.rewrite_comments(context, mock_llm_client)
        assert result[1][0]["rewritten"] == "Rewritten"
        assert len(result[1]) == 1

    def test_rewrite_comments_groq_free(self, mock_llm_client):
        context = {
            i: [{"comment": "Why?", "highlighted": "text", "paragraph": "para", "category": "llm"}]
            for i in range(1, 7)
        }
        mock_llm_client.chat_completion.return_value = "Rewritten"
        with patch("time.sleep") as mock_sleep:
            result = llm.rewrite_comments(context, mock_llm_client, groq_free=True)
            assert len(result) == 6
            assert mock_sleep.call_count > 0

    def test_determine_gender_from_name(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Frau"
        assert llm.determine_gender_from_name("Maria", mock_llm_client) == "Frau"

        mock_llm_client.chat_completion.return_value = "Unknown"
        assert llm.determine_gender_from_name("Maria", mock_llm_client) == "Herr/Frau"

    def test_detect_degree_from_filename(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Bachelor"
        assert llm.detect_degree_from_filename("Bachelor_Thesis.pdf", mock_llm_client) == "Bachelor"

        mock_llm_client.chat_completion.return_value = "Master"
        assert llm.detect_degree_from_filename("Master_Thesis.pdf", mock_llm_client) == "Master"

        mock_llm_client.chat_completion.return_value = "Something else"
        assert llm.detect_degree_from_filename("Thesis.pdf", mock_llm_client) is None

    def test_extract_document_metadata(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = json.dumps(
            {"author": "John Doe", "sid": "12345"}
        )
        pages_text = {0: "Sample Text"}
        result = llm.extract_document_metadata(pages_text, "English", mock_llm_client)
        assert result["author"] == "John Doe"
        assert result["id_number"] == "12345"

    def test_extract_document_metadata_json_error(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Not JSON"
        result = llm.extract_document_metadata({}, "English", mock_llm_client)
        assert result == {}

    def test_summarize_thesis(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "A summary"
        result = llm.summarize_thesis({0: "text"}, "English", mock_llm_client)
        assert "A summary" in result

    def test_rewrite_comments_in_pdf_verbose(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "Rewritten"
        mock_processor = MagicMock()
        mock_processor.extract_text_with_positions.return_value = {
            0: [{"text": "text", "bbox": (0, 0, 10, 10)}]
        }
        mock_processor.extract_annotations_with_positions.return_value = (
            {
                0: [
                    {
                        "comment": "Why?",
                        "rect": [0, 0, 10, 10],
                        "category": "llm",
                        "quadpoints": None,
                    }
                ]
            },
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_processor.find_annotation_context.return_value = {
            1: [{"comment": "Why?", "highlighted": "text", "paragraph": "para", "category": "llm"}]
        }

        result, stats = llm.rewrite_comments_in_pdf(
            "test.pdf", mock_llm_client, verbose=True, pdf_processor=mock_processor
        )
        assert result[1][0]["rewritten"] == "Rewritten"

    def test_get_summary_and_metadata_of_pdf_complex(self, mock_llm_client):
        mock_llm_client.chat_completion.side_effect = [
            json.dumps({"author": "John Doe"}),
            "Bachelor",  # For detect_degree_from_filename fallback
            "A summary",
        ]
        with patch("academic_doc_generator.core.pdf.extract_text_per_page") as mock_extract:
            mock_extract.return_value = {0: "Text"}
            with patch("time.sleep") as mock_sleep:
                summary, metadata = llm.get_summary_and_metadata_of_pdf(
                    "test.pdf", "English", mock_llm_client, groq_free=True, verbose=True
                )
                assert metadata["author"] == "John Doe"
                assert "A summary" in summary
                assert mock_sleep.called

    def test_detect_language(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "German"
        comments = {1: [{"rewritten": "Was ist das?"}]}
        assert llm.detect_language(comments, mock_llm_client, groq_free=False) == "German"

    def test_detect_language_sample_size(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "English"
        comments = {
            1: [{"rewritten": "One"}, {"rewritten": "Two"}],
            2: [{"rewritten": "Three"}, {"rewritten": "Four"}],
        }
        # Should stop after 3 comments
        assert (
            llm.detect_language(comments, mock_llm_client, groq_free=False, sample_size=3)
            == "English"
        )

    def test_rewrite_comments_verbose(self, mock_llm_client):
        context = {
            1: [{"comment": "Why?", "highlighted": "text", "paragraph": "para", "category": "llm"}]
        }
        mock_llm_client.chat_completion.return_value = "Rewritten"
        result = llm.rewrite_comments(context, mock_llm_client, verbose=True)
        assert result[1][0]["rewritten"] == "Rewritten"

    def test_extract_document_metadata_filename_fallback_fails(self, mock_llm_client):
        mock_llm_client.chat_completion.side_effect = [
            json.dumps({"author": "John Doe"}),
            "Something else",
        ]
        pages_text = {0: "Sample Text"}
        result = llm.extract_document_metadata(
            pages_text, "English", mock_llm_client, pdf_path="Thesis.pdf"
        )
        assert result["author"] == "John Doe"
        assert "bachelor_master" not in result

    def test_detect_language_groq_free(self, mock_llm_client):
        mock_llm_client.chat_completion.return_value = "German"
        comments = {1: [{"rewritten": "Was ist das?"}]}
        with patch("time.sleep") as mock_sleep:
            res = llm.detect_language(comments, mock_llm_client, groq_free=True)
            assert res == "German"
            mock_sleep.assert_called_once_with(2)

    @patch("academic_doc_generator.core.llm.LLMClient")
    def test_rewrite_comments_in_pdf_no_client(self, mock_llm_cls):
        mock_client = MagicMock()
        mock_llm_cls.return_value = mock_client
        mock_processor = MagicMock()
        mock_processor.extract_text_with_positions.return_value = {}
        mock_processor.extract_annotations_with_positions.return_value = (
            {},
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_processor.find_annotation_context.return_value = {}

        result, stats = llm.rewrite_comments_in_pdf(
            "test.pdf", llm_client=None, pdf_processor=mock_processor
        )
        assert result == {}
        mock_llm_cls.assert_called_once()

    @patch("academic_doc_generator.core.llm.LLMClient")
    @patch("academic_doc_generator.core.pdf.extract_text_with_positions")
    @patch("academic_doc_generator.core.pdf.extract_annotations_with_positions")
    @patch("academic_doc_generator.core.pdf.find_annotation_context")
    def test_rewrite_comments_in_pdf_no_processor(
        self, mock_find, mock_extract_ann, mock_extract_text, mock_llm_cls
    ):
        mock_client = MagicMock()
        mock_llm_cls.return_value = mock_client
        mock_extract_text.return_value = {}
        mock_extract_ann.return_value = ({}, {"quelle": 0, "language": 0, "ignore": 0})
        mock_find.return_value = {}

        result, stats = llm.rewrite_comments_in_pdf(
            "test.pdf", llm_client=mock_client, pdf_processor=None
        )
        assert result == {}

    @patch("academic_doc_generator.core.llm.LLMClient")
    @patch("academic_doc_generator.core.pdf.extract_text_per_page")
    @patch("academic_doc_generator.core.llm.extract_document_metadata")
    @patch("academic_doc_generator.core.llm.summarize_thesis")
    def test_get_summary_and_metadata_of_pdf_no_client(
        self, mock_summarize, mock_extract, mock_pdf_extract, mock_llm_cls
    ):
        mock_client = MagicMock()
        mock_llm_cls.return_value = mock_client
        mock_pdf_extract.return_value = {0: "text"}
        mock_extract.return_value = {"author": "Jane Doe"}
        mock_summarize.return_value = "Summary text"

        summary, metadata = llm.get_summary_and_metadata_of_pdf(
            "test.pdf", "German", llm_client=None
        )
        assert summary == "Summary text"
        assert metadata["author"] == "Jane Doe"
        mock_llm_cls.assert_called_once()


# --- Tests for colloquium.orchestrator ---


class TestColloquiumOrchestrator:
    @patch("academic_doc_generator.core.pdf.extract_text_per_page")
    @patch("academic_doc_generator.core.llm.rewrite_comments_in_pdf")
    @patch("academic_doc_generator.core.llm.detect_language")
    @patch("academic_doc_generator.core.llm.get_summary_and_metadata_of_pdf")
    @patch("academic_doc_generator.core.latex.create_formal_letter_tex")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.fill_form")
    @patch(
        "academic_doc_generator.colloquium.email_generator.EmailGenerator.generate_colloquium_email"
    )
    @patch(
        "academic_doc_generator.colloquium.email_generator.EmailGenerator.save_email_to_markdown"
    )
    @patch("academic_doc_generator.colloquium.calendar_generator.CalendarGenerator.generate_ics")
    @patch(
        "academic_doc_generator.colloquium.outlook_mail_generator.OutlookMailGenerator.create_outlook_mail"
    )
    @patch("academic_doc_generator.core.metadata.generate_metadata_file")
    def test_run_pipeline(
        self,
        mock_gen_metadata,
        mock_outlook,
        mock_ics,
        mock_save_email,
        mock_gen_email,
        mock_fill_form,
        mock_latex,
        mock_llm_summary,
        mock_detect_lang,
        mock_rewrite,
        mock_extract_text,
        mock_llm_client,
        tmp_path,
    ):
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="campus",
            room="1.101",
            llm_client=mock_llm_client,
            gemini_emark_enabled=True,
            output_folder=tmp_path,
        )

        mock_rewrite.return_value = (
            {},
            {"quelle": 5, "language": 6, "ignore": 0},
        )  # Trigger stats-based mods
        mock_detect_lang.return_value = "German"
        mock_llm_summary.return_value = ("Summary", {"author": "Me", "id_number": "1"})
        mock_extract_text.return_value = {0: "Text"}

        with patch(
            "academic_doc_generator.colloquium.orchestrator.GeminiThesisEvaluator"
        ) as mock_eval_cls:
            mock_eval = MagicMock()
            mock_eval.evaluate_thesis.return_value = "Gemini Grade"
            mock_eval.format_emark_for_latex.return_value = "Formatted Gemini"
            mock_eval_cls.return_value = mock_eval

            result = orchestrator.run_pipeline(config)
            assert result.tex_path is not None
            assert mock_rewrite.called
            assert mock_fill_form.called

    def test_get_gemini_emark_failure(self, mock_llm_client):
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="campus",
            room="1.101",
            llm_client=mock_llm_client,
            gemini_emark_enabled=True,
        )
        with patch(
            "academic_doc_generator.colloquium.orchestrator.GeminiThesisEvaluator"
        ) as mock_eval_cls:
            mock_eval = MagicMock()
            mock_eval.evaluate_thesis.return_value = None  # Failure
            mock_eval_cls.return_value = mock_eval

            result = orchestrator._get_gemini_emark(config, {"title": "Test"})
            assert result is None

    def test_get_gemini_emark_exception(self, mock_llm_client):
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="campus",
            room="1.101",
            llm_client=mock_llm_client,
            gemini_emark_enabled=True,
        )
        with patch("academic_doc_generator.colloquium.orchestrator.LLMClient") as mock_llm_cls:
            mock_llm_cls.side_effect = Exception("init error")
            result = orchestrator._get_gemini_emark(config, {"title": "Test"})
            assert result is None

    @patch("academic_doc_generator.colloquium.orchestrator.CalendarGenerator.generate_ics")
    @patch("academic_doc_generator.colloquium.orchestrator.email_generator.EmailGenerator")
    def test_generate_emails_and_calendar_error(
        self, mock_email_gen_cls, mock_ics, mock_llm_client
    ):
        mock_email_gen = MagicMock()
        mock_email_gen_cls.return_value = mock_email_gen
        mock_ics.side_effect = Exception("ICS Error")
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="campus",
            room="1.101",
        )
        result = orchestrator._generate_emails_and_calendar(config, {}, mock_llm_client, "out/")
        assert result[2] is None  # ics_path is None on error

    @patch("academic_doc_generator.colloquium.orchestrator.OutlookMailGenerator")
    def test_create_outlook_draft_error(self, mock_outlook_cls):
        mock_outlook = MagicMock()
        mock_outlook.create_outlook_mail.side_effect = Exception("Outlook Error")
        mock_outlook_cls.return_value = mock_outlook
        # Should catch exception and print error
        orchestrator._create_outlook_draft({}, "text", "ics", "email")

    @patch("academic_doc_generator.colloquium.orchestrator.generate_metadata_file")
    def test_generate_web_metadata_error(self, mock_gen, mock_llm_client):
        mock_gen.side_effect = Exception("Metadata Error")
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="campus",
            room="1.101",
        )
        result = orchestrator._generate_web_metadata(config, {}, {}, mock_llm_client, "out/")
        assert result == ""

    def test_run_pipeline_fill_form_only(self, mock_llm_client, tmp_path):
        config = ColloquiumWorkflowConfig(
            pdf_path=Path("test.pdf"),
            date="01.01.2024",
            time="10:00",
            location_type="online",
            zoom_link="https://zoom.us/j/123",
            llm_client=mock_llm_client,
            fill_form_only=True,
            output_folder=tmp_path,
        )
        with patch("academic_doc_generator.core.pdf.extract_text_per_page") as mock_extract:
            mock_extract.return_value = {0: "Text"}
            with patch(
                "academic_doc_generator.core.llm.get_summary_and_metadata_of_pdf"
            ) as mock_llm:
                mock_llm.return_value = ("Summary", {"author": "Me", "id_number": "1"})
                with patch("academic_doc_generator.colloquium.orchestrator._fill_grading_form"):
                    result = orchestrator.run_pipeline(config)
                    assert result.tex_path == ""


# --- Tests for colloquium.pdf_form_filler ---


class TestPdfFormFiller:
    @patch("pymupdf.open")
    def test_pdf_form_handler_details(self, mock_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()

        # Test different widget types
        mock_widget_text = MagicMock()
        mock_widget_text.field_name = "Text1"
        mock_widget_text.field_type = 7  # Text
        mock_widget_text.field_value = "Value"

        mock_widget_cb = MagicMock()
        mock_widget_cb.field_name = "CB1"
        mock_widget_cb.field_type = 2  # Checkbox
        mock_widget_cb.field_value = True

        mock_widget_other = MagicMock()
        mock_widget_other.field_name = "Other1"
        mock_widget_other.field_type = 3  # Radio
        mock_widget_other.field_value = "Option"

        mock_page.widgets.return_value = [mock_widget_text, mock_widget_cb, mock_widget_other]
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        assert handler.has_form_fields() is True
        fields = handler.list_form_fields()
        assert len(fields) == 3

        with patch("builtins.print") as mock_print:
            handler.print_form_fields()
            assert mock_print.called

    @patch("pymupdf.open")
    def test_pdf_form_handler_fill(self, mock_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()

        mock_widget_text = MagicMock()
        mock_widget_text.field_name = "Text1"
        mock_widget_text.field_type = 7

        mock_widget_cb = MagicMock()
        mock_widget_cb.field_name = "CB1"
        mock_widget_cb.field_type = 2

        mock_page.widgets.return_value = [mock_widget_text, mock_widget_cb]
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        handler.fill_form({"Text1": "Value", "CB1": True, "Missing": "X"}, "out.pdf")
        assert mock_widget_text.field_value == "Value"
        assert mock_widget_cb.field_value is True

        # Test flatten=True
        handler.fill_form({"Text1": "Value"}, "out.pdf", flatten=True)
        assert mock_doc.save.called

    def test_berechne_gesamtnote(self):
        assert pdf_form_filler.berechne_gesamtnote(1.0, 2.0) == 1.5
        assert pdf_form_filler.berechne_gesamtnote(1.3, 1.7) == 1.5

    def test_add_minutes(self):
        assert pdf_form_filler.add_minutes("10:00", 45) == "10:45"
        assert pdf_form_filler.add_minutes("23:30", 45) == "00:15"

    def test_generate_location_text(self):
        assert "Raum 1.101" in pdf_form_filler.generate_location_text("campus", room="1.101")
        assert "MyCompany" in pdf_form_filler.generate_location_text(
            "company", company_name="MyCompany"
        )
        assert "Zoom" in pdf_form_filler.generate_location_text("online")

        with pytest.raises(ValueError):
            pdf_form_filler.generate_location_text("campus")  # Missing room

    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("pathlib.Path.exists", return_value=True)
    def test_fill_form_util(self, mock_exists, mock_handler_cls):
        mock_handler = MagicMock()
        mock_handler_cls.return_value = mock_handler

        result = pdf_form_filler.fill_form(
            {"name_student": "Test", "Startzeit": "10:00"},
            "out/",
            "Bachelor",
            location_type="online",
        )
        assert result is not None
        assert mock_handler.fill_form.called

    def test_fill_form_util_unknown_degree(self):
        result = pdf_form_filler.fill_form({}, "out/", "Unknown")
        assert result is None


# --- Tests for cli.handlers ---


class TestCliHandlers:
    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.ColloquiumWorkflowConfig")
    @patch("academic_doc_generator.cli.handlers.run_pipeline")
    def test_run_colloquium_direct(self, mock_run, mock_config_cls, mock_llm_cls, mock_val):
        # Test basic handler call
        args = MagicMock()
        args.path = "test.pdf"
        mock_val.return_value = Path("test.pdf")
        args.api = "openai"
        args.model = "gpt-4"
        args.date = "01.01.2024"
        args.time = "10:00"
        args.location = "campus"
        args.room = "1.101"
        args.company_name = "Company"
        args.company_address = "Address"
        args.zoom_link = "http://zoom"
        args.zcode = "123"
        args.groq_free = False
        args.compile_pdf = True
        args.fill_form_only = False
        args.gemini_emark = False
        args.gemini_model = "model"
        args.output = "output_dir"

        handlers.run_colloquium_direct(args)
        assert mock_run.called

    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.run_project_pipeline")
    def test_run_project_direct(self, mock_run, mock_llm_cls, mock_val):
        args = MagicMock()
        args.path = "test.pdf"
        mock_val.return_value = Path("test.pdf")
        args.api = "openai"
        args.model = "gpt-4"
        args.output = None
        handlers.run_project_direct(args)
        assert mock_run.called

    @patch("academic_doc_generator.cli.handlers.validate_pdf_path")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    @patch("academic_doc_generator.cli.handlers.run_review_pipeline")
    def test_run_review_direct(self, mock_run, mock_llm_cls, mock_val):
        args = MagicMock()
        args.path = "test.pdf"
        mock_val.return_value = Path("test.pdf")
        args.api = "openai"
        args.model = "gpt-4"
        handlers.run_review_direct(args)
        assert mock_run.called

    def test_run_from_config_not_found(self):
        with pytest.raises(SystemExit):
            handlers.run_from_config("nonexistent.yaml")

    @patch("academic_doc_generator.cli.handlers.LLMClient")
    def test_run_colloquium_direct_error(self, mock_llm_cls):
        mock_llm_cls.side_effect = Exception("LLM Error")
        args = MagicMock()
        args.api = "openai"
        with pytest.raises(SystemExit):
            handlers.run_colloquium_direct(args)

    @patch("academic_doc_generator.project.llm.extract_text_per_page")
    def test_project_llm_extract_metadata_json_error(self, mock_extract, mock_llm_client):
        from academic_doc_generator.project import llm as project_llm

        mock_extract.return_value = {0: "text"}
        mock_llm_client.chat_completion.return_value = "invalid json"
        result = project_llm.extract_project_metadata("test.pdf", mock_llm_client)
        assert "error" in result


class TestOutlookMailGenerator:
    @patch("platform.system")
    def test_is_outlook_open_linux(self, mock_system):
        from academic_doc_generator.colloquium.outlook_mail_generator import OutlookMailGenerator

        mock_system.return_value = "Linux"
        assert OutlookMailGenerator.is_outlook_open() is False

    @patch("platform.system")
    @patch("subprocess.check_output")
    def test_is_outlook_open_windows(self, mock_check, mock_system):
        from academic_doc_generator.colloquium.outlook_mail_generator import OutlookMailGenerator

        mock_system.return_value = "Windows"
        mock_check.return_value = b"OUTLOOK.EXE"
        assert OutlookMailGenerator.is_outlook_open() is True

        mock_check.side_effect = Exception("error")
        assert OutlookMailGenerator.is_outlook_open() is False

    @patch("platform.system")
    @patch("subprocess.check_call")
    def test_is_outlook_open_macos(self, mock_check, mock_system):
        from academic_doc_generator.colloquium.outlook_mail_generator import OutlookMailGenerator

        mock_system.return_value = "Darwin"
        mock_check.return_value = 0
        assert OutlookMailGenerator.is_outlook_open() is True

        from subprocess import CalledProcessError

        mock_check.side_effect = CalledProcessError(1, "pgrep")
        assert OutlookMailGenerator.is_outlook_open() is False

    @patch("subprocess.run")
    def test_create_outlook_mail_linux(self, mock_run):
        from academic_doc_generator.colloquium.outlook_mail_generator import OutlookMailGenerator

        with patch("platform.system", return_value="Linux"):
            gen = OutlookMailGenerator()
            assert gen.create_outlook_mail("Student", "Body", verbose=True) is True
            assert mock_run.called
