from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceResources")


@_attrs_define
class WorkspaceResources:
    """
    Attributes:
        skills (list[str] | None | Unset):
        mcp (list[str] | None | Unset):
        knowledge_bases (list[str] | None | Unset):
    """

    skills: list[str] | None | Unset = UNSET
    mcp: list[str] | None | Unset = UNSET
    knowledge_bases: list[str] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        skills: list[str] | None | Unset
        if isinstance(self.skills, Unset):
            skills = UNSET
        elif isinstance(self.skills, list):
            skills = self.skills

        else:
            skills = self.skills

        mcp: list[str] | None | Unset
        if isinstance(self.mcp, Unset):
            mcp = UNSET
        elif isinstance(self.mcp, list):
            mcp = self.mcp

        else:
            mcp = self.mcp

        knowledge_bases: list[str] | None | Unset
        if isinstance(self.knowledge_bases, Unset):
            knowledge_bases = UNSET
        elif isinstance(self.knowledge_bases, list):
            knowledge_bases = self.knowledge_bases

        else:
            knowledge_bases = self.knowledge_bases

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if skills is not UNSET:
            field_dict["skills"] = skills
        if mcp is not UNSET:
            field_dict["mcp"] = mcp
        if knowledge_bases is not UNSET:
            field_dict["knowledge_bases"] = knowledge_bases

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_skills(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                skills_type_0 = cast(list[str], data)

                return skills_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        skills = _parse_skills(d.pop("skills", UNSET))

        def _parse_mcp(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                mcp_type_0 = cast(list[str], data)

                return mcp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        mcp = _parse_mcp(d.pop("mcp", UNSET))

        def _parse_knowledge_bases(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                knowledge_bases_type_0 = cast(list[str], data)

                return knowledge_bases_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        knowledge_bases = _parse_knowledge_bases(d.pop("knowledge_bases", UNSET))

        workspace_resources = cls(
            skills=skills,
            mcp=mcp,
            knowledge_bases=knowledge_bases,
        )

        return workspace_resources
