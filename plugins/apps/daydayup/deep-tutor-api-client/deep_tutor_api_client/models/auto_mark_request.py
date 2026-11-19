from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.llm_selection_payload import LLMSelectionPayload


T = TypeVar("T", bound="AutoMarkRequest")


@_attrs_define
class AutoMarkRequest:
    """
    Attributes:
        text (str):
        llm_selection (LLMSelectionPayload | None | Unset):
    """

    text: str
    llm_selection: LLMSelectionPayload | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        text = self.text

        llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.llm_selection, Unset):
            llm_selection = UNSET
        elif isinstance(self.llm_selection, LLMSelectionPayload):
            llm_selection = self.llm_selection.to_dict()
        else:
            llm_selection = self.llm_selection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
            }
        )
        if llm_selection is not UNSET:
            field_dict["llm_selection"] = llm_selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        d = dict(src_dict)
        text = d.pop("text")

        def _parse_llm_selection(data: object) -> LLMSelectionPayload | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                llm_selection_type_0 = LLMSelectionPayload.from_dict(data)

                return llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LLMSelectionPayload | None | Unset, data)

        llm_selection = _parse_llm_selection(d.pop("llm_selection", UNSET))

        auto_mark_request = cls(
            text=text,
            llm_selection=llm_selection,
        )

        auto_mark_request.additional_properties = d
        return auto_mark_request

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
