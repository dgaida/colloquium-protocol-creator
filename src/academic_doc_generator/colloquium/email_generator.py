# colloquium_pipeline/email_generator.py
"""Modul zur Generierung von Anmelde-E-Mails für Kolloquien."""

from typing import Optional
from pathlib import Path
from ..project.llm_interface import determine_gender_from_name
from ..core.utils import split_student_name
from datetime import datetime


def weekday_from_string(date_str, lang="de"):
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
        zoom_access_code: Optional[str] = None,
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
            zoom_access_code: Zoom-Code.

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
            zoom_access_code=zoom_access_code,
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
        zoom_access_code: Optional[str] = None,
    ) -> Optional[str]:
        """Generiert den Ortszusatz für die E-Mail und den Ort für das PDF-Formular.

        Args:
            location_type: Art des Kolloquiums ("campus", "company", "online").
            room: Raumnummer (nur für "campus").
            company_name: Name der Firma (nur für "company").
            company_address: Adresse der Firma (nur für "company").
            zoom_link: Zoom-Meeting-Link (nur für "online").
            zoom_access_code: Zoom-Zugangscode (nur für "online").

        Returns:
            Tuple aus (email_location_text, pdf_location_text).

        Raises:
            ValueError: Wenn erforderliche Parameter fehlen.
        """
        if location_type == "campus":
            if not room:
                raise ValueError("Für Campus-Kolloquium wird 'room' benötigt")
            email_text = f"in Raum {room} am Campus GM"

        elif location_type == "company":
            if not company_name:
                raise ValueError("Für Firmen-Kolloquium wird 'company_name' benötigt")

            if company_address:
                email_text = f"in der Firma {company_name}, {company_address}"
            else:
                email_text = f"in der Firma {company_name}"

        elif location_type == "online":
            if not zoom_link:
                raise ValueError("Für Online-Kolloquium wird 'zoom_link' benötigt")

            zoom_info = f"über Zoom:\n\nZoom-Link: {zoom_link}"
            if zoom_access_code:
                zoom_info += f"\nZugangscode: {zoom_access_code}"

            email_text = zoom_info
        else:
            raise ValueError(f"Unbekannter location_type: {location_type}")

        return email_text

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
        zoom_access_code: Optional[str] = None,
    ) -> str:
        """Generiert den Text für die Kolloquiums-Anmelde-E-Mail.

        Args:
            student_first_name: Vorname des Studierenden.
            student_last_name: Nachname des Studierenden.
            matriculation_number: Matrikelnummer.
            date_colloquium: Datum im Format "DD.MM.YYYY".
            time_colloquium: Uhrzeit im Format "HH:MM".
            first_examiner: Name des Prüfers.
            location_type: "campus", "company" oder "online".
            room: Raumnummer (optional, für Campus).
            company_name: Firmenname (optional, für Firma).
            company_address: Firmenadresse (optional, für Firma).
            zoom_link: Zoom-Link (optional, für Online).
            zoom_access_code: Zoom-Passcode (optional, für Online).

        Returns:
            Der generierte E-Mail-Text.
        """
        salutation = determine_gender_from_name(student_first_name, llm_client)
        weekday = weekday_from_string(date_colloquium)

        email_location = self._generate_location_text(
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
            zoom_link=zoom_link,
            zoom_access_code=zoom_access_code,
        )

        self.email_text = f"""Lieber Prüfungsservice,
hiermit möchte ich {salutation} {student_first_name} {student_last_name} ({matriculation_number}) zum Kolloquium anmelden. Dieses findet statt am:
{weekday}, {date_colloquium}, um {time_colloquium},
{email_location}.
{salutation} {student_last_name}: Bitte bereiten Sie eine max. 15-minütige Präsentation zu Ihrer Arbeit vor (wenn möglich inkl. Demo).
Viele Grüße,
{first_examiner.title()}"""
        return self.email_text

    def generate_final_grade_email(
        self,
        llm_client,
        student_first_name: str,
        student_last_name: str,
        matriculation_number: str,
        first_examiner: str,
    ) -> str:
        """Generiert den Text für die E-Mail zur Einreichung der Note.

        Args:
            llm_client: LLM-Client zur Geschlechtsbestimmung.
            student_first_name: Vorname des Studierenden.
            student_last_name: Nachname des Studierenden.
            matriculation_number: Matrikelnummer.
            first_examiner: Name des Prüfers.

        Returns:
            Der generierte E-Mail-Text.
        """
        salutation = determine_gender_from_name(student_first_name, llm_client)

        self.email_text = f"""Lieber Prüfungsservice,
hiermit möchte ich die Bewertung für {salutation} {student_first_name} {student_last_name} ({matriculation_number}) einreichen (s. Anhang).
Viele Grüße,
{first_examiner.title()}"""
        return self.email_text

    def save_email_to_markdown(
        self,
        output_folder: str,
        student_last_name: str,
        matriculation_number: str,
        filename_prefix: str = "kolloquium_anmeldung",
    ) -> str:
        """Speichert den E-Mail-Text in einer Markdown-Datei.

        Args:
            output_folder: Ordner, in dem die Datei gespeichert wird.
            student_last_name: Nachname des Studierenden (für Dateinamen).
            matriculation_number: Matrikelnummer (für Dateinamen).
            filename_prefix: Präfix für den Dateinamen.

        Returns:
            Pfad zur gespeicherten Markdown-Datei.
        """
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"{filename_prefix}_{student_last_name}_{matriculation_number}.md"
        self.email_path = output_path / filename

        with open(self.email_path, "w", encoding="utf-8") as f:
            f.write(self.email_text)

        print(f"E-Mail-Text gespeichert: {self.email_path}")
