"""End-to-end integration tests for colloquium workflow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.colloquium.orchestrator import run_pipeline
from academic_doc_generator.core.types import ColloquiumWorkflowConfig


@pytest.fixture
def mock_llm_client():
    """Create a mocked LLM client."""
    client = MagicMock()
    client.api_choice = "mock"
    client.llm = "mock-model"
    return client


@pytest.mark.integration
def test_colloquium_workflow_mocked_llm(mock_llm_client):
    """Test complete colloquium workflow with mocked LLM calls and PDF processing."""

    # We need to mock the PDF processing and LLM parts that would actually
    # hit an API or require a real complex PDF file.
    with (
        patch("academic_doc_generator.core.pdf.extract_text_with_positions") as mock_extract_text,
        patch(
            "academic_doc_generator.core.pdf.extract_annotations_with_positions"
        ) as mock_extract_annots,
        patch("academic_doc_generator.core.pdf.find_annotation_context") as mock_find_context,
        patch("academic_doc_generator.core.pdf.extract_text_per_page") as mock_extract_per_page,
        patch("academic_doc_generator.core.latex.compile_latex_to_pdf") as mock_compile,
        patch("academic_doc_generator.colloquium.pdf_form_filler.fill_form") as mock_fill_form,
        patch("academic_doc_generator.colloquium.orchestrator.OutlookMailGenerator"),
        tempfile.TemporaryDirectory() as tmpdir,
    ):

        # Setup mocks
        mock_extract_text.return_value = {0: []}
        mock_extract_annots.return_value = (
            {0: []},
            {"quelle": 0, "language": 0, "ignore": 0},
        )
        mock_find_context.return_value = {
            1: [
                {
                    "comment": "Good",
                    "highlighted": "text",
                    "paragraph": "para",
                    "category": "llm",
                }
            ]
        }
        mock_extract_per_page.return_value = {0: "Page 1", 1: "Page 2"}
        mock_compile.return_value = str(Path(tmpdir) / "output.pdf")

        # Mock LLM responses
        # 1. Comment rewriting
        # 2. Language detection
        # 3. Metadata extraction (JSON)
        # 4. Summarization
        # 5. Gender detection (for email)
        # 6. Final mark email gender detection
        # 7. Summarize for web
        mock_llm_client.chat_completion.side_effect = [
            "Rewritten Comment?",  # REWRITE_COMMENT
            "German",  # DETECT_LANGUAGE
            '{"author": "Max Mustermann", "sid": "123456", "title": "Thesis Title", "first_examiner": "Prof. Dr. Müller", "first_examiner_christian": "Max", "first_examiner_family": "Müller", "second_examiner": "Prof. Schmidt", "bachelor_master": "Bachelor", "course_of_study": "Informatik"}',  # EXTRACT_METADATA
            "Concise thesis summary.",  # SUMMARIZE_THESIS
            "Herr",  # DETERMINE_GENDER (for registration email)
            "Herr",  # DETERMINE_GENDER (for final mark email)
            "Web summary.",  # SUMMARIZE_FOR_WEB
        ]

        config = ColloquiumWorkflowConfig(
            pdf_path=Path("dummy.pdf"),
            date="15.01.2026",
            time="10:00",
            llm_client=mock_llm_client,
            output_folder=Path(tmpdir),
            compile_pdf=True,
            location_type="campus",
            room="3.217",
        )

        result = run_pipeline(config)

        # Verify outputs exist
        assert Path(result.tex_path).exists()
        assert result.pdf_path.endswith("output.pdf")
        assert Path(result.email_path).exists()
        assert Path(result.metadata_path).exists()

        # Verify LaTeX content
        with open(result.tex_path, encoding="utf-8") as f:
            content = f.read()
            assert r"\documentclass" in content
            assert "Max Mustermann" in content
            assert "Thesis Title" in content
            assert "Rewritten Comment?" in content

        # Verify Email content
        with open(result.email_path, encoding="utf-8") as f:
            email_content = f.read()
            assert "Lieber Prüfungsservice" in email_content
            assert "Max Mustermann" in email_content
            # 15.01.2026 is a Thursday
            assert "Donnerstag, 15.01.2026" in email_content
            assert "Raum 3.217" in email_content

        # Verify metadata file
        with open(result.metadata_path, encoding="utf-8") as f:
            metadata_content = f.read()
            assert 'title: "Thesis Title"' in metadata_content
            assert 'author: "M. M."' in metadata_content

        # Verify form filler was called with correct data
        mock_fill_form.assert_called_once()
        daten = mock_fill_form.call_args[0][0]
        assert daten["name_student"] == "Max Mustermann"
        assert daten["MatrNr"] == "123456"
        assert daten["KontrollInformatik"] is True
