# Beispiel-Ausgaben

Diese Seite zeigt Beispiele für die vom Academic Document Generator erzeugten Dokumente.

## Thesis-Kolloquium

### LaTeX-Protokollbrief
Das Tool erzeugt einen formellen `scrlttr2`-Brief im Corporate Design der TH Köln.

```latex
\documentclass[11pt,ngerman,parskip=full]{scrlttr2}
% TH Köln Briefkopf
\setkomavar{subject}{Bewertung Bachelor Arbeit von Max Mustermann}

% Zusammenfassung
\textbf{Zusammenfassung der Thesis:}
Die vorliegende Arbeit beschäftigt sich mit der Entwicklung eines...

% Fragen
\textbf{Fragen Prof. Dr. Müller:}
\begin{itemize}
    \item Seite 5: Könnten Sie die Wahl dieser Methodik näher begründen?
    \item Seite 12: Wie verhält sich der Algorithmus bei größeren Datenmengen?
\end{itemize}

% Statistik
\textbf{Hinweise zur Arbeit:}
- Anzahl der Kommentare: 15
- Fehlende Quellen: 2
- Sprachliche Qualität: Gut (3 Hinweise)
```

### Kompiliertes PDF
Das PDF enthält das TH Köln Logo, die Adresse des Prüfungsservice als Empfänger und Ihre digitale Unterschrift (falls unter `data/signature.png` vorhanden).

### Vorausgefülltes Bewertungsformular
Das offizielle PDF-Formular der TH Köln wird automatisch mit folgenden Daten befüllt:
- Name, Vorname & Matrikelnummer
- Titel der Arbeit
- Datum und Uhrzeit des Kolloquiums
- Korrekte Checkbox für den Studiengang (z.B. Wirtschaftsinformatik -> `KontrollWI`)

### E-Mail- & Outlook-Entwurf
Eine Markdown-Datei mit dem Text für den Prüfungsservice:
```markdown
Betreff: Protokoll & Bewertung Kolloquium: Max Mustermann (11122233)

Sehr geehrte Damen und Herren,

anbei erhalten Sie das Protokoll sowie die Bewertung für das Kolloquium von Herrn Max Mustermann.
...
```

---

## Projekt & WASP1

### LaTeX-Benotungsbrief
Ein Brief zur Mitteilung der Note an den Studierenden.

```latex
\setkomavar{subject}{Bewertung Ihrer Projektarbeit}

Sehr geehrter Herr Mustermann,

herzlichen Glückwunsch zur erfolgreichen Abgabe Ihrer Projektarbeit mit dem Titel "Entwicklung von...".
Ihre Arbeit wurde mit der Note \textbf{1,3} bewertet.
```

### Kompiliertes PDF (Projekt)
Ähnlich wie beim Kolloquiumsbrief, jedoch direkt an den Studierenden adressiert.

### E-Mail Prüfungsservice
Ein kurzer Text zur Übermittlung der Projektnote an das Sekretariat/Prüfungsservice.

### Feedback-E-Mail (Studierende)
Die KI analysiert das Projekt und generiert ein konstruktives Feedback:
```markdown
Betreff: Feedback zu Ihrer Projektarbeit

Hallo Max,

hier ist ein kurzes Feedback zu deiner Arbeit:
- **Stärken:** Sehr gute Strukturierung und klare Methodik.
- **Verbesserungspotenzial:** Die Evaluation der Ergebnisse hätte ausführlicher sein können.
- **Note:** 1,3
```

---

## Web-Metadaten (Steckbrief)
Für jedes Projekt/Thesis wird ein Jekyll-kompatibler Steckbrief generiert:

```markdown
---
layout: project
title: "KI-basierte Dokumentenerstellung"
author: "M. Mustermann"
date: 2026-01-20
summary: "Diese Arbeit untersucht die Automatisierung von..."
keywords: [KI, LaTeX, Python]
---
# Zusammenfassung
...
```

---

## Peer-Review

Review-Feedback wird als übersichtliches Markdown-Dokument ausgegeben.

```markdown
# Peer Review: [Titel des Papers]

- **Seite 1, Zeile 15:** Dieser Punkt benötigt eine genauere Erläuterung...
- **Seite 2, Zeile 42:** Die Abbildung 3 ist schwer lesbar...
- **Seite 3, Zeile 78:** Die Autoren sollten die Arbeit von [Name] berücksichtigen...
```
