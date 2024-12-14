from ..user import InsightsUser
from services.extract_service.extract_module.github_api.extractor import GitHubExtractor
from ...repoinsights.user import InsightsUser
from datetime import datetime
from typing import List, Dict, Any, Union


class InsightsProjectUserHandler:
    def __init__(self, repo: GitHubExtractor):
        self.repo = repo

    def get_members(self, since=None, until=None):
        members = self.repo.obtener_contribuidores()
        if since and until:
            return [
                InsightsUser(member)
                for member in members
                if since <= member["created_at"] <= until
            ]
        return [InsightsUser(member) for member in members]

    def get_stargazers(
        self, since: Union[datetime, None] = None, until: Union[datetime, None] = None
    ) -> List[InsightsUser]:
        stargazers = self.repo.obtener_stargazers()
        if since and until:
            return [
                InsightsUser(stargazer["user"])
                for stargazer in stargazers
                if since <= stargazer["starred_at"] <= until
            ]
        return [InsightsUser(stargazer["user"]) for stargazer in stargazers]
