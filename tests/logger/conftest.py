import json
import logging

import pytest


@pytest.fixture()
def mock_log_record(mocker):
    return mocker.MagicMock(spec=logging.LogRecord)
