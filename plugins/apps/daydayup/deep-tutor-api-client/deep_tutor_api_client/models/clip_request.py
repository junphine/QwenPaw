from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.favorite_metadata import FavoriteMetadata


T = TypeVar("T", bound="ClipRequest")


@_attrs_define
class ClipRequest:
    """
    Attributes:
        markdown (str):
        title (str | Unset):  Default: ''.
        source_url (str | Unset):  Default: ''.
        source_id (str | Unset):  Default: ''.
        favorite_type (str | Unset):  Default: ''.
        summary (str | Unset):  Default: ''.
        favorite_metadata (FavoriteMetadata | Unset):
    """

    markdown: str
    title: str | Unset = ""
    source_url: str | Unset = ""
    source_id: str | Unset = ""
    favorite_type: str | Unset = ""
    summary: str | Unset = ""
    favorite_metadata: FavoriteMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        markdown = self.markdown

        title = self.title

        source_url = self.source_url

        source_id = self.source_id

        favorite_type = self.favorite_type

        summary = self.summary

        favorite_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.favorite_metadata, Unset):
            favorite_metadata = self.favorite_metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "markdown": markdown,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if favorite_type is not UNSET:
            field_dict["favorite_type"] = favorite_type
        if summary is not UNSET:
            field_dict["summary"] = summary
        if favorite_metadata is not UNSET:
            field_dict["favorite_metadata"] = favorite_metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.favorite_metadata import FavoriteMetadata  # noqa: PLC0415

        d = dict(src_dict)
        markdown = d.pop("markdown")

        title = d.pop("title", UNSET)

        source_url = d.pop("source_url", UNSET)

        source_id = d.pop("source_id", UNSET)

        favorite_type = d.pop("favorite_type", UNSET)

        summary = d.pop("summary", UNSET)

        _favorite_metadata = d.pop("favorite_metadata", UNSET)
        favorite_metadata: FavoriteMetadata | Unset
        if isinstance(_favorite_metadata, Unset):
            favorite_metadata = UNSET
        else:
            favorite_metadata = FavoriteMetadata.from_dict(_favorite_metadata)

        clip_request = cls(
            markdown=markdown,
            title=title,
            source_url=source_url,
            source_id=source_id,
            favorite_type=favorite_type,
            summary=summary,
            favorite_metadata=favorite_metadata,
        )

        clip_request.additional_properties = d
        return clip_request

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
