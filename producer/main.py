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
    pika.adapters.blocking_connection.BlockingChannel
]:
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
    try:
        return int(MSG_LIMIT)
    except TypeError:
        return None


def send_message(
    channel: pika.adapters.blocking_connection.BlockingChannel
) -> None:
    msg = uuid4().hex
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=msg)
    logger.info(f"Sent {msg}")


def random_sleep() -> None:
    time.sleep(randint(MIN_SLEEP, MAX_SLEEP))


def main() -> None:
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
