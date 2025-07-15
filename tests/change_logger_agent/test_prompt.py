from unittest.mock import patch

import pytest
import yaml

from src.change_logger_agent.prompt import PromptLoader, load_prompt


class TestPromptLoader:
    """Test the PromptLoader class."""

    def test_prompt_loader_initialization(self, tmp_path):
        """Test PromptLoader initialization with custom prompts file path."""
        prompts_file = tmp_path / "custom_prompts.yml"
        prompts_file.write_text("test: value")

        loader = PromptLoader(str(prompts_file))
        assert loader.prompts_file == prompts_file

    def test_prompt_loader_default_path(self):
        """Test PromptLoader initialization with default path."""
        loader = PromptLoader()
        # The path should resolve to resources/prompts.yml at project root
        assert "prompts.yml" in str(loader.prompts_file)
        assert str(loader.prompts_file).endswith("resources/prompts.yml")

    def test_load_prompts_success(self, tmp_path):
        """Test successful loading of prompts from YAML file."""
        prompts_content = {
            "enrich_commit": {
                "system": "You are a software engineer.",
                "user": "Analyze this commit: {commit_message}",
            },
            "generate_changelog": {
                "system": "You are a changelog generator.",
                "user": "Create changelog from: {commits}",
            },
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))
        prompts = loader._load_prompts()

        assert prompts == prompts_content
        assert "enrich_commit" in prompts
        assert "generate_changelog" in prompts

    def test_load_prompts_file_not_found(self, tmp_path):
        """Test prompt loading when file doesn't exist."""
        non_existent_file = tmp_path / "missing.yml"
        loader = PromptLoader(str(non_existent_file))

        with pytest.raises(FileNotFoundError, match="Prompts file not found"):
            loader._load_prompts()

    def test_load_prompts_invalid_yaml(self, tmp_path):
        """Test prompt loading with invalid YAML content."""
        prompts_file = tmp_path / "invalid.yml"
        prompts_file.write_text("invalid: yaml: content: [")

        loader = PromptLoader(str(prompts_file))

        with pytest.raises(ValueError, match="Error parsing YAML file"):
            loader._load_prompts()

    def test_get_prompt_success(self, tmp_path):
        """Test successful prompt retrieval and formatting."""
        prompts_content = {
            "test_prompt": {
                "system": "You are a {role}.",
                "user": "Process this {item} with {method}.",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))
        result = loader.get_prompt(
            "test_prompt", role="engineer", item="commit", method="analysis"
        )

        expected = {
            "system": "You are a engineer.",
            "user": "Process this commit with analysis.",
        }
        assert result == expected

    def test_get_prompt_not_found(self, tmp_path):
        """Test prompt retrieval when prompt name doesn't exist."""
        prompts_content = {"existing_prompt": {"system": "test", "user": "test"}}

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        with pytest.raises(KeyError, match="Prompt 'missing_prompt' not found"):
            loader.get_prompt("missing_prompt")

    def test_get_prompt_missing_parameter(self, tmp_path):
        """Test prompt retrieval when required parameter is missing."""
        prompts_content = {
            "test_prompt": {
                "system": "You need {required_param}.",
                "user": "Also need {another_param}.",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        with pytest.raises(ValueError, match="Missing required parameter"):
            loader.get_prompt(
                "test_prompt", required_param="value"
            )  # missing another_param

    def test_get_prompt_partial_formatting(self, tmp_path):
        """Test prompt with only system or user component."""
        prompts_content = {
            "system_only": {"system": "System message with {param}."},
            "user_only": {"user": "User message with {param}."},
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        system_result = loader.get_prompt("system_only", param="test")
        assert system_result == {"system": "System message with test."}

        user_result = loader.get_prompt("user_only", param="test")
        assert user_result == {"user": "User message with test."}

    def test_list_prompts(self, tmp_path):
        """Test listing all available prompt names."""
        prompts_content = {
            "prompt1": {"system": "test"},
            "prompt2": {"user": "test"},
            "prompt3": {"system": "test", "user": "test"},
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))
        prompt_names = loader.list_prompts()

        assert set(prompt_names) == {"prompt1", "prompt2", "prompt3"}
        assert len(prompt_names) == 3

    def test_get_prompt_structure(self, tmp_path):
        """Test getting raw prompt structure without formatting."""
        prompts_content = {
            "test_prompt": {
                "system": "Raw {param} system.",
                "user": "Raw {param} user.",
                "metadata": {"description": "Test prompt", "parameters": ["param"]},
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))
        structure = loader.get_prompt_structure("test_prompt")

        assert structure == prompts_content["test_prompt"]
        assert "{param}" in structure["system"]  # Should remain unformatted

    def test_prompt_caching(self, tmp_path):
        """Test that prompts are cached after first load."""
        prompts_content = {"test": {"system": "test", "user": "test"}}

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        # First load
        loader._load_prompts()
        first_prompts = loader._prompts

        # Second load should use cache
        loader._load_prompts()
        second_prompts = loader._prompts

        assert first_prompts is second_prompts  # Same object reference

    def test_complex_prompt_formatting(self, tmp_path):
        """Test prompt formatting with complex parameters."""
        prompts_content = {
            "complex_prompt": {
                "system": "Analyze commits for {project} in {language}.",
                "user": "Commits:\n{commits}\n\nDiffs:\n{diffs}\n\nOutput format: {format}",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        complex_params = {
            "project": "MyProject",
            "language": "Python",
            "commits": "commit1\ncommit2\ncommit3",
            "diffs": "+added line\n-removed line",
            "format": "JSON",
        }

        result = loader.get_prompt("complex_prompt", **complex_params)

        assert "MyProject" in result["system"]
        assert "Python" in result["system"]
        assert "commit1\ncommit2\ncommit3" in result["user"]
        assert "JSON" in result["user"]


class TestLoadPromptFunction:
    """Test the load_prompt convenience function."""

    def test_load_prompt_function_success(self, tmp_path):
        """Test the load_prompt convenience function."""
        prompts_content = {
            "test_prompt": {"system": "System: {param1}", "user": "User: {param2}"}
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        # Mock the default prompts file path
        with patch.object(
            PromptLoader,
            "__init__",
            lambda self, file=None: (
                setattr(self, "prompts_file", prompts_file),
                setattr(self, "_prompts", None),
            )[1],
        ):
            result = load_prompt("test_prompt", param1="value1", param2="value2")

            expected = {"system": "System: value1", "user": "User: value2"}
            assert result == expected

    def test_load_prompt_function_error_propagation(self, tmp_path):
        """Test that load_prompt function properly propagates errors."""
        prompts_file = tmp_path / "missing.yml"

        with patch.object(
            PromptLoader,
            "__init__",
            lambda self, file=None: (
                setattr(self, "prompts_file", prompts_file),
                setattr(self, "_prompts", None),
            )[1],
        ):
            with pytest.raises(FileNotFoundError):
                load_prompt("any_prompt")


class TestPromptLoaderIntegration:
    """Integration tests for PromptLoader with realistic scenarios."""

    def test_real_world_enrich_commit_prompt(self, tmp_path):
        """Test with realistic enrich_commit prompt."""
        prompts_content = {
            "enrich_commit": {
                "system": "You are an expert software engineer that analyzes git commits and categorizes them into types like feature, bug_fix, refactor, documentation, test, chore, style, security, or performance.",
                "user": "Analyze this commit and provide a category and detailed description:\n\nCommit Message: {commit_message}\n\nDiff:\n{diff}\n\nRespond with a JSON object containing 'category' and 'description' fields.",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        commit_params = {
            "commit_message": "Add user authentication system",
            "diff": "+class AuthService:\n+    def authenticate(user, password):\n+        return validate_credentials(user, password)",
        }

        result = loader.get_prompt("enrich_commit", **commit_params)

        assert "expert software engineer" in result["system"]
        assert "Add user authentication system" in result["user"]
        assert "class AuthService" in result["user"]
        assert "JSON object" in result["user"]

    def test_real_world_generate_changelog_prompt(self, tmp_path):
        """Test with realistic generate_changelog prompt."""
        prompts_content = {
            "generate_changelog": {
                "system": "You are an expert technical writer that creates comprehensive changelogs from git commit data.",
                "user": "Generate a changelog from these enriched commits:\n\n{commits}\n\nUse this template as a guide:\n{template}\n\nCreate a professional changelog with title, description, and summary.",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        changelog_params = {
            "commits": "Commit 1: feature - Added auth\nCommit 2: bug_fix - Fixed login\nCommit 3: refactor - Cleaned code",
            "template": "# Release v{version}\n## Features\n{features}\n## Bug Fixes\n{bug_fixes}",
        }

        result = loader.get_prompt("generate_changelog", **changelog_params)

        assert "technical writer" in result["system"]
        assert "Added auth" in result["user"]
        assert "Release v{version}" in result["user"]
        assert "professional changelog" in result["user"]

    def test_multiple_prompts_same_loader(self, tmp_path):
        """Test using same loader for multiple different prompts."""
        prompts_content = {
            "prompt_a": {
                "system": "System A with {param_a}",
                "user": "User A with {param_b}",
            },
            "prompt_b": {
                "system": "System B with {param_c}",
                "user": "User B with {param_d}",
            },
            "prompt_c": {"user": "Only user C with {param_e}"},
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        # Test multiple prompt retrievals
        result_a = loader.get_prompt("prompt_a", param_a="A1", param_b="A2")
        result_b = loader.get_prompt("prompt_b", param_c="B1", param_d="B2")
        result_c = loader.get_prompt("prompt_c", param_e="C1")

        assert result_a["system"] == "System A with A1"
        assert result_a["user"] == "User A with A2"

        assert result_b["system"] == "System B with B1"
        assert result_b["user"] == "User B with B2"

        assert "system" not in result_c
        assert result_c["user"] == "Only user C with C1"

    def test_prompt_with_special_characters(self, tmp_path):
        """Test prompt handling with special characters and edge cases."""
        prompts_content = {
            "special_prompt": {
                "system": "Handle special chars: {special} and newlines\n{newline_param}",
                "user": "Unicode test: {unicode} and symbols: {symbols}",
            }
        }

        prompts_file = tmp_path / "prompts.yml"
        with open(prompts_file, "w") as f:
            yaml.dump(prompts_content, f)

        loader = PromptLoader(str(prompts_file))

        special_params = {
            "special": "!@#$%^&*()",
            "newline_param": "line1\nline2\nline3",
            "unicode": "café résumé naïve",
            "symbols": "→ ← ↑ ↓ ★ ♠ ♣ ♥ ♦",
        }

        result = loader.get_prompt("special_prompt", **special_params)

        assert "!@#$%^&*()" in result["system"]
        assert "line1\nline2\nline3" in result["system"]
        assert "café résumé naïve" in result["user"]
        assert "→ ← ↑ ↓" in result["user"]
