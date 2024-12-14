from typing import Dict
from loguru import logger
from services.traspaso_service.db_connector.models import Project, User, Commit
from services.traspaso_service.db_connector.database_handler import DatabaseHandler
from services.traspaso_service.db_connector.models import (
    Project,
    User,
    Commit,
    Issue,
    PullRequest,
    ProjectMember,
    Extraction,
    RepoLabel,
    RepoMilestone,
    Watcher,
)


class Cache:
    def __init__(self) -> None:
        self.user_id_map = {}
        self.project_id_map = {}
        self.commit_id_map = {}
        self.commit_comment_id_map = {}
        self.issue_id_map = {}
        self.pull_request_id_map = {}
        self.pull_request_history_id_map = {}
        self.label_id_map = {}
