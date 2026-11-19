from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.light_rag_vision_model_mode import LightRagVisionModelMode, check_light_rag_vision_model_mode
from ..models.light_rag_vision_model_reasoning_effort_type_0 import (
    LightRagVisionModelReasoningEffortType0,
    check_light_rag_vision_model_reasoning_effort_type_0,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.light_rag_model_selection import LightRagModelSelection


T = TypeVar("T", bound="LightRagVisionModel")


@_attrs_define
class LightRagVisionModel:
    """Configure disabled, inherited, or explicit vision model execution.

    Attributes:
        mode (LightRagVisionModelMode | Unset):  Default: 'disabled'.
        selection (LightRagModelSelection | None | Unset):
        reasoning_effort (LightRagVisionModelReasoningEffortType0 | None | Unset):
        max_async (int | Unset):  Default: 4.
        timeout (int | Unset):  Default: 240.
    """

    mode: LightRagVisionModelMode | Unset = "disabled"
    selection: LightRagModelSelection | None | Unset = UNSET
    reasoning_effort: LightRagVisionModelReasoningEffortType0 | None | Unset = UNSET
    max_async: int | Unset = 4
    timeout: int | Unset = 240

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

        reasoning_effort: None | str | Unset
        if isinstance(self.reasoning_effort, Unset):
            reasoning_effort = UNSET
        elif isinstance(self.reasoning_effort, str):
            reasoning_effort = self.reasoning_effort
        else:
            reasoning_effort = self.reasoning_effort

        max_async = self.max_async

        timeout = self.timeout

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if selection is not UNSET:
            field_dict["selection"] = selection
        if reasoning_effort is not UNSET:
            field_dict["reasoning_effort"] = reasoning_effort
        if max_async is not UNSET:
            field_dict["max_async"] = max_async
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.light_rag_model_selection import LightRagModelSelection  # noqa: PLC0415

        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: LightRagVisionModelMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_light_rag_vision_model_mode(_mode)

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

        def _parse_reasoning_effort(data: object) -> LightRagVisionModelReasoningEffortType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reasoning_effort_type_0 = check_light_rag_vision_model_reasoning_effort_type_0(data)

                return reasoning_effort_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LightRagVisionModelReasoningEffortType0 | None | Unset, data)

        reasoning_effort = _parse_reasoning_effort(d.pop("reasoning_effort", UNSET))

        max_async = d.pop("max_async", UNSET)

        timeout = d.pop("timeout", UNSET)

        light_rag_vision_model = cls(
            mode=mode,
            selection=selection,
            reasoning_effort=reasoning_effort,
            max_async=max_async,
            timeout=timeout,
        )

        return light_rag_vision_model
