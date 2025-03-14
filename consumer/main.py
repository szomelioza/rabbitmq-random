import functools

import pika

from common.config import Config
from common.logger import get_logger
from common.utils import get_connection, random_sleep
from consumer.constants import CONFIG_VALUES

logger = get_logger()


def run_loop(
    channel: pika.channel.Channel,
    queue_name: str,
    min_sleep: int,
    max_sleep: int
):
    """Run program loop to listen and print messages
    from the queue

    Args:
        channel (pika.channel.Channel): Channel used to receive messages
        queue_name (str): Name of the queue
        min_sleep (int): Minimum time to sleep
        max_sleep (int): Maximum time to sleep
    """
    try:
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=functools.partial(
                callback,
                min_sleep=min_sleep,
                max_sleep=max_sleep
            ),
            auto_ack=False
        )
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
    except Exception as e:
        logger.error(e)


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

    config = Config(CONFIG_VALUES).read()
    connection, channel = get_connection(
        config.RABBITMQ_HOST,
        config.QUEUE_NAME
    )

    run_loop(
        channel=channel,
        queue_name=config.QUEUE_NAME,
        min_sleep=config.MIN_SLEEP,
        max_sleep=config.MAX_SLEEP
    )

    connection.close()
    logger.info("Consumer ends.")


if __name__ == "__main__":
    main()
