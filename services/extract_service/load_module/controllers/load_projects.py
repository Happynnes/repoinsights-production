from loguru import logger
from typing import List

from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)
from services.extract_service.repoinsights.milestone import InsightsMilestone


class LoadProjectController:
    def __init__(
        self, user_controller: LoadUserController, temp_db: DatabaseHandler
    ) -> None:
        self.user_controller = user_controller
        self.temp_db = temp_db

    def main_project(self, repo_data: InsightsRepository):
        self.repository = repo_data
        owner = self.repository.owner if self.repository.owner is not None else None
        if owner:
            owner_id = self.user_controller.load_user(owner)
            self.repository.set_owner_id(owner_id)

        self.repo_id = self.load_repository(self.repository)

        self.repository.set_repo_id(self.repo_id)
        self.load_extraction_project(self.repo_id)
        return self.repo_id, self.repository

    def load_extraction_project(self, repo_id: int):
        logger.debug(
            "Loading extraction project for repository {name}",
            name=self.repository.name,
        )
        return self.temp_db.create_extraction_project(repo_id)

    def load_repository(self, repository: InsightsRepository):
        logger.debug(
            "Loading repository {owner} {name}",
            owner=repository.owner,
            name=repository.name,
        )
        return self.temp_db.create_project(repository)

    def update_repo_data(self, pr_repo: InsightsRepository | None):
        if pr_repo is None:
            return

        if pr_repo.forked_from is True:
            pr_repo.set_forked_from_id(self.repo_id)
        if pr_repo.owner is not None:
            pr_repo.set_owner_id(self.user_controller.load_user(pr_repo.owner))

    def load_milestones_data(self, milestones: List[InsightsMilestone]):
        logger.debug(
            "Loading milestones for repository {name}", name=self.repository.name
        )
        for milestone in milestones:
            milestone.set_repo_id(self.repo_id)
            self.temp_db.create_milestone(milestone)
