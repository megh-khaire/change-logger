import pytest
from pydantic import ValidationError

from src.change_logger_agent.models import (
    Changelog,
    Commit,
    CommitCategory,
    EnrichedCommit,
    EnrichedCommitResponse,
)


class TestCommitCategory:
    """Test the CommitCategory enum."""

    def test_commit_category_values(self):
        """Test that all expected commit categories are defined."""
        expected_categories = {
            "feature",
            "bug_fix",
            "refactor",
            "documentation",
            "test",
            "chore",
            "style",
            "security",
            "performance",
        }

        actual_categories = {category.value for category in CommitCategory}
        assert actual_categories == expected_categories

    def test_commit_category_string_representation(self):
        """Test string representation of commit categories."""
        assert str(CommitCategory.FEATURE) == "feature"
        assert str(CommitCategory.BUG_FIX) == "bug_fix"
        assert str(CommitCategory.REFACTOR) == "refactor"
        assert str(CommitCategory.DOCUMENTATION) == "documentation"
        assert str(CommitCategory.TEST) == "test"
        assert str(CommitCategory.CHORE) == "chore"
        assert str(CommitCategory.STYLE) == "style"
        assert str(CommitCategory.SECURITY) == "security"
        assert str(CommitCategory.PERFORMANCE) == "performance"

    def test_commit_category_comparison(self):
        """Test that commit categories can be compared."""
        assert CommitCategory.FEATURE == CommitCategory.FEATURE
        assert CommitCategory.FEATURE != CommitCategory.BUG_FIX
        assert CommitCategory.FEATURE == "feature"
        assert CommitCategory.BUG_FIX == "bug_fix"


class TestCommit:
    """Test the Commit model."""

    def test_commit_creation_valid(self):
        """Test creating a valid Commit instance."""
        commit = Commit(
            hash="abc123def456",
            message="Add user authentication",
            diff="+class AuthService:\n+    pass",
        )

        assert commit.hash == "abc123def456"
        assert commit.message == "Add user authentication"
        assert commit.diff == "+class AuthService:\n+    pass"

    def test_commit_creation_minimal(self):
        """Test creating a Commit with minimal valid data."""
        commit = Commit(hash="a", message="", diff="")

        assert commit.hash == "a"
        assert commit.message == ""
        assert commit.diff == ""

    def test_commit_creation_missing_fields(self):
        """Test that Commit creation fails with missing required fields."""
        with pytest.raises(ValidationError):
            Commit(hash="abc123", message="test")  # Missing diff

        with pytest.raises(ValidationError):
            Commit(hash="abc123", diff="test")  # Missing message

        with pytest.raises(ValidationError):
            Commit(message="test", diff="test")  # Missing hash

    def test_commit_hash_validation(self):
        """Test commit hash validation."""
        # Valid hashes
        valid_hashes = ["a", "abc123", "abc123def456789", "1234567890abcdef"]
        for hash_val in valid_hashes:
            commit = Commit(hash=hash_val, message="test", diff="test")
            assert commit.hash == hash_val

    def test_commit_equality(self):
        """Test Commit equality comparison."""
        commit1 = Commit(hash="abc123", message="test", diff="test")
        commit2 = Commit(hash="abc123", message="test", diff="test")
        commit3 = Commit(hash="def456", message="test", diff="test")

        assert commit1 == commit2
        assert commit1 != commit3

    def test_commit_dict_conversion(self):
        """Test converting Commit to dictionary."""
        commit = Commit(hash="abc123", message="Add feature", diff="+feature code")

        commit_dict = commit.model_dump()
        expected_dict = {
            "hash": "abc123",
            "message": "Add feature",
            "diff": "+feature code",
        }

        assert commit_dict == expected_dict

    def test_commit_json_serialization(self):
        """Test Commit JSON serialization."""
        commit = Commit(hash="abc123", message="Add feature", diff="+feature code")

        json_str = commit.model_dump_json()
        assert '"hash":"abc123"' in json_str
        assert '"message":"Add feature"' in json_str
        assert '"+feature code"' in json_str


class TestEnrichedCommitResponse:
    """Test the EnrichedCommitResponse model."""

    def test_enriched_commit_response_creation_valid(self):
        """Test creating a valid EnrichedCommitResponse."""
        response = EnrichedCommitResponse(
            category=CommitCategory.FEATURE,
            description="Added user authentication system",
        )

        assert response.category == CommitCategory.FEATURE
        assert response.description == "Added user authentication system"

    def test_enriched_commit_response_category_string(self):
        """Test creating EnrichedCommitResponse with string category."""
        response = EnrichedCommitResponse(
            category="bug_fix", description="Fixed memory leak"
        )

        assert response.category == CommitCategory.BUG_FIX
        assert response.description == "Fixed memory leak"

    def test_enriched_commit_response_invalid_category(self):
        """Test EnrichedCommitResponse creation with invalid category."""
        with pytest.raises(ValidationError):
            EnrichedCommitResponse(
                category="invalid_category", description="Test description"
            )

    def test_enriched_commit_response_missing_fields(self):
        """Test EnrichedCommitResponse creation with missing fields."""
        with pytest.raises(ValidationError):
            EnrichedCommitResponse(
                category=CommitCategory.FEATURE
            )  # Missing description

        with pytest.raises(ValidationError):
            EnrichedCommitResponse(description="Test")  # Missing category

    def test_enriched_commit_response_empty_description(self):
        """Test EnrichedCommitResponse with empty description."""
        response = EnrichedCommitResponse(category=CommitCategory.CHORE, description="")

        assert response.category == CommitCategory.CHORE
        assert response.description == ""


class TestEnrichedCommit:
    """Test the EnrichedCommit model."""

    def test_enriched_commit_creation_valid(self):
        """Test creating a valid EnrichedCommit."""
        enriched_commit = EnrichedCommit(
            hash="abc123",
            message="Add authentication",
            diff="+auth code",
            category=CommitCategory.FEATURE,
            description="Added user authentication system",
        )

        assert enriched_commit.hash == "abc123"
        assert enriched_commit.message == "Add authentication"
        assert enriched_commit.diff == "+auth code"
        assert enriched_commit.category == CommitCategory.FEATURE
        assert enriched_commit.description == "Added user authentication system"

    def test_enriched_commit_inheritance(self):
        """Test that EnrichedCommit properly inherits from both Commit and EnrichedCommitResponse."""
        enriched_commit = EnrichedCommit(
            hash="abc123",
            message="Test",
            diff="test",
            category=CommitCategory.TEST,
            description="Test commit",
        )

        # Should have all Commit fields
        assert hasattr(enriched_commit, "hash")
        assert hasattr(enriched_commit, "message")
        assert hasattr(enriched_commit, "diff")

        # Should have all EnrichedCommitResponse fields
        assert hasattr(enriched_commit, "category")
        assert hasattr(enriched_commit, "description")

    def test_enriched_commit_from_commit_and_response(self):
        """Test creating EnrichedCommit from Commit and EnrichedCommitResponse."""
        commit = Commit(hash="abc123", message="Fix bug", diff="-bug\n+fix")

        response = EnrichedCommitResponse(
            category=CommitCategory.BUG_FIX,
            description="Fixed critical bug in authentication",
        )

        # Simulate combining the two (as done in main.py)
        enriched_commit = EnrichedCommit(**commit.model_dump(), **response.model_dump())

        assert enriched_commit.hash == "abc123"
        assert enriched_commit.message == "Fix bug"
        assert enriched_commit.diff == "-bug\n+fix"
        assert enriched_commit.category == CommitCategory.BUG_FIX
        assert enriched_commit.description == "Fixed critical bug in authentication"

    def test_enriched_commit_validation_error(self):
        """Test EnrichedCommit creation with validation errors."""
        with pytest.raises(ValidationError):
            EnrichedCommit(
                hash="abc123",
                message="test",
                diff="test",
                category="invalid_category",  # Invalid category
                description="test",
            )


class TestChangelog:
    """Test the Changelog model."""

    def test_changelog_creation_valid(self):
        """Test creating a valid Changelog."""
        changelog = Changelog(
            title="Release v1.0.0",
            description="This release includes new features and bug fixes.",
            summary="Major release with authentication and performance improvements.",
        )

        assert changelog.title == "Release v1.0.0"
        assert (
            changelog.description == "This release includes new features and bug fixes."
        )
        assert (
            changelog.summary
            == "Major release with authentication and performance improvements."
        )

    def test_changelog_creation_minimal(self):
        """Test creating a Changelog with minimal data."""
        changelog = Changelog(title="", description="", summary="")

        assert changelog.title == ""
        assert changelog.description == ""
        assert changelog.summary == ""

    def test_changelog_missing_fields(self):
        """Test Changelog creation with missing required fields."""
        with pytest.raises(ValidationError):
            Changelog(title="test", description="test")  # Missing summary

        with pytest.raises(ValidationError):
            Changelog(title="test", summary="test")  # Missing description

        with pytest.raises(ValidationError):
            Changelog(description="test", summary="test")  # Missing title

    def test_changelog_long_content(self):
        """Test Changelog with long content."""
        long_title = "A" * 1000
        long_description = "B" * 10000
        long_summary = "C" * 5000

        changelog = Changelog(
            title=long_title, description=long_description, summary=long_summary
        )

        assert len(changelog.title) == 1000
        assert len(changelog.description) == 10000
        assert len(changelog.summary) == 5000

    def test_changelog_with_markdown(self):
        """Test Changelog with markdown content."""
        changelog = Changelog(
            title="# Release v1.0.0",
            description="## Features\n- Authentication\n- Performance\n\n## Bug Fixes\n- Fixed login issue",
            summary="Release with **new features** and *bug fixes*.",
        )

        assert changelog.title.startswith("#")
        assert "##" in changelog.description
        assert "**" in changelog.summary
        assert "*" in changelog.summary

    def test_changelog_dict_conversion(self):
        """Test converting Changelog to dictionary."""
        changelog = Changelog(
            title="Release v1.0.0", description="Release notes", summary="Summary"
        )

        changelog_dict = changelog.model_dump()
        expected_dict = {
            "title": "Release v1.0.0",
            "description": "Release notes",
            "summary": "Summary",
        }

        assert changelog_dict == expected_dict


class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_complete_workflow_models(self):
        """Test a complete workflow using all models together."""
        # Start with a raw commit
        commit = Commit(
            hash="feat001",
            message="Add user registration",
            diff="+class UserRegistration:\n+    def register(self, user):\n+        return self.save(user)",
        )

        # Create enrichment response
        enrichment = EnrichedCommitResponse(
            category=CommitCategory.FEATURE,
            description="Implemented user registration functionality with data validation and secure storage",
        )

        # Combine into enriched commit
        enriched_commit = EnrichedCommit(
            **commit.model_dump(), **enrichment.model_dump()
        )

        # Verify enriched commit has all expected data
        assert enriched_commit.hash == "feat001"
        assert enriched_commit.message == "Add user registration"
        assert enriched_commit.category == CommitCategory.FEATURE
        assert "registration functionality" in enriched_commit.description

        # Create final changelog
        changelog = Changelog(
            title="Release v1.1.0 - User Management",
            description="## Features\n- User registration with validation\n\n## Details\nThis release introduces user registration functionality.",
            summary="Added user registration capabilities to the platform.",
        )

        # Verify changelog
        assert "User Management" in changelog.title
        assert "registration" in changelog.description
        assert "capabilities" in changelog.summary

    def test_model_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized correctly."""
        # Create instances of all models
        commit = Commit(hash="abc123", message="Test commit", diff="+test")

        enrichment = EnrichedCommitResponse(
            category=CommitCategory.FEATURE, description="Test feature"
        )

        enriched_commit = EnrichedCommit(
            hash="def456",
            message="Test enriched",
            diff="+enriched",
            category=CommitCategory.BUG_FIX,
            description="Test bug fix",
        )

        changelog = Changelog(
            title="Test Release", description="Test description", summary="Test summary"
        )

        # Serialize to JSON and back
        models = [commit, enrichment, enriched_commit, changelog]
        model_classes = [Commit, EnrichedCommitResponse, EnrichedCommit, Changelog]

        for model, model_class in zip(models, model_classes):
            json_str = model.model_dump_json()
            reconstructed = model_class.model_validate_json(json_str)
            assert model == reconstructed
