from loguru import logger
from typing import List
from services.extract_service.repoinsights.user import InsightsUser
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)


class LoadProjectDataController:
    def __init__(
        self,
        temp_db: DatabaseHandler,
        repository: InsightsRepository,
        repo_id: int,
        user_controller: LoadUserController,
    ) -> None:
        self.temp_db = temp_db
        self.repository = repository
        self.repo_id = repo_id
        self.user_controller = user_controller

    def load_members_data(self, members: List[InsightsUser]):
        logger.debug("Loading members for repository {name}", name=self.repository.name)
        for member in members:
            user_id = self.user_controller.load_user(member)
            member_data = {
                "user_id": user_id,
                "project_id": self.repo_id,
            }
            return self.temp_db.create_members(member_data)

    def load_watchers(self, watchers: List[InsightsUser]):
        logger.debug(
            "Loading watchers for repository {name}", name=self.repository.name
        )
        self.temp_db.create_watchers(watchers, self.repo_id)

    def load_watchers_data(self, watchers: List[InsightsUser]):
        self.load_watchers(watchers)
