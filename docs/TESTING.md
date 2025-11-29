# Testing Guide

This document describes how to run tests for the colloquium-protocol-creator project.

## Installation

First, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

Or if you're using the editable install:

```bash
pip install -e ".[dev]"
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with coverage report

```bash
pytest --cov=colloquium_creator --cov=colloquium_pipeline --cov=review_creator --cov=review_pipeline
```

### Run specific test file

```bash
pytest tests/test_colloquium_creator.py
```

### Run specific test class or function

```bash
pytest tests/test_colloquium_creator.py::TestPdfProcessing
pytest tests/test_colloquium_creator.py::TestPdfProcessing::test_is_quelle_comment_valid
```

### Run with verbose output

```bash
pytest -v
```

### Run tests matching a pattern

```bash
pytest -k "quelle"  # Runs all tests with "quelle" in the name
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── test_colloquium_creator.py  # Main test file
└── ...
```

### Test Categories

- **TestPdfProcessing**: Tests for PDF parsing and annotation extraction
  - Quelle comment detection
  - Word-rectangle overlap
  - Annotation context finding

- **TestLLMInterface**: Tests for LLM interaction
  - Comment rewriting
  - Category handling (ignore, quelle, language, llm)
  - Language detection

- **TestLatexGeneration**: Tests for LaTeX generation
  - Special character escaping
  - Letter template creation
  - Comment concatenation

- **TestUtils**: Tests for utility functions
  - File finding

- **TestIntegration**: Integration tests for complete workflows

## Key Features Tested

### 1. Comment Categorization

The system categorizes comments into four types:

- **`llm`**: Regular comments that should be rewritten by the LLM
- **`quelle`**: Source-related comments (e.g., "Quelle?", "Source missing") - counted but not rewritten
- **`language`**: Language/grammar comments - counted but not rewritten
- **`ignore`**: "ab hier" comments - completely ignored

### 2. Quelle Detection

Comments are identified as "Quelle" comments if they:
- Are 20 characters or less (configurable)
- Contain the word "quelle" or "source" (case-insensitive, whole word)

Examples:
- ✅ "Quelle?"
- ✅ "Quelle fehlt"
- ✅ "source"
- ❌ "Quelle fehlt hier an dieser Stelle komplett" (too long)
- ❌ "Consequent" (not a whole word match)

### 3. Comment Processing Flow

1. PDF annotations are extracted with categories
2. Categories are counted in stats: `{"quelle": X, "language": Y, "ignore": Z}`
3. Comments are processed:
   - `ignore`: Excluded entirely
   - `quelle` and `language`: Kept with `rewritten=None`
   - `llm`: Sent to LLM for rewriting

## Writing New Tests

When adding new functionality, please add corresponding tests:

```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Mocking External Dependencies

For tests that would normally call external APIs (like Groq), use mocking:

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_api():
    with patch("module.ExternalAPI") as mock_api:
        mock_client = MagicMock()
        mock_api.return_value = mock_client
        
        # Your test code
        result = function_that_calls_api()
        
        # Verify
        mock_client.method.assert_called_once()
```

## Continuous Integration

Tests should pass before merging any pull request. Set up CI to run:

```bash
pytest --cov=colloquium_creator --cov-report=term-missing
```

## Troubleshooting

### Tests fail with import errors

Make sure the package is installed:
```bash
pip install -e .
```

### Tests fail with missing dependencies

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

### Mock tests fail

Ensure you're patching the correct module path where the function is used, not where it's defined.
