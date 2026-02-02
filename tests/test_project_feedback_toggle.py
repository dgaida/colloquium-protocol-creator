
from unittest.mock import MagicMock, patch
from academic_doc_generator.project.orchestrator import run_project_pipeline

@patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
@patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
@patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
@patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
@patch("academic_doc_generator.project.orchestrator.EmailGenerator")
@patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
@patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
def test_run_project_pipeline_feedback_toggle(
    mock_outlook_gen,
    mock_feedback_summary,
    mock_email_gen_class,
    mock_compile,
    mock_create_tex,
    mock_gender,
    mock_metadata,
    tmp_path
):
    # Setup mocks
    mock_metadata.return_value = {
        "student_name": "Max Mustermann",
        "matriculation_number": "123456",
        "title": "Test Title",
        "first_examiner": "Prof. Test",
        "work_type": "Praxisprojekt"
    }
    mock_gender.return_value = "Herr"

    mock_email_gen = MagicMock()
    mock_email_gen_class.return_value = mock_email_gen
    mock_email_gen.save_email_to_markdown.side_effect = ["service_email.md", "student_email.md"]

    mock_outlook = MagicMock()
    mock_outlook_gen.return_value = mock_outlook
    mock_outlook.is_outlook_open.return_value = True

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy")

    # Case 1: create_feedback_mail = True (default)
    result = run_project_pipeline(
        pdf_path=pdf_file,
        grade="1.0",
        output_folder=tmp_path,
        create_feedback_mail=True
    )

    assert result[3] == "student_email.md"
    mock_feedback_summary.assert_called_once()
    assert mock_outlook.create_outlook_mail.call_count == 2

    # Reset mocks for next case
    mock_feedback_summary.reset_mock()
    mock_outlook.create_outlook_mail.reset_mock()
    mock_email_gen.save_email_to_markdown.side_effect = ["service_email.md"]

    # Case 2: create_feedback_mail = False
    result = run_project_pipeline(
        pdf_path=pdf_file,
        grade="1.0",
        output_folder=tmp_path,
        create_feedback_mail=False
    )

    assert result[3] == ""
    mock_feedback_summary.assert_not_called()
    # Only 1 Outlook mail (for Prüfungsservice) should be created
    assert mock_outlook.create_outlook_mail.call_count == 1
