from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.book_edit_action import BookEditAction, check_book_edit_action
from ..types import UNSET, Unset

T = TypeVar("T", bound="BookEdit")


@_attrs_define
class BookEdit:
    """
    Attributes:
        action (BookEditAction):
        chapter_id (str | Unset):  Default: ''.
        page_id (str | Unset):  Default: ''.
        title (str | Unset):  Default: ''.
        body (str | Unset):  Default: ''.
        learning_objectives (list[str] | Unset):
        position (int | Unset):  Default: 0.
    """

    action: BookEditAction
    chapter_id: str | Unset = ""
    page_id: str | Unset = ""
    title: str | Unset = ""
    body: str | Unset = ""
    learning_objectives: list[str] | Unset = UNSET
    position: int | Unset = 0

    def to_dict(self) -> dict[str, Any]:
        action: str = self.action

        chapter_id = self.chapter_id

        page_id = self.page_id

        title = self.title

        body = self.body

        learning_objectives: list[str] | Unset = UNSET
        if not isinstance(self.learning_objectives, Unset):
            learning_objectives = self.learning_objectives

        position = self.position

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "action": action,
            }
        )
        if chapter_id is not UNSET:
            field_dict["chapter_id"] = chapter_id
        if page_id is not UNSET:
            field_dict["page_id"] = page_id
        if title is not UNSET:
            field_dict["title"] = title
        if body is not UNSET:
            field_dict["body"] = body
        if learning_objectives is not UNSET:
            field_dict["learning_objectives"] = learning_objectives
        if position is not UNSET:
            field_dict["position"] = position

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = check_book_edit_action(d.pop("action"))

        chapter_id = d.pop("chapter_id", UNSET)

        page_id = d.pop("page_id", UNSET)

        title = d.pop("title", UNSET)

        body = d.pop("body", UNSET)

        learning_objectives = cast(list[str], d.pop("learning_objectives", UNSET))

        position = d.pop("position", UNSET)

        book_edit = cls(
            action=action,
            chapter_id=chapter_id,
            page_id=page_id,
            title=title,
            body=body,
            learning_objectives=learning_objectives,
            position=position,
        )

        return book_edit
