import os
import time
from random import randint
from uuid import uuid4

import pika
import pika.exceptions

RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")
SENT_MSG_LIMIT = int(os.getenv("SENT_MSG_LIMIT", "100"))


def get_connection():
    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(RABBIT_MQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print(f"WARNING: RabbitMQ unreachable. Retrying {i}")
            time.sleep(5)
    raise Exception("ERROR: Unable to connect to RabbitMQ!")


def send_message(channel):
    msg = uuid4().hex
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=msg)
    print(f" Sent {msg}")


def random_sleep():
    time.sleep(randint(1, 10))


def main():
    print("Producer starts...")
    connection, channel = get_connection()

    try:
        for _ in range(SENT_MSG_LIMIT):
            send_message(channel)
            random_sleep()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()
        print("Producer ends.")


if __name__ == "__main__":
    main()
