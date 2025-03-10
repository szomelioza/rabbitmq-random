import itertools
import logging
import os
import sys
import time
from random import randint
from uuid import uuid4

import pika

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger("pika").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MSG_LIMIT = os.getenv("MSG_LIMIT")
MIN_SLEEP = int(os.getenv("MINSLEEP", "0"))
MAX_SLEEP = int(os.getenv("MAX_SLEEP", "3"))


def get_connection() -> tuple[
    pika.BlockingConnection,
    pika.channel.Channel
]:
    """Get RabbitMQ connection and channel

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
                pika.ConnectionParameters(RABBITMQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            logger.warning(f"WARNING: RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ!")


def get_msg_limit() -> int | None:
    """Get number of messages to send

    Returns:
        int | None: Number of messages to send
        or None for infinite amount
    """
    try:
        return int(MSG_LIMIT)
    except TypeError:
        return None


def send_message(
    channel: pika.channel.Channel
) -> None:
    """Send message to the channel

    Args:
        channel (pika.channel.Channel): Channel used to send messages

    Returns:
        None
    """
    msg = uuid4().hex
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=msg)
    logger.info(f"Sent {msg}")


def random_sleep() -> None:
    """Sleep for random time based on min and max provided

    Returns:
        None
    """
    time.sleep(randint(MIN_SLEEP, MAX_SLEEP))


def main() -> None:
    """Run program loop to send messages

    Establish connection to RabbitMQ and run loop until there
    are messages to send.

    Returns:
        None
    """
    logger.info("Producer starts...")
    try:
        connection, channel = get_connection()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    try:
        msg_limit = get_msg_limit()
        for _ in itertools.islice(itertools.count(), msg_limit):
            send_message(channel)
            random_sleep()
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)
    finally:
        connection.close()
        logger.info("Producer ends.")


if __name__ == "__main__":
    main()
