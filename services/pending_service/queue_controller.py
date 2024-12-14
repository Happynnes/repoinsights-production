from typing import Any, Dict
import json
import os
import pika
from loguru import logger

class RabbitMQError(Exception):
    """
    Handle all rabbitmq errors
    """


class QueueController:
    """
    Class to connect to rabbitmq
    """

    def __init__(self) -> None:
        self.rabbit_user = os.environ["RABBIT_USER"]
        self.rabbit_pass = os.environ["RABBIT_PASS"]
        self.rabbit_host = os.environ["RABBIT_HOST"]
        self.channel = None

    def connect(self):
        """
        Create or get a channel to rabbitmq
        """
        credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_pass)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials)
        )
        self.channel = connection.channel()
        self.channel.queue_declare(queue="pendientes", durable=True)

    def enqueue(self, project: Dict[str, Any]):
        """
        Add message to queue pendientes
        """
        project_json = json.dumps(project, default=str)
        if self.channel is None:
            raise RabbitMQError("Channel not found")

        self.channel.basic_publish(
            exchange="",
            routing_key="pendientes",
            body=project_json,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
            mandatory=True,
        )
        logger.info("Enqueued project {project}", project=project_json)
