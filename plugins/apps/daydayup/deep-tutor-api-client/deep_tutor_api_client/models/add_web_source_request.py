from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddWebSourceRequest")


@_attrs_define
class AddWebSourceRequest:
    """
    Attributes:
        url (str):
        max_depth (int | Unset):  Default: 3.
        max_pages (int | Unset):  Default: 200.
    """

    url: str
    max_depth: int | Unset = 3
    max_pages: int | Unset = 200
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        max_depth = self.max_depth

        max_pages = self.max_pages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )
        if max_depth is not UNSET:
            field_dict["max_depth"] = max_depth
        if max_pages is not UNSET:
            field_dict["max_pages"] = max_pages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        max_depth = d.pop("max_depth", UNSET)

        max_pages = d.pop("max_pages", UNSET)

        add_web_source_request = cls(
            url=url,
            max_depth=max_depth,
            max_pages=max_pages,
        )

        add_web_source_request.additional_properties = d
        return add_web_source_request

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
