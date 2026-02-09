from pathlib import Path
from unittest.mock import MagicMock, patch

from academic_doc_generator import cli
from academic_doc_generator.cli import handlers


def test_cli_exports_run_from_config():
    assert hasattr(cli, "run_from_config")
    assert cli.run_from_config is handlers.run_from_config


@patch("academic_doc_generator.cli.handlers.load_config")
@patch("academic_doc_generator.cli.handlers.LLMClient")
@patch("academic_doc_generator.cli.handlers.validate_pdf_path")
@patch("academic_doc_generator.cli.handlers.run_review_pipeline")
def test_run_from_config_returns_config(
    mock_run_review, mock_validate_pdf, mock_llm_class, mock_load_config
):
    mock_config = MagicMock()
    mock_config.get_llm_config.return_value = {}
    mock_config.get_task.return_value = "review"
    mock_config.get_output_config.return_value = {}
    mock_config.config = {"pdf": {"filename": "test.pdf"}}
    mock_load_config.return_value = mock_config

    mock_llm_class.return_value = MagicMock()
    mock_validate_pdf.return_value = Path("/test/test.pdf")
    mock_run_review.return_value = "/output/review.md"

    result = handlers.run_from_config("/test/config.json")

    assert result is mock_config
