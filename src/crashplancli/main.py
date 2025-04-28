import os
import signal
import site
import sys
import warnings
from importlib.metadata import entry_points
from importlib.metadata import version as get_version

import click
from click_plugins import with_plugins
from pycpg.settings import set_user_agent_prefix

from crashplancli import BANNER
from crashplancli import PRODUCT_NAME
from crashplancli.click_ext.groups import ExceptionHandlingGroup
from crashplancli.cmds.auditlogs import audit_logs
from crashplancli.cmds.devices import devices
from crashplancli.cmds.legal_hold import legal_hold
from crashplancli.cmds.profile import profile
from crashplancli.cmds.shell import shell
from crashplancli.cmds.users import users
from crashplancli.options import sdk_options

warnings.simplefilter("ignore", DeprecationWarning)


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    click.echo(err=True)
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)

crashplancli = get_version("crashplancli")

# Sets part of the user agent string that pycpg attaches to requests for the purposes of
# identifying CLI users.
set_user_agent_prefix(f"{PRODUCT_NAME}/{crashplancli}  (crashplan; crashplan.com )")

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 200,
}


@with_plugins(entry_points("crashplancli.plugins"))
@click.group(
    cls=ExceptionHandlingGroup,
    context_settings=CONTEXT_SETTINGS,
    help=BANNER,
    invoke_without_command=True,
    no_args_is_help=True,
)
@click.option(
    "--python",
    is_flag=True,
    help="Print path to the python interpreter env that `crashplancli` is installed in.",
)
@click.option(
    "--script-dir",
    is_flag=True,
    help="Print the directory the `crashplan` script was installed in (for adding to your PATH if needed).",
)
@sdk_options(hidden=True)
def cli(state, python, script_dir):
    if python:
        click.echo(sys.executable)
        sys.exit(0)
    if script_dir:
        for root, _dirs, files in os.walk(site.PREFIXES[0]):
            if "crashplan" in files or "crashplan.exe" in files:
                print(root)
                sys.exit(0)

        for root, _dirs, files in os.walk(site.USER_BASE):
            if "crashplan" in files or "crashplan.exe" in files:
                print(root)
                sys.exit(0)


cli.add_command(audit_logs)
cli.add_command(devices)
cli.add_command(legal_hold)
cli.add_command(profile)
cli.add_command(shell)
cli.add_command(users)
