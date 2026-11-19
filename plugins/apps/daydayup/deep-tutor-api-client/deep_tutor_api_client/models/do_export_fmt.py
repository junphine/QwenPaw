from typing import Literal

DoExportFmt = Literal["auto", "markdown", "pdf"]

DO_EXPORT_FMT_VALUES: set[DoExportFmt] = {
    "auto",
    "markdown",
    "pdf",
}


def check_do_export_fmt(value: str) -> DoExportFmt:
    if value in DO_EXPORT_FMT_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DO_EXPORT_FMT_VALUES!r}")
