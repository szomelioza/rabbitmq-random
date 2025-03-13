import os
from unittest.mock import patch

import pytest

from common.config import Config
from common.exceptions import InalidEnvVar, RequiredEnvVarNotSet


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
def test_missing_env(config_values):
    with pytest.raises(RequiredEnvVarNotSet, match="RABBITMQ_HOST"):
        Config(config_values).read()


@patch.dict(
    os.environ,
    {
        "RABBITMQ_HOST": "localhost",
        "MSG_LIMIT": "abc"
    },
    clear=True
)
def test_invalid_env(config_values):
    with pytest.raises(InalidEnvVar, match="MSG_LIMIT"):
        Config(config_values).read()
