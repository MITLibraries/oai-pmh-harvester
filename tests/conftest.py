from unittest.mock import patch

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    monkeypatch.setenv("WORKSPACE", "test")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_sentry_capture_message():
    with patch("harvester.utils.sentry_sdk.capture_message") as mock_capture:
        mock_capture.return_value = "message-sent-ok"
        yield mock_capture
