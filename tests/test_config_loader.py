"""
Unit tests for config_loader.py
"""

import json
import tempfile
from pathlib import Path

import pytest

from academic_doc_generator.config_loader import ConfigLoader, load_config


class TestConfigLoader:
    """Tests für den ConfigLoader."""

    def create_config_in_tmpdir(self, tmpdir, config_data, create_pdf=True):
        """Hilfsfunktion zum Erstellen einer Config mit optionaler PDF-Datei."""
        if create_pdf and "pdf" in config_data and "filename" in config_data["pdf"]:
            pdf_file = Path(tmpdir) / config_data["pdf"]["filename"]
            pdf_file.write_text("dummy")

        config_path = Path(tmpdir) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        return config_path

    def test_load_valid_colloquium_campus_config(self):
        """Test laden einer validen Campus-Kolloquium-Konfiguration."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "20.01.2026",
                "time": "14:00",
                "location_type": "campus",
                "room": "3.217",
            },
            "llm": {"api_choice": None, "model": None},
            "output": {"folder": None, "compile_pdf": True},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))

            assert config.get_task() == "colloquium"
            assert config.get_pdf_path().endswith("test.pdf")

            coll_config = config.get_colloquium_config()
            assert coll_config["date"] == "20.01.2026"
            assert coll_config["time"] == "14:00"
            assert coll_config["location_type"] == "campus"
            assert coll_config["room"] == "3.217"

    def test_load_valid_colloquium_company_config(self):
        """Test laden einer validen Firmen-Kolloquium-Konfiguration."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "25.01.2026",
                "time": "10:00",
                "location_type": "company",
                "company_name": "Beispiel GmbH",
                "company_address": "Musterstraße 42",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))
            coll_config = config.get_colloquium_config()

            assert coll_config["location_type"] == "company"
            assert coll_config["company_name"] == "Beispiel GmbH"
            assert coll_config["company_address"] == "Musterstraße 42"

    def test_load_valid_colloquium_online_config(self):
        """Test laden einer validen Online-Kolloquium-Konfiguration."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "30.01.2026",
                "time": "15:30",
                "location_type": "online",
                "zoom_link": "https://zoom.us/j/123456",
                "zcode": "test123",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))
            coll_config = config.get_colloquium_config()

            assert coll_config["location_type"] == "online"
            assert coll_config["zoom_link"] == "https://zoom.us/j/123456"
            assert coll_config["zcode"] == "test123"

    def test_load_valid_project_config(self):
        """Test laden einer validen Projektarbeits-Konfiguration."""
        config_data = {
            "task": "project",
            "pdf": {"filename": "project.pdf"},
            "llm": {"api_choice": "openai", "model": "gpt-4o"},
            "output": {"signature_file": "sig.png"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))

            assert config.get_task() == "project"
            llm_config = config.get_llm_config()
            assert llm_config["api_choice"] == "openai"
            assert llm_config["model"] == "gpt-4o"

            output_config = config.get_output_config()
            assert output_config["signature_file"] == "sig.png"

    def test_load_valid_review_config(self):
        """Test laden einer validen Review-Konfiguration."""
        config_data = {
            "task": "review",
            "pdf": {"filename": "paper.pdf"},
            "llm": {"groq_free": True},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))

            assert config.get_task() == "review"
            llm_config = config.get_llm_config()
            assert llm_config["groq_free"] is True

    def test_invalid_task(self):
        """Test Fehler bei ungültigem Task."""
        config_data = {"task": "invalid_task", "pdf": {"filename": "test.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="Ungültiger Task"):
                ConfigLoader(str(tmpdir))

    def test_missing_pdf_section(self):
        """Test Fehler bei fehlender PDF-Sektion."""
        config_data = {"task": "colloquium"}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data, create_pdf=False)

            with pytest.raises(ValueError, match="Sektion 'pdf' fehlt"):
                ConfigLoader(str(tmpdir))

    def test_missing_pdf_filename(self):
        """Test Fehler bei fehlender PDF-Dateiname."""
        config_data = {"task": "colloquium", "pdf": {}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data, create_pdf=False)

            with pytest.raises(ValueError, match="'filename' fehlt"):
                ConfigLoader(str(tmpdir))

    def test_missing_colloquium_section(self):
        """Test Fehler bei fehlendem Kolloquium-Sektion."""
        config_data = {"task": "colloquium", "pdf": {"filename": "test.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="Sektion 'colloquium' fehlt"):
                ConfigLoader(str(tmpdir))

    def test_missing_colloquium_date(self):
        """Test Fehler bei fehlendem Kolloquium-Datum."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {"time": "14:00", "location_type": "campus", "room": "3.217"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="Pflichtfeld 'date' fehlt"):
                ConfigLoader(str(tmpdir))

    def test_invalid_location_type(self):
        """Test Fehler bei ungültigem Location-Type."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "20.01.2026",
                "time": "14:00",
                "location_type": "invalid",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="Ungültiger location_type"):
                ConfigLoader(str(tmpdir))

    def test_missing_room_for_campus(self):
        """Test Fehler bei fehlendem Raum für Campus-Kolloquium."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "20.01.2026",
                "time": "14:00",
                "location_type": "campus",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="'room' erforderlich"):
                ConfigLoader(str(tmpdir))

    def test_missing_company_name_for_company(self):
        """Test Fehler bei fehlendem Firmennamen für Firmen-Kolloquium."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "20.01.2026",
                "time": "14:00",
                "location_type": "company",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="'company_name' erforderlich"):
                ConfigLoader(str(tmpdir))

    def test_missing_zoom_link_for_online(self):
        """Test Fehler bei fehlendem Zoom-Link für Online-Kolloquium."""
        config_data = {
            "task": "colloquium",
            "pdf": {"filename": "test.pdf"},
            "colloquium": {
                "date": "20.01.2026",
                "time": "14:00",
                "location_type": "online",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)

            with pytest.raises(ValueError, match="'zoom_link' erforderlich"):
                ConfigLoader(str(tmpdir))

    def test_file_not_found(self):
        """Test Fehler bei nicht existierendem Ordner."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader("/non/existent/directory")

    def test_invalid_json(self):
        """Test Fehler bei ungültigem JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, "w") as f:
                f.write("{ invalid json }")

            with pytest.raises(json.JSONDecodeError):
                ConfigLoader(str(tmpdir))

    def test_get_pdf_path(self):
        """Test PDF-Pfad Generierung."""
        config_data = {"task": "project", "pdf": {"filename": "test.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))
            pdf_path = config.get_pdf_path()

            assert pdf_path.endswith("test.pdf")
            assert str(tmpdir) in pdf_path

    def test_repr(self):
        """Test String-Repräsentation."""
        config_data = {"task": "review", "pdf": {"filename": "paper.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))
            repr_str = repr(config)

            assert "ConfigLoader" in repr_str
            assert "task=review" in repr_str

    def test_load_config_factory(self):
        """Test Factory-Funktion."""
        config_data = {"task": "project", "pdf": {"filename": "test.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = load_config(str(tmpdir))

            assert isinstance(config, ConfigLoader)
            assert config.get_task() == "project"

    def test_optional_fields(self):
        """Test dass optionale Felder None zurückgeben."""
        config_data = {"task": "project", "pdf": {"filename": "test.pdf"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            self.create_config_in_tmpdir(tmpdir, config_data)
            config = ConfigLoader(str(tmpdir))

            # Project hat keine colloquium section
            assert config.get_colloquium_config() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
