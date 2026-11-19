from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ComposerControls")


@_attrs_define
class ComposerControls:
    """
    Attributes:
        skills (bool | Unset):  Default: True.
        mcp (bool | Unset):  Default: True.
        partners (bool | Unset):  Default: True.
        preferences (bool | Unset):  Default: True.
        voice (bool | Unset):  Default: True.
    """

    skills: bool | Unset = True
    mcp: bool | Unset = True
    partners: bool | Unset = True
    preferences: bool | Unset = True
    voice: bool | Unset = True

    def to_dict(self) -> dict[str, Any]:
        skills = self.skills

        mcp = self.mcp

        partners = self.partners

        preferences = self.preferences

        voice = self.voice

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if skills is not UNSET:
            field_dict["skills"] = skills
        if mcp is not UNSET:
            field_dict["mcp"] = mcp
        if partners is not UNSET:
            field_dict["partners"] = partners
        if preferences is not UNSET:
            field_dict["preferences"] = preferences
        if voice is not UNSET:
            field_dict["voice"] = voice

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        skills = d.pop("skills", UNSET)

        mcp = d.pop("mcp", UNSET)

        partners = d.pop("partners", UNSET)

        preferences = d.pop("preferences", UNSET)

        voice = d.pop("voice", UNSET)

        composer_controls = cls(
            skills=skills,
            mcp=mcp,
            partners=partners,
            preferences=preferences,
            voice=voice,
        )

        return composer_controls
