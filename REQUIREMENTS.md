# Requirements and Guidelines

## LLM Token Limits  
- **Minimum Max Tokens Requirement**: When instantiating `LLMClient` or configuring LLM interactions across the codebase, the token limit (`max_tokens`) must be set to at least `2048` tokens (or higher where specified, e.g. `4096` for thesis evaluation).  
- **Do Not Reduce Token Limits**: Never decrease the configured `max_tokens` below `2048` unless explicitly requested by the user or required for a specific constraint. This ensures JSON metadata responses, thesis summaries, and generated feedback remain complete and are not truncated by the API.  
