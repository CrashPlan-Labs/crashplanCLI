import click

from crashplancli import BANNER
from crashplancli.options import sdk_options


@click.command()
@sdk_options()
def shell(state):
    """Open an IPython shell with pycpg initialized as `sdk`."""
    import IPython

    IPython.embed(colors="Neutral", banner1=BANNER, user_ns={"sdk": state.sdk})
