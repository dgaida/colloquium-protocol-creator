# colloquium_creator/utils.py
"""Small utility helpers."""

import glob
import os
from typing import Optional


def find_latest_tex(folder: str, pattern: str = "bewertung_brief_*.tex") -> Optional[str]:
    """Return the newest file in folder that matches pattern or None."""
    pat = os.path.join(folder, pattern)
    matches = glob.glob(pat)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)
