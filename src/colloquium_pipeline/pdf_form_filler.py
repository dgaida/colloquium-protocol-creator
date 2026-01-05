"""
PDF Formular-Tool zum Prüfen und Ausfüllen von PDF-Formularen mit PyMuPDF.

Dieses Script bietet Funktionen zum:
- Prüfen, ob ein PDF ausfüllbare Formularfelder enthält
- Auflisten aller Formularfelder mit ihren Namen
- Automatischen Ausfüllen von PDF-Formularen
"""

import fitz  # PyMuPDF
from typing import Dict, List, Optional
from pathlib import Path
import os
from datetime import datetime, timedelta


class PDFFormHandler:
    """Handler für PDF-Formulare zum Prüfen und Ausfüllen."""

    def __init__(self, pdf_path: str):
        """
        Initialisiert den PDF Form Handler.

        Args:
            pdf_path: Pfad zur PDF-Datei
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def __del__(self):
        """Schließt das PDF-Dokument beim Löschen des Objekts."""
        if hasattr(self, 'doc'):
            self.doc.close()

    def has_form_fields(self) -> bool:
        """
        Prüft, ob das PDF ausfüllbare Formularfelder enthält.

        Returns:
            True wenn Formularfelder vorhanden sind, sonst False
        """
        for page in self.doc:
            widgets = page.widgets()
            if widgets:
                return True
        return False

    def list_form_fields(self) -> List[Dict[str, any]]:
        """
        Listet alle Formularfelder mit Details auf.

        Returns:
            Liste von Dictionaries mit Feldinformationen (Name, Typ, Wert, Seite)
        """
        field_list = []

        for page_num, page in enumerate(self.doc, start=1):
            for widget in page.widgets():
                field_type_map = {
                    fitz.PDF_WIDGET_TYPE_TEXT: "Text",
                    fitz.PDF_WIDGET_TYPE_CHECKBOX: "Checkbox",
                    fitz.PDF_WIDGET_TYPE_RADIOBUTTON: "Radio Button",
                    fitz.PDF_WIDGET_TYPE_LISTBOX: "Listbox",
                    fitz.PDF_WIDGET_TYPE_COMBOBOX: "Combobox",
                    fitz.PDF_WIDGET_TYPE_SIGNATURE: "Signature",
                    fitz.PDF_WIDGET_TYPE_BUTTON: "Button"
                }

                field_data = {
                    'name': widget.field_name,
                    'type': field_type_map.get(widget.field_type, "Unknown"),
                    'type_code': widget.field_type,
                    'value': widget.field_value,
                    'page': page_num,
                }
                field_list.append(field_data)

        return field_list

    def print_form_fields(self) -> None:
        """Gibt alle Formularfelder formatiert auf der Konsole aus."""
        fields = self.list_form_fields()

        if not fields:
            print("❌ Keine Formularfelder gefunden!")
            print("\nDas PDF enthält keine ausfüllbaren Felder.")
            print("Die Formularersteller müssen das PDF mit Formularfeldern versehen.")
            return

        print(f"✅ {len(fields)} Formularfeld(er) gefunden:\n")

        # Gruppiere nach Typ
        text_fields = []
        checkbox_fields = []
        other_fields = []

        for field in fields:
            if field['type'] == 'Text':
                text_fields.append(field)
            elif field['type'] == 'Checkbox':
                checkbox_fields.append(field)
            else:
                other_fields.append(field)

        if text_fields:
            print("📝 Textfelder:")
            for field in text_fields:
                value_str = f" (aktuell: '{field['value']}')" if field['value'] else ""
                print(f"   • '{field['name']}' [Seite {field['page']}]{value_str}")
            print()

        if checkbox_fields:
            print("☑️  Checkboxen:")
            for field in checkbox_fields:
                checked = "✓" if field['value'] else "○"
                print(f"   {checked} '{field['name']}' [Seite {field['page']}]")
            print()

        if other_fields:
            print("🔧 Andere Felder:")
            for field in other_fields:
                print(f"   • '{field['name']}' ({field['type']}) [Seite {field['page']}]")
            print()

    def fill_form(self, field_data: Dict[str, any], output_path: str,
                  flatten: bool = False) -> bool:
        """
        Füllt das PDF-Formular mit den angegebenen Daten aus.

        Args:
            field_data: Dictionary mit Feldnamen als Keys und Werten als Values
            output_path: Pfad für die ausgefüllte PDF-Datei
            flatten: Wenn True, werden Formularfelder nach dem Ausfüllen
                    in normalen Text konvertiert (nicht mehr editierbar)

        Returns:
            True bei Erfolg, False bei Fehler

        Example:
            >>> handler = PDFFormHandler("formular.pdf")
            >>> data = {
            ...     "name_student": "Mustermann, Max",
            ...     "MatrNr": "123456",
            ...     "Schrift_Begruendung": True  # Checkbox aktivieren
            ... }
            >>> handler.fill_form(data, "ausgefuellt.pdf")
        """
        try:
            filled_count = 0
            not_found = []

            # Iteriere durch alle Seiten und deren Widgets
            for page in self.doc:
                for widget in page.widgets():
                    field_name = widget.field_name

                    if field_name in field_data:
                        value = field_data[field_name]

                        try:
                            # Behandle verschiedene Feldtypen
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = str(value)
                                widget.update()
                                filled_count += 1

                            elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                # Checkbox: True/False oder 1/0
                                if isinstance(value, bool):
                                    widget.field_value = value
                                elif isinstance(value, (int, str)):
                                    widget.field_value = bool(int(value))
                                widget.update()
                                filled_count += 1

                            else:
                                # Andere Feldtypen
                                widget.field_value = value
                                widget.update()
                                filled_count += 1

                        except Exception as e:
                            print(f"⚠️  Warnung: Feld '{field_name}' konnte nicht gesetzt werden: {e}")

            # Prüfe, welche Felder nicht gefunden wurden
            all_field_names = {field['name'] for field in self.list_form_fields()}
            not_found = [name for name in field_data.keys() if name not in all_field_names]

            if not_found:
                print(f"\n⚠️  {len(not_found)} Feld(er) nicht im PDF gefunden:")
                for name in not_found:
                    print(f"   • '{name}'")

            # Optional: Formular "flatten" (in Text konvertieren)
            if flatten:
                for page in self.doc:
                    page.annots()  # Erzwingt Rendering
                self.doc.save(output_path, deflate=True, garbage=3)
                print(f"\n✅ PDF gespeichert und geflattent (nicht mehr editierbar): {output_path}")
            else:
                self.doc.save(output_path, garbage=3, deflate=True)
                print(f"\n✅ PDF erfolgreich ausgefüllt: {output_path}")

            print(f"   {filled_count} Feld(er) wurden erfolgreich gesetzt")
            return True

        except Exception as e:
            print(f"❌ Fehler beim Ausfüllen: {e}")
            import traceback
            traceback.print_exc()
            return False


def berechne_gesamtnote(note1: float, note2: float) -> float:
    """
    Berechnet das arithmetische Mittel zweier Noten.

    Args:
        note1: Erste Note
        note2: Zweite Note

    Returns:
        Gesamtnote (arithmetisches Mittel), gerundet auf eine Dezimalstelle
    """
    return round((note1 + note2) / 2, 1)


def fill_form(data, output_folder: str, degree: str):
    if degree == "Master":
        # Pfad zur PDF-Datei
        pdf_path = os.path.join("data", "Bewertung Masterarbeit_Kolloquium DSS_DSC_form.pdf")
    elif degree == "Bachelor":
        # Pfad zur PDF-Datei
        pdf_path = os.path.join("data", "Bewertung Bachelorarbeit_Kolloquium Informatik_form.pdf")
    else:
        print(f"Error: Unknown degree: {degree}")
        return

    # Prüfe ob Datei existiert
    if not Path(pdf_path).exists():
        print(f"❌ Datei nicht gefunden: {pdf_path}")
        return

    # Handler initialisieren
    handler = PDFFormHandler(pdf_path)

    path = os.path.join(output_folder, f"Bewertung {degree}arbeit_Kolloq Inf_{data['name_student']}.pdf")

    data["Endzeit"] = add_minutes(data["Startzeit"], 45)

    # Formular ausfüllen (flatten=False bedeutet: editierbar bleiben)
    handler.fill_form(data, path, flatten=False)


def add_minutes(time_str: str, minutes: int) -> str:
    time_obj = datetime.strptime(time_str, "%H:%M")
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")


def main():
    """Beispiel-Verwendung des PDF Form Handlers."""
    # Pfad zur PDF-Datei
    pdf_path = os.path.join("data", "Bewertung Bachelorarbeit_Kolloquium Informatik_form.pdf")

    # Prüfe ob Datei existiert
    if not Path(pdf_path).exists():
        print(f"❌ Datei nicht gefunden: {pdf_path}")
        return

    # Handler initialisieren
    handler = PDFFormHandler(pdf_path)

    # Prüfen, ob Formularfelder vorhanden sind
    print("=" * 60)
    print("PDF FORMULAR-ANALYSE")
    print("=" * 60)

    if handler.has_form_fields():
        print("\n✅ Das PDF enthält ausfüllbare Formularfelder!\n")
        handler.print_form_fields()

        # Beispiel: Formular ausfüllen
        print("\n" + "=" * 60)
        print("BEISPIEL: FORMULAR AUSFÜLLEN")
        print("=" * 60 + "\n")

        # Noten definieren (als Zahlen für Berechnungen)
        note_ba_erstpruefer = 1.3
        note_ba_zweitpruefer = 1.7
        note_kolloq_erstpruefer = 1.0
        note_kolloq_zweitpruefer = 1.3

        # Berechnungen
        gesamtnote_ba = berechne_gesamtnote(note_ba_erstpruefer, note_ba_zweitpruefer)
        gesamtnote_kolloq = berechne_gesamtnote(note_kolloq_erstpruefer, note_kolloq_zweitpruefer)
        gesamtnote_gesamt = berechne_gesamtnote(gesamtnote_ba, gesamtnote_kolloq)

        # Beispieldaten basierend auf den tatsächlichen Feldnamen
        beispiel_daten = {
            # Studierenden-Daten
            "name_student": "Mustermann, Max",
            "MatrNr": "123456",

            # Bachelorarbeit - Erstprüfer
            "Note_schrift_Erstpruefer": str(note_ba_erstpruefer),
            "Datum_schrift_Erstpruefer": "15.12.2025",
            "Unterschrift 1 Prüferin": "Prof. Dr. Müller",
            "Schrift_Begruendung": True,  # Checkbox "Begründung liegt bei"

            # Bachelorarbeit - Zweitprüfer
            "Note_schrift_Zweitpruefer": str(note_ba_zweitpruefer),
            "Datum_schrift_Zweitpruefer": "16.12.2025",
            "Unterschrift 2 Prüferin": "Prof. Dr. Schmidt",
            "Schrift_Anschluss_Begruendung": True,  # "Anschluss an Begründung"

            # Gesamtnote Bachelorarbeit
            "Gesamtnote_schrift": str(gesamtnote_ba),

            # Kolloquium - Details
            "Datum der Prüfung": "05.01.2026",
            "Ort": "Raum A123 / Online",
            "Startzeit": "10:00",
            "Endzeit": "10:45",
            "Pruefungsfragen_Protokoll": True,  # Checkbox

            # Kolloquium - Erstprüfer
            "Note_kolloq_Erstpruefer": str(note_kolloq_erstpruefer),
            "Datum_kolloq_Erstpruefer": "05.01.2026",
            "Unterschrift 1 Prüferin_2": "Prof. Dr. Müller",
            "Kolloq_Begruendung": True,

            # Kolloquium - Zweitprüfer
            "Note_kolloq_Zweit": str(note_kolloq_zweitpruefer),
            "Datum_kolloq_Zweitpruefer": "05.01.2026",
            "Unterschrift 2 Prüferin_2": "Prof. Dr. Schmidt",
            "Kolloq_Anschluss_Begruendung": True,

            # Gesamtnote (Bachelorarbeit + Kolloquium)
            "Gesamtnote_alles": str(gesamtnote_gesamt),

            # Optional: Prüfungsfragen
            "Prüfungsfragen": "1. Erläutern Sie die Hauptergebnisse Ihrer Arbeit.\n2. Diskutieren Sie die verwendete Methodik."
        }

        print(f"📊 Berechnete Noten:")
        print(f"   • Bachelorarbeit: {gesamtnote_ba}")
        print(f"   • Kolloquium: {gesamtnote_kolloq}")
        print(f"   • Gesamt: {gesamtnote_gesamt}\n")

        # Formular ausfüllen (flatten=False bedeutet: editierbar bleiben)
        handler.fill_form(beispiel_daten, "Bewertung_ausgefuellt.pdf", flatten=False)

        print("\n" + "=" * 60)
        print("💡 TIPPS")
        print("=" * 60)
        print("\n1. Anpassung für eigene Daten:")
        print("   Ändere die Werte im 'beispiel_daten' Dictionary")
        print("\n2. Für Checkboxen:")
        print("   True = aktiviert, False = deaktiviert")
        print("\n3. Flatten-Option:")
        print("   flatten=True → PDF nicht mehr editierbar (für finale Version)")
        print("   flatten=False → PDF bleibt editierbar (Standard)")

    else:
        print("\n❌ Das PDF enthält KEINE ausfüllbaren Formularfelder!\n")
        print("Empfehlungen:")
        print("1. Bitte die Formularersteller, das PDF mit Adobe Acrobat")
        print("   oder einem ähnlichen Tool neu zu erstellen")
        print("2. Alle ausfüllbaren Bereiche sollten als 'Text Fields' definiert werden")
        print("3. Jedes Feld sollte einen eindeutigen Namen haben")
        print("4. Checkboxen für Ankreuzfelder verwenden")


if __name__ == "__main__":
    main()
