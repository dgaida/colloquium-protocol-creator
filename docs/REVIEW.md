# Peer Review Comment Generator

## Overview

This tool generates professional peer review comments for academic papers. It extracts annotations from an annotated paper PDF, rewrites rough reviewer notes into clear, constructive feedback, and generates a Markdown review document with page and line number references.

## What It Does

1. **Extracts PDF Annotations**: Reads comments you've added to the paper PDF during review
2. **Line Number Detection**: 
   - Attempts to detect printed line numbers in the PDF margins
   - Falls back to geometric estimation if line numbers aren't printed
3. **Comment Refinement**: Rewrites informal notes (e.g., "??", "unclear", "no!") into professional, constructive reviewer feedback
4. **Markdown Output**: Generates a structured review document with page/line references
5. **Language Normalization**: Always outputs comments in English for international publications

## Requirements

- Annotated paper PDF (with comments/highlights)
- At least one LLM API configured (OpenAI, Groq, Google Gemini, or Ollama)
- Paper should ideally have line numbers (common in journal submissions)

## Usage

### Python API Only

Currently, the review tool is only available via Python API:

```python
from llm_client import LLMClient
from review_pipeline import orchestrator

# Create LLM client (auto-detects available API)
client = LLMClient()

# Run review pipeline
md_file = orchestrator.run_review_pipeline(
    pdf_path="paper_to_review.pdf",
    llm_client=client,
    groq_free=True  # Enable rate limiting if using free tier
)

print(f"Review saved to: {md_file}")
```

### Workflow Integration

```python
# Example: Review paper in a specific folder
import os
from llm_client import LLMClient
from review_pipeline import orchestrator

folder = os.path.join("..", "Paper Reviews", "Conference2025")
pdf_filename = "submission_42.pdf"
pdf_path = os.path.join(folder, pdf_filename)

llm_client = LLMClient()

# Generate review
md_path = orchestrator.run_review_pipeline(
    pdf_path=pdf_path,
    llm_client=llm_client,
    groq_free=True,
    output_folder=folder
)

print(f"Review created: {md_path}")
```

## Line Number Detection

The tool uses two methods to determine line numbers:

### Method 1: Text-Based Detection (Preferred)

For papers with printed line numbers in the margins:

1. Scans the left margin (x < 20 points) of the page
2. Looks for numeric text near the annotation
3. Matches the number that vertically overlaps with the annotation

**Best for:** Journal submissions with IEEE/ACM style line numbering

### Method 2: Geometric Estimation (Fallback)

For papers without printed line numbers:

1. Calculates distance from top of page to annotation
2. Divides by assumed line height (default: 12 points)
3. Estimates line number

**Best for:** Papers in final published format without line numbers

### Line Number Accuracy

| Paper Format | Method | Accuracy |
|--------------|--------|----------|
| With printed line numbers | Text detection | High (~95%) |
| Without line numbers | Geometric | Moderate (~80%) |
| Two-column layout | Geometric | Lower (~70%) |

**Tip:** For highest accuracy, review papers in their submission format with line numbers enabled.

## Comment Rewriting

### Input: Rough Reviewer Notes

Common informal annotations during review:
- "??"
- "unclear"
- "no!"
- "wrong"
- "what about X?"
- "reference?"

### Output: Professional Feedback

The LLM rewrites these into constructive, polite comments:

| Original Note | Rewritten Comment |
|--------------|-------------------|
| "??" | "This point requires clarification. Could the authors elaborate on..." |
| "unclear" | "The explanation in this section could be made clearer by..." |
| "no!" | "I disagree with this claim. The authors should consider..." |
| "wrong" | "This statement appears to be incorrect. Please verify..." |
| "what about X?" | "The authors should discuss how their approach relates to X..." |
| "reference?" | "This claim would benefit from a supporting reference." |

### Rewriting Guidelines

The LLM follows these principles:

1. **Professional Tone**: Academic, respectful language
2. **Constructive**: Suggests improvements, not just criticism
3. **Clear**: Specific about what needs addressing
4. **Polite**: Uses phrases like "could", "should consider", "would benefit"
5. **English**: Always outputs in English for international reviews

## Output Format

### Markdown Review Document

**Filename:** `review_comments_<pdf_name>.md`

**Structure:**
```markdown
# Peer Review

Dear authors,

here are my comments on your manuscript:

- Page 1, Line 15: This point requires clarification. Could the authors elaborate on the methodology used for data collection?
- Page 2, Line 42: The explanation in this section could be made clearer by providing a concrete example.
- Page 3, Line 78: I disagree with this claim. The authors should consider recent work by Smith et al. (2024) which contradicts this finding.
- Page 5, Line 134: This statement appears to be incorrect. Please verify the calculation in Equation 3.
- Page 7, Line 201: The authors should discuss how their approach relates to the baseline methods mentioned in Section 2.
```

### Using the Review

1. **Copy to Review Form**: Paste comments into journal/conference review system
2. **Edit if Needed**: Manually adjust any comments that need refinement
3. **Add Summary**: Add overall assessment sections (strengths, weaknesses, decision)
4. **Submit**: Use as basis for complete review

## Advanced Configuration

### Rate Limiting for Free Tiers

```python
# Enable throttling for Groq free tier
md_file = orchestrator.run_review_pipeline(
    pdf_path="paper.pdf",
    llm_client=client,
    groq_free=True  # Adds 10s delay every 5 requests
)
```

### Custom LLM Settings

```python
from llm_client import LLMClient

# Use more capable model for better rewriting
client = LLMClient(
    api_choice="openai",
    llm="gpt-4o",
    temperature=0.7  # Higher for more natural language
)
```

### Custom Line Height

For papers with unusual formatting:

```python
from review_creator.md_generator import estimate_line_number

# Adjust line height for large fonts
line_number = estimate_line_number(
    y_coord=y,
    page_height=page_h,
    line_height=14.0  # Default is 12.0
)
```

## Comment Processing Details

### What Gets Processed

Only comments categorized as "llm" are rewritten. The tool respects the same categorization as the colloquium protocol generator:

- **LLM comments**: Regular annotations → Rewritten
- **Quelle comments**: Source notes → Skipped (not typical in reviews)
- **Language comments**: Grammar notes → Skipped
- **Ignore comments**: "ab hier" markers → Excluded

### Processing Pipeline

1. **Extract**: Read annotations from PDF
2. **Detect Lines**: Find line numbers via text detection or estimation
3. **Categorize**: Classify comments (usually all "llm" for reviews)
4. **Rewrite**: Send to LLM for professional reformulation
5. **Format**: Create Markdown with page/line references
6. **Save**: Write to `review_comments_<name>.md`

## Typical Review Workflow

### 1. Annotate Paper
```
- Read paper thoroughly
- Add comments as you go
- Use highlights for specific text
- Write brief notes (will be expanded by tool)
```

### 2. Generate Professional Comments
```python
from llm_client import LLMClient
from review_pipeline import orchestrator

client = LLMClient()
md_file = orchestrator.run_review_pipeline(
    pdf_path="paper.pdf",
    llm_client=client
)
```

### 3. Review Output
```
- Open generated .md file
- Check all comments make sense
- Edit any that need adjustment
- Verify page/line numbers are correct
```

### 4. Complete Review
```
- Add overall assessment
- Add summary of strengths
- Add summary of weaknesses  
- Add recommendation (accept/revise/reject)
- Submit to journal/conference
```

## Example Transformations

### Example 1: Methodology Question
```
Original: "why this approach?"
Page 3, Line 67

Rewritten: "Could the authors provide more justification for choosing 
this particular approach over alternative methods discussed in the 
literature?"
```

### Example 2: Clarity Issue
```
Original: "confusing"
Page 5, Line 123

Rewritten: "This section is difficult to follow. The authors should 
restructure the explanation to improve clarity, perhaps by adding a 
step-by-step breakdown of the algorithm."
```

### Example 3: Missing Reference
```
Original: "cite?"
Page 7, Line 189

Rewritten: "This claim requires supporting references. The authors 
should cite relevant prior work that establishes this finding."
```

### Example 4: Technical Error
```
Original: "wrong formula"
Page 9, Line 234

Rewritten: "There appears to be an error in Equation 5. Please verify 
the derivation, as the result seems inconsistent with the standard 
formulation."
```

## Limitations

### Line Number Detection
- **Two-column papers**: Line detection may be less accurate
- **Complex layouts**: Tables/figures can interfere with line estimation
- **No line numbers**: Geometric estimation is approximate

### Comment Quality
- **Very brief notes**: "?" may be too vague for good expansion
- **Context-dependent**: Comments without highlights may lack context
- **Technical details**: Very specific technical critiques may need manual editing

### Language Support
- Currently always outputs English
- Input annotations can be in any language
- Best results with English input annotations

## Tips for Best Results

### 1. Annotation Strategy
```
Good: "Why was method X chosen over Y? Performance comparison?"
Better context → Better rewriting

Poor: "?"
Too vague → Generic rewriting
```

### 2. Use Highlights
```
Highlight specific text you're commenting on
Tool can extract highlighted text for context
Results in more specific, targeted feedback
```

### 3. Be Specific in Notes
```
Good: "Missing ablation study for component X"
Poor: "incomplete"
```

### 4. Review in Submission Format
```
Use paper version with line numbers when possible
Results in accurate line references
Easier to verify comments later
```

### 5. Check Output
```
Always review generated comments
Edit for technical accuracy
Adjust tone if needed
Verify page/line references
```

## Integration with Review Systems

### For Journals
```python
# Generate review
md_file = orchestrator.run_review_pipeline("paper.pdf", client)

# Copy to review form:
# 1. Open .md file
# 2. Copy comments section
# 3. Paste into journal review system
# 4. Add required sections (summary, decision)
```

### For Conferences
```python
# Many conferences want reviews in specific format
# Use .md output as a base, then format appropriately

# Example: Convert to conference template
with open(md_file, 'r') as f:
    comments = f.read()

# Reformat for conference (e.g., HotCRP, EasyChair)
formatted = format_for_conference(comments)
```

## Troubleshooting

### No Annotations Extracted
**Problem:** Tool reports 0 comments

**Solutions:**
1. Verify PDF has actual annotations (not just highlights without text)
2. Check annotation tool saves comments properly
3. Try different PDF viewer for annotating

### Inaccurate Line Numbers
**Problem:** Line numbers don't match actual lines

**Solutions:**
1. Use paper with printed line numbers
2. Adjust `line_height` parameter for paper's font size
3. Manually correct line numbers in output .md file

### Poor Comment Quality
**Problem:** Rewritten comments are too generic

**Solutions:**
1. Write more detailed original annotations
2. Use a more capable LLM model (e.g., GPT-4)
3. Include highlighted text for context
4. Manually edit output for technical specifics

### Rate Limiting Errors
**Problem:** "Too Many Requests" from API

**Solutions:**
1. Use `groq_free=True` parameter
2. Switch to paid API tier
3. Use local Ollama model
4. Process papers one at a time with delays

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Protocols](COLLOQUIUM.md)
- [Project Grading Letters](PROJECT.md)
