from typing import Dict, Any, List, Tuple, Union
from loguru import logger
from typing import Dict, Any, List
import json
from time import sleep
from datetime import datetime

from services.traspaso_service.queue_client import QueueClient
from services.traspaso_service.db_connector.connector import DBConnector
from services.traspaso_service.db_connector.database_handler import DatabaseHandler
from services.traspaso_service.traspaso.traspaso import Client as TraspasoClient
from services.traspaso_service.exceptions import EmptyQueueError
from services.metrics_service.calc import calculate_metrics
from services.traspaso_service.delete_from_temp import DeleteFromTemp


class UUIDNotFoundException(Exception):
    pass


class LoggerFile:
    def __init__(self, debug):
        self.debug = debug

    def setup(self, project: str):
        logger.remove()
        dt = datetime.now()
        dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
        logger.add(
            f"logs/trapaso-{project}-{dt_str}.log", backtrace=True, diagnose=True
        )


def add_attempt(project: Dict):
    if project.get("attempt") is None:
        project["attempt"] = 0
    project["attempt"] = project["attempt"] + 1
    return project


def add_to_queue(project: Dict, queue_client: QueueClient):
    logger.error(
        "Error al traspasar el proyecto {project} encolado nuevamente", project=project
    )
    project = add_attempt(project)

    if project["attempt"] > 2:
        logger.error(
            "Se superó el límite de intentos, encolando para fallidos",
            traceback=True,
        )
        project["status"] = {"type": "traspaso", "uuid": project["uuid"]}
        json_data = json.dumps(project)
        queue_client.enqueue_failed(json_data)
        return

    json_data = json.dumps(project)
    queue_client.enqueue_curado(json_data)


def all_done(failed: List[Dict[str, Any]], saved: List[Dict[str, Any]]):
    logger.warning(
        "Todos los proyectos ya han sido traspasados \t fallidos {failed_projects} \t exitosos {saved_projects}",
        failed_projects=len(failed),
        saved_projects=len(saved),
    )


def main() -> None:
    queue_client = QueueClient()
    try:
        project = queue_client.get_from_queue_curado()
    except EmptyQueueError:
        # print("No hay proyectos en la cola")
        return

    except Exception as e:
        logger.exception("Error obteniendo de curado", traceback=True)
        return

    db_handler = DatabaseHandler(DBConnector())
    if project.get("uuid") is None:
        raise UUIDNotFoundException("No se ha podido obtener el uuid del proyecto")

    uuid = project["uuid"]
    logger.info("Traspasando proyecto {project}", project=project)
    traspaso_client = TraspasoClient(db_handler, uuid)
    try:
        LoggerFile(debug=True).setup(f"{project['owner']}/{project['repo']}")
        traspaso_client.migrate()
        calculate_metrics(project["repo"], project["uuid"])
        logger.info("Proyecto traspasado {project}", project=project)

    except Exception as e:
        logger.exception("Error", traceback=True)
        add_to_queue(
            project,
            queue_client,
        )

    DeleteFromTemp(uuid).delete_all()
    logger.info(
        "Proyecto eliminado de la base de datos temporal {project}", project=project
    )


if __name__ == "__main__":
    sleep_time = 60
    while True:
        main()
        print(f"Esperando {sleep_time} segundos")
        sleep(sleep_time)
