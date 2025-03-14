import sys
import time
from random import randint

import pika

from common.logger import get_logger

logger = get_logger()


def get_connection(rabbitmq_host: str, queue_name: str) -> tuple[
    pika.BlockingConnection,
    pika.channel.Channel
]:
    """Get RabbitMQ connection and channel

    Function will exit if connection cannot be established
    after retries.

    Args:
        rabbitmq_host (str): RabbitMQ host
        queue_name (str): Name of the queue

    Returns:
        tuple: RabbitMQ connection (pika.BlockingConnection) and
        RabbitMQ channel (pika.channel.Channel) where messages
        will be sent/received
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
            logger.warning(f"RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    logger.error("Unable to connect to RabbitMQ!")
    sys.exit(1)


def random_sleep(min: int, max: int) -> None:
    """Sleep for random time based on min and max provided

    Args:
        min (int): Minimum sleep time
        max (int): Maximum sleep time

    Returns:
        None
    """
    time.sleep(randint(min, max))
