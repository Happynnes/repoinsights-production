import json
import os
from typing import Dict, Any
from loguru import logger
import pika
import argparse
from services.pending_service.db_controller import DBController
from services.pending_service.pending_controller import PendingProjectsController
from services.pending_service.queue_controller import QueueController


def main(debug: bool):
    """
    Main function
    """
    logger.info("Starting pendientes service DEBUG={debug}", debug=debug)
    db_connector = DBController()
    pending_projects = PendingProjectsController(db_connector)
    queue_client = QueueController()
    queue_client.connect()
    projects = (
        pending_projects.get_json_projects() if debug else pending_projects.get_updated_projects()
    )
    for project in projects:
        queue_client.enqueue(project)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InsightsClient script")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    main(args.debug)
