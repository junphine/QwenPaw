from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LinkStatus")


@_attrs_define
class LinkStatus:
    """
    Attributes:
        enabled (bool):
        workspace_id (str | Unset):  Default: ''.
    """

    enabled: bool
    workspace_id: str | Unset = ""

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "enabled": enabled,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled")

        workspace_id = d.pop("workspace_id", UNSET)

        link_status = cls(
            enabled=enabled,
            workspace_id=workspace_id,
        )

        return link_status
