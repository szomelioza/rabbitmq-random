import os
import time
from random import randint

import pika

RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")


def get_connection():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBIT_MQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    return connection, channel


def random_sleep():
    time.sleep(randint(1, 10))


def callback(ch, method, properties, body):
    print(f" Received {body.decode()}")
    random_sleep()


def main():
    print("Consumer starts...")
    connection, channel = get_connection()

    try:
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=True
        )
        channel.start_consuming()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()
        print("Consumer ends.")


if __name__ == "__main__":
    main()
