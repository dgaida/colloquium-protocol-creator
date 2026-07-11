# Konfigurations-Handbuch

Diese Anleitung erklärt, wie Sie den Academic Document Generator mithilfe von JSON-Konfigurationsdateien anpassen.

## 📋 Übersicht

Das Tool unterstützt JSON-basierte Konfigurationen für drei Hauptanwendungsfälle:  
- **Kolloquium-Protokolle** (Thesis-Verteidigung)  
- **Praxisprojekt- & WASP1-Benotung**  
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

Passen Sie anschließend die `config.json` Datei an. Mindestens der Dateiname des zu analysierenden PDF-Dokuments (`pdf` -> `filename`) muss korrekt gesetzt sein.

### 3. Tool ausführen

**Option A: Über die CLI**
```bash
academic-doc-generator --config /pfad/zu/ihrer/thesis/config_colloquium_campus.json
```

**Option B: Über main.py**
Sie können das Tool auch über die `main.py` im Projekt-Stammverzeichnis ausführen. Passen Sie dazu in der `main.py` den Pfad (`folder`) zu dem Ordner an, in dem Ihr PDF und die neue JSON-Datei liegen.

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
- `config_wasp1_template.json` - WASP1-Projekt-Benotung  
- `config_review_template.json` - Peer-Review-Kommentare  

## ⚙️ Globale Konfiguration (config.yaml)

Zusätzlich zu den projekt-spezifischen JSON-Dateien gibt es eine globale `config.yaml` im Projekt-Stammverzeichnis für allgemeine Einstellungen:

```yaml
# Globaler Ordner für Web-Metadaten (*.md Steckbriefe)
web_metadata_folder: "/pfad/zu/ihrer/webseite/data/projects/"

# Standard-Prüfername (überschreibt Extraktion aus PDF)
first_examiner: "Prof. Dr. Vorname Nachname"
```

- `web_metadata_folder`: Wenn gesetzt, werden die generierten Jekyll-kompatiblen Steckbriefe automatisch in diesen Ordner kopiert.  
- `first_examiner`: Hier kann ein Name hinterlegt werden, der global für alle Dokumente als Erstprüfer verwendet wird.  

## 🔍 PDF-Parser & Web-Metadaten Verhalten

### Standard PDF-Parser (LiteParse)
Als Standard PDF-Parser wird nun [LiteParse](https://github.com/run-llama/liteparse) verwendet. LiteParse ermöglicht eine schnelle und zuverlässige Extraktion von PDF-Texten und Annotationen (Kommentaren).
Sollte die Verarbeitung mit LiteParse fehlschlagen (z. B. durch fehlende Abhängigkeiten oder korrupte Dokumente), greift das Tool automatisch auf **Docling** und danach auf **PyMuPDF** als Fallbacks zurück.

### Verhalten bei unbekannten Autoren (Unknown)
Wenn der Autor einer Arbeit nicht eindeutig identifiziert werden kann (also als `Unknown`, `Unknown Author` oder `Unbekannt` markiert ist), wird die generierte `*.md` Steckbrief-Datei mit der Kurzzusammenfassung **nicht** in den globalen Zielpfad (`web_metadata_folder`) kopiert oder verschoben. Sie verbleibt lediglich im lokalen Ausgabeordner. Dies verhindert, dass unvollständige oder fehlerhafte Steckbriefe auf den Academic Pages veröffentlicht werden.

## 📚 Weitere Dokumentation

- [Installationsanleitung](INSTALL.de.md)  
- [Kolloquium-Dokumentation](COLLOQUIUM.de.md)  
- [Projekt-Dokumentation](PROJECT.de.md)  
- [Review-Dokumentation](REVIEW.de.md)  
