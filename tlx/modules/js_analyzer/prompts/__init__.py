"""Prompt management package.

- loader.py:   discover + parse + validate .md prompt files
- rag.py:      separate Chroma collection 'prompts'
- registry.py: assemble system prompts, fetch by id/kind
"""

from .loader import LoaderError, Prompt, load_prompts, parse_frontmatter
from .rag import PromptRAG
from .registry import (
    PromptRegistry,
    get_registry,
    set_registry,
)

__all__ = [
    "Prompt", "load_prompts", "parse_frontmatter", "LoaderError",
    "PromptRAG",
    "PromptRegistry", "get_registry", "set_registry",
]
