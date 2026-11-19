from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RebuildBookRequest")


@_attrs_define
class RebuildBookRequest:
    """
    Attributes:
        book_id (str):
        auto_compile (bool | Unset):  Default: True.
        block_types (list[str] | None | Unset):
        expected_revision (int | None | Unset):
    """

    book_id: str
    auto_compile: bool | Unset = True
    block_types: list[str] | None | Unset = UNSET
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        book_id = self.book_id

        auto_compile = self.auto_compile

        block_types: list[str] | None | Unset
        if isinstance(self.block_types, Unset):
            block_types = UNSET
        elif isinstance(self.block_types, list):
            block_types = self.block_types

        else:
            block_types = self.block_types

        expected_revision: int | None | Unset
        if isinstance(self.expected_revision, Unset):
            expected_revision = UNSET
        else:
            expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "book_id": book_id,
            }
        )
        if auto_compile is not UNSET:
            field_dict["auto_compile"] = auto_compile
        if block_types is not UNSET:
            field_dict["block_types"] = block_types
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        book_id = d.pop("book_id")

        auto_compile = d.pop("auto_compile", UNSET)

        def _parse_block_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                block_types_type_0 = cast(list[str], data)

                return block_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        block_types = _parse_block_types(d.pop("block_types", UNSET))

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        rebuild_book_request = cls(
            book_id=book_id,
            auto_compile=auto_compile,
            block_types=block_types,
            expected_revision=expected_revision,
        )

        rebuild_book_request.additional_properties = d
        return rebuild_book_request

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
