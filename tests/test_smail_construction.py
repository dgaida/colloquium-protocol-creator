import pytest

from academic_doc_generator.core.email import EmailRecipient


def test_smail_address_standard():
    recipient = EmailRecipient(first_name="Max", last_name="Mustermann", gender="Herr")
    assert recipient.smail_address == "max.mustermann@smail.th-koeln.de"


def test_smail_address_double_first_name_with_space():
    recipient = EmailRecipient(first_name="Hans Georg", last_name="Müller", gender="Herr")
    # ä -> ae, space -> underscore
    assert recipient.smail_address == "hans_georg.mueller@smail.th-koeln.de"


def test_smail_address_double_last_name_with_hyphen():
    recipient = EmailRecipient(first_name="Maria", last_name="Müller-Lüdenscheid", gender="Frau")
    # ü -> ue, hyphen -> underscore
    assert recipient.smail_address == "maria.mueller_luedenscheid@smail.th-koeln.de"


def test_smail_address_special_characters():
    recipient = EmailRecipient(first_name="Groß", last_name="Fuß", gender="Herr")
    # ß -> ss
    assert recipient.smail_address == "gross.fuss@smail.th-koeln.de"


def test_smail_address_multiple_spaces_and_hyphens():
    recipient = EmailRecipient(
        first_name="Hans-Georg Peter", last_name="Von und zu Mühlen", gender="Herr"
    )
    # ü -> ue, space/hyphen -> underscore
    assert recipient.smail_address == "hans_georg_peter.von_und_zu_muehlen@smail.th-koeln.de"


if __name__ == "__main__":
    pytest.main([__file__])
