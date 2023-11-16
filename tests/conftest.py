import os

import pytest
from click.testing import CliRunner
from unittest.mock import patch


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {"WORKSPACE": "test"}
    yield


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def mock_sentry_capture_message():
    with patch("harvester.utils.sentry_sdk.capture_message") as mock_capture:
        mock_capture.return_value = "message-sent-ok"
        yield mock_capture
