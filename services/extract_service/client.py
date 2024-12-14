import json
from typing import Dict, Any, List, Union
from datetime import datetime
from loguru import logger
import uuid

from .utils.utils import format_dt, api_date
from services.extract_service.extract_module.extract_client import ExtractDataController
from .queue_module.enqueue_client import QueueController
from .load_module.load_client import LoadDataClient
from .excepctions.exceptions import LoadError, EmptyQueueError, TokensFileError
from services.extract_service.delete_uuid import DeleteFromTemp
from services.extract_service.config import GHToken


class InsightsClient:
    def __init__(self, data_types: List) -> None:
        self.data_types = data_types
        self.until = datetime.now()
        self.uuid = uuid.uuid4().hex
        self.attempt = 0
        self.project_id = None
        self.queue_client = QueueController()

        self.private = None

    def get_from_pendientes(self):
        pending_project = self.queue_client.get_from_queue()
        if pending_project:
            pending_repo = pending_project
            owner = pending_repo["owner"]
            repo = pending_repo["project"]
            since = (
                api_date(pending_repo["last_extraction"])
                if pending_repo["last_extraction"]
                else None
            )
            if pending_project.get("status"):
                self.uuid = pending_repo["status"]["uuid"]

            if pending_project.get("attempt"):
                self.attempt = pending_repo["attempt"]

            logger.critical("QUEUE pendientes {project}", project=pending_repo)
            self.pending_repo = pending_repo
            self.owner = owner
            self.repo = repo
            self.since = since
            if pending_project.get("private"):
                self.private = pending_project["private"]

            self.extract_data = ExtractDataController(
                owner=self.owner,
                repo=self.repo,
                since=self.since,
                until=self.until,
                data_types=self.data_types,
                private_token=self.private,
            )
            return f"{self.owner}/{self.repo}"

        else:
            # logger.critical("No hay proyectos pendientes")
            raise EmptyQueueError("No hay proyectos pendientes")

    def enqueue_to_modificacion(self, action_type, **kwargs):
        project_data = {}
        if action_type not in ["rename", "delete"]:
            raise ValueError('Invalid action_type. Must be either "rename" or "delete"')

        project_data["action"] = action_type
        project_data["project"] = {"owner": self.owner, "repo": self.repo}

        if action_type == "rename":
            new = kwargs.get("new")
            if not new:
                raise LoadError("No se especificó el nuevo nombre del proyecto")
            project_data["new"] = {"owner": new["owner"], "repo": new["repo"]}

        json_data = json.dumps(project_data)
        self.queue_client.enqueue(json_data, "modificaciones")

    def enqueue_to_failed(self):
        self.pending_repo["enqueue_time"] = datetime.now().isoformat()
        self.pending_repo["status"] = {"type": "extract", "uuid": self.uuid}

        json_data = json.dumps(self.pending_repo)
        self.queue_client.enqueue(json_data, "failed")

    def enqueue_to_pendientes(self, status=None):
        if status:
            self.pending_repo["enqueue_time"] = datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            self.pending_repo["status"] = {"type": status, "uuid": self.uuid}

        if self.pending_repo is None:
            raise LoadError("No hay proyecto pendiente")

        self.pending_repo["enqueue_time"] = datetime.now().isoformat()
        self.pending_repo["attempt"] = self.pending_repo["attempt"] + 1
        json_data = json.dumps(self.pending_repo)
        self.queue_client.enqueue(json_data, "pendientes")

    def extract(self) -> List[Dict[str, Any]]:
        logger.critical(
            "Extracting from GitHub {owner}/{project} DESDE -> {since} HASTA -> {until} {data_types}",
            owner=self.owner,
            project=self.repo,
            since=self.since,
            until=self.until,
            data_types=self.data_types,
        )
        print(
            f"Extracting from GitHub {self.owner}/{self.repo} DESDE -> {self.since} HASTA -> {self.until} {self.data_types}"
        )

        data = self.extract_data.extract()
        return data

    def load(self, results) -> None:
        logger.critical("Loading to TEMP DB")
        try:
            load_client = LoadDataClient(results, self.uuid, self.owner, self.repo)
            load_client.load_to_temp_db()
            self.project_id = load_client.get_project_id()
        except Exception as e:
            logger.critical(f"Error loading data to TEMP DB: {e}")
            raise LoadError("Error loading data to TEMP DB", e)

    def enqueue_to_curado(self) -> None:
        project_data = {
            "uuid": self.uuid,
            "owner": self.owner,
            "repo": self.repo,
            "project_id": self.project_id,
            "since": format_dt(self.since) if self.since else None,
            "until": format_dt(self.until) if self.until else None,
            "data_types": self.data_types,
        }
        json_data = json.dumps(project_data)
        self.queue_client.enqueue(json_data, "curado")
        logger.critical("Project ENQUEUE to CURADO published")

    def delete_from_temp(self):
        logger.critical("Deleting from TEMP DB")
        delete_client = DeleteFromTemp(self.uuid)
        delete_client.delete_all()

    def check_tokens(self):
        try:
            GHToken()
            return True
        except TokensFileError as e:
            logger.critical(f"Error al obtener tokens: {e}")
            return False
