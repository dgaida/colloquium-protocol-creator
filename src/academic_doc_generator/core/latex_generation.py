"""Modul zur Generierung von LaTeX-Dokumenten für Thesis-Bewertungen."""

from typing import Optional


def escape_for_latex(text: str, preserve_latex: bool = True) -> str:
    """Escapes special LaTeX characters in a string.

    Args:
        text: The string to escape.
        preserve_latex: If True, common LaTeX commands like \\textbf and \\item
                       are preserved and not escaped. Defaults to True.

    Returns:
        The escaped string.
    """
    if text is None:
        return ""

    # Replace zero-width spaces and other invisible chars that break LaTeX
    out_chars = []
    for ch in ("\u00ad", "\u200b", "\u200c", "\u200d", "\ufeff"):
        text = text.replace(ch, "")

    # Handle German special characters specifically if needed
    # (Though most modern LaTeX engines handle UTF-8 well with babel/fontspec)
    # This is a fallback for older engines or specific setups
    # text = text.replace("ß", r"{\ss}")
    # text = text.replace("Ä", r'\"A').replace("Ö", r'\"O').replace("Ü", r'\"U')
    # text = text.replace("ä", r'\"a').replace("ö", r'\"o').replace("ü", r'\"u')

    # Convert common UTF-8 chars that might cause issues in some LaTeX setups
    out_chars = []
    for ch in text:
        if ch == "ß":
            out_chars.append(r"{\ss}")  # German sharp s
        else:
            out_chars.append(ch)
    text = "".join(out_chars)

    # Escape LaTeX specials
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "„": r"``",
        "“": r"''",
        "”": r"''",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    if not preserve_latex:
        # If we don't want to preserve any LaTeX, escape braces and backslashes too
        text = text.replace("{", r"\{").replace("}", r"\}")
        text = text.replace("\\", r"\textbackslash{}")

    # Apply standard replacements
    for char, replacement in replacements.items():
        # Only replace if not part of an already escaped sequence or command
        # This is a very simple check and might not be perfect
        text = text.replace(char, replacement)

    # Clean up any triple backslashes or other artifacts from recursive escaping
    # text = text.replace(r"\\", r"\\") # This line is usually not needed

    # Final cleanup of common problematic unicode characters
    text = text.replace("–", "--")  # en-dash
    text = text.replace("—", "---")  # em-dash

    return text


def return_seite_page(lang: str = "German") -> str:
    """Returns 'Seite' or 'Page' depending on language.

    Args:
        lang: The language ("German" or "English").

    Returns:
        The language-specific word for 'Page'.
    """
    if lang.lower() == "german":
        return "Seite"
    return "Page"


def concatenate_comments(context_dict: dict, lang: str = "German") -> str:
    """Concatenates comments from a context dictionary into a single string.

    Args:
        context_dict: Dictionary mapping page numbers to list of AnnotationContext.
        lang: The language ("German" or "English").

    Returns:
        Concatenated string of all comments.
    """
    seite_word = return_seite_page(lang)
    comments = []
    for page, contexts in context_dict.items():
        for context in contexts:
            comment = context["comment"]
            comments.append(f"{seite_word} {page}: {comment}")

    return "\n\n".join(comments)


def create_formal_letter_tex(
    title: str,
    author: str,
    summary: str,
    questions: str,
    first_examiner: str,
    first_examiner_mail: str,
    second_examiner: str,
    recipient: str = "Prüfungsservice Campus Gummersbach",
    subject: str = "Bewertung der Thesis",
    place: str = "Gummersbach",
    date: str = r"\today",
    gemini_evaluation: Optional[str] = None,
) -> str:
    """Generiert den LaTeX-Code für das Bewertungsschreiben.

    Args:
        title (str): Titel der Thesis.
        author (str): Autor der Thesis.
        summary (str): Zusammenfassung der Thesis.
        questions (str): Fragen aus dem Kolloquium.
        first_examiner (str): Name des Erstprüfers.
        first_examiner_mail (str): E-Mail des Erstprüfers.
        second_examiner (str): Name des Zweitprüfers.
        recipient (str, optional): Empfänger des Schreibens.
        subject (str, optional): Betreff des Schreibens.
        place (str, optional): Place of issue. Defaults to "Gummersbach".
        date (str, optional): Date string. Defaults to LaTeX \today.
        gemini_evaluation (str, optional): Automatische Bewertung von Gemini.
    """
    # Füge Gemini-Bewertung hinzu, falls vorhanden
    gemini_section = ""
    if gemini_evaluation:
        gemini_section = f"\n\n{gemini_evaluation}\n"

    tex_template = rf"""
\documentclass[11pt,ngerman,parskip=full]{{scrlttr2}}
\usepackage{{fontspec}}
\setmainfont{{Latin Modern Roman}}
\usepackage[ngerman]{{babel}}
\usepackage{{geometry}}
\geometry{{a4paper, top=25mm, left=25mm, right=25mm, bottom=30mm}}
\usepackage{{url}}

% Sender info
\setkomavar{{fromname}}{{{first_examiner}}}
\setkomavar{{fromaddress}}{{Steinmüllerallee 1\\51643 Gummersbach}}
\setkomavar{{fromphone}}{{+49 2261-8196-6204}}
\setkomavar{{fromemail}}{{{first_examiner_mail}}}
\setkomavar{{place}}{{{place}}}
\setkomavar{{date}}{{{date}}}
\setkomavar{{signature}}{{{first_examiner}}}
\setkomavar{{subject}}{{{escape_for_latex(subject, preserve_latex=False)}}}

% Footer
\setkomavar{{firstfoot}}{{%
  \parbox[t]{{\textwidth}}{{\footnotesize
    Technische Hochschule Köln, Campus Gummersbach \\
    Sitz des Präsidiums: Claudiusstrasse 1, 50678 Köln \\
    www.th-koeln.de \\
    Steuer-Nr.: 214/5817/3402 - USt-IdNr.: DE 122653679 \\
    Bankverbindung: Sparkasse KölnBonn \\
  }}
}}

\begin{document}

\begin{letter}{{{escape_for_latex(recipient, preserve_latex=False)}}}

\opening{{Sehr geehrte Damen und Herren,}}

Bewertung folgender Thesis:\\[1ex]

\textbf{{Titel:}} {escape_for_latex(title, preserve_latex=False)} \\[1ex]
\textbf{{Autor:}} {escape_for_latex(author, preserve_latex=False)} \\[2ex]

\textbf{{Zusammenfassung der Thesis:}} \\
{escape_for_latex(summary, preserve_latex=False)}
{gemini_section}

\textbf{{Protokoll des Kolloquiums:}}\\[1ex]

\textbf{{Fragen {first_examiner}:}}\\

{questions}\\

\textbf{{Fragen {second_examiner}:}}\\

\textbf{{Vortrag:}} xx Minuten\\

Bewertung des Vortrags:

1. Inhaltliche Qualität & Struktur:

Kriterien:
\begin{itemize}
\item Verständlichkeit von Ziel, Problemstellung und Ergebnissen
\item Fachliche Richtigkeit
\item Logischer Aufbau, klarer roter Faden, sinnvolle Schwerpunktsetzung
\item Einhaltung der Zeit
\end{itemize}

Bewertung:
\begin{itemize}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{itemize}

2. Darstellung & Visualisierung:

Kriterien:
\begin{itemize}
\item Unterstützung des Vortrags durch Folien und Visualisierungen
\item Übersichtlichkeit und Angemessenheit der Gestaltung
\item Verständliche Vermittlung auch komplexer Inhalte
\end{itemize}

Bewertung:
\begin{itemize}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{itemize}

3. Präsentation & Auftreten:

Kriterien:
\begin{itemize}
\item Freier, sicherer und verständlicher Vortrag (Sprache, Tempo, Körpersprache)
\item Souveräner Umgang mit Fragen
\item Kritische Reflexion der eigenen Arbeit (Stärken, Grenzen, Ausblick)
\end{itemize}

Bewertung:
\begin{itemize}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{itemize}

Fragen an das Publikum: Ja / Nein \\

Wurden die praktischen Teile (Demo / Code) verständlich dargestellt?

\begin{itemize}
\item ja, live
\item ja, live, aber Fehlerhaft/nicht so gut
\item ja, Video
\item nein
\item nicht möglich
\end{itemize}

Gesamteindruck:

\begin{itemize}
\item sehr gut
\item sehr gut, manche gut
\item gut
\item gut, manche nicht so gut
\item viele nicht so gut oder gar nicht
\end{itemize}

Note des Kolloquiums: .\\[2ex]

Note der Thesis: .\\[2ex]

Gesamtnote (Thesis 3, Kolloquium 1): .\\[2ex]

\closing{{Mit freundlichen Grü{{\ss}}en}}

\end{letter}

\end{document}
"""
    return tex_template
