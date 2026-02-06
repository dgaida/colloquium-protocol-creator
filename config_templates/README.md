# Configuration Templates

This folder contains JSON configuration templates for different tasks supported by the colloquium-protocol-creator tool.

## Available Templates

### Colloquium Templates

#### 1. `config_colloquium_campus.json`
Configuration for a thesis colloquium taking place on campus.

**Required fields:**
- `colloquium.date`: Date of colloquium (format: `DD.MM.YYYY`)
- `colloquium.time`: Time of colloquium (format: `HH:MM`)
- `colloquium.location_type`: Must be `"campus"`
- `colloquium.room`: Room number (e.g., `"3.217"`)

#### 2. `config_colloquium_company.json`
Configuration for a thesis colloquium taking place at a company.

**Required fields:**
- `colloquium.date`: Date of colloquium
- `colloquium.time`: Time of colloquium
- `colloquium.location_type`: Must be `"company"`
- `colloquium.company_name`: Name of the company
- `colloquium.company_address`: (Optional) Full address

#### 3. `config_colloquium_online.json`
Configuration for an online thesis colloquium via Zoom.

**Required fields:**
- `colloquium.date`: Date of colloquium
- `colloquium.time`: Time of colloquium
- `colloquium.location_type`: Must be `"online"`
- `colloquium.zoom_link`: Zoom meeting URL
- `colloquium.zcode`: (Optional) Zoom access code

### Project Template

#### `config_project.json`
Configuration for generating a project work (Praxisprojekt) grading letter.

**Required fields:**
- `pdf.filename`: Name of the project PDF file

**Optional fields:**
- `output.signature_file`: Path to signature image

### Review Template

#### `config_review.json`
Configuration for generating peer review comments from an annotated paper.

**Required fields:**
- `pdf.filename`: Name of the paper PDF file

## Usage

### 1. List Available Templates

```bash
colloquium-protocol-creator --list-templates
```

### 2. Use a Template

Copy a template and customize it:

```bash
# Copy template
cp config_templates/config_colloquium_campus.json my_colloquium.json

# Edit with your values
nano my_colloquium.json

# Run the tool
colloquium-protocol-creator --config my_colloquium.json
```

### 3. Direct Execution

You can also use a template directly without copying:

```bash
colloquium-protocol-creator --config config_templates/config_colloquium_campus.json
```

## Configuration Structure

All configuration files follow this basic structure:

```json
{
  "task": "colloquium|project|review",
  "description": "Human-readable description",
  
  "pdf": {
    "filename": "name.pdf"
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
Type of task to execute. Must be one of:
- `"colloquium"`: Generate thesis colloquium protocol
- `"project"`: Generate project work grading letter
- `"review"`: Generate peer review comments

#### `pdf` (required)
- `filename`: Name of the PDF file

#### `llm` (optional)
- `api_choice`: LLM API to use (`"openai"`, `"groq"`, `"gemini"`, `"ollama"`, or `null` for auto-detection)
- `model`: Specific model name (or `null` for default)
- `groq_free`: Enable rate limiting for Groq free tier (default: `false`)

#### `output` (optional)
- `folder`: Output folder (default: same as PDF folder)
- `compile_pdf`: Whether to compile LaTeX to PDF (default: `true`)

### Task-Specific Fields

#### Colloquium Task
- `colloquium.date`: Date (format: `DD.MM.YYYY`)
- `colloquium.time`: Time (format: `HH:MM`)
- `colloquium.location_type`: `"campus"`, `"company"`, or `"online"`
- `colloquium.room`: Room number (for campus)
- `colloquium.company_name`: Company name (for company)
- `colloquium.company_address`: Company address (for company, optional)
- `colloquium.zoom_link`: Zoom URL (for online)
- `colloquium.zcode`: Zoom access code (for online, optional)

#### Project Task
- `output.signature_file`: Path to signature image (optional)

## Examples

### Example 1: Campus Colloquium

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
  }
}
```

### Example 2: Project Work with Custom LLM

```json
{
  "task": "project",
  "pdf": {
    "filename": "Praxisprojekt_Weber.pdf"
  },
  "llm": {
    "api_choice": "openai",
    "model": "gpt-4o"
  },
  "output": {
    "signature_file": "./signatures/prof_mueller.png"
  }
}
```

### Example 3: Peer Review with Rate Limiting

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

## Tips

1. **Use Relative Paths**: Use `..` for parent directories to keep configs portable
2. **Set `null` for Defaults**: Use `null` for auto-detection/default values
3. **Comments**: JSON doesn't support comments, but you can use the `"description"` field
4. **Version Control**: Keep templates in git, but create personal copies with actual paths
5. **Validation**: The tool validates all required fields before running

## Troubleshooting

### Invalid Configuration Error
```
ValueError: Ungültiger Task: xyz
```
**Solution:** Check that `task` is one of: `"colloquium"`, `"project"`, `"review"`

### Missing Required Field
```
ValueError: Pflichtfeld 'date' fehlt in 'colloquium'
```
**Solution:** Add the missing field to your configuration

### PDF Not Found
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution:** Verify that `pdf.filename` point to an existing file in the cwd

### Invalid Location Type
```
ValueError: Ungültiger location_type: office
```
**Solution:** Use one of: `"campus"`, `"company"`, `"online"`

## Related Documentation

- [Main README](../README.md)
- [Installation Guide](../docs/INSTALL.md)
- [Colloquium Documentation](../docs/COLLOQUIUM.md)
- [Project Documentation](../docs/PROJECT.md)
- [Review Documentation](../docs/REVIEW.md)
