import logging

import pytest

from harvester.config import Config


def test_configure_logger_defaults_to_root_logger():
    config = Config(logger=None)
    assert config.logger.name == "root"


def test_configure_logger_accepts_specific_logger():
    logger = logging.getLogger(__name__)
    config = Config(logger=logger)
    assert config.logger.name == "tests.test_config"


def test_configure_logger_not_verbose(config):
    result = config.configure_logger(verbose=False)
    assert config.logger.getEffectiveLevel() == int(logging.INFO)
    assert result == "Logger 'root' configured with level=INFO"


def test_configure_logger_verbose(config):
    result = config.configure_logger(verbose=True)
    assert config.logger.getEffectiveLevel() == int(logging.DEBUG)
    assert result == "Logger 'root' configured with level=DEBUG"


def test_configure_sentry_no_env_variable(config, monkeypatch):
    config.configure_logger(verbose=False)
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    result = config.configure_sentry()
    assert result == "No Sentry DSN found, exceptions will not be sent to Sentry"


def test_configure_sentry_env_variable_is_none(config, monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "None")
    result = config.configure_sentry()
    assert result == "No Sentry DSN found, exceptions will not be sent to Sentry"


def test_configure_sentry_env_variable_is_dsn(config, monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    result = config.configure_sentry()
    assert result == "Sentry DSN found, exceptions will be sent to Sentry with env=test"


def test_config_check_required_env_vars_success(config):
    config.check_required_env_vars()


def test_config_env_var_access_success(config):
    assert config.STATUS_UPDATE_INTERVAL == "1000"


def test_config_env_var_access_error(config):
    with pytest.raises(
        AttributeError, match="'DOES_NOT_EXIST' not a valid configuration variable"
    ):
        _ = config.DOES_NOT_EXIST
