from typing import Literal

MaterialInfoRenderMode = Literal["audio", "epub", "pdf", "text", "video"]

MATERIAL_INFO_RENDER_MODE_VALUES: set[MaterialInfoRenderMode] = {
    "audio",
    "epub",
    "pdf",
    "text",
    "video",
}


def check_material_info_render_mode(value: str) -> MaterialInfoRenderMode:
    if value in MATERIAL_INFO_RENDER_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MATERIAL_INFO_RENDER_MODE_VALUES!r}")
