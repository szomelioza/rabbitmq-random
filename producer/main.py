import itertools
import sys
from uuid import uuid4

import pika

from common.config import Config
from common.exceptions import InalidEnvVar, RequiredEnvVarNotSet
from common.logger import get_logger
from common.utils import get_connection, random_sleep
from producer.constants import CONFIG_VALUES

logger = get_logger()


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
    try:
        config = Config(CONFIG_VALUES).read()
    except RequiredEnvVarNotSet as e:
        logger.error(f"Required env var not set: {e}")
        sys.exit(1)
    except InalidEnvVar as e:
        logger.error(f"Invalid value for variable: {e}")
        sys.exit(1)

    try:
        connection, channel = get_connection(
            config.RABBITMQ_HOST,
            config.QUEUE_NAME
        )
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    try:
        for _ in itertools.islice(itertools.count(), config.MSG_LIMIT):
            send_message(channel, config.QUEUE_NAME)
            random_sleep(config.MIN_SLEEP, config.MAX_SLEEP)
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)
    finally:
        connection.close()
        logger.info("Producer ends.")


if __name__ == "__main__":
    main()
