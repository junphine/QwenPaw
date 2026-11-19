from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadingViewport")


@_attrs_define
class ReadingViewport:
    """
    Attributes:
        locator (int | None | Unset):
        selection (None | str | Unset):
        time_seconds (float | None | Unset):
    """

    locator: int | None | Unset = UNSET
    selection: None | str | Unset = UNSET
    time_seconds: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        locator: int | None | Unset
        if isinstance(self.locator, Unset):
            locator = UNSET
        else:
            locator = self.locator

        selection: None | str | Unset
        if isinstance(self.selection, Unset):
            selection = UNSET
        else:
            selection = self.selection

        time_seconds: float | None | Unset
        if isinstance(self.time_seconds, Unset):
            time_seconds = UNSET
        else:
            time_seconds = self.time_seconds

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if locator is not UNSET:
            field_dict["locator"] = locator
        if selection is not UNSET:
            field_dict["selection"] = selection
        if time_seconds is not UNSET:
            field_dict["time_seconds"] = time_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_locator(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        locator = _parse_locator(d.pop("locator", UNSET))

        def _parse_selection(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        selection = _parse_selection(d.pop("selection", UNSET))

        def _parse_time_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        time_seconds = _parse_time_seconds(d.pop("time_seconds", UNSET))

        reading_viewport = cls(
            locator=locator,
            selection=selection,
            time_seconds=time_seconds,
        )

        return reading_viewport
