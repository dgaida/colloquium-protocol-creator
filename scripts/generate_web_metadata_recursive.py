import json
import os
import re
import sys
from datetime import datetime

# Add src to path to ensure we can import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from llm_client import LLMClient

    from academic_doc_generator.core import llm, metadata, pdf, utils
except ImportError as e:
    print(f"Error: Could not import required modules. Make sure you are in the project root. {e}")
    sys.exit(1)

TARGET_WEB_FOLDER = r"D:\TH_Koeln\dgaida.github.io\_student_projects"


def process_folder(folder_path):
    """Process a single folder containing the target config file."""
    config_file = os.path.join(folder_path, "config_dgaida2.github.json")
    if not os.path.exists(config_file):
        return

    print(f"\n--- Processing: {folder_path} ---")
    try:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return

    # Extract LLM configuration from config file
    llm_cfg = config.get("llm", {})
    api_choice = llm_cfg.get("api_choice")
    model = llm_cfg.get("model")
    groq_free = llm_cfg.get("groq_free", False)

    print(f"Initializing LLMClient with model: {model} (API: {api_choice}, groq_free: {groq_free})")
    llm_client = LLMClient(api_choice=api_choice, llm=model)

    pdf_filename = config.get("pdf", {}).get("filename")
    if not pdf_filename:
        print(f"No PDF filename found in {config_file}")
        return

    pdf_path = os.path.join(folder_path, pdf_filename)
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return

    colloquium_date_str = config.get("colloquium", {}).get("date")
    if not colloquium_date_str:
        print(f"No colloquium date found in {config_file}")
        return

    try:
        dt_colloquium = datetime.strptime(colloquium_date_str, "%d.%m.%Y")
        date_str = dt_colloquium.strftime("%Y-%m-%d")
        semester = utils.get_semester(dt_colloquium)
    except ValueError:
        print(f"Invalid date format: {colloquium_date_str}. Expected DD.MM.YYYY")
        return

    print(f"Found PDF: {pdf_filename} and Date: {colloquium_date_str}")

    # 1. Extract text
    pages_text = pdf.extract_text_per_page(pdf_path)

    # 2. Detect language (simple check on first page)
    first_page_text = pages_text.get(0, "")
    if first_page_text:
        prompt = llm.build_prompt(llm.PromptTemplate.DETECT_LANGUAGE, text=first_page_text[:1000])
        language = llm_client.chat_completion([{"role": "user", "content": prompt}]).strip()
        language = "English" if "English" in language else "German"
    else:
        language = "German"

    print(f"Detected language: {language}")

    # 3. Extract metadata and summary using existing core logic
    # We use get_summary_and_metadata_of_pdf as it encapsulates the LLM calls
    summary_latex, doc_metadata = llm.get_summary_and_metadata_of_pdf(
        pdf_path, language, llm_client, groq_free=groq_free
    )

    work_type = f"{doc_metadata.get('bachelor_master', 'Bachelor')}thesis"

    # 4. Generate the Jekyll-compatible metadata file
    # This function creates the .md file and uses the SUMMARIZE_FOR_WEB prompt internally
    md_path = metadata.generate_metadata_file(
        output_folder=folder_path,
        title=doc_metadata.get("title", "Unknown Title"),
        author=doc_metadata.get("author", "Unknown Author"),
        pages_text=pages_text,
        llm_client=llm_client,
        work_type=work_type,
        semester=semester,
        date_str=date_str,
        copy_to_web_folder=False,
        move_to_web_folder=True,
        web_metadata_folder=TARGET_WEB_FOLDER,
    )

    print(f"✅ Generated web metadata: {md_path}")


def main():
    # Allow passing a root directory as argument, default to current dir
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"Starting recursive search in: {os.path.abspath(root_dir)}")

    found_any = False
    for root, _dirs, files in os.walk(root_dir):
        if "config_dgaida2.github.json" in files:
            # Check for existing .md file with pattern NNNN_....md
            existing_md = [f for f in files if re.match(r"^\d{4}_.*\.md$", f)]
            if existing_md:
                print(f"Skipping {root} because {existing_md[0]} already exists.")
                continue
            found_any = True
            process_folder(root)

    if not found_any:
        print("No 'config_dgaida.github.json' files found.")


if __name__ == "__main__":
    main()
