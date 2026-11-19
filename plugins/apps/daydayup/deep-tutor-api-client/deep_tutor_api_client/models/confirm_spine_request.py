from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.confirm_spine_request_spine_type_0 import ConfirmSpineRequestSpineType0


T = TypeVar("T", bound="ConfirmSpineRequest")


@_attrs_define
class ConfirmSpineRequest:
    """
    Attributes:
        book_id (str):
        spine (ConfirmSpineRequestSpineType0 | None | Unset):
        auto_compile (bool | Unset):  Default: True.
        block_types (list[str] | None | Unset):
        expected_revision (int | None | Unset):
    """

    book_id: str
    spine: ConfirmSpineRequestSpineType0 | None | Unset = UNSET
    auto_compile: bool | Unset = True
    block_types: list[str] | None | Unset = UNSET
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.confirm_spine_request_spine_type_0 import ConfirmSpineRequestSpineType0  # noqa: PLC0415

        book_id = self.book_id

        spine: dict[str, Any] | None | Unset
        if isinstance(self.spine, Unset):
            spine = UNSET
        elif isinstance(self.spine, ConfirmSpineRequestSpineType0):
            spine = self.spine.to_dict()
        else:
            spine = self.spine

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
        if spine is not UNSET:
            field_dict["spine"] = spine
        if auto_compile is not UNSET:
            field_dict["auto_compile"] = auto_compile
        if block_types is not UNSET:
            field_dict["block_types"] = block_types
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.confirm_spine_request_spine_type_0 import ConfirmSpineRequestSpineType0  # noqa: PLC0415

        d = dict(src_dict)
        book_id = d.pop("book_id")

        def _parse_spine(data: object) -> ConfirmSpineRequestSpineType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                spine_type_0 = ConfirmSpineRequestSpineType0.from_dict(data)

                return spine_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ConfirmSpineRequestSpineType0 | None | Unset, data)

        spine = _parse_spine(d.pop("spine", UNSET))

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

        confirm_spine_request = cls(
            book_id=book_id,
            spine=spine,
            auto_compile=auto_compile,
            block_types=block_types,
            expected_revision=expected_revision,
        )

        confirm_spine_request.additional_properties = d
        return confirm_spine_request

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
