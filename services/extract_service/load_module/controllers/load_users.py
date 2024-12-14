from loguru import logger
from typing import List
from services.extract_service.repoinsights.user import InsightsUser
from services.extract_service.repoinsights.repository import InsightsRepository
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)


class LoadUserController:
    def __init__(self, temp_db: DatabaseHandler) -> None:
        self.temp_db = temp_db

    def load_user(self, user: InsightsUser) -> int:
        logger.debug("Loading user {login}", login=user.login)
        return self.temp_db.create_user(user)
