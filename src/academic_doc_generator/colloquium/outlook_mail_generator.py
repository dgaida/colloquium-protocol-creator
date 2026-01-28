"""Modul zur automatischen Erstellung von Outlook-Mails für Kolloquiums-Anmeldungen."""

import platform
import subprocess
from typing import Optional


class OutlookMailGenerator:
    """Erstellt automatisch Outlook-Mails für Kolloquiums-Anmeldungen."""

    RECIPIENT_EMAIL = "studium-gm@th-koeln.de"

    def __init__(self):
        """Initialisiert den OutlookMailGenerator."""
        pass

    def create_outlook_mail(
        self,
        student_name: str,
        email_text: str,
        verbose: bool = False,
    ) -> bool:
        """Erstellt eine neue Outlook-Mail mit vorausgefülltem Inhalt.

        Args:
            student_name: Name des Studierenden (für Betreff).
            email_text: Kompletter E-Mail-Text.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        subject = f"Anmeldung Kolloquium {student_name}"

        try:
            system = platform.system()

            if system == "Windows":
                return self._create_outlook_mail_windows(subject, email_text, verbose)
            elif system == "Darwin":  # macOS
                return self._create_outlook_mail_macos(subject, email_text, verbose)
            elif system == "Linux":
                return self._create_outlook_mail_linux(subject, email_text, verbose)
            else:
                print(f"⚠️  Plattform '{system}' wird nicht unterstützt")
                return False

        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler beim Erstellen der Outlook-Mail: {e}")
                import traceback
                traceback.print_exc()
            return False

    def _create_outlook_mail_windows(
        self, subject: str, body: str, verbose: bool = False
    ) -> bool:
        """Erstellt Outlook-Mail unter Windows mit COM-Automation.

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            import win32com.client

            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            mail.To = self.RECIPIENT_EMAIL
            mail.Subject = subject
            mail.Body = body

            # Mail anzeigen (nicht senden!)
            mail.Display(False)

            print("✅ Outlook-Mail erstellt und geöffnet (bitte manuell absenden)")
            return True

        except ImportError:
            print("⚠️  pywin32 nicht installiert. Installiere mit: pip install pywin32")
            return False
        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler bei Windows Outlook: {e}")
                import traceback
                traceback.print_exc()
            return False

    def _create_outlook_mail_macos(
        self, subject: str, body: str, verbose: bool = False
    ) -> bool:
        """Erstellt Outlook-Mail unter macOS mit AppleScript.

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            # Escape Anführungszeichen und Backslashes für AppleScript
            escaped_subject = subject.replace('"', '\\"').replace("\\", "\\\\")
            escaped_body = body.replace('"', '\\"').replace("\\", "\\\\")
            escaped_recipient = self.RECIPIENT_EMAIL.replace('"', '\\"')

            applescript = f"""
            tell application "Microsoft Outlook"
                set newMessage to make new outgoing message with properties {{subject:"{escaped_subject}", content:"{escaped_body}"}}
                make new recipient at newMessage with properties {{email address:{{address:"{escaped_recipient}"}}}}
                open newMessage
                activate
            end tell
            """

            subprocess.run(["osascript", "-e", applescript], check=True)
            print("✅ Outlook-Mail erstellt und geöffnet (bitte manuell absenden)")
            return True

        except subprocess.CalledProcessError as e:
            if verbose:
                print(f"⚠️  Fehler bei macOS Outlook: {e}")
            return False
        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler bei macOS Outlook: {e}")
                import traceback
                traceback.print_exc()
            return False

    def _create_outlook_mail_linux(
        self, subject: str, body: str, verbose: bool = False
    ) -> bool:
        """Erstellt Mail-Link unter Linux (Outlook Web/xdg-open).

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            import urllib.parse

            # Erstelle mailto-Link
            params = {"subject": subject, "body": body}
            mailto_link = f"mailto:{self.RECIPIENT_EMAIL}?{urllib.parse.urlencode(params)}"

            # Öffne mit Standard-Mail-Client
            subprocess.run(["xdg-open", mailto_link], check=True)

            print("✅ Standard-Mail-Client geöffnet (bitte manuell absenden)")
            return True

        except subprocess.CalledProcessError:
            if verbose:
                print("⚠️  Konnte Standard-Mail-Client nicht öffnen")
            return False
        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler bei Linux Mail: {e}")
                import traceback
                traceback.print_exc()
            return False
