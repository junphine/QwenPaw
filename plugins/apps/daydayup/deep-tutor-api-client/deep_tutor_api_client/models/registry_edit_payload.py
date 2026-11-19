from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.registry_edit_payload_kind import RegistryEditPayloadKind, check_registry_edit_payload_kind
from ..models.registry_edit_payload_service_type_0 import (
    RegistryEditPayloadServiceType0,
    check_registry_edit_payload_service_type_0,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.registry_edit_payload_config_type_0 import RegistryEditPayloadConfigType0
    from ..models.registry_edit_payload_fields_type_0 import RegistryEditPayloadFieldsType0
    from ..models.registry_edit_payload_model_type_0 import RegistryEditPayloadModelType0
    from ..models.registry_edit_payload_ref_type_0 import RegistryEditPayloadRefType0
    from ..models.registry_edit_payload_task_type_0 import RegistryEditPayloadTaskType0


T = TypeVar("T", bound="RegistryEditPayload")


@_attrs_define
class RegistryEditPayload:
    """
    Attributes:
        kind (RegistryEditPayloadKind):
        task (None | RegistryEditPayloadTaskType0 | Unset):
        ref (None | RegistryEditPayloadRefType0 | Unset):
        fields (None | RegistryEditPayloadFieldsType0 | Unset):
        service (None | RegistryEditPayloadServiceType0 | Unset):
        profile_id (None | str | Unset):
        model_id (None | str | Unset):
        model (None | RegistryEditPayloadModelType0 | Unset):
        config (None | RegistryEditPayloadConfigType0 | Unset):
        delete (bool | Unset):  Default: False.
    """

    kind: RegistryEditPayloadKind
    task: None | RegistryEditPayloadTaskType0 | Unset = UNSET
    ref: None | RegistryEditPayloadRefType0 | Unset = UNSET
    fields: None | RegistryEditPayloadFieldsType0 | Unset = UNSET
    service: None | RegistryEditPayloadServiceType0 | Unset = UNSET
    profile_id: None | str | Unset = UNSET
    model_id: None | str | Unset = UNSET
    model: None | RegistryEditPayloadModelType0 | Unset = UNSET
    config: None | RegistryEditPayloadConfigType0 | Unset = UNSET
    delete: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.registry_edit_payload_config_type_0 import RegistryEditPayloadConfigType0  # noqa: PLC0415
        from ..models.registry_edit_payload_fields_type_0 import RegistryEditPayloadFieldsType0  # noqa: PLC0415
        from ..models.registry_edit_payload_model_type_0 import RegistryEditPayloadModelType0  # noqa: PLC0415
        from ..models.registry_edit_payload_ref_type_0 import RegistryEditPayloadRefType0  # noqa: PLC0415
        from ..models.registry_edit_payload_task_type_0 import RegistryEditPayloadTaskType0  # noqa: PLC0415

        kind: str = self.kind

        task: dict[str, Any] | None | Unset
        if isinstance(self.task, Unset):
            task = UNSET
        elif isinstance(self.task, RegistryEditPayloadTaskType0):
            task = self.task.to_dict()
        else:
            task = self.task

        ref: dict[str, Any] | None | Unset
        if isinstance(self.ref, Unset):
            ref = UNSET
        elif isinstance(self.ref, RegistryEditPayloadRefType0):
            ref = self.ref.to_dict()
        else:
            ref = self.ref

        fields: dict[str, Any] | None | Unset
        if isinstance(self.fields, Unset):
            fields = UNSET
        elif isinstance(self.fields, RegistryEditPayloadFieldsType0):
            fields = self.fields.to_dict()
        else:
            fields = self.fields

        service: None | str | Unset
        if isinstance(self.service, Unset):
            service = UNSET
        elif isinstance(self.service, str):
            service = self.service
        else:
            service = self.service

        profile_id: None | str | Unset
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        model_id: None | str | Unset
        if isinstance(self.model_id, Unset):
            model_id = UNSET
        else:
            model_id = self.model_id

        model: dict[str, Any] | None | Unset
        if isinstance(self.model, Unset):
            model = UNSET
        elif isinstance(self.model, RegistryEditPayloadModelType0):
            model = self.model.to_dict()
        else:
            model = self.model

        config: dict[str, Any] | None | Unset
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, RegistryEditPayloadConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        delete = self.delete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
            }
        )
        if task is not UNSET:
            field_dict["task"] = task
        if ref is not UNSET:
            field_dict["ref"] = ref
        if fields is not UNSET:
            field_dict["fields"] = fields
        if service is not UNSET:
            field_dict["service"] = service
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if model_id is not UNSET:
            field_dict["model_id"] = model_id
        if model is not UNSET:
            field_dict["model"] = model
        if config is not UNSET:
            field_dict["config"] = config
        if delete is not UNSET:
            field_dict["delete"] = delete

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.registry_edit_payload_config_type_0 import RegistryEditPayloadConfigType0  # noqa: PLC0415
        from ..models.registry_edit_payload_fields_type_0 import RegistryEditPayloadFieldsType0  # noqa: PLC0415
        from ..models.registry_edit_payload_model_type_0 import RegistryEditPayloadModelType0  # noqa: PLC0415
        from ..models.registry_edit_payload_ref_type_0 import RegistryEditPayloadRefType0  # noqa: PLC0415
        from ..models.registry_edit_payload_task_type_0 import RegistryEditPayloadTaskType0  # noqa: PLC0415

        d = dict(src_dict)
        kind = check_registry_edit_payload_kind(d.pop("kind"))

        def _parse_task(data: object) -> None | RegistryEditPayloadTaskType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                task_type_0 = RegistryEditPayloadTaskType0.from_dict(data)

                return task_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadTaskType0 | Unset, data)

        task = _parse_task(d.pop("task", UNSET))

        def _parse_ref(data: object) -> None | RegistryEditPayloadRefType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ref_type_0 = RegistryEditPayloadRefType0.from_dict(data)

                return ref_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadRefType0 | Unset, data)

        ref = _parse_ref(d.pop("ref", UNSET))

        def _parse_fields(data: object) -> None | RegistryEditPayloadFieldsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fields_type_0 = RegistryEditPayloadFieldsType0.from_dict(data)

                return fields_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadFieldsType0 | Unset, data)

        fields = _parse_fields(d.pop("fields", UNSET))

        def _parse_service(data: object) -> None | RegistryEditPayloadServiceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_type_0 = check_registry_edit_payload_service_type_0(data)

                return service_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadServiceType0 | Unset, data)

        service = _parse_service(d.pop("service", UNSET))

        def _parse_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        def _parse_model_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model_id = _parse_model_id(d.pop("model_id", UNSET))

        def _parse_model(data: object) -> None | RegistryEditPayloadModelType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                model_type_0 = RegistryEditPayloadModelType0.from_dict(data)

                return model_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadModelType0 | Unset, data)

        model = _parse_model(d.pop("model", UNSET))

        def _parse_config(data: object) -> None | RegistryEditPayloadConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = RegistryEditPayloadConfigType0.from_dict(data)

                return config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryEditPayloadConfigType0 | Unset, data)

        config = _parse_config(d.pop("config", UNSET))

        delete = d.pop("delete", UNSET)

        registry_edit_payload = cls(
            kind=kind,
            task=task,
            ref=ref,
            fields=fields,
            service=service,
            profile_id=profile_id,
            model_id=model_id,
            model=model,
            config=config,
            delete=delete,
        )

        registry_edit_payload.additional_properties = d
        return registry_edit_payload

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
