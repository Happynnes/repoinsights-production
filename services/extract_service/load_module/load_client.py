from pprint import pprint
from typing import List, Dict, Any
from loguru import logger

from services.extract_service.load_module.db_connector.connector import DBConnector
from services.extract_service.load_module.db_connector.database_handler import (
    DatabaseHandler,
)
from services.extract_service.excepctions.exceptions import ExtractDataResulstsError
from services.extract_service.load_module.controllers.load_commits import (
    LoadCommitController,
)
from services.extract_service.load_module.controllers.load_issues import (
    LoadIssueController,
)
from services.extract_service.load_module.controllers.load_labels import (
    LoadLabelController,
)
from services.extract_service.load_module.controllers.load_projects import (
    LoadProjectController,
)
from services.extract_service.load_module.controllers.load_pull_requests import (
    LoadPullRequestController,
)
from services.extract_service.load_module.controllers.load_users import (
    LoadUserController,
)
from services.extract_service.load_module.controllers.load_project_data import (
    LoadProjectDataController,
)
from services.extract_service.repoinsights.repository import InsightsRepository
from .sort_results import ResultSorter


class LoadDataClient:
    def __init__(
        self,
        results: List[Dict[str, Any]],
        uuid: str,
        owner: str,
        project: str,
    ) -> None:
        self.temp_db = DatabaseHandler(DBConnector("temp"), uuid)
        self.sorted_results = ResultSorter.sort(results)
        self.owner = owner
        self.project_name = project

        self.user_controller = LoadUserController(temp_db=self.temp_db)
        self.project_controller = LoadProjectController(
            temp_db=self.temp_db,
            user_controller=self.user_controller,
        )

    def load_controllers(self, project_id: int, project: InsightsRepository):
        self.commit_controller = LoadCommitController(
            temp_db=self.temp_db,
            repo_id=project_id,
            user_controller=self.user_controller,
        )
        self.pull_request_controller = LoadPullRequestController(
            temp_db=self.temp_db,
            user_controller=self.user_controller,
            commit_controller=self.commit_controller,
            project_controller=self.project_controller,
            repo_id=project_id,
        )
        self.issue_controller = LoadIssueController(
            temp_db=self.temp_db,
            repo_id=project_id,
            user_controller=self.user_controller,
        )
        self.label_controller = LoadLabelController(
            temp_db=self.temp_db,
            repo_id=project_id,
            repository=project,
        )

        self.project_data_controller = LoadProjectDataController(
            temp_db=self.temp_db,
            repository=project,
            repo_id=project_id,
            user_controller=self.user_controller,
        )

    def load_to_temp_db(self):
        for result in self.sorted_results:
            name, data = result["name"], result["data"]
            logger.critical(f"Loading {name}")
            if name == "project":
                self.repo_id, self.project = self.project_controller.main_project(data)
                self.load_controllers(self.repo_id, self.project)

            if name == "commit":
                self.commit_controller.load_commits_data(data)
            elif name == "watchers":
                self.project_data_controller.load_watchers_data(data)
            elif name == "pull_request":
                self.pull_request_controller.load_pull_requests_data(data)
            elif name == "issue":
                self.issue_controller.load_issues_data(data)
            elif name == "members":
                self.project_data_controller.load_members_data(data)
            elif name == "milestones":
                self.project_controller.load_milestones_data(data)
            elif name == "labels":
                self.label_controller.load_labels_data(data)

    def get_project_id(self) -> int:
        return self.project.id
