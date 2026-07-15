from pandas import DataFrame

from crashplancli.enums import OutputFormat
from crashplancli.output_formats import DataFrameOutputFormatter
from crashplancli.output_formats import to_csv

TEST_DATA = [
    {"a": "1", "b": "2"},
    {"a": "3", "b": "4"},
]

TEST_DATAFRAME = DataFrame(
    [
        {"string_column": "string1", "int_column": 42, "null_column": None},
        {"string_column": "string2", "int_column": 43, "null_column": None},
    ]
)


def test_to_csv_uses_unix_line_endings_to_avoid_extra_windows_line_breaks():
    # csv.DictWriter emits "\r\n" line endings. to_csv() writes into a
    # StringIO(newline=None), which strips those to "\n". This matters because
    # the result is echoed to stdout: on Windows a text-mode stdout translates
    # "\n" -> "\r\n", so if the "\r" were left in we'd get "\r\r\n" and a blank
    # line between every row.
    formatted_output = to_csv(TEST_DATA)
    assert "\r" not in formatted_output
    assert "\n" in formatted_output


def test_dataframe_csv_formatter_normalizes_windows_line_endings():
    # pandas defaults its line terminator to os.linesep, so on Windows to_csv()
    # emits "\r\n". Those rows would become "\r\r\n" (a blank line between every
    # row) once echoed to a text-mode stdout. Forcing the "\r\n" terminator here
    # reproduces the Windows output on any OS; the formatter must strip the "\r"
    # and yield "\n"-only rows.
    formatter = DataFrameOutputFormatter(OutputFormat.CSV)
    output = "".join(
        formatter.get_formatted_output(TEST_DATAFRAME, lineterminator="\r\n")
    )
    assert "\r" not in output
    assert (
        output
        == "string_column,int_column,null_column\nstring1,42,\nstring2,43,\n"
    )
