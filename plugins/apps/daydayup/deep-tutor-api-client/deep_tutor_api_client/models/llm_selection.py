from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LLMSelection")


@_attrs_define
class LLMSelection:
    """
    Attributes:
        profile_id (str):
        model_id (str):
        reasoning_effort (None | str | Unset):
    """

    profile_id: str
    model_id: str
    reasoning_effort: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        model_id = self.model_id

        reasoning_effort: None | str | Unset
        if isinstance(self.reasoning_effort, Unset):
            reasoning_effort = UNSET
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

        def _parse_reasoning_effort(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reasoning_effort = _parse_reasoning_effort(d.pop("reasoning_effort", UNSET))

        llm_selection = cls(
            profile_id=profile_id,
            model_id=model_id,
            reasoning_effort=reasoning_effort,
        )

        return llm_selection
