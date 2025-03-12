import functools
import sys

import pika

from common.config import Config
from common.exceptions import InalidEnvVar, RequiredEnvVarNotSet
from common.logger import get_logger
from common.utils import get_connection, random_sleep
from consumer.constants import CONFIG_VALUES

logger = get_logger()


def callback(
    channel: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes,
    min_sleep: int,
    max_sleep: int
) -> None:
    """Sleep and send ack once message is received

    Args:
        channel (pika.channel.Channel): Channel of received message
        method (pika.spec.Basic.Deliver): Message metadata
        properties: (pika.spec.BasicProperties): Message properties
        body (bytes): Message
        min_sleep (int): Minimum time to sleep
        max_sleep (int): Maximum time to sleep
    """
    logger.info(f"Received {body.decode()}")
    random_sleep(min_sleep, max_sleep)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    """Run program loop to receive messages

    Read env vars, establish connection to RabbitMQ and
    listen for messages in queue.

    Returns:
        None
    """
    logger.info("Consumer starts...")
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
        channel.basic_consume(
            queue=config.QUEUE_NAME,
            on_message_callback=functools.partial(
                callback,
                min_sleep=config.MIN_SLEEP,
                max_sleep=config.MAX_SLEEP
            ),
            auto_ack=False
        )
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)
    finally:
        connection.close()
        logger.info("Consumer ends.")


if __name__ == "__main__":
    main()
