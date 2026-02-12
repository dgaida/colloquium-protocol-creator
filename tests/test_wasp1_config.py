
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from academic_doc_generator.core.types import ProjectWorkflowConfig
from academic_doc_generator.project.orchestrator import run_project_pipeline

class TestWASP1Config:
    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
    @patch("academic_doc_generator.project.orchestrator.EmailGenerator")
    @patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
    @patch("academic_doc_generator.project.orchestrator.pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    def test_wasp1_work_type_is_used(
        self,
        mock_web,
        mock_pdf_proc,
        mock_outlook,
        mock_email,
        mock_compile,
        mock_create,
        mock_feedback,
        mock_gender,
        mock_extract,
    ):
        """Test that work_type from config is used in all relevant places."""
        # Setup mocks
        mock_extract.return_value = {
            "student_name": "Max Mueller",
            "student_first_name": "Max",
            "id_number": "12345",
            "title": "WASP1 Title",
            "first_examiner": "Prof. Test",
            "first_examiner_christian": "Test",
            "first_examiner_family": "Examiner",
            "work_type": "Praxisprojekt", # LLM thinks it's a Praxisprojekt
        }
        mock_gender.return_value = "Herr"
        mock_feedback.return_value = "- Feedback"
        mock_compile.return_value = "/test/output.pdf"

        mock_email_gen = MagicMock()
        mock_email_gen.generate_final_mark_email.return_value = "Email"
        mock_email.return_value = mock_email_gen

        mock_outlook_gen = MagicMock()
        mock_outlook.return_value = mock_outlook_gen

        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Config with WASP1 work type
            config = ProjectWorkflowConfig(
                pdf_path=Path("test.pdf"),
                llm_client=mock_client,
                output_folder=Path(tmpdir),
                compile_pdf=False,
                work_type="Projektteil WASP1",
                mark="1.0"
            )

            run_project_pipeline(config)

            # 1. Check LaTeX generation call
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            assert kwargs["work_type"] == "Projektteil WASP1"

            # 2. Check Outlook mail subjects
            # First call is to Service, second to Student (if Outlook open)
            service_mail_call = mock_outlook_gen.create_outlook_mail.call_args_list[0]
            assert "Projektteil WASP1" in service_mail_call.kwargs["subject"]

            # 3. Check Web Metadata call
            mock_web.assert_called_once()
            args, kwargs = mock_web.call_args
            assert kwargs["work_type"] == "Projektteil WASP1"
