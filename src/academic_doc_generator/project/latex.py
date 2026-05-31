# project_creator/latex.py
"""LaTeX generation for project work grading letters."""

import os
from typing import Optional

from ..core.latex import escape_for_latex
from ..core.types import StudentInfo
from ..core.utils import get_german_possessive_pronoun, get_semester


def create_project_grading_letter_tex(
    filename: str,
    author: str,
    title: str,
    examiner: str,
    contact: str,
    salutation: str,
    work_type: str = "Praxisprojekt",
    place: str = "Gummersbach",
    date: str = r"\today",
    signature_file: str = "signature.png",
    grade_mark: Optional[str] = None,
    students: Optional[list[StudentInfo]] = None,
) -> None:
    """Create a LaTeX file for a project work grading letter with TH Köln footer.

    Args:
        filename: Output path for the LaTeX file.
        author: Author info (name and ID). Used if students is None.
        title: Title of the project work.
        examiner: Name of the examiner.
        contact: Contact address of the examiner.
        salutation: Gender indicator ("Herr" or "Frau") for formal address. Used if students is None.
        work_type: Type of work (default: "Praxisprojekt").
        place: Place of issue (default: "Gummersbach").
        date: Date string (default: LaTeX \\today).
        signature_file: Path to signature image file (default: "signature.png").
        grade_mark: The mark obtained (default: None, results in a blank line).
        students: Optional list of student info dictionaries for group projects.
    """
    semester = get_semester()

    # Escape all text inputs for LaTeX
    title_safe = escape_for_latex(title, preserve_latex=False)
    work_type_safe = escape_for_latex(work_type, preserve_latex=False)

    # Handle mark
    mark_tex = grade_mark if grade_mark is not None else r"\underline{\hspace{2cm}}"

    # Handle multiple authors logic
    if students and len(students) > 1:
        # Multiple authors
        authors_formatted = []
        for s in students:
            s_salutation = s.get("salutation", "Herr/Frau")
            s_name = s.get("name", "Unknown")
            s_id = s.get("id_number", "unknown")
            authors_formatted.append(f"{s_salutation} {s_name}, Matrikelnr. {s_id}")

        authors_str = " und ".join(authors_formatted)
        authors_str_safe = escape_for_latex(authors_str, preserve_latex=False)
        subject_authors = ", ".join([s.get("name", "Unknown") for s in students])
        subject_authors_safe = escape_for_latex(subject_authors, preserve_latex=False)

        body_intro = f"{authors_str_safe},"

        # Use helper for pronoun (plural)
        possessive = get_german_possessive_pronoun(work_type, "Herr/Frau", plural=True)

        body_main = (
            f"haben im {semester} {possessive} {work_type_safe} bei mir gemacht. "
            f"Sie haben die Note {mark_tex} erhalten."
        )
        subject_line = f"{work_type_safe} {subject_authors_safe}"
    else:
        # Single author (either from students list or from author/salutation params)
        if students and len(students) == 1:
            s = students[0]
            current_salutation = s.get("salutation", salutation)
            current_author = f"{s.get('name')}, Matrikelnr. {s.get('id_number')}"
        else:
            current_salutation = salutation
            current_author = author

        author_safe = escape_for_latex(current_author, preserve_latex=False)
        salutation_safe = escape_for_latex(current_salutation, preserve_latex=False)

        # Use helper for pronoun
        possessive = get_german_possessive_pronoun(work_type, current_salutation, plural=False)
        er_sie = "Er" if current_salutation == "Herr" else "Sie"

        body_intro = f"{salutation_safe}\\\\ \\\\ {author_safe},"
        body_main = (
            f"hat im {semester} {possessive} {work_type_safe} bei mir gemacht. "
            f"{er_sie} hat die Note {mark_tex} erhalten."
        )
        subject_line = f"{work_type_safe} {salutation_safe} {author_safe}"

    # Handle signature
    signature_path_safe = signature_file.replace("\\", "/")
    signature_tex = f"\\includegraphics[width=4cm]{{{signature_path_safe}}}"
    if not os.path.exists(signature_file):
        signature_tex = f"""\\iffalse
% Uncomment the following line and provide the path to your signature image
% {signature_tex}
\\fi"""

    rendered_output = f"""\\documentclass[11pt,ngerman,parskip=full]{{scrlttr2}}
\\usepackage{{fontspec}}
\\setmainfont{{Latin Modern Roman}}
\\usepackage[ngerman]{{babel}}
\\usepackage{{geometry}}
\\geometry{{a4paper, top=25mm, left=25mm, right=25mm, bottom=30mm}}
\\usepackage{{graphicx}}

% Sender info
\\setkomavar{{fromname}}{{{examiner}}}
\\setkomavar{{fromaddress}}{{Steinmüllerallee 1\\\\51643 Gummersbach}}
\\setkomavar{{fromphone}}{{+49 2261-8196-6204}}
\\setkomavar{{fromemail}}{{{contact}}}
\\setkomavar{{place}}{{{place}}}
\\setkomavar{{date}}{{{date}}}
\\setkomavar{{subject}}{{{subject_line}}}

% Footer
\\setkomavar{{firstfoot}}{{%
  \\parbox[t]{{\\textwidth}}{{\\footnotesize
    Technische Hochschule Köln, Campus Gummersbach \\\\
    Sitz des Präsidiums: Claudiusstrasse 1, 50678 Köln \\\\
    www.th-koeln.de \\\\
    Steuer-Nr.: 214/5817/3402 - USt-IdNr.: DE 122653679 \\\\
    Bankverbindung: Sparkasse KölnBonn \\\\
    IBAN: DE34 3705 0198 1900 7098 56 - BIC: COLSDE33
  }}
}}

\\begin{{document}}

\\begin{{letter}}{{Prüfungsausschuss der TH Köln}}

\\opening{{Sehr geehrte Mitarbeiter*innen des Prüfungsservice,}}

{body_intro}

{body_main}

Das Thema war:

{title_safe}

\\closing{{Danke und viele Grü{{\\ss}}e,}}

{signature_tex}

\\end{{letter}}

\\end{{document}}
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(rendered_output)
    print(f"LaTeX file for project grading created: {filename}")
