import logging
import os
import sys
import time
from random import randint

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
MIN_SLEEP = int(os.getenv("MINSLEEP", "3"))
MAX_SLEEP = int(os.getenv("MAX_SLEEP", "5"))


def get_connection() -> tuple[
    pika.BlockingConnection,
    pika.channel.Channel
]:
    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(RABBITMQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_qos(prefetch_count=1)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            logger.warning(f"WARNING: RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ!")


def random_sleep() -> None:
    time.sleep(randint(MIN_SLEEP, MAX_SLEEP))


def callback(
    ch: pika.channel.Channel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes
) -> None:
    logger.info(f" Received {body.decode()}")
    random_sleep()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    logger.info("Consumer starts...")
    try:
        connection, channel = get_connection()
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
