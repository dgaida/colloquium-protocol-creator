# colloquium_pipeline/email_generator.py
"""Modul zur Generierung von Anmelde-E-Mails für Kolloquien."""

from typing import Optional
from pathlib import Path
from ..core.llm import determine_gender_from_name
from ..core.utils import split_student_name
from ..core.email import (
    EmailRecipient,
    ColloquiumRegistrationEmail,
    FinalGradeEmail,
    StudentFeedbackEmail,
    weekday_from_string
)


class EmailGenerator:
    def __init__(self):
        """ """
        self.email_path = None
        self.email_text = None

    def generate_and_save_email(
        self,
        llm_client,
        output_folder: str,
        author: str,
        matriculation: str,
        date_colloquium: str,
        uhrzeit_colloquium: str,
        first_examiner: str,
        location_type: str = "campus",
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        zoom_link: Optional[str] = None,
        zoom_meeting_access: Optional[str] = None,
    ) -> str:
        """Generiert und speichert die Kolloquiums-Anmelde-E-Mail.

        Args:
            llm_client: LLM-Client zur Geschlechtsbestimmung.
            output_folder: Zielordner.
            author: Name des Studierenden.
            matriculation: Matrikelnummer.
            date_colloquium: Datum des Kolloquiums.
            uhrzeit_colloquium: Uhrzeit des Kolloquiums.
            first_examiner: Erstprüfer.
            location_type: Art des Ortes.
            room: Raumnummer.
            company_name: Firmenname.
            company_address: Firmenadresse.
            zoom_link: Zoom-Link.
            zoom_meeting_access: Zoom-Code.

        Returns:
            Pfad zur gespeicherten E-Mail-Datei.
        """
        print("START WRITING MAIL")

        if author is None:
            print("Error: author is None")
            return ""

        student_first_name, student_last_name = split_student_name(author)

        self.generate_colloquium_email(
            llm_client=llm_client,
            student_first_name=student_first_name,
            student_last_name=student_last_name,
            matriculation_number=matriculation,
            date_colloquium=date_colloquium,
            time_colloquium=uhrzeit_colloquium,
            first_examiner=first_examiner,
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
            zoom_link=zoom_link,
            zoom_meeting_access=zoom_meeting_access,
        )

        return self.save_email_to_markdown(
            output_folder=output_folder,
            student_last_name=student_last_name,
            matriculation_number=matriculation,
        )

    def _generate_location_text(
        self,
        location_type: str,
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        zoom_link: Optional[str] = None,
        zoom_meeting_access: Optional[str] = None,
    ) -> str:
        """Generiert den Ortszusatz für die E-Mail.

        Args:
            location_type: Art des Kolloquiums ("campus", "company", "online").
            room: Raumnummer (nur für "campus").
            company_name: Name der Firma (nur für "company").
            company_address: Adresse der Firma (nur für "company").
            zoom_link: Zoom-Meeting-Link (nur für "online").
            zoom_meeting_access: Zoom-Zugangscode (nur für "online").

        Returns:
            email_location_text.

        Raises:
            ValueError: Wenn erforderliche Parameter fehlen.
        """
        if location_type == "campus":
            if not room:
                raise ValueError("Für Campus-Kolloquium wird 'room' benötigt")
            return f"in Raum {room} am Campus GM"

        elif location_type == "company":
            if not company_name:
                raise ValueError("Für Firmen-Kolloquium wird 'company_name' benötigt")

            if company_address:
                return f"in der Firma {company_name}, {company_address}"
            else:
                return f"in der Firma {company_name}"

        elif location_type == "online":
            if not zoom_link:
                raise ValueError("Für Online-Kolloquium wird 'zoom_link' benötigt")

            zoom_info = f"über Zoom:\n\nZoom-Link: {zoom_link}"
            if zoom_meeting_access:
                zoom_info += f"\nZugangscode: {zoom_meeting_access}"

            return zoom_info
        else:
            raise ValueError(f"Unbekannter location_type: {location_type}")

    def generate_colloquium_email(
        self,
        llm_client,
        student_first_name: str,
        student_last_name: str,
        matriculation_number: str,
        date_colloquium: str,
        time_colloquium: str,
        first_examiner: str,
        location_type: str,
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        zoom_link: Optional[str] = None,
        zoom_meeting_access: Optional[str] = None,
    ) -> str:
        """Generiert den Text für die Kolloquiums-Anmelde-E-Mail."""
        gender = determine_gender_from_name(student_first_name, llm_client)
        student = EmailRecipient(
            first_name=student_first_name,
            last_name=student_last_name,
            gender=gender,
            identifier=matriculation_number
        )

        location_text = self._generate_location_text(
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
            zoom_link=zoom_link,
            zoom_meeting_access=zoom_meeting_access,
        )

        template = ColloquiumRegistrationEmail()
        self.email_text = template.render(
            student=student,
            examiner=first_examiner,
            date=date_colloquium,
            time=time_colloquium,
            location_text=location_text
        )
        return self.email_text

    def generate_final_grade_email(
        self,
        evaluator_client,
        first_name: str,
        last_name: str,
        student_identifier: str,
        examiner_name: str,
    ) -> str:
        """Generiert den Text für die E-Mail zur Einreichung der Note."""
        gender = determine_gender_from_name(first_name, evaluator_client)
        student = EmailRecipient(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            identifier=student_identifier
        )

        template = FinalGradeEmail()
        self.email_text = template.render(
            student=student,
            examiner=examiner_name
        )
        return self.email_text

    def generate_student_feedback_email(
        self,
        gender: str,
        last_name: str,
        grade: str,
        feedback_bulletpoints: str,
        examiner_name: str,
    ) -> str:
        """Generiert eine Feedback-E-Mail an den Studierenden."""
        student = EmailRecipient(
            first_name="", # Not used in feedback salutation if we have last_name and gender
            last_name=last_name,
            gender=gender
        )

        template = StudentFeedbackEmail()
        self.email_text = template.render(
            student=student,
            grade=grade,
            feedback_bulletpoints=feedback_bulletpoints,
            examiner=examiner_name
        )
        return self.email_text

    def save_email_to_markdown(
        self,
        output_folder: str,
        student_last_name: str,
        matriculation_number: str,
        filename_prefix: str = "kolloquium_anmeldung",
    ) -> str:
        """Speichert den E-Mail-Text in einer Markdown-Datei."""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{filename_prefix}_{student_last_name}_{matriculation_number}.md"
        self.email_path = output_path / filename

        with open(self.email_path, "w", encoding="utf-8") as f:
            f.write(self.email_text)

        print(f"E-Mail-Text gespeichert: {self.email_path}")
        return str(self.email_path)
