from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.composer_controls import ComposerControls
    from ..models.starters import Starters


T = TypeVar("T", bound="ChatPageCustomization")


@_attrs_define
class ChatPageCustomization:
    """
    Attributes:
        hidden_modes (list[str] | Unset):
        controls (ComposerControls | Unset):
        starters (Starters | Unset):
    """

    hidden_modes: list[str] | Unset = UNSET
    controls: ComposerControls | Unset = UNSET
    starters: Starters | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        hidden_modes: list[str] | Unset = UNSET
        if not isinstance(self.hidden_modes, Unset):
            hidden_modes = self.hidden_modes

        controls: dict[str, Any] | Unset = UNSET
        if not isinstance(self.controls, Unset):
            controls = self.controls.to_dict()

        starters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.starters, Unset):
            starters = self.starters.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if hidden_modes is not UNSET:
            field_dict["hidden_modes"] = hidden_modes
        if controls is not UNSET:
            field_dict["controls"] = controls
        if starters is not UNSET:
            field_dict["starters"] = starters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.composer_controls import ComposerControls  # noqa: PLC0415
        from ..models.starters import Starters  # noqa: PLC0415

        d = dict(src_dict)
        hidden_modes = cast(list[str], d.pop("hidden_modes", UNSET))

        _controls = d.pop("controls", UNSET)
        controls: ComposerControls | Unset
        if isinstance(_controls, Unset):
            controls = UNSET
        else:
            controls = ComposerControls.from_dict(_controls)

        _starters = d.pop("starters", UNSET)
        starters: Starters | Unset
        if isinstance(_starters, Unset):
            starters = UNSET
        else:
            starters = Starters.from_dict(_starters)

        chat_page_customization = cls(
            hidden_modes=hidden_modes,
            controls=controls,
            starters=starters,
        )

        return chat_page_customization
