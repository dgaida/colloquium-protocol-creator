# colloquium_pipeline/email_generator.py
"""Modul zur Generierung von Anmelde-E-Mails für Kolloquien."""

from pathlib import Path
from typing import Optional

from ..core.email import (
    ColloquiumRegistrationEmail,
    EmailRecipient,
    FinalGradeEmail,
    StudentFeedbackEmail,
)
from ..core.llm import determine_gender_from_name
from ..core.utils import split_stud_name


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
        zcode: Optional[str] = None,
    ) -> str:
        """Generiert und speichert die Kolloquiums-Anmelde-E-Mail."""
        print("START WRITING MAIL")

        if author is None:
            print("Error: author is None")
            return ""

        student_first_name, student_last_name = split_stud_name(author)

        self.generate_colloquium_email(
            llm_client=llm_client,
            student_first_name=student_first_name,
            student_last_name=student_last_name,
            sid=matriculation,
            date_colloquium=date_colloquium,
            time_colloquium=uhrzeit_colloquium,
            first_examiner=first_examiner,
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
            zoom_link=zoom_link,
            zcode=zcode,
        )

        return self.save_email_to_markdown(
            output_folder=output_folder,
            student_last_name=student_last_name,
            sid=matriculation,
        )

    def _generate_location_text(
        self,
        location_type: str,
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        zoom_link: Optional[str] = None,
        zcode: Optional[str] = None,
    ) -> str:
        """Generiert den Ortszusatz für die E-Mail."""
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
            if zcode:
                zoom_info += f"\nZugangscode: {zcode}"

            return zoom_info
        else:
            raise ValueError(f"Unbekannter location_type: {location_type}")

    def generate_colloquium_email(
        self,
        llm_client,
        student_first_name: str,
        student_last_name: str,
        sid: str,
        date_colloquium: str,
        time_colloquium: str,
        first_examiner: str,
        location_type: str,
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        zoom_link: Optional[str] = None,
        zcode: Optional[str] = None,
    ) -> str:
        """Generiert den Text für die Kolloquiums-Anmelde-E-Mail."""
        gender = determine_gender_from_name(student_first_name, llm_client)
        student = EmailRecipient(
            first_name=student_first_name,
            last_name=student_last_name,
            gender=gender,
            identifier=sid,
        )

        location_text = self._generate_location_text(
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
            zoom_link=zoom_link,
            zcode=zcode,
        )

        template = ColloquiumRegistrationEmail()
        self.email_text = template.render(
            student=student,
            examiner=first_examiner,
            date=date_colloquium,
            time=time_colloquium,
            location_text=location_text,
        )
        return self.email_text

    def generate_final_mark_email(
        self,
        evaluator_client,
        first_name: str,
        last_name: str,
        sid: str,
        examiner_name: str,
    ) -> str:
        """Generiert den Text für die E-Mail zur Einreichung der Note."""
        gender = determine_gender_from_name(first_name, evaluator_client)
        student = EmailRecipient(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            identifier=sid,
        )

        template = FinalGradeEmail()
        self.email_text = template.render(student=student, examiner=examiner_name)
        return self.email_text

    def generate_student_feedback_email(
        self,
        gender: str,
        last_name: str,
        mark: str,
        feedback_bulletpoints: str,
        examiner_name: str,
    ) -> str:
        """Generiert eine Feedback-E-Mail an den Studierenden."""
        student = EmailRecipient(
            first_name="",  # Not used in feedback salutation if we have last_name and gender
            last_name=last_name,
            gender=gender,
        )

        template = StudentFeedbackEmail()
        self.email_text = template.render(
            student=student,
            mark=mark,
            feedback_bulletpoints=feedback_bulletpoints,
            examiner=examiner_name,
        )
        return self.email_text

    def save_email_to_markdown(
        self,
        output_folder: str,
        student_last_name: str,
        sid: str,
        filename_prefix: str = "kolloquium_anmeldung",
    ) -> str:
        """Speichert den E-Mail-Text in einer Markdown-Datei."""
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{filename_prefix}_{student_last_name}_{sid}.md"
        self.email_path = output_path / filename

        with open(self.email_path, "w", encoding="utf-8") as f:
            f.write(self.email_text)

        print(f"E-Mail-Text gespeichert: {self.email_path}")
        return str(self.email_path)
