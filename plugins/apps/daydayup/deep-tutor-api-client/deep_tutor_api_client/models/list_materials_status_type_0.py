from typing import Literal

ListMaterialsStatusType0 = Literal["failed", "processing", "queued", "ready"]

LIST_MATERIALS_STATUS_TYPE_0_VALUES: set[ListMaterialsStatusType0] = {
    "failed",
    "processing",
    "queued",
    "ready",
}


def check_list_materials_status_type_0(value: str) -> ListMaterialsStatusType0:
    if value in LIST_MATERIALS_STATUS_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIST_MATERIALS_STATUS_TYPE_0_VALUES!r}")
