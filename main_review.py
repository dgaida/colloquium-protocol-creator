# main_review.py

import os
from llm_client import LLMClient
from review_pipeline import orchestrator

# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    # change name of folder and name of paper here
    folder = os.path.join("..", "Paper Reviews")
    pdf_filename = "paper_for_review.pdf"

    # Create LLMClient - will automatically detect available API
    # You can also specify: LLMClient(api_choice="gemini", llm="gemini-2.0-flash-exp")
    llm_client = LLMClient()

    print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    pdf_path = os.path.join(folder, pdf_filename)

    orchestrator.run_review_pipeline(
        pdf_path=pdf_path,
        llm_client=llm_client,
        groq_free=True  # Set to False if not using free tier
    )
