from services.pending_service.db_controller import DBController
from services.pending_service.models import Project, Commit, Extraction
from sqlalchemy.orm import sessionmaker, aliased
from loguru import logger
from datetime import datetime
from sqlalchemy.sql.schema import Column
from sqlalchemy import func, and_, asc
from sqlalchemy.sql.functions import coalesce

from typing import List, Union, Dict, Any
from .utils import format_dt
from pprint import pprint
import json


class PendingProjectsController:
    def __init__(self, connector: DBController):
        self.connector = connector
        self.session_maker = sessionmaker(bind=connector.engine)
        self.db_session = self.session_maker()

    def get_updated_projects(self) -> List[Dict[str, Any]]:
        enqueue_list = []
        extraction_alias = aliased(Extraction)
        commit_alias = aliased(Commit)

        last_extractions = (
            self.db_session.query(
                extraction_alias.project_id.label("project_id"),
                func.max(extraction_alias.date).label("max_extraction_date"),
            )
            .group_by(extraction_alias.project_id)
            .subquery()
        )

        last_commits = (
            self.db_session.query(
                commit_alias.project_id.label("project_id"),
                func.max(commit_alias.created_at).label("max_commit_date"),
            )
            .group_by(commit_alias.project_id)
            .subquery()
        )

        projects_with_dates = (
            self.db_session.query(
                Project,
                coalesce(
                    last_extractions.c.max_extraction_date,
                    last_commits.c.max_commit_date,
                ).label("last_activity_date"),
            )
            .outerjoin(last_extractions, Project.id == last_extractions.c.project_id)
            .outerjoin(last_commits, Project.id == last_commits.c.project_id)
            .filter(Project.forked_from == None)
            .filter(
                coalesce(
                    last_extractions.c.max_extraction_date,
                    last_commits.c.max_commit_date,
                )
                < datetime.utcnow().date()
            )
            .order_by(asc("last_activity_date"))
            .all()
        )
        for project, last_activity_date in projects_with_dates:
            enqueue_list.append(
                {
                    "enqueue_time": datetime.now(),
                    "attempt": 1,
                    "owner": project.owner.login,
                    "project": project.name,
                    "last_extraction": format_dt(last_activity_date)
                    if last_activity_date != datetime.min
                    else None,
                }
            )
        return enqueue_list

    def get_json_projects(self) -> List[Dict[str, Any]]:
        logger.info("Getting test projects")
        with open("test_projects.json") as f:
            projects = json.load(f)
        return projects
