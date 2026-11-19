from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.light_rag_model_selection_reasoning_effort_type_0 import (
    LightRagModelSelectionReasoningEffortType0,
    check_light_rag_model_selection_reasoning_effort_type_0,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LightRagModelSelection")


@_attrs_define
class LightRagModelSelection:
    """Identify a catalog model and its optional reasoning selection.

    Attributes:
        profile_id (str):
        model_id (str):
        reasoning_effort (LightRagModelSelectionReasoningEffortType0 | None | Unset):
    """

    profile_id: str
    model_id: str
    reasoning_effort: LightRagModelSelectionReasoningEffortType0 | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        model_id = self.model_id

        reasoning_effort: None | str | Unset
        if isinstance(self.reasoning_effort, Unset):
            reasoning_effort = UNSET
        elif isinstance(self.reasoning_effort, str):
            reasoning_effort = self.reasoning_effort
        else:
            reasoning_effort = self.reasoning_effort

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "profile_id": profile_id,
                "model_id": model_id,
            }
        )
        if reasoning_effort is not UNSET:
            field_dict["reasoning_effort"] = reasoning_effort

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        profile_id = d.pop("profile_id")

        model_id = d.pop("model_id")

        def _parse_reasoning_effort(data: object) -> LightRagModelSelectionReasoningEffortType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reasoning_effort_type_0 = check_light_rag_model_selection_reasoning_effort_type_0(data)

                return reasoning_effort_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LightRagModelSelectionReasoningEffortType0 | None | Unset, data)

        reasoning_effort = _parse_reasoning_effort(d.pop("reasoning_effort", UNSET))

        light_rag_model_selection = cls(
            profile_id=profile_id,
            model_id=model_id,
            reasoning_effort=reasoning_effort,
        )

        return light_rag_model_selection
