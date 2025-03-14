from __future__ import annotations

import os
import sys

from common.exceptions import InalidEnvVar, RequiredEnvVarNotSet
from common.logger import get_logger

logger = get_logger()


class Config:
    """App configuration read from env vars

    Args:
        config_values (list[dict]): Env vars to read
            Each dict element must contain:
            - `name` (str): Name of the env var
            - `type` (type): Type of the env var
            - `required` (bool): Whether env var must be declared
            - `default` (Any): Default value for the env var
    """

    def __init__(self, config_values: list[dict]):
        """Initialize config"""
        self._parsed_config = {}
        self.config_values = config_values

    def read(self) -> Config:
        """Read and parse env vars

        Function will exit if env vars are not correct.
        It can happen when required env var is missing or
        type of env var is invalid.

        Returns:
            Config: object with parsed env vars
        """
        try:
            for var in self.config_values:
                value = os.getenv(var["name"])

                if value is None:
                    if var["required"]:
                        raise RequiredEnvVarNotSet(var["name"])
                    self._parsed_config[var["name"]] = var["default"]
                else:
                    try:
                        self._parsed_config[var["name"]] = var["type"](value)
                    except ValueError:
                        raise InalidEnvVar(var["name"])
            return self
        except RequiredEnvVarNotSet as e:
            logger.error(f"Required env var not set: {e}")
        except InalidEnvVar as e:
            logger.error(f"Invalid value for variable: {e}")

        sys.exit(1)

    def __getattr__(self, var_name: str):
        """Return value of env var

        Args:
            var_name (str): Name of the var to return

        Returns:
            Any: Value of the set env var
        """
        return self._parsed_config[var_name]
