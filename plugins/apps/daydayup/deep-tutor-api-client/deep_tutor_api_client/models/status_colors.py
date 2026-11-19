from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusColors")


@_attrs_define
class StatusColors:
    """
    Attributes:
        todo (str | Unset):  Default: '#2563eb'.
        doing (str | Unset):  Default: '#a16207'.
        done (str | Unset):  Default: '#15803d'.
    """

    todo: str | Unset = "#2563eb"
    doing: str | Unset = "#a16207"
    done: str | Unset = "#15803d"

    def to_dict(self) -> dict[str, Any]:
        todo = self.todo

        doing = self.doing

        done = self.done

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if todo is not UNSET:
            field_dict["todo"] = todo
        if doing is not UNSET:
            field_dict["doing"] = doing
        if done is not UNSET:
            field_dict["done"] = done

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        todo = d.pop("todo", UNSET)

        doing = d.pop("doing", UNSET)

        done = d.pop("done", UNSET)

        status_colors = cls(
            todo=todo,
            doing=doing,
            done=done,
        )

        return status_colors
