from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tour_complete_payload_catalog_type_0 import TourCompletePayloadCatalogType0
    from ..models.tour_complete_payload_test_results_type_0 import TourCompletePayloadTestResultsType0


T = TypeVar("T", bound="TourCompletePayload")


@_attrs_define
class TourCompletePayload:
    """
    Attributes:
        catalog (None | TourCompletePayloadCatalogType0 | Unset):
        test_results (None | TourCompletePayloadTestResultsType0 | Unset):
    """

    catalog: None | TourCompletePayloadCatalogType0 | Unset = UNSET
    test_results: None | TourCompletePayloadTestResultsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tour_complete_payload_catalog_type_0 import TourCompletePayloadCatalogType0  # noqa: PLC0415
        from ..models.tour_complete_payload_test_results_type_0 import (
            TourCompletePayloadTestResultsType0,  # noqa: PLC0415
        )

        catalog: dict[str, Any] | None | Unset
        if isinstance(self.catalog, Unset):
            catalog = UNSET
        elif isinstance(self.catalog, TourCompletePayloadCatalogType0):
            catalog = self.catalog.to_dict()
        else:
            catalog = self.catalog

        test_results: dict[str, Any] | None | Unset
        if isinstance(self.test_results, Unset):
            test_results = UNSET
        elif isinstance(self.test_results, TourCompletePayloadTestResultsType0):
            test_results = self.test_results.to_dict()
        else:
            test_results = self.test_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if catalog is not UNSET:
            field_dict["catalog"] = catalog
        if test_results is not UNSET:
            field_dict["test_results"] = test_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tour_complete_payload_catalog_type_0 import TourCompletePayloadCatalogType0  # noqa: PLC0415
        from ..models.tour_complete_payload_test_results_type_0 import (
            TourCompletePayloadTestResultsType0,  # noqa: PLC0415
        )

        d = dict(src_dict)

        def _parse_catalog(data: object) -> None | TourCompletePayloadCatalogType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                catalog_type_0 = TourCompletePayloadCatalogType0.from_dict(data)

                return catalog_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TourCompletePayloadCatalogType0 | Unset, data)

        catalog = _parse_catalog(d.pop("catalog", UNSET))

        def _parse_test_results(data: object) -> None | TourCompletePayloadTestResultsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                test_results_type_0 = TourCompletePayloadTestResultsType0.from_dict(data)

                return test_results_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TourCompletePayloadTestResultsType0 | Unset, data)

        test_results = _parse_test_results(d.pop("test_results", UNSET))

        tour_complete_payload = cls(
            catalog=catalog,
            test_results=test_results,
        )

        tour_complete_payload.additional_properties = d
        return tour_complete_payload

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
