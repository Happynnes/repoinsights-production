import pika
import os
from loguru import logger
import json
from typing import Dict, Any, Union, Optional
from .exceptions import EmptyQueueError


class QueueClient:
    def __init__(self):
        self.user = os.environ["RABBIT_USER"]
        self.password = os.environ["RABBIT_PASS"]
        self.host = os.environ["RABBIT_HOST"]
        self.queue_curado = os.environ["RABBIT_QUEUE_CURADO"]
        self.queue_failed = os.environ["RABBIT_QUEUE_FAILED"]
        self.queue_pendientes = os.environ["RABBIT_QUEUE_PENDIENTES"]
        self.queue_modificaciones = os.environ["RABBIT_QUEUE_MODIFICACIONES"]
        self.queue_pausa = os.environ["RABBIT_QUEUE_PAUSA"]
        self.credentials = pika.PlainCredentials(self.user, self.password)

    def _get_connection(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=self.credentials)
        )
        return connection

    def get_from_queue_curado(self) -> Dict[str, Any]:
        connection = self._get_connection()
        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_curado, durable=True)
            method_frame, _, body = channel.basic_get(self.queue_curado)
            if method_frame is None:
                raise EmptyQueueError("Error obteniendo de curado")

            channel.basic_ack(method_frame.delivery_tag) if method_frame else None
            data = body.decode("utf-8")
            project = json.loads(data)
            if project is None:
                raise Exception("No hay proyectos en la cola")

            return project

        finally:
            connection.close()

    def enqueue_failed(self, project: str):
        self.enqueue(project, self.queue_failed)

    def enqueue_pendientes(self, project: str):
        self.enqueue(project, self.queue_pendientes)

    def enqueue_curado(self, project: str):
        self.enqueue(project, self.queue_curado)

    def enqueue_to_specific_queue(self, queue: str, project: str):
        self.enqueue(project, queue)

    def enqueue(self, project: str, queue: str):
        connection = self._get_connection()
        try:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=project,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
            logger.info(f"Project {project} published to queue {queue}")
        finally:
            connection.close()
