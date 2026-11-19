from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectSubagentRequest")


@_attrs_define
class ConnectSubagentRequest:
    """
    Attributes:
        name (str):
        agent_kind (str):
        cwd (str | Unset):  Default: ''.
        description (str | Unset):  Default: ''.
        agent_id (str | Unset):  Default: ''.
    """

    name: str
    agent_kind: str
    cwd: str | Unset = ""
    description: str | Unset = ""
    agent_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        agent_kind = self.agent_kind

        cwd = self.cwd

        description = self.description

        agent_id = self.agent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "agent_kind": agent_kind,
            }
        )
        if cwd is not UNSET:
            field_dict["cwd"] = cwd
        if description is not UNSET:
            field_dict["description"] = description
        if agent_id is not UNSET:
            field_dict["agent_id"] = agent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        agent_kind = d.pop("agent_kind")

        cwd = d.pop("cwd", UNSET)

        description = d.pop("description", UNSET)

        agent_id = d.pop("agent_id", UNSET)

        connect_subagent_request = cls(
            name=name,
            agent_kind=agent_kind,
            cwd=cwd,
            description=description,
            agent_id=agent_id,
        )

        connect_subagent_request.additional_properties = d
        return connect_subagent_request

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
