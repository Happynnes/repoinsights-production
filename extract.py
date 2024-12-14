from datetime import datetime
import argparse
from time import sleep
from typing import Optional
from loguru import logger
import gc


from services.extract_service.client import InsightsClient
from services.extract_service.excepctions.exceptions import (
    GitHubUserException,
    ProjectNotFoundError,
    LimitExceededError,
    EmptyQueueError,
)


class LoggerFile:
    def __init__(self, debug):
        self.debug = debug

    def setup(self, project: str):
        logger.remove()
        dt = datetime.now()
        dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
        logger.add(
            f"logs/extract-{project}-{dt_str}.log", backtrace=True, diagnose=True
        )


def handle_extract_exceptions(client: InsightsClient, e):
    if isinstance(e, GitHubUserException):
        client.enqueue_to_modificacion(
            action_type="rename", new={"owner": "new_name", "repo": "new_name"}
        )
        logger.exception(
            "Repositorio encontrado con otro nombre, encolando para eliminar",
            traceback=True,
        )
    elif isinstance(e, ProjectNotFoundError):
        client.enqueue_to_modificacion(action_type="delete")
        logger.exception(
            "Proyecto no encontrado, marcar como eliminado", traceback=True
        )
    elif isinstance(e, KeyboardInterrupt):
        logger.exception("Proceso interrumpido por el usuario", traceback=True)
        client.enqueue_to_pendientes()

    elif isinstance(e, LimitExceededError):
        logger.exception(
            "Se superó el límite de intentos, encolando para pendientes", traceback=True
        )
        client.enqueue_to_failed()
    elif isinstance(e, EmptyQueueError):
        # logger.info("No hay proyectos en la cola", traceback=False)
        return
    else:
        logger.exception(
            f"Fallo desconocido. encolando en pendientes: {e}", traceback=True
        )
        client.enqueue_to_pendientes()

    if not isinstance(e, EmptyQueueError):
        try:
            client.delete_from_temp()
        except Exception as e:
            logger.exception(
                f"Fallo desconocido al eliminar de la tabla temp: {e}", traceback=True
            )


def handle_load_exceptions(client: InsightsClient, e):
    logger.exception(f"Fallo en la carga. volviendo a encolar: {e}", traceback=True)
    client.enqueue_to_pendientes("load")


def main(debug: Optional[bool] = None) -> None:
    """
    "commits", "pull_requests", "issues", "labels", "stargazers", "members", "milestones
    """
    logger_client = LoggerFile(debug)
    results = None
    project = None

    data_types = [
        "commits",
        "pull_requests",
        "issues",
        "labels",
        "milestones",
    ]

    client = InsightsClient(data_types)
    tokens_file = client.check_tokens()
    if not tokens_file:
        return
    try:
        project = client.get_from_pendientes()
        if client.attempt > 2:
            raise LimitExceededError("Se superó el límite de intentos")

        logger_client.setup(project)
        results = client.extract()
        client.load(results)
        client.enqueue_to_curado()

    except Exception as e:
        handle_extract_exceptions(client, e)
        return
    finally:
        del results
        del project
        gc.collect()


if __name__ == "__main__":
    sleep_time = 60
    while True:
        parser = argparse.ArgumentParser(description="InsightsClient script")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        parser.add_argument(
            "--single",
            action="store_true",
            help="Run only one time and exit",
        )
        args = parser.parse_args()
        main(args.debug)
        sleep(sleep_time)
        if args.single:
            break
