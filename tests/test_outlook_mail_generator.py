"""
Unit tests for src/academic_doc_generator/colloquium/outlook_mail_generator.py
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.colloquium.outlook_mail_generator import (
    OutlookMailGenerator,
)


class TestOutlookMailGeneratorInit:
    """Tests für die Initialisierung."""

    def test_init(self):
        """Test Initialisierung des OutlookMailGenerator."""
        generator = OutlookMailGenerator()

        # Prüfe dass RECIPIENT_EMAIL gesetzt ist
        assert generator.RECIPIENT_EMAIL == "studium-gm@th-koeln.de"


class TestCreateOutlookMail:
    """Tests für die create_outlook_mail Hauptmethode."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch.object(OutlookMailGenerator, "_create_outlook_mail_windows")
    def test_create_outlook_mail_windows(self, mock_windows, mock_platform):
        """Test create_outlook_mail auf Windows."""
        mock_platform.return_value = "Windows"
        mock_windows.return_value = True

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Max Mustermann",
            email_text="Test email text",
            attachment_path="/path/to/calendar.ics",
            verbose=False,
            recipient="test@example.com",
        )

        assert result is True
        mock_windows.assert_called_once_with(
            "Anmeldung Kolloquium Max Mustermann",
            "Test email text",
            "/path/to/calendar.ics",
            False,
            "test@example.com",
        )

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch.object(OutlookMailGenerator, "_create_outlook_mail_macos")
    def test_create_outlook_mail_macos(self, mock_macos, mock_platform):
        """Test create_outlook_mail auf macOS."""
        mock_platform.return_value = "Darwin"
        mock_macos.return_value = True

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Test Student",
            email_text="Test text",
            attachment_path=None,
            verbose=True,
        )

        assert result is True
        mock_macos.assert_called_once_with(
            "Anmeldung Kolloquium Test Student",
            "Test text",
            None,
            True,
            "studium-gm@th-koeln.de",
        )

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch.object(OutlookMailGenerator, "_create_outlook_mail_linux")
    def test_create_outlook_mail_linux(self, mock_linux, mock_platform):
        """Test create_outlook_mail auf Linux."""
        mock_platform.return_value = "Linux"
        mock_linux.return_value = True

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Linux User", email_text="Linux test", verbose=False
        )

        assert result is True
        mock_linux.assert_called_once()

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    def test_create_outlook_mail_unsupported_platform(self, mock_platform):
        """Test create_outlook_mail auf nicht unterstützter Plattform."""
        mock_platform.return_value = "FreeBSD"

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Test", email_text="Test", verbose=False
        )

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch.object(OutlookMailGenerator, "_create_outlook_mail_windows")
    def test_create_outlook_mail_exception(self, mock_windows, mock_platform):
        """Test create_outlook_mail mit Exception."""
        mock_platform.return_value = "Windows"
        mock_windows.side_effect = Exception("Test error")

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Test", email_text="Test", verbose=False
        )

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch.object(OutlookMailGenerator, "_create_outlook_mail_windows")
    @patch("builtins.print")
    def test_create_outlook_mail_verbose_exception(self, mock_print, mock_windows, mock_platform):
        """Test create_outlook_mail mit Exception und verbose=True."""
        mock_platform.return_value = "Windows"
        mock_windows.side_effect = Exception("Detailed error")

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(student_name="Test", email_text="Test", verbose=True)

        assert result is False
        # Prüfe dass Fehler gedruckt wurde
        assert any("Fehler" in str(mock_call) for mock_call in mock_print.call_args_list)


class TestOpenIcsInOutlook:
    """Tests für die open_ics_in_outlook Methode."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch(
        "academic_doc_generator.colloquium.outlook_mail_generator.os.startfile",
        create=True,
    )
    @patch("builtins.print")
    def test_open_ics_in_outlook_windows_success(self, mock_print, mock_startfile, mock_platform):
        """Test open_ics_in_outlook auf Windows erfolgreich."""
        mock_platform.return_value = "Windows"

        generator = OutlookMailGenerator()
        result = generator.open_ics_in_outlook("/path/to/calendar.ics", verbose=False)

        assert result is True
        mock_startfile.assert_called_once_with("/path/to/calendar.ics")

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    def test_open_ics_in_outlook_non_windows(self, mock_platform):
        """Test open_ics_in_outlook auf nicht-Windows System."""
        mock_platform.return_value = "Darwin"

        generator = OutlookMailGenerator()
        result = generator.open_ics_in_outlook("/path/to/calendar.ics", verbose=False)

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch("builtins.print")
    def test_open_ics_in_outlook_non_windows_verbose(self, mock_print, mock_platform):
        """Test open_ics_in_outlook auf nicht-Windows mit verbose."""
        mock_platform.return_value = "Linux"

        generator = OutlookMailGenerator()
        result = generator.open_ics_in_outlook("/path/to/calendar.ics", verbose=True)

        assert result is False
        assert any("nur unter Windows" in str(mock_call) for mock_call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch(
        "academic_doc_generator.colloquium.outlook_mail_generator.os.startfile",
        create=True,
    )
    def test_open_ics_in_outlook_exception(self, mock_startfile, mock_platform):
        """Test open_ics_in_outlook mit Exception."""
        mock_platform.return_value = "Windows"
        mock_startfile.side_effect = Exception("File not found")

        generator = OutlookMailGenerator()
        result = generator.open_ics_in_outlook("/path/to/calendar.ics", verbose=False)

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch(
        "academic_doc_generator.colloquium.outlook_mail_generator.os.startfile",
        create=True,
    )
    @patch("builtins.print")
    def test_open_ics_in_outlook_verbose_exception(self, mock_print, mock_startfile, mock_platform):
        """Test open_ics_in_outlook mit Exception und verbose."""
        mock_platform.return_value = "Windows"
        mock_startfile.side_effect = Exception("Access denied")

        generator = OutlookMailGenerator()
        result = generator.open_ics_in_outlook("/path/to/calendar.ics", verbose=True)

        assert result is False
        assert any("Fehler" in str(mock_call) for mock_call in mock_print.call_args_list)


class TestCreateOutlookMailWindows:
    """Tests für die Windows-spezifische Implementierung."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Setzt Mocks für win32com auf, die plattformunabhängig funktionieren."""
        self.mock_win32com = MagicMock()
        self.mock_win32com_client = MagicMock()
        self.mock_win32com.client = self.mock_win32com_client

        # Patch sys.modules so 'import win32com.client' works everywhere
        with patch.dict(
            "sys.modules",
            {
                "win32com": self.mock_win32com,
                "win32com.client": self.mock_win32com_client,
            },
        ):
            yield

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.abspath")
    @patch("builtins.print")
    def test_create_outlook_mail_windows_success(self, mock_print, mock_abspath, mock_exists):
        """Test Windows-Mail-Erstellung erfolgreich."""
        # Mock Outlook COM objects
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_outlook.CreateItem.return_value = mock_mail
        self.mock_win32com_client.Dispatch.return_value = mock_outlook

        mock_exists.return_value = True
        mock_abspath.return_value = "/absolute/path/to/calendar.ics"

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_windows(
            subject="Test Subject",
            body="Test Body",
            attachment_path="/path/to/calendar.ics",
            verbose=False,
        )

        assert result is True
        self.mock_win32com_client.Dispatch.assert_called_once_with("Outlook.Application")
        mock_outlook.CreateItem.assert_called_once_with(0)
        assert mock_mail.To == "studium-gm@th-koeln.de"
        assert mock_mail.Subject == "Test Subject"
        assert mock_mail.Body == "Test Body"
        mock_mail.Attachments.Add.assert_called_once_with("/absolute/path/to/calendar.ics")
        mock_mail.Display.assert_called_once_with(False)

    @patch("builtins.print")
    def test_create_outlook_mail_windows_no_attachment(self, mock_print):
        """Test Windows-Mail ohne Anhang."""
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_outlook.CreateItem.return_value = mock_mail
        self.mock_win32com_client.Dispatch.return_value = mock_outlook

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_windows(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is True
        mock_mail.Attachments.Add.assert_not_called()

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("builtins.print")
    def test_create_outlook_mail_windows_attachment_not_found(self, mock_print, mock_exists):
        """Test Windows-Mail mit nicht existierendem Anhang."""
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_outlook.CreateItem.return_value = mock_mail
        self.mock_win32com_client.Dispatch.return_value = mock_outlook

        mock_exists.return_value = False

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_windows(
            subject="Test",
            body="Body",
            attachment_path="/nonexistent.ics",
            verbose=False,
        )

        assert result is True
        mock_mail.Attachments.Add.assert_not_called()
        assert any("nicht gefunden" in str(mock_call) for mock_call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("builtins.print")
    def test_create_outlook_mail_windows_verbose_attachment(self, mock_print, mock_exists):
        """Test Windows-Mail mit verbose und Anhang."""
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_outlook.CreateItem.return_value = mock_mail
        self.mock_win32com_client.Dispatch.return_value = mock_outlook

        mock_exists.return_value = True

        generator = OutlookMailGenerator()
        generator._create_outlook_mail_windows(
            subject="Test", body="Body", attachment_path="/test.ics", verbose=True
        )

        assert any(
            "als Anhang hinzugefügt" in str(mock_call) for mock_call in mock_print.call_args_list
        )

    def test_create_outlook_mail_windows_import_error(self):
        """Test Windows-Mail mit fehlendem pywin32."""
        generator = OutlookMailGenerator()

        # Wir müssen den globalen Patch für diesen Test umgehen oder überschreiben
        with (
            patch.dict("sys.modules", {"win32com": None, "win32com.client": None}),
            patch("builtins.print") as mock_print,
        ):
            result = generator._create_outlook_mail_windows("Test", "Body", None, False)
            assert result is False
            assert any(
                "pywin32 nicht installiert" in str(call) for call in mock_print.call_args_list
            )

    @patch("builtins.print")
    def test_create_outlook_mail_windows_com_exception(self, mock_print):
        """Test Windows-Mail mit COM-Exception."""
        self.mock_win32com_client.Dispatch.side_effect = Exception("COM Error")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_windows(
            subject="Test", body="Body", attachment_path=None, verbose=True
        )

        assert result is False
        assert any("Fehler" in str(mock_call) for mock_call in mock_print.call_args_list)


class TestCreateOutlookMailMacOS:
    """Tests für die macOS-spezifische Implementierung."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("builtins.print")
    def test_create_outlook_mail_macos_success(self, mock_print, mock_exists, mock_subprocess):
        """Test macOS-Mail-Erstellung erfolgreich."""
        mock_exists.return_value = True

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test Subject",
            body="Test Body",
            attachment_path="/path/to/calendar.ics",
            verbose=False,
        )

        assert result is True
        mock_subprocess.assert_called_once()

        # Prüfe AppleScript-Aufruf
        call_args = mock_subprocess.call_args
        assert call_args[0][0][0] == "osascript"
        assert call_args[0][0][1] == "-e"
        applescript = call_args[0][0][2]
        assert "Microsoft Outlook" in applescript
        assert "Test Subject" in applescript
        assert "Test Body" in applescript
        assert "calendar.ics" in applescript

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("builtins.print")
    def test_create_outlook_mail_macos_no_attachment(self, mock_print, mock_subprocess):
        """Test macOS-Mail ohne Anhang."""
        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is True
        call_args = mock_subprocess.call_args
        applescript = call_args[0][0][2]
        assert "attachment" not in applescript.lower()

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("builtins.print")
    def test_create_outlook_mail_macos_attachment_verbose(
        self, mock_print, mock_exists, mock_subprocess
    ):
        """Test macOS-Mail mit Anhang und verbose."""
        mock_exists.return_value = True

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test", body="Body", attachment_path="/test.ics", verbose=True
        )

        assert result is True
        assert any(
            "als Anhang hinzugefügt" in str(mock_call) for mock_call in mock_print.call_args_list
        )

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    def test_create_outlook_mail_macos_subprocess_error(self, mock_subprocess):
        """Test macOS-Mail mit subprocess-Fehler."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "osascript")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("builtins.print")
    def test_create_outlook_mail_macos_verbose_error(self, mock_print, mock_subprocess):
        """Test macOS-Mail mit Fehler und verbose."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "osascript")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test", body="Body", attachment_path=None, verbose=True
        )

        assert result is False
        assert any("Fehler" in str(mock_call) for mock_call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    def test_create_outlook_mail_macos_general_exception(self, mock_subprocess):
        """Test macOS-Mail mit allgemeiner Exception."""
        mock_subprocess.side_effect = Exception("Unexpected error")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    def test_create_outlook_mail_macos_special_chars(self, mock_exists, mock_subprocess):
        """Test macOS-Mail mit Sonderzeichen."""
        mock_exists.return_value = True

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_macos(
            subject='Test "Subject" with \\backslash',
            body='Body with "quotes" and \\backslash',
            attachment_path="/path/with spaces/file.ics",
            verbose=False,
        )

        assert result is True
        call_args = mock_subprocess.call_args
        applescript = call_args[0][0][2]
        # Prüfe dass Escaping stattgefunden hat
        assert '\\"' in applescript or "\\\\'" in applescript


class TestCreateOutlookMailLinux:
    """Tests für die Linux-spezifische Implementierung."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    @patch("builtins.print")
    def test_create_outlook_mail_linux_success(self, mock_print, mock_urllib, mock_subprocess):
        """Test Linux-Mail-Erstellung erfolgreich."""
        mock_urllib.urlencode.return_value = "subject=Test&body=Body"

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_linux(
            subject="Test Subject",
            body="Test Body",
            attachment_path="/path/to/calendar.ics",
            verbose=False,
        )

        assert result is True
        mock_subprocess.assert_called_once()

        # Prüfe xdg-open Aufruf
        call_args = mock_subprocess.call_args
        assert call_args[0][0][0] == "xdg-open"
        assert "mailto:" in call_args[0][0][1]
        assert "studium-gm@th-koeln.de" in call_args[0][0][1]

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    @patch("builtins.print")
    def test_create_outlook_mail_linux_with_ics_verbose(
        self, mock_print, mock_urllib, mock_subprocess
    ):
        """Test Linux-Mail mit ICS-Datei und verbose."""
        mock_urllib.urlencode.return_value = "subject=Test&body=Body"

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_linux(
            subject="Test", body="Body", attachment_path="/test.ics", verbose=True
        )

        assert result is True
        assert any(
            "nicht automatisch hinzugefügt" in str(mock_call)
            for mock_call in mock_print.call_args_list
        )

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    def test_create_outlook_mail_linux_subprocess_error(self, mock_urllib, mock_subprocess):
        """Test Linux-Mail mit subprocess-Fehler."""
        mock_urllib.urlencode.return_value = "subject=Test&body=Body"
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "xdg-open")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_linux(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is False

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    @patch("builtins.print")
    def test_create_outlook_mail_linux_verbose_error(
        self, mock_print, mock_urllib, mock_subprocess
    ):
        """Test Linux-Mail mit Fehler und verbose."""
        mock_urllib.urlencode.return_value = "subject=Test&body=Body"
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "xdg-open")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_linux(
            subject="Test", body="Body", attachment_path=None, verbose=True
        )

        assert result is False
        assert any(
            "Konnte Standard-Mail-Client nicht" in str(mock_call)
            for mock_call in mock_print.call_args_list
        )

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    def test_create_outlook_mail_linux_general_exception(self, mock_urllib, mock_subprocess):
        """Test Linux-Mail mit allgemeiner Exception."""
        mock_urllib.urlencode.side_effect = Exception("URL encoding error")

        generator = OutlookMailGenerator()
        result = generator._create_outlook_mail_linux(
            subject="Test", body="Body", attachment_path=None, verbose=False
        )

        assert result is False


class TestIntegration:
    """Integrationstests für OutlookMailGenerator."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.abspath")
    def test_full_windows_workflow(self, mock_abspath, mock_exists, mock_platform):
        """Test vollständiger Windows-Workflow."""
        mock_platform.return_value = "Windows"
        mock_exists.return_value = True
        mock_abspath.return_value = "/abs/path/calendar.ics"

        mock_win32com = MagicMock()
        mock_win32com_client = MagicMock()
        mock_win32com.client = mock_win32com_client
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_win32com_client.Dispatch.return_value = mock_outlook
        mock_outlook.CreateItem.return_value = mock_mail

        with patch.dict(
            "sys.modules",
            {"win32com": mock_win32com, "win32com.client": mock_win32com_client},
        ):
            generator = OutlookMailGenerator()
            result = generator.create_outlook_mail(
                student_name="Mustermann, Max",
                email_text="Lieber Prüfungsservice,\nhiermit möchte ich Herr Max Mustermann anmelden.",
                attachment_path="/path/to/calendar.ics",
                verbose=False,
            )

            assert result is True
            assert mock_mail.Subject == "Anmeldung Kolloquium Mustermann, Max"
            assert "Herr Max Mustermann" in mock_mail.Body
            mock_mail.Attachments.Add.assert_called_once()
            mock_mail.Display.assert_called_once()

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.os.path.exists")
    def test_full_macos_workflow(self, mock_exists, mock_subprocess, mock_platform):
        """Test vollständiger macOS-Workflow."""
        mock_platform.return_value = "Darwin"
        mock_exists.return_value = True

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Schmidt, Anna",
            email_text="Test email für macOS",
            attachment_path="/Users/test/calendar.ics",
            verbose=False,
        )

        assert result is True
        mock_subprocess.assert_called_once()

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.subprocess.run")
    @patch("academic_doc_generator.colloquium.outlook_mail_generator.urllib.parse")
    def test_full_linux_workflow(self, mock_urllib, mock_subprocess, mock_platform):
        """Test vollständiger Linux-Workflow."""
        mock_platform.return_value = "Linux"
        mock_urllib.urlencode.return_value = "subject=Test&body=Test"

        generator = OutlookMailGenerator()
        result = generator.create_outlook_mail(
            student_name="Weber, Julia",
            email_text="Test email für Linux",
            attachment_path=None,
            verbose=False,
        )

        assert result is True
        mock_subprocess.assert_called_once()


class TestEdgeCases:
    """Tests für Grenzfälle und spezielle Szenarien."""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    def test_empty_email_text(self, mock_platform):
        """Test mit leerem E-Mail-Text."""
        mock_platform.return_value = "Windows"
        mock_win32com = MagicMock()
        mock_win32com_client = MagicMock()
        mock_win32com.client = mock_win32com_client
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_win32com_client.Dispatch.return_value = mock_outlook
        mock_outlook.CreateItem.return_value = mock_mail

        with patch.dict(
            "sys.modules",
            {"win32com": mock_win32com, "win32com.client": mock_win32com_client},
        ):
            generator = OutlookMailGenerator()
            result = generator.create_outlook_mail(
                student_name="Test", email_text="", verbose=False
            )

            assert result is True
            assert mock_mail.Body == ""

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    def test_very_long_student_name(self, mock_platform):
        """Test mit sehr langem Studentennamen."""
        mock_platform.return_value = "Windows"
        mock_win32com = MagicMock()
        mock_win32com_client = MagicMock()
        mock_win32com.client = mock_win32com_client
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_win32com_client.Dispatch.return_value = mock_outlook
        mock_outlook.CreateItem.return_value = mock_mail

        long_name = "von und zu Testdoppelnamen-Mustermann, Maximilian Alexander"
        with patch.dict(
            "sys.modules",
            {"win32com": mock_win32com, "win32com.client": mock_win32com_client},
        ):
            generator = OutlookMailGenerator()
            result = generator.create_outlook_mail(
                student_name=long_name, email_text="Test", verbose=False
            )

            assert result is True
            assert long_name in mock_mail.Subject

    @patch("academic_doc_generator.colloquium.outlook_mail_generator.platform.system")
    def test_special_characters_in_email(self, mock_platform):
        """Test mit Sonderzeichen im E-Mail-Text."""
        mock_platform.return_value = "Windows"
        mock_win32com = MagicMock()
        mock_win32com_client = MagicMock()
        mock_win32com.client = mock_win32com_client
        mock_outlook = MagicMock()
        mock_mail = MagicMock()
        mock_win32com_client.Dispatch.return_value = mock_outlook
        mock_outlook.CreateItem.return_value = mock_mail

        special_text = "Test mit Umlauten: äöüß und Sonderzeichen: €@#"
        with patch.dict(
            "sys.modules",
            {"win32com": mock_win32com, "win32com.client": mock_win32com_client},
        ):
            generator = OutlookMailGenerator()
            result = generator.create_outlook_mail(
                student_name="Test", email_text=special_text, verbose=False
            )

            assert result is True
            assert mock_mail.Body == special_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
