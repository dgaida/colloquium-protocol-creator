from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_llm_client():
    """Reusable LLM client mock."""
    client = MagicMock()
    client.api_choice = "mock"
    client.llm = "mock-model"
    return client


@pytest.fixture
def mock_pdf_processor():
    """Reusable PDF processor mock."""
    processor = MagicMock()
    processor.extract_text_with_positions.return_value = {}
    processor.extract_annotations_with_positions.return_value = (
        {},
        {"quelle": 0, "language": 0, "ignore": 0},
    )
    processor.find_annotation_context.return_value = {}
    return processor


@pytest.fixture
def sample_context():
    """Standard annotation context for testing."""
    return {
        1: [
            {
                "comment": "Test?",
                "highlighted": "text",
                "paragraph": "para",
                "category": "llm",
            }
        ]
    }
