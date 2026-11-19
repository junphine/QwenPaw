from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TextQuoteSelectorPayload")


@_attrs_define
class TextQuoteSelectorPayload:
    """
    Attributes:
        type_ (Literal['TextQuoteSelector']):
        exact (str):
        prefix (str | Unset):  Default: ''.
        suffix (str | Unset):  Default: ''.
    """

    type_: Literal["TextQuoteSelector"]
    exact: str
    prefix: str | Unset = ""
    suffix: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        exact = self.exact

        prefix = self.prefix

        suffix = self.suffix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "exact": exact,
            }
        )
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if suffix is not UNSET:
            field_dict["suffix"] = suffix

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["TextQuoteSelector"], d.pop("type"))
        if type_ != "TextQuoteSelector":
            raise ValueError(f"type must match const 'TextQuoteSelector', got '{type_}'")

        exact = d.pop("exact")

        prefix = d.pop("prefix", UNSET)

        suffix = d.pop("suffix", UNSET)

        text_quote_selector_payload = cls(
            type_=type_,
            exact=exact,
            prefix=prefix,
            suffix=suffix,
        )

        text_quote_selector_payload.additional_properties = d
        return text_quote_selector_payload

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
