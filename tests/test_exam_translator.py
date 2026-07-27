from unittest.mock import MagicMock, patch

from academic_doc_generator.exam_translator.translator import (
    mask_comments,
    split_latex_exam_into_sections,
    translate_latex_exam,
    unmask_comments,
)


def test_split_latex_exam_with_comments():
    latex_content = r"""
\documentclass{exam}
% \begin{questions}
\begin{questions}
\question Erste Frage
% \end{questions}
\end{questions}
\end{document}
"""
    preamble, questions, postamble = split_latex_exam_into_sections(latex_content)

    assert r"% \begin{questions}" in preamble
    assert r"\begin{questions}" in preamble
    assert len(questions) == 1
    assert questions[0] == r"\question Erste Frage" + "\n" + r"% \end{questions}"
    assert r"\end{questions}" in postamble


def test_split_latex_exam_ignores_commented_question():
    latex_content = r"""
\begin{questions}
\question Active Q1
% \question Commented Q2
\question Active Q3
\end{questions}
"""
    # minimal document
    full_content = r"\documentclass{exam}" + latex_content + r"\end{document}"
    preamble, questions, postamble = split_latex_exam_into_sections(full_content)

    assert len(questions) == 2
    assert "Active Q1" in questions[0]
    assert r"% \question Commented Q2" in questions[0]
    assert "Active Q3" in questions[1]
    assert r"\end{document}" in postamble


def test_split_latex_exam_with_tabs():
    latex_content = """\\documentclass{exam}
\\begin{document}
\t\\begin{questions}
\t\\question Tabbed Q1
\t\\question Tabbed Q2
\t\\end{questions}
\\end{document}
"""
    preamble, questions, postamble = split_latex_exam_into_sections(latex_content)

    assert "\\begin{questions}" in preamble
    assert len(questions) == 2
    assert "Tabbed Q1" in questions[0]
    assert "Tabbed Q2" in questions[1]
    assert "\\end{questions}" in postamble


def test_split_latex_with_user_complex_data():
    latex_content = r"""\documentclass[a4paper]{exam}
\begin{document}
\begin{center} \fbox{Test} \end{center}
\clearpage
\section*{Szenario}
Text before questions.
	\begin{questions}
		\question Q1
		\question Q2
	\end{questions}\end{document}"""

    preamble, questions, postamble = split_latex_exam_into_sections(latex_content)

    assert r"\begin{document}" in preamble
    assert "Szenario" in preamble
    assert "Text before questions" in preamble
    assert r"\begin{questions}" in preamble
    assert len(questions) == 2
    assert "Q1" in questions[0]
    assert "Q2" in questions[1]
    assert r"\end{questions}" in postamble
    assert r"\end{document}" in postamble


def test_mask_unmask_comments():
    text = r"""\question Eine Frage
% Ein Kommentar
Noch mehr Text
    % Eingerückter Kommentar"""

    masked, comment_map = mask_comments(text)
    assert "%%COMMENT_0%%" in masked
    assert "%%COMMENT_1%%" in masked
    assert "Ein Kommentar" not in masked
    assert "Eingerückter Kommentar" not in masked

    restored = unmask_comments(masked, comment_map)
    assert restored == text


@patch("academic_doc_generator.exam_translator.translator.LLMClient")
def test_translate_exam_preserves_comments(mock_llm_class):
    mock_llm = mock_llm_class.return_value
    # Mock LLM to just return the input (pretending it's translated)
    mock_llm.chat_completion.side_effect = lambda messages: (
        messages[0]["content"]
        .split("German LaTeX question to translate:")[1]
        .split("Translated English LaTeX question:")[0]
        .strip()
        if "German LaTeX question to translate:" in messages[0]["content"]
        else messages[0]["content"]
    )

    # Simpler mock for this test
    # In each section, placeholders start from %%COMMENT_0%%
    def side_effect(messages):
        content = messages[0]["content"]
        if "German LaTeX preamble:" in content:
            return "Translated Preamble\n%%COMMENT_0%%"
        if "German LaTeX question to translate:" in content:
            return "Translated Question\n%%COMMENT_0%%"
        return content

    mock_llm.chat_completion.side_effect = side_effect

    with (
        patch("builtins.open", MagicMock()),
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "academic_doc_generator.exam_translator.translator.split_latex_exam_into_sections"
        ) as mock_split,
    ):
        mock_split.return_value = (
            r"\documentclass{exam}" + "\n" + r"% Preamble Comment" + "\n" + r"\begin{questions}",
            [r"\question German Question" + "\n" + r"% Question Comment"],
            r"\end{questions}" + "\n" + r"\end{document}",
        )

        # Mocking file writing
        output_file = "test_engl.tex"
        with patch(
            "academic_doc_generator.exam_translator.translator.open",
            create=True,
        ) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()

            translate_latex_exam("test.tex", llm_client=mock_llm, output_path=output_file)

            # Get the written content
            args, kwargs = mock_open.return_value.__enter__.return_value.write.call_args
            written_content = args[0]

            assert "% Preamble Comment" in written_content
            assert "% Question Comment" in written_content
            assert "Translated Preamble" in written_content
            assert "Translated Question" in written_content


def test_setup_exam_translator_logger(tmp_path):
    import logging

    from academic_doc_generator.exam_translator.translator import setup_exam_translator_logger

    log_file = tmp_path / "test_logger.log"
    # Ensure any existing handlers from previous tests are cleared to avoid contamination
    logger = logging.getLogger("exam_translator")
    logger.handlers.clear()

    logger = setup_exam_translator_logger(log_file=str(log_file))
    assert logger.name == "exam_translator"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert logger.handlers[0].baseFilename == str(log_file.resolve())


@patch("academic_doc_generator.exam_translator.translator.LLMClient")
def test_translate_latex_exam_logging(mock_llm_class, tmp_path):
    import logging
    from pathlib import Path

    from academic_doc_generator.exam_translator.translator import translate_latex_exam

    mock_llm = mock_llm_class.return_value
    mock_llm.api_choice = "kiconnect"
    mock_llm.llm = "openai-gpt-oss-120b"
    mock_llm.chat_completion.return_value = "Translated section content"

    input_file = tmp_path / "exam.tex"
    output_file = tmp_path / "exam_engl.tex"
    log_file = Path("exam_translator.log")

    # Clean log file if exists before test
    log_file.unlink(missing_ok=True)

    # Clear handlers before test
    logging.getLogger("exam_translator").handlers.clear()

    latex_content = r"""\documentclass{exam}
\begin{questions}
\question Erste Frage
\end{questions}
\end{document}"""

    input_file.write_text(latex_content, encoding="utf-8")

    try:
        translate_latex_exam(input_file, llm_client=mock_llm, output_path=output_file)

        # Verify log file exists and contains expected log messages
        assert log_file.exists()
        log_content = log_file.read_text(encoding="utf-8")
        assert "Starte Übersetzung von LaTeX-Klausur" in log_content
        assert "Original Frage 1:" in log_content
        assert "Erste Frage" in log_content
        assert "Übersetzte Frage 1:" in log_content
        assert "Translated section content" in log_content
        assert "LaTeX-Übersetzung erfolgreich abgeschlossen" in log_content

    finally:
        # Cleanup
        log_file.unlink(missing_ok=True)
        logging.getLogger("exam_translator").handlers.clear()


@patch("academic_doc_generator.exam_translator.xml_translator.LLMClient")
def test_translate_xml_exam_logging(mock_llm_class, tmp_path):
    import logging
    from pathlib import Path

    from academic_doc_generator.exam_translator.xml_translator import translate_xml_exam

    mock_llm = mock_llm_class.return_value
    mock_llm.api_choice = "kiconnect"
    mock_llm.llm = "openai-gpt-oss-120b"
    mock_llm.chat_completion.return_value = "Translated XML content"

    input_file = tmp_path / "exam.xml"
    output_file = tmp_path / "exam_engl.xml"
    log_file = Path("exam_translator.log")

    # Clean log file if exists before test
    log_file.unlink(missing_ok=True)

    # Clear handlers before test
    logging.getLogger("exam_translator").handlers.clear()

    xml_content = """<questestinterop>
<item>
<presentation>
<material>
<mattext texttype="text/xhtml">Erste XML Aufgabe</mattext>
</material>
</presentation>
</item>
</questestinterop>"""

    input_file.write_text(xml_content, encoding="utf-8")

    try:
        translate_xml_exam(input_file, llm_client=mock_llm, output_path=output_file)

        # Verify log file exists and contains expected log messages
        assert log_file.exists()
        log_content = log_file.read_text(encoding="utf-8")
        assert "Starte Übersetzung von XML-Klausur" in log_content
        assert "Original XML-Abschnitt:" in log_content
        assert "Erste XML Aufgabe" in log_content
        assert "Übersetzter XML-Abschnitt:" in log_content
        assert "Translated XML content" in log_content
        assert "XML-Übersetzung erfolgreich abgeschlossen" in log_content

    finally:
        # Cleanup
        log_file.unlink(missing_ok=True)
        logging.getLogger("exam_translator").handlers.clear()
