import os
from typing import Callable, List, Optional

from change_logger_agent.main import generate_changelog_from_commits
from change_logger_agent.models import Changelog, Commit
from change_logger_cli.models import GitCommit


class AgentClient:
    """Client for interacting with the changelog generation agent."""

    def __init__(self):
        """Initialize the agent client."""
        # Ensure OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable must be set")

    def generate_changelog(
        self,
        git_commits: List[GitCommit],
        template: str = None,
        progress_callback: Optional[Callable] = None,
    ) -> Changelog:
        """Generate changelog from git commits using the agent."""
        # Convert GitCommit objects to agent Commit objects
        agent_commits = []
        for git_commit in git_commits:
            agent_commit = Commit(
                hash=git_commit.hash, message=git_commit.message, diff=git_commit.diff
            )
            agent_commits.append(agent_commit)

        # Use the agent to generate changelog
        if template:
            changelog = generate_changelog_from_commits(
                agent_commits, template, progress_callback
            )
        else:
            changelog = generate_changelog_from_commits(
                agent_commits, progress_callback=progress_callback
            )

        return changelog
