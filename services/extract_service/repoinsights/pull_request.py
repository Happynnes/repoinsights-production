from .comment import InsightsPullRequestComment
from .repository import InsightsRepository
from .commit import InsightsCommit
from .user import InsightsUser
from typing import Union, List, Dict, Any
from loguru import logger
import json


class InsightsPullRequest:
    """
    Pendientes: additions, deletion, changed_files
    """

    def __init__(self, pull_request: Dict[str, Any]):
        self.number: int = pull_request["number"]
        self.title = pull_request["title"]
        self.description = pull_request["body"]
        self.state = pull_request["state"]
        self.created_at = pull_request["created_at"]
        self.updated_at = pull_request["updated_at"]
        self.closed_at = pull_request["closed_at"]
        self.merged_at = pull_request["merged_at"]
        self.merged = True if pull_request["merged_at"] else False
        self.base_branch = pull_request["base"]["ref"]
        self.head_branch = pull_request["head"]["ref"]
        self.base_commit_sha = pull_request["base"]["sha"]
        self.head_commit_sha = pull_request["head"]["sha"]
        self.body = pull_request["body"]
        self.author = InsightsUser(pull_request["user"])

        self.base_repo = self.set_repo(pull_request["base"]["repo"])
        self.head_repo = self.set_repo(pull_request["head"]["repo"])

        self.intra_branch = self.set_intra_branch(pull_request)
        self.comments = []
        self.commits = []
        self.base_repo_id = None
        self.head_repo_id = None

    def set_repo(self, repo: Dict[str, Any]) -> Union[InsightsRepository, None]:
        return InsightsRepository(repo) if repo else None

    def set_intra_branch(self, pr: Dict) -> bool:
        if pr["head"]["repo"] is None or pr["base"]["repo"] is None:
            return False
        return (
            True
            if pr["base"]["repo"]["full_name"] == pr["head"]["repo"]["full_name"]
            else False
        )

    def __str__(self):
        return f"Pull Request #{self.number} ({self.state})"

    def set_head_commit(self, commit: InsightsCommit):
        self.head_commit = commit

    def set_base_commit(self, commit: InsightsCommit):
        self.base_commit = commit

    def set_head_commit_id(self, commit_id: int):
        self.head_commit_id = commit_id

    def set_base_commit_id(self, commit_id: int):
        self.base_commit_id = commit_id

    def set_head_repo_id(self, repo_id: int):
        self.head_repo_id = repo_id

    def set_base_repo_id(self, repo_id: int):
        self.base_repo_id = repo_id

    def set_comments(self, comments: list[InsightsPullRequestComment]):
        self.comments = comments

    def set_user_id(self, user_id: int):
        self.user_id = user_id

    def set_project_id(self, project_id: int):
        self.project_id = project_id

    def set_commits(self, commits: List[InsightsCommit]):
        self.commits = commits

    def to_dict(self):
        return {
            "head_repo_id": self.head_repo_id,
            "base_repo_id": self.base_repo_id,
            "head_commit_id": self.head_commit_id,
            "base_commit_id": self.base_commit_id,
            "user_id": self.user_id,
            "pullreq_id": self.number,
            "intra_branch": self.intra_branch,
            "merged": self.merged,
            # "additions": self.additions,
            # "deletions": self.deletions,
            # "changed_files": self.changed_files,
        }
