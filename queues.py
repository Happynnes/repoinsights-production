import argparse
import pika
import os
import json
from typing import Dict, Any, Union, Optional
from loguru import logger

"""
{
    "owner": "mavam", 
    "repo": "stat-cookbook", 
    "since": "May 18, 2013, 12:00 AM", 
    "until": "June 17, 2013, 12:00 AM", 
    "data_types": ["commits", "pull_requests", "issues", "labels", "milestones"]
}
"""


class QueueClient:
    def __init__(self):
        self.user = os.environ["RABBIT_USER"]
        self.password = os.environ["RABBIT_PASS"]
        self.host = os.environ["RABBIT_HOST"]
        self.queue_curado = os.environ["RABBIT_QUEUE_CURADO"]
        self.queue_pendientes = os.environ["RABBIT_QUEUE_PENDIENTES"]
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, credentials=self.credentials)
        )
        self.channel = self.connection.channel()

    def get_from_queue(self, queue_name: str) -> Union[Dict[str, Any], None]:
        if queue_name == "curado":
            queue = self.queue_curado
        elif queue_name == "pendientes":
            queue = self.queue_pendientes
        else:
            raise ValueError(f"Queue {queue_name} not found")

        # get message but dont delete it from queue
        method_frame, _, body = self.channel.basic_get(queue, auto_ack=False)
        if method_frame:
            data = body.decode("utf-8")
            return json.loads(data)
        else:
            return None

    def enqueue(self, project: str):
        self.channel.queue_declare(queue=self.queue_curado, durable=True)
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_curado,
            body=project,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )
        logger.info(f"Project {project} published")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True, help="Name of the queue")
    args = parser.parse_args()

    if args.name:
        queue_client = QueueClient()
        message = queue_client.get_from_queue(args.name)
        if message is not None:
            logger.info(f"Message received from {args.name}: {message}")
        else:
            logger.info(f"No message found in {args.name} queue")


if __name__ == "__main__":
    main()
