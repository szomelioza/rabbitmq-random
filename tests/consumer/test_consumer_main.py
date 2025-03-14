import functools
from unittest.mock import MagicMock, patch

import pytest

from common.config import Config
from consumer.main import callback, main, run_loop


@pytest.fixture
def mock_channel():
    channel = MagicMock()
    channel.basic_consume = MagicMock()
    channel.start_consuming = MagicMock()
    return channel


def test_run_loop(mock_channel):

    run_loop(
        channel=mock_channel,
        queue_name="test",
        min_sleep=0,
        max_sleep=1
    )

    _, consume_kwargs = mock_channel.basic_consume.call_args
    assert consume_kwargs["queue"] == "test"
    assert isinstance(consume_kwargs["on_message_callback"], functools.partial)
    assert consume_kwargs["on_message_callback"].func == callback
    assert consume_kwargs["on_message_callback"].keywords == {
        "min_sleep": 0,
        "max_sleep": 1
    }
    assert not consume_kwargs["auto_ack"]
    mock_channel.start_consuming.assert_called_once()


@patch("consumer.main.logger")
def test_run_loop_keyboard_exception(mock_logger, mock_channel):
    mock_channel.basic_consume.side_effect = [KeyboardInterrupt]

    run_loop(
        channel=mock_channel,
        queue_name="test",
        min_sleep=0,
        max_sleep=1
    )

    mock_logger.error.assert_called_once_with("KeyboardInterrupt")


@patch("consumer.main.logger")
def test_run_loop_exception(mock_logger, mock_channel):
    mock_channel.basic_consume.side_effect = [Exception]

    run_loop(
        channel=mock_channel,
        queue_name="test",
        min_sleep=0,
        max_sleep=1
    )

    mock_logger.error.assert_called_once()


@patch("consumer.main.random_sleep")
@patch("consumer.main.logger")
def test_callback(mock_logger, mock_random_sleep, mock_channel):

    mock_method = MagicMock()
    mock_method.delivery_tag = 123

    callback(
        channel=mock_channel,
        method=mock_method,
        properties=None,
        body="test_message".encode(),
        min_sleep=0,
        max_sleep=1
    )

    mock_logger.info.assert_called_once_with(
        "Received test_message"
    )
    mock_random_sleep.assert_called_once_with(0, 1)
    mock_channel.basic_ack.assert_called_once_with(
        delivery_tag=123
    )


@patch("consumer.main.logger")
@patch("consumer.main.get_connection")
@patch("consumer.main.run_loop")
@patch.object(Config, "read")
def test_main(
    mock_config_read,
    mock_run_loop,
    mock_get_connection,
    mock_logger
):
    mock_config = MagicMock()
    mock_config.QUEUE_NAME = "queue"
    mock_config.MIN_SLEEP = 1
    mock_config.RABBITMQ_HOST = "host"
    mock_config.MAX_SLEEP = 5
    mock_config_read.return_value = mock_config
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_get_connection.return_value = (mock_connection, mock_channel)

    main()

    mock_logger.info.assert_any_call("Consumer starts...")
    mock_logger.info.assert_any_call("Consumer ends.")
    mock_config_read.assert_called_once()
    mock_get_connection.assert_called_once_with(
        "host",
        "queue"
    )
    mock_run_loop.assert_called_once_with(
        channel=mock_channel,
        queue_name="queue",
        min_sleep=1,
        max_sleep=5
    )
    mock_connection.close.assert_called_once()
