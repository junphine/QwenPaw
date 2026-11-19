from typing import Literal

RegistryEditPayloadKind = Literal["default", "model", "provider", "task_choice"]

REGISTRY_EDIT_PAYLOAD_KIND_VALUES: set[RegistryEditPayloadKind] = {
    "default",
    "model",
    "provider",
    "task_choice",
}


def check_registry_edit_payload_kind(value: str) -> RegistryEditPayloadKind:
    if value in REGISTRY_EDIT_PAYLOAD_KIND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REGISTRY_EDIT_PAYLOAD_KIND_VALUES!r}")
