from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageTotals")


@_attrs_define
class UsageTotals:
    """
    Attributes:
        total_tokens (int | Unset):  Default: 0.
        prompt_tokens (int | Unset):  Default: 0.
        completion_tokens (int | Unset):  Default: 0.
        total_calls (int | Unset):  Default: 0.
        cache_read_input_tokens (int | Unset):  Default: 0.
        cache_creation_input_tokens (int | Unset):  Default: 0.
        cache_input_tokens (int | Unset):  Default: 0.
        cache_reported_calls (int | Unset):  Default: 0.
        cache_hit_rate (float | None | Unset):
        ttft_seconds (float | None | Unset):
        tokens_per_second (float | None | Unset):
        duration_seconds (float | Unset):  Default: 0.0.
        estimated_calls (int | Unset):  Default: 0.
    """

    total_tokens: int | Unset = 0
    prompt_tokens: int | Unset = 0
    completion_tokens: int | Unset = 0
    total_calls: int | Unset = 0
    cache_read_input_tokens: int | Unset = 0
    cache_creation_input_tokens: int | Unset = 0
    cache_input_tokens: int | Unset = 0
    cache_reported_calls: int | Unset = 0
    cache_hit_rate: float | None | Unset = UNSET
    ttft_seconds: float | None | Unset = UNSET
    tokens_per_second: float | None | Unset = UNSET
    duration_seconds: float | Unset = 0.0
    estimated_calls: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_tokens = self.total_tokens

        prompt_tokens = self.prompt_tokens

        completion_tokens = self.completion_tokens

        total_calls = self.total_calls

        cache_read_input_tokens = self.cache_read_input_tokens

        cache_creation_input_tokens = self.cache_creation_input_tokens

        cache_input_tokens = self.cache_input_tokens

        cache_reported_calls = self.cache_reported_calls

        cache_hit_rate: float | None | Unset
        if isinstance(self.cache_hit_rate, Unset):
            cache_hit_rate = UNSET
        else:
            cache_hit_rate = self.cache_hit_rate

        ttft_seconds: float | None | Unset
        if isinstance(self.ttft_seconds, Unset):
            ttft_seconds = UNSET
        else:
            ttft_seconds = self.ttft_seconds

        tokens_per_second: float | None | Unset
        if isinstance(self.tokens_per_second, Unset):
            tokens_per_second = UNSET
        else:
            tokens_per_second = self.tokens_per_second

        duration_seconds = self.duration_seconds

        estimated_calls = self.estimated_calls

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_tokens is not UNSET:
            field_dict["total_tokens"] = total_tokens
        if prompt_tokens is not UNSET:
            field_dict["prompt_tokens"] = prompt_tokens
        if completion_tokens is not UNSET:
            field_dict["completion_tokens"] = completion_tokens
        if total_calls is not UNSET:
            field_dict["total_calls"] = total_calls
        if cache_read_input_tokens is not UNSET:
            field_dict["cache_read_input_tokens"] = cache_read_input_tokens
        if cache_creation_input_tokens is not UNSET:
            field_dict["cache_creation_input_tokens"] = cache_creation_input_tokens
        if cache_input_tokens is not UNSET:
            field_dict["cache_input_tokens"] = cache_input_tokens
        if cache_reported_calls is not UNSET:
            field_dict["cache_reported_calls"] = cache_reported_calls
        if cache_hit_rate is not UNSET:
            field_dict["cache_hit_rate"] = cache_hit_rate
        if ttft_seconds is not UNSET:
            field_dict["ttft_seconds"] = ttft_seconds
        if tokens_per_second is not UNSET:
            field_dict["tokens_per_second"] = tokens_per_second
        if duration_seconds is not UNSET:
            field_dict["duration_seconds"] = duration_seconds
        if estimated_calls is not UNSET:
            field_dict["estimated_calls"] = estimated_calls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_tokens = d.pop("total_tokens", UNSET)

        prompt_tokens = d.pop("prompt_tokens", UNSET)

        completion_tokens = d.pop("completion_tokens", UNSET)

        total_calls = d.pop("total_calls", UNSET)

        cache_read_input_tokens = d.pop("cache_read_input_tokens", UNSET)

        cache_creation_input_tokens = d.pop("cache_creation_input_tokens", UNSET)

        cache_input_tokens = d.pop("cache_input_tokens", UNSET)

        cache_reported_calls = d.pop("cache_reported_calls", UNSET)

        def _parse_cache_hit_rate(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cache_hit_rate = _parse_cache_hit_rate(d.pop("cache_hit_rate", UNSET))

        def _parse_ttft_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ttft_seconds = _parse_ttft_seconds(d.pop("ttft_seconds", UNSET))

        def _parse_tokens_per_second(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        tokens_per_second = _parse_tokens_per_second(d.pop("tokens_per_second", UNSET))

        duration_seconds = d.pop("duration_seconds", UNSET)

        estimated_calls = d.pop("estimated_calls", UNSET)

        usage_totals = cls(
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_calls=total_calls,
            cache_read_input_tokens=cache_read_input_tokens,
            cache_creation_input_tokens=cache_creation_input_tokens,
            cache_input_tokens=cache_input_tokens,
            cache_reported_calls=cache_reported_calls,
            cache_hit_rate=cache_hit_rate,
            ttft_seconds=ttft_seconds,
            tokens_per_second=tokens_per_second,
            duration_seconds=duration_seconds,
            estimated_calls=estimated_calls,
        )

        usage_totals.additional_properties = d
        return usage_totals

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
