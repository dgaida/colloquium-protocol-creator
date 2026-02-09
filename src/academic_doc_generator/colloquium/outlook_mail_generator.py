"""Modul zur automatischen Erstellung von Outlook-Mails für Kolloquiums-Anmeldungen."""

import os
import platform
import subprocess
from typing import Optional
import traceback
import urllib.parse


class OutlookMailGenerator:
    """Erstellt automatisch Outlook-Mails für Kolloquiums-Anmeldungen."""

    RECIPIENT_EMAIL = "studium-gm@th-koeln.de"

    def __init__(self):
        """Initialisiert den OutlookMailGenerator."""
        pass

    @staticmethod
    def is_outlook_open() -> bool:
        """Prüft, ob Outlook aktuell geöffnet ist.

        Returns:
            True wenn Outlook läuft, sonst False.
        """
        import subprocess

        system = platform.system()
        try:
            if system == "Windows":
                # Prüfe mit tasklist unter Windows
                output = subprocess.check_output(
                    'tasklist /FI "IMAGENAME eq outlook.exe"',
                    shell=True,
                    stderr=subprocess.STDOUT,
                )
                return b"outlook.exe" in output.lower()
            elif system == "Darwin":  # macOS
                # Prüfe mit pgrep unter macOS
                try:
                    subprocess.check_call(["pgrep", "-x", "Microsoft Outlook"])
                    return True
                except subprocess.CalledProcessError:
                    return False
            else:
                return False
        except Exception:
            return False

    def create_outlook_mail(
        self,
        stud_name: str,
        email_text: str,
        attachment_path: Optional[str] = None,
        verbose: bool = False,
        subject: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> bool:
        """Erstellt eine neue Outlook-Mail mit vorausgefülltem Inhalt.

        Args:
            stud_name: Name des Studierenden (für Betreff).
            email_text: Kompletter E-Mail-Text.
            attachment_path: Pfad zur Datei, die als Anhang hinzugefügt werden soll.
            verbose: Debug-Ausgaben aktivieren.
            subject: Optionaler Betreff. Falls None, wird ein Standardbetreff erstellt.
            recipient: E-Mail-Empfänger. Falls None, wird RECIPIENT_EMAIL verwendet.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        if subject is None:
            subject = f"Anmeldung Kolloquium {stud_name}"

        if recipient is None:
            recipient = self.RECIPIENT_EMAIL

        try:
            system = platform.system()

            if system == "Windows":
                return self._create_outlook_mail_windows(
                    subject, email_text, attachment_path, verbose, recipient
                )
            elif system == "Darwin":  # macOS
                return self._create_outlook_mail_macos(
                    subject, email_text, attachment_path, verbose, recipient
                )
            elif system == "Linux":
                return self._create_outlook_mail_linux(
                    subject, email_text, attachment_path, verbose, recipient
                )
            else:
                print(f"⚠️  Plattform '{system}' wird nicht unterstützt")
                return False

        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler beim Erstellen der Outlook-Mail: {e}")
                traceback.print_exc()
            return False

    def open_ics_in_outlook(self, ics_file_path: str, verbose: bool = False) -> bool:
        """Öffnet eine ICS-Datei direkt in Outlook (nur Windows).

        Args:
            ics_file_path: Pfad zur ICS-Datei.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            system = platform.system()

            if system == "Windows":
                # Öffne ICS-Datei mit Standard-Anwendung (Outlook)
                os.startfile(ics_file_path)  # type: ignore[attr-defined]
                print("✅ ICS-Datei in Outlook geöffnet")
                return True
            else:
                if verbose:
                    print(
                        "ℹ️  Direktes Öffnen in Outlook nur unter Windows unterstützt"
                    )
                return False

        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler beim Öffnen der ICS-Datei: {e}")
                traceback.print_exc()
            return False

    def _create_outlook_mail_windows(
        self,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        verbose: bool = False,
        recipient: Optional[str] = None,
    ) -> bool:
        """Erstellt Outlook-Mail unter Windows mit COM-Automation.

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            attachment_path: Pfad zur Datei als Anhang.
            verbose: Debug-Ausgaben aktivieren.
            recipient: E-Mail-Empfänger.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            import win32com.client

            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            mail.To = recipient if recipient else self.RECIPIENT_EMAIL
            mail.Subject = subject
            mail.Body = body

            # Füge Anhang hinzu
            if attachment_path:
                if os.path.exists(attachment_path):
                    mail.Attachments.Add(os.path.abspath(attachment_path))
                    if verbose:
                        print(f"✅ Datei als Anhang hinzugefügt: {attachment_path}")
                else:
                    print(f"⚠️  Datei nicht gefunden: {attachment_path}")

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
                traceback.print_exc()
            return False

    def _create_outlook_mail_macos(
        self,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        verbose: bool = False,
        recipient: Optional[str] = None,
    ) -> bool:
        """Erstellt Outlook-Mail unter macOS mit AppleScript.

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            attachment_path: Pfad zur Datei als Anhang.
            verbose: Debug-Ausgaben aktivieren.
            recipient: E-Mail-Empfänger.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            # Escape Anführungszeichen und Backslashes für AppleScript
            escaped_subject = subject.replace('"', '\\"').replace("\\", "\\\\")
            escaped_body = body.replace('"', '\\"').replace("\\", "\\\\")
            final_recipient = recipient if recipient else self.RECIPIENT_EMAIL
            escaped_recipient = final_recipient.replace('"', '\\"')

            # Basis-AppleScript
            applescript = f"""
            tell application "Microsoft Outlook"
                set newMessage to make new outgoing message with properties {{subject:"{escaped_subject}", content:"{escaped_body}"}}
                make new recipient at newMessage with properties {{email address:{{address:"{escaped_recipient}"}}}}
            """

            # Füge Anhang hinzu, falls vorhanden
            if attachment_path:
                if os.path.exists(attachment_path):
                    escaped_path = attachment_path.replace('"', '\\"').replace(
                        "\\", "\\\\"
                    )
                    applescript += f"""
                make new attachment at newMessage with properties {{file:POSIX file "{escaped_path}"}}
                """
                    if verbose:
                        print(f"✅ Datei als Anhang hinzugefügt: {attachment_path}")

            applescript += """
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
                traceback.print_exc()
            return False

    def _create_outlook_mail_linux(
        self,
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        verbose: bool = False,
        recipient: Optional[str] = None,
    ) -> bool:
        """Erstellt Mail-Link unter Linux (Outlook Web/xdg-open).

        Args:
            subject: E-Mail-Betreff.
            body: E-Mail-Text.
            attachment_path: Pfad zur Datei (wird unter Linux ignoriert).
            verbose: Debug-Ausgaben aktivieren.
            recipient: E-Mail-Empfänger.

        Returns:
            True wenn erfolgreich, False bei Fehler.
        """
        try:
            # Erstelle mailto-Link
            params = {"subject": subject, "body": body}
            final_recipient = recipient if recipient else self.RECIPIENT_EMAIL
            mailto_link = f"mailto:{final_recipient}?{urllib.parse.urlencode(params)}"

            # Öffne mit Standard-Mail-Client
            subprocess.run(["xdg-open", mailto_link], check=True)

            if attachment_path and verbose:
                print(
                    "ℹ️  Anhänge werden unter Linux nicht automatisch hinzugefügt. Bitte manuell anhängen."
                )

            print("✅ Standard-Mail-Client geöffnet (bitte manuell absenden)")
            return True

        except subprocess.CalledProcessError:
            if verbose:
                print("⚠️  Konnte Standard-Mail-Client nicht öffnen")
            return False
        except Exception as e:
            if verbose:
                print(f"⚠️  Fehler bei Linux Mail: {e}")

                traceback.print_exc()
            return False
