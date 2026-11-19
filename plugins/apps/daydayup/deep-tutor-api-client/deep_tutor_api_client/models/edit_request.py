from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.edit_request_action import EditRequestAction, check_edit_request_action
from ..models.edit_request_source_type_0 import EditRequestSourceType0, check_edit_request_source_type_0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.llm_selection_payload import LLMSelectionPayload


T = TypeVar("T", bound="EditRequest")


@_attrs_define
class EditRequest:
    """
    Attributes:
        text (str):
        instruction (str):
        action (EditRequestAction | Unset):  Default: 'rewrite'.
        source (EditRequestSourceType0 | None | Unset):
        kb_name (None | str | Unset):
        llm_selection (LLMSelectionPayload | None | Unset):
    """

    text: str
    instruction: str
    action: EditRequestAction | Unset = "rewrite"
    source: EditRequestSourceType0 | None | Unset = UNSET
    kb_name: None | str | Unset = UNSET
    llm_selection: LLMSelectionPayload | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        text = self.text

        instruction = self.instruction

        action: str | Unset = UNSET
        if not isinstance(self.action, Unset):
            action = self.action

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        elif isinstance(self.source, str):
            source = self.source
        else:
            source = self.source

        kb_name: None | str | Unset
        if isinstance(self.kb_name, Unset):
            kb_name = UNSET
        else:
            kb_name = self.kb_name

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
                "instruction": instruction,
            }
        )
        if action is not UNSET:
            field_dict["action"] = action
        if source is not UNSET:
            field_dict["source"] = source
        if kb_name is not UNSET:
            field_dict["kb_name"] = kb_name
        if llm_selection is not UNSET:
            field_dict["llm_selection"] = llm_selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        d = dict(src_dict)
        text = d.pop("text")

        instruction = d.pop("instruction")

        _action = d.pop("action", UNSET)
        action: EditRequestAction | Unset
        if isinstance(_action, Unset):
            action = UNSET
        else:
            action = check_edit_request_action(_action)

        def _parse_source(data: object) -> EditRequestSourceType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_type_0 = check_edit_request_source_type_0(data)

                return source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EditRequestSourceType0 | None | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        def _parse_kb_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kb_name = _parse_kb_name(d.pop("kb_name", UNSET))

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

        edit_request = cls(
            text=text,
            instruction=instruction,
            action=action,
            source=source,
            kb_name=kb_name,
            llm_selection=llm_selection,
        )

        edit_request.additional_properties = d
        return edit_request

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
