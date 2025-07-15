"""Changelog Agent - AI-powered changelog generation."""

from .main import generate_changelog_from_commits, generate_changelog, enrich_commit
from .models import Changelog, Commit, EnrichedCommit, CommitCategory
from .llm import generate_llm_response
from .prompt import load_prompt, PromptLoader
from .template import DEFAULT_TEMPLATE

__version__ = "0.1.0"

__all__ = [
    "generate_changelog_from_commits",
    "generate_changelog",
    "enrich_commit",
    "Changelog",
    "Commit",
    "EnrichedCommit",
    "CommitCategory",
    "generate_llm_response",
    "load_prompt",
    "PromptLoader",
    "DEFAULT_TEMPLATE",
]
