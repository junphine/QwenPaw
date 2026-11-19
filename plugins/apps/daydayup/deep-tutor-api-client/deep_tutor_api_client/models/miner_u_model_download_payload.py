from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.miner_u_model_download_payload_model_type import (
    MinerUModelDownloadPayloadModelType,
    check_miner_u_model_download_payload_model_type,
)
from ..models.miner_u_model_download_payload_source import (
    MinerUModelDownloadPayloadSource,
    check_miner_u_model_download_payload_source,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MinerUModelDownloadPayload")


@_attrs_define
class MinerUModelDownloadPayload:
    """One-click model download request (draft form values, like /test).

    Attributes:
        model_type (MinerUModelDownloadPayloadModelType | Unset):  Default: 'pipeline'.
        source (MinerUModelDownloadPayloadSource | Unset):  Default: 'huggingface'.
        endpoint (str | Unset):  Default: ''.
        local_cli_path (str | Unset):  Default: ''.
    """

    model_type: MinerUModelDownloadPayloadModelType | Unset = "pipeline"
    source: MinerUModelDownloadPayloadSource | Unset = "huggingface"
    endpoint: str | Unset = ""
    local_cli_path: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model_type: str | Unset = UNSET
        if not isinstance(self.model_type, Unset):
            model_type = self.model_type

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        endpoint = self.endpoint

        local_cli_path = self.local_cli_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model_type is not UNSET:
            field_dict["model_type"] = model_type
        if source is not UNSET:
            field_dict["source"] = source
        if endpoint is not UNSET:
            field_dict["endpoint"] = endpoint
        if local_cli_path is not UNSET:
            field_dict["local_cli_path"] = local_cli_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _model_type = d.pop("model_type", UNSET)
        model_type: MinerUModelDownloadPayloadModelType | Unset
        if isinstance(_model_type, Unset):
            model_type = UNSET
        else:
            model_type = check_miner_u_model_download_payload_model_type(_model_type)

        _source = d.pop("source", UNSET)
        source: MinerUModelDownloadPayloadSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_miner_u_model_download_payload_source(_source)

        endpoint = d.pop("endpoint", UNSET)

        local_cli_path = d.pop("local_cli_path", UNSET)

        miner_u_model_download_payload = cls(
            model_type=model_type,
            source=source,
            endpoint=endpoint,
            local_cli_path=local_cli_path,
        )

        miner_u_model_download_payload.additional_properties = d
        return miner_u_model_download_payload

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
