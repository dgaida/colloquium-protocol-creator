"""Configuration loader for colloquium-protocol-creator.

This module provides functionality to load and validate configuration files
for different tasks (colloquium, project, review).
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class ConfigLoader:
    """Lädt und validiert Konfigurationsdateien für verschiedene Tasks."""

    VALID_TASKS = ["colloquium", "project", "review"]
    VALID_LOCATION_TYPES = ["campus", "company", "online"]

    def __init__(self, folder_path: str):
        """Initialisiert den ConfigLoader.

        Args:
            folder_path: Pfad zum Ordner, der die JSON-Konfigurationsdatei enthält.
                        Es wird nach config*.json gesucht und die erste gefundene Datei verwendet.

        Raises:
            FileNotFoundError: Wenn keine Config-Datei gefunden wird.
            json.JSONDecodeError: Wenn die Config-Datei kein valides JSON ist.
        """
        self.folder_path = Path(folder_path)

        if not self.folder_path.exists():
            raise FileNotFoundError(f"Ordner nicht gefunden: {folder_path}")

        # Suche nach config*.json Dateien im Ordner
        config_files = sorted(self.folder_path.glob("config*.json"))

        if not config_files:
            raise FileNotFoundError(f"Keine config*.json Datei gefunden in: {folder_path}")

        # Nehme die erste gefundene Datei
        json_path = config_files[0]

        with open(json_path, encoding="utf-8") as f:
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
            raise ValueError(f"Ungültiger Task: {task}. Erlaubt: {self.VALID_TASKS}")

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
                f"Ungültiger location_type: {loc_type}. " f"Erlaubt: {self.VALID_LOCATION_TYPES}"
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
        filename = pdf_config["filename"]
        return os.path.join(self.folder_path, filename)

    def get_task(self) -> str:
        """Gibt den Task-Typ zurück.

        Returns:
            Task-Typ ("colloquium", "project", oder "review").
        """
        return self.config["task"]

    def get_llm_config(self) -> dict[str, Any]:
        """Gibt die LLM-Konfiguration zurück.

        Returns:
            Dictionary mit LLM-Konfiguration (api_choice, model, etc.).
        """
        return self.config.get("llm", {})

    def get_output_config(self) -> dict[str, Any]:
        """Gibt die Output-Konfiguration zurück.

        Returns:
            Dictionary mit Output-Konfiguration (folder, compile_pdf, etc.).
        """
        return self.config.get("output", {})

    def get_colloquium_config(self) -> Optional[dict[str, Any]]:
        """Gibt die Kolloquiums-Konfiguration zurück.

        Returns:
            Dictionary mit Kolloquiums-Details oder None wenn nicht vorhanden.
        """
        return self.config.get("colloquium")

    def get_project_config(self) -> Optional[dict[str, Any]]:
        """Gibt die Projekt-Konfiguration zurück.

        Returns:
            Dictionary mit Projekt-Details oder None wenn nicht vorhanden.
        """
        return self.config.get("project")

    def get_gemini_emark_config(self) -> dict[str, Any]:
        """Gibt die Gemini-Emarks-Konfiguration zurück.

        Returns:
            Dictionary mit Gemini-Emarks-Einstellungen:
            - enabled: bool (default False)
            - model: str (default "gemini-2.0-flash-exp")
        """
        default_config = {"enabled": False, "model": "gemini-2.0-flash-exp"}
        return self.config.get("gemini_emark", default_config)

    def __repr__(self) -> str:
        """String-Repräsentation des ConfigLoaders.

        Returns:
            Beschreibung der geladenen Konfiguration.
        """
        return f"ConfigLoader(task={self.get_task()}, pdf={self.get_pdf_path()})"


def load_config(folder_path: str) -> ConfigLoader:
    """Factory-Funktion zum Laden einer Konfiguration.

    Args:
        folder_path: Pfad zum Ordner, der die JSON-Konfigurationsdatei enthält.

    Returns:
        ConfigLoader-Instanz mit geladener und validierter Konfiguration.

    Example:
        >>> config = load_config("config_templates")
        >>> print(config.get_task())
        colloquium
        >>> print(config.get_pdf_path())
        config_templates/Bachelorarbeit_Mustermann.pdf
    """
    return ConfigLoader(folder_path)
