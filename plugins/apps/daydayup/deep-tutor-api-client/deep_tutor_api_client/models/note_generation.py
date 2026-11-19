from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="NoteGeneration")


@_attrs_define
class NoteGeneration:
    """The learning block on the open note page this turn fills in.

    Sent by the note companion when a block's own "Generate" runs. The server
    owns the instructions that follow from it, so the learner's message stays
    exactly what they see in the conversation.

        Attributes:
            block_id (str):
            kind (str | Unset):  Default: ''.
    """

    block_id: str
    kind: str | Unset = ""

    def to_dict(self) -> dict[str, Any]:
        block_id = self.block_id

        kind = self.kind

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "block_id": block_id,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        block_id = d.pop("block_id")

        kind = d.pop("kind", UNSET)

        note_generation = cls(
            block_id=block_id,
            kind=kind,
        )

        return note_generation
