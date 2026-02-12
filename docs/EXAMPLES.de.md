# Beispiel-Ausgaben

Diese Seite zeigt Beispiele für die vom Academic Document Generator erzeugten Dokumente.

## Thesis-Kolloquiums-Brief (Kolloquiumsprotokoll)

Das Tool erzeugt einen formellen `scrlttr2`-Brief im Corporate Design der TH Köln.

```latex
\documentclass[11pt,ngerman,parskip=full]{scrlttr2}
% TH Köln Briefkopf
\setkomavar{subject}{Bewertung Bachelor Arbeit von Max Mustermann}

% Zusammenfassung
\textbf{Zusammenfassung der Thesis:}
Die Arbeit behandelt...

% Fragen
\textbf{Fragen Prof. Dr. Müller:}
Seite 5: Könnten Sie die Wahl dieser Methodik näher begründen?
Seite 12: Wie verhält sich der Algorithmus bei größeren Datenmengen?
```

## Peer-Review-Kommentare

Review-Feedback wird als übersichtliches Markdown-Dokument ausgegeben.

```markdown
# Peer Review

- Page 1, Line 15: This point requires clarification...
- Page 2, Line 42: The explanation could be clearer by...
- Page 3, Line 78: The authors should consider recent work by...
```
