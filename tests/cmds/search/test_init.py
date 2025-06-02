import pytest

from crashplancli.cmds.search import _try_get_logger_for_server
from crashplancli.errors import crashplancliError
from crashplancli.logger.enums import ServerProtocol


_TEST_ERROR_MESSAGE = "TEST ERROR MESSAGE"
_TEST_HOST = "example.com"
_TEST_CERTS = "./certs.pem"


@pytest.fixture
def patched_get_logger_method(mocker):
    return mocker.patch("crashplancli.cmds.search.get_logger_for_server")


@pytest.fixture
def errored_logger(patched_get_logger_method):
    patched_get_logger_method.side_effect = Exception(_TEST_ERROR_MESSAGE)


def test_try_get_logger_for_server_calls_get_logger_for_server(
    patched_get_logger_method,
):
    _try_get_logger_for_server(
        _TEST_HOST,
        ServerProtocol.TLS_TCP,
        _TEST_CERTS,
    )
    patched_get_logger_method.assert_called_once_with(
        _TEST_HOST,
        ServerProtocol.TLS_TCP,
        _TEST_CERTS,
    )


def test_try_get_logger_for_server_when_exception_raised_raises_crashplan_cli_error(
    errored_logger,
):
    with pytest.raises(crashplancliError) as err:
        _try_get_logger_for_server(
            _TEST_HOST,
            ServerProtocol.TCP,
            _TEST_CERTS,
        )

    assert (
        str(err.value)
        == f"Unable to connect to example.com. Failed with error: {_TEST_ERROR_MESSAGE}."
    )
