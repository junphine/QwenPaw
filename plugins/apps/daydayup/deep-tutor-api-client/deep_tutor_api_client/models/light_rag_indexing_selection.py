from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.light_rag_indexing_vision import LightRagIndexingVision
    from ..models.light_rag_model_selection import LightRagModelSelection


T = TypeVar("T", bound="LightRagIndexingSelection")


@_attrs_define
class LightRagIndexingSelection:
    """Resolved create/rebuild overrides, without mutable engine inheritance.

    Attributes:
        extract (LightRagModelSelection): Identify a catalog model and its optional reasoning selection.
        vlm (LightRagIndexingVision | Unset): Represent an explicitly enabled or disabled indexing vision model.
    """

    extract: LightRagModelSelection
    vlm: LightRagIndexingVision | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        extract = self.extract.to_dict()

        vlm: dict[str, Any] | Unset = UNSET
        if not isinstance(self.vlm, Unset):
            vlm = self.vlm.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "extract": extract,
            }
        )
        if vlm is not UNSET:
            field_dict["vlm"] = vlm

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.light_rag_indexing_vision import LightRagIndexingVision  # noqa: PLC0415
        from ..models.light_rag_model_selection import LightRagModelSelection  # noqa: PLC0415

        d = dict(src_dict)
        extract = LightRagModelSelection.from_dict(d.pop("extract"))

        _vlm = d.pop("vlm", UNSET)
        vlm: LightRagIndexingVision | Unset
        if isinstance(_vlm, Unset):
            vlm = UNSET
        else:
            vlm = LightRagIndexingVision.from_dict(_vlm)

        light_rag_indexing_selection = cls(
            extract=extract,
            vlm=vlm,
        )

        return light_rag_indexing_selection
