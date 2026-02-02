"""Unit tests for src/academic_doc_generator/core/utils.py"""

from academic_doc_generator.core.utils import split_student_name


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
