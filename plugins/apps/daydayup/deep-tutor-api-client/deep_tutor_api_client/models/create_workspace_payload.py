from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.workspace_resources import WorkspaceResources


T = TypeVar("T", bound="CreateWorkspacePayload")


@_attrs_define
class CreateWorkspacePayload:
    """
    Attributes:
        name (str):
        instructions (None | str | Unset):
        resources (None | Unset | WorkspaceResources):
        path (None | str | Unset):
    """

    name: str
    instructions: None | str | Unset = UNSET
    resources: None | Unset | WorkspaceResources = UNSET
    path: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.workspace_resources import WorkspaceResources  # noqa: PLC0415

        name = self.name

        instructions: None | str | Unset
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        else:
            instructions = self.instructions

        resources: dict[str, Any] | None | Unset
        if isinstance(self.resources, Unset):
            resources = UNSET
        elif isinstance(self.resources, WorkspaceResources):
            resources = self.resources.to_dict()
        else:
            resources = self.resources

        path: None | str | Unset
        if isinstance(self.path, Unset):
            path = UNSET
        else:
            path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if resources is not UNSET:
            field_dict["resources"] = resources
        if path is not UNSET:
            field_dict["path"] = path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace_resources import WorkspaceResources  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_instructions(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        instructions = _parse_instructions(d.pop("instructions", UNSET))

        def _parse_resources(data: object) -> None | Unset | WorkspaceResources:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                resources_type_0 = WorkspaceResources.from_dict(data)

                return resources_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WorkspaceResources, data)

        resources = _parse_resources(d.pop("resources", UNSET))

        def _parse_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        path = _parse_path(d.pop("path", UNSET))

        create_workspace_payload = cls(
            name=name,
            instructions=instructions,
            resources=resources,
            path=path,
        )

        create_workspace_payload.additional_properties = d
        return create_workspace_payload

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
