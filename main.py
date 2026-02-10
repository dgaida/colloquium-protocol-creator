# main.py

import os

from academic_doc_generator import cli

# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    # change name of folder in which thesis and a config_*.json file is located here

    folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "Student")

    mycfgloader = cli.run_from_config(folder)
