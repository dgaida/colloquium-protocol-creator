# Configuration Loader API

API reference for the `ConfigLoader` class and related functions.

## Overview

The configuration loader provides a type-safe way to load and validate JSON configuration files for all three use cases (colloquium, project, review).

## Classes

### `ConfigLoader`

Main class for loading and validating configuration files.

#### Constructor

```python
ConfigLoader(folder_path: str)
```

**Parameters:**

- `folder_path` (str): Path to folder containing `config*.json` file

**Raises:**

- `FileNotFoundError`: If no config file found
- `json.JSONDecodeError`: If config file contains invalid JSON
- `ValueError`: If config validation fails

**Example:**

```python
from academic_doc_generator.config_loader import ConfigLoader

config = ConfigLoader("/path/to/thesis/folder")
```

#### Methods

##### `get_task()`

```python
def get_task(self) -> str
```

Returns the task type.

**Returns:** `str` - One of `"colloquium"`, `"project"`, `"review"`

**Example:**

```python
task = config.get_task()
print(task)  # "colloquium"
```

##### `get_pdf_path()`

```python
def get_pdf_path(self) -> str
```

Returns the full path to the PDF file.

**Returns:** `str` - Absolute path to PDF

**Example:**

```python
pdf_path = config.get_pdf_path()
# "/path/to/thesis/Bachelorarbeit_Mustermann.pdf"
```

##### `get_llm_config()`

```python
def get_llm_config(self) -> Dict[str, Any]
```

Returns LLM configuration.

**Returns:** `dict` with keys:

- `api_choice` (str | None): LLM provider
- `model` (str | None): Model name
- `groq_free` (bool): Rate limiting flag

**Example:**

```python
llm_config = config.get_llm_config()
# {
#     "api_choice": "openai",
#     "model": "gpt-4o-mini",
#     "groq_free": False
# }
```

##### `get_output_config()`

```python
def get_output_config(self) -> Dict[str, Any]
```

Returns output configuration.

**Returns:** `dict` with keys:

- `folder` (str | None): Output directory
- `compile_pdf` (bool): PDF compilation flag
- `fill_form_only` (bool): Form-only mode flag

**Example:**

```python
output_config = config.get_output_config()
# {
#     "folder": None,
#     "compile_pdf": True,
#     "fill_form_only": False
# }
```

##### `get_colloquium_config()`

```python
def get_colloquium_config(self) -> Optional[Dict[str, Any]]
```

Returns colloquium-specific configuration.

**Returns:** `dict | None` with keys:

- `date` (str): Colloquium date (DD.MM.YYYY)
- `time` (str): Colloquium time (HH:MM)
- `location_type` (str): One of "campus", "company", "online"
- `room` (str | None): Room number (campus only)
- `company_name` (str | None): Company name
- `company_address` (str | None): Company address
- `zoom_link` (str | None): Zoom URL
- `zoom_meeting_access` (str | None): Zoom access code

**Example:**

```python
coll_config = config.get_colloquium_config()
if coll_config:
    print(coll_config["date"])  # "20.01.2026"
    print(coll_config["location_type"])  # "campus"
```

##### `get_project_config()`

```python
def get_project_config(self) -> Optional[Dict[str, Any]]
```

Returns project-specific configuration.

**Returns:** `dict | None` with keys:

- `grade` (str | None): Project grade

**Example:**

```python
proj_config = config.get_project_config()
if proj_config:
    grade = proj_config.get("grade")
```

##### `get_gemini_evaluation_config()`

```python
def get_gemini_evaluation_config(self) -> Dict[str, Any]
```

Returns Gemini evaluation configuration.

**Returns:** `dict` with keys:

- `enabled` (bool): Whether evaluation is enabled
- `model` (str): Gemini model name

**Example:**

```python
gemini_config = config.get_gemini_evaluation_config()
# {
#     "enabled": False,
#     "model": "gemini-2.0-flash-exp"
# }
```

## Functions

### `load_config()`

```python
def load_config(folder_path: str) -> ConfigLoader
```

Factory function to load a configuration.

**Parameters:**

- `folder_path` (str): Path to folder containing config file

**Returns:** `ConfigLoader` instance

**Example:**

```python
from academic_doc_generator.config_loader import load_config

config = load_config("/path/to/thesis")
print(config.get_task())
```

## Constants

### `VALID_TASKS`

```python
VALID_TASKS = ["colloquium", "project", "review"]
```

List of valid task types.

### `VALID_LOCATION_TYPES`

```python
VALID_LOCATION_TYPES = ["campus", "company", "online"]
```

List of valid location types for colloquium.

## Type Definitions

### `LLMConfig`

```python
class LLMConfig(TypedDict, total=False):
    api_choice: Optional[str]
    model: Optional[str]
    groq_free: bool
```

### `OutputConfig`

```python
class OutputConfig(TypedDict, total=False):
    folder: Optional[str]
    compile_pdf: bool
    fill_form_only: bool
    signature_file: Optional[str]
    create_feedback_mail: bool
```

### `ColloquiumConfig`

```python
class ColloquiumConfig(TypedDict, total=False):
    date: str
    time: str
    location_type: LocationType
    room: Optional[str]
    company_name: Optional[str]
    company_address: Optional[str]
    zoom_link: Optional[str]
    zoom_meeting_access: Optional[str]
```

## Examples

### Complete Workflow

```python
from academic_doc_generator.config_loader import load_config
from llm_client import LLMClient
from academic_doc_generator.colloquium.orchestrator import run_pipeline

# Load configuration
config = load_config("/path/to/thesis")

# Create LLM client
llm_config = config.get_llm_config()
client = LLMClient(
    api_choice=llm_config.get("api_choice"),
    llm=llm_config.get("model")
)

# Execute task
if config.get_task() == "colloquium":
    coll_config = config.get_colloquium_config()
    output_config = config.get_output_config()
    
    tex, pdf, email = run_pipeline(
        pdf_path=config.get_pdf_path(),
        date_colloquium=coll_config["date"],
        uhrzeit_colloquium=coll_config["time"],
        llm_client=client,
        location_type=coll_config["location_type"],
        room=coll_config.get("room"),
        compile_pdf=output_config.get("compile_pdf", True)
    )
```

### Error Handling

```python
from academic_doc_generator.config_loader import load_config

try:
    config = load_config("/path/to/thesis")
    print(f"Loaded config for task: {config.get_task()}")
    
except FileNotFoundError:
    print("No config*.json file found in folder")
    
except ValueError as e:
    print(f"Config validation error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Validation Example

```python
config = load_config("/path/to/thesis")

# Get colloquium config
coll_config = config.get_colloquium_config()

# Validation is already done by ConfigLoader
# These checks will not raise errors:
assert coll_config["location_type"] in ["campus", "company", "online"]

if coll_config["location_type"] == "campus":
    assert "room" in coll_config
    print(f"Colloquium in room: {coll_config['room']}")
```

## See Also

- [Configuration Guide](../configuration.md)
- [CLI Reference](../cli.md)
- [Core Modules](core.md)
