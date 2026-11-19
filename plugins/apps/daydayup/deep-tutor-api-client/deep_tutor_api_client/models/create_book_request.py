from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_book_request_chat_selections_item import CreateBookRequestChatSelectionsItem
    from ..models.create_book_request_notebook_refs_item import CreateBookRequestNotebookRefsItem
    from ..models.create_book_request_source_refs_item import CreateBookRequestSourceRefsItem


T = TypeVar("T", bound="CreateBookRequest")


@_attrs_define
class CreateBookRequest:
    """
    Attributes:
        source_refs (list[CreateBookRequestSourceRefsItem] | Unset):
        user_intent (str | Unset):  Default: ''.
        chat_session_id (str | Unset):  Default: ''.
        chat_selections (list[CreateBookRequestChatSelectionsItem] | Unset):
        notebook_refs (list[CreateBookRequestNotebookRefsItem] | Unset):
        knowledge_bases (list[str] | Unset):
        question_categories (list[int] | Unset):
        question_entries (list[int] | Unset):
        language (str | Unset):  Default: 'en'.
        fallback_language (str | Unset):  Default: 'en'.
        depth (str | Unset):  Default: 'standard'.
    """

    source_refs: list[CreateBookRequestSourceRefsItem] | Unset = UNSET
    user_intent: str | Unset = ""
    chat_session_id: str | Unset = ""
    chat_selections: list[CreateBookRequestChatSelectionsItem] | Unset = UNSET
    notebook_refs: list[CreateBookRequestNotebookRefsItem] | Unset = UNSET
    knowledge_bases: list[str] | Unset = UNSET
    question_categories: list[int] | Unset = UNSET
    question_entries: list[int] | Unset = UNSET
    language: str | Unset = "en"
    fallback_language: str | Unset = "en"
    depth: str | Unset = "standard"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_refs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.source_refs, Unset):
            source_refs = []
            for source_refs_item_data in self.source_refs:
                source_refs_item = source_refs_item_data.to_dict()
                source_refs.append(source_refs_item)

        user_intent = self.user_intent

        chat_session_id = self.chat_session_id

        chat_selections: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.chat_selections, Unset):
            chat_selections = []
            for chat_selections_item_data in self.chat_selections:
                chat_selections_item = chat_selections_item_data.to_dict()
                chat_selections.append(chat_selections_item)

        notebook_refs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.notebook_refs, Unset):
            notebook_refs = []
            for notebook_refs_item_data in self.notebook_refs:
                notebook_refs_item = notebook_refs_item_data.to_dict()
                notebook_refs.append(notebook_refs_item)

        knowledge_bases: list[str] | Unset = UNSET
        if not isinstance(self.knowledge_bases, Unset):
            knowledge_bases = self.knowledge_bases

        question_categories: list[int] | Unset = UNSET
        if not isinstance(self.question_categories, Unset):
            question_categories = self.question_categories

        question_entries: list[int] | Unset = UNSET
        if not isinstance(self.question_entries, Unset):
            question_entries = self.question_entries

        language = self.language

        fallback_language = self.fallback_language

        depth = self.depth

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source_refs is not UNSET:
            field_dict["source_refs"] = source_refs
        if user_intent is not UNSET:
            field_dict["user_intent"] = user_intent
        if chat_session_id is not UNSET:
            field_dict["chat_session_id"] = chat_session_id
        if chat_selections is not UNSET:
            field_dict["chat_selections"] = chat_selections
        if notebook_refs is not UNSET:
            field_dict["notebook_refs"] = notebook_refs
        if knowledge_bases is not UNSET:
            field_dict["knowledge_bases"] = knowledge_bases
        if question_categories is not UNSET:
            field_dict["question_categories"] = question_categories
        if question_entries is not UNSET:
            field_dict["question_entries"] = question_entries
        if language is not UNSET:
            field_dict["language"] = language
        if fallback_language is not UNSET:
            field_dict["fallback_language"] = fallback_language
        if depth is not UNSET:
            field_dict["depth"] = depth

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_book_request_chat_selections_item import (
            CreateBookRequestChatSelectionsItem,  # noqa: PLC0415
        )
        from ..models.create_book_request_notebook_refs_item import CreateBookRequestNotebookRefsItem  # noqa: PLC0415
        from ..models.create_book_request_source_refs_item import CreateBookRequestSourceRefsItem  # noqa: PLC0415

        d = dict(src_dict)
        _source_refs = d.pop("source_refs", UNSET)
        source_refs: list[CreateBookRequestSourceRefsItem] | Unset = UNSET
        if _source_refs is not UNSET:
            source_refs = []
            for source_refs_item_data in _source_refs:
                source_refs_item = CreateBookRequestSourceRefsItem.from_dict(source_refs_item_data)

                source_refs.append(source_refs_item)

        user_intent = d.pop("user_intent", UNSET)

        chat_session_id = d.pop("chat_session_id", UNSET)

        _chat_selections = d.pop("chat_selections", UNSET)
        chat_selections: list[CreateBookRequestChatSelectionsItem] | Unset = UNSET
        if _chat_selections is not UNSET:
            chat_selections = []
            for chat_selections_item_data in _chat_selections:
                chat_selections_item = CreateBookRequestChatSelectionsItem.from_dict(chat_selections_item_data)

                chat_selections.append(chat_selections_item)

        _notebook_refs = d.pop("notebook_refs", UNSET)
        notebook_refs: list[CreateBookRequestNotebookRefsItem] | Unset = UNSET
        if _notebook_refs is not UNSET:
            notebook_refs = []
            for notebook_refs_item_data in _notebook_refs:
                notebook_refs_item = CreateBookRequestNotebookRefsItem.from_dict(notebook_refs_item_data)

                notebook_refs.append(notebook_refs_item)

        knowledge_bases = cast(list[str], d.pop("knowledge_bases", UNSET))

        question_categories = cast(list[int], d.pop("question_categories", UNSET))

        question_entries = cast(list[int], d.pop("question_entries", UNSET))

        language = d.pop("language", UNSET)

        fallback_language = d.pop("fallback_language", UNSET)

        depth = d.pop("depth", UNSET)

        create_book_request = cls(
            source_refs=source_refs,
            user_intent=user_intent,
            chat_session_id=chat_session_id,
            chat_selections=chat_selections,
            notebook_refs=notebook_refs,
            knowledge_bases=knowledge_bases,
            question_categories=question_categories,
            question_entries=question_entries,
            language=language,
            fallback_language=fallback_language,
            depth=depth,
        )

        create_book_request.additional_properties = d
        return create_book_request

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
