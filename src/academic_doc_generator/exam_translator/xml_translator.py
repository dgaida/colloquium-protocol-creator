# src/academic_doc_generator/exam_translator/xml_translator.py
"""Module for translating XML-based exam content (e.g., ILIAS export) from German to English."""

import re
from pathlib import Path
from typing import Optional, Union

from llm_client import LLMClient

from ..core.prompts import PromptTemplate, build_prompt


def translate_xml_exam(
    input_path: Union[str, Path],
    llm_client: Optional[LLMClient] = None,
    output_path: Optional[Union[str, Path]] = None,
    verbose: bool = False,
) -> str:
    """Translates an XML exam file from German to English.

    This function searches for <mattext texttype="text/xhtml">...</mattext> tags
    and translates their content using an LLM, preserving tags and entities.

    Args:
        input_path: Path to the German XML exam file.
        llm_client: LLMClient instance. If None, a new one is created.
        output_path: Path for the English output. If None, a suffix "_engl" is added.
        verbose: If True, prints detailed translation progress.

    Returns:
        Path to the saved English XML file.
    """
    if llm_client is None:
        llm_client = LLMClient()
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_engl{suffix}"
    else:
        output_path = Path(output_path)

    print(f"\n📄 Reading XML file: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        content = f.read()

    # Regex to find mattext tags with xhtml texttype
    # We use a non-greedy match for the content
    pattern = re.compile(r'(<mattext texttype="text/xhtml">)(.*?)(</mattext>)', re.DOTALL)

    matches = list(pattern.finditer(content))
    print(f"🔍 Found {len(matches)} sections to translate.")

    # We process in reverse to not mess up indices if we were doing string slicing,
    # but here we'll use re.sub with a callback for safety and simplicity.

    count = 0

    def replace_match(match):
        nonlocal count
        count += 1
        prefix = match.group(1)
        inner_text = match.group(2)
        suffix = match.group(3)

        if not inner_text.strip():
            return match.group(0)

        print(f"   [{count}/{len(matches)}] Translating section...")

        prompt = build_prompt(PromptTemplate.TRANSLATE_XML_XHTML, text=inner_text)
        messages = [{"role": "user", "content": prompt}]
        translated_text = llm_client.chat_completion(messages).strip()

        if verbose:
            print(f"--- Original ---\n{inner_text}\n--- Translated ---\n{translated_text}\n")

        return f"{prefix}{translated_text}{suffix}"

    final_content = pattern.sub(replace_match, content)

    print(f"\n💾 Saving English version: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print("✅ Translation completed!")
    return str(output_path)
