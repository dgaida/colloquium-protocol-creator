import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from academic_doc_generator.core.email import EmailRecipient, FinalGradeEmail
from academic_doc_generator.core.types import ProjectWorkflowConfig
from academic_doc_generator.project.orchestrator import run_project_pipeline


class TestGlobalExaminer:
    @patch("academic_doc_generator.project.orchestrator.load_global_config")
    @patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
    @patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
    @patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
    @patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
    @patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
    @patch("academic_doc_generator.project.orchestrator.EmailGenerator")
    @patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
    @patch("academic_doc_generator.project.orchestrator.pdf")
    @patch("academic_doc_generator.project.orchestrator.generate_metadata_file")
    def test_global_examiner_overrides_metadata(
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
        mock_load_config,
    ):
        """Test that first_examiner from config.yaml is used."""
        # Setup mocks
        mock_load_config.return_value = {"first_examiner": "Global Examiner"}
        mock_extract.return_value = {
            "student_name": "Test Student",
            "first_examiner": "Metadata Examiner",
        }
        mock_gender.return_value = "Herr"
        mock_feedback.return_value = "- Feedback"

        mock_email_gen = MagicMock()
        mock_email.return_value = mock_email_gen

        with tempfile.TemporaryDirectory() as tmpdir:
            config = ProjectWorkflowConfig(
                pdf_path=Path("test.pdf"),
                output_folder=Path(tmpdir),
                compile_pdf=False,
            )
            run_project_pipeline(config)

            # Check LaTeX generation call uses Global Examiner
            _, kwargs = mock_create.call_args
            assert kwargs["examiner"] == "Global Examiner"

            # Check Email generation call uses Global Examiner
            _, kwargs = mock_email_gen.generate_final_mark_email.call_args
            assert kwargs["examiner_name"] == "Global Examiner"

    def test_email_render_robust_to_none_examiner(self):
        """Test that Email templates don't crash when examiner is None."""
        student = EmailRecipient("Max", "Mustermann", "Herr", "12345")
        template = FinalGradeEmail()

        # This should NOT raise AttributeError: 'NoneType' object has no attribute 'title'
        rendered = template.render(student=student, examiner=None)

        assert "Unbekannt" in rendered
        assert "Max Mustermann" in rendered
