"""Configuration loader for colloquium-protocol-creator.

This module provides functionality to load and validate configuration files
for different tasks (colloquium, project, review).
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import glob


class ConfigLoader:
    """Lädt und validiert Konfigurationsdateien für verschiedene Tasks."""

    VALID_TASKS = ["colloquium", "project", "review"]
    VALID_LOCATION_TYPES = ["campus", "company", "online"]

    def __init__(self, pdf_path: str):
        """Initialisiert den ConfigLoader.

        Args:
            pdf_path: Pfad zur JSON-Konfigurationsdatei.

        Raises:
            FileNotFoundError: Wenn die Config-Datei nicht existiert.
            json.JSONDecodeError: Wenn die Config-Datei kein valides JSON ist.
        """
        self.pdf_path = Path(pdf_path)

        # TODO: muss im aktuellen Ordner nach json Dateien suchen und die erste nehmen und solange json Dateien nehmen
        #  bis die validate_config grünes licht gibt
        pat = os.path.join(pdf_path, "*.json")
        matches = glob.glob(pat)
        print(matches)

        json_file = "config_colloq_voss.json"

        json_path = Path(os.path.join(self.pdf_path, json_file))

        if not json_path.exists():
            raise FileNotFoundError(f"Config-Datei nicht gefunden: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self._validate_config()

    def _validate_config(self) -> None:
        """Validiert die geladene Konfiguration.

        Raises:
            ValueError: Wenn die Konfiguration ungültig ist.
        """
        # Task validieren
        task = self.config.get("task")
        if task not in self.VALID_TASKS:
            raise ValueError(
                f"Ungültiger Task: {task}. Erlaubt: {self.VALID_TASKS}"
            )

        # PDF-Pfad validieren
        if "pdf" not in self.config:
            raise ValueError("Sektion 'pdf' fehlt in der Konfiguration")

        pdf_config = self.config["pdf"]
        if "filename" not in pdf_config:
            raise ValueError("'filename' fehlt in der PDF-Konfiguration")

        # Task-spezifische Validierung
        if task == "colloquium":
            self._validate_colloquium_config()
        elif task == "project":
            self._validate_project_config()
        elif task == "review":
            self._validate_review_config()

    def _validate_colloquium_config(self) -> None:
        """Validiert Kolloquiums-spezifische Konfiguration."""
        if "colloquium" not in self.config:
            raise ValueError("Sektion 'colloquium' fehlt für Task 'colloquium'")

        coll = self.config["colloquium"]

        # Pflichtfelder
        required = ["date", "time", "location_type"]
        for field in required:
            if field not in coll:
                raise ValueError(f"Pflichtfeld '{field}' fehlt in 'colloquium'")

        # Location-Type validieren
        loc_type = coll["location_type"]
        if loc_type not in self.VALID_LOCATION_TYPES:
            raise ValueError(
                f"Ungültiger location_type: {loc_type}. "
                f"Erlaubt: {self.VALID_LOCATION_TYPES}"
            )

        # Location-spezifische Pflichtfelder
        if loc_type == "campus" and "room" not in coll:
            raise ValueError("'room' erforderlich für location_type 'campus'")
        elif loc_type == "company" and "company_name" not in coll:
            raise ValueError("'company_name' erforderlich für location_type 'company'")
        elif loc_type == "online" and "zoom_link" not in coll:
            raise ValueError("'zoom_link' erforderlich für location_type 'online'")

    def _validate_project_config(self) -> None:
        """Validiert Projektarbeits-spezifische Konfiguration."""
        # Für Project-Task sind nur PDF und LLM-Konfiguration erforderlich
        pass

    def _validate_review_config(self) -> None:
        """Validiert Review-spezifische Konfiguration."""
        # Für Review-Task sind nur PDF und LLM-Konfiguration erforderlich
        pass

    def get_pdf_path(self) -> str:
        """Gibt den vollständigen Pfad zur PDF-Datei zurück.

        Returns:
            Vollständiger Pfad zur PDF-Datei.
        """
        pdf_config = self.config["pdf"]
        folder = self.pdf_path
        filename = pdf_config["filename"]
        return os.path.join(folder, filename)

    def get_task(self) -> str:
        """Gibt den Task-Typ zurück.

        Returns:
            Task-Typ ("colloquium", "project", oder "review").
        """
        return self.config["task"]

    def get_llm_config(self) -> Dict[str, Any]:
        """Gibt die LLM-Konfiguration zurück.

        Returns:
            Dictionary mit LLM-Konfiguration (api_choice, model, etc.).
        """
        return self.config.get("llm", {})

    def get_output_config(self) -> Dict[str, Any]:
        """Gibt die Output-Konfiguration zurück.

        Returns:
            Dictionary mit Output-Konfiguration (folder, compile_pdf, etc.).
        """
        return self.config.get("output", {})

    def get_colloquium_config(self) -> Optional[Dict[str, Any]]:
        """Gibt die Kolloquiums-Konfiguration zurück.

        Returns:
            Dictionary mit Kolloquiums-Details oder None wenn nicht vorhanden.
        """
        return self.config.get("colloquium")

    def __repr__(self) -> str:
        """String-Repräsentation des ConfigLoaders.

        Returns:
            Beschreibung der geladenen Konfiguration.
        """
        return (
            f"ConfigLoader(task={self.get_task()}, "
            f"pdf={self.get_pdf_path()})"
        )


def load_config(pdf_path: str) -> ConfigLoader:
    """Factory-Funktion zum Laden einer Konfiguration.

    Args:
        pdf_path: Pfad zur JSON-Konfigurationsdatei.

    Returns:
        ConfigLoader-Instanz mit geladener und validierter Konfiguration.

    Example:
        >>> config = load_config("config_templates/config_colloquium_campus.json")
        >>> print(config.get_task())
        colloquium
        >>> print(config.get_pdf_path())
        ../BachelorThesen/2025_26_WS/Mustermann/Bachelorarbeit_Mustermann.pdf
    """
    return ConfigLoader(pdf_path)
