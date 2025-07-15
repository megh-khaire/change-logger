import os
from pathlib import Path
from typing import Optional

import typer
from change_logger_cli.client import AgentClient
from change_logger_cli.git import GitUtils
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="change-logger",
    help="Generate changelogs from git repositories using AI",
    add_completion=False,
)
console = Console()


def validate_git_repo(repo_path: str = ".") -> GitUtils:
    """Validate that we're in a git repository."""
    git_utils = GitUtils(repo_path)
    if not git_utils.is_git_repo():
        console.print(
            "[red]Error: Not a git repository or no git repository found.[/red]"
        )
        raise typer.Exit(1)
    return git_utils


@app.command()
def generate(
    repo_path: str = typer.Option(".", "--repo", "-r", help="Path to git repository"),
    from_ref: Optional[str] = typer.Option(
        None, "--from", "-f", help="Starting reference (tag, branch, or SHA)"
    ),
    to_ref: Optional[str] = typer.Option(
        "HEAD", "--to", "-t", help="Ending reference (tag, branch, or SHA)"
    ),
    auto: bool = typer.Option(
        False, "--auto", "-a", help="Automatically detect last version tag"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", help="Custom template for changelog generation"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
):
    """Generate changelog from git commits."""

    # Validate git repository
    git_utils = validate_git_repo(repo_path)

    # Validate OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[red]Error: OPENAI_API_KEY environment variable must be set.[/red]"
        )
        console.print("Please set your OpenAI API key:")
        console.print("export OPENAI_API_KEY='your-api-key-here'")
        raise typer.Exit(1)

    try:
        # Initialize agent client
        agent_client = AgentClient()

        # Determine which commits to process
        if auto:
            console.print("[blue]Auto-detecting last version tag...[/blue]")
            latest_tag = git_utils.get_latest_tag()
            if not latest_tag:
                console.print("[red]Error: No version tags found in repository.[/red]")
                raise typer.Exit(1)
            console.print(f"[green]Found latest tag: {latest_tag}[/green]")
            git_commits = git_utils.get_commits_between(latest_tag, to_ref)
        elif from_ref:
            console.print(f"[blue]Getting commits from {from_ref} to {to_ref}[/blue]")
            git_commits = git_utils.get_commits_between(from_ref, to_ref)
        else:
            console.print(
                "[red]Error: Must specify either --sha, --from, or --auto[/red]"
            )
            console.print("Use --help for more information.")
            raise typer.Exit(1)

        if not git_commits:
            console.print("[yellow]No commits found in the specified range.[/yellow]")
            raise typer.Exit(0)

        console.print(f"[green]Found {len(git_commits)} commit(s) to process[/green]")

        # Show commit summary
        table = Table(title="Commits to Process")
        table.add_column("SHA", style="cyan")
        table.add_column("Message", style="white")
        table.add_column("Author", style="green")

        for commit in git_commits[:10]:  # Show first 10 commits
            table.add_row(
                commit.hash[:8],
                (
                    commit.message.split("\n")[0][:50] + "..."
                    if len(commit.message) > 50
                    else commit.message.split("\n")[0]
                ),
                commit.author,
            )

        if len(git_commits) > 10:
            table.add_row("...", f"and {len(git_commits) - 10} more commits", "")

        console.print(table)

        # Load template if provided
        template = None
        if template_path:
            try:
                template = Path(template_path).read_text()
            except FileNotFoundError:
                console.print(
                    f"[red]Error: Template file not found: {template_path}[/red]"
                )
                raise typer.Exit(1)

        # Generate changelog
        with console.status("[bold green]Generating changelog with AI..."):
            changelog = agent_client.generate_changelog(git_commits, template)

        # Format and display changelog
        changelog_content = f"# {changelog.title}\n\n"
        changelog_content += f"{changelog.description}\n\n"
        changelog_content += f"## Summary\n\n{changelog.summary}\n"

        console.print(
            Panel(
                Markdown(changelog_content),
                title="Generated Changelog",
                border_style="green",
            )
        )

        # Save to file if specified
        if output:
            output_path = Path(output)
            output_path.write_text(changelog_content)
            console.print(f"[green]Changelog saved to: {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def tags(
    repo_path: str = typer.Option(".", "--repo", "-r", help="Path to git repository"),
):
    """List version tags in the repository."""
    git_utils = validate_git_repo(repo_path)

    version_tags = git_utils.get_version_tags()

    if not version_tags:
        console.print("[yellow]No version tags found in repository.[/yellow]")
        return

    table = Table(title="Version Tags")
    table.add_column("Tag", style="cyan")
    table.add_column("Latest", style="green")

    for i, tag in enumerate(version_tags):
        latest = "✓" if i == 0 else ""
        table.add_row(tag, latest)

    console.print(table)


@app.command()
def commits(
    from_ref: str = typer.Argument(help="Starting reference (tag, branch, or SHA)"),
    to_ref: str = typer.Argument("HEAD", help="Ending reference (tag, branch, or SHA)"),
    repo_path: str = typer.Option(".", "--repo", "-r", help="Path to git repository"),
):
    """List commits between two references."""
    git_utils = validate_git_repo(repo_path)

    try:
        git_commits = git_utils.get_commits_between(from_ref, to_ref)

        if not git_commits:
            console.print("[yellow]No commits found in the specified range.[/yellow]")
            return

        table = Table(title=f"Commits from {from_ref} to {to_ref}")
        table.add_column("SHA", style="cyan")
        table.add_column("Message", style="white")
        table.add_column("Author", style="green")
        table.add_column("Date", style="yellow")

        for commit in git_commits:
            table.add_row(
                commit.hash[:8],
                (
                    commit.message.split("\n")[0][:60] + "..."
                    if len(commit.message) > 60
                    else commit.message.split("\n")[0]
                ),
                commit.author,
                commit.date[:10],  # Show just the date part
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    repo_path: str = typer.Option(".", "--repo", "-r", help="Path to git repository"),
):
    """Show repository information."""
    git_utils = validate_git_repo(repo_path)

    latest_tag = git_utils.get_latest_tag()
    current_branch = git_utils.get_current_branch()
    remote_url = git_utils.get_remote_url()
    version_tags = git_utils.get_version_tags()

    table = Table(title="Repository Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Current Branch", current_branch)
    table.add_row("Remote URL", remote_url or "N/A")
    table.add_row("Latest Tag", latest_tag or "N/A")
    table.add_row("Total Version Tags", str(len(version_tags)))

    console.print(table)


if __name__ == "__main__":
    app()
