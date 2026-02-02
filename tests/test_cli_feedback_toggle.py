from academic_doc_generator.cli import create_parser


def test_project_parser_feedback_toggle():
    parser = create_parser()

    # Default should be True
    args = parser.parse_args(["project", "test.pdf"])
    assert args.create_feedback_mail is True

    # --create-feedback-mail should be True
    args = parser.parse_args(["project", "test.pdf", "--create-feedback-mail"])
    assert args.create_feedback_mail is True

    # --no-feedback-mail should be False
    args = parser.parse_args(["project", "test.pdf", "--no-feedback-mail"])
    assert args.create_feedback_mail is False
