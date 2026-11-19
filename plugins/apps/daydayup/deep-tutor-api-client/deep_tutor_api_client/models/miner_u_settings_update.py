from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.miner_u_settings_update_mode import MinerUSettingsUpdateMode, check_miner_u_settings_update_mode
from ..models.miner_u_settings_update_model_download_source import (
    MinerUSettingsUpdateModelDownloadSource,
    check_miner_u_settings_update_model_download_source,
)
from ..models.miner_u_settings_update_model_version import (
    MinerUSettingsUpdateModelVersion,
    check_miner_u_settings_update_model_version,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MinerUSettingsUpdate")


@_attrs_define
class MinerUSettingsUpdate:
    """MinerU document-parsing backend settings.

    ``api_token`` is tri-state: ``None`` keeps the stored token (the UI sends
    None when the user didn't edit the secret field), ``""`` clears it, and a
    non-empty string or string array replaces it. The GET payload never echoes
    the raw token.

        Attributes:
            mode (MinerUSettingsUpdateMode | Unset):  Default: 'local'.
            api_base_url (str | Unset):  Default: 'https://mineru.net'.
            api_token (list[str] | None | str | Unset):
            local_cli_path (str | Unset):  Default: ''.
            model_download_source (MinerUSettingsUpdateModelDownloadSource | Unset):  Default: 'huggingface'.
            model_download_endpoint (str | Unset):  Default: ''.
            model_version (MinerUSettingsUpdateModelVersion | Unset):  Default: 'pipeline'.
            language (str | Unset):  Default: 'auto'.
            enable_formula (bool | Unset):  Default: True.
            enable_table (bool | Unset):  Default: True.
            is_ocr (bool | Unset):  Default: False.
            allow_local_model_download (bool | Unset):  Default: False.
    """

    mode: MinerUSettingsUpdateMode | Unset = "local"
    api_base_url: str | Unset = "https://mineru.net"
    api_token: list[str] | None | str | Unset = UNSET
    local_cli_path: str | Unset = ""
    model_download_source: MinerUSettingsUpdateModelDownloadSource | Unset = "huggingface"
    model_download_endpoint: str | Unset = ""
    model_version: MinerUSettingsUpdateModelVersion | Unset = "pipeline"
    language: str | Unset = "auto"
    enable_formula: bool | Unset = True
    enable_table: bool | Unset = True
    is_ocr: bool | Unset = False
    allow_local_model_download: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode

        api_base_url = self.api_base_url

        api_token: list[str] | None | str | Unset
        if isinstance(self.api_token, Unset):
            api_token = UNSET
        elif isinstance(self.api_token, list):
            api_token = self.api_token

        else:
            api_token = self.api_token

        local_cli_path = self.local_cli_path

        model_download_source: str | Unset = UNSET
        if not isinstance(self.model_download_source, Unset):
            model_download_source = self.model_download_source

        model_download_endpoint = self.model_download_endpoint

        model_version: str | Unset = UNSET
        if not isinstance(self.model_version, Unset):
            model_version = self.model_version

        language = self.language

        enable_formula = self.enable_formula

        enable_table = self.enable_table

        is_ocr = self.is_ocr

        allow_local_model_download = self.allow_local_model_download

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if api_base_url is not UNSET:
            field_dict["api_base_url"] = api_base_url
        if api_token is not UNSET:
            field_dict["api_token"] = api_token
        if local_cli_path is not UNSET:
            field_dict["local_cli_path"] = local_cli_path
        if model_download_source is not UNSET:
            field_dict["model_download_source"] = model_download_source
        if model_download_endpoint is not UNSET:
            field_dict["model_download_endpoint"] = model_download_endpoint
        if model_version is not UNSET:
            field_dict["model_version"] = model_version
        if language is not UNSET:
            field_dict["language"] = language
        if enable_formula is not UNSET:
            field_dict["enable_formula"] = enable_formula
        if enable_table is not UNSET:
            field_dict["enable_table"] = enable_table
        if is_ocr is not UNSET:
            field_dict["is_ocr"] = is_ocr
        if allow_local_model_download is not UNSET:
            field_dict["allow_local_model_download"] = allow_local_model_download

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: MinerUSettingsUpdateMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = check_miner_u_settings_update_mode(_mode)

        api_base_url = d.pop("api_base_url", UNSET)

        def _parse_api_token(data: object) -> list[str] | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                api_token_type_1 = cast(list[str], data)

                return api_token_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | str | Unset, data)

        api_token = _parse_api_token(d.pop("api_token", UNSET))

        local_cli_path = d.pop("local_cli_path", UNSET)

        _model_download_source = d.pop("model_download_source", UNSET)
        model_download_source: MinerUSettingsUpdateModelDownloadSource | Unset
        if isinstance(_model_download_source, Unset):
            model_download_source = UNSET
        else:
            model_download_source = check_miner_u_settings_update_model_download_source(_model_download_source)

        model_download_endpoint = d.pop("model_download_endpoint", UNSET)

        _model_version = d.pop("model_version", UNSET)
        model_version: MinerUSettingsUpdateModelVersion | Unset
        if isinstance(_model_version, Unset):
            model_version = UNSET
        else:
            model_version = check_miner_u_settings_update_model_version(_model_version)

        language = d.pop("language", UNSET)

        enable_formula = d.pop("enable_formula", UNSET)

        enable_table = d.pop("enable_table", UNSET)

        is_ocr = d.pop("is_ocr", UNSET)

        allow_local_model_download = d.pop("allow_local_model_download", UNSET)

        miner_u_settings_update = cls(
            mode=mode,
            api_base_url=api_base_url,
            api_token=api_token,
            local_cli_path=local_cli_path,
            model_download_source=model_download_source,
            model_download_endpoint=model_download_endpoint,
            model_version=model_version,
            language=language,
            enable_formula=enable_formula,
            enable_table=enable_table,
            is_ocr=is_ocr,
            allow_local_model_download=allow_local_model_download,
        )

        miner_u_settings_update.additional_properties = d
        return miner_u_settings_update

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
