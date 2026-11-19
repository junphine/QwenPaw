from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="StarterPrompt")


@_attrs_define
class StarterPrompt:
    """
    Attributes:
        label (str):
        prompt (str):
    """

    label: str
    prompt: str

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        prompt = self.prompt

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "label": label,
                "prompt": prompt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        prompt = d.pop("prompt")

        starter_prompt = cls(
            label=label,
            prompt=prompt,
        )

        return starter_prompt
