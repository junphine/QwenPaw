from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_attachment_request import ChatAttachmentRequest
    from ..models.chat_message_request_llm_selection_type_0 import ChatMessageRequestLlmSelectionType0


T = TypeVar("T", bound="ChatMessageRequest")


@_attrs_define
class ChatMessageRequest:
    """
    Attributes:
        content (str | Unset):  Default: ''.
        session_id (None | str | Unset):
        session_key (None | str | Unset):
        chat_id (None | str | Unset):
        attachments (list[ChatAttachmentRequest] | Unset):
        llm_selection (ChatMessageRequestLlmSelectionType0 | None | Unset):
    """

    content: str | Unset = ""
    session_id: None | str | Unset = UNSET
    session_key: None | str | Unset = UNSET
    chat_id: None | str | Unset = UNSET
    attachments: list[ChatAttachmentRequest] | Unset = UNSET
    llm_selection: ChatMessageRequestLlmSelectionType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.chat_message_request_llm_selection_type_0 import (
            ChatMessageRequestLlmSelectionType0,  # noqa: PLC0415
        )

        content = self.content

        session_id: None | str | Unset
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        else:
            session_id = self.session_id

        session_key: None | str | Unset
        if isinstance(self.session_key, Unset):
            session_key = UNSET
        else:
            session_key = self.session_key

        chat_id: None | str | Unset
        if isinstance(self.chat_id, Unset):
            chat_id = UNSET
        else:
            chat_id = self.chat_id

        attachments: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.llm_selection, Unset):
            llm_selection = UNSET
        elif isinstance(self.llm_selection, ChatMessageRequestLlmSelectionType0):
            llm_selection = self.llm_selection.to_dict()
        else:
            llm_selection = self.llm_selection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if session_key is not UNSET:
            field_dict["session_key"] = session_key
        if chat_id is not UNSET:
            field_dict["chat_id"] = chat_id
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if llm_selection is not UNSET:
            field_dict["llmSelection"] = llm_selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_attachment_request import ChatAttachmentRequest  # noqa: PLC0415
        from ..models.chat_message_request_llm_selection_type_0 import (
            ChatMessageRequestLlmSelectionType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        content = d.pop("content", UNSET)

        def _parse_session_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        session_id = _parse_session_id(d.pop("session_id", UNSET))

        def _parse_session_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        session_key = _parse_session_key(d.pop("session_key", UNSET))

        def _parse_chat_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        chat_id = _parse_chat_id(d.pop("chat_id", UNSET))

        _attachments = d.pop("attachments", UNSET)
        attachments: list[ChatAttachmentRequest] | Unset = UNSET
        if _attachments is not UNSET:
            attachments = []
            for attachments_item_data in _attachments:
                attachments_item = ChatAttachmentRequest.from_dict(attachments_item_data)

                attachments.append(attachments_item)

        def _parse_llm_selection(data: object) -> ChatMessageRequestLlmSelectionType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                llm_selection_type_0 = ChatMessageRequestLlmSelectionType0.from_dict(data)

                return llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChatMessageRequestLlmSelectionType0 | None | Unset, data)

        llm_selection = _parse_llm_selection(d.pop("llmSelection", UNSET))

        chat_message_request = cls(
            content=content,
            session_id=session_id,
            session_key=session_key,
            chat_id=chat_id,
            attachments=attachments,
            llm_selection=llm_selection,
        )

        chat_message_request.additional_properties = d
        return chat_message_request

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
