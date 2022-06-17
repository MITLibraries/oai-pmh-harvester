import os

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def test_env():
    os.environ = {"WORKSPACE": "test"}
    yield


@pytest.fixture
def cli_runner():
    runner = CliRunner()
    return runner
