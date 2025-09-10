#

import os
from review_pipeline import orchestrator


# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    # change name of folder and name of paper here
    folder = os.path.join("..", "Paper Reviews")
    pdf_filename = "paper_for_review.pdf"

    # make sure you have an API key from groq
    # for google colab
    # from google.colab import userdata
    # groq_api_key = userdata.get("GROQ_API_KEY")

    groq_api_key = os.getenv("GROQ_API_KEY")

    pdf_path = os.path.join(folder, pdf_filename)

    orchestrator.run_review_pipeline(
        pdf_path=pdf_path,
        groq_api_key=groq_api_key,
        groq_free=True
    )

