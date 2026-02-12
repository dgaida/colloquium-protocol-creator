# Benotungsbriefe für Praxisprojekte

## Übersicht

Dieses Tool automatisiert die Erstellung formeller Benotungsbriefe für Praxisprojekte, Projektarbeiten und ähnliche Leistungen an der TH Köln. Es extrahiert Metadaten aus dem Projekt-PDF, bestimmt automatisch die korrekte Anrede (Herr/Frau) und generiert eine LaTeX-Briefvorlage im TH Köln-Format sowie Feedback-E-Mails.

## Erzeugte Dateien (Ergebnisse)

### 1. LaTeX-Benotungsbrief
**Dateiname:** `projektarbeit_brief_<matrikelnr>.tex`
Ein formeller `scrlttr2`-Brief mit dem Briefkopf und Fußzeile der TH Köln.

### 2. Kompiliertes PDF
**Dateiname:** `projektarbeit_brief_<matrikelnr>.pdf`
Das druckfertige PDF des Benotungsbriefs (erfordert LuaLaTeX).

### 3. E-Mail für den Prüfungsservice
**Dateiname:** `projekt_anmeldung_<name>_<matrikelnr>.md`
Eine fertige E-Mail-Vorlage zur Einreichung der Note beim Prüfungsservice.

### 4. Feedback-E-Mails für Studierende
**Dateiname:** `feedback_student_<name>_<matrikelnr>.md`
Ein automatisch generierter Entwurf mit einer Zusammenfassung der Stärken und Schwächen sowie der Note.

---

## Anforderungen

- Projektarbeit als PDF mit Deckblatt (Text muss selektierbar sein)
- Mindestens ein konfigurierter LLM-API-Key (OpenAI, Groq, Google Gemini) oder lokales Ollama
- LaTeX-Installation (LuaLaTeX empfohlen)
- (Optional) Unterschrift unter `data/signature.png`

## Benutzung

### Kommandozeile (CLI)

```bash
# Basis-Nutzung
academic-doc-generator project /pfad/zu/Praxisprojekt_Mueller.pdf

# Feedback-Mail deaktivieren (Standard ist aktiviert)
academic-doc-generator project project.pdf --no-feedback-mail
```

## Feedback & Studierenden-E-Mail

Wenn `create_feedback_mail` aktiviert ist (Standard), führt das Tool folgende Schritte aus:
1. Analyse der Projektarbeit mithilfe der KI.
2. Extraktion der E-Mail-Adresse des Studierenden vom Deckblatt.
3. Generierung einer Markdown-Datei mit einer Feedback-Zusammenfassung.
4. Bereitstellung eines E-Mail-Entwurfs für den Studierenden.

---

## Funktionsweise (Details)

1. **Metadaten-Extraktion**: Erkennt automatisch Name, Matrikelnummer, Projekttitel, Prüfer und E-Mail-Adresse des Studierenden.
2. **Geschlechtserkennung**: Nutzt die KI, um basierend auf dem Vornamen die korrekte deutsche Anrede (Herr/Frau) zu bestimmen.
3. **Semester-Berechnung**: Ermittelt automatisch das aktuelle Semester (SoSe/WS).
4. **LaTeX-Generierung**: Erstellt den Brief im Corporate Design der TH Köln.
5. **Signatur-Integration**: Bindet automatisch ein Bild Ihrer Unterschrift ein, falls vorhanden.

---

## Fehlerbehebung

### E-Mail-Adresse nicht erkannt
- Stellen Sie sicher, dass die E-Mail-Adresse auf dem Deckblatt steht und als Text kopierbar ist.
- Falls die Extraktion fehlschlägt, müssen Sie die Adresse manuell im E-Mail-Entwurf ergänzen.

### Falsche Anrede (Herr/Frau)
- Bei uneindeutigen Vornamen kann die Erkennung fehlschlagen. Sie können die Anrede einfach in der generierten `.tex`-Datei korrigieren.

## Weitere Dokumentation

- [Installationsanleitung](INSTALL.md)
- [Kolloquium-Protokolle](COLLOQUIUM.md)
- [Konfigurations-Handbuch](configuration.md)
