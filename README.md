# rabbitmq-random

![](https://github.com/szomelioza/rabbitmq-random/actions/workflows/build-producer.yml/badge.svg)
![](https://github.com/szomelioza/rabbitmq-random/actions/workflows/build-consumer.yml/badge.svg)

A simple RabbitMQ producer/consumer setup for testing queue behavior.

- The **producer** sends messages at random intervals.
- The **consumer** processes messages and sleeps for a random duration.

Designed for experimenting with queue saturation and message flow in RabbitMQ.

## Usage
The Producer and Consumer are available as Docker images and can be run using the following commands:
```sh
docker run -e RABBITMQ_HOST=rabbitmq -e QUEUE_NAME=my_queue ghcr.io/szomelioza/rabbitmq-random-producer:latest
docker run -e RABBITMQ_HOST=rabbitmq -e QUEUE_NAME=my_queue ghcr.io/szomelioza/rabbitmq-random-consumer:latest
```
For a Docker Compose example, see [docker-compose.yml](docker-compose.yml).

## Environment Variables
### Producer
| Name | Description | Type | Default |
| ---- | ----------- | ---- | ------- |
| RABBITMQ_HOST | RabbitMQ server address | Required | N/A |
| QUEUE_NAME | Name of the queue to send messages to | Required | N/A |
| MSG_LIMIT | Number of messages to send | Optional | None (inifinity) |
| MIN_SLEEP | Minimum delay (in seconds) between messages | Optional | 0 |
| MAX_SLEEP | Maximum delay (in seconds) between messages | Optional | 3 |
### Consumer
| Name | Description | Type | Default |
| ---- | ----------- | ---- | ------- |
| RABBITMQ_HOST | RabbitMQ server address | Required | N/A |
| QUEUE_NAME | Name of the queue to receive messages from | Required | N/A |
| MIN_SLEEP | Minimum delay (in seconds) before acknowledging a message | Optional | 3 |
| MAX_SLEEP | Maximum delay (in seconds) before acknowledging a message | Optional | 5 |
