from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.automation_run_kind import AutomationRunKind, check_automation_run_kind
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationRun")


@_attrs_define
class AutomationRun:
    """
    Attributes:
        id (str):
        job_id (str):
        name (str):
        message (str):
        at (str):
        kind (AutomationRunKind):
        expr (None | str | Unset):
        every_seconds (int | None | Unset):
        session_id (None | str | Unset):
        enabled (bool | Unset):  Default: True.
    """

    id: str
    job_id: str
    name: str
    message: str
    at: str
    kind: AutomationRunKind
    expr: None | str | Unset = UNSET
    every_seconds: int | None | Unset = UNSET
    session_id: None | str | Unset = UNSET
    enabled: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        job_id = self.job_id

        name = self.name

        message = self.message

        at = self.at

        kind: str = self.kind

        expr: None | str | Unset
        if isinstance(self.expr, Unset):
            expr = UNSET
        else:
            expr = self.expr

        every_seconds: int | None | Unset
        if isinstance(self.every_seconds, Unset):
            every_seconds = UNSET
        else:
            every_seconds = self.every_seconds

        session_id: None | str | Unset
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        else:
            session_id = self.session_id

        enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "job_id": job_id,
                "name": name,
                "message": message,
                "at": at,
                "kind": kind,
            }
        )
        if expr is not UNSET:
            field_dict["expr"] = expr
        if every_seconds is not UNSET:
            field_dict["every_seconds"] = every_seconds
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        job_id = d.pop("job_id")

        name = d.pop("name")

        message = d.pop("message")

        at = d.pop("at")

        kind = check_automation_run_kind(d.pop("kind"))

        def _parse_expr(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expr = _parse_expr(d.pop("expr", UNSET))

        def _parse_every_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        every_seconds = _parse_every_seconds(d.pop("every_seconds", UNSET))

        def _parse_session_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        session_id = _parse_session_id(d.pop("session_id", UNSET))

        enabled = d.pop("enabled", UNSET)

        automation_run = cls(
            id=id,
            job_id=job_id,
            name=name,
            message=message,
            at=at,
            kind=kind,
            expr=expr,
            every_seconds=every_seconds,
            session_id=session_id,
            enabled=enabled,
        )

        automation_run.additional_properties = d
        return automation_run

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
