import json
import json as json_module
import threading

import pytest
from pycpg.sdk import SDKClient
from requests import HTTPError
from requests import Response
from tests.conftest import convert_str_to_date
from tests.conftest import create_mock_response

from crashplancli.logger import CliLogger


@pytest.fixture
def sdk(mocker):
    return mocker.MagicMock(spec=SDKClient)


@pytest.fixture
def mock_42(mocker):
    return mocker.patch("pycpg.sdk.from_local_account")


@pytest.fixture
def logger(mocker):
    mock = mocker.MagicMock()
    return mock


@pytest.fixture
def cli_logger(mocker):
    mock = mocker.MagicMock(spec=CliLogger)
    return mock


@pytest.fixture
def cli_state_with_user(sdk_with_user, cli_state):
    cli_state.sdk = sdk_with_user
    return cli_state


@pytest.fixture
def cli_state_without_user(sdk_without_user, cli_state):
    cli_state.sdk = sdk_without_user
    return cli_state


@pytest.fixture
def custom_error(mocker):
    err = mocker.MagicMock(spec=HTTPError)
    resp = mocker.MagicMock(spec=Response)
    resp.text = "TEST_ERR"
    err.response = resp
    return err


def get_filter_value_from_json(json, filter_index):
    return json_module.loads(str(json))["filters"][filter_index]["value"]


def filter_term_is_in_call_args(filter_group, term):
    for f in filter_group:
        if term in str(f):
            return True
    return False


def parse_date_from_filter_value(json, filter_index):
    date_str = get_filter_value_from_json(json, filter_index)
    return convert_str_to_date(date_str)


def thread_safe_side_effect():
    def f(*args):
        with threading.Lock():
            f.call_count += 1
            f.call_args_list.append(args)

    f.call_count = 0
    f.call_args_list = []
    return f


def get_generator_for_get_all(mocker, mock_return_items):
    if not mock_return_items:
        mock_return_items = []
    elif not isinstance(mock_return_items, dict):
        mock_return_items = [json.loads(mock_return_items)]

    def gen(*args, **kwargs):
        yield create_mock_response(mocker, data={"items": mock_return_items})

    return gen


def get_mark_for_search_and_send_to(command_group):
    search_cmd = [command_group, "search"]
    send_to_cmd = [command_group, "send-to", "0.0.0.0"]
    return pytest.mark.parametrize("command", (search_cmd, send_to_cmd))
