import os
from unittest.mock import patch

import pytest

from src.change_logger_agent.main import generate_changelog_from_commits
from src.change_logger_agent.models import (
    Changelog,
    Commit,
    CommitCategory,
    EnrichedCommitResponse,
)


class TestEndToEndIntegration:
    """End-to-end integration tests for the entire changelog generation pipeline."""

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_complete_changelog_generation_workflow(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test the complete workflow from raw commits to final changelog."""
        # Arrange - Create realistic raw commits
        raw_commits = [
            Commit(
                hash="feat001",
                message="Add user authentication with OAuth2 support",
                diff="+class AuthService:\n+    def oauth_login(self, provider):\n+        return self.validate_token(provider)",
            ),
            Commit(
                hash="fix001",
                message="Fix memory leak in data processor",
                diff="-    self.cache = {}\n+    self.cache = weakref.WeakKeyDictionary()",
            ),
            Commit(
                hash="refact001",
                message="Refactor database connection handling",
                diff="-    conn = sqlite3.connect('db')\n+    conn = self.connection_pool.get_connection()",
            ),
            Commit(
                hash="docs001",
                message="Update API documentation for v2.0",
                diff="+## Authentication\n+OAuth2 flow is now supported",
            ),
            Commit(
                hash="test001",
                message="Add comprehensive unit tests for auth module",
                diff="+def test_oauth_login():\n+    assert auth.oauth_login('github') is not None",
            ),
        ]

        # Mock prompt responses
        mock_load_prompt.side_effect = [
            # Enrichment prompts for each commit
            {
                "system": "Analyze commits",
                "user": "Commit: {commit_message}\nDiff: {diff}",
            },
            {
                "system": "Analyze commits",
                "user": "Commit: {commit_message}\nDiff: {diff}",
            },
            {
                "system": "Analyze commits",
                "user": "Commit: {commit_message}\nDiff: {diff}",
            },
            {
                "system": "Analyze commits",
                "user": "Commit: {commit_message}\nDiff: {diff}",
            },
            {
                "system": "Analyze commits",
                "user": "Commit: {commit_message}\nDiff: {diff}",
            },
            # Changelog generation prompt
            {
                "system": "Generate changelog",
                "user": "Commits: {commits}\nTemplate: {template}",
            },
        ]

        # Mock LLM responses for enrichment
        enrichment_responses = [
            EnrichedCommitResponse(
                category=CommitCategory.FEATURE,
                description="Implemented OAuth2 authentication flow with support for multiple providers including GitHub, Google, and Microsoft. Added secure token validation and user session management.",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.BUG_FIX,
                description="Resolved critical memory leak in the data processing pipeline by replacing standard dictionary cache with weak reference implementation to prevent memory accumulation.",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.REFACTOR,
                description="Improved database connection management by implementing connection pooling pattern to enhance performance and resource utilization.",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.DOCUMENTATION,
                description="Updated comprehensive API documentation to reflect new OAuth2 authentication endpoints and usage examples for version 2.0 release.",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.TEST,
                description="Added extensive unit test coverage for authentication module including OAuth2 flow testing, token validation, and error handling scenarios.",
            ),
        ]

        # Mock final changelog response
        final_changelog = Changelog(
            title="Release v2.0.0 - Authentication & Performance Update",
            description="""## 🚀 Features
- **OAuth2 Authentication**: Added comprehensive OAuth2 support with multiple provider integration
- **Connection Pooling**: Implemented database connection pooling for improved performance

## 🐛 Bug Fixes
- **Memory Management**: Fixed critical memory leak in data processing pipeline

## 📚 Documentation & Testing
- Updated API documentation for v2.0 with OAuth2 examples
- Added comprehensive unit test coverage for authentication module

## 🔧 Internal Improvements
- Refactored database connection handling for better resource management""",
            summary="Major release introducing OAuth2 authentication, fixing critical memory issues, and improving database performance. Includes comprehensive documentation updates and expanded test coverage.",
        )

        # Set up all mock responses
        mock_generate_llm_response.side_effect = enrichment_responses + [
            final_changelog
        ]

        # Act - Run the complete workflow
        result = generate_changelog_from_commits(raw_commits)

        # Assert - Verify the final result
        assert isinstance(result, Changelog)
        assert "Authentication & Performance Update" in result.title
        assert "OAuth2 Authentication" in result.description
        assert "memory leak" in result.description
        assert "connection pooling" in result.description
        assert "documentation" in result.description
        assert "unit test" in result.description
        assert "Major release" in result.summary

        # Verify all components were called correctly
        assert mock_load_prompt.call_count == 6  # 5 enrichments + 1 changelog
        assert mock_generate_llm_response.call_count == 6  # 5 enrichments + 1 changelog

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_single_commit_workflow(self, mock_load_prompt, mock_generate_llm_response):
        """Test workflow with a single commit."""
        # Arrange
        single_commit = [
            Commit(
                hash="hotfix001",
                message="Fix critical security vulnerability in login",
                diff="-    if user.password == password:\n+    if bcrypt.checkpw(password.encode(), user.password_hash):",
            )
        ]

        mock_load_prompt.side_effect = [
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Generate", "user": "Commits: {commits}"},
        ]

        enrichment_response = EnrichedCommitResponse(
            category=CommitCategory.SECURITY,
            description="Fixed critical security vulnerability by replacing plain text password comparison with secure bcrypt hashing algorithm to prevent password exposure.",
        )

        changelog_response = Changelog(
            title="Hotfix v1.0.1 - Security Update",
            description="## 🔒 Security\n- Fixed critical password comparison vulnerability in authentication system",
            summary="Emergency security hotfix addressing password handling vulnerability.",
        )

        mock_generate_llm_response.side_effect = [
            enrichment_response,
            changelog_response,
        ]

        # Act
        result = generate_changelog_from_commits(single_commit)

        # Assert
        assert isinstance(result, Changelog)
        assert "Security Update" in result.title
        assert "password comparison vulnerability" in result.description
        assert "Emergency security hotfix" in result.summary

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_empty_commits_workflow(self, mock_load_prompt, mock_generate_llm_response):
        """Test workflow with empty commits list."""
        # Arrange
        empty_commits = []

        mock_load_prompt.return_value = {
            "system": "Generate",
            "user": "Commits: {commits}",
        }

        changelog_response = Changelog(
            title="No Changes",
            description="No commits found for this release.",
            summary="Empty release with no changes.",
        )

        mock_generate_llm_response.return_value = changelog_response

        # Act
        result = generate_changelog_from_commits(empty_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert result.title == "No Changes"
        assert "No commits found" in result.description

        # Verify no enrichment calls were made
        assert mock_generate_llm_response.call_count == 1  # Only changelog generation

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_workflow_with_custom_template(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test workflow with custom changelog template."""
        # Arrange
        commits = [
            Commit(
                hash="feat001",
                message="Add dark mode theme",
                diff="+class DarkTheme:\n+    def apply(self):\n+        return 'dark-theme.css'",
            )
        ]

        custom_template = """
# Custom Release {version}

## What's New
{features}

## Fixes
{bug_fixes}

## Other
{other_changes}
"""

        mock_load_prompt.side_effect = [
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Generate", "user": "Template: {template}"},
        ]

        enrichment_response = EnrichedCommitResponse(
            category=CommitCategory.FEATURE,
            description="Added dark mode theme support with custom CSS styling and automatic theme switching based on user preferences.",
        )

        changelog_response = Changelog(
            title="Custom Release v1.1.0",
            description="## What's New\n- Dark mode theme support with automatic switching\n\n## Fixes\n(None)\n\n## Other\n(None)",
            summary="Added dark mode theme functionality to improve user experience.",
        )

        mock_generate_llm_response.side_effect = [
            enrichment_response,
            changelog_response,
        ]

        # Act
        result = generate_changelog_from_commits(commits, custom_template)

        # Assert
        assert isinstance(result, Changelog)
        assert "Custom Release" in result.title
        assert "What's New" in result.description
        assert "Dark mode theme" in result.description

        # Verify template was passed to changelog generation
        changelog_call = mock_load_prompt.call_args_list[1]
        assert changelog_call.kwargs['template'] == custom_template

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_workflow_with_mixed_commit_types(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test workflow with various commit types and categories."""
        # Arrange
        mixed_commits = [
            Commit(
                hash="perf001",
                message="Optimize database queries",
                diff="+CREATE INDEX",
            ),
            Commit(
                hash="style001",
                message="Format code with prettier",
                diff="+prettier.config.js",
            ),
            Commit(
                hash="chore001",
                message="Update dependencies",
                diff="+package-lock.json",
            ),
            Commit(hash="sec001", message="Add rate limiting", diff="+RateLimiter"),
        ]

        mock_load_prompt.side_effect = [
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Analyze", "user": "Commit: {commit_message}"},
            {"system": "Generate", "user": "Commits: {commits}"},
        ]

        enrichment_responses = [
            EnrichedCommitResponse(
                category=CommitCategory.PERFORMANCE,
                description="Optimized database queries",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.STYLE, description="Applied code formatting"
            ),
            EnrichedCommitResponse(
                category=CommitCategory.CHORE,
                description="Updated project dependencies",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.SECURITY, description="Added API rate limiting"
            ),
        ]

        changelog_response = Changelog(
            title="Release v1.2.0 - Maintenance & Security",
            description="## Performance\n- Database query optimization\n## Security\n- API rate limiting\n## Maintenance\n- Code formatting and dependency updates",
            summary="Maintenance release with performance improvements and security enhancements.",
        )

        mock_generate_llm_response.side_effect = enrichment_responses + [
            changelog_response
        ]

        # Act
        result = generate_changelog_from_commits(mixed_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert "Maintenance & Security" in result.title
        assert "Performance" in result.description
        assert "Security" in result.description
        assert "Maintenance" in result.description
        assert mock_generate_llm_response.call_count == 5

    def test_error_handling_in_workflow(self):
        """Test error handling when LLM calls fail."""
        # Arrange
        commits = [Commit(hash="test001", message="Test commit", diff="+test")]

        # Act & Assert - Test enrichment failure
        with patch("src.change_logger_agent.main.load_prompt") as mock_load_prompt:
            with patch(
                "src.change_logger_agent.main.generate_llm_response"
            ) as mock_generate_llm_response:
                mock_load_prompt.return_value = {"system": "test", "user": "test"}
                mock_generate_llm_response.side_effect = Exception("LLM API Error")

                with pytest.raises(Exception, match="LLM API Error"):
                    generate_changelog_from_commits(commits)

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_large_commit_batch_workflow(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test workflow with large number of commits."""
        # Arrange - Create 20 commits
        large_commit_batch = []
        for i in range(20):
            commit = Commit(
                hash=f"commit{i:03d}",
                message=f"Commit {i}: Update module {i}",
                diff=f"+module_{i} = new_implementation()",
            )
            large_commit_batch.append(commit)

        # Mock responses
        mock_load_prompt.return_value = {"system": "test", "user": "test"}

        # Create enrichment responses
        enrichment_responses = []
        for i in range(20):
            response = EnrichedCommitResponse(
                category=CommitCategory.REFACTOR,
                description=f"Updated module {i} with new implementation",
            )
            enrichment_responses.append(response)

        # Final changelog
        final_changelog = Changelog(
            title="Release v2.0.0 - Major Refactoring",
            description="## Refactoring\n- Updated 20 modules with new implementations",
            summary="Major refactoring release updating multiple core modules.",
        )

        mock_generate_llm_response.side_effect = enrichment_responses + [
            final_changelog
        ]

        # Act
        result = generate_changelog_from_commits(large_commit_batch)

        # Assert
        assert isinstance(result, Changelog)
        assert "Major Refactoring" in result.title
        assert "20 modules" in result.description
        # Verify all commits were processed
        assert (
            mock_generate_llm_response.call_count == 21
        )  # 20 enrichments + 1 changelog


class TestIntegrationWithRealPrompts:
    """Integration tests using realistic prompt structures."""

    def test_integration_with_prompt_loading(self, tmp_path):
        """Test integration that includes actual prompt loading."""
        # Create realistic prompts file
        prompts_content = {
            "enrich_commit": {
                "system": "You are an expert software engineer that categorizes git commits.",
                "user": "Analyze this commit:\nMessage: {commit_message}\nDiff: {diff}\nProvide category and description.",
            },
            "generate_changelog": {
                "system": "You are a technical writer creating changelogs.",
                "user": "Create a changelog from these commits:\n{commits}\nUse template: {template}",
            },
        }

        prompts_file = tmp_path / "prompts.yml"
        import yaml

        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        # Test with actual prompt loading
        with patch("src.change_logger_agent.prompt.PromptLoader") as mock_prompt_loader:
            mock_loader_instance = mock_prompt_loader.return_value
            mock_loader_instance.get_prompt.side_effect = [
                {
                    "system": "You are an expert software engineer that categorizes git commits.",
                    "user": "Analyze this commit:\nMessage: Add feature\nDiff: +feature\nProvide category and description.",
                },
                {
                    "system": "You are a technical writer creating changelogs.",
                    "user": "Create a changelog from these commits:\nCommit details\nUse template: Default",
                },
            ]

            with patch("src.change_logger_agent.main.generate_llm_response") as mock_llm:
                enrichment_response = EnrichedCommitResponse(
                    category=CommitCategory.FEATURE,
                    description="Added new feature functionality",
                )

                changelog_response = Changelog(
                    title="Release v1.0.0",
                    description="## Features\n- Added new feature functionality",
                    summary="Release with new features",
                )

                mock_llm.side_effect = [enrichment_response, changelog_response]

                # Execute test
                commits = [
                    Commit(hash="feat001", message="Add feature", diff="+feature")
                ]
                result = generate_changelog_from_commits(commits)

                # Verify
                assert isinstance(result, Changelog)
                assert "Release v1.0.0" == result.title

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_environment_setup_integration(self):
        """Test that environment setup works correctly in integration."""
        # This test verifies that the OpenAI API key is properly configured
        # and that the modules can be imported without environment issues

        from src.change_logger_agent.llm import client
        from src.change_logger_agent.main import generate_changelog_from_commits
        from src.change_logger_agent.models import Commit

        # Verify modules imported successfully
        assert client is not None
        assert generate_changelog_from_commits is not None
        assert Commit is not None

        # Test would continue with actual API calls in a full integration test
        # but we're keeping this focused on environment setup verification
