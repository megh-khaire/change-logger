import os
from unittest.mock import patch

import pytest

from src.change_logger_agent.models import (
    Changelog,
    Commit,
    CommitCategory,
    EnrichedCommit,
)


@pytest.fixture
def sample_commit():
    """Fixture providing a sample commit for testing."""
    return Commit(
        hash="abc123def456",
        message="Add user authentication system",
        diff="+class AuthService:\n+    def authenticate(self, username, password):\n+        # Authentication logic here\n+        return True",
    )


@pytest.fixture
def sample_commits():
    """Fixture providing multiple sample commits for testing."""
    return [
        Commit(
            hash="feat001",
            message="Add real-time notifications",
            diff="+class NotificationService:\n+    def send_notification(self, user, message):\n+        pass",
        ),
        Commit(
            hash="fix001",
            message="Fix memory leak in data processing",
            diff="-    data = load_all_data()\n+    data = load_data_efficiently()",
        ),
        Commit(
            hash="refact001",
            message="Refactor authentication module",
            diff="class AuthService:\n-    def old_authenticate(self):\n+    def authenticate(self):",
        ),
    ]


@pytest.fixture
def sample_enriched_commits():
    """Fixture providing multiple sample enriched commits for testing."""
    return [
        EnrichedCommit(
            hash="feat001",
            message="Add real-time notifications",
            diff="+class NotificationService:\n+    def send_notification(self, user, message):\n+        pass",
            category=CommitCategory.FEATURE,
            description="Implemented a comprehensive real-time notification system that allows users to receive instant updates about important events.",
        ),
        EnrichedCommit(
            hash="fix001",
            message="Fix memory leak in data processing",
            diff="-    data = load_all_data()\n+    data = load_data_efficiently()",
            category=CommitCategory.BUG_FIX,
            description="Resolved a critical memory leak in the data processing pipeline by implementing more efficient data loading mechanisms.",
        ),
        EnrichedCommit(
            hash="refact001",
            message="Refactor authentication module",
            diff="class AuthService:\n-    def old_authenticate(self):\n+    def authenticate(self):",
            category=CommitCategory.REFACTOR,
            description="Restructured the authentication module to improve code maintainability and remove deprecated methods.",
        ),
    ]


@pytest.fixture
def sample_changelog():
    """Fixture providing a sample changelog for testing."""
    return Changelog(
        title="Release v1.2.0",
        description="This release introduces real-time notifications, fixes critical memory issues, and improves code structure.",
        summary="Major improvements to notification system and performance optimizations.",
    )


@pytest.fixture
def mock_openai_key():
    """Fixture to mock the OpenAI API key environment variable."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        yield


@pytest.fixture
def mock_prompts_file(tmp_path):
    """Fixture to create a temporary prompts file for testing."""
    prompts_content = """
enrich_commit:
  system: "You are an AI assistant that analyzes git commits."
  user: "Analyze this commit: {commit_message}\\n\\nDiff: {diff}"

generate_changelog:
  system: "You are an AI assistant that generates changelogs."
  user: "Generate a changelog from these commits: {commits}\\n\\nTemplate: {template}"
"""
    prompts_file = tmp_path / "prompts.yml"
    prompts_file.write_text(prompts_content)
    return prompts_file


@pytest.fixture
def mock_llm_response():
    """Fixture providing a mock LLM response for testing."""
    return {
        "category": "feature",
        "description": "Added a new feature that improves user experience significantly.",
    }


@pytest.fixture(autouse=True)
def setup_environment():
    """Fixture to set up the test environment."""
    # Set required environment variables
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        yield


# Mock responses for different test scenarios
@pytest.fixture
def mock_enriched_commit_response():
    """Mock response for commit enrichment."""
    return {
        "category": "feature",
        "description": "Implemented a comprehensive authentication system with OAuth support.",
    }


@pytest.fixture
def mock_changelog_response():
    """Mock response for changelog generation."""
    return {
        "title": "Release v1.2.0",
        "description": "This release introduces new features and important bug fixes.",
        "summary": "Enhanced user authentication and improved system reliability.",
    }


# Path fixtures for testing file operations
@pytest.fixture
def temp_prompts_dir(tmp_path):
    """Create a temporary directory with prompts file."""
    prompts_dir = tmp_path / "resources"
    prompts_dir.mkdir()

    prompts_file = prompts_dir / "prompts.yml"
    prompts_content = """
enrich_commit:
  system: "You are an AI assistant that analyzes git commits and categorizes them."
  user: "Analyze this commit message: {commit_message}\\n\\nDiff:\\n{diff}\\n\\nProvide a category and detailed description."

generate_changelog:
  system: "You are an AI assistant that generates comprehensive changelogs."
  user: "Create a changelog from these commits:\\n{commits}\\n\\nUse this template: {template}"
"""
    prompts_file.write_text(prompts_content)
    return prompts_dir


@pytest.fixture
def sample_template():
    """Fixture providing a sample template for testing."""
    return """
# Changelog

## Version {version}

### Features
{features}

### Bug Fixes
{bug_fixes}

### Other Changes
{other_changes}
"""
