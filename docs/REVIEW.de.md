# Peer-Review-Kommentare

## Übersicht

Dieses Tool generiert professionelles Peer-Review-Feedback für wissenschaftliche Veröffentlichungen. Es extrahiert informelle Korrekturnotizen aus einem annotierten PDF, erkennt automatisch Zeilennummern aus den Rändern und generiert ein strukturiertes Markdown-Dokument mit präzisen Seiten- und Zeilenreferenzen.

## Erzeugte Dateien (Ergebnisse)

### 1. Markdown-Review-Dokument
**Dateiname:** `review_<dateiname>.md`
Ein übersichtliches Dokument, das alle Anmerkungen nach Seite und Zeile sortiert enthält. Das Feedback wird automatisch in professionelles Englisch übersetzt und formuliert.

---

## Anforderungen

- Annotiertes Paper als PDF (mit Kommentaren/Hervorhebungen)
- Mindestens ein konfigurierter LLM-API-Key (OpenAI empfohlen für höchste Qualität)

## Benutzung

### Kommandozeile (CLI)

```bash
# Basis-Nutzung
academic-doc-generator review paper.pdf

# Ausgabeordner festlegen
academic-doc-generator review paper.pdf --out ./reviews
```

## Hauptmerkmale

- ✅ **Automatische Zeilenzuordnung**: Manuelles Abtippen von Seiten- und Zeilennummern entfällt.
- ✅ **Konstruktiver Ton**: Verwandelt stichpunktartige Notizen in professionelle akademische Sprache.
- ✅ **Strukturiertes Format**: Erzeugt eine saubere Markdown-Datei, bereit für Einreichungssysteme.
- ✅ **Automatische Übersetzung**: Übersetzt deutsche Notizen automatisch ins Englische.

---

## Funktionsweise (Details)

1. **Extraktion von Annotationen**: Liest Hervorhebungen und Kommentare aus dem PDF.
2. **Zeilennummer-Erkennung**: Identifiziert automatisch Zeilennummern an den Rändern des PDFs für exakte Referenzen.
3. **Kontextsensitive Umformulierung**: Ordnet Ihre Notizen dem markierten Text und den umgebenden Absätzen zu.
4. **Professionelle Veredelung**: Schreibt kurze Notizen (z. B. "unlar", "Beleg fehlt") in konstruktives, höfliches Feedback um.
5. **Englische Ausgabe**: Generiert das Feedback immer auf Englisch, passend für internationale Einreichungen bei Journalen und Konferenzen.

---

## Tipps für Reviewer

1. **Exakt Markieren**: Markieren Sie genau die Phrase oder den Satz, auf den sich Ihr Kommentar bezieht.
2. **Kurze Notizen reichen**: Sie können kurze Stichpunkte schreiben; die KI formuliert daraus hilfreiche Vorschläge.
3. **Zeilennummern**: Das Tool funktioniert am besten bei Dokumenten mit sichtbaren Zeilennummern am Rand (Standard bei vielen Journal-Einreichungen).

## Weitere Dokumentation

- [Installationsanleitung](INSTALL.md)
- [Kolloquium-Protokolle](COLLOQUIUM.md)
- [Konfigurations-Handbuch](configuration.md)
