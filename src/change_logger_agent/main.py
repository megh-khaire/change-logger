from typing import List

from dotenv import load_dotenv

from .llm import generate_llm_response
from .models import Changelog, Commit, EnrichedCommit, EnrichedCommitResponse
from .prompt import load_prompt
from .template import DEFAULT_TEMPLATE

load_dotenv()


def enrich_commit(commit: Commit) -> EnrichedCommit:
    prompt = load_prompt(
        "enrich_commit", commit_message=commit.message, diff=commit.diff
    )
    response = generate_llm_response(
        input=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        output_model=EnrichedCommitResponse,
    )
    enriched_commit_response = EnrichedCommitResponse.model_validate(response)
    return EnrichedCommit(
        **commit.model_dump(), **enriched_commit_response.model_dump()
    )


def generate_changelog(
    enriched_commits: List[EnrichedCommit], template: str = DEFAULT_TEMPLATE
):
    formatted_commit_chunks = []
    for commit in enriched_commits:
        formatted_commit_chunks.append(
            f"\nCommit Message: {commit.message}\n\nDescription: {commit.description}\n\nCategory: {commit.category}"
        )
    formatted_commits = "\n".join(formatted_commit_chunks)

    prompt = load_prompt(
        "generate_changelog", commits=formatted_commits, template=template
    )
    response = generate_llm_response(
        input=[
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ],
        output_model=Changelog,
    )
    return Changelog.model_validate(response)


def generate_changelog_from_commits(
    commits: List[Commit], template: str = DEFAULT_TEMPLATE
):
    enriched_commits = []
    for commit in commits:
        enriched_commit = enrich_commit(commit)
        enriched_commits.append(enriched_commit)
    changelog = generate_changelog(enriched_commits, template)
    return changelog
