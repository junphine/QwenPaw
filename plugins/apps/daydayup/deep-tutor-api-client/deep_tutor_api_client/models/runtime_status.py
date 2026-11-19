from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from ..models.runtime_status_coordination_mode import (
    RuntimeStatusCoordinationMode,
    check_runtime_status_coordination_mode,
)
from ..models.runtime_status_redis_status import RuntimeStatusRedisStatus, check_runtime_status_redis_status
from ..types import UNSET, Unset

T = TypeVar("T", bound="RuntimeStatus")


@_attrs_define
class RuntimeStatus:
    """
    Attributes:
        worker_id (str):
        worker_count (int):
        coordination_mode (RuntimeStatusCoordinationMode):
        redis_configured (bool):
        redis_status (RuntimeStatusRedisStatus):
        lease_ttl_seconds (int):
        renew_interval_seconds (int):
        recovery_interval_seconds (int):
        leader_id (None | str | Unset):
        leader_healthy (bool | None | Unset):
        owner_turn_count (int | Unset):  Default: 0.
        recovery_backlog (int | Unset):  Default: 0.
        protocol_version (Literal['2.0'] | Unset):  Default: '2.0'.
        minimum_web_protocol_version (Literal['2.0'] | Unset):  Default: '2.0'.
    """

    worker_id: str
    worker_count: int
    coordination_mode: RuntimeStatusCoordinationMode
    redis_configured: bool
    redis_status: RuntimeStatusRedisStatus
    lease_ttl_seconds: int
    renew_interval_seconds: int
    recovery_interval_seconds: int
    leader_id: None | str | Unset = UNSET
    leader_healthy: bool | None | Unset = UNSET
    owner_turn_count: int | Unset = 0
    recovery_backlog: int | Unset = 0
    protocol_version: Literal["2.0"] | Unset = "2.0"
    minimum_web_protocol_version: Literal["2.0"] | Unset = "2.0"

    def to_dict(self) -> dict[str, Any]:
        worker_id = self.worker_id

        worker_count = self.worker_count

        coordination_mode: str = self.coordination_mode

        redis_configured = self.redis_configured

        redis_status: str = self.redis_status

        lease_ttl_seconds = self.lease_ttl_seconds

        renew_interval_seconds = self.renew_interval_seconds

        recovery_interval_seconds = self.recovery_interval_seconds

        leader_id: None | str | Unset
        if isinstance(self.leader_id, Unset):
            leader_id = UNSET
        else:
            leader_id = self.leader_id

        leader_healthy: bool | None | Unset
        if isinstance(self.leader_healthy, Unset):
            leader_healthy = UNSET
        else:
            leader_healthy = self.leader_healthy

        owner_turn_count = self.owner_turn_count

        recovery_backlog = self.recovery_backlog

        protocol_version = self.protocol_version

        minimum_web_protocol_version = self.minimum_web_protocol_version

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "worker_id": worker_id,
                "worker_count": worker_count,
                "coordination_mode": coordination_mode,
                "redis_configured": redis_configured,
                "redis_status": redis_status,
                "lease_ttl_seconds": lease_ttl_seconds,
                "renew_interval_seconds": renew_interval_seconds,
                "recovery_interval_seconds": recovery_interval_seconds,
            }
        )
        if leader_id is not UNSET:
            field_dict["leader_id"] = leader_id
        if leader_healthy is not UNSET:
            field_dict["leader_healthy"] = leader_healthy
        if owner_turn_count is not UNSET:
            field_dict["owner_turn_count"] = owner_turn_count
        if recovery_backlog is not UNSET:
            field_dict["recovery_backlog"] = recovery_backlog
        if protocol_version is not UNSET:
            field_dict["protocol_version"] = protocol_version
        if minimum_web_protocol_version is not UNSET:
            field_dict["minimum_web_protocol_version"] = minimum_web_protocol_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        worker_id = d.pop("worker_id")

        worker_count = d.pop("worker_count")

        coordination_mode = check_runtime_status_coordination_mode(d.pop("coordination_mode"))

        redis_configured = d.pop("redis_configured")

        redis_status = check_runtime_status_redis_status(d.pop("redis_status"))

        lease_ttl_seconds = d.pop("lease_ttl_seconds")

        renew_interval_seconds = d.pop("renew_interval_seconds")

        recovery_interval_seconds = d.pop("recovery_interval_seconds")

        def _parse_leader_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        leader_id = _parse_leader_id(d.pop("leader_id", UNSET))

        def _parse_leader_healthy(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        leader_healthy = _parse_leader_healthy(d.pop("leader_healthy", UNSET))

        owner_turn_count = d.pop("owner_turn_count", UNSET)

        recovery_backlog = d.pop("recovery_backlog", UNSET)

        protocol_version = cast(Literal["2.0"] | Unset, d.pop("protocol_version", UNSET))
        if protocol_version != "2.0" and not isinstance(protocol_version, Unset):
            raise ValueError(f"protocol_version must match const '2.0', got '{protocol_version}'")

        minimum_web_protocol_version = cast(Literal["2.0"] | Unset, d.pop("minimum_web_protocol_version", UNSET))
        if minimum_web_protocol_version != "2.0" and not isinstance(minimum_web_protocol_version, Unset):
            raise ValueError(
                f"minimum_web_protocol_version must match const '2.0', got '{minimum_web_protocol_version}'"
            )

        runtime_status = cls(
            worker_id=worker_id,
            worker_count=worker_count,
            coordination_mode=coordination_mode,
            redis_configured=redis_configured,
            redis_status=redis_status,
            lease_ttl_seconds=lease_ttl_seconds,
            renew_interval_seconds=renew_interval_seconds,
            recovery_interval_seconds=recovery_interval_seconds,
            leader_id=leader_id,
            leader_healthy=leader_healthy,
            owner_turn_count=owner_turn_count,
            recovery_backlog=recovery_backlog,
            protocol_version=protocol_version,
            minimum_web_protocol_version=minimum_web_protocol_version,
        )

        return runtime_status
