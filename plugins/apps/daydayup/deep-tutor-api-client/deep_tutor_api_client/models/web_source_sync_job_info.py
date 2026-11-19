from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSourceSyncJobInfo")


@_attrs_define
class WebSourceSyncJobInfo:
    """
    Attributes:
        owner_id (str):
        kb_name (str):
        source_id (str):
        state (str):
        next_run_at (int):
        last_run_at (int | None | Unset):
        attempt (int | Unset):  Default: 0.
        error (None | str | Unset):
        cancel_requested (bool | Unset):  Default: False.
    """

    owner_id: str
    kb_name: str
    source_id: str
    state: str
    next_run_at: int
    last_run_at: int | None | Unset = UNSET
    attempt: int | Unset = 0
    error: None | str | Unset = UNSET
    cancel_requested: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        owner_id = self.owner_id

        kb_name = self.kb_name

        source_id = self.source_id

        state = self.state

        next_run_at = self.next_run_at

        last_run_at: int | None | Unset
        if isinstance(self.last_run_at, Unset):
            last_run_at = UNSET
        else:
            last_run_at = self.last_run_at

        attempt = self.attempt

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        cancel_requested = self.cancel_requested

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "owner_id": owner_id,
                "kb_name": kb_name,
                "source_id": source_id,
                "state": state,
                "next_run_at": next_run_at,
            }
        )
        if last_run_at is not UNSET:
            field_dict["last_run_at"] = last_run_at
        if attempt is not UNSET:
            field_dict["attempt"] = attempt
        if error is not UNSET:
            field_dict["error"] = error
        if cancel_requested is not UNSET:
            field_dict["cancel_requested"] = cancel_requested

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        owner_id = d.pop("owner_id")

        kb_name = d.pop("kb_name")

        source_id = d.pop("source_id")

        state = d.pop("state")

        next_run_at = d.pop("next_run_at")

        def _parse_last_run_at(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        last_run_at = _parse_last_run_at(d.pop("last_run_at", UNSET))

        attempt = d.pop("attempt", UNSET)

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        cancel_requested = d.pop("cancel_requested", UNSET)

        web_source_sync_job_info = cls(
            owner_id=owner_id,
            kb_name=kb_name,
            source_id=source_id,
            state=state,
            next_run_at=next_run_at,
            last_run_at=last_run_at,
            attempt=attempt,
            error=error,
            cancel_requested=cancel_requested,
        )

        web_source_sync_job_info.additional_properties = d
        return web_source_sync_job_info

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
