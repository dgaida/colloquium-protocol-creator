import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock
from academic_doc_generator.exam_translator.xml_translator import translate_xml_exam

def test_translate_xml_exam(tmp_path):
    # Setup test file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<questestinterop>
  <item ident="il_0_quest_123" title="Question 1">
    <presentation>
      <flow>
        <material>
          <mattext texttype="text/xhtml">&lt;p&gt;Betrachten Sie die folgende Konfusionsmatrix&lt;/p&gt;</mattext>
        </material>
      </flow>
    </presentation>
  </item>
</questestinterop>"""

    input_file = tmp_path / "test_exam.xml"
    input_file.write_text(xml_content, encoding="utf-8")

    # Mock LLM Client
    mock_llm = MagicMock()
    mock_llm.chat_completion.return_value = "&lt;p&gt;Consider the following confusion matrix&lt;/p&gt;"
    mock_llm.api_choice = "mock"
    mock_llm.llm = "mock-model"

    output_path = translate_xml_exam(input_file, llm_client=mock_llm)

    # Verify result
    assert os.path.exists(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        translated_xml = f.read()

    assert "&lt;p&gt;Consider the following confusion matrix&lt;/p&gt;" in translated_xml
    assert "<mattext texttype=\"text/xhtml\">" in translated_xml
    assert "</mattext>" in translated_xml
    assert "il_0_quest_123" in translated_xml

def test_translate_xml_exam_complex(tmp_path):
    # Setup test file with complex content
    inner_text = "&lt;p&gt;Betrachten Sie die folgende Konfusionsmatrix&lt;/p&gt;&#13;&#10;&lt;p&gt;&lt;img alt=&quot;&quot; height=&quot;528&quot; src=&quot;il_13890_mob_1186557&quot; title=&quot;konfusion_matrix.png&quot; width=&quot;600&quot; /&gt;&lt;/p&gt;"
    xml_content = f"""<mattext texttype="text/xhtml">{inner_text}</mattext>"""

    input_file = tmp_path / "complex.xml"
    input_file.write_text(xml_content, encoding="utf-8")

    # Mock LLM Client
    mock_llm = MagicMock()
    # Mock should return the "translated" version (we just simulate translation here)
    translated_inner = "&lt;p&gt;Consider the following confusion matrix&lt;/p&gt;&#13;&#10;&lt;p&gt;&lt;img alt=&quot;&quot; height=&quot;528&quot; src=&quot;il_13890_mob_1186557&quot; title=&quot;konfusion_matrix.png&quot; width=&quot;600&quot; /&gt;&lt;/p&gt;"
    mock_llm.chat_completion.return_value = translated_inner

    output_path = translate_xml_exam(input_file, llm_client=mock_llm)

    with open(output_path, "r", encoding="utf-8") as f:
        result = f.read()

    assert translated_inner in result
    assert "height=&quot;528&quot;" in result
    assert "width=&quot;600&quot;" in result
