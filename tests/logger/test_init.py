import logging
import os
from logging.handlers import RotatingFileHandler

import pytest
from requests import Request

from crashplancli.enums import OutputFormat
from crashplancli.enums import SendToFileEventsOutputFormat
from crashplancli.logger import add_handler_to_logger
from crashplancli.logger import CliLogger
from crashplancli.logger import get_logger_for_server
from crashplancli.logger import get_view_error_details_message
from crashplancli.logger import logger_has_handlers
from crashplancli.logger.enums import ServerProtocol
from crashplancli.logger.formatters import FileEventDictToCEFFormatter
from crashplancli.logger.formatters import FileEventDictToJSONFormatter
from crashplancli.logger.formatters import FileEventDictToRawJSONFormatter
from crashplancli.logger.handlers import NoPrioritySysLogHandler
from crashplancli.util import get_user_project_path


@pytest.fixture(autouse=True)
def init_socket_mock(mocker):
    return mocker.patch("crashplancli.logger.NoPrioritySysLogHandler.connect_socket")


@pytest.fixture(autouse=True)
def fresh_syslog_handler(init_socket_mock):
    # Set handlers to empty list so it gets initialized each test
    get_logger_for_server(
        "example.com",
        ServerProtocol.TCP,
        SendToFileEventsOutputFormat.CEF,
        None,
    ).handlers = []
    init_socket_mock.call_count = 0


def test_add_handler_to_logger_does_as_expected():
    logger = logging.getLogger("TEST_crashplan_CLI")
    formatter = logging.Formatter()
    handler = logging.Handler()
    add_handler_to_logger(logger, handler, formatter)
    assert handler in logger.handlers
    assert handler.formatter == formatter


def test_logger_has_handlers_when_logger_has_handlers_returns_true():
    logger = logging.getLogger("TEST_crashplan_CLI")
    handler = logging.Handler()
    logger.addHandler(handler)
    assert logger_has_handlers(logger)


def test_logger_has_handlers_when_logger_does_not_have_handlers_returns_false():
    logger = logging.getLogger("TEST_crashplan_CLI")
    logger.handlers = []
    assert not logger_has_handlers(logger)


def test_get_view_exceptions_location_message_returns_expected_message():
    actual = get_view_error_details_message()
    path = os.path.join(get_user_project_path("log"), "crashplan_errors.log")
    expected = f"View details in {path}"
    assert actual == expected


def test_get_logger_for_server_has_info_level():
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert logger.level == logging.INFO


def test_get_logger_for_server_when_given_cef_format_uses_cef_formatter():
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert isinstance(logger.handlers[0].formatter, FileEventDictToCEFFormatter)


def test_get_logger_for_server_when_given_json_format_uses_json_formatter():
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, OutputFormat.JSON, None
    )
    assert isinstance(logger.handlers[0].formatter, FileEventDictToJSONFormatter)


def test_get_logger_for_server_when_given_raw_json_format_uses_raw_json_formatter():
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, OutputFormat.RAW, None
    )
    assert isinstance(logger.handlers[0].formatter, FileEventDictToRawJSONFormatter)


def test_get_logger_for_server_when_called_twice_only_has_one_handler():
    get_logger_for_server("example.com", ServerProtocol.TCP, OutputFormat.JSON, None)
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert len(logger.handlers) == 1


def test_get_logger_for_server_uses_no_priority_syslog_handler():
    logger = get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert isinstance(logger.handlers[0], NoPrioritySysLogHandler)


def test_get_logger_for_server_constructs_handler_with_expected_args(
    mocker, monkeypatch
):
    no_priority_syslog_handler = mocker.patch(
        "crashplancli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, "cert"
    )
    no_priority_syslog_handler.assert_called_once_with(
        "example.com", 514, ServerProtocol.TCP, "cert"
    )


def test_get_logger_for_server_when_hostname_includes_port_constructs_handler_with_expected_args(
    mocker,
):
    no_priority_syslog_handler = mocker.patch(
        "crashplancli.logger.handlers.NoPrioritySysLogHandler.__init__"
    )
    no_priority_syslog_handler.return_value = None
    get_logger_for_server(
        "example.com:999", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    no_priority_syslog_handler.assert_called_once_with(
        "example.com",
        999,
        ServerProtocol.TCP,
        None,
    )


def test_get_logger_for_server_inits_socket(init_socket_mock):
    get_logger_for_server(
        "example.com", ServerProtocol.TCP, SendToFileEventsOutputFormat.CEF, None
    )
    assert init_socket_mock.call_count == 1


class TestCliLogger:
    def test_init_creates_user_error_logger_with_expected_handlers(self):
        logger = CliLogger()
        handler_types = [type(h) for h in logger._logger.handlers]
        assert RotatingFileHandler in handler_types

    def test_log_error_logs_expected_text_at_expected_level(self, caplog):
        with caplog.at_level(logging.ERROR):
            ex = Exception("TEST")
            CliLogger().log_error(ex)
            assert str(ex) in caplog.text

    def test_log_verbose_error_logs_expected_text_at_expected_level(
        self, mocker, caplog
    ):
        with caplog.at_level(logging.ERROR):
            request = mocker.MagicMock(sepc=Request)
            request.body = {"foo": "bar"}
            CliLogger().log_verbose_error("crashplan dothing --flag YES", request)
            assert "'crashplan dothing --flag YES'" in caplog.text
            assert "Request parameters: {'foo': 'bar'}" in caplog.text
