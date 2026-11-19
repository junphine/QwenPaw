from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.session_organization_request_session_kind_type_0 import (
    SessionOrganizationRequestSessionKindType0,
    check_session_organization_request_session_kind_type_0,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SessionOrganizationRequest")


@_attrs_define
class SessionOrganizationRequest:
    """User-controlled organization metadata stored with the conversation.

    Attributes:
        workspace_id (None | str | Unset):
        parent_session_id (None | str | Unset):
        session_kind (None | SessionOrganizationRequestSessionKindType0 | Unset):
        pinned (bool | None | Unset):
        archived (bool | None | Unset):
        tutor_source_message_id (int | None | str | Unset):
    """

    workspace_id: None | str | Unset = UNSET
    parent_session_id: None | str | Unset = UNSET
    session_kind: None | SessionOrganizationRequestSessionKindType0 | Unset = UNSET
    pinned: bool | None | Unset = UNSET
    archived: bool | None | Unset = UNSET
    tutor_source_message_id: int | None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        parent_session_id: None | str | Unset
        if isinstance(self.parent_session_id, Unset):
            parent_session_id = UNSET
        else:
            parent_session_id = self.parent_session_id

        session_kind: None | str | Unset
        if isinstance(self.session_kind, Unset):
            session_kind = UNSET
        elif isinstance(self.session_kind, str):
            session_kind = self.session_kind
        else:
            session_kind = self.session_kind

        pinned: bool | None | Unset
        if isinstance(self.pinned, Unset):
            pinned = UNSET
        else:
            pinned = self.pinned

        archived: bool | None | Unset
        if isinstance(self.archived, Unset):
            archived = UNSET
        else:
            archived = self.archived

        tutor_source_message_id: int | None | str | Unset
        if isinstance(self.tutor_source_message_id, Unset):
            tutor_source_message_id = UNSET
        else:
            tutor_source_message_id = self.tutor_source_message_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if parent_session_id is not UNSET:
            field_dict["parent_session_id"] = parent_session_id
        if session_kind is not UNSET:
            field_dict["session_kind"] = session_kind
        if pinned is not UNSET:
            field_dict["pinned"] = pinned
        if archived is not UNSET:
            field_dict["archived"] = archived
        if tutor_source_message_id is not UNSET:
            field_dict["tutor_source_message_id"] = tutor_source_message_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_parent_session_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_session_id = _parse_parent_session_id(d.pop("parent_session_id", UNSET))

        def _parse_session_kind(data: object) -> None | SessionOrganizationRequestSessionKindType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                session_kind_type_0 = check_session_organization_request_session_kind_type_0(data)

                return session_kind_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SessionOrganizationRequestSessionKindType0 | Unset, data)

        session_kind = _parse_session_kind(d.pop("session_kind", UNSET))

        def _parse_pinned(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        pinned = _parse_pinned(d.pop("pinned", UNSET))

        def _parse_archived(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        archived = _parse_archived(d.pop("archived", UNSET))

        def _parse_tutor_source_message_id(data: object) -> int | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | str | Unset, data)

        tutor_source_message_id = _parse_tutor_source_message_id(d.pop("tutor_source_message_id", UNSET))

        session_organization_request = cls(
            workspace_id=workspace_id,
            parent_session_id=parent_session_id,
            session_kind=session_kind,
            pinned=pinned,
            archived=archived,
            tutor_source_message_id=tutor_source_message_id,
        )

        session_organization_request.additional_properties = d
        return session_organization_request

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
