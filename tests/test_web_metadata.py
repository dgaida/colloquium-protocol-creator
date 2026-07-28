"""
Unit tests for src/academic_doc_generator/core/metadata.py
"""

import os
import tempfile
from unittest.mock import MagicMock

from academic_doc_generator.core import metadata


def test_get_initials():
    """Test generation of initials."""
    assert metadata.get_initials("Max Mustermann") == "M. M."
    assert metadata.get_initials("Max-Moritz Mustermann") == "M. M. M."
    assert metadata.get_initials("Max Moritz Mustermann") == "M. M. M."
    assert metadata.get_initials(None) == "U. A."
    assert metadata.get_initials("Unknown Author") == "U. A."


def test_get_author_slug():
    """Test generation of author slugs."""
    assert metadata.get_author_slug("Max Mustermann") == "mamu"
    assert metadata.get_author_slug("Max-Moritz Mustermann") == "mamu"
    assert metadata.get_author_slug("Mustermann") == "must"
    assert metadata.get_author_slug(None) == "unkn"


def test_generate_metadata_file():
    """Test generation of web metadata Markdown file."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "This is a test summary for the web."

    pages_text = {0: "Page 1 content", 1: "Page 2 content"}

    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Test Thesis",
            author="Max Mustermann",
            pages_text=pages_text,
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="Wintersemester 24/25",
            date_str="2025-01-20",
        )

        assert os.path.exists(md_path)
        assert md_path.endswith("2025_ws2425_ba_mamu.md")

        with open(md_path, encoding="utf-8") as f:
            content = f.read()

        assert 'title: "Test Thesis"' in content
        assert 'author: "M. M."' in content
        assert 'date: "2025-01-20"' in content
        assert "This is a test summary for the web." in content
        assert 'type: "Bachelorthesis"' in content
        assert 'semester: "Wintersemester 24/25"' in content


def test_generate_metadata_file_with_copy(mocker):
    """Test generation and copying of web metadata file."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary"

    # Mock load_global_config to return a destination folder
    with tempfile.TemporaryDirectory() as target_dir:
        mocker.patch(
            "academic_doc_generator.core.metadata.load_global_config",
            return_value={"web_metadata_folder": target_dir},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = metadata.generate_metadata_file(
                output_folder=tmpdir,
                title="Test",
                author="Max Mustermann",
                pages_text={0: "text"},
                llm_client=mock_client,
                work_type="Bachelorthesis",
                semester="WS 24/25",
                date_str="2025-01-20",
            )

            # Check original file
            assert os.path.exists(md_path)

            # Check copied file
            filename = os.path.basename(md_path)
            copied_path = os.path.join(target_dir, filename)
            assert os.path.exists(copied_path)


def test_generate_metadata_file_with_move(mocker):
    """Test generation and moving of web metadata file."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary"

    with tempfile.TemporaryDirectory() as target_dir, tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Test Move",
            author="Max Mustermann",
            pages_text={0: "text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="WS 24/25",
            date_str="2025-01-20",
            copy_to_web_folder=False,
            move_to_web_folder=True,
            web_metadata_folder=target_dir,
        )

        # Check that the file was moved to the target directory
        filename = os.path.basename(md_path)
        moved_path = os.path.join(target_dir, filename)
        assert md_path == moved_path
        assert os.path.exists(moved_path)

        # Check that the original file in tmpdir is gone
        original_path = os.path.join(tmpdir, filename)
        assert not os.path.exists(original_path)


def test_get_author_slug_empty_parts():
    """Test get_author_slug when split results in no parts."""
    assert metadata.get_author_slug("   ") == "unkn"


def test_generate_metadata_file_unknown_students():
    """Test unknown author with group project students."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary"
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Test",
            author="Unknown",
            pages_text={0: "text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="WS 24/25",
            students=[{"name": "Unknown Author"}, {"name": "Unbekannt"}],
            copy_to_web_folder=True,
        )
        assert os.path.exists(md_path)


def test_generate_metadata_file_unknown_author():
    """Test unknown author without group project students."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary"
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Test",
            author="Unknown",
            pages_text={0: "text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="WS 24/25",
            copy_to_web_folder=True,
        )
        assert os.path.exists(md_path)


def test_generate_metadata_file_group_project():
    """Test group project metadata generation."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "This work by Alice Smith and Bob Jones is great."
    students = [
        {"name": "Alice Smith"},
        {"name": "Bob Jones"},
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Group Thesis",
            author="Alice Smith",
            pages_text={0: "text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="Wintersemester 24/25",
            date_str="2025-01-20",
            students=students,
            copy_to_web_folder=False,
        )
        assert os.path.exists(md_path)
        assert md_path.endswith("2025_ws2425_ba_alsm_bojo.md")
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        assert 'author: "A. S. & B. J."' in content
        assert "This work by A. S. and B. J. is great." in content


def test_generate_metadata_file_copy_exception(mocker):
    """Test exception handling during file copying."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Summary"
    mocker.patch("shutil.copy2", side_effect=OSError("Simulated file error"))
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = metadata.generate_metadata_file(
            output_folder=tmpdir,
            title="Test Exception",
            author="Max Mustermann",
            pages_text={0: "text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="WS 24/25",
            web_metadata_folder="some_folder",
            copy_to_web_folder=True,
        )
        assert os.path.exists(md_path)
