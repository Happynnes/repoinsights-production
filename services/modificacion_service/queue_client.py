import pika
import os
from loguru import logger
import json
from typing import Dict, Any, Union, Optional

from .modificacion import ConsolidadaHandler


class QueueClient:
    def __init__(self):
        self.user = os.environ["RABBIT_USER"]
        self.password = os.environ["RABBIT_PASS"]
        self.host = os.environ["RABBIT_HOST"]
        self.queue_modificaciones = os.environ["RABBIT_QUEUE_MODIFICACIONES"]
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=self.credentials)
        )
        self.channel = self.connection.channel()

    def callback(self, ch, method, properties, body):
        data = body.decode("utf-8")
        message = json.loads(data)
        ConsolidadaHandler().handle(message)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_listening(self):
        self.channel.queue_declare(queue=self.queue_modificaciones, durable=True)
        self.channel.basic_consume(
            queue=self.queue_modificaciones,
            on_message_callback=self.callback,
            auto_ack=False,
        )
        logger.info(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def handle_error(self, e: Exception | BaseException) -> None:
        logger.exception(f"Error: {e}", traceback=True)
        self.connection.close()
        raise e
