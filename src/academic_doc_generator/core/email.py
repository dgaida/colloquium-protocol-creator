"""Centralized email generation with templates."""

from dataclasses import dataclass
from typing import Protocol
from datetime import datetime


def weekday_from_string(date_str: str, lang: str = "de") -> str:
    """Get the weekday name from a date string (DD.MM.YYYY)."""
    date = datetime.strptime(date_str, "%d.%m.%Y")
    weekday_idx = date.weekday()  # Montag = 0

    weekdays = {
        "de": [
            "Montag",
            "Dienstag",
            "Mittwoch",
            "Donnerstag",
            "Freitag",
            "Samstag",
            "Sonntag",
        ],
        "en": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    }

    if lang not in weekdays:
        raise ValueError(f"Unsupported language: {lang}")

    return weekdays[lang][weekday_idx]


@dataclass
class EmailRecipient:
    """Represents an email recipient with formal German addressing."""
    first_name: str
    last_name: str
    gender: str  # "Herr", "Frau", or "Herr/Frau"
    identifier: str = ""  # Matriculation number or other ID

    @property
    def formal_salutation(self) -> str:
        """German formal greeting."""
        if self.gender == "Herr/Frau" or not self.gender:
            return "Guten Tag"
        return f"Guten Tag {self.gender} {self.last_name}"

    @property
    def full_name_with_title(self) -> str:
        """E.g., 'Herr Max Mustermann'"""
        if self.gender == "Herr/Frau" or not self.gender:
            return f"{self.first_name} {self.last_name}"
        return f"{self.gender} {self.first_name} {self.last_name}"

    @property
    def full_name_with_id(self) -> str:
        """E.g., 'Herr Max Mustermann (123456)'"""
        name = self.full_name_with_title
        if self.identifier:
            return f"{name} ({self.identifier})"
        return name

    @property
    def title_last_name(self) -> str:
        """E.g., 'Herr Mustermann'"""
        if self.gender == "Herr/Frau" or not self.gender:
            return self.last_name
        return f"{self.gender} {self.last_name}"


class EmailTemplate(Protocol):
    """Protocol for email templates."""
    def render(self, **kwargs) -> str:
        ...


class ColloquiumRegistrationEmail:
    """Template for colloquium registration emails."""

    def render(
        self,
        student: EmailRecipient,
        examiner: str,
        date: str,
        time: str,
        location_text: str,
    ) -> str:
        weekday = weekday_from_string(date)

        return f"""Lieber Prüfungsservice,
hiermit möchte ich {student.full_name_with_id} zum Kolloquium anmelden. Dieses findet statt am:
{weekday}, {date}, um {time},
{location_text}.
{student.title_last_name}: Bitte bereiten Sie eine max. 15-minütige Präsentation zu Ihrer Arbeit vor (wenn möglich inkl. Demo).
Viele Grüße,
{examiner.title()}"""


class FinalGradeEmail:
    """Template for submitting final grades to the examination service."""

    def render(
        self,
        student: EmailRecipient,
        examiner: str,
    ) -> str:
        return f"""Lieber Prüfungsservice,
hiermit möchte ich die Bewertung für {student.full_name_with_id} einreichen (s. Anhang).
Viele Grüße,
{examiner.title()}"""


class StudentFeedbackEmail:
    """Template for providing feedback directly to the student."""

    def render(
        self,
        student: EmailRecipient,
        grade: str,
        feedback_bulletpoints: str,
        examiner: str,
    ) -> str:
        return f"""{student.formal_salutation},

ich habe Ihre Arbeit mit einer {grade} bewertet. Hier ist mein Feedback zu Ihrer Arbeit:

{feedback_bulletpoints}

Viele Grüße,
{examiner.title()}"""
