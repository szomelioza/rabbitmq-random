import os

import pika

RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
QUEUE_NAME = os.getenv("QUEUE_NAME")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBIT_MQ_HOST)
)
channel = connection.channel()

_, _, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=True)

if body:
    print(f" [x] Received {body}")
else:
    print("Queue empty!")
connection.close()
