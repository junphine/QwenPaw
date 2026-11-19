from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LearningCaptureUpdateRequest")


@_attrs_define
class LearningCaptureUpdateRequest:
    """
    Attributes:
        status (None | str | Unset):
        user_note (None | str | Unset):
        rejected_reason (None | str | Unset):
    """

    status: None | str | Unset = UNSET
    user_note: None | str | Unset = UNSET
    rejected_reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        user_note: None | str | Unset
        if isinstance(self.user_note, Unset):
            user_note = UNSET
        else:
            user_note = self.user_note

        rejected_reason: None | str | Unset
        if isinstance(self.rejected_reason, Unset):
            rejected_reason = UNSET
        else:
            rejected_reason = self.rejected_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if user_note is not UNSET:
            field_dict["user_note"] = user_note
        if rejected_reason is not UNSET:
            field_dict["rejected_reason"] = rejected_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_user_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_note = _parse_user_note(d.pop("user_note", UNSET))

        def _parse_rejected_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rejected_reason = _parse_rejected_reason(d.pop("rejected_reason", UNSET))

        learning_capture_update_request = cls(
            status=status,
            user_note=user_note,
            rejected_reason=rejected_reason,
        )

        learning_capture_update_request.additional_properties = d
        return learning_capture_update_request

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
