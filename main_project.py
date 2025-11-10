# main_project.py
"""Example script for generating project work grading letters."""

import os
from llm_client import LLMClient
from project_pipeline import orchestrator

if __name__ == "__main__":
    # Change folder and filename to match your project work
    folder = os.path.join("..", "Projektarbeiten", "2025_SoSe", "xy")
    pdf_filename = "Praxisprojekt_xy.pdf"

    # Create LLMClient - will automatically detect available API
    # You can also specify: LLMClient(api_choice="openai", llm="gpt-4o")
    llm_client = LLMClient()

    print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    pdf_path = os.path.join(folder, pdf_filename)

    # Optional: provide path to your signature image
    # signature_path = os.path.join(folder, "signature.png")

    tex_file, pdf_file = orchestrator.run_project_pipeline(
        pdf_path=pdf_path,
        llm_client=llm_client,
        # signature_file=signature_path  # uncomment if you have a signature
    )

    print(f"\n✓ LaTeX file created: {tex_file}")
    if pdf_file:
        print(f"✓ PDF file created: {pdf_file}")
