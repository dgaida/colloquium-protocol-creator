# colloquium_creator/utils.py
"""Small utility helpers."""

import glob
import os
from typing import Optional


def find_latest_tex(folder: str, pattern: str = "bewertung_brief_*.tex") -> Optional[str]:
    """Find the most recently modified TeX file in a folder matching a pattern.

    This function searches for files in the given folder whose names match
    a specified glob pattern (e.g., ``bewertung_brief_*.tex``). If one or more
    files match, the function returns the path to the file with the most
    recent modification time. If no files match, it returns ``None``.

    Args:
        folder: Path to the folder where TeX files are searched.
        pattern: Glob pattern for matching file names.
            Defaults to ``"bewertung_brief_*.tex"``.

    Returns:
        The absolute path to the newest matching TeX file as a string,
        or ``None`` if no file matches the pattern.

    Raises:
        None directly, but errors may propagate if:
            * The provided folder does not exist.
            * There are permission issues when accessing the folder.

    Example:
        >>> find_latest_tex("/tmp", "bewertung_brief_*.tex")
        '/tmp/bewertung_brief_12345.tex'

    Notes:
        - The "newest" file is determined by the last modification time
          (`os.path.getmtime`).
        - The function returns an absolute path suitable for further processing,
          e.g., compilation with LuaLaTeX.
    """
    pat = os.path.join(folder, pattern)
    matches = glob.glob(pat)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)
