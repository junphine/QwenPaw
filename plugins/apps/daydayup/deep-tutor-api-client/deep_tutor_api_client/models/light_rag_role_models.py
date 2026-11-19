from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.light_rag_model_selection import LightRagModelSelection
    from ..models.light_rag_role_model import LightRagRoleModel
    from ..models.light_rag_vision_model import LightRagVisionModel


T = TypeVar("T", bound="LightRagRoleModels")


@_attrs_define
class LightRagRoleModels:
    """Group the independent base model and its four role overrides.

    Attributes:
        base (LightRagModelSelection): Identify a catalog model and its optional reasoning selection.
        extract (LightRagRoleModel | Unset): Configure a text role through base inheritance or an explicit model.
        keyword (LightRagRoleModel | Unset): Configure a text role through base inheritance or an explicit model.
        query (LightRagRoleModel | Unset): Configure a text role through base inheritance or an explicit model.
        vlm (LightRagVisionModel | Unset): Configure disabled, inherited, or explicit vision model execution.
    """

    base: LightRagModelSelection
    extract: LightRagRoleModel | Unset = UNSET
    keyword: LightRagRoleModel | Unset = UNSET
    query: LightRagRoleModel | Unset = UNSET
    vlm: LightRagVisionModel | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        base = self.base.to_dict()

        extract: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extract, Unset):
            extract = self.extract.to_dict()

        keyword: dict[str, Any] | Unset = UNSET
        if not isinstance(self.keyword, Unset):
            keyword = self.keyword.to_dict()

        query: dict[str, Any] | Unset = UNSET
        if not isinstance(self.query, Unset):
            query = self.query.to_dict()

        vlm: dict[str, Any] | Unset = UNSET
        if not isinstance(self.vlm, Unset):
            vlm = self.vlm.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base": base,
            }
        )
        if extract is not UNSET:
            field_dict["extract"] = extract
        if keyword is not UNSET:
            field_dict["keyword"] = keyword
        if query is not UNSET:
            field_dict["query"] = query
        if vlm is not UNSET:
            field_dict["vlm"] = vlm

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.light_rag_model_selection import LightRagModelSelection  # noqa: PLC0415
        from ..models.light_rag_role_model import LightRagRoleModel  # noqa: PLC0415
        from ..models.light_rag_vision_model import LightRagVisionModel  # noqa: PLC0415

        d = dict(src_dict)
        base = LightRagModelSelection.from_dict(d.pop("base"))

        _extract = d.pop("extract", UNSET)
        extract: LightRagRoleModel | Unset
        if isinstance(_extract, Unset):
            extract = UNSET
        else:
            extract = LightRagRoleModel.from_dict(_extract)

        _keyword = d.pop("keyword", UNSET)
        keyword: LightRagRoleModel | Unset
        if isinstance(_keyword, Unset):
            keyword = UNSET
        else:
            keyword = LightRagRoleModel.from_dict(_keyword)

        _query = d.pop("query", UNSET)
        query: LightRagRoleModel | Unset
        if isinstance(_query, Unset):
            query = UNSET
        else:
            query = LightRagRoleModel.from_dict(_query)

        _vlm = d.pop("vlm", UNSET)
        vlm: LightRagVisionModel | Unset
        if isinstance(_vlm, Unset):
            vlm = UNSET
        else:
            vlm = LightRagVisionModel.from_dict(_vlm)

        light_rag_role_models = cls(
            base=base,
            extract=extract,
            keyword=keyword,
            query=query,
            vlm=vlm,
        )

        return light_rag_role_models
