import logging
import time
from random import randint

import pika

logger = logging.getLogger(__name__)


def get_connection(rabbitmq_host: str, queue_name: str) -> tuple[
    pika.BlockingConnection,
    pika.channel.Channel
]:
    """Get RabbitMQ connection and channel

    Args:
        rabbitmq_host (str): RabbitMQ host
        queue_name (str): Name of the queue

    Returns:
        tuple: RabbitMQ connection (pika.BlockingConnection) and
        RabbitMQ channel (pika.channel.Channel) where messages will be sent to

    Raises:
        Exception: If after retries it's still
        not possible to establish connection
    """
    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(rabbitmq_host)
            )
            channel = connection.channel()
            channel.queue_declare(queue=queue_name)
            logger.info("Connected to RabbitMQ")
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            logger.warning(f"WARNING: RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ!")


def random_sleep(min: int, max: int) -> None:
    """Sleep for random time based on min and max provided

    Args:
        min (int): Minimum sleep time
        max (int): Maximum sleep time

    Returns:
        None
    """
    time.sleep(randint(min, max))
