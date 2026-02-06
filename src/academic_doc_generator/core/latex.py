"""LaTeX generation and helper functions."""

import os
import re
import subprocess
import unicodedata
from functools import lru_cache
from typing import Dict, List, Optional


@lru_cache(maxsize=1024)
def escape_latex_text(text: str) -> str:
    """Escape text for safe LaTeX insertion (no LaTeX commands preserved).

    Caches results for performance on repeated strings.

    Args:
        text: Input text to escape.

    Returns:
        LaTeX-safe string.
    """
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", text)

    # Remove invisible chars (soft hyphen, zero-width spaces, etc.)
    text = _remove_invisible_chars(text)

    # Replace dash-like characters with plain ASCII hyphen
    text = _normalize_dashes(text, replacement="-")

    # Define all replacements including specials and sharp s
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "„": r"``",
        "“": r"''",
        "ß": r"{\ss}",
    }

    # Use regex to perform all replacements in one pass to avoid double-escaping
    pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
    text = pattern.sub(lambda m: replacements[m.group(0)], text)

    return text


def escape_latex_with_commands(text: str) -> str:
    """Escape text while preserving LaTeX commands like \\textbf{}.

    Use this when the text may contain intentional LaTeX formatting.

    Args:
        text: Input text that may contain LaTeX commands.

    Returns:
        LaTeX-safe string with commands preserved.
    """
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", text)

    # Remove invisible chars
    text = _remove_invisible_chars(text)

    # Replace dash-like characters with LaTeX-safe dash
    text = _normalize_dashes(text, replacement="{-}")

    # German sharp s (using a unique placeholder to avoid being escaped by _escape_special_chars)
    # Actually _escape_special_chars doesn't escape backslash or braces, so it's fine.
    text = text.replace("ß", r"{\ss}")

    # Escape LaTeX specials but don't touch backslashes/braces
    text = _escape_special_chars(text)

    return text


def escape_for_latex(text: str, preserve_latex: bool = True) -> str:
    """Legacy wrapper for LaTeX escaping.

    Args:
        text: Input text.
        preserve_latex: Whether to preserve LaTeX commands.

    Returns:
        Escaped text.
    """
    if preserve_latex:
        return escape_latex_with_commands(text)
    return escape_latex_text(text)


def _remove_invisible_chars(text: str) -> str:
    """Remove soft hyphens, zero-width spaces, etc."""
    for ch in ("\u00ad", "\u200b", "\u200c", "\u200d", "\ufeff"):
        text = text.replace(ch, "")
    return text


def _normalize_dashes(text: str, replacement: str) -> str:
    """Replace all Unicode dash variants with specified replacement."""
    out_chars = []
    for ch in text:
        if unicodedata.category(ch) == "Pd":  # any punctuation-dash
            out_chars.append(replacement)
        else:
            out_chars.append(ch)
    return "".join(out_chars)


def _escape_special_chars(text: str) -> str:
    """Escape standard LaTeX special characters except backslash and braces."""
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "„": r"``",
        "“": r"''",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def return_seite_page(lang: str) -> str:
    """Returns 'Seite' if German, 'page' if English.

    Args:
        lang (str): English or German

    Returns:
        str: "Seite" if German, "page" if English.
    """
    return "Seite" if lang.lower().startswith("german") else "page"


def create_formal_letter_tex(
    filename: str,
    recipient: str,
    subject: str,
    title: str,
    author: str,
    summary: str,
    first_examiner: str,
    second_examiner: str,
    first_examiner_mail: str,
    questions: str,
    place: str = "Gummersbach",
    date: str = r"\today",
    gemini_evaluation: Optional[str] = None,
):
    """Create a LaTeX file for a formal letter with TH Köln footer.

    Args:
        filename (str): Output path for the LaTeX file.
        recipient (str): Recipient of the letter.
        subject (str): Subject line.
        title (str): Thesis title.
        author (str): Author name and matriculation number.
        summary (str): summary of the thesis.
        first_examiner (str): name of first examiner.
        second_examiner (str): name of second examiner.
        first_examiner_mail (str): email of first examiner.
        questions (str): questions from first examiner.
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
\setkomavar{{subject}}{{{escape_latex_text(subject)}}}

% Footer
\setkomavar{{firstfoot}}{{%
  \parbox[t]{{\textwidth}}{{\footnotesize
    Technische Hochschule Köln, Campus Gummersbach \\
    Sitz des Präsidiums: Claudiusstrasse 1, 50678 Köln \\
    www.th-koeln.de \\
    Steuer-Nr.: 214/5817/3402 - USt-IdNr.: DE 122653679 \\
    Bankverbindung: Sparkasse KölnBonn \\
    IBAN: DE34 3705 0198 1900 7098 56 - BIC: COLSDE33
  }}
}}

\begin{{document}}

\begin{{letter}}{{{escape_latex_text(recipient)}}}

\opening{{Sehr geehrte Damen und Herren,}}

Bewertung folgender Thesis:\\[1ex]

\textbf{{Titel:}} {escape_latex_text(title)} \\[1ex]
\textbf{{Autor:}} {escape_latex_text(author)} \\[2ex]

\textbf{{Zusammenfassung der Thesis:}} \\

{summary}


\textbf{{Protokoll des Kolloquiums:}}\\[1ex]

\textbf{{Fragen {first_examiner}:}}\\

{questions}\\


\textbf{{Fragen {second_examiner}:}}\\

\textbf{{Vortrag:}} xx Minuten\\

Bewertung des Vortrags:

1. Inhaltliche Qualität & Struktur:

Kriterien:
\begin{{itemize}}
\item Verständlichkeit von Ziel, Problemstellung und Ergebnissen
\item Fachliche Richtigkeit
\item Logischer Aufbau, klarer roter Faden, sinnvolle Schwerpunktsetzung
\item Einhaltung der Zeit
\end{{itemize}}

Bewertung der Kriterien:

\begin{{itemize}}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{{itemize}}

2. Darstellung & Visualisierung:

Kriterien:
\begin{{itemize}}
\item Unterstützung des Vortrags durch Folien und Visualisierungen
\item Übersichtlichkeit und Angemessenheit der Gestaltung
\item Verständliche Vermittlung auch komplexer Inhalte
\end{{itemize}}

Bewertung der Kriterien:

\begin{{itemize}}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{{itemize}}

3. Präsentation & Auftreten:

Kriterien:
\begin{{itemize}}
\item Freier, sicherer und verständlicher Vortrag (Sprache, Tempo, Körpersprache)
\item Souveräner Umgang mit Fragen
\item Kritische Reflexion der eigenen Arbeit (Stärken, Grenzen, Ausblick)
\end{{itemize}}

Bewertung der Kriterien:

\begin{{itemize}}
\item sehr gut
\item gut
\item befriedigend
\item ausreichend
\end{{itemize}}

Demo:
\begin{{itemize}}
\item ja, live
\item ja, live, aber Fehlerhaft/nicht so gut
\item ja, Video
\item nein
\item nicht möglich
\end{{itemize}}

Fragen konnten beantwortet werden:
\begin{{itemize}}
\item sehr gut
\item sehr gut, manche gut
\item gut
\item gut, manche nicht so gut
\item viele nicht so gut oder gar nicht
\end{{itemize}}

.\\[2ex]

Dauer des Kolloquiums: 45 Minuten
{gemini_section}

\closing{{Mit freundlichen Grü{{\ss}}en}}

\end{{letter}}

\end{{document}}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tex_template)
    print(f"LaTeX file created: {filename}")


def concatenate_comments(
    results: Dict[int, List[dict]], language: str, verbose: bool = False
) -> str:
    """Concatenate rewritten comments into a LaTeX-formatted string.

    Each comment is prefixed with the page number and separated by two
    LaTeX line breaks (\\\\ \\\\) for readability.

    Args:
        results (dict): Dictionary mapping page numbers to lists of rewritten
            comment dictionaries (as returned by `rewrite_comments_in_pdf`).
        language (str): Language of the comments ("German" or "English") to
            determine whether "Seite" or "page" is used as the prefix.
        verbose (bool, optional): If True, prints the concatenated comments.
            Defaults to False.

    Returns:
        str: A LaTeX-ready string with all rewritten comments, separated by
        two line breaks and labeled with their page numbers.
    """
    seite_page = return_seite_page(language)

    questions = " \\\\\n\\\\\n".join(
        f"{seite_page} {page}: {item['rewritten']}"
        for page, items in results.items()
        for item in items
    )

    if verbose:
        print(questions)

    return questions


def compile_latex_to_pdf(
    tex_path: str, output_dir: Optional[str] = None, engine: str = "lualatex"
) -> str:
    """Compile a LaTeX file into a PDF using the specified engine.

    Args:
        tex_path (str): Path to the .tex file.
        output_dir (str, optional): Directory for the PDF. Defaults to same as tex file.
        engine (str, optional): "lualatex" or "pdflatex"

    Returns:
        str: Path to the generated PDF, or an empty string if compilation fails.
    """
    if output_dir is None:
        output_dir = os.path.dirname(tex_path)

    cmd = [
        engine,
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        tex_path,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: LaTeX compilation failed for {tex_path}")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Exit status: {e.returncode}")
        return ""
    except FileNotFoundError:
        print(
            f"❌ Error: LaTeX engine '{engine}' not found. Please ensure it is installed."
        )
        return ""

    pdf_path = os.path.join(
        output_dir, os.path.splitext(os.path.basename(tex_path))[0] + ".pdf"
    )
    return pdf_path
