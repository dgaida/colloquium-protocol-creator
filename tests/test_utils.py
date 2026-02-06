"""Unit tests for src/academic_doc_generator/core/utils.py"""

from academic_doc_generator.core.utils import split_stud_name


def test_split_stud_name_simple():
    assert split_stud_name("Max Mustermann") == ("Max", "Mustermann")


def test_split_stud_name_comma():
    assert split_stud_name("Mustermann, Max") == ("Max", "Mustermann")


def test_split_stud_name_multiple_first():
    assert split_stud_name("Hans Georg Mustermann") == ("Hans Georg", "Mustermann")


def test_split_stud_name_none():
    assert split_stud_name(None) == ("Student", "Name")


def test_split_stud_name_empty():
    assert split_stud_name("") == ("Student", "Name")


def test_split_stud_name_single():
    assert split_stud_name("Max") == ("Max", "Name")
