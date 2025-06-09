from getpass import getpass

import click
from click import echo
from click import secho

import crashplancli.profile as cliprofile
from crashplancli.click_ext.options import incompatible_with
from crashplancli.click_ext.types import PromptChoice
from crashplancli.click_ext.types import TOTP
from crashplancli.errors import crashplancliError
from crashplancli.options import yes_option
from crashplancli.profile import CREATE_PROFILE_HELP
from crashplancli.sdk_client import create_sdk
from crashplancli.util import does_user_agree


@click.group()
def profile():
    """Manage crashplan connection settings."""
    pass


debug_option = click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Turn on debug logging.",
)
totp_option = click.option(
    "--totp", help="TOTP token for multi-factor authentication.", type=TOTP()
)


def profile_name_arg(required=False):
    return click.argument("profile_name", required=required)


def name_option(required=False):
    return click.option(
        "-n",
        "--name",
        required=required,
        help="The name of the crashplan CLI profile to use when executing this command.",
    )


def server_option(required=False):
    return click.option(
        "-s",
        "--server",
        required=required,
        help="The URL you use to sign into crashplan.",
    )


def username_option(required=False):
    return click.option(
        "-u",
        "--username",
        required=required,
        cls=incompatible_with(["api_client_id", "secret"]),
        help="The username of the crashplan API user.",
    )


password_option = click.option(
    "--password",
    cls=incompatible_with(["api_client_id", "secret"]),
    help="The password for the crashplan API user. If this option is omitted, interactive prompts "
    "will be used to obtain the password.",
)

disable_ssl_option = click.option(
    "--disable-ssl-errors",
    type=click.types.BOOL,
    help="For development purposes, do not validate the SSL certificates of crashplan servers. "
    "This is not recommended, except for specific scenarios like testing. Attach this flag to the update command to toggle the setting.",
    default=None,
)


def api_client_id_option(required=False):
    return click.option(
        "--api-client-id",
        required=required,
        cls=incompatible_with(["username", "password", "totp"]),
        help="The API client key for API client authentication.  Used with the `--secret` option.",
    )


def secret_option(required=False):
    return click.option(
        "--secret",
        required=required,
        cls=incompatible_with(["username", "password", "totp"]),
        help="The API secret for API client authentication.  Used with the `--api-client` option.",
    )


@profile.command()
@profile_name_arg()
def show(profile_name):
    """Print the details of a profile."""
    cpgprofile = cliprofile.get_profile(profile_name)
    echo(f"\n{cpgprofile.name}:")
    if cpgprofile.api_client_auth == "True":
        echo(f"\t* api-client-id = {cpgprofile.username}")
    else:
        echo(f"\t* username = {cpgprofile.username}")
    echo(f"\t* authority url = {cpgprofile.authority_url}")
    echo(f"\t* ignore-ssl-errors = {cpgprofile.ignore_ssl_errors}")
    echo(f"\t* api-client-auth-profile = {cpgprofile.api_client_auth}")
    if cpgprofile.api_client_auth == "True":
        if cliprofile.get_stored_password(cpgprofile.name) is not None:
            echo("\t* The API client secret is set.")
    else:
        if cliprofile.get_stored_password(cpgprofile.name) is not None:
            echo("\t* A password is set.")
    echo("")
    echo("")


@profile.command()
@name_option(required=True)
@server_option(required=True)
@username_option(required=True)
@password_option
@totp_option
@yes_option(hidden=True)
@disable_ssl_option
@debug_option
def create(
    name,
    server,
    username,
    password,
    disable_ssl_errors,
    debug,
    totp,
):
    """
    Create a profile with username/password authentication.
    The first profile created will be the default.
    """
    cliprofile.create_profile(
        name,
        server,
        username,
        disable_ssl_errors,
        api_client_auth=False,
    )
    password = password or _prompt_for_password()
    if password:
        _set_pw(name, password, debug, totp=totp, api_client=False)
    echo(f"Successfully created profile '{name}'.")


@profile.command()
@name_option(required=True)
@server_option(required=True)
@api_client_id_option(required=True)
@secret_option(required=True)
@yes_option(hidden=True)
@disable_ssl_option
@debug_option
def create_api_client(
    name,
    server,
    api_client_id,
    secret,
    disable_ssl_errors,
    debug,
):
    """
    Create a profile with crashplan API client authentication.
    The first profile created will be the default.
    """
    cliprofile.create_profile(
        name,
        server,
        api_client_id,
        disable_ssl_errors,
        api_client_auth=True,
    )
    _set_pw(name, secret, debug, totp=False, api_client=True)
    echo(f"Successfully created profile '{name}'.")


@profile.command()
@name_option()
@server_option()
@api_client_id_option()
@secret_option()
@username_option()
@password_option
@totp_option
@disable_ssl_option
@yes_option(hidden=True)
@debug_option
def update(
    name,
    server,
    api_client_id,
    secret,
    username,
    password,
    disable_ssl_errors,
    debug,
    totp,
):
    """Update an existing profile."""
    cpgprofile = cliprofile.get_profile(name)

    if not any(
        [
            server,
            api_client_id,
            secret,
            username,
            password,
            disable_ssl_errors is not None,
        ]
    ):
        if cpgprofile.api_client_auth == "True":
            raise click.UsageError(
                "Must provide at least one of `--server`, `--api-client-id`, `--secret`, or "
                "`--disable-ssl-errors` when updating an API client profile.  "
                "Provide both `--username` and `--password` options to switch this profile to username/password authentication."
            )
        else:
            raise click.UsageError(
                "Must provide at least one of `--server`, `--username`, `--password`, or "
                "`--disable-ssl-errors` when updating a username/password authenticated profile.  "
                "Provide both `--api-client-id` and `--secret` options to switch this profile to crashplan API client authentication."
            )

    if cpgprofile.api_client_auth == "True":
        if (username and not password) or (password and not username):
            raise click.UsageError(
                "This profile currently uses API client authentication.  "
                "Please provide both the `--username` and `--password` options to update this profile to use username/password authentication."
            )
        elif username and password:
            if does_user_agree(
                "You passed the `--username` and `--password options for a profile currently using crashplan API client authentication.  "
                "Are you sure you would like to update this profile to use username/password authentication? This will overwrite existing credentials. (y/n): "
            ):
                cliprofile.update_profile(
                    cpgprofile.name,
                    server,
                    username,
                    disable_ssl_errors,
                    api_client_auth=False,
                )
                _set_pw(cpgprofile.name, password, debug, api_client=False)
            else:
                echo(f"Profile '{cpgprofile.name}` was not updated.")
                return
        else:
            cliprofile.update_profile(
                cpgprofile.name,
                server,
                api_client_id,
                disable_ssl_errors,
            )
            if secret:
                _set_pw(cpgprofile.name, secret, debug, api_client=True)

    else:
        if (api_client_id and not secret) or (api_client_id and not secret):
            raise click.UsageError(
                "This profile currently uses username/password authentication.  "
                "Please provide both the `--api-client-id` and `--secret` options to update this profile to use crashplan API client authentication."
            )
        elif api_client_id and secret:
            if does_user_agree(
                "You passed the `--api-client-id` and `--secret options for a profile currently using username/password authentication.  "
                "Are you sure you would like to update this profile to use crashplan API client authentication? This will overwrite existing credentials. (y/n): "
            ):
                cliprofile.update_profile(
                    cpgprofile.name,
                    server,
                    api_client_id,
                    disable_ssl_errors,
                    api_client_auth=True,
                )
                _set_pw(cpgprofile.name, secret, debug, api_client=True)
            else:
                echo(f"Profile '{name}` was not updated.")
                return
        else:
            cliprofile.update_profile(
                cpgprofile.name,
                server,
                username,
                disable_ssl_errors,
            )
            if not password and not cpgprofile.has_stored_password:
                password = _prompt_for_password()

            if password:
                _set_pw(cpgprofile.name, password, debug, totp=totp)

    echo(f"Profile '{cpgprofile.name}' has been updated.")


@profile.command()
@profile_name_arg()
@debug_option
def reset_pw(profile_name, debug):
    """\b
    Change the stored password for a profile. Only affects what's stored in the local profile,
    does not make any changes to the crashplan user account."""
    password = getpass()
    profile_name_saved = _set_pw(profile_name, password, debug)
    echo(f"Password updated for profile '{profile_name_saved}'.")


@profile.command("list")
def _list():
    """Show all existing stored profiles."""
    profiles = cliprofile.get_all_profiles()
    if not profiles:
        raise crashplancliError("No existing profile.", help=CREATE_PROFILE_HELP)
    for cpgprofile in profiles:
        echo(str(cpgprofile))


@profile.command()
@profile_name_arg()
def use(profile_name):
    """\b
    Set a profile as the default. If not providing a profile-name,
    prompts for a choice from a list of all profiles."""

    if not profile_name:
        _select_profile_from_prompt()
        return

    _set_default_profile(profile_name)


@profile.command()
@yes_option()
@profile_name_arg(required=True)
def delete(profile_name):
    """Deletes a profile and its stored password (if any)."""
    try:
        cliprofile.get_profile(profile_name)
    except crashplancliError:
        raise crashplancliError(f"Profile '{profile_name}' does not exist.")
    message = (
        "\nDeleting this profile will also delete any stored passwords and checkpoints. "
        "Are you sure? (y/n): "
    )
    if cliprofile.is_default_profile(profile_name):
        message = f"\n'{profile_name}' is currently the default profile!\n{message}"
    if does_user_agree(message):
        cliprofile.delete_profile(profile_name)
        echo(f"Profile '{profile_name}' has been deleted.")


@profile.command()
@yes_option()
def delete_all():
    """Deletes all profiles and saved passwords (if any)."""
    existing_profiles = cliprofile.get_all_profiles()
    if existing_profiles:
        profile_str_list = "\n\t".join(
            [cpgprofile.name for cpgprofile in existing_profiles]
        )
        message = (
            f"\nAre you sure you want to delete the following profiles?\n\t{profile_str_list}"
            "\n\nThis will also delete any stored passwords and checkpoints. (y/n): "
        )
        if does_user_agree(message):
            for profile_obj in existing_profiles:
                cliprofile.delete_profile(profile_obj.name)
                echo(f"Profile '{profile_obj.name}' has been deleted.")
    else:
        echo("\nNo profiles exist. Nothing to delete.")


def _prompt_for_password():
    if does_user_agree("Would you like to set a password? (y/n): "):
        password = getpass()
        return password


def _set_pw(profile_name, password, debug, totp=None, api_client=False):
    cpgprofile = cliprofile.get_profile(profile_name)
    try:
        create_sdk(
            cpgprofile,
            is_debug_mode=debug,
            password=password,
            totp=totp,
            api_client=api_client,
        )
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cliprofile.set_password(password, cpgprofile.name)
    return cpgprofile.name


def _select_profile_from_prompt():
    """Set the default profile from user input."""
    profiles = cliprofile.get_all_profiles()
    profile_names = [profile_choice.name for profile_choice in profiles]
    choices = PromptChoice(profile_names)
    choices.print_choices()
    prompt_message = "Input the number of the profile you wish to use"
    profile_name = click.prompt(prompt_message, type=choices)
    _set_default_profile(profile_name)


def _set_default_profile(profile_name):
    cliprofile.switch_default_profile(profile_name)
    _print_default_profile_was_set(profile_name)


def _print_default_profile_was_set(profile_name):
    echo(f"{profile_name} has been set as the default profile.")
