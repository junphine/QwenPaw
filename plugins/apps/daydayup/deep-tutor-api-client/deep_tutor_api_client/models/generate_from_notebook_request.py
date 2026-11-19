from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.notebook_record_input import NotebookRecordInput


T = TypeVar("T", bound="GenerateFromNotebookRequest")


@_attrs_define
class GenerateFromNotebookRequest:
    """
    Attributes:
        notebook_id (str):
        records (list[NotebookRecordInput]):
    """

    notebook_id: str
    records: list[NotebookRecordInput]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notebook_id = self.notebook_id

        records = []
        for records_item_data in self.records:
            records_item = records_item_data.to_dict()
            records.append(records_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notebook_id": notebook_id,
                "records": records,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notebook_record_input import NotebookRecordInput  # noqa: PLC0415

        d = dict(src_dict)
        notebook_id = d.pop("notebook_id")

        records = []
        _records = d.pop("records")
        for records_item_data in _records:
            records_item = NotebookRecordInput.from_dict(records_item_data)

            records.append(records_item)

        generate_from_notebook_request = cls(
            notebook_id=notebook_id,
            records=records,
        )

        generate_from_notebook_request.additional_properties = d
        return generate_from_notebook_request

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
