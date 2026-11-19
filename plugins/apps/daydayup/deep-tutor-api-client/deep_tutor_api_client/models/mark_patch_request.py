from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mark_patch_request_metadata_type_0 import MarkPatchRequestMetadataType0


T = TypeVar("T", bound="MarkPatchRequest")


@_attrs_define
class MarkPatchRequest:
    """
    Attributes:
        kind (None | str | Unset):
        start_seconds (float | None | Unset):
        end_seconds (float | None | Unset):
        start_locator (int | None | Unset):
        end_locator (int | None | Unset):
        quote (None | str | Unset):
        note (None | str | Unset):
        reviewed (bool | None | Unset):
        metadata (MarkPatchRequestMetadataType0 | None | Unset):
    """

    kind: None | str | Unset = UNSET
    start_seconds: float | None | Unset = UNSET
    end_seconds: float | None | Unset = UNSET
    start_locator: int | None | Unset = UNSET
    end_locator: int | None | Unset = UNSET
    quote: None | str | Unset = UNSET
    note: None | str | Unset = UNSET
    reviewed: bool | None | Unset = UNSET
    metadata: MarkPatchRequestMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.mark_patch_request_metadata_type_0 import MarkPatchRequestMetadataType0  # noqa: PLC0415

        kind: None | str | Unset
        if isinstance(self.kind, Unset):
            kind = UNSET
        else:
            kind = self.kind

        start_seconds: float | None | Unset
        if isinstance(self.start_seconds, Unset):
            start_seconds = UNSET
        else:
            start_seconds = self.start_seconds

        end_seconds: float | None | Unset
        if isinstance(self.end_seconds, Unset):
            end_seconds = UNSET
        else:
            end_seconds = self.end_seconds

        start_locator: int | None | Unset
        if isinstance(self.start_locator, Unset):
            start_locator = UNSET
        else:
            start_locator = self.start_locator

        end_locator: int | None | Unset
        if isinstance(self.end_locator, Unset):
            end_locator = UNSET
        else:
            end_locator = self.end_locator

        quote: None | str | Unset
        if isinstance(self.quote, Unset):
            quote = UNSET
        else:
            quote = self.quote

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        reviewed: bool | None | Unset
        if isinstance(self.reviewed, Unset):
            reviewed = UNSET
        else:
            reviewed = self.reviewed

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, MarkPatchRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if kind is not UNSET:
            field_dict["kind"] = kind
        if start_seconds is not UNSET:
            field_dict["start_seconds"] = start_seconds
        if end_seconds is not UNSET:
            field_dict["end_seconds"] = end_seconds
        if start_locator is not UNSET:
            field_dict["start_locator"] = start_locator
        if end_locator is not UNSET:
            field_dict["end_locator"] = end_locator
        if quote is not UNSET:
            field_dict["quote"] = quote
        if note is not UNSET:
            field_dict["note"] = note
        if reviewed is not UNSET:
            field_dict["reviewed"] = reviewed
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mark_patch_request_metadata_type_0 import MarkPatchRequestMetadataType0  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kind = _parse_kind(d.pop("kind", UNSET))

        def _parse_start_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        start_seconds = _parse_start_seconds(d.pop("start_seconds", UNSET))

        def _parse_end_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        end_seconds = _parse_end_seconds(d.pop("end_seconds", UNSET))

        def _parse_start_locator(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        start_locator = _parse_start_locator(d.pop("start_locator", UNSET))

        def _parse_end_locator(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        end_locator = _parse_end_locator(d.pop("end_locator", UNSET))

        def _parse_quote(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        quote = _parse_quote(d.pop("quote", UNSET))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_reviewed(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        reviewed = _parse_reviewed(d.pop("reviewed", UNSET))

        def _parse_metadata(data: object) -> MarkPatchRequestMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = MarkPatchRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MarkPatchRequestMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        mark_patch_request = cls(
            kind=kind,
            start_seconds=start_seconds,
            end_seconds=end_seconds,
            start_locator=start_locator,
            end_locator=end_locator,
            quote=quote,
            note=note,
            reviewed=reviewed,
            metadata=metadata,
        )

        mark_patch_request.additional_properties = d
        return mark_patch_request

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
