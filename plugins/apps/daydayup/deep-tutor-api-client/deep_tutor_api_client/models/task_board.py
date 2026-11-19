from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.session_task_links import SessionTaskLinks
    from ..models.status_colors import StatusColors
    from ..models.task_card import TaskCard


T = TypeVar("T", bound="TaskBoard")


@_attrs_define
class TaskBoard:
    """
    Attributes:
        cards (list[TaskCard]):
        colors (StatusColors | Unset):
        session_links (list[SessionTaskLinks] | Unset):
        revision (int | Unset):  Default: 0.
    """

    cards: list[TaskCard]
    colors: StatusColors | Unset = UNSET
    session_links: list[SessionTaskLinks] | Unset = UNSET
    revision: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cards = []
        for cards_item_data in self.cards:
            cards_item = cards_item_data.to_dict()
            cards.append(cards_item)

        colors: dict[str, Any] | Unset = UNSET
        if not isinstance(self.colors, Unset):
            colors = self.colors.to_dict()

        session_links: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.session_links, Unset):
            session_links = []
            for session_links_item_data in self.session_links:
                session_links_item = session_links_item_data.to_dict()
                session_links.append(session_links_item)

        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cards": cards,
            }
        )
        if colors is not UNSET:
            field_dict["colors"] = colors
        if session_links is not UNSET:
            field_dict["session_links"] = session_links
        if revision is not UNSET:
            field_dict["revision"] = revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.session_task_links import SessionTaskLinks  # noqa: PLC0415
        from ..models.status_colors import StatusColors  # noqa: PLC0415
        from ..models.task_card import TaskCard  # noqa: PLC0415

        d = dict(src_dict)
        cards = []
        _cards = d.pop("cards")
        for cards_item_data in _cards:
            cards_item = TaskCard.from_dict(cards_item_data)

            cards.append(cards_item)

        _colors = d.pop("colors", UNSET)
        colors: StatusColors | Unset
        if isinstance(_colors, Unset):
            colors = UNSET
        else:
            colors = StatusColors.from_dict(_colors)

        _session_links = d.pop("session_links", UNSET)
        session_links: list[SessionTaskLinks] | Unset = UNSET
        if _session_links is not UNSET:
            session_links = []
            for session_links_item_data in _session_links:
                session_links_item = SessionTaskLinks.from_dict(session_links_item_data)

                session_links.append(session_links_item)

        revision = d.pop("revision", UNSET)

        task_board = cls(
            cards=cards,
            colors=colors,
            session_links=session_links,
            revision=revision,
        )

        task_board.additional_properties = d
        return task_board

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
