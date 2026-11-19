from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.react_edit_request_mode import ReactEditRequestMode, check_react_edit_request_mode
from ..models.react_edit_request_tools_item import ReactEditRequestToolsItem, check_react_edit_request_tools_item
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.llm_selection_payload import LLMSelectionPayload


T = TypeVar("T", bound="ReactEditRequest")


@_attrs_define
class ReactEditRequest:
    """
    Attributes:
        selected_text (str):
        instruction (str | Unset):  Default: ''.
        mode (ReactEditRequestMode | Unset):  Default: 'rewrite'.
        tools (list[ReactEditRequestToolsItem] | Unset):
        kb_name (None | str | Unset):
        llm_selection (LLMSelectionPayload | None | Unset):
    """

    selected_text: str
    instruction: str | Unset = ""
    mode: ReactEditRequestMode | Unset = "rewrite"
    tools: list[ReactEditRequestToolsItem] | Unset = UNSET
    kb_name: None | str | Unset = UNSET
    llm_selection: LLMSelectionPayload | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        selected_text = self.selected_text

        instruction = self.instruction

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode

        tools: list[str] | Unset = UNSET
        if not isinstance(self.tools, Unset):
            tools = []
            for tools_item_data in self.tools:
                tools_item: str = tools_item_data
                tools.append(tools_item)

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
                "selected_text": selected_text,
            }
        )
        if instruction is not UNSET:
            field_dict["instruction"] = instruction
        if mode is not UNSET:
            field_dict["mode"] = mode
        if tools is not UNSET:
            field_dict["tools"] = tools
        if kb_name is not UNSET:
            field_dict["kb_name"] = kb_name
        if llm_selection is not UNSET:
            field_dict["llm_selection"] = llm_selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.llm_selection_payload import LLMSelectionPayload  # noqa: PLC0415

        d = dict(src_dict)
        selected_text = d.pop("selected_text")

        instruction = d.pop("instruction", UNSET)

        _mode = d.pop("mode", UNSET)
        mode: ReactEditRequestMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_react_edit_request_mode(_mode)

        _tools = d.pop("tools", UNSET)
        tools: list[ReactEditRequestToolsItem] | Unset = UNSET
        if _tools is not UNSET:
            tools = []
            for tools_item_data in _tools:
                tools_item = check_react_edit_request_tools_item(tools_item_data)

                tools.append(tools_item)

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

        react_edit_request = cls(
            selected_text=selected_text,
            instruction=instruction,
            mode=mode,
            tools=tools,
            kb_name=kb_name,
            llm_selection=llm_selection,
        )

        react_edit_request.additional_properties = d
        return react_edit_request

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
