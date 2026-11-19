from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BilingualPairingInfo")


@_attrs_define
class BilingualPairingInfo:
    """
    Attributes:
        pairing_id (str):
        source_url (str):
        target_url (str):
        source_file (str | Unset):  Default: ''.
        target_file (str | Unset):  Default: ''.
        source_lang (str | Unset):  Default: ''.
        target_lang (str | Unset):  Default: ''.
        pairing_method (str | Unset):  Default: 'hreflang'.
        updated_at (int | Unset):  Default: 0.
    """

    pairing_id: str
    source_url: str
    target_url: str
    source_file: str | Unset = ""
    target_file: str | Unset = ""
    source_lang: str | Unset = ""
    target_lang: str | Unset = ""
    pairing_method: str | Unset = "hreflang"
    updated_at: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pairing_id = self.pairing_id

        source_url = self.source_url

        target_url = self.target_url

        source_file = self.source_file

        target_file = self.target_file

        source_lang = self.source_lang

        target_lang = self.target_lang

        pairing_method = self.pairing_method

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pairing_id": pairing_id,
                "source_url": source_url,
                "target_url": target_url,
            }
        )
        if source_file is not UNSET:
            field_dict["source_file"] = source_file
        if target_file is not UNSET:
            field_dict["target_file"] = target_file
        if source_lang is not UNSET:
            field_dict["source_lang"] = source_lang
        if target_lang is not UNSET:
            field_dict["target_lang"] = target_lang
        if pairing_method is not UNSET:
            field_dict["pairing_method"] = pairing_method
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pairing_id = d.pop("pairing_id")

        source_url = d.pop("source_url")

        target_url = d.pop("target_url")

        source_file = d.pop("source_file", UNSET)

        target_file = d.pop("target_file", UNSET)

        source_lang = d.pop("source_lang", UNSET)

        target_lang = d.pop("target_lang", UNSET)

        pairing_method = d.pop("pairing_method", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        bilingual_pairing_info = cls(
            pairing_id=pairing_id,
            source_url=source_url,
            target_url=target_url,
            source_file=source_file,
            target_file=target_file,
            source_lang=source_lang,
            target_lang=target_lang,
            pairing_method=pairing_method,
            updated_at=updated_at,
        )

        bilingual_pairing_info.additional_properties = d
        return bilingual_pairing_info

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
