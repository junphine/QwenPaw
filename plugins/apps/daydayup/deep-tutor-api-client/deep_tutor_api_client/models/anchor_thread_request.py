from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.anchor_thread_request_origin import AnchorThreadRequestOrigin, check_anchor_thread_request_origin
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnchorThreadRequest")


@_attrs_define
class AnchorThreadRequest:
    """
    Attributes:
        session_id (str):
        block_id (str):
        quote (str | Unset):  Default: ''.
        origin (AnchorThreadRequestOrigin | Unset):  Default: 'ask'.
    """

    session_id: str
    block_id: str
    quote: str | Unset = ""
    origin: AnchorThreadRequestOrigin | Unset = "ask"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        block_id = self.block_id

        quote = self.quote

        origin: str | Unset = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session_id": session_id,
                "block_id": block_id,
            }
        )
        if quote is not UNSET:
            field_dict["quote"] = quote
        if origin is not UNSET:
            field_dict["origin"] = origin

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_id = d.pop("session_id")

        block_id = d.pop("block_id")

        quote = d.pop("quote", UNSET)

        _origin = d.pop("origin", UNSET)
        origin: AnchorThreadRequestOrigin | Unset
        if isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = check_anchor_thread_request_origin(_origin)

        anchor_thread_request = cls(
            session_id=session_id,
            block_id=block_id,
            quote=quote,
            origin=origin,
        )

        anchor_thread_request.additional_properties = d
        return anchor_thread_request

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
