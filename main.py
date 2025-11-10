# main.py

import os
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    # change name of folder and name of thesis here
    folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "xy")
    pdf_filename = "Bachelorarbeit_xy.pdf"

    # Create LLMClient - will automatically detect available API
    # You can also specify: LLMClient(api_choice="openai", llm="gpt-4o")
    llm_client = LLMClient()

    print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    pdf_path = os.path.join(folder, pdf_filename)

    orchestrator.run_pipeline(
        pdf_path=pdf_path,
        llm_client=llm_client,
        groq_free=True  # Set to False if not using free tier
    )
