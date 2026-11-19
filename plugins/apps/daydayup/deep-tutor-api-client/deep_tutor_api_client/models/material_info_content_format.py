from typing import Literal

MaterialInfoContentFormat = Literal["plain_text", "web_markdown"]

MATERIAL_INFO_CONTENT_FORMAT_VALUES: set[MaterialInfoContentFormat] = {
    "plain_text",
    "web_markdown",
}


def check_material_info_content_format(value: str) -> MaterialInfoContentFormat:
    if value in MATERIAL_INFO_CONTENT_FORMAT_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MATERIAL_INFO_CONTENT_FORMAT_VALUES!r}")
