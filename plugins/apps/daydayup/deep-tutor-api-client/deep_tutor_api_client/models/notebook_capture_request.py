from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotebookCaptureRequest")


@_attrs_define
class NotebookCaptureRequest:
    """
    Attributes:
        notebook_ids (list[str]):
        material_ids (list[str] | Unset):
        title (str | Unset):  Default: ''.
        summary (str | Unset):  Default: ''.
    """

    notebook_ids: list[str]
    material_ids: list[str] | Unset = UNSET
    title: str | Unset = ""
    summary: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notebook_ids = self.notebook_ids

        material_ids: list[str] | Unset = UNSET
        if not isinstance(self.material_ids, Unset):
            material_ids = self.material_ids

        title = self.title

        summary = self.summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notebook_ids": notebook_ids,
            }
        )
        if material_ids is not UNSET:
            field_dict["material_ids"] = material_ids
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        notebook_ids = cast(list[str], d.pop("notebook_ids"))

        material_ids = cast(list[str], d.pop("material_ids", UNSET))

        title = d.pop("title", UNSET)

        summary = d.pop("summary", UNSET)

        notebook_capture_request = cls(
            notebook_ids=notebook_ids,
            material_ids=material_ids,
            title=title,
            summary=summary,
        )

        notebook_capture_request.additional_properties = d
        return notebook_capture_request

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
