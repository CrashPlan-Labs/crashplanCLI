from datetime import datetime
from datetime import timezone

import click

from crashplancli.click_ext.options import incompatible_with
from crashplancli.logger.enums import ServerProtocol

include_all_option = click.option(
    "--include-all",
    default=False,
    is_flag=True,
    help="Display simple properties of the primary level of the nested response.",
    cls=incompatible_with("columns"),
)


def server_options(f):
    hostname_arg = click.argument("hostname")
    protocol_option = click.option(
        "-p",
        "--protocol",
        type=click.Choice(ServerProtocol(), case_sensitive=False),
        default=ServerProtocol.UDP,
        help="Protocol used to send logs to server. "
        "Use TCP-TLS for additional security. Defaults to UDP.",
    )
    certs_option = click.option(
        "--certs",
        type=str,
        help="A CA certificates-chain file for the TCP-TLS protocol.",
    )
    ignore_cert_validation = click.option(
        "--ignore-cert-validation",
        help="Set to skip CA certificate validation. "
        "Incompatible with the 'certs' option.",
        is_flag=True,
        default=None,
        cls=incompatible_with(["certs"]),
    )
    f = hostname_arg(f)
    f = protocol_option(f)
    f = certs_option(f)
    f = ignore_cert_validation(f)
    return f


AdvancedQueryAndSavedSearchIncompatible = incompatible_with(
    ["advanced_query", "saved_search"]
)


class BeginOption(AdvancedQueryAndSavedSearchIncompatible):
    """click.Option subclass that enforces correct --begin option usage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        # if ctx.obj is None it means we're in autocomplete mode and don't want to validate
        if ctx.obj is not None:
            profile = opts.get("profile") or ctx.obj.profile.name
            cursor = ctx.obj.cursor_getter(profile)
            checkpoint_arg_present = "use_checkpoint" in opts
            checkpoint_value = (
                cursor.get(opts.get("use_checkpoint", ""))
                if checkpoint_arg_present
                else None
            )
            begin_present = "begin" in opts
            if (
                checkpoint_arg_present
                and checkpoint_value is not None
                and begin_present
            ):
                opts.pop("begin")
                try:
                    checkpoint_value = datetime.fromtimestamp(
                        float(checkpoint_value), timezone.utc
                    )
                except ValueError:
                    pass
                click.echo(
                    "Ignoring --begin value as --use-checkpoint was passed and checkpoint of "
                    f"{checkpoint_value} exists.\n",
                    err=True,
                )
            if (
                checkpoint_arg_present
                and checkpoint_value is None
                and not begin_present
            ):
                raise click.UsageError(
                    message="--begin date is required for --use-checkpoint when no checkpoint "
                    "exists yet.",
                )
            if not checkpoint_arg_present and not begin_present:
                raise click.UsageError(message="--begin date is required.")
        return super().handle_parse_result(ctx, opts, args)
