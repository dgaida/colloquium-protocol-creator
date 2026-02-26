"""Centralized email generation with templates."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


def weekday_from_string(date_str: str, lang: str = "de") -> str:
    """Get the weekday name from a date string (DD.MM.YYYY).

    Args:
        date_str: Date in format DD.MM.YYYY.
        lang: Language for the weekday name ("de" or "en"). Defaults to "de".

    Returns:
        Name of the weekday in the specified language.

    Raises:
        ValueError: If the date format is invalid or language is unsupported.
    """
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

    @staticmethod
    def format_recipients_salutation(recipients: list["EmailRecipient"]) -> str:
        """Format joint salutation for multiple recipients.

        Example: "Guten Tag Frau Musterfrau, guten Tag Herr Mustermann"
        """
        if not recipients:
            return "Guten Tag"
        if len(recipients) == 1:
            return recipients[0].formal_salutation

        parts = [r.formal_salutation for r in recipients]
        # Lowercase "guten Tag" for subsequent parts
        formatted_parts = [parts[0]]
        for p in parts[1:]:
            formatted_parts.append(p[0].lower() + p[1:])
        return ", ".join(formatted_parts)

    @staticmethod
    def format_recipients_full_names(recipients: list["EmailRecipient"]) -> str:
        """Format joint names for multiple recipients.

        Example: "Frau Maria Musterfrau (123456) und Herr Max Mustermann (654321)"
        """
        if not recipients:
            return "Unbekannt"
        if len(recipients) == 1:
            return recipients[0].full_name_with_id

        parts = [r.full_name_with_id for r in recipients]
        if len(parts) == 2:
            return " und ".join(parts)
        return ", ".join(parts[:-1]) + " und " + parts[-1]


class EmailTemplate(Protocol):
    """Protocol for email templates."""

    def render(self, **kwargs) -> str: ...


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
        """Render the registration email text.

        Args:
            student: The student being registered.
            examiner: Name of the first examiner.
            date: Date of the colloquium (DD.MM.YYYY).
            time: Time of the colloquium (HH:MM).
            location_text: Formatted location description.

        Returns:
            The rendered email body as a string.
        """
        weekday = weekday_from_string(date)

        examiner_str = examiner.title() if examiner else "Unbekannt"
        return f"""Lieber Prüfungsservice,
hiermit möchte ich {student.full_name_with_id} zum Kolloquium anmelden. Dieses findet statt am:
{weekday}, {date}, um {time},
{location_text}.
{student.title_last_name}: Bitte bereiten Sie eine max. 15-minütige Präsentation zu Ihrer Arbeit vor (wenn möglich inkl. Demo).
Viele Grüße,
{examiner_str}"""


class FinalGradeEmail:
    """Template for submitting final marks to the examination service."""

    def render(
        self,
        student: EmailRecipient,
        examiner: str,
        students: list[EmailRecipient] = None,
    ) -> str:
        examiner_str = examiner.title() if examiner else "Unbekannt"
        if students and len(students) > 1:
            names = EmailRecipient.format_recipients_full_names(students)
            plural_text = "die Bewertungen"
        else:
            names = student.full_name_with_id
            plural_text = "die Bewertung"

        return f"""Lieber Prüfungsservice,
hiermit möchte ich {plural_text} für {names} einreichen (s. Anhang).
Viele Grüße,
{examiner_str}"""


class StudentFeedbackEmail:
    """Template for providing feedback directly to the student."""

    def render(
        self,
        student: EmailRecipient,
        mark: str,
        feedback_bulletpoints: str,
        examiner: str,
        students: list[EmailRecipient] = None,
    ) -> str:
        examiner_str = examiner.title() if examiner else "Unbekannt"
        if students and len(students) > 1:
            salutation = EmailRecipient.format_recipients_salutation(students)
            arbeit_text = "Ihre gemeinsame Arbeit"
        else:
            salutation = student.formal_salutation
            arbeit_text = "Ihre Arbeit"

        return f"""{salutation},

ich habe {arbeit_text} mit einer {mark} bewertet. Hier ist mein Feedback zu Ihrer Arbeit:

{feedback_bulletpoints}

Viele Grüße,
{examiner_str}"""
