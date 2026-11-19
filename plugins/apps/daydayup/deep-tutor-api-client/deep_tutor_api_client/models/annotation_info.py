from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.annotation_info_selectors_item import AnnotationInfoSelectorsItem


T = TypeVar("T", bound="AnnotationInfo")


@_attrs_define
class AnnotationInfo:
    """
    Attributes:
        annotation_id (str):
        locator (int):
        kind (str):
        color (str):
        quote (str):
        note (str):
        rects (list[list[float]]):
        author (str):
        created_at (float):
        updated_at (float):
        material_revision (int | Unset):  Default: 1.
        source_anchor (str | Unset):  Default: ''.
        selectors (list[AnnotationInfoSelectorsItem] | Unset):
    """

    annotation_id: str
    locator: int
    kind: str
    color: str
    quote: str
    note: str
    rects: list[list[float]]
    author: str
    created_at: float
    updated_at: float
    material_revision: int | Unset = 1
    source_anchor: str | Unset = ""
    selectors: list[AnnotationInfoSelectorsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        annotation_id = self.annotation_id

        locator = self.locator

        kind = self.kind

        color = self.color

        quote = self.quote

        note = self.note

        rects = []
        for rects_item_data in self.rects:
            rects_item = rects_item_data

            rects.append(rects_item)

        author = self.author

        created_at = self.created_at

        updated_at = self.updated_at

        material_revision = self.material_revision

        source_anchor = self.source_anchor

        selectors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.selectors, Unset):
            selectors = []
            for selectors_item_data in self.selectors:
                selectors_item = selectors_item_data.to_dict()
                selectors.append(selectors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_id": annotation_id,
                "locator": locator,
                "kind": kind,
                "color": color,
                "quote": quote,
                "note": note,
                "rects": rects,
                "author": author,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if material_revision is not UNSET:
            field_dict["material_revision"] = material_revision
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor
        if selectors is not UNSET:
            field_dict["selectors"] = selectors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.annotation_info_selectors_item import AnnotationInfoSelectorsItem  # noqa: PLC0415

        d = dict(src_dict)
        annotation_id = d.pop("annotation_id")

        locator = d.pop("locator")

        kind = d.pop("kind")

        color = d.pop("color")

        quote = d.pop("quote")

        note = d.pop("note")

        rects = []
        _rects = d.pop("rects")
        for rects_item_data in _rects:
            rects_item = cast(list[float], rects_item_data)

            rects.append(rects_item)

        author = d.pop("author")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        material_revision = d.pop("material_revision", UNSET)

        source_anchor = d.pop("source_anchor", UNSET)

        _selectors = d.pop("selectors", UNSET)
        selectors: list[AnnotationInfoSelectorsItem] | Unset = UNSET
        if _selectors is not UNSET:
            selectors = []
            for selectors_item_data in _selectors:
                selectors_item = AnnotationInfoSelectorsItem.from_dict(selectors_item_data)

                selectors.append(selectors_item)

        annotation_info = cls(
            annotation_id=annotation_id,
            locator=locator,
            kind=kind,
            color=color,
            quote=quote,
            note=note,
            rects=rects,
            author=author,
            created_at=created_at,
            updated_at=updated_at,
            material_revision=material_revision,
            source_anchor=source_anchor,
            selectors=selectors,
        )

        annotation_info.additional_properties = d
        return annotation_info

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
