from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.change_block_type_request_params_override_type_0 import ChangeBlockTypeRequestParamsOverrideType0


T = TypeVar("T", bound="ChangeBlockTypeRequest")


@_attrs_define
class ChangeBlockTypeRequest:
    """
    Attributes:
        book_id (str):
        page_id (str):
        block_id (str):
        new_type (str):
        params_override (ChangeBlockTypeRequestParamsOverrideType0 | None | Unset):
        expected_revision (int | None | Unset):
    """

    book_id: str
    page_id: str
    block_id: str
    new_type: str
    params_override: ChangeBlockTypeRequestParamsOverrideType0 | None | Unset = UNSET
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.change_block_type_request_params_override_type_0 import (
            ChangeBlockTypeRequestParamsOverrideType0,  # noqa: PLC0415
        )

        book_id = self.book_id

        page_id = self.page_id

        block_id = self.block_id

        new_type = self.new_type

        params_override: dict[str, Any] | None | Unset
        if isinstance(self.params_override, Unset):
            params_override = UNSET
        elif isinstance(self.params_override, ChangeBlockTypeRequestParamsOverrideType0):
            params_override = self.params_override.to_dict()
        else:
            params_override = self.params_override

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
                "page_id": page_id,
                "block_id": block_id,
                "new_type": new_type,
            }
        )
        if params_override is not UNSET:
            field_dict["params_override"] = params_override
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.change_block_type_request_params_override_type_0 import (
            ChangeBlockTypeRequestParamsOverrideType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        book_id = d.pop("book_id")

        page_id = d.pop("page_id")

        block_id = d.pop("block_id")

        new_type = d.pop("new_type")

        def _parse_params_override(data: object) -> ChangeBlockTypeRequestParamsOverrideType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_override_type_0 = ChangeBlockTypeRequestParamsOverrideType0.from_dict(data)

                return params_override_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChangeBlockTypeRequestParamsOverrideType0 | None | Unset, data)

        params_override = _parse_params_override(d.pop("params_override", UNSET))

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        change_block_type_request = cls(
            book_id=book_id,
            page_id=page_id,
            block_id=block_id,
            new_type=new_type,
            params_override=params_override,
            expected_revision=expected_revision,
        )

        change_block_type_request.additional_properties = d
        return change_block_type_request

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
