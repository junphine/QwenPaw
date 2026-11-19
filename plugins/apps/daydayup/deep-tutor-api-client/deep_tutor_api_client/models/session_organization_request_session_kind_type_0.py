from typing import Literal

SessionOrganizationRequestSessionKindType0 = Literal["chat", "immersive_reading", "selection_tutor"]

SESSION_ORGANIZATION_REQUEST_SESSION_KIND_TYPE_0_VALUES: set[SessionOrganizationRequestSessionKindType0] = {
    "chat",
    "immersive_reading",
    "selection_tutor",
}


def check_session_organization_request_session_kind_type_0(value: str) -> SessionOrganizationRequestSessionKindType0:
    if value in SESSION_ORGANIZATION_REQUEST_SESSION_KIND_TYPE_0_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {SESSION_ORGANIZATION_REQUEST_SESSION_KIND_TYPE_0_VALUES!r}"
    )
