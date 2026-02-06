# project_creator/latex.py
"""LaTeX generation for project work grading letters."""

import os
from typing import Optional
from ..core.latex import escape_for_latex
from ..core.utils import get_semester


def create_project_grading_letter_tex(
    filename: str,
    s_name: str,
    s_id: str,
    p_title: str,
    e_name: str,
    e_contact: str,
    gender: str,
    work_type: str = "Praxisprojekt",
    place: str = "Gummersbach",
    date: str = r"\today",
    signature_file: str = "signature.png",
    s_valuation: Optional[str] = None,
) -> None:
    """Create a LaTeX file for a project work grading letter with TH Köln footer.

    Args:
        filename: Output path for the LaTeX file.
        s_name: Full name of the student.
        s_id: Student's matriculation number.
        p_title: Title of the project work.
        e_name: Name of the examiner.
        e_contact: Email address of the examiner.
        gender: Gender indicator ("Herr" or "Frau") for formal address.
        work_type: Type of work (default: "Praxisprojekt").
        place: Place of issue (default: "Gummersbach").
        date: Date string (default: LaTeX \\today).
        signature_file: Path to signature image file (default: "signature.png").
        s_valuation: The valuation obtained (default: None, results in a blank line).
    """
    semester = get_semester()

    # Escape all text inputs for LaTeX
    s_name_safe = escape_for_latex(s_name, preserve_latex=False)
    p_title_safe = escape_for_latex(p_title, preserve_latex=False)
    work_type_safe = escape_for_latex(work_type, preserve_latex=False)

    sein_ihr = "sein" if gender == "Herr" else "ihr"
    er_sie = "Er" if gender == "Herr" else "Sie"

    # Handle valuation
    valuation_tex = (
        s_valuation if s_valuation is not None else r"\underline{\hspace{2cm}}"
    )

    # Handle signature
    signature_path_safe = signature_file.replace("\\", "/")
    signature_tex = f"\\includegraphics[width=4cm]{{{signature_path_safe}}}"
    if not os.path.exists(signature_file):
        signature_tex = f"""\\iffalse
% Uncomment the following line and provide the path to your signature image
% {signature_tex}
\\fi"""

    doc_body = f"""\\documentclass[11pt,ngerman,parskip=full]{{scrlttr2}}
\\usepackage{{fontspec}}
\\setmainfont{{Latin Modern Roman}}
\\usepackage[ngerman]{{babel}}
\\usepackage{{geometry}}
\\geometry{{a4paper, top=25mm, left=25mm, right=25mm, bottom=30mm}}
\\usepackage{{graphicx}}

% Sender info
\\setkomavar{{fromname}}{{{e_name}}}
\\setkomavar{{fromaddress}}{{Steinmüllerallee 1\\\\51643 Gummersbach}}
\\setkomavar{{fromphone}}{{+49 2261-8196-6204}}
\\setkomavar{{fromemail}}{{{e_contact}}}
\\setkomavar{{place}}{{{place}}}
\\setkomavar{{date}}{{{date}}}
\\setkomavar{{subject}}{{{work_type_safe} {gender} {s_name_safe}}}

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

{gender}

{s_name_safe}, Matrikelnr. {s_id},

hat im {semester} {sein_ihr} {work_type_safe} bei mir gemacht. {er_sie} hat die Note {valuation_tex} erhalten.

Das Thema war:

{p_title_safe}

\\closing{{Danke und viele Grü{{\\ss}}e,}}

{signature_tex}

\\end{{letter}}

\\end{{document}}
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(doc_body)
    print(f"LaTeX file for project grading created: {filename}")
