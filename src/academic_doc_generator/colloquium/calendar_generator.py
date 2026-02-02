"""Modul zur Generierung von ICS-Kalender-Dateien für Kolloquiumstermine."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class CalendarGenerator:
    """Erstellt ICS-Kalender-Dateien für Kolloquiumstermine."""

    def __init__(self):
        """Initialisiert den CalendarGenerator."""
        self.ics_path = None

    def generate_ics(
        self,
        output_folder: str,
        student_name: str,
        date_colloquium: str,
        time_colloquium: str,
        duration_minutes: int = 45,
        location_type: str = "campus",
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
    ) -> str:
        """Generiert eine ICS-Kalender-Datei für das Kolloquium.

        Args:
            output_folder: Ausgabeordner für die ICS-Datei.
            student_name: Name des Studierenden.
            date_colloquium: Datum im Format "DD.MM.YYYY".
            time_colloquium: Uhrzeit im Format "HH:MM".
            duration_minutes: Dauer des Kolloquiums in Minuten (Standard: 45).
            location_type: "campus", "company" oder "online".
            room: Raumnummer (für Campus).
            company_name: Firmenname (für Firma).
            company_address: Firmenadresse (für Firma).

        Returns:
            Pfad zur erstellten ICS-Datei.
        """
        # Parse Datum und Uhrzeit
        dt_start = datetime.strptime(
            f"{date_colloquium} {time_colloquium}", "%d.%m.%Y %H:%M"
        )
        dt_end = dt_start + timedelta(minutes=duration_minutes)

        # Formatiere für ICS (Format: YYYYMMDDTHHMMSS)
        start_str = dt_start.strftime("%Y%m%dT%H%M%S")
        end_str = dt_end.strftime("%Y%m%dT%H%M%S")

        # Erstelle Zeitstempel für UID und DTSTAMP
        now = datetime.now().strftime("%Y%m%dT%H%M%SZ")

        # Erstelle Location-String
        location = self._generate_location_string(
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
        )

        # Erstelle ICS-Inhalt
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//TH Köln//Kolloquium//DE
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:kolloquium-{student_name.replace(" ", "-").replace(",", "")}-{now}@th-koeln.de
DTSTAMP:{now}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:Kolloquium {student_name}
LOCATION:{location}
DESCRIPTION:Kolloquium für {student_name}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT30M
ACTION:DISPLAY
DESCRIPTION:Erinnerung: Kolloquium {student_name} in 30 Minuten
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Erinnerung: Kolloquium {student_name} morgen
END:VALARM
END:VEVENT
END:VCALENDAR"""

        # Speichere ICS-Datei
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        # Bereinige Dateinamen (entferne Kommas und Leerzeichen)
        safe_name = student_name.replace(",", "").replace(" ", "_")
        filename = f"kolloquium_{safe_name}.ics"
        self.ics_path = output_path / filename

        with open(self.ics_path, "w", encoding="utf-8") as f:
            f.write(ics_content)

        print(f"✅ Kalender-Datei erstellt: {self.ics_path}")
        return str(self.ics_path)

    def _generate_location_string(
        self,
        location_type: str,
        room: Optional[str] = None,
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
    ) -> str:
        """Generiert den Location-String für die ICS-Datei.

        Args:
            location_type: Art des Kolloquiums ("campus", "company", "online").
            room: Raumnummer (nur für "campus").
            company_name: Name der Firma (nur für "company").
            company_address: Adresse der Firma (nur für "company").

        Returns:
            Location-String für ICS-Datei.

        Raises:
            ValueError: Wenn erforderliche Parameter fehlen.
        """
        if location_type == "campus":
            if not room:
                raise ValueError("Für Campus-Kolloquium wird 'room' benötigt")
            return f"Raum {room}, Campus Gummersbach, Steinmüllerallee 1, 51643 Gummersbach"

        elif location_type == "company":
            if not company_name:
                raise ValueError("Für Firmen-Kolloquium wird 'company_name' benötigt")

            if company_address:
                return f"{company_name}, {company_address}"
            else:
                return company_name

        elif location_type == "online":
            return "Online (Zoom)"

        else:
            raise ValueError(f"Unbekannter location_type: {location_type}")
