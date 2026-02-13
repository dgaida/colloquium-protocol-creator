# Protokoll-Generator für Thesis-Kolloquien

## Übersicht

Dieses Tool automatisiert die Erstellung formeller Protokollbriefe für Bachelor- und Master-Kolloquien an der TH Köln. Es extrahiert Ihre Korrekturanmerkungen aus einem annotierten Thesis-PDF, formuliert diese mithilfe einer KI in klare Fragen um und generiert sowohl den Protokollbrief als auch das vorausgefüllte Bewertungsformular.

## Erzeugte Dateien (Ergebnisse)

Eine detaillierte Übersicht mit Bildern finden Sie auf der Seite [Beispiele](EXAMPLES.md#thesis-kolloquium).

### 1. [LaTeX-Protokollbrief](EXAMPLES.md#latex-protokollbrief)
**Dateiname:** `bewertung_brief_<matrikelnr>.tex`
Ein formeller `scrlttr2`-Brief mit dem Briefkopf und Fußzeile der TH Köln.

### 2. [Kompiliertes PDF](EXAMPLES.md#kompiliertes-pdf)
**Dateiname:** `bewertung_brief_<matrikelnr>.pdf`
Das druckfertige PDF des Protokollbriefs (erfordert LuaLaTeX).

### 3. [Vorausgefülltes Bewertungsformular](EXAMPLES.md#vorausgefulltes-bewertungsformular)
**Dateiname:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<stud_name>.pdf`
Das offizielle Formular der TH Köln, automatisch ausgefüllt mit Namen, Daten und den korrekten Checkboxen für den Studiengang.

### 4. [E-Mail- & Outlook-Entwurf](EXAMPLES.md#e-mail-outlook-entwurf)
**Dateiname:** `kolloquium_anmeldung_<name>_<matrikelnr>.md`
Eine fertige E-Mail für den Prüfungsservice. Falls Outlook geöffnet ist, wird automatisch ein Entwurf mit ICS-Kalenderanhang erstellt.

### 5. [Web-Metadaten (Steckbrief)](EXAMPLES.md#web-metadaten-steckbrief)
**Dateiname:** `YYYY-MM-DD-titel.md`
Ein Jekyll-kompatibler Steckbrief der Arbeit (Summary, Keywords, etc.) für die eigene Webseite. Der Pfad, wohin diese Dateien kopiert werden sollen, kann global in der `config.yaml` definiert werden.

---

## Anforderungen

- Annotiertes Thesis-PDF (mit Kommentaren/Hervorhebungen)
- Mindestens ein konfigurierter LLM-API-Key (OpenAI, Groq, Google Gemini) oder lokales Ollama
- LaTeX-Installation (LuaLaTeX empfohlen)
- (Optional) Unterschrift unter `data/signature.png`

## Benutzung

Der empfohlene Weg ist die Nutzung einer [Konfigurationsdatei](configuration.md).

### Kommandozeile (CLI)

```bash
# Mit einer Konfigurationsdatei
academic-doc-generator --config config_colloquium_campus.json

# Basis-Nutzung (erkennt verfügbare API automatisch)
academic-doc-generator colloquium /pfad/zu/Bachelorarbeit_Mueller.pdf --date 20.01.2026 --time 14:00 --room 3.217
```

### Nutzung über main.py

Sie können das Tool auch über die `main.py` ausführen, indem Sie dort den Pfad zum Thesis-Ordner angeben. Details dazu finden Sie im [Konfigurations-Handbuch](configuration.md#3-tool-ausfuhren).

## Metadaten & Studiengänge

Das Tool extrahiert den `course_of_study` automatisch vom Titelblatt der Thesis und wählt die entsprechende Checkbox im offiziellen Bewertungsformular aus:

| Studiengang | PDF-Formular Checkbox |
|-----------------|-------------------|
| Informatik | KontrollInformatik |
| Wirtschaftsinformatik | KontrollWI |
| Medieninformatik | KontrollMedien |
| IT-Management | KontrollITM |

## Kommentar-Kategorien

Das Tool folgt dem Workflow des Autors: Um die Thesis flüssig lesen zu können, werden nur kurze Notizen (Annotationen) im PDF gemacht. Das Tool kategorisiert diese automatisch, um sie im Protokollbrief passend aufzubereiten.

### 1. KI-Kommentare (Standard)
Verständnisfragen oder inhaltliche Anmerkungen, die von der KI in höfliche, klare Prüfungsfragen umformuliert werden.
*Beispiel: "Warum?" → "Könnten Sie die Begründung für diese Entscheidung näher erläutern?"*

### 2. Quelle-Kommentare
Hinweise auf fehlende Quellen. Der Autor schreibt hier meist nur kurz "Quelle?", "Quelle fehlt" oder "Beleg?". Diese werden in der Statistik gezählt, aber nicht umformuliert.
*Regel: Enthält "quelle" oder "source" und ist kurz.*

### 3. Sprach-Kommentare
Hinweise auf Grammatik, Rechtschreibung oder Stil. Sie werden gezählt, um am Ende einen Hinweis auf die sprachliche Qualität zu geben.
*Beispiele: "Grammatik", "Ausdruck", "unleserlich", "Rechtschreibung".*

### 4. Ignorieren / Marker
Spezielle Marker zur eigenen Orientierung.
*Beispiel: "ab hier" – Dieser Kommentar dient nur als Hinweis für den Leser, wo er das nächste Mal weiterlesen möchte, falls die Thesis nicht in einem Rutsch gelesen wird. Solche Marker werden im Protokoll ignoriert.*

---

## Funktionsweise (Details)

Für Interessierte, hier der technische Ablauf:

1. **Extraktion von PDF-Annotationen**: Liest Ihre Kommentare und Hervorhebungen aus dem PDF.
2. **Kontext-Analyse**: Ordnet jeden Kommentar dem exakt markierten Text und dem umgebenden Absatz zu.
3. **Intelligente Kategorisierung**: Sortiert Kommentare nach Typ (Frage, Quelle, Sprache).
4. **KI-Veredelung**: Schreibt kurze Notizen in präzise Prüfungsfragen um.
5. **Metadaten-Extraktion**: Erkennt Name, Matrikelnummer, Titel und Prüfer automatisch.
6. **Thesis-Zusammenfassung**: Erstellt eine Kurzfassung basierend auf den ersten 10 Seiten.
7. **Signatur-Integration**: Bindet automatisch ein Bild Ihrer Unterschrift ein, falls vorhanden.

---

## Fehlerbehebung

### Outlook-Entwurf wird nicht erstellt
- Stellen Sie sicher, dass Outlook geöffnet ist, bevor Sie das Tool starten.
- Unter macOS müssen Sie ggf. die Berechtigung zur Steuerung von Outlook erteilen.

### Studiengang wird nicht erkannt
- Stellen Sie sicher, dass der Name des Studiengangs klar auf dem Titelblatt steht.
- Alternativ können Sie `course_of_study` manuell in der JSON-Konfiguration setzen.

## Weitere Dokumentation

- [Installationsanleitung](INSTALL.md)
- [Praxisprojekt-Benotung](PROJECT.md)
- [Konfigurations-Handbuch](configuration.md)
