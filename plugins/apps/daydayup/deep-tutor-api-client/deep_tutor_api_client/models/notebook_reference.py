from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotebookReference")


@_attrs_define
class NotebookReference:
    """
    Attributes:
        notebook_id (str):
        record_ids (list[str] | Unset):
    """

    notebook_id: str
    record_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        notebook_id = self.notebook_id

        record_ids: list[str] | Unset = UNSET
        if not isinstance(self.record_ids, Unset):
            record_ids = self.record_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "notebook_id": notebook_id,
            }
        )
        if record_ids is not UNSET:
            field_dict["record_ids"] = record_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        notebook_id = d.pop("notebook_id")

        record_ids = cast(list[str], d.pop("record_ids", UNSET))

        notebook_reference = cls(
            notebook_id=notebook_id,
            record_ids=record_ids,
        )

        return notebook_reference
