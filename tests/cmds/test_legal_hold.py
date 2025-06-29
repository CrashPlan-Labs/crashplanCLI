import datetime

import pytest
from pycpg.exceptions import PycpgBadRequestError
from pycpg.response import PycpgResponse
from requests import HTTPError
from requests import Response

from crashplancli.cmds.legal_hold import _check_matter_is_accessible
from crashplancli.date_helper import convert_datetime_to_timestamp
from crashplancli.main import cli

_NAMESPACE = "crashplancli.cmds.legal_hold"
TEST_MATTER_ID = "99999"
TEST_LEGAL_HOLD_MEMBERSHIP_UID = "88888"
TEST_LEGAL_HOLD_MEMBERSHIP_UID_2 = "77777"
ACTIVE_TEST_USERNAME = "user@example.com"
ACTIVE_TEST_USER_ID = "12345"
INACTIVE_TEST_USERNAME = "inactive@example.com"
INACTIVE_TEST_USER_ID = "54321"
TEST_POLICY_UID = "66666"
_CREATE_EVENT_ID = "564564654566"
_MEMBERSHIP_EVENT_ID = "74533457745"
TEST_PRESERVATION_POLICY_UID = "1010101010"
MATTER_RESPONSE = """
{
    "legalHoldUid": "88888",
    "name": "Test_Matter",
    "description": "",
    "notes": null,
    "holdExtRef": null,
    "active": true,
    "creationDate": "2020-01-01T00:00:00.000-06:00",
    "lastModified": "2019-12-19T20:32:10.781Z",
    "creator_username": "creator@example.com",
    "creator": {
        "userUid": "12345",
        "username": "creator@example.com",
        "email": "user@example.com",
        "userExtRef": null
    },
    "holdPolicyUid": "66666"
}
"""
POLICY_RESPONSE = """
{
    "legalHoldPolicyUid": "1010101010",
    "name": "Test",
    "creatorUser": {
        "userUid": "12345",
        "userId": 12345,
        "username": "user@example.com",
        "email": "user@example.com",
        "firstName": "User",
        "lastName": "User"
    },
    "policy": {
        "backupOpenFiles": true,
        "compression": "ON",
        "dataDeDupAutoMaxFileSizeForLan": 1000000000,
        "dataDeDupAutoMaxFileSizeForWan": 1000000000,
        "dataDeDuplication": "FULL",
        "encryptionEnabled": true,
        "scanIntervalMillis": 86400000,
        "scanTime": "03:00",
        "watchFiles": true,
        "destinations": [],
        "backupRunWindow": {
            "alwaysRun": true,
            "startTimeOfDay": "01:00",
            "endTimeOfDay": "06:00",
            "days": ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        },
        "backupPaths": {
            "paths": [],
            "excludePatterns": {
                "windows": [],
                "linux": [],
                "macintosh": [],
                "all": []
            }
        },
        "retentionPolicy": {
            "backupFrequencyMillis": 900000,
            "keepDeleted": true,
            "keepDeletedMinutes": 0,
            "versionLastWeekIntervalMinutes": 15,
            "versionLastNinetyDaysIntervalMinutes": 1440,
            "versionLastYearIntervalMinutes": 10080,
            "versionPrevYearsIntervalMinutes": 43200
        }
    },
    "creationDate": "2019-05-14T16:19:09.930Z",
    "modificationDate": "2019-05-14T16:19:09.930Z"
}
"""
EMPTY_CUSTODIANS_RESPONSE = """{"memberships": []}"""
ALL_ACTIVE_CUSTODIANS_RESPONSE = """
{
    "memberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": true,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "12345",
                "username": "user@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
ALL_INACTIVE_CUSTODIANS_RESPONSE = """
{
    "memberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": false,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "02345",
                "username": "inactive@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
ALL_ACTIVE_AND_INACTIVE_CUSTODIANS_RESPONSE = """
{
    "memberships": [
        {
            "legalHoldMembershipUid": "88888",
            "active": true,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "12345",
                "username": "user@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        },
        {
            "legalHoldMembershipUid": "88888",
            "active": false,
            "creationDate": "2020-07-16T08:50:23.405Z",
            "legalHold": {
                "legalHoldUid": "99999",
                "name": "test"
            },
            "user": {
                "userUid": "02345",
                "username": "inactive@example.com",
                "email": "user@example.com",
                "userExtRef": null
            }
        }
    ]
}
"""
TEST_EVENT_PAGE = [
    {
        "eventUid": "564564654566",
        "eventType": "HOLD_CREATED",
        "eventDate": "2015-05-16T15:07:44.820Z",
        "legalHoldUid": "88888",
        "actorPrincipal": {
            "type": "USER",
            "principalId": "12345",
            "displayName": "holdcreator@example.com",
            "user": {"email": "holdcreator@example.com"},
        },
    },
    {
        "eventUid": "74533457745",
        "eventType": "MEMBERSHIP_CREATED",
        "eventDate": "2019-05-17T15:07:44.820Z",
        "legalHoldUid": "88888",
        "legalHoldMembershipUid": "645576514441664433",
        "actorPrincipal": {
            "type": "USER",
            "principalId": "1234512345",
            "displayName": "creator@example.com",
            "user": {"email": "creator@example.com"},
        },
        "custodianPrincipal": {
            "type": "USER",
            "principalId": "12345",
            "displayName": "kim.jones@crashplan.com",
            "user": {"email": "kim.jones@crashplan.com"},
        },
    },
    {
        "eventUid": "74533457745",
        "eventType": "MEMBERSHIP_CREATED",
        "eventDate": "2019-05-17T15:07:44.820Z",
        "legalHoldUid": "88888",
        "legalHoldMembershipUid": "645576514441664433",
        "actorPrincipal": {
            "type": "API_KEY",
            "principalId": "key-bb5709f7-508d-4ea4-98a0-cpgf11111b42",
            "displayName": "key-bb5709f7-508d-4ea4-98a0-cpgf11111b42 (pycpg API client)",
        },
        "custodianPrincipal": {
            "type": "USER",
            "principalId": "12345",
            "displayName": "kim.jones@crashplan.com",
            "user": {"email": "kim.jones@crashplan.com"},
        },
    },
]

EMPTY_EVENTS_RESPONSE = "{[]}"
EMPTY_MATTERS_RESPONSE = '{"matters": []}'
ALL_MATTERS_RESPONSE = f'{{"matters": [{MATTER_RESPONSE}]}}'
LEGAL_HOLD_COMMAND = "legal-hold"


def _create_pycpg_response(mocker, text):
    response = mocker.MagicMock(spec=Response)
    response.text = text
    response._content_consumed = mocker.MagicMock()
    response.status_code = 200
    return PycpgResponse(response)


@pytest.fixture
def matter_response(mocker):
    return _create_pycpg_response(mocker, MATTER_RESPONSE)


@pytest.fixture
def preservation_policy_response(mocker):
    return _create_pycpg_response(mocker, POLICY_RESPONSE)


@pytest.fixture
def empty_legal_hold_memberships_response(mocker):
    return [_create_pycpg_response(mocker, EMPTY_CUSTODIANS_RESPONSE)]


@pytest.fixture
def active_legal_hold_memberships_response(mocker):
    return [_create_pycpg_response(mocker, ALL_ACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def inactive_legal_hold_memberships_response(mocker):
    return [_create_pycpg_response(mocker, ALL_INACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def active_and_inactive_legal_hold_memberships_response(mocker):
    return [_create_pycpg_response(mocker, ALL_ACTIVE_AND_INACTIVE_CUSTODIANS_RESPONSE)]


@pytest.fixture
def empty_events_response(mocker):
    return _create_pycpg_response(mocker, EMPTY_EVENTS_RESPONSE)


def events_list_generator():
    yield TEST_EVENT_PAGE


@pytest.fixture
def get_user_id_success(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {
        "users": [{"userUid": ACTIVE_TEST_USER_ID}]
    }


@pytest.fixture
def empty_matters_response(mocker):
    return [_create_pycpg_response(mocker, EMPTY_MATTERS_RESPONSE)]


@pytest.fixture
def all_matters_response(mocker):
    return [_create_pycpg_response(mocker, ALL_MATTERS_RESPONSE)]


@pytest.fixture
def get_user_id_failure(cli_state):
    cli_state.sdk.users.get_by_username.return_value = {"users": []}


@pytest.fixture
def check_matter_accessible_success(cli_state, matter_response):
    cli_state.sdk.legalhold.get_matter_by_uid.return_value = matter_response


@pytest.fixture
def check_matter_accessible_failure(cli_state, custom_error):
    cli_state.sdk.legalhold.get_matter_by_uid.side_effect = PycpgBadRequestError(
        custom_error
    )


@pytest.fixture
def get_all_events_success(cli_state):
    cli_state.sdk.legalhold.get_all_events.return_value = events_list_generator()


@pytest.fixture
def user_already_added_response(mocker):
    mock_response = mocker.MagicMock(spec=Response)
    mock_response.text = "USER_ALREADY_IN_HOLD"
    http_error = HTTPError()
    http_error.response = mock_response
    return PycpgBadRequestError(http_error)


def test_add_user_raises_user_already_added_error_when_user_already_on_hold(
    runner, cli_state, user_already_added_response
):

    cli_state.sdk.legalhold.add_to_matter.side_effect = user_already_added_response
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert f"'{ACTIVE_TEST_USERNAME}' is already on the legal hold matter id={TEST_MATTER_ID}"


def test_add_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    runner, cli_state, check_matter_accessible_failure, get_user_id_success
):
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        f"Matter with id={TEST_MATTER_ID} either does not exist or your profile does not have "
        f"permission to view it."
    )


def test_add_user_adds_user_to_hold_if_user_and_matter_exist(
    runner, cli_state, check_matter_accessible_success, get_user_id_success
):
    runner.invoke(
        cli,
        [
            "legal-hold",
            "add-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.legalhold.add_to_matter.assert_called_once_with(
        ACTIVE_TEST_USER_ID, TEST_MATTER_ID
    )


def test_remove_user_raises_legalhold_not_found_error_if_matter_inaccessible(
    runner, cli_state, check_matter_accessible_failure, get_user_id_success
):
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        f"Matter with id={TEST_MATTER_ID} either does not exist or your profile does not have "
        "permission to view it."
    )


def test_remove_user_raises_user_not_in_matter_error_if_user_not_active_in_matter(
    runner,
    cli_state,
    check_matter_accessible_success,
    get_user_id_success,
    empty_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        empty_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    assert result.exit_code == 1
    assert (
        f"User '{ACTIVE_TEST_USERNAME}' is not an active member of legal hold matter "
        f"'{TEST_MATTER_ID}'"
    )


def test_remove_user_removes_user_if_user_in_matter(
    runner,
    cli_state,
    check_matter_accessible_success,
    get_user_id_success,
    active_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_legal_hold_memberships_response
    )
    membership_uid = "88888"
    runner.invoke(
        cli,
        [
            "legal-hold",
            "remove-user",
            "--matter-id",
            TEST_MATTER_ID,
            "--username",
            ACTIVE_TEST_USERNAME,
        ],
        obj=cli_state,
    )
    cli_state.sdk.legalhold.remove_from_matter.assert_called_once_with(membership_uid)


def test_matter_accessible_check_only_makes_one_http_call_when_called_multiple_times_with_same_matter_id(
    sdk, check_matter_accessible_success
):
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    _check_matter_is_accessible(sdk, TEST_MATTER_ID)
    assert sdk.legalhold.get_matter_by_uid.call_count == 1


def test_show_matter_prints_active_and_inactive_results_when_include_inactive_flag_set(
    runner,
    cli_state,
    check_matter_accessible_success,
    active_and_inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME in result.output


def test_show_matter_prints_active_results_only(
    runner,
    cli_state,
    check_matter_accessible_success,
    active_and_inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_and_inactive_legal_hold_memberships_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output


def test_show_matter_prints_no_active_members_when_no_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    empty_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        empty_legal_hold_memberships_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_inactive_members_when_no_inactive_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    active_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        active_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME in result.output
    assert INACTIVE_TEST_USERNAME not in result.output
    assert "No inactive matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership(
    runner,
    cli_state,
    check_matter_accessible_success,
    inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_no_active_members_when_no_active_membership_and_inactive_membership_included(
    runner,
    cli_state,
    check_matter_accessible_success,
    inactive_legal_hold_memberships_response,
):
    cli_state.sdk.legalhold.get_all_matter_custodians.return_value = (
        inactive_legal_hold_memberships_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-inactive"], obj=cli_state
    )
    assert ACTIVE_TEST_USERNAME not in result.output
    assert INACTIVE_TEST_USERNAME in result.output
    assert "No active matter members." in result.output


def test_show_matter_prints_preservation_policy_when_include_policy_flag_set(
    runner, cli_state, check_matter_accessible_success, preservation_policy_response
):
    cli_state.sdk.legalhold.get_policy_by_uid.return_value = (
        preservation_policy_response
    )
    result = runner.invoke(
        cli, ["legal-hold", "show", TEST_MATTER_ID, "--include-policy"], obj=cli_state
    )
    assert TEST_PRESERVATION_POLICY_UID in result.output


def test_show_matter_does_not_print_preservation_policy(
    runner, cli_state, check_matter_accessible_success, preservation_policy_response
):
    cli_state.sdk.legalhold.get_policy_by_uid.return_value = (
        preservation_policy_response
    )
    result = runner.invoke(cli, ["legal-hold", "show", TEST_MATTER_ID], obj=cli_state)
    assert TEST_PRESERVATION_POLICY_UID not in result.output


def test_add_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_add.csv", "w") as csv:
            csv.writelines(["matter_id,username\n", "test,value\n"])
        runner.invoke(cli, ["legal-hold", "bulk", "add", "test_add.csv"], obj=cli_state)
    assert bulk_processor.call_args[0][1] == [
        {"matter_id": "test", "username": "value"}
    ]


def test_remove_bulk_users_uses_expected_arguments(runner, mocker, cli_state):
    bulk_processor = mocker.patch(f"{_NAMESPACE}.run_bulk_process")
    with runner.isolated_filesystem():
        with open("test_remove.csv", "w") as csv:
            csv.writelines(["matter_id,username\n", "test,value\n"])
        runner.invoke(
            cli, ["legal-hold", "bulk", "remove", "test_remove.csv"], obj=cli_state
        )
        assert bulk_processor.call_args[0][1] == [
            {"matter_id": "test", "username": "value"}
        ]


def test_list_with_format_csv_returns_csv_format(
    runner, cli_state, all_matters_response
):
    cli_state.sdk.legalhold.get_all_matters.return_value = all_matters_response
    result = runner.invoke(cli, ["legal-hold", "list", "-f", "csv"], obj=cli_state)
    assert "legalHoldUid" in result.output
    assert "name" in result.output
    assert "description" in result.output
    assert "active" in result.output
    assert "creationDate" in result.output
    assert "lastModified" in result.output
    assert "creator" in result.output
    assert "holdPolicyUid" in result.output
    assert "creator_username" in result.output
    assert "88888" in result.output
    assert "Test_Matter" in result.output
    comma_count = [c for c in result.output if c == ","]
    assert len(comma_count) >= 13


def test_list_with_csv_format_returns_no_response_when_response_is_empty(
    runner, cli_state, empty_legal_hold_memberships_response, empty_matters_response
):
    cli_state.sdk.legalhold.get_all_matters.return_value = empty_matters_response
    result = runner.invoke(
        cli,
        ["legal-hold", "list", "--matter-id", TEST_MATTER_ID, "-f", "csv"],
        obj=cli_state,
    )
    assert "Matter ID,Name,Description,Creator,Creation Date" not in result.output


def test_search_events_shows_events_that_respect_type_filters(
    runner, cli_state, get_all_events_success
):

    result = runner.invoke(
        cli,
        [
            "legal-hold",
            "search-events",
            "--matter-id",
            TEST_MATTER_ID,
            "--event-type",
            "HOLD_CREATED",
        ],
        obj=cli_state,
    )

    assert _CREATE_EVENT_ID in result.output
    assert _MEMBERSHIP_EVENT_ID not in result.output


def test_search_events_with_csv_returns_no_events_when_response_is_empty(
    runner, cli_state, get_all_events_success, empty_events_response
):
    cli_state.sdk.legalhold.get_all_events.return_value = empty_events_response
    result = runner.invoke(
        cli,
        ["legal-hold", "events", "--matter-id", TEST_MATTER_ID, "-f", "csv"],
        obj=cli_state,
    )

    assert (
        "actorEmail,actorUsername,actorLastName,actorUserUid,actorUserExtRef"
        not in result.output
    )


def test_search_events_is_called_with_expected_begin_timestamp(runner, cli_state):
    expected_timestamp = convert_datetime_to_timestamp(
        datetime.datetime.strptime("2017-01-01", "%Y-%m-%d")
    )
    command = [
        "legal-hold",
        "search-events",
        "--matter-id",
        TEST_MATTER_ID,
        "--begin",
        "2017-01-01T00:00:00",
    ]
    runner.invoke(cli, command, obj=cli_state)

    cli_state.sdk.legalhold.get_all_events.assert_called_once_with(
        TEST_MATTER_ID, expected_timestamp, None
    )


def test_search_events_when_no_results_outputs_no_results(runner, cli_state):
    cli_state.sdk.legalhold.get_all_matters.return_value = empty_matters_response
    command = ["legal-hold", "search-events", "--matter-id", TEST_MATTER_ID]
    result = runner.invoke(cli, command, obj=cli_state)
    assert "No results found." in result.output


@pytest.mark.parametrize(
    "command, error_msg",
    [
        (
            f"{LEGAL_HOLD_COMMAND} add-user --matter-id test-matter-id",
            "Missing option '-u' / '--username'.",
        ),
        (
            f"{LEGAL_HOLD_COMMAND} remove-user --matter-id test-matter-id",
            "Missing option '-u' / '--username'.",
        ),
        (
            f"{LEGAL_HOLD_COMMAND} add-user",
            "Missing option '-m' / '--matter-id'.",
        ),
        (
            f"{LEGAL_HOLD_COMMAND} remove-user",
            "Missing option '-m' / '--matter-id'.",
        ),
        (f"{LEGAL_HOLD_COMMAND} show", "Missing argument 'MATTER_ID'."),
        (
            f"{LEGAL_HOLD_COMMAND} bulk add",
            "Error: Missing argument 'CSV_FILE'.",
        ),
        (
            f"{LEGAL_HOLD_COMMAND} bulk remove",
            "Error: Missing argument 'CSV_FILE'.",
        ),
    ],
)
def test_legal_hold_command_when_missing_required_parameters_returns_error(
    command, error_msg, runner, cli_state
):
    result = runner.invoke(cli, command.split(" "), obj=cli_state)
    assert result.exit_code == 2
    assert error_msg in "".join(result.output)
