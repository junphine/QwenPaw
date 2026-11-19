from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataMigrationPayload")


@_attrs_define
class DataMigrationPayload:
    """
    Attributes:
        features (list[str]):
        source_workspace_id (str | Unset):  Default: ''.
        target_workspace_id (str | Unset):  Default: ''.
        include_historical (bool | Unset):  Default: False.
        session_ids (list[str] | None | Unset):
    """

    features: list[str]
    source_workspace_id: str | Unset = ""
    target_workspace_id: str | Unset = ""
    include_historical: bool | Unset = False
    session_ids: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        features = self.features

        source_workspace_id = self.source_workspace_id

        target_workspace_id = self.target_workspace_id

        include_historical = self.include_historical

        session_ids: list[str] | None | Unset
        if isinstance(self.session_ids, Unset):
            session_ids = UNSET
        elif isinstance(self.session_ids, list):
            session_ids = self.session_ids

        else:
            session_ids = self.session_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "features": features,
            }
        )
        if source_workspace_id is not UNSET:
            field_dict["source_workspace_id"] = source_workspace_id
        if target_workspace_id is not UNSET:
            field_dict["target_workspace_id"] = target_workspace_id
        if include_historical is not UNSET:
            field_dict["include_historical"] = include_historical
        if session_ids is not UNSET:
            field_dict["session_ids"] = session_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        features = cast(list[str], d.pop("features"))

        source_workspace_id = d.pop("source_workspace_id", UNSET)

        target_workspace_id = d.pop("target_workspace_id", UNSET)

        include_historical = d.pop("include_historical", UNSET)

        def _parse_session_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                session_ids_type_0 = cast(list[str], data)

                return session_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        session_ids = _parse_session_ids(d.pop("session_ids", UNSET))

        data_migration_payload = cls(
            features=features,
            source_workspace_id=source_workspace_id,
            target_workspace_id=target_workspace_id,
            include_historical=include_historical,
            session_ids=session_ids,
        )

        data_migration_payload.additional_properties = d
        return data_migration_payload

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
