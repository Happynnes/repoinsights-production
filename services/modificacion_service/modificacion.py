from typing import Any, Dict
from pprint import pprint

from .conn import ConsolidadaConnection
from .models import Project


class ConsolidadaHandler:
    def __init__(self) -> None:
        self.session = ConsolidadaConnection.get_session()

    def __del__(self) -> None:
        self.session.close()

    def rename_project(self, message) -> None:
        current = message["current"]
        c_owner, c_name = current["owner"], current["repo"]

        new = message["new"]
        n_owner, n_name = new["owner"], new["repo"]

        project = (
            self.session.query(Project).filter_by(owner_id=c_owner, name=c_name).first()
        )
        if project:
            project.owner_id = n_owner
            project.name = n_name
            self.session.commit()

    def delete_project(self, message) -> None:
        current = message["project"]
        c_owner, c_name = current["owner"], current["repo"]

        project = (
            self.session.query(Project)
            .filter(Project.name == c_name, Project.forked_from.is_(None))
            .first()
        )
        pprint(project)
        if project:
            project.deleted = True  # type: ignore
            self.session.commit()

    def handle(self, message: Dict[str, Any]) -> None:
        action = message["action"]

        if action == "rename":
            self.rename_project(message)

        elif action == "delete":
            self.delete_project(message)
        else:
            raise BaseException("Invalid action")
