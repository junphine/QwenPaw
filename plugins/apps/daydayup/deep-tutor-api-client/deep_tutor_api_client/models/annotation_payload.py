from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.annotation_payload_kind import AnnotationPayloadKind, check_annotation_payload_kind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.text_position_selector_payload import TextPositionSelectorPayload
    from ..models.text_quote_selector_payload import TextQuoteSelectorPayload


T = TypeVar("T", bound="AnnotationPayload")


@_attrs_define
class AnnotationPayload:
    """An annotation as the reader sends it.

    ``rects`` are normalised to the unit box (0..1, origin top-left) by the
    client, because only the client knows the rendered geometry. They are still
    re-validated server-side — an inverted or out-of-range rectangle is ordered
    and clipped rather than trusted.

        Attributes:
            locator (int):
            annotation_id (str | Unset):  Default: ''.
            kind (AnnotationPayloadKind | Unset):  Default: 'highlight'.
            color (str | Unset):  Default: 'yellow'.
            quote (str | Unset):  Default: ''.
            note (str | Unset):  Default: ''.
            rects (list[list[float]] | Unset):
            source_anchor (str | Unset):  Default: ''.
            selectors (list[TextPositionSelectorPayload | TextQuoteSelectorPayload] | Unset):
    """

    locator: int
    annotation_id: str | Unset = ""
    kind: AnnotationPayloadKind | Unset = "highlight"
    color: str | Unset = "yellow"
    quote: str | Unset = ""
    note: str | Unset = ""
    rects: list[list[float]] | Unset = UNSET
    source_anchor: str | Unset = ""
    selectors: list[TextPositionSelectorPayload | TextQuoteSelectorPayload] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.text_quote_selector_payload import TextQuoteSelectorPayload  # noqa: PLC0415

        locator = self.locator

        annotation_id = self.annotation_id

        kind: str | Unset = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind

        color = self.color

        quote = self.quote

        note = self.note

        rects: list[list[float]] | Unset = UNSET
        if not isinstance(self.rects, Unset):
            rects = []
            for rects_item_data in self.rects:
                rects_item = rects_item_data

                rects.append(rects_item)

        source_anchor = self.source_anchor

        selectors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.selectors, Unset):
            selectors = []
            for selectors_item_data in self.selectors:
                selectors_item: dict[str, Any]
                if isinstance(selectors_item_data, TextQuoteSelectorPayload):
                    selectors_item = selectors_item_data.to_dict()
                else:
                    selectors_item = selectors_item_data.to_dict()

                selectors.append(selectors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
            }
        )
        if annotation_id is not UNSET:
            field_dict["annotation_id"] = annotation_id
        if kind is not UNSET:
            field_dict["kind"] = kind
        if color is not UNSET:
            field_dict["color"] = color
        if quote is not UNSET:
            field_dict["quote"] = quote
        if note is not UNSET:
            field_dict["note"] = note
        if rects is not UNSET:
            field_dict["rects"] = rects
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor
        if selectors is not UNSET:
            field_dict["selectors"] = selectors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.text_position_selector_payload import TextPositionSelectorPayload  # noqa: PLC0415
        from ..models.text_quote_selector_payload import TextQuoteSelectorPayload  # noqa: PLC0415

        d = dict(src_dict)
        locator = d.pop("locator")

        annotation_id = d.pop("annotation_id", UNSET)

        _kind = d.pop("kind", UNSET)
        kind: AnnotationPayloadKind | Unset
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = check_annotation_payload_kind(_kind)

        color = d.pop("color", UNSET)

        quote = d.pop("quote", UNSET)

        note = d.pop("note", UNSET)

        _rects = d.pop("rects", UNSET)
        rects: list[list[float]] | Unset = UNSET
        if _rects is not UNSET:
            rects = []
            for rects_item_data in _rects:
                rects_item = cast(list[float], rects_item_data)

                rects.append(rects_item)

        source_anchor = d.pop("source_anchor", UNSET)

        _selectors = d.pop("selectors", UNSET)
        selectors: list[TextPositionSelectorPayload | TextQuoteSelectorPayload] | Unset = UNSET
        if _selectors is not UNSET:
            selectors = []
            for selectors_item_data in _selectors:

                def _parse_selectors_item(data: object) -> TextPositionSelectorPayload | TextQuoteSelectorPayload:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        selectors_item_type_0 = TextQuoteSelectorPayload.from_dict(data)

                        return selectors_item_type_0
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    if not isinstance(data, dict):
                        raise TypeError()
                    selectors_item_type_1 = TextPositionSelectorPayload.from_dict(data)

                    return selectors_item_type_1

                selectors_item = _parse_selectors_item(selectors_item_data)

                selectors.append(selectors_item)

        annotation_payload = cls(
            locator=locator,
            annotation_id=annotation_id,
            kind=kind,
            color=color,
            quote=quote,
            note=note,
            rects=rects,
            source_anchor=source_anchor,
            selectors=selectors,
        )

        annotation_payload.additional_properties = d
        return annotation_payload

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
