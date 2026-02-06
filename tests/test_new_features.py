"""Test-Skript für die neuen Kalender- und Mail-Features."""

import os
import sys

# Füge das src-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from academic_doc_generator.colloquium.calendar_generator import CalendarGenerator
from academic_doc_generator.colloquium.outlook_mail_generator import (
    OutlookMailGenerator,
)


def test_calendar_generation():
    """Testet die Kalender-Generierung."""
    print("=" * 60)
    print("TEST: Kalender-Generierung")
    print("=" * 60)

    calendar_gen = CalendarGenerator()

    # Test 1: Campus-Kolloquium
    print("\n1️⃣  Test: Campus-Kolloquium")
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder="./test_output",
            stud_name="Mustermann, Max",
            date_colloquium="15.02.2026",
            time_colloquium="14:00",
            duration_minutes=45,
            location_type="campus",
            room="3.217",
        )
        print(f"✅ Erfolgreich: {ics_path}")
    except Exception as e:
        print(f"❌ Fehler: {e}")

    # Test 2: Firmen-Kolloquium
    print("\n2️⃣  Test: Firmen-Kolloquium")
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder="./test_output",
            stud_name="Schmidt, Anna",
            date_colloquium="20.03.2026",
            time_colloquium="10:00",
            duration_minutes=45,
            location_type="company",
            company_name="Beispiel GmbH",
            company_address="Musterstraße 123, 50667 Köln",
        )
        print(f"✅ Erfolgreich: {ics_path}")
    except Exception as e:
        print(f"❌ Fehler: {e}")

    # Test 3: Online-Kolloquium
    print("\n3️⃣  Test: Online-Kolloquium")
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder="./test_output",
            stud_name="Weber, Julia",
            date_colloquium="10.04.2026",
            time_colloquium="16:00",
            duration_minutes=45,
            location_type="online",
        )
        print(f"✅ Erfolgreich: {ics_path}")
    except Exception as e:
        print(f"❌ Fehler: {e}")


def test_outlook_mail_generation():
    """Testet die Outlook-Mail-Generierung."""
    print("\n" + "=" * 60)
    print("TEST: Outlook-Mail-Generierung")
    print("=" * 60)

    outlook_gen = OutlookMailGenerator()

    email_text = """Lieber Prüfungsservice,
hiermit möchte ich Herr Max Mustermann (123456) zum Kolloquium anmelden. Dieses findet statt am:
Montag, 15.02.2026, um 14:00,
in Raum 3.217 am Campus GM.
Herr Mustermann: Bitte bereiten Sie eine max. 15-minütige Präsentation zu Ihrer Arbeit vor (wenn möglich inkl. Demo).
Viele Grüße,
Prof. Dr. Müller"""

    print("\n📧 Versuche Outlook-Mail zu erstellen...")
    print("   (Dies wird nur funktionieren, wenn Outlook installiert ist)")

    try:
        success = outlook_gen.create_outlook_mail(
            stud_name="Mustermann, Max",
            email_text=email_text,
            verbose=True,
        )

        if success:
            print("✅ Mail erfolgreich erstellt")
        else:
            print("⚠️  Mail konnte nicht erstellt werden (siehe Ausgabe oben)")

    except Exception as e:
        print(f"❌ Fehler: {e}")


def test_ics_file_content():
    """Testet den Inhalt der generierten ICS-Datei."""
    print("\n" + "=" * 60)
    print("TEST: ICS-Dateiinhalt")
    print("=" * 60)

    calendar_gen = CalendarGenerator()

    try:
        ics_path = calendar_gen.generate_ics(
            output_folder="./test_output",
            stud_name="Test, Student",
            date_colloquium="01.01.2026",
            time_colloquium="12:00",
            duration_minutes=45,
            location_type="campus",
            room="1.234",
        )

        print(f"\n📄 Inhalt von {ics_path}:\n")
        with open(ics_path, "r", encoding="utf-8") as f:
            print(f.read())

    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    print("\n🧪 STARTE TESTS FÜR NEUE FEATURES\n")

    # Erstelle Test-Output-Ordner
    os.makedirs("./test_output", exist_ok=True)

    # Führe Tests aus
    test_calendar_generation()
    test_outlook_mail_generation()
    test_ics_file_content()

    print("\n" + "=" * 60)
    print("✅ ALLE TESTS ABGESCHLOSSEN")
    print("=" * 60)
    print("\nGenerierte Dateien befinden sich in: ./test_output/")
    print("ICS-Dateien können jetzt in einen Kalender importiert werden.")
