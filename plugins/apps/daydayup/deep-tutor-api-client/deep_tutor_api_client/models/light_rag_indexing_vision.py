from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.light_rag_indexing_vision_mode import LightRagIndexingVisionMode, check_light_rag_indexing_vision_mode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.light_rag_model_selection import LightRagModelSelection


T = TypeVar("T", bound="LightRagIndexingVision")


@_attrs_define
class LightRagIndexingVision:
    """Represent an explicitly enabled or disabled indexing vision model.

    Attributes:
        mode (LightRagIndexingVisionMode | Unset):  Default: 'disabled'.
        selection (LightRagModelSelection | None | Unset):
    """

    mode: LightRagIndexingVisionMode | Unset = "disabled"
    selection: LightRagModelSelection | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.light_rag_model_selection import LightRagModelSelection  # noqa: PLC0415

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode

        selection: dict[str, Any] | None | Unset
        if isinstance(self.selection, Unset):
            selection = UNSET
        elif isinstance(self.selection, LightRagModelSelection):
            selection = self.selection.to_dict()
        else:
            selection = self.selection

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if selection is not UNSET:
            field_dict["selection"] = selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.light_rag_model_selection import LightRagModelSelection  # noqa: PLC0415

        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: LightRagIndexingVisionMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_light_rag_indexing_vision_mode(_mode)

        def _parse_selection(data: object) -> LightRagModelSelection | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                selection_type_0 = LightRagModelSelection.from_dict(data)

                return selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LightRagModelSelection | None | Unset, data)

        selection = _parse_selection(d.pop("selection", UNSET))

        light_rag_indexing_vision = cls(
            mode=mode,
            selection=selection,
        )

        return light_rag_indexing_vision
