# Protokoll-Generator für Thesis-Kolloquien

## Übersicht

Dieses Tool automatisiert die Erstellung formeller Protokollbriefe für Bachelor- und Master-Kolloquien an der TH Köln. Es extrahiert Ihre Korrekturanmerkungen aus einem annotierten Thesis-PDF, formuliert diese mithilfe einer KI in klare Fragen um und generiert sowohl den Protokollbrief als auch das vorausgefüllte Bewertungsformular.

## Erzeugte Dateien (Ergebnisse)

### 1. LaTeX-Protokollbrief
**Dateiname:** `bewertung_brief_<matrikelnr>.tex`
Ein formeller `scrlttr2`-Brief mit dem Briefkopf und Fußzeile der TH Köln.

### 2. Kompiliertes PDF
**Dateiname:** `bewertung_brief_<matrikelnr>.pdf`
Das druckfertige PDF des Protokollbriefs (erfordert LuaLaTeX).

### 3. Vorausgefülltes Bewertungsformular
**Dateiname:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<stud_name>.pdf`
Das offizielle Formular der TH Köln, automatisch ausgefüllt mit Namen, Daten und den korrekten Checkboxen für den Studiengang.

### 4. E-Mail- & Outlook-Entwurf
**Dateiname:** `kolloquium_anmeldung_<name>_<matrikelnr>.md`
Eine fertige E-Mail für den Prüfungsservice. Falls Outlook geöffnet ist, wird automatisch ein Entwurf mit ICS-Kalenderanhang erstellt.

---

## Anforderungen

- Annotiertes Thesis-PDF (mit Kommentaren/Hervorhebungen)
- Mindestens ein konfigurierter LLM-API-Key (OpenAI, Groq, Google Gemini) oder lokales Ollama
- LaTeX-Installation (LuaLaTeX empfohlen)
- (Optional) Unterschrift unter `data/signature.png`

## Benutzung

### Kommandozeile (CLI)

Der empfohlene Weg zur Nutzung des Tools:

```bash
# Basis-Nutzung (erkennt verfügbare API automatisch)
academic-doc-generator colloquium /pfad/zu/Bachelorarbeit_Mueller.pdf --date 20.01.2026 --time 14:00 --room 3.217

# Mit einer Konfigurationsdatei
academic-doc-generator --config config_colloquium_campus.json
```

## Metadaten & Studiengänge

Das Tool extrahiert den `course_of_study` automatisch vom Titelblatt der Thesis und wählt die entsprechende Checkbox im offiziellen Bewertungsformular aus:

| Studiengang | PDF-Formular Checkbox |
|-----------------|-------------------|
| Informatik | KontrollInformatik |
| Wirtschaftsinformatik | ControlWI |
| Medieninformatik | KontrollMedien |
| IT-Management | KontrollITM |

## Kommentar-Kategorien

Annotationen im PDF werden automatisch in vier Typen kategorisiert:

### 1. KI-Kommentare (Standard)
Normale Kommentare, die von der KI in höfliche, klare Fragen umformuliert werden.
*Beispiel: "Warum?" → "Könnten Sie die Begründung für diese Entscheidung näher erläutern?"*

### 2. Quelle-Kommentare
Hinweise auf fehlende Quellen. Sie werden in der Statistik gezählt, aber nicht umformuliert.
*Regel: Enthält "quelle" oder "source" und ist kurz.*

### 3. Sprach-Kommentare
Hinweise auf Grammatik oder Rechtschreibung. Sie werden gezählt, um am Ende einen Hinweis auf die sprachliche Qualität zu geben.

### 4. Ignorieren
Marker wie "ab hier" werden komplett ignoriert.

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
