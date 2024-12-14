from typing import Optional, Dict, Any, List
from datetime import datetime
from services.extract_service.extract_module.github_api.controllers.repository import (
    Repository,
)
from services.extract_service.extract_module.github_api.controllers.commit import (
    Commit,
)
from services.extract_service.extract_module.github_api.controllers.user import User
from services.extract_service.extract_module.github_api.controllers.issue import Issue
from services.extract_service.extract_module.github_api.controllers.pull_request import (
    PullRequest,
)

from services.extract_service.extract_module.github_api.github_api import GitHubAPI


class GitHubExtractor:
    def __init__(
        self,
        usuario: str,
        repositorio: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        private_token: str | None = None,
    ):
        self.usuario = usuario
        self.since = since
        self.until = until
        self.api = GitHubAPI(private_token=private_token)

        self.user = User(self.api)
        self.repositorio = Repository(self.api, repositorio, usuario, self.user)
        self.commit = Commit(self.api, usuario, repositorio, self.user)
        self.issue = Issue(self.api, usuario, repositorio)
        self.pull_request = PullRequest(self.api, usuario, repositorio, self.user)

    def obtener_repo_info(self):
        return self.repositorio.obtener_repositorio()

    def obtener_contribuidores(self):
        return self.repositorio.obtener_contribuidores()

    def obtener_usuario(self, usuario):
        return self.user.obtener_usuario(usuario)

    def obtener_commits(self, since: Optional[datetime] = None, until=None):
        return self.commit.obtener_commits(since=since, until=until)

    def obtener_commit(self, commit_sha):
        return self.commit.obtener_commit(commit_sha)

    def obtener_commit_comments(self, commit_sha):
        return self.commit.obtener_commit_comments(commit_sha)

    def obtener_comments(self):
        return self.commit.obtener_comments()

    def obtener_issues(self, since=None, until=None, state=None):
        return self.issue.obtener_issues(since=since, until=until, state=state)

    def obtener_issues_comments(self):
        return self.issue.obtener_issues_comments()

    def obtener_issue_events(self, issue_id: str) -> List[Dict[str, Any]]:
        return self.issue.obtener_issue_events(issue_id)

    def obtener_issues_events(self):
        return self.issue.obtener_issues_events()

    def obtener_pull_requests(
        self, state=None, sort=None, direction=None, since=None, until=None
    ):
        return self.pull_request.obtener_pull_requests(
            state=state, sort=sort, direction=direction, since=since, until=until
        )

    def obtener_pull_requests_comments(self):
        return self.pull_request.obtener_pull_requests_comments()

    def obtener_pull_requests_commits(self, pull_request_number: int):
        return self.pull_request.obtener_pull_requests_commits(pull_request_number)

    def obtener_labels(self):
        return self.repositorio.obtener_labels()

    def obtener_stargazers(self):
        return self.repositorio.obtener_stargazers()

    def obtener_milestone(self, state=None):
        return self.repositorio.obtener_milestone(state=state)
