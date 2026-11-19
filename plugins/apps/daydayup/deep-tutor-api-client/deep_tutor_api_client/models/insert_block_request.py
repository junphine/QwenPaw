from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.insert_block_request_params_type_0 import InsertBlockRequestParamsType0


T = TypeVar("T", bound="InsertBlockRequest")


@_attrs_define
class InsertBlockRequest:
    """
    Attributes:
        book_id (str):
        page_id (str):
        block_type (str):
        params (InsertBlockRequestParamsType0 | None | Unset):
        position (int | None | Unset):
        compile_now (bool | Unset):  Default: True.
        expected_revision (int | None | Unset):
    """

    book_id: str
    page_id: str
    block_type: str
    params: InsertBlockRequestParamsType0 | None | Unset = UNSET
    position: int | None | Unset = UNSET
    compile_now: bool | Unset = True
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.insert_block_request_params_type_0 import InsertBlockRequestParamsType0  # noqa: PLC0415

        book_id = self.book_id

        page_id = self.page_id

        block_type = self.block_type

        params: dict[str, Any] | None | Unset
        if isinstance(self.params, Unset):
            params = UNSET
        elif isinstance(self.params, InsertBlockRequestParamsType0):
            params = self.params.to_dict()
        else:
            params = self.params

        position: int | None | Unset
        if isinstance(self.position, Unset):
            position = UNSET
        else:
            position = self.position

        compile_now = self.compile_now

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
                "block_type": block_type,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params
        if position is not UNSET:
            field_dict["position"] = position
        if compile_now is not UNSET:
            field_dict["compile_now"] = compile_now
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.insert_block_request_params_type_0 import InsertBlockRequestParamsType0  # noqa: PLC0415

        d = dict(src_dict)
        book_id = d.pop("book_id")

        page_id = d.pop("page_id")

        block_type = d.pop("block_type")

        def _parse_params(data: object) -> InsertBlockRequestParamsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = InsertBlockRequestParamsType0.from_dict(data)

                return params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(InsertBlockRequestParamsType0 | None | Unset, data)

        params = _parse_params(d.pop("params", UNSET))

        def _parse_position(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        position = _parse_position(d.pop("position", UNSET))

        compile_now = d.pop("compile_now", UNSET)

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        insert_block_request = cls(
            book_id=book_id,
            page_id=page_id,
            block_type=block_type,
            params=params,
            position=position,
            compile_now=compile_now,
            expected_revision=expected_revision,
        )

        insert_block_request.additional_properties = d
        return insert_block_request

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
