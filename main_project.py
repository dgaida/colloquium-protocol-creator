# main_project.py
"""Example script for generating project work grading letters."""

import os
from project_pipeline import orchestrator


if __name__ == "__main__":
    # Change folder and filename to match your project work
    folder = os.path.join("..", "Projektarbeiten", "2025_SoSe", "xy")
    pdf_filename = "Praxisprojekt_xy.pdf"
    
    # Get Groq API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if groq_api_key is None:
        raise RuntimeError(
            "GROQ_API_KEY environment variable not set. "
            "Please set it with: export GROQ_API_KEY='your_key_here'"
        )
    
    pdf_path = os.path.join(folder, pdf_filename)
    
    # Optional: provide path to your signature image
    # signature_path = os.path.join(folder, "signature.png")
    
    tex_file, pdf_file = orchestrator.run_project_pipeline(
        pdf_path=pdf_path,
        groq_api_key=groq_api_key,
        # signature_file=signature_path  # uncomment if you have a signature
    )
    
    print(f"\n✓ LaTeX file created: {tex_file}")
    if pdf_file:
        print(f"✓ PDF file created: {pdf_file}")
