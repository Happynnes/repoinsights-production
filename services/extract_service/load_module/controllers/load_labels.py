from typing import List
from loguru import logger
from services.extract_service.repoinsights.label import InsightsLabel
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)


class LoadLabelController:
    def __init__(
        self, temp_db: DatabaseHandler, repo_id: int, repository: InsightsRepository
    ) -> None:
        self.temp_db = temp_db
        self.repo_id = repo_id
        self.repository = repository

    def load_labels_data(self, labels: List[InsightsLabel]):
        logger.debug("Loading labels for repository {name}", name=self.repository.name)
        for label in labels:
            label.set_project_id(self.repo_id)
            self.temp_db.create_label(label)
