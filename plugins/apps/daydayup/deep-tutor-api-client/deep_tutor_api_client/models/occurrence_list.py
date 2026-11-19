from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.occurrence import Occurrence


T = TypeVar("T", bound="OccurrenceList")


@_attrs_define
class OccurrenceList:
    """
    Attributes:
        occurrences (list[Occurrence]):
        revision (int):
    """

    occurrences: list[Occurrence]
    revision: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        occurrences = []
        for occurrences_item_data in self.occurrences:
            occurrences_item = occurrences_item_data.to_dict()
            occurrences.append(occurrences_item)

        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "occurrences": occurrences,
                "revision": revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.occurrence import Occurrence  # noqa: PLC0415

        d = dict(src_dict)
        occurrences = []
        _occurrences = d.pop("occurrences")
        for occurrences_item_data in _occurrences:
            occurrences_item = Occurrence.from_dict(occurrences_item_data)

            occurrences.append(occurrences_item)

        revision = d.pop("revision")

        occurrence_list = cls(
            occurrences=occurrences,
            revision=revision,
        )

        occurrence_list.additional_properties = d
        return occurrence_list

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
