# Configuration Guide

This guide explains how to configure the Academic Document Generator using JSON configuration files.

## 📋 Overview

The tool supports JSON-based configuration for three use cases:

- **Colloquium protocols** (thesis defense)  
- **Project work & WASP1 grading** letters  
- **Peer review** comments  

## 🎯 Quick Start

### 1. Choose a Template

```bash
# List available templates
academic-doc-generator --list-templates
```

### 2. Copy and Customize

```bash
# Copy template to your thesis folder
cp config_templates/config_colloquium_campus.json /path/to/thesis/
```

After copying, customize the `config.json` file. At a minimum, you must set the correct PDF filename (`pdf` -> `filename`).

### 3. Run the Tool

**Option A: Use main.py**
You can run the tool via `main.py` in the project root. To do this, edit the `folder` variable in `main.py` to point to the directory containing your PDF and the JSON config.
```bash
python main.py
```

**Option B: Use CLI directly**
```bash
academic-doc-generator --config /path/to/thesis/config_colloquium_campus.json
```

## 📝 Configuration Structure

### Common Fields

#### `output` (optional)

```json
{
  "output": {
    "folder": null,              // null = same as PDF folder
    "compile_pdf": true,         // Compile LaTeX to PDF
    "signature_file": "signature.png", // Path to signature image
    "create_feedback_mail": true // Generate feedback email (for projects)
  }
}
```

- `folder`: Output directory (`null` = PDF's folder)  
- `compile_pdf`: Whether to compile `.tex` to PDF  
- `signature_file`: Path to signature image (defaults to `signature.png` or auto-detected in `data/`)  
- `create_feedback_mail`: Whether to generate student feedback (mainly used in `project` task)  

## 🎓 Colloquium Configuration

```json
{
  "task": "colloquium",
  "colloquium": {
    "date": "20.01.2026",
    "time": "14:00",
    "location_type": "campus",
    "room": "3.217"
  }
}
```

**Metadata Overrides (Optional):**
You can add a `metadata` section to manually set fields if automatic extraction fails:  
- `course_of_study`: e.g., "Informatik", "Medieninformatik"  
- `author`: Student name  

## 📂 Project Configuration

```json
{
  "task": "project",
  "project": {
    "mark": "1.3"
  },
  "output": {
    "create_feedback_mail": true
  }
}
```

## 📄 Review Configuration

```json
{
  "task": "review",
  "pdf": {
    "filename": "paper.pdf"
  }
}
```

## 🔑 API Keys Configuration

Create `secrets.env` in project root:

```bash
OPENAI_API_KEY=sk-xxxxxxxx
GROQ_API_KEY=gsk-xxxxxxxx
GEMINI_API_KEY=AIzaSyxxxxxxxx
```

## 💡 Advanced Options

### Rate Limiting for Free Tiers

```json
{
  "llm": {
    "api_choice": "groq",
    "groq_free": true
  }
}
```

### Fill Form Only Mode

```json
{
  "output": {
    "fill_form_only": true
  }
}
```

## 📝 Configuration Templates

Pre-built JSON configurations for common workflows in the `config_templates/` directory:

- `config_colloquium_campus.json` - Thesis colloquium on campus  
- `config_colloquium_company.json` - Thesis colloquium at a company  
- `config_colloquium_online.json` - Online thesis colloquium (Zoom)  
- `config_project_template.json` - Project work grading  
- `config_wasp1_template.json` - WASP1 project grading  
- `config_review_template.json` - Peer review comments  

## ⚙️ Global Configuration (config.yaml)

In addition to project-specific JSON files, there is a global `config.yaml` in the project root for general settings:

```yaml
# Global folder for web metadata (*.md profiles)
web_metadata_folder: "/path/to/your/website/data/projects/"

# Default first examiner name (overrides PDF extraction)
first_examiner: "Prof. Dr. Firstname Lastname"
```

- `web_metadata_folder`: If set, generated Jekyll-compatible project profiles are automatically copied to this folder.  
- `first_examiner`: A name set here will be used as the first examiner for all generated documents.  

## 🔍 PDF Parser & Web Metadata Behavior

### Default PDF Parser (LiteParse)
[LiteParse](https://github.com/run-llama/liteparse) is now utilized as the default PDF parser for fast and reliable extraction of text and annotation coordinates from PDFs.
If parsing with LiteParse fails (e.g., due to environment issues or corrupt documents), the tool automatically falls back to **Docling** and then to **PyMuPDF**.

### Handling of Unknown Authors
If the author of a thesis or project cannot be identified (i.e., is marked as `Unknown`, `Unknown Author`, or `Unbekannt`), the generated `*.md` project profile with the summary is **not** copied or moved to the configured `web_metadata_folder`. It remains only in your local output folder. This prevents incomplete or invalid profiles from being published on academic pages.

## 📚 Related Documentation

- [Installation Guide](INSTALL.en.md)  
- [Colloquium Documentation](COLLOQUIUM.en.md)  
- [Project Documentation](PROJECT.en.md)  
- [Review Documentation](REVIEW.en.md)  
