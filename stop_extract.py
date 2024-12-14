import argparse
import json
import pika
from typing import Any, Dict
from loguru import logger
from time import sleep

from services.traspaso_service.queue_client import QueueClient


def move_messages(queue_client: QueueClient, status: str, max_messages: int):
    connection = queue_client._get_connection()
    processed_messages = 0
    source_queue, target_queue = (
        (queue_client.queue_pendientes, queue_client.queue_pausa)
        if status == "stop"
        else (queue_client.queue_pausa, queue_client.queue_pendientes)
    )
    try:
        channel = connection.channel()
        channel.queue_declare(queue=source_queue, durable=True)
        channel.queue_declare(queue=target_queue, durable=True)
        while processed_messages < max_messages:
            method_frame, _, body = channel.basic_get(source_queue)
            if method_frame is None:
                break
            data = body.decode("utf-8")
            message = json.loads(data)
            queue_client.enqueue_to_specific_queue(target_queue, json.dumps(message))
            logger.info(f"Message {message['owner']} moved to {target_queue}")
            channel.basic_ack(method_frame.delivery_tag)
            processed_messages += 1
        logger.info("All messages processed.")
    finally:
        connection.close()


if __name__ == "__main__":
    MAX = 1000
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--status",
        required=True,
        choices=["stop", "resume"],
        help="Whether to stop or resume the processing of messages.",
    )
    args = parser.parse_args()

    queue_client = QueueClient()
    if args.status == "stop":
        while True:
            move_messages(queue_client, args.status, MAX)
            print("Waiting 10 seconds...")
            sleep(10)
    else:
        move_messages(queue_client, args.status, MAX)
