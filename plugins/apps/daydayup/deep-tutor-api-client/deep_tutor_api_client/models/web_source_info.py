from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.web_source_info_bilingual_pairings_item import WebSourceInfoBilingualPairingsItem
    from ..models.web_source_info_navigation_type_0 import WebSourceInfoNavigationType0


T = TypeVar("T", bound="WebSourceInfo")


@_attrs_define
class WebSourceInfo:
    """
    Attributes:
        id (str):
        url (str):
        max_depth (int | Unset):  Default: 3.
        max_pages (int | Unset):  Default: 200.
        enabled (bool | Unset):  Default: True.
        auto_sync_enabled (bool | Unset):  Default: True.
        sync_interval_hours (int | Unset):  Default: 24.
        page_count (int | Unset):  Default: 0.
        last_synced_at (str | Unset):  Default: ''.
        last_sync_status (str | Unset):  Default: 'pending'.
        last_sync_error (None | str | Unset):
        added_at (str | Unset):  Default: ''.
        navigation (None | Unset | WebSourceInfoNavigationType0):
        bilingual_pairings (list[WebSourceInfoBilingualPairingsItem] | Unset):
    """

    id: str
    url: str
    max_depth: int | Unset = 3
    max_pages: int | Unset = 200
    enabled: bool | Unset = True
    auto_sync_enabled: bool | Unset = True
    sync_interval_hours: int | Unset = 24
    page_count: int | Unset = 0
    last_synced_at: str | Unset = ""
    last_sync_status: str | Unset = "pending"
    last_sync_error: None | str | Unset = UNSET
    added_at: str | Unset = ""
    navigation: None | Unset | WebSourceInfoNavigationType0 = UNSET
    bilingual_pairings: list[WebSourceInfoBilingualPairingsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.web_source_info_navigation_type_0 import WebSourceInfoNavigationType0  # noqa: PLC0415

        id = self.id

        url = self.url

        max_depth = self.max_depth

        max_pages = self.max_pages

        enabled = self.enabled

        auto_sync_enabled = self.auto_sync_enabled

        sync_interval_hours = self.sync_interval_hours

        page_count = self.page_count

        last_synced_at = self.last_synced_at

        last_sync_status = self.last_sync_status

        last_sync_error: None | str | Unset
        if isinstance(self.last_sync_error, Unset):
            last_sync_error = UNSET
        else:
            last_sync_error = self.last_sync_error

        added_at = self.added_at

        navigation: dict[str, Any] | None | Unset
        if isinstance(self.navigation, Unset):
            navigation = UNSET
        elif isinstance(self.navigation, WebSourceInfoNavigationType0):
            navigation = self.navigation.to_dict()
        else:
            navigation = self.navigation

        bilingual_pairings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.bilingual_pairings, Unset):
            bilingual_pairings = []
            for bilingual_pairings_item_data in self.bilingual_pairings:
                bilingual_pairings_item = bilingual_pairings_item_data.to_dict()
                bilingual_pairings.append(bilingual_pairings_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "url": url,
            }
        )
        if max_depth is not UNSET:
            field_dict["max_depth"] = max_depth
        if max_pages is not UNSET:
            field_dict["max_pages"] = max_pages
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if auto_sync_enabled is not UNSET:
            field_dict["auto_sync_enabled"] = auto_sync_enabled
        if sync_interval_hours is not UNSET:
            field_dict["sync_interval_hours"] = sync_interval_hours
        if page_count is not UNSET:
            field_dict["page_count"] = page_count
        if last_synced_at is not UNSET:
            field_dict["last_synced_at"] = last_synced_at
        if last_sync_status is not UNSET:
            field_dict["last_sync_status"] = last_sync_status
        if last_sync_error is not UNSET:
            field_dict["last_sync_error"] = last_sync_error
        if added_at is not UNSET:
            field_dict["added_at"] = added_at
        if navigation is not UNSET:
            field_dict["navigation"] = navigation
        if bilingual_pairings is not UNSET:
            field_dict["bilingual_pairings"] = bilingual_pairings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.web_source_info_bilingual_pairings_item import WebSourceInfoBilingualPairingsItem  # noqa: PLC0415
        from ..models.web_source_info_navigation_type_0 import WebSourceInfoNavigationType0  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        url = d.pop("url")

        max_depth = d.pop("max_depth", UNSET)

        max_pages = d.pop("max_pages", UNSET)

        enabled = d.pop("enabled", UNSET)

        auto_sync_enabled = d.pop("auto_sync_enabled", UNSET)

        sync_interval_hours = d.pop("sync_interval_hours", UNSET)

        page_count = d.pop("page_count", UNSET)

        last_synced_at = d.pop("last_synced_at", UNSET)

        last_sync_status = d.pop("last_sync_status", UNSET)

        def _parse_last_sync_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_sync_error = _parse_last_sync_error(d.pop("last_sync_error", UNSET))

        added_at = d.pop("added_at", UNSET)

        def _parse_navigation(data: object) -> None | Unset | WebSourceInfoNavigationType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                navigation_type_0 = WebSourceInfoNavigationType0.from_dict(data)

                return navigation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WebSourceInfoNavigationType0, data)

        navigation = _parse_navigation(d.pop("navigation", UNSET))

        _bilingual_pairings = d.pop("bilingual_pairings", UNSET)
        bilingual_pairings: list[WebSourceInfoBilingualPairingsItem] | Unset = UNSET
        if _bilingual_pairings is not UNSET:
            bilingual_pairings = []
            for bilingual_pairings_item_data in _bilingual_pairings:
                bilingual_pairings_item = WebSourceInfoBilingualPairingsItem.from_dict(bilingual_pairings_item_data)

                bilingual_pairings.append(bilingual_pairings_item)

        web_source_info = cls(
            id=id,
            url=url,
            max_depth=max_depth,
            max_pages=max_pages,
            enabled=enabled,
            auto_sync_enabled=auto_sync_enabled,
            sync_interval_hours=sync_interval_hours,
            page_count=page_count,
            last_synced_at=last_synced_at,
            last_sync_status=last_sync_status,
            last_sync_error=last_sync_error,
            added_at=added_at,
            navigation=navigation,
            bilingual_pairings=bilingual_pairings,
        )

        web_source_info.additional_properties = d
        return web_source_info

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
