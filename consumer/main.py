import logging
import os
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

RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
MIN_SLEEP = int(os.getenv("MINSLEEP", "3"))
MAX_SLEEP = int(os.getenv("MAX_SLEEP", "5"))


def get_connection():
    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(RABBIT_MQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_qos(prefetch_count=1)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            logger.warning(f"WARNING: RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    raise Exception("Unable to connect to RabbitMQ!")


def random_sleep():
    time.sleep(randint(MIN_SLEEP, MAX_SLEEP))


def callback(ch, method, properties, body):
    logger.info(f" Received {body.decode()}")
    random_sleep()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    logger.info("Consumer starts...")
    connection, channel = get_connection()

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
