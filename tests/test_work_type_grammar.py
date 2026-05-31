import pytest
from academic_doc_generator.core.utils import get_german_possessive_pronoun, get_german_dative_your

def test_possessive_pronoun_praxisprojekt():
    # Praxisprojekt is neuter -> sein/ihr/ihr
    assert get_german_possessive_pronoun("Praxisprojekt", "Herr") == "sein"
    assert get_german_possessive_pronoun("Praxisprojekt", "Frau") == "ihr"
    assert get_german_possessive_pronoun("Praxisprojekt", "Herr", plural=True) == "ihr"

def test_possessive_pronoun_informatikprojekt():
    # Informatikprojekt is neuter -> sein/ihr/ihr
    assert get_german_possessive_pronoun("Informatikprojekt", "Herr") == "sein"
    assert get_german_possessive_pronoun("Informatikprojekt", "Frau") == "ihr"
    assert get_german_possessive_pronoun("Informatikprojekt", "Herr", plural=True) == "ihr"

def test_possessive_pronoun_projektarbeit():
    # Projektarbeit is feminine -> seine/ihre/ihre
    assert get_german_possessive_pronoun("Projektarbeit", "Herr") == "seine"
    assert get_german_possessive_pronoun("Projektarbeit", "Frau") == "ihre"
    assert get_german_possessive_pronoun("Projektarbeit", "Herr", plural=True) == "ihre"

def test_possessive_pronoun_wasp1():
    # Projektteil WASP1 contains "teil" -> masculine -> seinen/ihren/ihren
    assert get_german_possessive_pronoun("Projektteil WASP1", "Herr") == "seinen"
    assert get_german_possessive_pronoun("Projektteil WASP1", "Frau") == "ihren"
    assert get_german_possessive_pronoun("Projektteil WASP1", "Herr", plural=True) == "ihren"

def test_dative_your():
    # Dative "zu Ihrem/Ihrer"
    assert get_german_dative_your("Praxisprojekt") == "Ihrem"
    assert get_german_dative_your("Informatikprojekt") == "Ihrem"
    assert get_german_dative_your("Projektarbeit") == "Ihrer"
    assert get_german_dative_your("Bachelorthesis") == "Ihrer"
    assert get_german_dative_your("Projektteil WASP1") == "Ihrem"
