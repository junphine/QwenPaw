from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreatePartnerInvocationRequest")


@_attrs_define
class CreatePartnerInvocationRequest:
    """
    Attributes:
        session_key (str):
        requester_partner_id (str):
        target_partner_id (str):
        question (str):
    """

    session_key: str
    requester_partner_id: str
    target_partner_id: str
    question: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_key = self.session_key

        requester_partner_id = self.requester_partner_id

        target_partner_id = self.target_partner_id

        question = self.question

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "session_key": session_key,
                "requester_partner_id": requester_partner_id,
                "target_partner_id": target_partner_id,
                "question": question,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_key = d.pop("session_key")

        requester_partner_id = d.pop("requester_partner_id")

        target_partner_id = d.pop("target_partner_id")

        question = d.pop("question")

        create_partner_invocation_request = cls(
            session_key=session_key,
            requester_partner_id=requester_partner_id,
            target_partner_id=target_partner_id,
            question=question,
        )

        create_partner_invocation_request.additional_properties = d
        return create_partner_invocation_request

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
