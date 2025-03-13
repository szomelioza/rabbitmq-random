from unittest.mock import MagicMock, patch

import pika
import pytest

from common.utils import get_connection, random_sleep


@patch("common.utils.pika.BlockingConnection")
def test_get_connection_success(mock_connection):
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel

    connection, channel = get_connection("host", "queue")

    mock_connection.assert_called_once_with(pika.ConnectionParameters("host"))
    channel.queue_declare.assert_called_once_with(queue="queue")

    assert connection == mock_connection.return_value
    assert channel == mock_channel


@patch(
    "common.utils.pika.BlockingConnection",
    side_effect=pika.exceptions.AMQPConnectionError
)
@patch("common.utils.time.sleep")
def test_get_connection_fail(mock_sleep, mock_connection):

    with pytest.raises(Exception, match="Unable to connect to RabbitMQ!"):
        get_connection("host", "queue")

    assert mock_connection.call_count == 10
    assert mock_sleep.call_count == 10


@patch("common.utils.time.sleep")
@patch("common.utils.randint", return_value=2)
def test_random_sleep(mock_randint, mock_sleep):
    random_sleep(0, 2)
    mock_randint.assert_called_once_with(0, 2)
    mock_sleep.assert_called_once_with(2)
