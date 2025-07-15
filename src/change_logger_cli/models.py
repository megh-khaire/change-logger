from pydantic import BaseModel


class GitCommit(BaseModel):
    hash: str
    message: str
    diff: str
    author: str
    date: str
