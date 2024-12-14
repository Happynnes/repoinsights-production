from typing import Union, List
from services.extract_service.repoinsights.commit import InsightsCommit
from services.extract_service.repoinsights.comment import InsightsCommitComment
from services.extract_service.extract_module.github_api.extractor import GitHubExtractor
from datetime import datetime
from typing import Dict, Any


class InsightsCommitHandler:
    def __init__(self, repo: GitHubExtractor):
        self.repo = repo

    def get_commits(self, since: Union[None, datetime], until: Union[None, datetime]):
        kwargs: Dict[str, Any] = {}
        if since:
            kwargs["since"] = since
        if until:
            kwargs["until"] = until

        commits = self.repo.obtener_commits(**kwargs)
        return [InsightsCommit(commit) for commit in commits]

    def get_commit(self, commit_sha: str):
        commit = self.repo.obtener_commit(commit_sha)
        return InsightsCommit(commit)

    def get_commit_comments(self, commits: List[InsightsCommit]):
        comments = self.repo.obtener_comments()
        for commit in commits:
            # find commit.id in comments list
            commit_comments = [
                InsightsCommitComment(comment)
                for comment in comments
                if comment["commit_id"] == commit.sha
            ]
            commit.set_comments(commit_comments)
