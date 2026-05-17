# Testing Guide

This document describes how to run tests for the Academic Document Generator project.

## Installation

First, install the development dependencies:

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
pytest --cov=academic_doc_generator
```

### Run specific test file

```bash
pytest tests/test_colloquium_creator.py
```

### Run with verbose output

```bash
pytest -v
```

## Test Structure

The test suite is organized in the `tests/` directory:

- `test_colloquium_creator.py`: Tests for PDF parsing, annotation extraction, and LaTeX generation for colloquiums.  
- `test_project_creator.py`: Tests for metadata extraction and gender detection in project work.  
- `test_review_creator.py`: Tests for line number detection and Markdown generation for peer reviews.  
- `test_pipelines.py`: Integration tests for the high-level orchestrators.  
- `test_outlook_mail_generator.py`: Platform-independent tests for email generation (using mocking for Windows/macOS specific COM/AppleScript calls).  
- `test_utils.py`: Unit tests for helper functions like name splitting.  

## Key Features Tested

### 1. Comment Categorization
Verified categories: `llm`, `quelle`, `language`, `ignore`.

### 2. Metadata Extraction
Testing LLM-based extraction of author, matriculation number, title, and course of study from various PDF formats.

### 3. Integration Pipelines
Mocked end-to-end tests for `colloquium`, `project`, and `review` tasks.

## Mocking External Dependencies

### LLM APIs
We use `llm_client` mocks to avoid actual API calls and costs during testing.

### Platform-Specific Modules
For `win32com` (Outlook on Windows), we use `sys.modules` patching in `conftest.py` or within tests to allow the test suite to run on Linux CI environments:

```python
with patch.dict("sys.modules", {"win32com.client": MagicMock()}):
    # Test Windows-specific logic
```

## Continuous Integration

Tests are automatically run on GitHub Actions for every push and pull request.

```bash
# Example CI command
pytest --cov=academic_doc_generator --cov-report=xml
```

## Troubleshooting

### Tests fail with `ModuleNotFoundError`
Ensure the package is installed in editable mode: `pip install -e .`

### Platform-specific failures
If tests related to Outlook fail on Linux, check the mocking of `win32com` and `subprocess` calls for AppleScript.
