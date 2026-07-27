# src/academic_doc_generator/exam_translator/translator.py
"""Modul zur Übersetzung von LaTeX-Klausuren (exam-Klasse) von Deutsch nach Englisch."""

import logging
import re
from pathlib import Path

from llm_client import LLMClient

from ..core.prompts import PromptTemplate, build_prompt


def setup_exam_translator_logger(log_file: str = "exam_translator.log") -> logging.Logger:
    """Sets up and configures the 'exam_translator' logger.

    Logs are written to the specified file (default: 'exam_translator.log')
    in the current working directory.

    Args:
        log_file: Path to the log file.

    Returns:
        logging.Logger: The configured Logger instance.
    """
    logger = logging.getLogger("exam_translator")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if the logger is already initialized
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def mask_comments(text: str) -> tuple[str, dict[str, str]]:
    """Ersetzt Zeilen, die mit % beginnen, durch Platzhalter.

    Args:
        text: Der LaTeX-Text.

    Returns:
        Tuple aus (maskierter_text, comment_map):
        - maskierter_text: Text mit Platzhaltern
        - comment_map: Mapping von Platzhalter zu Originalzeile
    """
    lines = text.splitlines()
    masked_lines = []
    comment_map: dict[str, str] = {}

    for line in lines:
        if line.strip().startswith("%"):
            placeholder = f"%%COMMENT_{len(comment_map)}%%"
            comment_map[placeholder] = line
            masked_lines.append(placeholder)
        else:
            masked_lines.append(line)

    return "\n".join(masked_lines), comment_map


def unmask_comments(text: str, comment_map: dict[str, str]) -> str:
    """Stellt die ursprünglichen Kommentare aus den Platzhaltern wieder her.

    Args:
        text: Der übersetzte Text mit Platzhaltern.
        comment_map: Mapping von Platzhalter zu Originalzeile.

    Returns:
        Der Text mit wiederhergestellten Kommentaren.
    """

    def replace_func(match):
        return comment_map.get(match.group(0), match.group(0))

    return re.sub(r"%%COMMENT_\d+%%", replace_func, text)


def split_latex_exam_into_sections(
    latex_content: str, verbose: bool = False
) -> tuple[str, list[str], str]:
    """Teilt ein LaTeX-Dokument in Präambel, Fragen und Postamble auf.

    Ignoriert auskommentierte \\begin{questions} und \\end{questions} Befehle.

    Args:
        latex_content: Der komplette LaTeX-Quelltext.
        verbose: Wenn True, werden zusätzliche Informationen ausgegeben.

    Returns:
        Tuple aus (preamble, questions_list, postamble):
        - preamble: Der Teil vor \\begin{questions} inklusive \\begin{questions}
        - questions_list: Liste der einzelnen Fragen, die jeweils mit \\question beginnen
        - postamble: Der Teil ab \\end{questions} inklusive \\end{questions}

    Example:
        >>> preamble, questions, postamble = split_latex_exam_into_sections(latex_text)
        >>> len(questions)
        5
    """
    # Finde den Anfang der Questions-Umgebung (nicht am Zeilenanfang auskommentiert)
    # Nutze [^\n%]*?, um sicherzustellen, dass kein % vor \begin{questions} steht.
    match = re.search(r"(?m)^(?![ \t]*%)[^\n%]*?\\begin\{questions\}", latex_content)

    if not match:
        raise ValueError("Keine \\begin{questions} Umgebung gefunden!")

    # Präambel ist alles bis einschließlich \begin{questions}
    preamble_end = match.end()
    preamble = latex_content[:preamble_end]

    # Rest des Dokuments
    remaining = latex_content[preamble_end:]

    # Finde das Ende der Questions-Umgebung (nicht am Zeilenanfang auskommentiert)
    end_match = re.search(r"(?m)^(?![ \t]*%)[^\n%]*?\\end\{questions\}", remaining)

    if not end_match:
        raise ValueError("Keine \\end{questions} Umgebung gefunden!")

    # Nur der Teil zwischen \begin{questions} und \end{questions}
    questions_content = remaining[: end_match.start()]
    postamble = remaining[end_match.start() :]  # \end{questions} und alles danach

    # Teile in einzelne Questions auf (beginnend mit \question)
    # Nutze einen lookahead, um \question als Delimiter zu verwenden,
    # aber nur wenn es nicht am Zeilenanfang auskommentiert ist.
    # [ \t]* erlaubt eingerückte Fragen.
    question_pattern = r"(?m)^(?![ \t]*%)[ \t]*(?=\\question)"
    questions_raw = re.split(question_pattern, questions_content)

    # Entferne leere Strings und Whitespace-only Einträge
    questions = [q.strip() for q in questions_raw if q.strip()]

    return preamble, questions, postamble


def translate_question_to_english(
    question_text: str, llm_client: LLMClient, verbose: bool = False
) -> str:
    """Übersetzt einen einzelnen Frage-Abschnitt von Deutsch nach Englisch.

    Args:
        question_text: Der LaTeX-Code einer einzelnen Frage (beginnt mit \\question).
        llm_client: LLMClient-Instanz für API-Zugriff.
        verbose: Wenn True, werden Debug-Informationen ausgegeben.

    Returns:
        Der übersetzte LaTeX-Code der Frage.

    Example:
        >>> client = LLMClient()
        >>> translated = translate_question_to_english(question, client)
    """
    # Maskiere Kommentare vor der Übersetzung
    masked_text, comment_map = mask_comments(question_text)

    prompt = build_prompt(PromptTemplate.TRANSLATE_QUESTION, text=masked_text)

    messages = [{"role": "user", "content": prompt}]
    translated = llm_client.chat_completion(messages)

    if verbose:
        print(f"\n{'=' * 60}")
        print("ORIGINAL:")
        print(question_text[:200] + "...")
        print(f"\n{'=' * 60}")
        print("TRANSLATED:")
        print(translated[:200] + "...")
        print(f"{'=' * 60}\n")

    # Stelle Kommentare wieder her
    return unmask_comments(translated, comment_map).strip()


def translate_preamble_to_english(
    preamble: str, llm_client: LLMClient, verbose: bool = False
) -> str:
    """Übersetzt die Präambel (Header, Anweisungen) von Deutsch nach Englisch.

    Args:
        preamble: Der Präambel-Teil des LaTeX-Dokuments.
        llm_client: LLMClient-Instanz für API-Zugriff.
        verbose: Wenn True, werden Debug-Informationen ausgegeben.

    Returns:
        Die übersetzte Präambel.
    """
    # Maskiere Kommentare vor der Übersetzung
    masked_text, comment_map = mask_comments(preamble)

    prompt = build_prompt(PromptTemplate.TRANSLATE_PREAMBLE, text=masked_text)

    messages = [{"role": "user", "content": prompt}]
    translated = llm_client.chat_completion(messages)

    if verbose:
        print(f"\n{'=' * 60}")
        print("PREAMBLE TRANSLATED")
        print(f"Länge Preamble: {len(preamble)}, Länge translated Preamble: {len(translated)}")
        if len(translated) < len(preamble) - 500:
            print(translated)
        print(f"{'=' * 60}\n")

    # Stelle Kommentare wieder her
    return unmask_comments(translated, comment_map).strip()


def translate_latex_exam(
    input_path: str | Path,
    llm_client: LLMClient = None,
    output_path: str | Path = None,
    verbose: bool = False,
) -> str:
    """Übersetzt eine komplette LaTeX-Klausur von Deutsch nach Englisch.

    Diese Funktion:
    1. Liest die LaTeX-Datei ein
    2. Teilt sie in Präambel und einzelne Fragen auf
    3. Übersetzt jeden Abschnitt einzeln mit dem LLM
    4. Fügt alle übersetzten Teile wieder zusammen
    5. Speichert das Ergebnis mit Suffix "_engl"

    Args:
        input_path: Pfad zur deutschen LaTeX-Klausur.
        llm_client: LLMClient-Instanz. Wenn None, wird eine neue erstellt.
        output_path: Pfad für die englische Ausgabe. Wenn None, wird automatisch
                    der Eingabepfad mit Suffix "_engl" verwendet.
        verbose: Wenn True, werden Debug-Informationen ausgegeben.

    Returns:
        Pfad zur gespeicherten englischen LaTeX-Datei.

    Raises:
        FileNotFoundError: Wenn die Eingabedatei nicht existiert.
        ValueError: Wenn die LaTeX-Struktur nicht korrekt ist.

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()
        >>> output = translate_latex_exam("KIKlausurSoSe25_1.tex", client)
        >>> print(output)
        KIKlausurSoSe25_1_engl.tex
    """
    logger = setup_exam_translator_logger()
    logger.info("=== Starte Übersetzung von LaTeX-Klausur ===")
    logger.info(f"Input: {input_path}")

    # Erstelle LLMClient falls nicht vorhanden
    if llm_client is None:
        llm_client = LLMClient(api_choice="kiconnect", llm="openai-gpt-oss-120b")
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")

    # Konvertiere zu Path-Objekten
    input_path = Path(input_path)

    if not input_path.exists():
        logger.error(f"Datei nicht gefunden: {input_path}")
        raise FileNotFoundError(f"Datei nicht gefunden: {input_path}")

    # Bestimme Output-Pfad
    if output_path is None:
        stem = input_path.stem  # Dateiname ohne Endung
        suffix = input_path.suffix  # .tex
        output_path = input_path.parent / f"{stem}_engl{suffix}"
    else:
        output_path = Path(output_path)

    logger.info(f"Output: {output_path}")
    print(f"\n📄 Lese LaTeX-Datei: {input_path}")

    # Lese Input-Datei
    with open(input_path, encoding="utf-8") as f:
        latex_content = f.read()

    print("✂️  Teile Dokument in Abschnitte...")

    # Teile in Abschnitte
    preamble, questions, postamble = split_latex_exam_into_sections(latex_content, verbose)

    print(f"   • Präambel: {len(preamble)} Zeichen")
    print(f"   • Anzahl Fragen: {len(questions)}")
    print(f"   • Postamble: {len(postamble)} Zeichen")

    logger.info("Abschnittsaufteilung:")
    logger.info(f"  - Präambel: {len(preamble)} Zeichen")
    logger.info(f"  - Anzahl Fragen: {len(questions)}")
    logger.info(f"  - Postamble: {len(postamble)} Zeichen")

    # Übersetze Präambel
    print("\n🌍 Übersetze Präambel...")
    translated_preamble = translate_preamble_to_english(preamble, llm_client, verbose=verbose)

    # Übersetze jede Frage einzeln
    print(f"\n🌍 Übersetze {len(questions)} Fragen...")
    translated_questions = []

    for i, question in enumerate(questions, start=1):
        print(f"   [{i}/{len(questions)}] Übersetze Frage {i}...")
        logger.info(f"--- Starte Übersetzung von Frage {i}/{len(questions)} ---")
        logger.info(f"Original Frage {i}:\n{question}")

        translated = translate_question_to_english(question, llm_client, verbose=verbose)

        logger.info(f"Übersetzte Frage {i}:\n{translated}")
        logger.info(f"--- Ende Übersetzung von Frage {i}/{len(questions)} ---\n")
        translated_questions.append(translated)

    # Füge alles zusammen
    print("\n🔗 Füge übersetzte Abschnitte zusammen...")

    # Stelle sicher, dass Questions mit Newline beginnen
    questions_text = "\n\n".join(translated_questions)

    translated_content = f"{translated_preamble}\n\n{questions_text}\n\n{postamble}"

    # Speichere Ergebnis
    print(f"\n💾 Speichere englische Version: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print("✅ Übersetzung abgeschlossen!")
    print(f"   Original: {input_path}")
    print(f"   Übersetzt: {output_path}")

    logger.info("✅ LaTeX-Übersetzung erfolgreich abgeschlossen!")
    logger.info(f"Gespeichert unter: {output_path}")
    logger.info("============================================\n")

    return str(output_path)
