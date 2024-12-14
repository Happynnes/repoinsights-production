import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..github_api import GitHubAPI
from .user import User
from services.extract_service.utils.utils import add_users_to_dict_keys
from .user import User
from services.extract_service.utils.utils import add_users_to_dict_keys


class Issue:
    def __init__(self, api: GitHubAPI, usuario, repositorio) -> None:
        self.usuario = usuario
        self.api = api
        self.repositorio = repositorio

    def obtener_issues(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/issues"
        params: Dict[str, Any] = {"per_page": 100}
        if state:
            params["state"] = state
        if since:
            params["since"] = since

        issues = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            name="issues",
            url=url,
            params=params,
        )

        issues_filtrados = self.api._filtrar_por_fecha(issues, since, until)
        users = User(self.api)._get_users_for_keys(
            issues_filtrados, ["user", "assignee"]
        )
        add_users_to_dict_keys(issues_filtrados, users, ["user", "assignee"])
        return issues_filtrados

    def obtener_issues_comments(self) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/issues/comments"
        params = {"per_page": 100}
        issues_comments = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            name="issues_comments",
            url=url,
            params=params,
        )
        users = User(self.api)._get_users_for_keys(issues_comments, ["user"])
        add_users_to_dict_keys(issues_comments, users, ["user"])
        return issues_comments

    def obtener_issue_events(self, issue_id) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/issues/{issue_id}/events"
        params = {"per_page": 100}
        issues_events = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            name=f"issues_events de {issue_id}",
            url=url,
            params=params,
        )
        users = User(self.api)._get_users_for_keys(issues_events, ["actor"])
        add_users_to_dict_keys(issues_events, users, ["actor"])
        return issues_events

    def obtener_issues_events(self) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/repos/{self.usuario}/{self.repositorio}/issues/events"
        params = {"per_page": 100}
        issues_events = self.api.rate_limit_handling(
            self.api._realizar_solicitud_paginada,
            name="issues_events",
            url=url,
            params=params,
        )
        users = User(self.api)._get_users_for_keys(issues_events, ["actor"])
        add_users_to_dict_keys(issues_events, users, ["actor"])
        return issues_events
