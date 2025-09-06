#

import os
from colloquium_pipeline import orchestrator


# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    # change name of folder and name of thesis here
    folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "xy")
    pdf_filename = "Bachelorarbeit_xy.pdf"

    # make sure you have an API key from groq
    # for google colab
    # from google.colab import userdata
    # groq_api_key = userdata.get("GROQ_API_KEY")

    groq_api_key = os.getenv("GROQ_API_KEY")

    pdf_path = os.path.join(folder, pdf_filename)

    orchestrator.run_pipeline(
        pdf_path=pdf_path,
        groq_api_key=groq_api_key,
        groq_free=True
    )

