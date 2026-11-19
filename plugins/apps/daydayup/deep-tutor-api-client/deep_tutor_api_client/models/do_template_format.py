from typing import Literal

DoTemplateFormat = Literal["csv", "xlsx"]

DO_TEMPLATE_FORMAT_VALUES: set[DoTemplateFormat] = {
    "csv",
    "xlsx",
}


def check_do_template_format(value: str) -> DoTemplateFormat:
    if value in DO_TEMPLATE_FORMAT_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DO_TEMPLATE_FORMAT_VALUES!r}")
