"""Test-Skript für die neuen Kalender- und Mail-Features."""

import contextlib
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

from academic_doc_generator.core import pdf
from academic_doc_generator.core.metadata import generate_metadata_file

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
            student_name="Mustermann, Max",
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
            student_name="Schmidt, Anna",
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
            student_name="Weber, Julia",
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
            student_name="Mustermann, Max",
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
            student_name="Test, Student",
            date_colloquium="01.01.2026",
            time_colloquium="12:00",
            duration_minutes=45,
            location_type="campus",
            room="1.234",
        )

        print(f"\n📄 Inhalt von {ics_path}:\n")
        with open(ics_path, encoding="utf-8") as f:
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

# ==============================================================================
# Pytest Unit Tests for Fallback PDF Parser and Unknown Author behavior
# ==============================================================================


def test_pdf_parser_fallback_chain_success_liteparse():
    """Test that extract_text_with_positions successfully uses liteparse first."""
    with patch("liteparse.LiteParse") as mock_liteparse:
        mock_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.height = 800
        mock_page.width = 600

        mock_item_1 = MagicMock()
        mock_item_1.text = "Hello World"
        mock_item_1.x = 10
        mock_item_1.y = 20
        mock_item_1.width = 100
        mock_item_1.height = 15
        mock_item_1.words = []

        mock_page.text_items = [mock_item_1]
        mock_instance.parse.return_value.pages = [mock_page]
        mock_liteparse.return_value = mock_instance

        # Call with a dummy PDF file that has valid %PDF header
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4\n")
            f.flush()
            temp_path = f.name

        try:
            res = pdf.extract_text_with_positions(temp_path)
            assert len(res) == 1
            # Hello World split into parts
            assert res[0][0]["text"] == "Hello"
        finally:
            with contextlib.suppress(OSError):
                os.remove(temp_path)


def test_pdf_parser_fallback_chain_liteparse_fails():
    """Test that extract_text_with_positions falls back to docling when liteparse fails."""
    with (
        patch("liteparse.LiteParse", side_effect=Exception("LiteParse failed")),
        patch("academic_doc_generator.core.pdf.DoclingPdfParser") as mock_docling,
    ):

        mock_instance = MagicMock()
        mock_page = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "Docling text"
        mock_cell.rect.r_x0 = 10
        mock_cell.rect.r_y0 = 20
        mock_cell.rect.r_x1 = 50
        mock_cell.rect.r_y1 = 30

        mock_page.iterate_cells.return_value = [mock_cell]
        mock_instance.iterate_pages.return_value = [(1, mock_page)]
        mock_docling.return_value.load.return_value = mock_instance

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4\n")
            f.flush()
            temp_path = f.name

        try:
            res = pdf.extract_text_with_positions(temp_path)
            assert len(res) == 1
            assert res[0][0]["text"] == "Docling text"
        finally:
            with contextlib.suppress(OSError):
                os.remove(temp_path)


def test_unknown_author_metadata_not_copied():
    """Test that metadata file is not copied to web folder if author is Unknown."""
    mock_client = MagicMock()
    mock_client.chat_completion.return_value = "Concise summary for web"

    with tempfile.TemporaryDirectory() as tmp_out, tempfile.TemporaryDirectory() as tmp_web:

        # Case 1: Unknown Author
        md_path = generate_metadata_file(
            output_folder=tmp_out,
            title="A Great Thesis",
            author="Unknown",
            pages_text={0: "Page text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="Wintersemester 24/25",
            date_str="2026-02-15",
            copy_to_web_folder=True,
            web_metadata_folder=tmp_web,
        )

        # Verify local file is created but not copied to the web metadata folder
        assert os.path.exists(md_path)
        assert len(os.listdir(tmp_web)) == 0

        # Case 2: Known Author
        md_path_2 = generate_metadata_file(
            output_folder=tmp_out,
            title="A Great Thesis",
            author="Max Mustermann",
            pages_text={0: "Page text"},
            llm_client=mock_client,
            work_type="Bachelorthesis",
            semester="Wintersemester 24/25",
            date_str="2026-02-15",
            copy_to_web_folder=True,
            web_metadata_folder=tmp_web,
        )

        # Verify copied file is created in tmp_web
        assert os.path.exists(md_path_2)
        assert len(os.listdir(tmp_web)) == 1
