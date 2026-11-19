from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="TimedMediaViewport")


@_attrs_define
class TimedMediaViewport:
    """
    Attributes:
        time_seconds (float):
    """

    time_seconds: float

    def to_dict(self) -> dict[str, Any]:
        time_seconds = self.time_seconds

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "time_seconds": time_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time_seconds = d.pop("time_seconds")

        timed_media_viewport = cls(
            time_seconds=time_seconds,
        )

        return timed_media_viewport
