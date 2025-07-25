import click
from click._compat import get_text_stderr

from crashplancli.logger import get_view_error_details_message

ERRORED = False


class crashplancliError(click.ClickException):
    """Base CLI exception. The `message` param automatically gets logged to error file and printed
    to stderr in red text. If `help` param is provided, it will also be printed to stderr after the
    message but not logged to file.
    """

    def __init__(self, message, help=None):
        self.help = help
        super().__init__(message)

    def show(self, file=None):
        """Override default `show` to print CLI errors in red text."""
        if file is None:
            file = get_text_stderr()
        click.secho(f"Error: {self.format_message()}", file=file, fg="red")
        if self.help:
            click.echo(self.help, err=True)


class LoggedCLIError(crashplancliError):
    """Exception to be raised when wanting to point users to error logs for error details.

    If `message` param is provided it will be printed to screen along with message on where to
    find error details in the log.
    """

    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

    def format_message(self):
        locations_message = get_view_error_details_message()
        return (
            f"{self.message}\n{locations_message}"
            if self.message
            else locations_message
        )


class UserDoesNotExistError(crashplancliError):
    """An error to represent a username that is not in our system. The CLI shows this error when
    the user tries to add or remove a user that does not exist. This error is not shown during
    bulk add or remove."""

    def __init__(self, username):
        super().__init__(
            f"User '{username}' does not exist or you do not have permission to view them."
        )


class UserNotInLegalHoldError(crashplancliError):
    def __init__(self, username, matter_id):
        super().__init__(
            f"User '{username}' is not an active member of legal hold matter '{matter_id}'."
        )
