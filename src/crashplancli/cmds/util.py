from crashplancli import errors
from crashplancli.logger import get_main_cli_logger
from crashplancli.output_formats import OutputFormat

logger = get_main_cli_logger()


def try_get_default_header(include_all, default_header, output_format):
    """Returns appropriate header based on include-all and output format. If returns None,
    the CLI format option will figure out the header based on the data keys."""
    output_header = None if include_all else default_header
    if output_format != OutputFormat.TABLE and include_all:
        err_text = "--include-all only allowed for Table output format."
        logger.log_error(err_text)
        raise errors.crashplancliError(err_text)
    return output_header
