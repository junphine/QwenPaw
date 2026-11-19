from typing import Literal

AnnotationPayloadKind = Literal["citation", "highlight", "note", "underline"]

ANNOTATION_PAYLOAD_KIND_VALUES: set[AnnotationPayloadKind] = {
    "citation",
    "highlight",
    "note",
    "underline",
}


def check_annotation_payload_kind(value: str) -> AnnotationPayloadKind:
    if value in ANNOTATION_PAYLOAD_KIND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ANNOTATION_PAYLOAD_KIND_VALUES!r}")
