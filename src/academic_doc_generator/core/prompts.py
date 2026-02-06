"""Centralized LLM prompt templates."""

from enum import Enum
from typing import Any


class PromptTemplate(Enum):
    """Collection of LLM prompt templates."""

    REWRITE_COMMENT = """
You are given a PDF paragraph, a highlighted text (the exact words the reader commented on),
and the original rough comment/annotation.

Your task: Rewrite the comment into a clear, polite, and specific question or feedback that
directly refers to the highlighted text and is understandable in the context of the paragraph.

IMPORTANT:
- Detect the language of the original comment.
- Always produce the rewritten comment in the SAME language (usually German, sometimes English).
- Format the summary so that it can be directly inserted into a LaTeX document.
- Use normal LaTeX text, not markdown.

Paragraph:
{paragraph}

Highlighted text:
{highlighted}

Original Comment:
{comment}

Rewritten Comment (same language as original):
"""

    DETECT_DEGREE = """
You are given the filename of a thesis PDF.
Determine if this is a Bachelor thesis or a Master thesis based on the filename.

Filename: {filename}

Common indicators:
- "Bachelor", "BA", "Bachelorarbeit" → Bachelor thesis
- "Master", "MA", "Masterarbeit" → Master thesis

Return ONLY one word: "Bachelor" or "Master"
If you cannot determine it, return "Unknown"
"""

    EXTRACT_METADATA = """
You are given the first pages of a thesis submitted at a University.
It is written in {language}.
Extract the following information if available:

- Author full name
- Matriculation number (Matrikelnr.)
- Title of the thesis
- First examiner (Erstprüfer)
- Christian name of first examiner
- Family name of first examiner
- Second examiner (Zweitprüfer)
- 'Bachelor' if it is a Bachelor thesis or 'Master' if it is a Master thesis
- Course of study (Studiengang). Often find "Studiengang" followed by either "Informatik", "Wirtschaftsinformatik", "Medieninformatik" or "IT-Management".

Return the result as a valid JSON object with keys:
"author", "id_number", "title", "first_examiner", "first_examiner_christian", "first_examiner_family",
"second_examiner", "bachelor_master", "course_of_study".

If something is missing, use null as the value.
Do not include any extra text.

Document text:
{text}
"""

    SUMMARIZE_THESIS = """
You are given the first ten pages of a thesis submitted to a University.
Please provide a concise summary in {language}.

Format the summary so that it can be directly inserted into a LaTeX document.

Formatting rules:
- Use normal LaTeX text, not markdown.
- Use line breaks (`\\\\`) between sentences to improve readability.
- If appropriate, structure the summary as an itemized list with `\\begin{{itemize}} ... \\end{{itemize}}`.
- If you use itemize, then DO NOT add line breaks (`\\\\`) at the end of an item.
- Avoid special characters that break LaTeX (like unescaped #, $, %, &, _, {{, }}).

The summary should highlight:
- The main topic of the thesis
- The research questions or goals
- The methods used
- The key results (if available in the text)

Text:
{text}

Now provide the LaTeX-formatted summary:
"""

    DETECT_LANGUAGE = """
Decide if the following text is written in German or English.
Respond with exactly one word: "German" or "English".

Text:
{text}
"""

    DETERMINE_GENDER = """
Based on the following German or international first name, determine whether
the person should be addressed as "Herr" (Mr.) or "Frau" (Ms./Mrs.) in a
formal German letter.

First name: {first_name}

Respond with ONLY one word: either "Herr" or "Frau".
If uncertain, respond with "Herr/Frau".
"""

    EXTRACT_PROJECT_METADATA = """
You are given the first pages of a project work (Praxisprojekt) submitted
at TH Köln University. Extract the following information if available:

- Student's full name (Autor/Author)
- Student's first name only (Vorname)
- Matriculation number (Matrikelnr.)
- Title of the project work
- First examiner (Erstprüfer/Betreuer)
- Christian name of first examiner
- Family name of first examiner
- Type of work (e.g., "Praxisprojekt", "Projektarbeit")
- Student's email address
- Course of study (Studiengang). Often find "Studiengang" followed by either "Informatik", "Wirtschaftsinformatik", "Medieninformatik" or "IT-Management".

Return the result as a valid JSON object with keys:
"student_name", "student_first_name", "id_number", "title",
"first_examiner", "first_examiner_christian", "first_examiner_family",
"work_type", "student_email", "course_of_study".

If something is missing, use null as the value.
Do not include any extra text, only valid JSON.

Document text:
{text}
"""

    REWRITE_COMMENT_MARKDOWN = """
You are reviewing an academic paper.
Rewrite the following rough reviewer comment into a clear, polite, and constructive
remark addressed to the authors. Keep the meaning, but phrase it in professional
review style. Always write it in English.

Paragraph (if available):
{paragraph}

Highlighted text (if available):
{highlighted}

Original Comment:
{comment}

Rewritten comment (Markdown):
"""

    TRANSLATE_QUESTION = """You are a professional translator specialized in academic LaTeX documents.

Your task: Translate the following LaTeX exam question from German to English.

CRITICAL RULES:
1. PRESERVE ALL LaTeX commands, environments, and formatting EXACTLY as they are
2. PRESERVE ALL mathematical formulas and equations UNCHANGED
3. ONLY translate the German text content to English
4. Keep all \\question, \\part, \\begin{{...}}, \\end{{...}}, etc. commands unchanged
5. Keep all \\choice, \\CorrectChoice commands unchanged
6. Translate text inside solution environments (\\begin{{solutionordottedlines}}, \\begin{{solutionorgrid}}, etc.)
7. Preserve line breaks and spacing
8. Do NOT add explanations or comments
9. Return ONLY the translated LaTeX code
10. Preserve placeholders like %%COMMENT_N%% unchanged and at their original position

Examples of what to preserve:
- Math: $s_1$, $\\gamma = 0.9$, \\[equation\\]
- Commands: \\question[7], \\part[\\half], \\CorrectChoice
- Environments: \\begin{{oneparchoices}}, \\begin{{parts}}
- References: \\ref{{tab:...}}, \\label{{...}}
- Placeholders: %%COMMENT_0%%, %%COMMENT_1%%

German LaTeX question to translate:

{text}

Translated English LaTeX question:
"""

    TRANSLATE_PREAMBLE = """You are a professional translator specialized in academic LaTeX documents.

Your task: Translate the following LaTeX exam preamble/header from German to English.

CRITICAL RULES:
1. PRESERVE ALL LaTeX commands and package declarations EXACTLY
2. ONLY translate German text content in headers, instructions, and labels
3. Translate exam instructions for students
4. Translate header/footer content (course name, exam title, etc.)
5. Translate labels like "Aufgabe Nr.", "Punktzahl:", "Summe", etc.
6. Keep all \\usepackage, \\newcommand, \\setlength commands unchanged
7. Change babel language from ngerman to english where appropriate
8. Do NOT add explanations
9. Return ONLY the translated LaTeX code
10. Preserve placeholders like %%COMMENT_N%% unchanged and at their original position

German LaTeX preamble:

{text}

Translated English LaTeX preamble:
"""

    SUMMARIZE_FOR_WEB = """
You are given the first ten pages of a student's thesis or project report.
Please provide a very concise summary (2-3 sentences) in English that is suitable for publication on a website.
It should be easy to understand for a general audience. Do not write 'A student ...' or mention the student's name, but use passive voice instead.

Text:
{text}

Summary:
"""

    THESIS_EVALUATION = """Du bist ein erfahrener Professor für Informatik an der TH Köln und bewertest eine {niveau}arbeit.

**Titel der Arbeit:** {title}

**Deine Aufgabe:**

1. **Kritische Analyse der Stärken und Schwächen:**
   - Analysiere die gesamte Arbeit gründlich
   - Identifiziere mindestens 5 konkrete Stärken der Arbeit
   - Identifiziere mindestens 5 konkrete Schwächen oder Verbesserungspotenziale
   - Beziehe dich auf spezifische Kapitel, Methoden, Argumente oder Abbildungen
   - Bewerte das Niveau angemessen für eine {niveau}arbeit

2. **Kolloquiumsfragen:**
   - Entwickle genau 10 Fragen für das Kolloquium
   - Die Fragen sollen das Verständnis der Studierenden prüfen
   - Fragen sollen sich auf kritische Stellen, Designentscheidungen und Ergebnisse beziehen
   - Niveau muss einer {niveau}arbeit angemessen sein
   - Mischung aus technischen Details und konzeptionellem Verständnis

**Wichtig:**
- Antworte ausschließlich auf Deutsch
- Formatiere deine Antwort als LaTeX-Text (verwende \\\\, \\textbf{{}}, \\begin{{itemize}}, etc.)
- Escape LaTeX-Sonderzeichen korrekt (verwende \\& statt &, \\% statt %, etc.)
- Sei konstruktiv und professionell
- Gib konkrete Beispiele aus der Arbeit

**Format der Antwort:**

\\textbf{{Stärken der Arbeit:}}

\\begin{{itemize}}
\\item Stärke 1 mit konkretem Bezug
\\item Stärke 2 mit konkretem Bezug
\\item ...
\\end{{itemize}}

\\textbf{{Schwächen und Verbesserungspotenzial:}}

\\begin{{itemize}}
\\item Schwäche 1 mit konkretem Bezug
\\item Schwäche 2 mit konkretem Bezug
\\item ...
\\end{{itemize}}

\\textbf{{Vorgeschlagene Kolloquiumsfragen:}}

\\begin{{enumerate}}
\\item Frage 1
\\item Frage 2
\\item ...
\\item Frage 10
\\end{{enumerate}}
"""

    REWRITE_TO_CONSTRUCTIVE_FEEDBACK = """
Du bist ein Professor und bewertest ein Praxisprojekt eines Studierenden.
Schreibe den folgenden kurzen Korrekturkommentar in ein klares, höfliches und konstruktives
Feedback an den Studierenden um. Behalte die Bedeutung bei, aber formuliere es als professionelles
Feedback (KEINE Fragen, sondern direkte Rückmeldung). Schreibe immer auf Deutsch.

Hervorgehobener Text (falls vorhanden):
{highlighted}

Ursprünglicher Kommentar:
{comment}

Umgeschriebenes Feedback:
"""

    SUMMARIZE_FEEDBACKS = """
Hier sind verschiedene Feedback-Punkte zu einer studentischen Arbeit:
{text}

Fasse dieses Feedback in 3 bis 4 prägnanten Bulletpoints zusammen.
Die Bulletpoints sollen die wichtigsten Stärken und Schwächen der Arbeit hervorheben.
Schreibe auf Deutsch. Starte direkt mit den Bulletpoints.
"""


def build_prompt(template: PromptTemplate, **kwargs: Any) -> str:
    """Build a prompt from template with validation."""
    return template.value.strip().format(**kwargs)
