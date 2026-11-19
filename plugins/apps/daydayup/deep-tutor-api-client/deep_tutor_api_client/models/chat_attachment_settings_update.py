from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ChatAttachmentSettingsUpdate")


@_attrs_define
class ChatAttachmentSettingsUpdate:
    """Chat attachment policy (size caps + extraction budgets).

    Bounds mirror the normalization clamps in
    ``runtime_settings.CHAT_ATTACHMENT_*_RANGE`` so the API rejects loudly
    what the file layer would silently clamp.

        Attributes:
            max_file_mb (int):
            max_total_mb (int):
            max_chars_per_doc (int):
            max_chars_total (int):
    """

    max_file_mb: int
    max_total_mb: int
    max_chars_per_doc: int
    max_chars_total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_file_mb = self.max_file_mb

        max_total_mb = self.max_total_mb

        max_chars_per_doc = self.max_chars_per_doc

        max_chars_total = self.max_chars_total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "max_file_mb": max_file_mb,
                "max_total_mb": max_total_mb,
                "max_chars_per_doc": max_chars_per_doc,
                "max_chars_total": max_chars_total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_file_mb = d.pop("max_file_mb")

        max_total_mb = d.pop("max_total_mb")

        max_chars_per_doc = d.pop("max_chars_per_doc")

        max_chars_total = d.pop("max_chars_total")

        chat_attachment_settings_update = cls(
            max_file_mb=max_file_mb,
            max_total_mb=max_total_mb,
            max_chars_per_doc=max_chars_per_doc,
            max_chars_total=max_chars_total,
        )

        chat_attachment_settings_update.additional_properties = d
        return chat_attachment_settings_update

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
