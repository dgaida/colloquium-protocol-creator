import os
import subprocess
from unittest.mock import patch, MagicMock
from academic_doc_generator.core.latex_generation import compile_latex_to_pdf


def test_compile_latex_to_pdf_success():
    """Test successful LaTeX compilation."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        pdf_path = compile_latex_to_pdf("test.tex", output_dir="out")

        assert pdf_path == os.path.join("out", "test.pdf")
        mock_run.assert_called_once()


def test_compile_latex_to_pdf_failure():
    """Test LaTeX compilation failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["lualatex"])

        # This should no longer raise an exception
        pdf_path = compile_latex_to_pdf("test.tex", output_dir="out")

        assert pdf_path == ""
        mock_run.assert_called_once()


def test_compile_latex_to_pdf_not_found():
    """Test when LaTeX engine is not found."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()

        # This should no longer raise an exception
        pdf_path = compile_latex_to_pdf("test.tex", output_dir="out")

        assert pdf_path == ""
        mock_run.assert_called_once()
