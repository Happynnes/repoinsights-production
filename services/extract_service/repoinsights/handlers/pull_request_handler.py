from typing import List, Union, Optional, Dict, Any
from ..pull_request import InsightsPullRequest
from ..comment import InsightsPullRequestComment
from ..commit import InsightsCommit
from datetime import datetime
from services.extract_service.extract_module.extract_client import GitHubExtractor
from ...utils.utils import get_int_from_dict
from pprint import pprint
from loguru import logger
from services.extract_service.extract_module.github_api.github_api import GitHubError


class InsightsPullRequestHandler:
    def __init__(self, repo: GitHubExtractor):
        self.repo = repo

    def get_all_pull_requests(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[InsightsPullRequest]:
        processed_pull_requests = []
        pull_requests = self.repo.obtener_pull_requests(
            state="all", since=start_date, until=end_date
        )
        for pr in pull_requests:
            try:
                processed_pull_requests.append(self._process_pull_request(pr))
            except GitHubError as e:
                logger.exception(
                    f"Error al procesar pull request {pr['number']} {e}",
                    traceback=True,
                    e=e,
                )
                continue

        return processed_pull_requests

    def _process_pull_request(self, pr: Dict[str, Any]):
        gh_pr = InsightsPullRequest(pr)
        self._set_pull_request_commits(gh_pr)
        return gh_pr

    def _set_pull_request_commits(self, pull_request: InsightsPullRequest) -> None:
        base_commit = InsightsCommit(
            self.repo.obtener_commit(pull_request.base_commit_sha)
        )
        head_commit = InsightsCommit(
            self.repo.obtener_commit(pull_request.head_commit_sha)
        )
        pull_request.set_base_commit(base_commit)
        pull_request.set_head_commit(head_commit)

    def get_pull_request_comments(self, pull_requests: List[InsightsPullRequest]):
        comments = self.repo.obtener_pull_requests_comments()
        for pull_request in pull_requests:
            pull_request_comments = [
                InsightsPullRequestComment(comment)
                for comment in comments
                if get_int_from_dict(comment, "pull_request_url") == pull_request.number
            ]
            pull_request.set_comments(pull_request_comments)

    def get_pull_request_commits(self, pull_requests: List[InsightsPullRequest]):
        for pull_request in pull_requests:
            commits = self.repo.obtener_pull_requests_commits(pull_request.number)
            insight_commits = [InsightsCommit(commit) for commit in commits]
            pull_request.set_commits(insight_commits)
