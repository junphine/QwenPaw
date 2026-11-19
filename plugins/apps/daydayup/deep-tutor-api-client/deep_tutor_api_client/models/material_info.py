from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.material_info_content_format import MaterialInfoContentFormat, check_material_info_content_format
from ..models.material_info_render_mode import MaterialInfoRenderMode, check_material_info_render_mode
from ..types import UNSET, Unset

T = TypeVar("T", bound="MaterialInfo")


@_attrs_define
class MaterialInfo:
    """
    Attributes:
        material_id (str):
        filename (str):
        unit (str):
        unit_count (int):
        mime (str | Unset):  Default: ''.
        title (str | Unset):  Default: ''.
        byte_size (int | Unset):  Default: 0.
        char_count (int | Unset):  Default: 0.
        created_at (float | Unset):  Default: 0.0.
        has_raw_view (bool | Unset):  Default: False.
        render_mode (MaterialInfoRenderMode | Unset):  Default: 'text'.
        extractor (str | Unset):  Default: ''.
        content_format (MaterialInfoContentFormat | Unset):  Default: 'plain_text'.
        source_type (str | Unset):  Default: 'upload'.
        source_url (str | Unset):  Default: ''.
        revision (int | Unset):  Default: 1.
        annotation_count (int | Unset):  Default: 0.
    """

    material_id: str
    filename: str
    unit: str
    unit_count: int
    mime: str | Unset = ""
    title: str | Unset = ""
    byte_size: int | Unset = 0
    char_count: int | Unset = 0
    created_at: float | Unset = 0.0
    has_raw_view: bool | Unset = False
    render_mode: MaterialInfoRenderMode | Unset = "text"
    extractor: str | Unset = ""
    content_format: MaterialInfoContentFormat | Unset = "plain_text"
    source_type: str | Unset = "upload"
    source_url: str | Unset = ""
    revision: int | Unset = 1
    annotation_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        material_id = self.material_id

        filename = self.filename

        unit = self.unit

        unit_count = self.unit_count

        mime = self.mime

        title = self.title

        byte_size = self.byte_size

        char_count = self.char_count

        created_at = self.created_at

        has_raw_view = self.has_raw_view

        render_mode: str | Unset = UNSET
        if not isinstance(self.render_mode, Unset):
            render_mode = self.render_mode

        extractor = self.extractor

        content_format: str | Unset = UNSET
        if not isinstance(self.content_format, Unset):
            content_format = self.content_format

        source_type = self.source_type

        source_url = self.source_url

        revision = self.revision

        annotation_count = self.annotation_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "material_id": material_id,
                "filename": filename,
                "unit": unit,
                "unit_count": unit_count,
            }
        )
        if mime is not UNSET:
            field_dict["mime"] = mime
        if title is not UNSET:
            field_dict["title"] = title
        if byte_size is not UNSET:
            field_dict["byte_size"] = byte_size
        if char_count is not UNSET:
            field_dict["char_count"] = char_count
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if has_raw_view is not UNSET:
            field_dict["has_raw_view"] = has_raw_view
        if render_mode is not UNSET:
            field_dict["render_mode"] = render_mode
        if extractor is not UNSET:
            field_dict["extractor"] = extractor
        if content_format is not UNSET:
            field_dict["content_format"] = content_format
        if source_type is not UNSET:
            field_dict["source_type"] = source_type
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if revision is not UNSET:
            field_dict["revision"] = revision
        if annotation_count is not UNSET:
            field_dict["annotation_count"] = annotation_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        material_id = d.pop("material_id")

        filename = d.pop("filename")

        unit = d.pop("unit")

        unit_count = d.pop("unit_count")

        mime = d.pop("mime", UNSET)

        title = d.pop("title", UNSET)

        byte_size = d.pop("byte_size", UNSET)

        char_count = d.pop("char_count", UNSET)

        created_at = d.pop("created_at", UNSET)

        has_raw_view = d.pop("has_raw_view", UNSET)

        _render_mode = d.pop("render_mode", UNSET)
        render_mode: MaterialInfoRenderMode | Unset
        if isinstance(_render_mode, Unset):
            render_mode = UNSET
        else:
            render_mode = check_material_info_render_mode(_render_mode)

        extractor = d.pop("extractor", UNSET)

        _content_format = d.pop("content_format", UNSET)
        content_format: MaterialInfoContentFormat | Unset
        if isinstance(_content_format, Unset):
            content_format = UNSET
        else:
            content_format = check_material_info_content_format(_content_format)

        source_type = d.pop("source_type", UNSET)

        source_url = d.pop("source_url", UNSET)

        revision = d.pop("revision", UNSET)

        annotation_count = d.pop("annotation_count", UNSET)

        material_info = cls(
            material_id=material_id,
            filename=filename,
            unit=unit,
            unit_count=unit_count,
            mime=mime,
            title=title,
            byte_size=byte_size,
            char_count=char_count,
            created_at=created_at,
            has_raw_view=has_raw_view,
            render_mode=render_mode,
            extractor=extractor,
            content_format=content_format,
            source_type=source_type,
            source_url=source_url,
            revision=revision,
            annotation_count=annotation_count,
        )

        material_info.additional_properties = d
        return material_info

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
