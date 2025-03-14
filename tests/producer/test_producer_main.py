from unittest.mock import MagicMock, patch

import pytest

from common.config import Config
from producer.main import main, run_loop, send_message


@pytest.mark.parametrize(
    "msg_limit, min_sleep, max_sleep, expected_iterations",
    [
        (10, 0, 1, 10),
        (1, 1, 1, 1),
        (None, 3, 5, 5)  # Mock inifinite loop
    ]
)
@patch("producer.main.send_message")
@patch("producer.main.random_sleep")
def test_run_loop(
    mock_send_message,
    mock_random_sleep,
    msg_limit,
    min_sleep,
    max_sleep,
    expected_iterations
):
    mock_channel = MagicMock()
    if msg_limit is None:
        mock_send_message.side_effect = [None, None, None, None, Exception]

    run_loop(
        msg_limit=msg_limit,
        channel=mock_channel,
        queue_name="test",
        min_sleep=min_sleep,
        max_sleep=max_sleep
    )

    assert mock_send_message.call_count == expected_iterations
    assert mock_random_sleep.call_count == expected_iterations


@patch("producer.main.send_message")
@patch("producer.main.random_sleep")
@patch("producer.main.logger")
def test_run_loop_keyboard_interrupt(
    mock_logger,
    mock_send_message,
    mock_random_sleep,
):
    mock_logger.error = MagicMock()
    mock_send_message.side_effect = [None, KeyboardInterrupt]
    mock_channel = MagicMock()

    run_loop(
        msg_limit=5,
        channel=mock_channel,
        queue_name="test",
        min_sleep=5,
        max_sleep=5
    )

    mock_logger.error.assert_called_once_with("KeyboardInterrupt")


@patch("producer.main.send_message")
@patch("producer.main.random_sleep")
@patch("producer.main.logger")
def test_run_loop_exception(
    mock_logger,
    mock_send_message,
    mock_random_sleep,
):
    mock_logger.error = MagicMock()
    mock_send_message.side_effect = [None, Exception]
    mock_channel = MagicMock()

    run_loop(
        msg_limit=5,
        channel=mock_channel,
        queue_name="test",
        min_sleep=5,
        max_sleep=5
    )

    mock_logger.error.assert_called_once()


@patch("producer.main.uuid4")
def test_send_message(mock_uuid):
    mock_uuid.return_value.hex = "test_message"
    mock_channel = MagicMock()
    mock_channel.basic_publish = MagicMock()
    queue_name = "test"

    send_message(channel=mock_channel, queue_name=queue_name)

    mock_uuid.assert_called_once()
    mock_channel.basic_publish.assert_called_once_with(
        exchange="",
        routing_key="test",
        body="test_message"
    )


@patch("producer.main.logger")
@patch("producer.main.get_connection")
@patch("producer.main.run_loop")
@patch.object(Config, "read")
def test_main(
    mock_config_read,
    mock_run_loop,
    mock_get_connection,
    mock_logger
):
    mock_config = MagicMock()
    mock_config.RABBITMQ_HOST = "host"
    mock_config.QUEUE_NAME = "queue"
    mock_config.MSG_LIMIT = 10
    mock_config.MIN_SLEEP = 1
    mock_config.MAX_SLEEP = 5
    mock_config_read.return_value = mock_config

    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_get_connection.return_value = (mock_connection, mock_channel)

    main()

    mock_logger.info.assert_any_call("Producer starts...")
    mock_logger.info.assert_any_call("Producer ends.")

    mock_config_read.assert_called_once()

    mock_get_connection.assert_called_once_with(
        "host",
        "queue"
    )

    mock_run_loop.assert_called_once_with(
        msg_limit=10,
        channel=mock_channel,
        queue_name="queue",
        min_sleep=1,
        max_sleep=5
    )

    mock_connection.close.assert_called_once()
