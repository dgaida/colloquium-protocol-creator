"""
Unit tests for src/academic_doc_generator/colloquium/email_generator.py
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime

from academic_doc_generator.colloquium import email_generator


class TestWeekdayFromString:
    """Tests für die weekday_from_string Funktion."""

    def test_weekday_german_monday(self):
        """Test Wochentag für Montag auf Deutsch."""
        # 20.01.2026 ist ein Dienstag
        result = email_generator.weekday_from_string("20.01.2026", lang="de")
        assert result == "Dienstag"

    def test_weekday_german_friday(self):
        """Test Wochentag für Freitag auf Deutsch."""
        # 23.01.2026 ist ein Freitag
        result = email_generator.weekday_from_string("23.01.2026", lang="de")
        assert result == "Freitag"

    def test_weekday_german_sunday(self):
        """Test Wochentag für Sonntag auf Deutsch."""
        # 25.01.2026 ist ein Sonntag
        result = email_generator.weekday_from_string("25.01.2026", lang="de")
        assert result == "Sonntag"

    def test_weekday_english_monday(self):
        """Test Wochentag auf Englisch."""
        result = email_generator.weekday_from_string("20.01.2026", lang="en")
        assert result == "Tuesday"

    def test_weekday_english_friday(self):
        """Test Wochentag für Freitag auf Englisch."""
        result = email_generator.weekday_from_string("23.01.2026", lang="en")
        assert result == "Friday"

    def test_weekday_invalid_language(self):
        """Test mit ungültiger Sprache."""
        with pytest.raises(ValueError, match="Unsupported language"):
            email_generator.weekday_from_string("20.01.2026", lang="fr")

    def test_weekday_different_years(self):
        """Test Wochentage in verschiedenen Jahren."""
        # 01.01.2025 ist ein Mittwoch
        result = email_generator.weekday_from_string("01.01.2025", lang="de")
        assert result == "Mittwoch"
        
        # 01.01.2026 ist ein Donnerstag
        result = email_generator.weekday_from_string("01.01.2026", lang="de")
        assert result == "Donnerstag"


class TestEmailGenerator:
    """Tests für die EmailGenerator-Klasse."""

    def test_init(self):
        """Test Initialisierung des EmailGenerator."""
        generator = email_generator.EmailGenerator()
        
        assert generator.email_path is None
        assert generator.email_text is None

    def test_generate_location_text_campus(self):
        """Test _generate_location_text für Campus."""
        generator = email_generator.EmailGenerator()
        
        result = generator._generate_location_text(
            location_type="campus", room="3.217"
        )
        
        assert result == "in Raum 3.217 am Campus GM"

    def test_generate_location_text_campus_no_room(self):
        """Test _generate_location_text für Campus ohne Raum."""
        generator = email_generator.EmailGenerator()
        
        with pytest.raises(ValueError, match="'room' benötigt"):
            generator._generate_location_text(location_type="campus")

    def test_generate_location_text_company_with_address(self):
        """Test _generate_location_text für Firma mit Adresse."""
        generator = email_generator.EmailGenerator()
        
        result = generator._generate_location_text(
            location_type="company",
            company_name="Beispiel GmbH",
            company_address="Musterstraße 42, 51643 Gummersbach"
        )
        
        assert result == "in der Firma Beispiel GmbH, Musterstraße 42, 51643 Gummersbach"

    def test_generate_location_text_company_without_address(self):
        """Test _generate_location_text für Firma ohne Adresse."""
        generator = email_generator.EmailGenerator()
        
        result = generator._generate_location_text(
            location_type="company", company_name="Test GmbH"
        )
        
        assert result == "in der Firma Test GmbH"

    def test_generate_location_text_company_no_name(self):
        """Test _generate_location_text für Firma ohne Namen."""
        generator = email_generator.EmailGenerator()
        
        with pytest.raises(ValueError, match="'company_name' benötigt"):
            generator._generate_location_text(location_type="company")

    def test_generate_location_text_online_with_passcode(self):
        """Test _generate_location_text für Online mit Passcode."""
        generator = email_generator.EmailGenerator()
        
        result = generator._generate_location_text(
            location_type="online",
            zoom_link="https://zoom.us/j/123456",
            zoom_passcode="test123"
        )
        
        assert "über Zoom:" in result
        assert "https://zoom.us/j/123456" in result
        assert "Zugangscode: test123" in result

    def test_generate_location_text_online_without_passcode(self):
        """Test _generate_location_text für Online ohne Passcode."""
        generator = email_generator.EmailGenerator()
        
        result = generator._generate_location_text(
            location_type="online", zoom_link="https://zoom.us/j/123456"
        )
        
        assert "über Zoom:" in result
        assert "https://zoom.us/j/123456" in result
        assert "Zugangscode" not in result

    def test_generate_location_text_online_no_link(self):
        """Test _generate_location_text für Online ohne Link."""
        generator = email_generator.EmailGenerator()
        
        with pytest.raises(ValueError, match="'zoom_link' benötigt"):
            generator._generate_location_text(location_type="online")

    def test_generate_location_text_unknown_type(self):
        """Test _generate_location_text mit unbekanntem Typ."""
        generator = email_generator.EmailGenerator()
        
        with pytest.raises(ValueError, match="Unbekannter location_type"):
            generator._generate_location_text(location_type="unknown")

    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    def test_generate_colloquium_email_campus(self, mock_gender, mock_weekday):
        """Test generate_colloquium_email für Campus-Kolloquium."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Dienstag"
        
        generator = email_generator.EmailGenerator()
        generator.generate_colloquium_email(
            llm_client=MagicMock(),
            student_first_name="Max",
            student_last_name="Mustermann",
            matriculation_number="12345",
            date_colloquium="20.01.2026",
            time_colloquium="14:00",
            first_examiner="Prof. Test",
            location_type="campus",
            room="3.217"
        )
        
        assert generator.email_text is not None
        assert "Herr Max Mustermann" in generator.email_text
        assert "12345" in generator.email_text
        assert "Dienstag, 20.01.2026, um 14:00" in generator.email_text
        assert "in Raum 3.217 am Campus GM" in generator.email_text
        assert "Prof. Test" in generator.email_text

    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    def test_generate_colloquium_email_female_student(self, mock_gender, mock_weekday):
        """Test generate_colloquium_email für weibliche Studierende."""
        mock_gender.return_value = "Frau"
        mock_weekday.return_value = "Mittwoch"
        
        generator = email_generator.EmailGenerator()
        generator.generate_colloquium_email(
            llm_client=MagicMock(),
            student_first_name="Maria",
            student_last_name="Musterfrau",
            matriculation_number="67890",
            date_colloquium="21.01.2026",
            time_colloquium="10:00",
            first_examiner="Dr. Test",
            location_type="campus",
            room="1.101"
        )
        
        assert "Frau Maria Musterfrau" in generator.email_text

    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    def test_generate_colloquium_email_company(self, mock_gender, mock_weekday):
        """Test generate_colloquium_email für Firmen-Kolloquium."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Donnerstag"
        
        generator = email_generator.EmailGenerator()
        generator.generate_colloquium_email(
            llm_client=MagicMock(),
            student_first_name="Test",
            student_last_name="Student",
            matriculation_number="11111",
            date_colloquium="22.01.2026",
            time_colloquium="15:00",
            first_examiner="Prof. Example",
            location_type="company",
            company_name="Test GmbH",
            company_address="Teststraße 1"
        )
        
        assert "in der Firma Test GmbH, Teststraße 1" in generator.email_text

    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    def test_generate_colloquium_email_online(self, mock_gender, mock_weekday):
        """Test generate_colloquium_email für Online-Kolloquium."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Freitag"
        
        generator = email_generator.EmailGenerator()
        generator.generate_colloquium_email(
            llm_client=MagicMock(),
            student_first_name="Online",
            student_last_name="Student",
            matriculation_number="99999",
            date_colloquium="23.01.2026",
            time_colloquium="16:00",
            first_examiner="Prof. Remote",
            location_type="online",
            zoom_link="https://zoom.us/j/123",
            zoom_passcode="abc123"
        )
        
        assert "über Zoom:" in generator.email_text
        assert "https://zoom.us/j/123" in generator.email_text
        assert "Zugangscode: abc123" in generator.email_text

    def test_save_email_to_markdown(self):
        """Test save_email_to_markdown."""
        generator = email_generator.EmailGenerator()
        generator.email_text = "Test email content"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.save_email_to_markdown(
                output_folder=tmpdir,
                student_last_name="Mustermann",
                matriculation_number="12345"
            )
            
            assert generator.email_path is not None
            assert os.path.exists(generator.email_path)
            
            # Prüfe Dateinamen
            expected_filename = "kolloquium_anmeldung_Mustermann_12345.md"
            assert generator.email_path.name == expected_filename
            
            # Prüfe Inhalt
            with open(generator.email_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == "Test email content"

    def test_save_email_to_markdown_creates_folder(self):
        """Test dass save_email_to_markdown Ordner erstellt."""
        generator = email_generator.EmailGenerator()
        generator.email_text = "Test"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            subfolder = os.path.join(tmpdir, "subdir", "nested")
            generator.save_email_to_markdown(
                output_folder=subfolder,
                student_last_name="Test",
                matriculation_number="00000"
            )
            
            assert os.path.exists(subfolder)
            assert os.path.exists(generator.email_path)

    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    @patch("builtins.print")
    def test_generate_and_save_email_complete_flow(self, mock_print, mock_weekday, mock_gender):
        """Test complete flow von generate_and_save_email."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Montag"
        
        generator = email_generator.EmailGenerator()
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=mock_client,
                output_folder=tmpdir,
                author="Mustermann, Max",
                matriculation="12345",
                date_colloquium="19.01.2026",
                uhrzeit_colloquium="09:00",
                first_examiner="Prof. Dr. Test",
                location_type="campus",
                room="2.208"
            )
            
            assert generator.email_text is not None
            assert generator.email_path is not None
            assert os.path.exists(generator.email_path)
            
            # Prüfe Email-Inhalt
            assert "Herr Max Mustermann" in generator.email_text
            assert "12345" in generator.email_text
            assert "Montag, 19.01.2026, um 09:00" in generator.email_text
            assert "in Raum 2.208 am Campus GM" in generator.email_text
            
            # Prüfe dass Datei gespeichert wurde
            with open(generator.email_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == generator.email_text

    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    @patch("builtins.print")
    def test_generate_and_save_email_author_format_firstname_lastname(
        self, mock_print, mock_gender
    ):
        """Test generate_and_save_email mit 'Vorname Nachname' Format."""
        mock_gender.return_value = "Frau"
        
        generator = email_generator.EmailGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=MagicMock(),
                output_folder=tmpdir,
                author="Maria Musterfrau",  # Format: Vorname Nachname
                matriculation="67890",
                date_colloquium="20.01.2026",
                uhrzeit_colloquium="14:00",
                first_examiner="Prof. Test",
                location_type="campus",
                room="3.217"
            )
            
            assert "Frau Maria Musterfrau" in generator.email_text
            assert "kolloquium_anmeldung_Musterfrau_67890.md" in str(generator.email_path)

    @patch("builtins.print")
    def test_generate_and_save_email_author_none(self, mock_print):
        """Test generate_and_save_email mit author=None."""
        generator = email_generator.EmailGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=MagicMock(),
                output_folder=tmpdir,
                author=None,
                matriculation="12345",
                date_colloquium="20.01.2026",
                uhrzeit_colloquium="14:00",
                first_examiner="Prof. Test",
                location_type="campus",
                room="3.217"
            )
            
            # Sollte früh abbrechen
            assert generator.email_text is None
            assert any("Error: author" in str(call) for call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    def test_generate_and_save_email_single_name(self, mock_weekday, mock_gender):
        """Test generate_and_save_email mit nur einem Namen."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Dienstag"
        
        generator = email_generator.EmailGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=MagicMock(),
                output_folder=tmpdir,
                author="SingleName",
                matriculation="11111",
                date_colloquium="20.01.2026",
                uhrzeit_colloquium="14:00",
                first_examiner="Prof. Test",
                location_type="campus",
                room="3.217"
            )
            
            # Bei nur einem Namen: Vorname = "SingleName", Nachname = "SingleName"
            assert generator.email_text is not None
            assert "SingleName" in generator.email_text


class TestIntegration:
    """Integrationstests für EmailGenerator."""

    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    def test_full_email_generation_campus(self, mock_weekday, mock_gender):
        """Test vollständige Email-Generierung für Campus."""
        mock_gender.return_value = "Herr"
        mock_weekday.return_value = "Dienstag"
        
        generator = email_generator.EmailGenerator()
        mock_client = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=mock_client,
                output_folder=tmpdir,
                author="Mustermann, Max",
                matriculation="12345",
                date_colloquium="20.01.2026",
                uhrzeit_colloquium="14:00",
                first_examiner="Prof. Dr. Hans Meyer",
                location_type="campus",
                room="3.217"
            )
            
            # Prüfe dass alle Komponenten vorhanden sind
            assert generator.email_text is not None
            assert generator.email_path is not None
            
            # Prüfe Email-Struktur
            assert "Lieber Prüfungsservice," in generator.email_text
            assert "hiermit möchte ich" in generator.email_text
            assert "Herr Max Mustermann (12345)" in generator.email_text
            assert "Dienstag, 20.01.2026, um 14:00" in generator.email_text
            assert "in Raum 3.217 am Campus GM" in generator.email_text
            assert "Bitte bereiten Sie eine max. 15-minütige Präsentation" in generator.email_text
            assert "Viele Grüße," in generator.email_text
            assert "Prof. Dr. Hans Meyer" in generator.email_text
            
            # Prüfe Datei
            assert os.path.exists(generator.email_path)
            with open(generator.email_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == generator.email_text

    @patch("academic_doc_generator.colloquium.email_generator.determine_gender_from_name")
    @patch("academic_doc_generator.colloquium.email_generator.weekday_from_string")
    def test_full_email_generation_online(self, mock_weekday, mock_gender):
        """Test vollständige Email-Generierung für Online."""
        mock_gender.return_value = "Frau"
        mock_weekday.return_value = "Mittwoch"
        
        generator = email_generator.EmailGenerator()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator.generate_and_save_email(
                llm_client=MagicMock(),
                output_folder=tmpdir,
                author="Musterfrau, Maria",
                matriculation="67890",
                date_colloquium="21.01.2026",
                uhrzeit_colloquium="15:30",
                first_examiner="Dr. Anna Schmidt",
                location_type="online",
                zoom_link="https://zoom.us/j/123456789",
                zoom_passcode="Kolloquium2026"
            )
            
            # Prüfe Online-spezifische Details
            assert "über Zoom:" in generator.email_text
            assert "Zoom-Link: https://zoom.us/j/123456789" in generator.email_text
            assert "Zugangscode: Kolloquium2026" in generator.email_text
            assert "Frau Maria Musterfrau" in generator.email_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
