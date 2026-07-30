from unittest.mock import MagicMock, patch

from academic_doc_generator.core.types import ProjectWorkflowConfig
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
    tmp_path,
):
    # Setup mocks
    mock_metadata.return_value = {
        "student_name": "Max Mustermann",
        "student_first_name": "Max",
        "id_number": "123456",
        "title": "Test Title",
        "first_examiner": "Prof. Test",
        "work_type": "Praxisprojekt",
    }
    mock_gender.return_value = "Herr"

    mock_email_gen = MagicMock()
    mock_email_gen_class.return_value = mock_email_gen
    mock_email_gen.save_email_to_markdown.side_effect = [
        "service_email.md",
        "student_email.md",
    ]

    mock_outlook = MagicMock()
    mock_outlook_gen.return_value = mock_outlook
    mock_outlook.is_outlook_open.return_value = True

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy")

    # Case 1: create_feedback_mail = True (default)
    config = ProjectWorkflowConfig(
        pdf_path=pdf_file,
        mark="1.0",
        output_folder=tmp_path,
        create_feedback_mail=True,
    )
    result = run_project_pipeline(config)

    assert result.student_email_path == "student_email.md"
    mock_feedback_summary.assert_called_once()
    assert mock_outlook.create_outlook_mail.call_count == 2

    # Reset mocks for next case
    mock_feedback_summary.reset_mock()
    mock_outlook.create_outlook_mail.reset_mock()
    mock_email_gen.save_email_to_markdown.side_effect = ["service_email.md"]

    # Case 2: create_feedback_mail = False
    config = ProjectWorkflowConfig(
        pdf_path=pdf_file,
        mark="1.0",
        output_folder=tmp_path,
        create_feedback_mail=False,
    )
    result = run_project_pipeline(config)

    assert result.student_email_path == ""
    mock_feedback_summary.assert_not_called()
    # Only 1 Outlook mail (for Prüfungsservice) should be created
    assert mock_outlook.create_outlook_mail.call_count == 1


@patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
@patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
@patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
@patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
@patch("academic_doc_generator.project.orchestrator.EmailGenerator")
@patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
@patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
def test_run_project_pipeline_orchestrator_edge_cases(
    mock_outlook_gen,
    mock_feedback_summary,
    mock_email_gen_class,
    mock_compile,
    mock_create_tex,
    mock_gender,
    mock_metadata,
    tmp_path,
):
    import os
    from io import StringIO
    from unittest.mock import patch

    # 1. Mock metadata: first name is recognized
    mock_metadata.return_value = {
        "student_name": "Max Mustermann",
        "student_first_name": "Max",
        "id_number": "123456",
        "title": "Test Title",
        "first_examiner": "Prof. Test",
        "work_type": "Praxisprojekt",
    }
    mock_gender.return_value = "Herr"

    mock_email_gen = MagicMock()
    mock_email_gen_class.return_value = mock_email_gen

    mock_outlook = MagicMock()
    mock_outlook_gen.return_value = mock_outlook
    mock_outlook.is_outlook_open.return_value = True

    # Force exceptions in create_outlook_mail to cover lines 226-227 and 243-244
    mock_outlook.create_outlook_mail.side_effect = Exception("Outlook error")

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy")

    # Mock os.path.exists to return True specifically for the signature file in data/
    # This covers lines 129-130
    original_exists = os.path.exists

    def mock_exists(path):
        if path == os.path.join("data", "signature.png"):
            return True
        return original_exists(path)

    config = ProjectWorkflowConfig(
        pdf_path=pdf_file,
        mark="1.0",
        output_folder=None,  # covers line 62
        create_feedback_mail=True,
    )

    with (
        patch("os.path.exists", mock_exists),
        patch("sys.stdout", new=StringIO()) as fake_out,
    ):
        run_project_pipeline(config)
        output = fake_out.getvalue()

    # Verify we printed using signature found in data/
    assert "Using signature found in data/signature.png" in output

    # Verify we caught Outlook exception for service mail (lines 226-227)
    assert "Fehler beim Erstellen der Outlook-Mail (Service)" in output

    # Verify we caught Outlook exception for student mail (lines 243-244)
    assert "Fehler beim Erstellen der Outlook-Mail (Student)" in output


@patch("academic_doc_generator.project.orchestrator.extract_project_metadata")
@patch("academic_doc_generator.project.orchestrator.determine_gender_from_name")
@patch("academic_doc_generator.project.orchestrator.create_project_grading_letter_tex")
@patch("academic_doc_generator.project.orchestrator.compile_latex_to_pdf")
@patch("academic_doc_generator.project.orchestrator.EmailGenerator")
@patch("academic_doc_generator.project.orchestrator.generate_feedback_summary")
@patch("academic_doc_generator.project.orchestrator.OutlookMailGenerator")
def test_run_project_pipeline_first_name_not_recognized(
    mock_outlook_gen,
    mock_feedback_summary,
    mock_email_gen_class,
    mock_compile,
    mock_create_tex,
    mock_gender,
    mock_metadata,
    tmp_path,
):
    from io import StringIO
    from unittest.mock import patch

    # Mock metadata: first name is not recognized (student_name is "Unknown")
    mock_metadata.return_value = {
        "student_name": "Unknown",
        "student_first_name": None,
        "id_number": "123456",
        "title": "Test Title",
        "first_examiner": "Prof. Test",
        "work_type": "Praxisprojekt",
    }
    mock_gender.return_value = "Herr"

    mock_email_gen = MagicMock()
    mock_email_gen_class.return_value = mock_email_gen

    mock_outlook = MagicMock()
    mock_outlook_gen.return_value = mock_outlook
    mock_outlook.is_outlook_open.return_value = True

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("dummy")

    config = ProjectWorkflowConfig(
        pdf_path=pdf_file,
        mark="1.0",
        output_folder=None,
        create_feedback_mail=True,
    )

    with patch("sys.stdout", new=StringIO()) as fake_out:
        run_project_pipeline(config)
        output = fake_out.getvalue()

    # Verify warning when first name is not recognized (line 271)
    assert "Warnung: Vorname wurde nicht erkannt" in output
