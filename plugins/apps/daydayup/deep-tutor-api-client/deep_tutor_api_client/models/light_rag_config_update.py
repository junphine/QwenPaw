from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.light_rag_role_models import LightRagRoleModels


T = TypeVar("T", bound="LightRagConfigUpdate")


@_attrs_define
class LightRagConfigUpdate:
    """Partial update for LightRAG query + indexing knobs (omitted fields kept).

    Attributes:
        role_models (LightRagRoleModels | None | Unset):
        top_k (int | None | Unset):
        response_type (None | str | Unset):
        max_concurrent_files (int | None | Unset):
        llm_model_max_async (int | None | Unset):
        entity_extract_max_gleaning (int | None | Unset):
        llm_timeout (int | None | Unset):
        llm_profile_id (None | str | Unset):
        llm_model_id (None | str | Unset):
    """

    role_models: LightRagRoleModels | None | Unset = UNSET
    top_k: int | None | Unset = UNSET
    response_type: None | str | Unset = UNSET
    max_concurrent_files: int | None | Unset = UNSET
    llm_model_max_async: int | None | Unset = UNSET
    entity_extract_max_gleaning: int | None | Unset = UNSET
    llm_timeout: int | None | Unset = UNSET
    llm_profile_id: None | str | Unset = UNSET
    llm_model_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.light_rag_role_models import LightRagRoleModels  # noqa: PLC0415

        role_models: dict[str, Any] | None | Unset
        if isinstance(self.role_models, Unset):
            role_models = UNSET
        elif isinstance(self.role_models, LightRagRoleModels):
            role_models = self.role_models.to_dict()
        else:
            role_models = self.role_models

        top_k: int | None | Unset
        if isinstance(self.top_k, Unset):
            top_k = UNSET
        else:
            top_k = self.top_k

        response_type: None | str | Unset
        if isinstance(self.response_type, Unset):
            response_type = UNSET
        else:
            response_type = self.response_type

        max_concurrent_files: int | None | Unset
        if isinstance(self.max_concurrent_files, Unset):
            max_concurrent_files = UNSET
        else:
            max_concurrent_files = self.max_concurrent_files

        llm_model_max_async: int | None | Unset
        if isinstance(self.llm_model_max_async, Unset):
            llm_model_max_async = UNSET
        else:
            llm_model_max_async = self.llm_model_max_async

        entity_extract_max_gleaning: int | None | Unset
        if isinstance(self.entity_extract_max_gleaning, Unset):
            entity_extract_max_gleaning = UNSET
        else:
            entity_extract_max_gleaning = self.entity_extract_max_gleaning

        llm_timeout: int | None | Unset
        if isinstance(self.llm_timeout, Unset):
            llm_timeout = UNSET
        else:
            llm_timeout = self.llm_timeout

        llm_profile_id: None | str | Unset
        if isinstance(self.llm_profile_id, Unset):
            llm_profile_id = UNSET
        else:
            llm_profile_id = self.llm_profile_id

        llm_model_id: None | str | Unset
        if isinstance(self.llm_model_id, Unset):
            llm_model_id = UNSET
        else:
            llm_model_id = self.llm_model_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if role_models is not UNSET:
            field_dict["role_models"] = role_models
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if response_type is not UNSET:
            field_dict["response_type"] = response_type
        if max_concurrent_files is not UNSET:
            field_dict["max_concurrent_files"] = max_concurrent_files
        if llm_model_max_async is not UNSET:
            field_dict["llm_model_max_async"] = llm_model_max_async
        if entity_extract_max_gleaning is not UNSET:
            field_dict["entity_extract_max_gleaning"] = entity_extract_max_gleaning
        if llm_timeout is not UNSET:
            field_dict["llm_timeout"] = llm_timeout
        if llm_profile_id is not UNSET:
            field_dict["llm_profile_id"] = llm_profile_id
        if llm_model_id is not UNSET:
            field_dict["llm_model_id"] = llm_model_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.light_rag_role_models import LightRagRoleModels  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_role_models(data: object) -> LightRagRoleModels | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                role_models_type_0 = LightRagRoleModels.from_dict(data)

                return role_models_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LightRagRoleModels | None | Unset, data)

        role_models = _parse_role_models(d.pop("role_models", UNSET))

        def _parse_top_k(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        top_k = _parse_top_k(d.pop("top_k", UNSET))

        def _parse_response_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        response_type = _parse_response_type(d.pop("response_type", UNSET))

        def _parse_max_concurrent_files(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_concurrent_files = _parse_max_concurrent_files(d.pop("max_concurrent_files", UNSET))

        def _parse_llm_model_max_async(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        llm_model_max_async = _parse_llm_model_max_async(d.pop("llm_model_max_async", UNSET))

        def _parse_entity_extract_max_gleaning(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        entity_extract_max_gleaning = _parse_entity_extract_max_gleaning(d.pop("entity_extract_max_gleaning", UNSET))

        def _parse_llm_timeout(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        llm_timeout = _parse_llm_timeout(d.pop("llm_timeout", UNSET))

        def _parse_llm_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        llm_profile_id = _parse_llm_profile_id(d.pop("llm_profile_id", UNSET))

        def _parse_llm_model_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        llm_model_id = _parse_llm_model_id(d.pop("llm_model_id", UNSET))

        light_rag_config_update = cls(
            role_models=role_models,
            top_k=top_k,
            response_type=response_type,
            max_concurrent_files=max_concurrent_files,
            llm_model_max_async=llm_model_max_async,
            entity_extract_max_gleaning=entity_extract_max_gleaning,
            llm_timeout=llm_timeout,
            llm_profile_id=llm_profile_id,
            llm_model_id=llm_model_id,
        )

        light_rag_config_update.additional_properties = d
        return light_rag_config_update

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
