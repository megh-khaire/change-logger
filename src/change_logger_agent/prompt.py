import yaml
from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """Utility class to load and format prompts from prompts.yml file."""

    def __init__(self, prompts_file: str = "../../resources/prompts.yml"):
        """Initialize the PromptLoader with the path to prompts file.

        Args:
            prompts_file: Path to the prompts YAML file, relative to this file's directory
        """
        self.prompts_file = Path(__file__).parent / prompts_file
        self._prompts = None

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from the YAML file."""
        if self._prompts is None:
            try:
                with open(self.prompts_file, "r", encoding="utf-8") as f:
                    self._prompts = yaml.safe_load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"Prompts file not found: {self.prompts_file}")
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML file: {e}")
        return self._prompts

    def get_prompt(self, prompt_name: str, **kwargs) -> Dict[str, str]:
        """Get a formatted prompt by name.

        Args:
            prompt_name: Name of the prompt to retrieve
            **kwargs: Variables to format the prompt with

        Returns:
            Dictionary containing 'system' and 'user' formatted prompts

        Raises:
            KeyError: If prompt_name is not found
            ValueError: If formatting fails
        """
        prompts = self._load_prompts()

        if prompt_name not in prompts:
            available_prompts = list(prompts.keys())
            raise KeyError(
                f"Prompt '{prompt_name}' not found. Available prompts: {available_prompts}"
            )

        prompt_config = prompts[prompt_name]

        try:
            formatted_prompt = {}

            # Format system prompt if it exists
            if "system" in prompt_config:
                formatted_prompt["system"] = prompt_config["system"].format(**kwargs)

            # Format user prompt if it exists
            if "user" in prompt_config:
                formatted_prompt["user"] = prompt_config["user"].format(**kwargs)

            return formatted_prompt

        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt formatting: {e}")

    def list_prompts(self) -> list:
        """List all available prompt names."""
        prompts = self._load_prompts()
        return list(prompts.keys())

    def get_prompt_structure(self, prompt_name: str) -> Dict[str, Any]:
        """Get the raw structure of a prompt without formatting.

        Args:
            prompt_name: Name of the prompt to retrieve

        Returns:
            Raw prompt configuration
        """
        prompts = self._load_prompts()

        if prompt_name not in prompts:
            available_prompts = list(prompts.keys())
            raise KeyError(
                f"Prompt '{prompt_name}' not found. Available prompts: {available_prompts}"
            )

        return prompts[prompt_name]


def load_prompt(prompt_name: str, **kwargs) -> Dict[str, str]:
    """Convenience function to load and format a prompt.

    Args:
        prompt_name: Name of the prompt to retrieve
        **kwargs: Variables to format the prompt with

    Returns:
        Dictionary containing 'system' and 'user' formatted prompts
    """
    loader = PromptLoader()
    return loader.get_prompt(prompt_name, **kwargs)
