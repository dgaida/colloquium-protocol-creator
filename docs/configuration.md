# Configuration Guide

This guide explains how to configure the Academic Document Generator using JSON configuration files.

## 📋 Overview

The tool supports JSON-based configuration for all three use cases:

- **Colloquium protocols** (thesis defense)
- **Project work grading** letters
- **Peer review** comments

## 🎯 Quick Start

### 1. Choose a Template

```bash
# List available templates
colloquium-protocol-creator --list-templates
```

Available templates:

- `config_colloquium_campus.json` - Campus colloquium
- `config_colloquium_company.json` - Company colloquium
- `config_colloquium_online.json` - Online colloquium
- `config_project_template.json` - Project grading
- `config_review_template.json` - Peer review

### 2. Copy and Customize

```bash
# Copy template to your thesis folder
cp config_templates/config_colloquium_campus.json /path/to/thesis/

# Edit the configuration
nano config_colloquium_campus.json
```

### 3. Run the Tool

```bash
# Option A: Use main.py
python main.py  # Edit folder path in main.py first

# Option B: Use CLI directly
colloquium-protocol-creator --config /path/to/thesis/config_colloquium_campus.json
```

## 📝 Configuration Structure

All configuration files follow this structure:

```json
{
  "task": "colloquium|project|review",
  "description": "Human-readable description",
  
  "pdf": {
    "filename": "thesis.pdf"
  },
  
  "llm": {
    "api_choice": null,
    "model": null,
    "groq_free": false
  },
  
  "output": {
    "folder": null,
    "compile_pdf": true
  }
}
```

### Common Fields

#### `task` (required)

Type of task to execute:

- `"colloquium"` - Generate thesis colloquium protocol
- `"project"` - Generate project work grading letter
- `"review"` - Generate peer review comments

#### `pdf` (required)

```json
{
  "pdf": {
    "filename": "Bachelorarbeit_Mustermann.pdf"
  }
}
```

- `filename`: Name of the PDF file (located in same folder as config)

#### `llm` (optional)

```json
{
  "llm": {
    "api_choice": "openai",     // or "groq", "gemini", "ollama", null
    "model": "gpt-4o-mini",     // or null for default
    "groq_free": true           // Enable rate limiting for free tier
  }
}
```

- `api_choice`: LLM provider (`null` = auto-detection)
- `model`: Specific model name (`null` = default for provider)
- `groq_free`: Enable throttling for Groq free tier

#### `output` (optional)

```json
{
  "output": {
    "folder": null,              // null = same as PDF folder
    "compile_pdf": true          // Compile LaTeX to PDF
  }
}
```

- `folder`: Output directory (`null` = PDF's folder)
- `compile_pdf`: Whether to compile `.tex` to PDF

## 🎓 Colloquium Configuration

### Campus Colloquium

```json
{
  "task": "colloquium",
  "pdf": {
    "filename": "Bachelorarbeit_Mustermann.pdf"
  },
  "colloquium": {
    "date": "20.01.2026",
    "time": "14:00",
    "location_type": "campus",
    "room": "3.217"
  },
  "llm": {
    "api_choice": null,
    "model": null,
    "groq_free": true
  },
  "output": {
    "folder": null,
    "compile_pdf": true,
    "fill_form_only": false
  }
}
```

**Required fields for campus:**
- `date`: Format `DD.MM.YYYY`
- `time`: Format `HH:MM`
- `location_type`: Must be `"campus"`
- `room`: Room number (e.g., `"3.217"`)

### Company Colloquium

```json
{
  "task": "colloquium",
  "colloquium": {
    "date": "25.01.2026",
    "time": "10:00",
    "location_type": "company",
    "company_name": "Beispiel GmbH",
    "company_address": "Musterstraße 42, 51643 Gummersbach"
  }
}
```

**Required fields for company:**
- `location_type`: Must be `"company"`
- `company_name`: Company name
- `company_address`: Full address (optional)

### Online Colloquium

```json
{
  "task": "colloquium",
  "colloquium": {
    "date": "30.01.2026",
    "time": "15:30",
    "location_type": "online",
    "zoom_link": "https://zoom.us/j/1234567890",
    "zoom_meeting_access": "ColloquiumXY"
  }
}
```

**Required fields for online:**
- `location_type`: Must be `"online"`
- `zoom_link`: Zoom meeting URL
- `zoom_meeting_access`: Access code (optional)

### Gemini Evaluation (Optional)

Enable automatic thesis evaluation with Google Gemini:

```json
{
  "gemini_evaluation": {
    "enabled": true,
    "model": "gemini-2.0-flash-exp"
  }
}
```

This generates:
- Strengths and weaknesses analysis
- 10 suggested colloquium questions
- Added to LaTeX protocol automatically

## 📂 Project Configuration

```json
{
  "task": "project",
  "pdf": {
    "filename": "Praxisprojekt_Weber.pdf"
  },
  "project": {
    "grade": null
  },
  "llm": {
    "api_choice": null,
    "model": null
  },
  "output": {
    "folder": null,
    "compile_pdf": true,
    "signature_file": "signature.png",
    "create_feedback_mail": true
  }
}
```

**Optional fields:**
- `grade`: Grade for project (e.g., `"1.3"` or `null`)
- `signature_file`: Path to signature image
- `create_feedback_mail`: Generate feedback email for student

## 📄 Review Configuration

```json
{
  "task": "review",
  "pdf": {
    "filename": "paper_submission_42.pdf"
  },
  "llm": {
    "api_choice": null,
    "model": null,
    "groq_free": false
  },
  "output": {
    "folder": null
  }
}
```

Simple configuration - only PDF path and LLM settings needed.

## 🔑 API Keys Configuration

Create `secrets.env` in project root:

```bash
# OpenAI (paid, reliable)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Groq (free tier: 30 requests/minute)
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini (free tier: 60 requests/minute)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ollama - no key needed (local)
```

### API Priority

If multiple keys are present:

1. First checks for specified `api_choice` in config
2. Falls back to auto-detection: OpenAI → Groq → Gemini → Ollama

## 💡 Examples

### Example 1: Campus Colloquium with Custom LLM

```json
{
  "task": "colloquium",
  "pdf": {
    "filename": "Bachelorarbeit_Mustermann.pdf"
  },
  "colloquium": {
    "date": "20.01.2026",
    "time": "14:00",
    "location_type": "campus",
    "room": "3.217"
  },
  "llm": {
    "api_choice": "openai",
    "model": "gpt-4o"
  }
}
```

### Example 2: Project with Signature

```json
{
  "task": "project",
  "pdf": {
    "filename": "Praxisprojekt_Weber.pdf"
  },
  "llm": {
    "api_choice": "gemini"
  },
  "output": {
    "signature_file": "./signatures/prof_mueller.png"
  }
}
```

### Example 3: Review with Rate Limiting

```json
{
  "task": "review",
  "pdf": {
    "filename": "paper.pdf"
  },
  "llm": {
    "api_choice": "groq",
    "groq_free": true
  }
}
```

## 🛠️ Workflow Integration

### Using with `main.py`

```python
# main.py
import os
from academic_doc_generator import cli

folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "Mustermann")
cli.run_from_config(folder)
```

The tool will:
1. Search for `config*.json` in the specified folder
2. Load the first matching config file
3. Execute the configured task

### Using with CLI

```bash
# Direct execution
colloquium-protocol-creator --config /path/to/config.json

# List templates first
colloquium-protocol-creator --list-templates

# Use template directly
colloquium-protocol-creator --config config_templates/config_colloquium_campus.json
```

## 🔧 Advanced Options

### Rate Limiting for Free Tiers

```json
{
  "llm": {
    "api_choice": "groq",
    "groq_free": true  // Adds 4s delay per request, 10s every 5 requests
  }
}
```

Prevents "Too Many Requests" errors on free tiers.

### Fill Form Only Mode

```json
{
  "output": {
    "fill_form_only": true  // Skip protocol generation, only fill PDF form
  }
}
```

Useful for quick form generation without full protocol.

### Custom Output Folder

```json
{
  "output": {
    "folder": "../Output/2025_WS"  // Relative or absolute path
  }
}
```

## ❗ Validation Rules

The configuration is validated before execution:

- ✅ Valid `task` values: `colloquium`, `project`, `review`
- ✅ PDF file must exist in the config's folder
- ✅ Required location fields based on `location_type`
- ✅ Date format: `DD.MM.YYYY`
- ✅ Time format: `HH:MM`

### Error Examples

```json
{
  "task": "invalid"  // ❌ Error: Ungültiger Task
}
```

```json
{
  "colloquium": {
    "location_type": "campus"
    // ❌ Error: 'room' erforderlich für location_type 'campus'
  }
}
```

## 🎯 Tips

1. **Use Relative Paths**: Use `..` for parent directories
2. **Set `null` for Defaults**: Use `null` for auto-detection
3. **Version Control**: Keep templates in git, create copies with actual paths
4. **Validation**: Tool validates all fields before running
5. **Multiple Configs**: Create different configs for different students

## 📚 Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Documentation](COLLOQUIUM.md)
- [Project Documentation](PROJECT.md)
- [Review Documentation](REVIEW.md)
