from services.modificacion_service.queue_client import QueueClient

if __name__ == "__main__":
    queue_client = QueueClient()
    try:
        queue_client.start_listening()
    except Exception as e:
        queue_client.handle_error(e)
