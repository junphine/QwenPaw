from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LearnerProfileRequest")


@_attrs_define
class LearnerProfileRequest:
    """
    Attributes:
        age (int | None | Unset):
        grade_level (None | str | Unset):
        curriculum (None | str | Unset):
        language (None | str | Unset):
        reading_level (None | str | Unset):
        explanation_style (None | str | Unset):
    """

    age: int | None | Unset = UNSET
    grade_level: None | str | Unset = UNSET
    curriculum: None | str | Unset = UNSET
    language: None | str | Unset = UNSET
    reading_level: None | str | Unset = UNSET
    explanation_style: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        age: int | None | Unset
        if isinstance(self.age, Unset):
            age = UNSET
        else:
            age = self.age

        grade_level: None | str | Unset
        if isinstance(self.grade_level, Unset):
            grade_level = UNSET
        else:
            grade_level = self.grade_level

        curriculum: None | str | Unset
        if isinstance(self.curriculum, Unset):
            curriculum = UNSET
        else:
            curriculum = self.curriculum

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        reading_level: None | str | Unset
        if isinstance(self.reading_level, Unset):
            reading_level = UNSET
        else:
            reading_level = self.reading_level

        explanation_style: None | str | Unset
        if isinstance(self.explanation_style, Unset):
            explanation_style = UNSET
        else:
            explanation_style = self.explanation_style

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if age is not UNSET:
            field_dict["age"] = age
        if grade_level is not UNSET:
            field_dict["grade_level"] = grade_level
        if curriculum is not UNSET:
            field_dict["curriculum"] = curriculum
        if language is not UNSET:
            field_dict["language"] = language
        if reading_level is not UNSET:
            field_dict["reading_level"] = reading_level
        if explanation_style is not UNSET:
            field_dict["explanation_style"] = explanation_style

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_age(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        age = _parse_age(d.pop("age", UNSET))

        def _parse_grade_level(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        grade_level = _parse_grade_level(d.pop("grade_level", UNSET))

        def _parse_curriculum(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        curriculum = _parse_curriculum(d.pop("curriculum", UNSET))

        def _parse_language(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_reading_level(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reading_level = _parse_reading_level(d.pop("reading_level", UNSET))

        def _parse_explanation_style(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        explanation_style = _parse_explanation_style(d.pop("explanation_style", UNSET))

        learner_profile_request = cls(
            age=age,
            grade_level=grade_level,
            curriculum=curriculum,
            language=language,
            reading_level=reading_level,
            explanation_style=explanation_style,
        )

        learner_profile_request.additional_properties = d
        return learner_profile_request

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
