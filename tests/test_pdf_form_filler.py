"""
Unit tests for src/academic_doc_generator/colloquium/pdf_form_filler.py
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from academic_doc_generator.colloquium import pdf_form_filler


class TestPDFFormHandler:
    """Tests für die PDFFormHandler-Klasse."""

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_init(self, mock_pymupdf):
        """Test Initialisierung des PDFFormHandler."""
        mock_doc = MagicMock()
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        mock_pymupdf.open.assert_called_once_with("test.pdf")
        assert handler.pdf_path == "test.pdf"
        assert handler.doc == mock_doc

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_del(self, mock_pymupdf):
        """Test dass Dokument beim Löschen geschlossen wird."""
        mock_doc = MagicMock()
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        del handler

        mock_doc.close.assert_called_once()

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_has_form_fields_true(self, mock_pymupdf):
        """Test has_form_fields gibt True zurück wenn Felder vorhanden."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        result = handler.has_form_fields()

        assert result is True

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_has_form_fields_false(self, mock_pymupdf):
        """Test has_form_fields gibt False zurück wenn keine Felder vorhanden."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.widgets.return_value = []
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        result = handler.has_form_fields()

        assert result is False

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_list_form_fields(self, mock_pymupdf):
        """Test list_form_fields extrahiert Feldinfo korrekt."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_widget.field_name = "test_field"
        mock_widget.field_type = mock_pymupdf.PDF_WIDGET_TYPE_TEXT
        mock_widget.field_value = "test_value"
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_TEXT = 1

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        fields = handler.list_form_fields()

        assert len(fields) == 1
        assert fields[0]["name"] == "test_field"
        assert fields[0]["value"] == "test_value"
        assert fields[0]["page"] == 1

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_list_form_fields_multiple_types(self, mock_pymupdf):
        """Test list_form_fields mit verschiedenen Feldtypen."""
        mock_doc = MagicMock()
        mock_page = MagicMock()

        # Text widget
        mock_text_widget = MagicMock()
        mock_text_widget.field_name = "text_field"
        mock_text_widget.field_type = 1  # PDF_WIDGET_TYPE_TEXT
        mock_text_widget.field_value = "text"

        # Checkbox widget
        mock_checkbox_widget = MagicMock()
        mock_checkbox_widget.field_name = "checkbox_field"
        mock_checkbox_widget.field_type = 2  # PDF_WIDGET_TYPE_CHECKBOX
        mock_checkbox_widget.field_value = True

        mock_page.widgets.return_value = [mock_text_widget, mock_checkbox_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_TEXT = 1
        mock_pymupdf.PDF_WIDGET_TYPE_CHECKBOX = 2

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        fields = handler.list_form_fields()

        assert len(fields) == 2
        assert fields[0]["name"] == "text_field"
        assert fields[0]["type"] == "Text"
        assert fields[1]["name"] == "checkbox_field"
        assert fields[1]["type"] == "Checkbox"

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    @patch("builtins.print")
    def test_print_form_fields_empty(self, mock_print, mock_pymupdf):
        """Test print_form_fields ohne Felder."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.widgets.return_value = []
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")
        handler.print_form_fields()

        # Prüfe dass Fehlermeldung gedruckt wurde
        assert any(
            "Keine Formularfelder gefunden" in str(call) for call in mock_print.call_args_list
        )

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_fill_form_text_field(self, mock_pymupdf):
        """Test fill_form mit Textfeld."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_widget.field_name = "test_field"
        mock_widget.field_type = 1  # PDF_WIDGET_TYPE_TEXT
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_TEXT = 1

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {"test_field": "new_value"}
        result = handler.fill_form(field_data, "/tmp/output.pdf", flatten=False)

        assert result is True
        assert mock_widget.field_value == "new_value"
        mock_widget.update.assert_called_once()
        mock_doc.save.assert_called_once()

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_fill_form_checkbox(self, mock_pymupdf):
        """Test fill_form mit Checkbox."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_widget.field_name = "checkbox_field"
        mock_widget.field_type = 2  # PDF_WIDGET_TYPE_CHECKBOX
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_CHECKBOX = 2

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {"checkbox_field": True}
        result = handler.fill_form(field_data, "/tmp/output.pdf")

        assert result is True
        assert mock_widget.field_value is True

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_fill_form_checkbox_string_value(self, mock_pymupdf):
        """Test fill_form mit Checkbox und String-Wert."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_widget.field_name = "checkbox_field"
        mock_widget.field_type = 2  # PDF_WIDGET_TYPE_CHECKBOX
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_CHECKBOX = 2

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {"checkbox_field": "1"}
        result = handler.fill_form(field_data, "/tmp/output.pdf")

        assert result is True
        assert mock_widget.field_value is True

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_fill_form_flatten(self, mock_pymupdf):
        """Test fill_form mit flatten=True."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.widgets.return_value = []
        mock_page.annots.return_value = []
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {}
        result = handler.fill_form(field_data, "/tmp/output.pdf", flatten=True)

        assert result is True
        mock_page.annots.assert_called_once()

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    @patch("builtins.print")
    def test_fill_form_field_not_found(self, mock_print, mock_pymupdf):
        """Test fill_form mit nicht existierendem Feld."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_widget = MagicMock()
        mock_widget.field_name = "existing_field"
        mock_widget.field_type = 1
        mock_page.widgets.return_value = [mock_widget]
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc
        mock_pymupdf.PDF_WIDGET_TYPE_TEXT = 1

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {"nonexistent_field": "value"}
        result = handler.fill_form(field_data, "/tmp/output.pdf")

        assert result is True
        # Prüfe dass Warnung gedruckt wurde
        assert any("nicht im PDF gefunden" in str(call) for call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.pdf_form_filler.pymupdf")
    def test_fill_form_exception(self, mock_pymupdf):
        """Test fill_form mit Exception."""
        mock_doc = MagicMock()
        mock_doc.save.side_effect = Exception("Save failed")
        mock_page = MagicMock()
        mock_page.widgets.return_value = []
        mock_doc.__iter__.return_value = [mock_page]
        mock_pymupdf.open.return_value = mock_doc

        handler = pdf_form_filler.PDFFormHandler("test.pdf")

        field_data = {}
        result = handler.fill_form(field_data, "/tmp/output.pdf")

        assert result is False


class TestHelperFunctions:
    """Tests für Hilfsfunktionen."""

    def test_berechne_gesamtnote(self):
        """Test berechne_gesamtnote."""
        assert pdf_form_filler.berechne_gesamtnote(1.0, 2.0) == 1.5
        assert pdf_form_filler.berechne_gesamtnote(1.3, 1.7) == 1.5
        assert pdf_form_filler.berechne_gesamtnote(2.3, 2.7) == 2.5

    def test_berechne_gesamtnote_rounding(self):
        """Test berechne_gesamtnote Rundung.

        Python's round() verwendet "banker's rounding" (round half to even):
        - 1.65 wird zu 1.6 gerundet (gerade Zahl)
        - 1.75 wird zu 1.8 gerundet (gerade Zahl)
        - 1.35 wird zu 1.4 gerundet (gerade Zahl)
        - 1.45 wird zu 1.4 gerundet (gerade Zahl)
        """
        assert pdf_form_filler.berechne_gesamtnote(1.0, 2.3) == 1.6  # (1.0 + 2.3) / 2 = 1.65 -> 1.6
        assert (
            pdf_form_filler.berechne_gesamtnote(1.3, 1.4) == 1.4
        )  # (1.3 + 1.4) / 2 = 1.35 -> 1.4 (bereits 1.4)
        assert pdf_form_filler.berechne_gesamtnote(1.0, 1.9) == 1.4  # (1.0 + 1.9) / 2 = 1.45 -> 1.4
        assert (
            pdf_form_filler.berechne_gesamtnote(2.0, 2.1) == 2.0
        )  # (2.0 + 2.1) / 2 = 2.05 -> 2.1 (wird zu 2.0 gerundet, aber dann auf 1 Stelle)

    def test_add_minutes(self):
        """Test add_minutes."""
        assert pdf_form_filler.add_minutes("10:00", 45) == "10:45"
        assert pdf_form_filler.add_minutes("14:30", 30) == "15:00"
        assert pdf_form_filler.add_minutes("23:30", 45) == "00:15"  # Über Mitternacht

    def test_add_minutes_negative(self):
        """Test add_minutes mit negativer Minutenzahl."""
        assert pdf_form_filler.add_minutes("10:00", -30) == "09:30"

    def test_generate_location_text_campus(self):
        """Test generate_location_text für Campus."""
        result = pdf_form_filler.generate_location_text(location_type="campus", room="3.217")
        assert result == "Raum 3.217, Campus Gummersbach"

    def test_generate_location_text_campus_no_room(self):
        """Test generate_location_text für Campus ohne Raum."""
        with pytest.raises(ValueError, match="'room' benötigt"):
            pdf_form_filler.generate_location_text(location_type="campus")

    def test_generate_location_text_company(self):
        """Test generate_location_text für Firma."""
        result = pdf_form_filler.generate_location_text(
            location_type="company", company_name="Beispiel GmbH"
        )
        assert result == "Beispiel GmbH"

    def test_generate_location_text_company_no_name(self):
        """Test generate_location_text für Firma ohne Namen."""
        with pytest.raises(ValueError, match="'company_name' benötigt"):
            pdf_form_filler.generate_location_text(location_type="company")

    def test_generate_location_text_online(self):
        """Test generate_location_text für Online."""
        result = pdf_form_filler.generate_location_text(location_type="online")
        assert result == "Zoom"

    def test_generate_location_text_invalid_type(self):
        """Test generate_location_text mit ungültigem Typ."""
        with pytest.raises(ValueError, match="Unbekannter location_type"):
            pdf_form_filler.generate_location_text(location_type="invalid")


class TestFillForm:
    """Tests für die fill_form Funktion."""

    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.generate_location_text")
    @patch("builtins.print")
    def test_fill_form_bachelor_campus(self, mock_print, mock_gen_loc, mock_handler_class):
        """Test fill_form für Bachelor-Arbeit auf Campus."""
        mock_gen_loc.return_value = "Raum 3.217, Campus Gummersbach"
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        data = {
            "name_student": "Max Mustermann",
            "MatrNr": "12345",
            "Startzeit": "14:00",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf_form_filler.fill_form(
                data, tmpdir, "Bachelor", location_type="campus", room="3.217"
            )

            assert result is not None
            mock_handler.fill_form.assert_called_once()
            call_args = mock_handler.fill_form.call_args[0]
            assert call_args[0]["Ort"] == "Raum 3.217, Campus Gummersbach"
            assert call_args[0]["Endzeit"] == "14:45"

    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.generate_location_text")
    def test_fill_form_master_company(self, mock_gen_loc, mock_handler_class):
        """Test fill_form für Master-Arbeit in Firma."""
        mock_gen_loc.return_value = "Beispiel GmbH"
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        data = {
            "name_student": "Maria Musterfrau",
            "MatrNr": "67890",
            "Startzeit": "10:00",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pdf_form_filler.fill_form(
                data,
                tmpdir,
                "Master",
                location_type="company",
                company_name="Beispiel GmbH",
            )

            assert result is not None
            # Prüfe dass Master-PDF verwendet wurde
            call_args = mock_handler_class.call_args[0]
            assert "Masterarbeit" in call_args[0]

    @patch("builtins.print")
    def test_fill_form_unknown_degree(self, mock_print):
        """Test fill_form mit unbekanntem Abschluss."""
        data = {"name_student": "Test"}

        result = pdf_form_filler.fill_form(
            data, "/tmp", "Unknown", location_type="campus", room="3.217"
        )

        assert result is None
        assert any("Unknown degree" in str(call) for call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.pdf_form_filler.Path")
    @patch("builtins.print")
    def test_fill_form_pdf_not_found(self, mock_print, mock_path_class):
        """Test fill_form wenn PDF nicht gefunden wird."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        data = {"name_student": "Test"}

        result = pdf_form_filler.fill_form(
            data, "/tmp", "Bachelor", location_type="campus", room="3.217"
        )

        assert result is None

    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.generate_location_text")
    @patch("builtins.print")
    def test_fill_form_location_error(self, mock_print, mock_gen_loc, mock_handler_class):
        """Test fill_form mit Fehler bei Location-Generierung."""
        mock_gen_loc.side_effect = ValueError("Location error")

        data = {"name_student": "Test", "Startzeit": "14:00"}

        result = pdf_form_filler.fill_form(data, "/tmp", "Bachelor", location_type="campus")

        assert result is None


class TestMain:
    """Tests für die main-Funktion."""

    @patch("academic_doc_generator.colloquium.pdf_form_filler.Path")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("builtins.print")
    def test_main_pdf_not_found(self, mock_print, mock_handler_class, mock_path_class):
        """Test main wenn PDF nicht existiert."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        pdf_form_filler.main()

        assert any("Datei nicht gefunden" in str(call) for call in mock_print.call_args_list)

    @patch("academic_doc_generator.colloquium.pdf_form_filler.Path")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("builtins.print")
    def test_main_with_form_fields(self, mock_print, mock_handler_class, mock_path_class):
        """Test main mit Formularfeldern."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        mock_handler = MagicMock()
        mock_handler.has_form_fields.return_value = True
        mock_handler.fill_form.return_value = True
        mock_handler_class.return_value = mock_handler

        pdf_form_filler.main()

        mock_handler.has_form_fields.assert_called_once()
        mock_handler.print_form_fields.assert_called_once()
        mock_handler.fill_form.assert_called_once()

    @patch("academic_doc_generator.colloquium.pdf_form_filler.Path")
    @patch("academic_doc_generator.colloquium.pdf_form_filler.PDFFormHandler")
    @patch("builtins.print")
    def test_main_without_form_fields(self, mock_print, mock_handler_class, mock_path_class):
        """Test main ohne Formularfelder."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        mock_handler = MagicMock()
        mock_handler.has_form_fields.return_value = False
        mock_handler_class.return_value = mock_handler

        pdf_form_filler.main()

        mock_handler.has_form_fields.assert_called_once()
        assert any("KEINE ausfüllbaren" in str(call) for call in mock_print.call_args_list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
