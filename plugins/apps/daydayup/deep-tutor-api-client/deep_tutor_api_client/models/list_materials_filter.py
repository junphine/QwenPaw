from typing import Literal

ListMaterialsFilter = Literal["all", "failed", "processing", "unassigned"]

LIST_MATERIALS_FILTER_VALUES: set[ListMaterialsFilter] = {
    "all",
    "failed",
    "processing",
    "unassigned",
}


def check_list_materials_filter(value: str) -> ListMaterialsFilter:
    if value in LIST_MATERIALS_FILTER_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIST_MATERIALS_FILTER_VALUES!r}")
