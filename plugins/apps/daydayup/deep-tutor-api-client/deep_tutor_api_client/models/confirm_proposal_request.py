from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.confirm_proposal_request_proposal_type_0 import ConfirmProposalRequestProposalType0


T = TypeVar("T", bound="ConfirmProposalRequest")


@_attrs_define
class ConfirmProposalRequest:
    """
    Attributes:
        book_id (str):
        proposal (ConfirmProposalRequestProposalType0 | None | Unset):
        expected_revision (int | None | Unset):
    """

    book_id: str
    proposal: ConfirmProposalRequestProposalType0 | None | Unset = UNSET
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.confirm_proposal_request_proposal_type_0 import (
            ConfirmProposalRequestProposalType0,  # noqa: PLC0415
        )

        book_id = self.book_id

        proposal: dict[str, Any] | None | Unset
        if isinstance(self.proposal, Unset):
            proposal = UNSET
        elif isinstance(self.proposal, ConfirmProposalRequestProposalType0):
            proposal = self.proposal.to_dict()
        else:
            proposal = self.proposal

        expected_revision: int | None | Unset
        if isinstance(self.expected_revision, Unset):
            expected_revision = UNSET
        else:
            expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "book_id": book_id,
            }
        )
        if proposal is not UNSET:
            field_dict["proposal"] = proposal
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.confirm_proposal_request_proposal_type_0 import (
            ConfirmProposalRequestProposalType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        book_id = d.pop("book_id")

        def _parse_proposal(data: object) -> ConfirmProposalRequestProposalType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                proposal_type_0 = ConfirmProposalRequestProposalType0.from_dict(data)

                return proposal_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ConfirmProposalRequestProposalType0 | None | Unset, data)

        proposal = _parse_proposal(d.pop("proposal", UNSET))

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        confirm_proposal_request = cls(
            book_id=book_id,
            proposal=proposal,
            expected_revision=expected_revision,
        )

        confirm_proposal_request.additional_properties = d
        return confirm_proposal_request

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
