import re
from typing import List, Optional

import git
from git import Repo
from change_logger_cli.models import GitCommit


class GitUtils:
    """Utility class for git operations."""

    def __init__(self, repo_path: str = "."):
        """Initialize GitUtils with repository path."""
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def get_latest_tag(self) -> Optional[str]:
        """Get the latest git tag."""
        try:
            tags = sorted(
                self.repo.tags, key=lambda t: t.commit.committed_date, reverse=True
            )
            if tags:
                return tags[0].name
            return None
        except Exception:
            return None

    def get_commits_between(
        self, from_ref: str, to_ref: str = "HEAD"
    ) -> List[GitCommit]:
        """Get commits between two references."""
        try:
            commit_range = f"{from_ref}..{to_ref}"
            commits = list(self.repo.iter_commits(commit_range))

            git_commits = []
            for commit in commits:
                # Get the diff for this commit
                diff = self._get_commit_diff(commit)

                git_commits.append(
                    GitCommit(
                        hash=commit.hexsha,
                        message=commit.message.strip(),
                        diff=diff,
                        author=commit.author.name,
                        date=commit.committed_datetime.isoformat(),
                    )
                )

            return git_commits
        except Exception as e:
            raise ValueError(f"Error getting commits: {e}")

    def get_commits_from_shas(self, shas: List[str]) -> List[GitCommit]:
        """Get commits from a list of SHA hashes."""
        git_commits = []
        for sha in shas:
            try:
                commit = self.repo.commit(sha)
                diff = self._get_commit_diff(commit)

                git_commits.append(
                    GitCommit(
                        hash=commit.hexsha,
                        message=commit.message.strip(),
                        diff=diff,
                        author=commit.author.name,
                        date=commit.committed_datetime.isoformat(),
                    )
                )
            except Exception as e:
                raise ValueError(f"Error getting commit {sha}: {e}")

        return git_commits

    def _get_commit_diff(self, commit) -> str:
        """Get the diff for a commit."""
        try:
            # Get the diff against the first parent (or empty tree for initial commit)
            if commit.parents:
                diff = commit.parents[0].diff(commit, create_patch=True)
            else:
                # First commit - diff against empty tree
                diff = commit.diff(git.NULL_TREE, create_patch=True)

            # Convert diff to string
            diff_text = ""
            for item in diff:
                if item.diff:
                    diff_text += str(item.diff.decode("utf-8", errors="ignore"))

            return diff_text
        except Exception:
            return ""

    def get_version_tags(self) -> List[str]:
        """Get all version tags (tags that look like version numbers)."""
        tags = []
        version_pattern = re.compile(r"^v?\d+\.\d+\.\d+")

        for tag in self.repo.tags:
            if version_pattern.match(tag.name):
                tags.append(tag.name)

        # Sort by semantic version
        def version_key(tag):
            # Extract numbers from version string
            numbers = re.findall(r"\d+", tag)
            return tuple(int(n) for n in numbers)

        return sorted(tags, key=version_key, reverse=True)

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        return self.repo.active_branch.name

    def get_remote_url(self) -> Optional[str]:
        """Get the remote URL of the repository."""
        try:
            return self.repo.remotes.origin.url
        except Exception:
            return None

    def is_git_repo(self) -> bool:
        """Check if the current directory is a git repository."""
        try:
            self.repo.git_dir
            return True
        except Exception:
            return False
