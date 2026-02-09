import time

import pytest

from academic_doc_generator.core.latex import (
    escape_latex_text,
    escape_latex_with_commands,
)


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("100% done", r"100\% done"),
        ("A & B", r"A \& B"),
        ("$5", r"\$5"),
        ("file_name", r"file\_name"),
        ("Straße", r"Stra{\ss}e"),
        ("test–dash—test", "test-dash-test"),  # En-dash and em-dash
        ("Braces {test}", r"Braces \{test\}"),
        ("Backslash \\ test", r"Backslash \textbackslash{} test"),
        ("", ""),
        (None, ""),
    ],
)
def test_escape_latex_text(input_text, expected):
    assert escape_latex_text(input_text) == expected


@pytest.mark.parametrize(
    "input_text,expected",
    [
        (
            r"Some \textbf{bold} and \emph{italic}",
            r"Some \textbf{bold} and \emph{italic}",
        ),
        ("100% done", r"100\% done"),
        ("A & B", r"A \& B"),
        ("Straße", r"Stra{\ss}e"),
        ("test–dash—test", "test{-}dash{-}test"),
        ("", ""),
        (None, ""),
    ],
)
def test_escape_latex_with_commands(input_text, expected):
    assert escape_latex_with_commands(input_text) == expected


def test_cache_performance():
    """Verify caching works for repeated strings."""
    text = "Repeat this very long string many times" * 100

    # First call
    start = time.perf_counter()
    escape_latex_text(text)
    first_duration = time.perf_counter() - start

    # Second call (should be cached)
    start = time.perf_counter()
    escape_latex_text(text)
    cached_duration = time.perf_counter() - start

    # The cached call should be significantly faster
    # We use a conservative check here
    assert cached_duration < first_duration
