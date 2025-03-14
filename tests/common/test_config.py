import os
from unittest.mock import patch

import pytest

from common.config import Config


@pytest.fixture
def config_values():
    return [
        {
            "name": "RABBITMQ_HOST",
            "type": str,
            "required": True,
            "default": None
        },
        {
            "name": "MSG_LIMIT",
            "type": int,
            "required": False,
            "default": None
        },
        {
            "name": "MIN_SLEEP",
            "type": int,
            "required": False,
            "default": 0
        }
    ]


@patch.dict(
    os.environ,
    {
        "RABBITMQ_HOST": "localhost",
        "MSG_LIMIT": "10",
        "MIN_SLEEP": "1"
    }
)
def test_read_success(config_values):
    config = Config(config_values).read()

    assert config.RABBITMQ_HOST == "localhost"
    assert config.MSG_LIMIT == 10
    assert config.MIN_SLEEP == 1


@patch.dict(os.environ, {"RABBITMQ_HOST": "localhost"}, clear=True)
def test_default_values_used(config_values):
    config = Config(config_values).read()

    assert config.RABBITMQ_HOST == "localhost"
    assert config.MSG_LIMIT is None
    assert config.MIN_SLEEP == 0


@patch.dict(os.environ, {}, clear=True)
@patch("common.config.sys.exit")
def test_missing_env(mock_exit, config_values):
    Config(config_values).read()
    mock_exit.assert_called_once_with(1)


@patch.dict(
    os.environ,
    {
        "RABBITMQ_HOST": "localhost",
        "MSG_LIMIT": "abc"
    },
    clear=True
)
@patch("common.config.sys.exit")
def test_invalid_env(mock_exit, config_values):
    Config(config_values).read()
    mock_exit.assert_called_once_with(1)
