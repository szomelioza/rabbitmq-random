import os

import pika

RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBIT_MQ_HOST)
)
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)

msg = "Test message"

channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=msg)
print(f" [x] Sent {msg}")

connection.close()
