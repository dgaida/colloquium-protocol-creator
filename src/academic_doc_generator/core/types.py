# src/academic_doc_generator/core/types.py
"""Common type definitions for academic-doc-generator.

This module provides TypedDicts and type aliases for complex data structures
used throughout the package, improving type safety and IDE support.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Protocol, TypedDict

# ==============================================================================
# Literals for constrained string values
# ==============================================================================

LocationType = Literal["campus", "company", "online"]
"""Type of colloquium location."""

CommentCategory = Literal["llm", "quelle", "language", "ignore"]
"""Category of PDF annotation comment."""

DegreeType = Literal["Bachelor", "Master"]
"""Type of academic degree."""

GenderType = Literal["Herr", "Frau", "Herr/Frau"]
"""Formal German address form."""

# ==============================================================================
# Bounding Box Types
# ==============================================================================

BBox = tuple[float, float, float, float]
"""Bounding box as (x0, y0, x1, y1) in PDF coordinates (bottom-left origin)."""


# ==============================================================================
# Protocols for Flexible Interfaces
# ==============================================================================


class LLMClientProtocol(Protocol):
    """Protocol defining the interface for LLM clients.

    This allows for flexible LLM implementations and easier testing with mocks.

    Attributes:
        api_choice: The API provider being used (e.g., "openai", "groq").
        llm: The specific model name being used.
    """

    api_choice: str
    llm: str

    def chat_completion(self, messages: list[dict[str, str]]) -> str:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            The LLM's response text.
        """
        ...


# ==============================================================================
# PDF Processing Types
# ==============================================================================


class WordBox(TypedDict):
    """A word extracted from a PDF with its bounding box."""

    text: str
    bbox: BBox


class AnnotationData(TypedDict):
    """Raw annotation data extracted from PDF."""

    comment: str
    subtype: str
    rect: Optional[BBox]
    quadpoints: Optional[list[float]]
    category: CommentCategory


class AnnotationContext(TypedDict):
    """Annotation with surrounding context from the document."""

    comment: str
    highlighted: str
    paragraph: str
    category: CommentCategory


class AnnotationWithLine(AnnotationContext):
    """Annotation context with line number for review generation."""

    line: int


class CommentStats(TypedDict):
    """Statistics about comment categories in a document."""

    quelle: int
    language: int
    ignore: int


# ==============================================================================
# LLM Processing Types
# ==============================================================================


class RewrittenComment(TypedDict):
    """A comment that has been rewritten by the LLM."""

    original: str
    rewritten: Optional[str]  # None if category != "llm"
    highlighted: str
    paragraph: str
    category: CommentCategory


class RewrittenReviewComment(TypedDict):
    """A review comment rewritten for peer review with line info."""

    original: str
    rewritten: str
    line: int
    page: int


# ==============================================================================
# Metadata Types
# ==============================================================================


class ThesisMetadata(TypedDict, total=False):
    """Metadata extracted from a thesis PDF.

    Note: total=False allows all fields to be optional.
    """

    author: Optional[str]
    id_number: Optional[str]
    title: Optional[str]
    first_examiner: Optional[str]
    second_examiner: Optional[str]
    first_examiner_christian: Optional[str]
    first_examiner_family: Optional[str]
    bachelor_master: Optional[DegreeType]
    course_of_study: Optional[str]


class StudentInfo(TypedDict, total=False):
    """Information about a single student/author."""

    name: str
    first_name: str
    id_number: str
    email: Optional[str]


class ProjectMetadata(TypedDict, total=False):
    """Metadata extracted from a project work PDF."""

    students: list[StudentInfo]
    student_name: Optional[str]
    student_first_name: Optional[str]
    id_number: Optional[str]
    title: Optional[str]
    first_examiner: Optional[str]
    first_examiner_christian: Optional[str]
    first_examiner_family: Optional[str]
    work_type: Optional[str]
    student_email: Optional[str]
    course_of_study: Optional[str]


# ==============================================================================
# Configuration Types
# ==============================================================================


class LLMConfig(TypedDict, total=False):
    """LLM configuration settings."""

    api_choice: Optional[str]
    model: Optional[str]
    groq_free: bool


class OutputConfig(TypedDict, total=False):
    """Output configuration settings."""

    folder: Optional[str]
    compile_pdf: bool
    fill_form_only: bool
    signature_file: Optional[str]
    create_feedback_mail: bool


class ColloquiumConfig(TypedDict, total=False):
    """Configuration for colloquium tasks."""

    date: str  # Format: DD.MM.YYYY
    time: str  # Format: HH:MM
    location_type: LocationType
    room: Optional[str]  # Required if location_type="campus"
    company_name: Optional[str]  # Required if location_type="company"
    company_address: Optional[str]  # Optional for company
    zoom_link: Optional[str]  # Required if location_type="online"
    zcode: Optional[str]  # Optional for online


class GeminiEmarkConfig(TypedDict, total=False):
    """Configuration for Gemini automatic emark."""

    enabled: bool
    model: Optional[str]
    use_text_extraction: bool


class PDFConfig(TypedDict):
    """PDF file configuration."""

    filename: str


# ==============================================================================
# Dataclass Configuration Types
# ==============================================================================


@dataclass
class ColloquiumWorkflowConfig:
    """Consolidated configuration for colloquium workflow."""

    pdf_path: Path
    date: str
    time: str
    location_type: LocationType
    llm_client: Optional[LLMClientProtocol] = None
    output_folder: Optional[Path] = None
    compile_pdf: bool = True
    fill_form_only: bool = False
    groq_free: bool = False
    room: Optional[str] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    zoom_link: Optional[str] = None
    zcode: Optional[str] = None
    gemini_emark_enabled: bool = False
    gemini_model: Optional[str] = None
    gemini_use_text_extraction: bool = True


@dataclass
class ProjectWorkflowConfig:
    """Consolidated configuration for project workflow."""

    pdf_path: Path
    llm_client: Optional[LLMClientProtocol] = None
    output_folder: Optional[Path] = None
    compile_pdf: bool = True
    signature_file: str = "signature.png"
    mark: Optional[str] = None
    create_feedback_mail: bool = True
    work_type: Optional[str] = None


# ==============================================================================
# Pipeline Result Types
# ==============================================================================


@dataclass
class ColloquiumWorkflowResult:
    """Results produced by colloquium workflow."""

    tex_path: str
    pdf_path: str
    email_path: str
    metadata_path: str


@dataclass
class ProjectWorkflowResult:
    """Results produced by project workflow."""

    tex_path: str
    pdf_path: str
    service_email_path: str
    student_email_path: str
    metadata_path: str


ColloquiumResult = tuple[str, str, str, str]
"""Legacy result type for colloquium pipeline."""

ProjectResult = tuple[str, str, str, str, str]
"""Legacy result type for project pipeline."""

ReviewResult = str
"""Result of review pipeline: markdown_path."""

# ==============================================================================
# Type Aliases for Common Patterns
# ==============================================================================

PageWords = dict[int, list[WordBox]]
"""Mapping of page indices (0-based) to lists of words."""

PageAnnotations = dict[int, list[AnnotationData]]
"""Mapping of page indices (0-based) to lists of annotations."""

PageContexts = dict[int, list[AnnotationContext]]
"""Mapping of page numbers (1-based) to annotation contexts."""

RewrittenComments = dict[int, list[RewrittenComment]]
"""Mapping of page numbers (1-based) to rewritten comments."""

PageText = dict[int, str]
"""Mapping of page indices (0-based) to full text content."""
