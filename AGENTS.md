# Agent Instructions

Welcome, Agent. To maintain the quality and cleanliness of this repository, please adhere to the following rules:

## Repository Hygiene
- **No Temporary Files**: Do not leave any temporary files (e.g., `changes.txt`, `test_output.log`, or generated `.md` drafts) in the repository root or source directories after completing a task.
- **Clean Workspace**: Ensure that any files created for debugging or intermediate steps are deleted before submission.

## Coding Standards
- **Linter & Formatter**: Always run `ruff` and `black` on your changes.
- **Testing**: Ensure that you run existing tests and add new ones for any new logic (especially for core utilities like `EmailRecipient`).
- **Environment**: If `pytest` is missing, install dependencies using `pip install -r requirements_dev.txt && pip install -e .`.

## Logic Specifics
- **Email Construction**: Student email addresses at TH Köln must follow the format `vorname.nachname@smail.th-koeln.de`.
  - Replace spaces and hyphens with underscores.
  - Convert German umlauts (\"ä\", \"ö\", \"ü\") to \"ae\", \"oe\", \"ue\".
  - Convert \"ß\" to \"ss\".
  - Use lowercase for the entire address.
