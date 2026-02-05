import pathlib
import shutil


def generate_api_docs():
    """
    Automates the creation of API documentation markdown files for the project.
    Each Python module in src/academic_doc_generator is mapped to a markdown file
    containing a mkdocstrings identifier.
    Also generates a SUMMARY.md for mkdocs-literate-nav.
    """
    src_root = pathlib.Path("src")
    pkg_root = src_root / "academic_doc_generator"
    api_ref_root = pathlib.Path("docs/api_reference")

    if api_ref_root.exists():
        shutil.rmtree(api_ref_root)
    api_ref_root.mkdir(parents=True, exist_ok=True)

    print(f"Generating API documentation in {api_ref_root}...")

    # For navigation
    nav_lines = ["# Navigation\n"]

    # Sort files to ensure consistent order
    paths = sorted(pkg_root.rglob("*.py"))

    for path in paths:
        # Skip internal or private modules
        if path.name.startswith("_") and path.name != "__init__.py":
            continue

        # Calculate module identifier (e.g., academic_doc_generator.core.pdf_processing)
        rel_path = path.relative_to(src_root)
        module_parts = list(rel_path.with_suffix("").parts)

        if module_parts[-1] == "__init__":
            module_parts.pop()
            if not module_parts:
                continue
            is_index = True
        else:
            is_index = False

        module_identifier = ".".join(module_parts)

        # Calculate target markdown file path
        # Skip 'academic_doc_generator' for the folder structure to keep it cleaner
        rel_module_path = (
            pathlib.Path(*module_parts[1:])
            if len(module_parts) > 1
            else pathlib.Path(".")
        )

        if is_index:
            target_md = api_ref_root / rel_module_path / "index.md"
        else:
            target_md = api_ref_root / rel_module_path.with_suffix(".md")

        target_md.parent.mkdir(parents=True, exist_ok=True)

        with open(target_md, "w", encoding="utf-8") as f:
            f.write(f"# {module_parts[-1]}\n\n")
            f.write(f"::: {module_identifier}\n")

        # Add to nav
        indent = "  " * (len(module_parts) - 1)
        display_name = module_parts[-1]
        link = target_md.relative_to(api_ref_root)
        nav_lines.append(f"{indent}* [{display_name}]({link})\n")

    # Create the SUMMARY.md for literate-nav
    with open(api_ref_root / "SUMMARY.md", "w", encoding="utf-8") as f:
        f.writelines(nav_lines)

    # Also create a main index.md if it doesn't exist or update it
    with open(api_ref_root / "index.md", "w", encoding="utf-8") as f:
        f.write("# API Reference\n\n")
        f.write("Welcome to the API reference for the Academic Document Generator.\n\n")
        f.write("::: academic_doc_generator\n")

    print("Done!")


if __name__ == "__main__":
    generate_api_docs()
