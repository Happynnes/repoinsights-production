from services.extract_service.extract_module.github_api.extractor import GitHubExtractor
from services.extract_service.repoinsights.label import InsightsLabel


class InsightsLabelHandler:
    def __init__(self, repo: GitHubExtractor):
        self.repo = repo

    def get_labels(self):
        labels = self.repo.obtener_labels()
        return [InsightsLabel(label) for label in labels]
