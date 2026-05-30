"""Exam Translator package for converting LaTeX and XML exam documents from German to English."""

from .translator import (
    split_latex_exam_into_sections,
    translate_latex_exam,
    translate_preamble_to_english,
    translate_question_to_english,
)
from .xml_translator import translate_xml_exam

__all__ = [
    "translate_latex_exam",
    "translate_xml_exam",
    "split_latex_exam_into_sections",
    "translate_question_to_english",
    "translate_preamble_to_english",
]
