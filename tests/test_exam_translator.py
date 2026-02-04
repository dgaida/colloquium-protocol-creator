
from unittest.mock import MagicMock, patch
from academic_doc_generator.exam_translator.translator import (
    split_latex_exam_into_sections,
    translate_latex_exam,
    mask_comments,
    unmask_comments
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
    assert "% \question Commented Q2" in questions[0]
    assert "Active Q3" in questions[1]
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
    mock_llm.chat_completion.side_effect = lambda messages: messages[0]['content'].split("German LaTeX question to translate:")[1].split("Translated English LaTeX question:")[0].strip() if "German LaTeX question to translate:" in messages[0]['content'] else messages[0]['content']

    # Simpler mock for this test
    # In each section, placeholders start from %%COMMENT_0%%
    def side_effect(messages):
        content = messages[0]['content']
        if "German LaTeX preamble:" in content:
            return "Translated Preamble\n%%COMMENT_0%%"
        if "German LaTeX question to translate:" in content:
            return "Translated Question\n%%COMMENT_0%%"
        return content

    mock_llm.chat_completion.side_effect = side_effect

    with patch("builtins.open", MagicMock()):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("academic_doc_generator.exam_translator.translator.split_latex_exam_into_sections") as mock_split:
                mock_split.return_value = (
                    r"\documentclass{exam}" + "\n" + r"% Preamble Comment" + "\n" + r"\begin{questions}",
                    [r"\question German Question" + "\n" + r"% Question Comment"],
                    r"\end{questions}" + "\n" + r"\end{document}"
                )

                # Mocking file writing
                output_file = "test_engl.tex"
                with patch("academic_doc_generator.exam_translator.translator.open", create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value = MagicMock()

                    translate_latex_exam("test.tex", llm_client=mock_llm, output_path=output_file)

                    # Get the written content
                    args, kwargs = mock_open.return_value.__enter__.return_value.write.call_args
                    written_content = args[0]

                    assert "% Preamble Comment" in written_content
                    assert "% Question Comment" in written_content
                    assert "Translated Preamble" in written_content
                    assert "Translated Question" in written_content
