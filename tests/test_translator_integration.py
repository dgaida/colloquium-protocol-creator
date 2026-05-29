import pytest
from unittest.mock import patch, MagicMock
from academic_doc_generator.cli.main import main
import sys

class TestTranslatorIntegration:
    @patch("academic_doc_generator.cli.handlers.run_translator_direct")
    @patch("academic_doc_generator.core.validation.validate_api_keys")
    def test_translator_subcommand_dispatch(self, mock_validate, mock_handler):
        mock_validate.return_value = ["openai"]
        test_args = ["academic-doc-generator", "translator", "test.xml", "--api", "openai"]

        with patch.object(sys, "argv", test_args):
            main()

        mock_handler.assert_called_once()
        args = mock_handler.call_args[0][0]
        assert args.command == "translator"
        assert args.input == "test.xml"
        assert args.api == "openai"

    @patch("academic_doc_generator.cli.handlers.translate_xml_exam")
    @patch("academic_doc_generator.cli.handlers.LLMClient")
    def test_run_translator_direct_xml(self, mock_llm, mock_translate_xml, tmp_path):
        from academic_doc_generator.cli.handlers import run_translator_direct
        import argparse

        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<root></root>")

        args = argparse.Namespace(
            input=str(xml_file),
            output=None,
            api="openai",
            model="gpt-4",
            verbose=False
        )

        run_translator_direct(args)

        mock_llm.assert_called_once_with(api_choice="openai", llm="gpt-4")
        mock_translate_xml.assert_called_once()
