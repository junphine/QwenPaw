from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.upsert_entry_request_origin_type import (
    UpsertEntryRequestOriginType,
    check_upsert_entry_request_origin_type,
)
from ..models.upsert_entry_request_source import UpsertEntryRequestSource, check_upsert_entry_request_source
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.answer_image_upload import AnswerImageUpload
    from ..models.upsert_entry_request_options_type_0 import UpsertEntryRequestOptionsType0


T = TypeVar("T", bound="UpsertEntryRequest")


@_attrs_define
class UpsertEntryRequest:
    """
    Attributes:
        question_id (str):
        question (str):
        session_id (str | Unset):  Default: ''.
        origin_type (UpsertEntryRequestOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        turn_id (str | Unset):  Default: ''.
        question_type (str | Unset):  Default: ''.
        options (None | Unset | UpsertEntryRequestOptionsType0):
        correct_answer (str | Unset):  Default: ''.
        explanation (str | Unset):  Default: ''.
        difficulty (str | Unset):  Default: ''.
        user_answer (str | Unset):  Default: ''.
        user_answer_images (list[AnswerImageUpload] | None | Unset):
        source (UpsertEntryRequestSource | Unset):  Default: 'deep_question'.
        material_id (str | Unset):  Default: ''.
        material_title (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        section_title (str | Unset):  Default: ''.
        is_correct (bool | Unset):  Default: False.
        assessment_type (str | Unset):  Default: ''.
        result (str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        attempt_count (int | Unset):  Default: 1.
        hints_used (int | Unset):  Default: 0.
        confidence (float | None | Unset):
        response_time (float | None | Unset):
        quality (float | None | Unset):
    """

    question_id: str
    question: str
    session_id: str | Unset = ""
    origin_type: UpsertEntryRequestOriginType | Unset = "conversation"
    origin_ref: str | Unset = ""
    turn_id: str | Unset = ""
    question_type: str | Unset = ""
    options: None | Unset | UpsertEntryRequestOptionsType0 = UNSET
    correct_answer: str | Unset = ""
    explanation: str | Unset = ""
    difficulty: str | Unset = ""
    user_answer: str | Unset = ""
    user_answer_images: list[AnswerImageUpload] | None | Unset = UNSET
    source: UpsertEntryRequestSource | Unset = "deep_question"
    material_id: str | Unset = ""
    material_title: str | Unset = ""
    section_id: str | Unset = ""
    section_title: str | Unset = ""
    is_correct: bool | Unset = False
    assessment_type: str | Unset = ""
    result: str | Unset = ""
    mastery_path_id: str | Unset = ""
    knowledge_point_id: str | Unset = ""
    attempt_count: int | Unset = 1
    hints_used: int | Unset = 0
    confidence: float | None | Unset = UNSET
    response_time: float | None | Unset = UNSET
    quality: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.upsert_entry_request_options_type_0 import UpsertEntryRequestOptionsType0  # noqa: PLC0415

        question_id = self.question_id

        question = self.question

        session_id = self.session_id

        origin_type: str | Unset = UNSET
        if not isinstance(self.origin_type, Unset):
            origin_type = self.origin_type

        origin_ref = self.origin_ref

        turn_id = self.turn_id

        question_type = self.question_type

        options: dict[str, Any] | None | Unset
        if isinstance(self.options, Unset):
            options = UNSET
        elif isinstance(self.options, UpsertEntryRequestOptionsType0):
            options = self.options.to_dict()
        else:
            options = self.options

        correct_answer = self.correct_answer

        explanation = self.explanation

        difficulty = self.difficulty

        user_answer = self.user_answer

        user_answer_images: list[dict[str, Any]] | None | Unset
        if isinstance(self.user_answer_images, Unset):
            user_answer_images = UNSET
        elif isinstance(self.user_answer_images, list):
            user_answer_images = []
            for user_answer_images_type_0_item_data in self.user_answer_images:
                user_answer_images_type_0_item = user_answer_images_type_0_item_data.to_dict()
                user_answer_images.append(user_answer_images_type_0_item)

        else:
            user_answer_images = self.user_answer_images

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        material_id = self.material_id

        material_title = self.material_title

        section_id = self.section_id

        section_title = self.section_title

        is_correct = self.is_correct

        assessment_type = self.assessment_type

        result = self.result

        mastery_path_id = self.mastery_path_id

        knowledge_point_id = self.knowledge_point_id

        attempt_count = self.attempt_count

        hints_used = self.hints_used

        confidence: float | None | Unset
        if isinstance(self.confidence, Unset):
            confidence = UNSET
        else:
            confidence = self.confidence

        response_time: float | None | Unset
        if isinstance(self.response_time, Unset):
            response_time = UNSET
        else:
            response_time = self.response_time

        quality: float | None | Unset
        if isinstance(self.quality, Unset):
            quality = UNSET
        else:
            quality = self.quality

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "question_id": question_id,
                "question": question,
            }
        )
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if origin_type is not UNSET:
            field_dict["origin_type"] = origin_type
        if origin_ref is not UNSET:
            field_dict["origin_ref"] = origin_ref
        if turn_id is not UNSET:
            field_dict["turn_id"] = turn_id
        if question_type is not UNSET:
            field_dict["question_type"] = question_type
        if options is not UNSET:
            field_dict["options"] = options
        if correct_answer is not UNSET:
            field_dict["correct_answer"] = correct_answer
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if difficulty is not UNSET:
            field_dict["difficulty"] = difficulty
        if user_answer is not UNSET:
            field_dict["user_answer"] = user_answer
        if user_answer_images is not UNSET:
            field_dict["user_answer_images"] = user_answer_images
        if source is not UNSET:
            field_dict["source"] = source
        if material_id is not UNSET:
            field_dict["material_id"] = material_id
        if material_title is not UNSET:
            field_dict["material_title"] = material_title
        if section_id is not UNSET:
            field_dict["section_id"] = section_id
        if section_title is not UNSET:
            field_dict["section_title"] = section_title
        if is_correct is not UNSET:
            field_dict["is_correct"] = is_correct
        if assessment_type is not UNSET:
            field_dict["assessment_type"] = assessment_type
        if result is not UNSET:
            field_dict["result"] = result
        if mastery_path_id is not UNSET:
            field_dict["mastery_path_id"] = mastery_path_id
        if knowledge_point_id is not UNSET:
            field_dict["knowledge_point_id"] = knowledge_point_id
        if attempt_count is not UNSET:
            field_dict["attempt_count"] = attempt_count
        if hints_used is not UNSET:
            field_dict["hints_used"] = hints_used
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if response_time is not UNSET:
            field_dict["response_time"] = response_time
        if quality is not UNSET:
            field_dict["quality"] = quality

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.answer_image_upload import AnswerImageUpload  # noqa: PLC0415
        from ..models.upsert_entry_request_options_type_0 import UpsertEntryRequestOptionsType0  # noqa: PLC0415

        d = dict(src_dict)
        question_id = d.pop("question_id")

        question = d.pop("question")

        session_id = d.pop("session_id", UNSET)

        _origin_type = d.pop("origin_type", UNSET)
        origin_type: UpsertEntryRequestOriginType | Unset
        if isinstance(_origin_type, Unset):
            origin_type = UNSET
        else:
            origin_type = check_upsert_entry_request_origin_type(_origin_type)

        origin_ref = d.pop("origin_ref", UNSET)

        turn_id = d.pop("turn_id", UNSET)

        question_type = d.pop("question_type", UNSET)

        def _parse_options(data: object) -> None | Unset | UpsertEntryRequestOptionsType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                options_type_0 = UpsertEntryRequestOptionsType0.from_dict(data)

                return options_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpsertEntryRequestOptionsType0, data)

        options = _parse_options(d.pop("options", UNSET))

        correct_answer = d.pop("correct_answer", UNSET)

        explanation = d.pop("explanation", UNSET)

        difficulty = d.pop("difficulty", UNSET)

        user_answer = d.pop("user_answer", UNSET)

        def _parse_user_answer_images(data: object) -> list[AnswerImageUpload] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                user_answer_images_type_0 = []
                _user_answer_images_type_0 = data
                for user_answer_images_type_0_item_data in _user_answer_images_type_0:
                    user_answer_images_type_0_item = AnswerImageUpload.from_dict(user_answer_images_type_0_item_data)

                    user_answer_images_type_0.append(user_answer_images_type_0_item)

                return user_answer_images_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AnswerImageUpload] | None | Unset, data)

        user_answer_images = _parse_user_answer_images(d.pop("user_answer_images", UNSET))

        _source = d.pop("source", UNSET)
        source: UpsertEntryRequestSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_upsert_entry_request_source(_source)

        material_id = d.pop("material_id", UNSET)

        material_title = d.pop("material_title", UNSET)

        section_id = d.pop("section_id", UNSET)

        section_title = d.pop("section_title", UNSET)

        is_correct = d.pop("is_correct", UNSET)

        assessment_type = d.pop("assessment_type", UNSET)

        result = d.pop("result", UNSET)

        mastery_path_id = d.pop("mastery_path_id", UNSET)

        knowledge_point_id = d.pop("knowledge_point_id", UNSET)

        attempt_count = d.pop("attempt_count", UNSET)

        hints_used = d.pop("hints_used", UNSET)

        def _parse_confidence(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        confidence = _parse_confidence(d.pop("confidence", UNSET))

        def _parse_response_time(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        response_time = _parse_response_time(d.pop("response_time", UNSET))

        def _parse_quality(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        quality = _parse_quality(d.pop("quality", UNSET))

        upsert_entry_request = cls(
            question_id=question_id,
            question=question,
            session_id=session_id,
            origin_type=origin_type,
            origin_ref=origin_ref,
            turn_id=turn_id,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty,
            user_answer=user_answer,
            user_answer_images=user_answer_images,
            source=source,
            material_id=material_id,
            material_title=material_title,
            section_id=section_id,
            section_title=section_title,
            is_correct=is_correct,
            assessment_type=assessment_type,
            result=result,
            mastery_path_id=mastery_path_id,
            knowledge_point_id=knowledge_point_id,
            attempt_count=attempt_count,
            hints_used=hints_used,
            confidence=confidence,
            response_time=response_time,
            quality=quality,
        )

        upsert_entry_request.additional_properties = d
        return upsert_entry_request

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
