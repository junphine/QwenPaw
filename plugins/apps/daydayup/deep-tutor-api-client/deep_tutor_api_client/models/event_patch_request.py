from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.event_patch_request_scope import EventPatchRequestScope, check_event_patch_request_scope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_patch import EventPatch


T = TypeVar("T", bound="EventPatchRequest")


@_attrs_define
class EventPatchRequest:
    """
    Attributes:
        changes (EventPatch): Every field optional; explicit null clears rrule/color/task links only.
        scope (EventPatchRequestScope | Unset):  Default: 'all'.
        occurrence (None | str | Unset):
    """

    changes: EventPatch
    scope: EventPatchRequestScope | Unset = "all"
    occurrence: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        changes = self.changes.to_dict()

        scope: str | Unset = UNSET
        if not isinstance(self.scope, Unset):
            scope = self.scope

        occurrence: None | str | Unset
        if isinstance(self.occurrence, Unset):
            occurrence = UNSET
        else:
            occurrence = self.occurrence

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "changes": changes,
            }
        )
        if scope is not UNSET:
            field_dict["scope"] = scope
        if occurrence is not UNSET:
            field_dict["occurrence"] = occurrence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_patch import EventPatch  # noqa: PLC0415

        d = dict(src_dict)
        changes = EventPatch.from_dict(d.pop("changes"))

        _scope = d.pop("scope", UNSET)
        scope: EventPatchRequestScope | Unset
        if isinstance(_scope, Unset):
            scope = UNSET
        else:
            scope = check_event_patch_request_scope(_scope)

        def _parse_occurrence(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        occurrence = _parse_occurrence(d.pop("occurrence", UNSET))

        event_patch_request = cls(
            changes=changes,
            scope=scope,
            occurrence=occurrence,
        )

        return event_patch_request
