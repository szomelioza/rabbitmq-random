import logging
import os
import sys

import pika

from common.utils import get_connection, random_sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger("pika").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MIN_SLEEP = int(os.getenv("MINSLEEP", "3"))
MAX_SLEEP = int(os.getenv("MAX_SLEEP", "5"))


def callback(
    channel: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes
) -> None:
    """Sleep and send ack once message is received

    Args:
        channel (pika.channel.Channel): Channel of received message
        method (pika.spec.Basic.Deliver): Message metadata
        properties: (pika.spec.BasicProperties): Message properties
        body (bytes): Message
    """
    logger.info(f"Received {body.decode()}")
    random_sleep(MIN_SLEEP, MAX_SLEEP)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    """Run program loop to receive messages

    Establish connection to RabbitMQ and listen for message in queue.

    Returns:
        None
    """
    logger.info("Consumer starts...")
    try:
        connection, channel = get_connection(RABBITMQ_HOST, QUEUE_NAME)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    try:
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
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
