import json
from datetime import datetime

import click

from crashplancli.click_ext.options import incompatible_with
from crashplancli.click_ext.types import FileOrString
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


send_to_format_options = click.option(
    "-f",
    "--format",
    type=click.Choice(SendToFileEventsOutputFormat(), case_sensitive=False),
    help="The output format of the result. Defaults to RAW-JSON format.",
    default=SendToFileEventsOutputFormat.RAW,
)
