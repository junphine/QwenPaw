from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadingReference")


@_attrs_define
class ReadingReference:
    """
    Attributes:
        material_id (str):
        revision (int):
        locators (list[int] | Unset):
    """

    material_id: str
    revision: int
    locators: list[int] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        material_id = self.material_id

        revision = self.revision

        locators: list[int] | Unset = UNSET
        if not isinstance(self.locators, Unset):
            locators = self.locators

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "material_id": material_id,
                "revision": revision,
            }
        )
        if locators is not UNSET:
            field_dict["locators"] = locators

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        material_id = d.pop("material_id")

        revision = d.pop("revision")

        locators = cast(list[int], d.pop("locators", UNSET))

        reading_reference = cls(
            material_id=material_id,
            revision=revision,
            locators=locators,
        )

        return reading_reference
