"""Unit tests for src/academic_doc_generator/core/utils.py"""

from academic_doc_generator.core.utils import clean_json_response, split_student_name


def test_clean_json_response_plain():
    content = '{"author": "Max Mustermann", "id_number": "123456"}'
    assert clean_json_response(content) == content


def test_clean_json_response_markdown_json_block():
    content = '```json\n{"author": "Max Mustermann", "id_number": "123456"}\n```'
    expected = '{"author": "Max Mustermann", "id_number": "123456"}'
    assert clean_json_response(content) == expected


def test_clean_json_response_markdown_block_no_lang():
    content = '```\n{"author": "Max Mustermann"}\n```'
    expected = '{"author": "Max Mustermann"}'
    assert clean_json_response(content) == expected


def test_clean_json_response_surrounding_text():
    content = 'Hier ist das Ergebnis:\n{"author": "Max Mustermann"}\nViel Erfolg!'
    expected = '{"author": "Max Mustermann"}'
    assert clean_json_response(content) == expected


def test_clean_json_response_empty():
    assert clean_json_response("") == ""
    assert clean_json_response(None) == ""


def test_split_student_name_simple():
    assert split_student_name("Max Mustermann") == ("Max", "Mustermann")


def test_split_student_name_comma():
    assert split_student_name("Mustermann, Max") == ("Max", "Mustermann")


def test_split_student_name_multiple_first():
    assert split_student_name("Hans Georg Mustermann") == ("Hans Georg", "Mustermann")


def test_split_student_name_none():
    assert split_student_name(None) == ("Student", "Name")


def test_split_student_name_empty():
    assert split_student_name("") == ("Student", "Name")


def test_split_student_name_single():
    assert split_student_name("Max") == ("Max", "Name")
