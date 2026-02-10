# src/academic_doc_generator/exam_translator/__init__.py
"""Exam Translator package for converting LaTeX exam documents from German to English."""

from .translator import (
    split_latex_exam_into_sections,
    translate_latex_exam,
    translate_preamble_to_english,
    translate_question_to_english,
)

__all__ = [
    "translate_latex_exam",
    "split_latex_exam_into_sections",
    "translate_question_to_english",
    "translate_preamble_to_english",
]
