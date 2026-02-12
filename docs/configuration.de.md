# Konfigurations-Handbuch

Diese Anleitung erklärt, wie Sie den Academic Document Generator mithilfe von JSON-Konfigurationsdateien anpassen.

## 📋 Übersicht

Das Tool unterstützt JSON-basierte Konfigurationen für drei Hauptanwendungsfälle:
- **Kolloquium-Protokolle** (Thesis-Verteidigung)
- **Praxisprojekt-Benotung**
- **Peer-Review** Kommentare

## 🎯 Quick Start

### 1. Vorlage auswählen

```bash
# Verfügbare Vorlagen auflisten
academic-doc-generator --list-templates
```

### 2. Kopieren und Anpassen

```bash
# Vorlage in Ihren Thesis-Ordner kopieren
cp config_templates/config_colloquium_campus.json /pfad/zu/ihrer/thesis/
```

### 3. Tool ausführen

```bash
# Über die CLI
academic-doc-generator --config /pfad/zu/ihrer/thesis/config_colloquium_campus.json
```

## 📝 Konfigurations-Struktur

### Gemeinsame Felder

#### `output` (optional)

```json
{
  "output": {
    "folder": null,              // null = gleicher Ordner wie PDF
    "compile_pdf": true,         // LaTeX zu PDF kompilieren
    "signature_file": "signature.png", // Pfad zur Unterschrift
    "create_feedback_mail": true // Feedback-Mail generieren (für Projekte)
  }
}
```

- `folder`: Ausgabe-Verzeichnis (`null` = Ordner des PDFs)
- `compile_pdf`: Ob `.tex` zu PDF kompiliert werden soll
- `signature_file`: Pfad zur Unterschrift (Standard ist `signature.png` oder Suche in `data/`)
- `create_feedback_mail`: Ob studentisches Feedback generiert werden soll

## 🎓 Kolloquium-Konfiguration

```json
{
  "task": "colloquium",
  "colloquium": {
    "date": "20.01.2026",
    "time": "14:00",
    "location_type": "campus",
    "room": "3.217"
  }
}
```

**Manuelle Metadaten (Optional):**
Falls die automatische Extraktion fehlschlägt, können Sie Felder manuell setzen:
- `course_of_study`: z. B. "Informatik", "Medieninformatik"
- `author`: Name des Studierenden

## 📂 Projekt-Konfiguration

```json
{
  "task": "project",
  "project": {
    "mark": "1.3"
  },
  "output": {
    "create_feedback_mail": true
  }
}
```

## 🔑 API-Keys konfigurieren

Erstellen Sie eine `secrets.env` im Projekt-Stammverzeichnis:

```bash
OPENAI_API_KEY=sk-xxxxxxxx
GROQ_API_KEY=gsk-xxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxx
```

## 📝 Konfigurations-Vorlagen

Vorgefertigte JSON-Konfigurationen im Ordner `config_templates/`:

- `config_colloquium_campus.json` - Thesis-Kolloquium auf dem Campus
- `config_colloquium_company.json` - Thesis-Kolloquium im Unternehmen
- `config_colloquium_online.json` - Online-Kolloquium (Zoom)
- `config_project_template.json` - Praxisprojekt-Benotung
- `config_review_template.json` - Peer-Review-Kommentare

## 📚 Weitere Dokumentation

- [Installationsanleitung](INSTALL.md)
- [Kolloquium-Dokumentation](COLLOQUIUM.md)
- [Projekt-Dokumentation](PROJECT.md)
- [Review-Dokumentation](REVIEW.md)
