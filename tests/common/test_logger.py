import logging
from unittest.mock import MagicMock, patch

from common.logger import get_logger


@patch("common.logger.logging.basicConfig")
@patch("common.logger.logging.getLogger")
def test_get_logger(mock_get_logger, mock_basic_config):
    mock_logger = MagicMock(logging.Logger)
    mock_get_logger.return_value = mock_logger

    logger = get_logger()

    assert isinstance(logger, logging.Logger)

    mock_get_logger.assert_any_call("pika")
    mock_logger.setLevel.assert_called_once_with(logging.CRITICAL)
