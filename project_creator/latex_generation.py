# project_creator/latex_generation.py
"""LaTeX generation for project work grading letters."""

from datetime import datetime
from colloquium_creator.latex_generation import escape_for_latex


def get_current_semester() -> str:
    """Determine the current semester based on the current date.
    
    Winter semester (WS) runs from October 1 to end of February.
    Summer semester (SoSe) runs from March 1 to end of September.
    
    Returns:
        str: Semester string in format "WS25/26" or "SoSe25".
    """
    now = datetime.now()
    month = now.month
    year = now.year
    
    if 3 <= month <= 9:
        # Summer semester (March to September)
        return f"SoSe{year % 100}"
    else:
        # Winter semester (October to February)
        if month >= 10:
            return f"WS{year % 100}/{(year + 1) % 100}"
        else:
            return f"WS{(year - 1) % 100}/{year % 100}"


def create_project_grading_letter_tex(
    filename: str,
    student_name: str,
    matriculation_number: str,
    project_title: str,
    examiner_name: str,
    examiner_mail: str,
    gender: str,
    work_type: str = "Praxisprojekt",
    place: str = "Gummersbach",
    date: str = r"\today",
    signature_file: str = "signature.png"
) -> None:
    """Create a LaTeX file for a project work grading letter with TH Köln footer.
    
    Args:
        filename: Output path for the LaTeX file.
        student_name: Full name of the student.
        matriculation_number: Student's matriculation number.
        project_title: Title of the project work.
        examiner_name: Name of the examiner.
        examiner_mail: Email address of the examiner.
        gender: Gender indicator ("Herr" or "Frau") for formal address.
        work_type: Type of work (default: "Praxisprojekt").
        place: Place of issue (default: "Gummersbach").
        date: Date string (default: LaTeX \\today).
        signature_file: Path to signature image file (default: "signature.png").
    """
    semester = get_current_semester()
    
    # Escape all text inputs for LaTeX
    student_name_safe = escape_for_latex(student_name, preserve_latex=False)
    project_title_safe = escape_for_latex(project_title, preserve_latex=False)
    work_type_safe = escape_for_latex(work_type, preserve_latex=False)
    
    tex_template = f"""\\documentclass[11pt,ngerman,parskip=full]{{scrlttr2}}
\\usepackage{{fontspec}}
\\setmainfont{{Latin Modern Roman}}
\\usepackage[ngerman]{{babel}}
\\usepackage{{geometry}}
\\geometry{{a4paper, top=25mm, left=25mm, right=25mm, bottom=30mm}}
\\usepackage{{graphicx}}

% Sender info
\\setkomavar{{fromname}}{{{examiner_name}}}
\\setkomavar{{fromaddress}}{{Steinmüllerallee 1\\\\51643 Gummersbach}}
\\setkomavar{{fromphone}}{{+49 2261-8196-6204}}
\\setkomavar{{fromemail}}{{{examiner_mail}}}
\\setkomavar{{place}}{{{place}}}
\\setkomavar{{date}}{{{date}}}
\\setkomavar{{subject}}{{{work_type_safe} {gender} {student_name_safe}}}

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

{student_name_safe}, Matrikelnr. {matriculation_number},

hat im {semester} sein/ihr {work_type_safe} bei mir gemacht. Er/Sie hat die Note \\underline{{\\hspace{{2cm}}}} erhalten.

Das Thema war:

{project_title_safe}

\\closing{{Danke und viele Grü{{\\ss}}e,}}

\\iffalse
% Uncomment the following line and provide the path to your signature image
% \\includegraphics[width=4cm]{{{signature_file}}}
\\fi

\\end{{letter}}

\\end{{document}}
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tex_template)
    print(f"LaTeX file for project grading created: {filename}")
