from unittest.mock import patch

import pytest

from src.change_logger_agent.main import (
    enrich_commit,
    generate_changelog,
    generate_changelog_from_commits,
)
from src.change_logger_agent.models import (
    Changelog,
    Commit,
    CommitCategory,
    EnrichedCommit,
    EnrichedCommitResponse,
)


class TestEnrichCommit:
    """Test the enrich_commit function."""

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_enrich_commit_success(self, mock_load_prompt, mock_generate_llm_response):
        """Test successful commit enrichment."""
        # Arrange
        commit = Commit(
            hash="abc123",
            message="Add user authentication",
            diff="+class AuthService:\n+    pass",
        )

        mock_load_prompt.return_value = {
            "system": "Analyze commits",
            "user": "Commit: {commit_message}\nDiff: {diff}",
        }

        mock_response = EnrichedCommitResponse(
            category=CommitCategory.FEATURE,
            description="Added user authentication system",
        )
        mock_generate_llm_response.return_value = mock_response

        # Act
        result = enrich_commit(commit)

        # Assert
        assert isinstance(result, EnrichedCommit)
        assert result.hash == "abc123"
        assert result.message == "Add user authentication"
        assert result.category == CommitCategory.FEATURE
        assert result.description == "Added user authentication system"

        mock_load_prompt.assert_called_once_with(
            "enrich_commit",
            commit_message="Add user authentication",
            diff="+class AuthService:\n+    pass",
        )
        mock_generate_llm_response.assert_called_once()

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_enrich_commit_with_complex_diff(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test commit enrichment with complex diff."""
        # Arrange
        commit = Commit(
            hash="def456",
            message="Refactor database connection",
            diff="-    conn = sqlite3.connect('db.sqlite')\n+    conn = get_db_connection()",
        )

        mock_load_prompt.return_value = {
            "system": "Analyze commits",
            "user": "Commit: {commit_message}\nDiff: {diff}",
        }

        mock_response = EnrichedCommitResponse(
            category=CommitCategory.REFACTOR,
            description="Refactored database connection to use centralized connection management",
        )
        mock_generate_llm_response.return_value = mock_response

        # Act
        result = enrich_commit(commit)

        # Assert
        assert result.category == CommitCategory.REFACTOR
        assert "centralized connection management" in result.description

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_enrich_commit_prompt_error(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test commit enrichment when prompt loading fails."""
        # Arrange
        commit = Commit(hash="error123", message="Test commit", diff="+test")

        mock_load_prompt.side_effect = KeyError("enrich_commit")

        # Act & Assert
        with pytest.raises(KeyError):
            enrich_commit(commit)


class TestGenerateChangelog:
    """Test the generate_changelog function."""

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_generate_changelog_success(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test successful changelog generation."""
        # Arrange
        enriched_commits = [
            EnrichedCommit(
                hash="feat001",
                message="Add notifications",
                diff="+NotificationService",
                category=CommitCategory.FEATURE,
                description="Added notification system",
            ),
            EnrichedCommit(
                hash="fix001",
                message="Fix memory leak",
                diff="-cache = {}\n+cache = WeakKeyDictionary()",
                category=CommitCategory.BUG_FIX,
                description="Fixed memory leak in cache",
            ),
        ]

        mock_load_prompt.return_value = {
            "system": "Generate changelog",
            "user": "Commits: {commits}\nTemplate: {template}",
        }

        expected_changelog = Changelog(
            title="Release v1.1.0",
            description="This release adds notifications and fixes memory issues.",
            summary="New features and bug fixes",
        )
        mock_generate_llm_response.return_value = expected_changelog

        # Act
        result = generate_changelog(enriched_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert result.title == "Release v1.1.0"
        assert "notifications" in result.description
        assert "memory issues" in result.description

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_generate_changelog_with_template(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test changelog generation with custom template."""
        # Arrange
        enriched_commits = [
            EnrichedCommit(
                hash="feat001",
                message="Add feature",
                diff="+feature",
                category=CommitCategory.FEATURE,
                description="Added new feature",
            )
        ]

        custom_template = "# Custom Changelog\n## Features\n{features}"

        mock_load_prompt.return_value = {
            "system": "Generate changelog",
            "user": "Commits: {commits}\nTemplate: {template}",
        }

        expected_changelog = Changelog(
            title="Custom Release",
            description="Custom formatted changelog",
            summary="Custom summary",
        )
        mock_generate_llm_response.return_value = expected_changelog

        # Act
        result = generate_changelog(enriched_commits, custom_template)

        # Assert
        assert result.title == "Custom Release"

        # Verify template was passed to prompt
        call_args = mock_load_prompt.call_args
        assert call_args.kwargs['template'] == custom_template

    def test_generate_changelog_empty_commits(self):
        """Test changelog generation with empty commit list."""
        # Arrange
        enriched_commits = []

        # Act
        with patch("src.change_logger_agent.main.load_prompt") as mock_load_prompt:
            with patch(
                "src.change_logger_agent.main.generate_llm_response"
            ) as mock_generate_llm_response:
                mock_load_prompt.return_value = {"system": "test", "user": "test"}
                mock_generate_llm_response.return_value = Changelog(
                    title="Empty Release",
                    description="No changes",
                    summary="No changes",
                )

                result = generate_changelog(enriched_commits)

        # Assert
        assert isinstance(result, Changelog)


class TestGenerateChangelogFromCommits:
    """Test the generate_changelog_from_commits function."""

    @patch("src.change_logger_agent.main.enrich_commit")
    @patch("src.change_logger_agent.main.generate_changelog")
    def test_generate_changelog_from_commits_success(
        self, mock_generate_changelog, mock_enrich_commit
    ):
        """Test successful changelog generation from raw commits."""
        # Arrange
        raw_commits = [
            Commit(
                hash="feat001", message="Add notifications", diff="+NotificationService"
            ),
            Commit(hash="fix001", message="Fix memory leak", diff="-cache = {}"),
        ]

        enriched_commits = [
            EnrichedCommit(
                hash="feat001",
                message="Add notifications",
                diff="+NotificationService",
                category=CommitCategory.FEATURE,
                description="Added notification system",
            ),
            EnrichedCommit(
                hash="fix001",
                message="Fix memory leak",
                diff="-cache = {}",
                category=CommitCategory.BUG_FIX,
                description="Fixed memory leak",
            ),
        ]

        mock_enrich_commit.side_effect = enriched_commits

        expected_changelog = Changelog(
            title="Release v1.1.0",
            description="Release with new features and fixes",
            summary="Features and bug fixes",
        )
        mock_generate_changelog.return_value = expected_changelog

        # Act
        result = generate_changelog_from_commits(raw_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert result.title == "Release v1.1.0"

        # Verify all commits were enriched
        assert mock_enrich_commit.call_count == 2
        # Verify generate_changelog was called with the enriched commits
        mock_generate_changelog.assert_called_once()
        call_args = mock_generate_changelog.call_args
        assert call_args[0][0] == enriched_commits  # First argument should be enriched_commits
        assert "### Added" in call_args[0][1]  # Second argument should contain the default template

    @patch("src.change_logger_agent.main.enrich_commit")
    @patch("src.change_logger_agent.main.generate_changelog")
    def test_generate_changelog_from_commits_with_template(
        self, mock_generate_changelog, mock_enrich_commit
    ):
        """Test changelog generation from commits with custom template."""
        # Arrange
        raw_commits = [Commit(hash="feat001", message="Add feature", diff="+feature")]

        enriched_commit = EnrichedCommit(
            hash="feat001",
            message="Add feature",
            diff="+feature",
            category=CommitCategory.FEATURE,
            description="Added new feature",
        )

        mock_enrich_commit.return_value = enriched_commit

        custom_template = "# Custom Template"
        expected_changelog = Changelog(
            title="Custom Release",
            description="Custom description",
            summary="Custom summary",
        )
        mock_generate_changelog.return_value = expected_changelog

        # Act
        result = generate_changelog_from_commits(raw_commits, custom_template)

        # Assert
        assert result.title == "Custom Release"
        mock_generate_changelog.assert_called_once_with(
            [enriched_commit], custom_template
        )

    @patch("src.change_logger_agent.main.enrich_commit")
    def test_generate_changelog_from_commits_enrichment_error(self, mock_enrich_commit):
        """Test error handling when commit enrichment fails."""
        # Arrange
        raw_commits = [Commit(hash="error001", message="Error commit", diff="+error")]

        mock_enrich_commit.side_effect = Exception("Enrichment failed")

        # Act & Assert
        with pytest.raises(Exception, match="Enrichment failed"):
            generate_changelog_from_commits(raw_commits)

    def test_generate_changelog_from_commits_empty_list(self):
        """Test changelog generation with empty commit list."""
        # Arrange
        raw_commits = []

        # Act
        with patch(
            "src.change_logger_agent.main.generate_changelog"
        ) as mock_generate_changelog:
            mock_generate_changelog.return_value = Changelog(
                title="Empty Release", description="No changes", summary="No changes"
            )

            result = generate_changelog_from_commits(raw_commits)

        # Assert
        assert isinstance(result, Changelog)
        # Verify generate_changelog was called with empty list and default template
        mock_generate_changelog.assert_called_once()
        call_args = mock_generate_changelog.call_args
        assert call_args[0][0] == []  # First argument should be empty list
        assert "### Added" in call_args[0][1]  # Second argument should contain the default template


class TestIntegration:
    """Integration tests for the main module."""

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_full_workflow_integration(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test the complete workflow from raw commits to changelog."""
        # Arrange
        raw_commits = [
            Commit(
                hash="feat001",
                message="Add user registration",
                diff="+class UserRegistration:\n+    def register(self):\n+        pass",
            ),
            Commit(
                hash="fix001",
                message="Fix login validation",
                diff="-if username:\n+if username and len(username) > 0:",
            ),
            Commit(
                hash="docs001",
                message="Update API documentation",
                diff="+## Authentication\n+Users can register and login",
            ),
        ]

        # Mock responses for enrichment
        enrichment_responses = [
            EnrichedCommitResponse(
                category=CommitCategory.FEATURE,
                description="Implemented user registration functionality",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.BUG_FIX,
                description="Fixed validation logic in login process",
            ),
            EnrichedCommitResponse(
                category=CommitCategory.DOCUMENTATION,
                description="Updated API documentation with authentication details",
            ),
        ]

        # Mock changelog response
        changelog_response = Changelog(
            title="Release v1.0.0 - Authentication System",
            description="This release introduces user authentication with registration and improved login validation.",
            summary="Added user registration, fixed login validation, and updated documentation.",
        )

        # Setup mocks
        mock_load_prompt.side_effect = [
            {"system": "enrich", "user": "commit: {commit_message}\ndiff: {diff}"},
            {"system": "enrich", "user": "commit: {commit_message}\ndiff: {diff}"},
            {"system": "enrich", "user": "commit: {commit_message}\ndiff: {diff}"},
            {"system": "changelog", "user": "commits: {commits}\ntemplate: {template}"},
        ]

        mock_generate_llm_response.side_effect = enrichment_responses + [
            changelog_response
        ]

        # Act
        result = generate_changelog_from_commits(raw_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert "Authentication System" in result.title
        assert "registration" in result.description
        assert "login validation" in result.description
        # Note: "documentation" is in the summary, not description for this mock response
        assert "documentation" in result.summary

        # Verify all commits were processed
        assert mock_generate_llm_response.call_count == 4  # 3 enrichments + 1 changelog

    @patch("src.change_logger_agent.main.generate_llm_response")
    @patch("src.change_logger_agent.main.load_prompt")
    def test_workflow_with_different_commit_types(
        self, mock_load_prompt, mock_generate_llm_response
    ):
        """Test workflow with various types of commits."""
        # Arrange
        raw_commits = [
            Commit(hash="perf001", message="Optimize database queries", diff="+index"),
            Commit(hash="sec001", message="Add input validation", diff="+sanitize"),
            Commit(
                hash="style001", message="Format code with prettier", diff="+prettier"
            ),
            Commit(hash="test001", message="Add unit tests", diff="+test_"),
            Commit(
                hash="chore001", message="Update dependencies", diff="+package.json"
            ),
        ]

        # Mock enrichment responses for different categories
        enrichment_responses = [
            EnrichedCommitResponse(
                category=CommitCategory.PERFORMANCE, description="Optimized queries"
            ),
            EnrichedCommitResponse(
                category=CommitCategory.SECURITY, description="Added validation"
            ),
            EnrichedCommitResponse(
                category=CommitCategory.STYLE, description="Formatted code"
            ),
            EnrichedCommitResponse(
                category=CommitCategory.TEST, description="Added tests"
            ),
            EnrichedCommitResponse(
                category=CommitCategory.CHORE, description="Updated deps"
            ),
        ]

        changelog_response = Changelog(
            title="Release v1.1.0 - Improvements & Maintenance",
            description="This release includes performance optimizations, security improvements, code formatting, new tests, and dependency updates.",
            summary="Performance, security, and maintenance improvements.",
        )

        # Setup mocks
        mock_load_prompt.return_value = {"system": "test", "user": "test"}
        mock_generate_llm_response.side_effect = enrichment_responses + [
            changelog_response
        ]

        # Act
        result = generate_changelog_from_commits(raw_commits)

        # Assert
        assert isinstance(result, Changelog)
        assert "Improvements & Maintenance" in result.title
        assert mock_generate_llm_response.call_count == 6  # 5 enrichments + 1 changelog
