from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.apply_ops_request_ops_item import ApplyOpsRequestOpsItem


T = TypeVar("T", bound="ApplyOpsRequest")


@_attrs_define
class ApplyOpsRequest:
    """
    Attributes:
        ops (list[ApplyOpsRequestOpsItem]):
    """

    ops: list[ApplyOpsRequestOpsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ops = []
        for ops_item_data in self.ops:
            ops_item = ops_item_data.to_dict()
            ops.append(ops_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ops": ops,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.apply_ops_request_ops_item import ApplyOpsRequestOpsItem  # noqa: PLC0415

        d = dict(src_dict)
        ops = []
        _ops = d.pop("ops")
        for ops_item_data in _ops:
            ops_item = ApplyOpsRequestOpsItem.from_dict(ops_item_data)

            ops.append(ops_item)

        apply_ops_request = cls(
            ops=ops,
        )

        apply_ops_request.additional_properties = d
        return apply_ops_request

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
