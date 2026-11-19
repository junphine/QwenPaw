from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.material_detail_content_format import MaterialDetailContentFormat, check_material_detail_content_format
from ..models.material_detail_render_mode import MaterialDetailRenderMode, check_material_detail_render_mode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.material_detail_outline_item import MaterialDetailOutlineItem
    from ..models.material_detail_unit_refs_item import MaterialDetailUnitRefsItem


T = TypeVar("T", bound="MaterialDetail")


@_attrs_define
class MaterialDetail:
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
        render_mode (MaterialDetailRenderMode | Unset):  Default: 'text'.
        extractor (str | Unset):  Default: ''.
        content_format (MaterialDetailContentFormat | Unset):  Default: 'plain_text'.
        source_type (str | Unset):  Default: 'upload'.
        source_url (str | Unset):  Default: ''.
        revision (int | Unset):  Default: 1.
        annotation_count (int | Unset):  Default: 0.
        outline (list[MaterialDetailOutlineItem] | Unset):
        outline_text (str | Unset):  Default: ''.
        unit_refs (list[MaterialDetailUnitRefsItem] | Unset):
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
    render_mode: MaterialDetailRenderMode | Unset = "text"
    extractor: str | Unset = ""
    content_format: MaterialDetailContentFormat | Unset = "plain_text"
    source_type: str | Unset = "upload"
    source_url: str | Unset = ""
    revision: int | Unset = 1
    annotation_count: int | Unset = 0
    outline: list[MaterialDetailOutlineItem] | Unset = UNSET
    outline_text: str | Unset = ""
    unit_refs: list[MaterialDetailUnitRefsItem] | Unset = UNSET
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

        outline: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.outline, Unset):
            outline = []
            for outline_item_data in self.outline:
                outline_item = outline_item_data.to_dict()
                outline.append(outline_item)

        outline_text = self.outline_text

        unit_refs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.unit_refs, Unset):
            unit_refs = []
            for unit_refs_item_data in self.unit_refs:
                unit_refs_item = unit_refs_item_data.to_dict()
                unit_refs.append(unit_refs_item)

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
        if outline is not UNSET:
            field_dict["outline"] = outline
        if outline_text is not UNSET:
            field_dict["outline_text"] = outline_text
        if unit_refs is not UNSET:
            field_dict["unit_refs"] = unit_refs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.material_detail_outline_item import MaterialDetailOutlineItem  # noqa: PLC0415
        from ..models.material_detail_unit_refs_item import MaterialDetailUnitRefsItem  # noqa: PLC0415

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
        render_mode: MaterialDetailRenderMode | Unset
        if isinstance(_render_mode, Unset):
            render_mode = UNSET
        else:
            render_mode = check_material_detail_render_mode(_render_mode)

        extractor = d.pop("extractor", UNSET)

        _content_format = d.pop("content_format", UNSET)
        content_format: MaterialDetailContentFormat | Unset
        if isinstance(_content_format, Unset):
            content_format = UNSET
        else:
            content_format = check_material_detail_content_format(_content_format)

        source_type = d.pop("source_type", UNSET)

        source_url = d.pop("source_url", UNSET)

        revision = d.pop("revision", UNSET)

        annotation_count = d.pop("annotation_count", UNSET)

        _outline = d.pop("outline", UNSET)
        outline: list[MaterialDetailOutlineItem] | Unset = UNSET
        if _outline is not UNSET:
            outline = []
            for outline_item_data in _outline:
                outline_item = MaterialDetailOutlineItem.from_dict(outline_item_data)

                outline.append(outline_item)

        outline_text = d.pop("outline_text", UNSET)

        _unit_refs = d.pop("unit_refs", UNSET)
        unit_refs: list[MaterialDetailUnitRefsItem] | Unset = UNSET
        if _unit_refs is not UNSET:
            unit_refs = []
            for unit_refs_item_data in _unit_refs:
                unit_refs_item = MaterialDetailUnitRefsItem.from_dict(unit_refs_item_data)

                unit_refs.append(unit_refs_item)

        material_detail = cls(
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
            outline=outline,
            outline_text=outline_text,
            unit_refs=unit_refs,
        )

        material_detail.additional_properties = d
        return material_detail

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
