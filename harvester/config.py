# ruff: noqa: FBT001

"""harvester.config module."""
import logging
import os
from typing import Any

import sentry_sdk

DEFAULT_RETRY_AFTER = 30
MAX_RETRIES = 10
RETRY_STATUS_CODES = [429, 500, 503]
MAX_ALLOWED_ERRORS = 10


class Config:
    REQUIRED_ENV_VARS = ("WORKSPACE",)
    OPTIONAL_ENV_VARS = ("RECORD_SKIP_LIST", "SENTRY_DSN", "STATUS_UPDATE_INTERVAL")

    def __init__(self, logger: logging.Logger | None = None):
        """Set root logger as default when creating class instance."""
        if logger is None:
            self.logger = logging.getLogger()
        else:
            self.logger = logger

    def check_required_env_vars(self) -> None:
        """Method to raise exception if required env vars not set."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            message = f"Missing required environment variables: {', '.join(missing_vars)}"
            raise OSError(message)

    def configure_logger(self, verbose: bool) -> str:
        for handler in logging.root.handlers:
            handler.filters.clear()
        if verbose:
            logging.basicConfig(
                format="%(asctime)s %(levelname)s %(name)s.%(funcName)s() "
                "line %(lineno)d: %(message)s"
            )
            self.logger.setLevel(logging.DEBUG)
            for handler in logging.root.handlers:
                handler.addFilter(logging.Filter("harvester"))
        else:
            logging.basicConfig(
                format=("%(asctime)s %(levelname)s %(name)s.%(funcName)s(): %(message)s")
            )
            self.logger.setLevel(logging.INFO)
        return (
            f"Logger '{self.logger.name}' configured with level="
            f"{logging.getLevelName(self.logger.getEffectiveLevel())}"
        )

    def configure_sentry(self) -> str:
        sentry_dsn = self.SENTRY_DSN
        if sentry_dsn and sentry_dsn.lower() != "none":
            sentry_sdk.init(sentry_dsn, environment=self.WORKSPACE)
            return (
                "Sentry DSN found, exceptions will be sent to Sentry with env="
                f"{self.WORKSPACE}"
            )
        return "No Sentry DSN found, exceptions will not be sent to Sentry"

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Provide dot notation access to configurations and env vars on this class."""
        if name in self.REQUIRED_ENV_VARS or name in self.OPTIONAL_ENV_VARS:
            if name == "STATUS_UPDATE_INTERVAL":
                return os.getenv(name, "1000")
            return os.getenv(name)
        message = f"'{name}' not a valid configuration variable"
        raise AttributeError(message)
