from enum import StrEnum

from pydantic import BaseModel


class CommitCategory(StrEnum):
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    TEST = "test"
    CHORE = "chore"
    STYLE = "style"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Commit(BaseModel):
    hash: str
    message: str
    diff: str


class EnrichedCommitResponse(BaseModel):
    category: CommitCategory
    description: str


class EnrichedCommit(Commit, EnrichedCommitResponse):
    pass


class Changelog(BaseModel):
    title: str
    description: str
    summary: str
