import argparse
import json
from typing import Any, Dict
from loguru import logger

from services.traspaso_service.queue_client import QueueClient


def transfer_messages(queue_client: QueueClient, type: Any, max_messages: int):
    connection = queue_client._get_connection()
    processed_messages = 0
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_client.queue_failed, durable=True)
        while processed_messages < max_messages:
            method_frame, _, body = channel.basic_get(queue_client.queue_failed)
            if method_frame is None:
                break
            data = body.decode("utf-8")
            message = json.loads(data)
            if should_transfer_message(type, message):
                transfer_message(queue_client, type, message)
                logger.info(f"Message {message['owner']} transferred")
            else:
                queue_client.enqueue_failed(json.dumps(message))
                logger.info(
                    f"Message {message['owner']} put back in queue {queue_client.queue_failed}"
                )
            channel.basic_ack(method_frame.delivery_tag)
            processed_messages += 1
        logger.info("All messages processed.")
    finally:
        connection.close()


def should_transfer_message(type: str, message: Dict[str, Any]) -> bool:
    if (type == "traspaso" and message.get("status", {}).get("type") == "traspaso") or (
        type == "extract" and message.get("status", {}).get("type") == "extract"
    ):
        return True
    return False


def reset_attempts(message: Dict[str, Any]) -> Dict[str, Any]:
    message["attempt"] = 0
    return message


def transfer_message(queue_client: QueueClient, type, message):
    message = reset_attempts(message)
    if type == "traspaso":
        queue_client.enqueue_curado(json.dumps(message))
    elif type == "extract":
        queue_client.enqueue_pendientes(json.dumps(message))


if __name__ == "__main__":
    MAX = 100
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        required=True,
        choices=["traspaso", "extract"],
        help="Type of messages to transfer.",
    )
    args = parser.parse_args()

    queue_client = QueueClient()
    transfer_messages(queue_client, args.type, MAX)
