import json
from datetime import datetime
from datetime import timedelta

import pytest
from click.testing import CliRunner
from pycpg.response import PycpgResponse
from pycpg.sdk import SDKClient
from requests import HTTPError
from requests import Response

import crashplancli.errors as error_tracker
from crashplancli.config import ConfigAccessor
from crashplancli.options import CLIState
from crashplancli.profile import crashplanProfile

TEST_ID = "TEST_ID"


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def io_prevention(monkeypatch):
    monkeypatch.setattr("logging.FileHandler._open", lambda *args, **kwargs: None)


def create_profile_values_dict(
    authority=None,
    username=None,
    ignore_ssl=False,
    api_client_auth="False",
):
    return {
        ConfigAccessor.AUTHORITY_KEY: "example.com",
        ConfigAccessor.USERNAME_KEY: "foo",
        ConfigAccessor.IGNORE_SSL_ERRORS_KEY: "True",
        ConfigAccessor.API_CLIENT_AUTH_KEY: "False",
    }


@pytest.fixture
def sdk(mocker):
    return mocker.MagicMock(spec=SDKClient)


@pytest.fixture
def sdk_with_user(sdk):
    sdk.users.get_by_username.return_value = {"users": [{"userUid": TEST_ID}]}
    return sdk


@pytest.fixture
def sdk_without_user(sdk):
    sdk.users.get_by_username.return_value = {"users": []}
    return sdk


@pytest.fixture
def mock_42(mocker):
    return mocker.patch("pycpg.sdk.from_local_account")


@pytest.fixture
def cli_state(mocker, sdk, profile):
    mock_state = mocker.MagicMock(spec=CLIState)
    mock_state._sdk = sdk
    mock_state.profile = profile
    mock_state.search_filters = []
    mock_state.totp = None
    mock_state.assume_yes = False
    return mock_state


class MockSection:
    def __init__(self, name=None, values_dict=None):
        self.name = name
        self.values_dict = values_dict or create_profile_values_dict()

    def __getitem__(self, item):
        return self.values_dict[item]

    def __setitem__(self, key, value):
        self.values_dict[key] = value

    def get(self, item):
        return self.values_dict.get(item)


def create_mock_profile(name="Test Profile Name"):
    profile_section = MockSection(name)
    profile = crashplanProfile(profile_section)
    return profile


def setup_mock_accessor(mock_accessor, name=None, values_dict=None):
    profile_section = MockSection(name, values_dict)
    mock_accessor.get_profile.return_value = profile_section
    return mock_accessor


@pytest.fixture
def profile(mocker):
    mock = mocker.MagicMock(spec=crashplanProfile)
    mock.name = "testcliprofile"
    return mock


@pytest.fixture(autouse=True)
def mock_makedirs(mocker):
    return mocker.patch("os.makedirs")


@pytest.fixture(autouse=True)
def mock_remove(mocker):
    return mocker.patch("os.remove")


@pytest.fixture(autouse=True)
def mock_listdir(mocker):
    return mocker.patch("os.listdir")


def func_keyword_args(
    one=None, two=None, three=None, default="testdefault", nargstest=None
):
    pass


def func_single_positional_arg(one):
    pass


def func_single_positional_arg_many_optional_args(one, two=None, three=None, four=None):
    pass


def func_positional_args(one, two, three):
    pass


def func_mixed_args(one, two, three=None, four=None):
    pass


def func_with_sdk(sdk, one, two, three=None, four=None):
    pass


def func_single_positional_arg_with_sdk_and_profile(
    sdk, profile, one, two=None, three=None, four=None
):
    pass


def func_with_args(args):
    pass


def convert_str_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_test_date(days_ago=None, hours_ago=None, minutes_ago=None):
    """Note: only pass in one parameter to get the right test date... this is just a test func."""
    now = datetime.utcnow()
    if days_ago:
        return now - timedelta(days=days_ago)
    if hours_ago:
        return now - timedelta(hours=hours_ago)
    if minutes_ago:
        return now - timedelta(minutes=minutes_ago)


def get_test_date_str(days_ago):
    return get_test_date(days_ago).strftime("%Y-%m-%d")


begin_date_str = get_test_date_str(days_ago=89)
begin_date_str_with_time = f"{begin_date_str} 3:12:33"
begin_date_str_with_t_time = f"{begin_date_str}T3:12:33"
end_date_str = get_test_date_str(days_ago=10)
end_date_str_with_time = f"{end_date_str} 11:22:43"
begin_date_str = get_test_date_str(days_ago=89)
begin_date_with_time = [get_test_date_str(days_ago=89), "3:12:33"]
end_date_str = get_test_date_str(days_ago=10)
end_date_with_time = [get_test_date_str(days_ago=10), "11:22:43"]


class ErrorTrackerTestHelper:
    def __enter__(self):
        error_tracker.ERRORED = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        error_tracker.ERRORED = False


TEST_FILE_PATH = "some/path"


@pytest.fixture
def mock_to_table(mocker):
    return mocker.patch("crashplancli.output_formats.to_table")


@pytest.fixture
def mock_to_csv(mocker):
    return mocker.patch("crashplancli.output_formats.to_csv")


@pytest.fixture
def mock_to_json(mocker):
    return mocker.patch("crashplancli.output_formats.to_json")


@pytest.fixture
def mock_to_formatted_json(mocker):
    return mocker.patch("crashplancli.output_formats.to_formatted_json")


@pytest.fixture
def mock_dataframe_to_json(mocker):
    return mocker.patch("pandas.DataFrame.to_json")


@pytest.fixture
def mock_dataframe_to_csv(mocker):
    return mocker.patch("pandas.DataFrame.to_csv")


@pytest.fixture
def mock_dataframe_to_string(mocker):
    return mocker.patch("pandas.DataFrame.to_string")


def create_mock_response(mocker, data=None, status=200):
    if isinstance(data, (dict, list)):
        data = json.dumps(data)
    elif not data:
        data = ""
    response = mocker.MagicMock(spec=Response)
    response.text = data
    response.status_code = status
    response.encoding = None
    response._content_consumed = ""
    return PycpgResponse(response)


def create_mock_http_error(mocker, data=None, status=400):
    mock_http_error = mocker.MagicMock(spec=HTTPError)
    mock_http_error.response = create_mock_response(mocker, data=data, status=status)
    return mock_http_error
