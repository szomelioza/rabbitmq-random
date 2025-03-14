import itertools
from uuid import uuid4

import pika

from common.config import Config
from common.logger import get_logger
from common.utils import get_connection, random_sleep
from producer.constants import CONFIG_VALUES

logger = get_logger()


def run_loop(
    msg_limit: int | None,
    channel: pika.channel.Channel,
    queue_name: str,
    min_sleep: int,
    max_sleep: int
):
    """Run program loop to send messages to queue

    Args:
        msg_limit (str | None): Limit of messages to send
        channel (pika.channel.Channel): Channel used to send messages
        queue_name (str): Name of the queue
        min_sleep (int): Minimum time to sleep
        max_sleep (int): Maximum time to sleep
    """
    try:
        for _ in itertools.islice(itertools.count(), msg_limit):
            send_message(channel, queue_name)
            random_sleep(min_sleep, max_sleep)
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)


def send_message(
    channel: pika.channel.Channel,
    queue_name: str
) -> None:
    """Send message to the channel

    Args:
        channel (pika.channel.Channel): Channel used to send messages
        queue_name (str): Name of the queue to use

    Returns:
        None
    """
    msg = uuid4().hex
    channel.basic_publish(exchange="", routing_key=queue_name, body=msg)
    logger.info(f"Sent {msg}")


def main() -> None:
    """Run program loop to send messages

    Read env vars, establish connection to RabbitMQ and
    run loop until there are messages to send.

    Returns:
        None
    """
    logger.info("Producer starts...")

    config = Config(CONFIG_VALUES).read()
    connection, channel = get_connection(
        config.RABBITMQ_HOST,
        config.QUEUE_NAME
    )

    run_loop(
        msg_limit=config.MSG_LIMIT,
        channel=channel,
        queue_name=config.QUEUE_NAME,
        min_sleep=config.MIN_SLEEP,
        max_sleep=config.MAX_SLEEP
    )

    connection.close()
    logger.info("Producer ends.")


if __name__ == "__main__":
    main()
