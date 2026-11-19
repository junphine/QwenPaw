from typing import Literal

MaterialDetailRenderMode = Literal["audio", "epub", "pdf", "text", "video"]

MATERIAL_DETAIL_RENDER_MODE_VALUES: set[MaterialDetailRenderMode] = {
    "audio",
    "epub",
    "pdf",
    "text",
    "video",
}


def check_material_detail_render_mode(value: str) -> MaterialDetailRenderMode:
    if value in MATERIAL_DETAIL_RENDER_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MATERIAL_DETAIL_RENDER_MODE_VALUES!r}")
