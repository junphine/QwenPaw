from typing import Literal

MaterialDetailContentFormat = Literal["plain_text", "web_markdown"]

MATERIAL_DETAIL_CONTENT_FORMAT_VALUES: set[MaterialDetailContentFormat] = {
    "plain_text",
    "web_markdown",
}


def check_material_detail_content_format(value: str) -> MaterialDetailContentFormat:
    if value in MATERIAL_DETAIL_CONTENT_FORMAT_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MATERIAL_DETAIL_CONTENT_FORMAT_VALUES!r}")
