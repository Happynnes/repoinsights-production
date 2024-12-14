from services.extract_service.extract_module.extract_client import GitHubExtractor
from typing import Dict, Any
from services.extract_service.repoinsights.repository import InsightsRepository


class InsightsRepositoryHandler:
    def __init__(self, repo: GitHubExtractor) -> None:
        self.repo = repo

    def get_main_repo(self):
        repo = self.repo.obtener_repo_info()
        return InsightsRepository(repo)
