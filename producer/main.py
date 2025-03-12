import itertools
import os
import sys
from uuid import uuid4

import pika

from common.logger import get_logger
from common.utils import get_connection, random_sleep

logger = get_logger()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MSG_LIMIT = os.getenv("MSG_LIMIT")
MIN_SLEEP = int(os.getenv("MINSLEEP", "0"))
MAX_SLEEP = int(os.getenv("MAX_SLEEP", "3"))


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


def main() -> None:
    """Run program loop to send messages

    Establish connection to RabbitMQ and run loop until there
    are messages to send.

    Returns:
        None
    """
    logger.info("Producer starts...")
    try:
        connection, channel = get_connection(RABBITMQ_HOST, QUEUE_NAME)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    try:
        msg_limit = get_msg_limit()
        for _ in itertools.islice(itertools.count(), msg_limit):
            send_message(channel)
            random_sleep(MIN_SLEEP, MAX_SLEEP)
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)
    finally:
        connection.close()
        logger.info("Producer ends.")


if __name__ == "__main__":
    main()
