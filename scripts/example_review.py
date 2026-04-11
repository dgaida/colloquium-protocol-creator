# scripts/example_review.py

import os

from llm_client import LLMClient

from academic_doc_generator.review import orchestrator

if __name__ == "__main__":
    # Change name of folder and name of paper PDF here
    folder = os.path.join("..", "..", "Publikationen", "Paper Reviews")
    pdf_filename = "TIMC-25-0786.R1_Proof_hi.pdf"

    # The LLMClient automatically picks up API keys from environment variables or secrets.env
    # You can also pass api_choice="groq" if you want to force Groq
    llm_client = LLMClient()

    pdf_path = os.path.join(folder, pdf_filename)

    # Check if file exists before running
    if os.path.exists(pdf_path):
        orchestrator.run_review_pipeline(pdf_path=pdf_path, llm_client=llm_client, groq_free=True)
    else:
        print(f"File not found: {pdf_path}")
        print("Please adjust the 'folder' and 'pdf_filename' variables in this script.")
