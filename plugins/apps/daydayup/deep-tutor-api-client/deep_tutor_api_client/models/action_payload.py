from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ActionPayload")


@_attrs_define
class ActionPayload:
    """
    Attributes:
        locator (int):
        selection (str | Unset):  Default: ''.
        locale (str | Unset):  Default: 'en'.
        question_id (str | Unset):  Default: ''.
        help_request_id (str | Unset):  Default: ''.
    """

    locator: int
    selection: str | Unset = ""
    locale: str | Unset = "en"
    question_id: str | Unset = ""
    help_request_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locator = self.locator

        selection = self.selection

        locale = self.locale

        question_id = self.question_id

        help_request_id = self.help_request_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
            }
        )
        if selection is not UNSET:
            field_dict["selection"] = selection
        if locale is not UNSET:
            field_dict["locale"] = locale
        if question_id is not UNSET:
            field_dict["question_id"] = question_id
        if help_request_id is not UNSET:
            field_dict["help_request_id"] = help_request_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        locator = d.pop("locator")

        selection = d.pop("selection", UNSET)

        locale = d.pop("locale", UNSET)

        question_id = d.pop("question_id", UNSET)

        help_request_id = d.pop("help_request_id", UNSET)

        action_payload = cls(
            locator=locator,
            selection=selection,
            locale=locale,
            question_id=question_id,
            help_request_id=help_request_id,
        )

        action_payload.additional_properties = d
        return action_payload

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
