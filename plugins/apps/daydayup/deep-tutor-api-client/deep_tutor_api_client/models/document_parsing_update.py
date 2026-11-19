from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_parsing_update_engines_type_0 import DocumentParsingUpdateEnginesType0
    from ..models.image_description_model_selection import ImageDescriptionModelSelection


T = TypeVar("T", bound="DocumentParsingUpdate")


@_attrs_define
class DocumentParsingUpdate:
    """Document-parsing settings update (the multi-engine control panel).

    ``engine`` (when provided) switches the active parse engine. ``engines``
    carries partial per-engine updates merged over the stored slices. For the
    MinerU engine, ``api_token`` stays tri-state: omit it (or send ``None``) to
    keep the stored token, ``""`` clears it, a non-empty string replaces it.
    The MinerU engine's own knobs can also be edited via the legacy
    ``/mineru`` endpoints; both preserve the other engines' settings.

        Attributes:
            engine (None | str | Unset):
            engines (DocumentParsingUpdateEnginesType0 | None | Unset):
            image_caption (bool | None | Unset):
            image_description_model (ImageDescriptionModelSelection | None | Unset):
    """

    engine: None | str | Unset = UNSET
    engines: DocumentParsingUpdateEnginesType0 | None | Unset = UNSET
    image_caption: bool | None | Unset = UNSET
    image_description_model: ImageDescriptionModelSelection | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_parsing_update_engines_type_0 import DocumentParsingUpdateEnginesType0  # noqa: PLC0415
        from ..models.image_description_model_selection import ImageDescriptionModelSelection  # noqa: PLC0415

        engine: None | str | Unset
        if isinstance(self.engine, Unset):
            engine = UNSET
        else:
            engine = self.engine

        engines: dict[str, Any] | None | Unset
        if isinstance(self.engines, Unset):
            engines = UNSET
        elif isinstance(self.engines, DocumentParsingUpdateEnginesType0):
            engines = self.engines.to_dict()
        else:
            engines = self.engines

        image_caption: bool | None | Unset
        if isinstance(self.image_caption, Unset):
            image_caption = UNSET
        else:
            image_caption = self.image_caption

        image_description_model: dict[str, Any] | None | Unset
        if isinstance(self.image_description_model, Unset):
            image_description_model = UNSET
        elif isinstance(self.image_description_model, ImageDescriptionModelSelection):
            image_description_model = self.image_description_model.to_dict()
        else:
            image_description_model = self.image_description_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if engine is not UNSET:
            field_dict["engine"] = engine
        if engines is not UNSET:
            field_dict["engines"] = engines
        if image_caption is not UNSET:
            field_dict["image_caption"] = image_caption
        if image_description_model is not UNSET:
            field_dict["image_description_model"] = image_description_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_parsing_update_engines_type_0 import DocumentParsingUpdateEnginesType0  # noqa: PLC0415
        from ..models.image_description_model_selection import ImageDescriptionModelSelection  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_engine(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        engine = _parse_engine(d.pop("engine", UNSET))

        def _parse_engines(data: object) -> DocumentParsingUpdateEnginesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                engines_type_0 = DocumentParsingUpdateEnginesType0.from_dict(data)

                return engines_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentParsingUpdateEnginesType0 | None | Unset, data)

        engines = _parse_engines(d.pop("engines", UNSET))

        def _parse_image_caption(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        image_caption = _parse_image_caption(d.pop("image_caption", UNSET))

        def _parse_image_description_model(data: object) -> ImageDescriptionModelSelection | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                image_description_model_type_0 = ImageDescriptionModelSelection.from_dict(data)

                return image_description_model_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ImageDescriptionModelSelection | None | Unset, data)

        image_description_model = _parse_image_description_model(d.pop("image_description_model", UNSET))

        document_parsing_update = cls(
            engine=engine,
            engines=engines,
            image_caption=image_caption,
            image_description_model=image_description_model,
        )

        document_parsing_update.additional_properties = d
        return document_parsing_update

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
