from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddChapterRequest")


@_attrs_define
class AddChapterRequest:
    """
    Attributes:
        title (str | Unset):  Default: ''.
        position (int | None | Unset):
        content_type (str | Unset):  Default: 'theory'.
        learning_objectives (list[str] | Unset):
        summary (str | Unset):  Default: ''.
        expected_revision (int | None | Unset):
    """

    title: str | Unset = ""
    position: int | None | Unset = UNSET
    content_type: str | Unset = "theory"
    learning_objectives: list[str] | Unset = UNSET
    summary: str | Unset = ""
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        position: int | None | Unset
        if isinstance(self.position, Unset):
            position = UNSET
        else:
            position = self.position

        content_type = self.content_type

        learning_objectives: list[str] | Unset = UNSET
        if not isinstance(self.learning_objectives, Unset):
            learning_objectives = self.learning_objectives

        summary = self.summary

        expected_revision: int | None | Unset
        if isinstance(self.expected_revision, Unset):
            expected_revision = UNSET
        else:
            expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if position is not UNSET:
            field_dict["position"] = position
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if learning_objectives is not UNSET:
            field_dict["learning_objectives"] = learning_objectives
        if summary is not UNSET:
            field_dict["summary"] = summary
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        def _parse_position(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        position = _parse_position(d.pop("position", UNSET))

        content_type = d.pop("content_type", UNSET)

        learning_objectives = cast(list[str], d.pop("learning_objectives", UNSET))

        summary = d.pop("summary", UNSET)

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        add_chapter_request = cls(
            title=title,
            position=position,
            content_type=content_type,
            learning_objectives=learning_objectives,
            summary=summary,
            expected_revision=expected_revision,
        )

        add_chapter_request.additional_properties = d
        return add_chapter_request

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
