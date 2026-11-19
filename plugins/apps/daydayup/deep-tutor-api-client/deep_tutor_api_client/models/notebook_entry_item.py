from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notebook_entry_item_origin_type import NotebookEntryItemOriginType, check_notebook_entry_item_origin_type
from ..models.notebook_entry_item_result_type_0 import (
    NotebookEntryItemResultType0,
    check_notebook_entry_item_result_type_0,
)
from ..models.notebook_entry_item_score_trend import NotebookEntryItemScoreTrend, check_notebook_entry_item_score_trend
from ..models.notebook_entry_item_source import NotebookEntryItemSource, check_notebook_entry_item_source
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.answer_image_item import AnswerImageItem
    from ..models.category_item import CategoryItem
    from ..models.notebook_entry_item_practice_type_0 import NotebookEntryItemPracticeType0
    from ..models.options import Options


T = TypeVar("T", bound="NotebookEntryItem")


@_attrs_define
class NotebookEntryItem:
    """
    Attributes:
        id (int):
        question (str):
        created_at (float):
        updated_at (float):
        session_id (str | Unset):  Default: ''.
        session_title (str | Unset):  Default: ''.
        origin_type (NotebookEntryItemOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        turn_id (str | Unset):  Default: ''.
        question_id (str | Unset):  Default: ''.
        question_type (str | Unset):  Default: ''.
        options (Options | Unset):
        correct_answer (str | Unset):  Default: ''.
        explanation (str | Unset):  Default: ''.
        difficulty (str | Unset):  Default: ''.
        user_answer (str | Unset):  Default: ''.
        user_answer_images (list[AnswerImageItem] | Unset):
        source (NotebookEntryItemSource | Unset):  Default: 'deep_question'.
        material_id (str | Unset):  Default: ''.
        material_title (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        section_title (str | Unset):  Default: ''.
        score_trend (NotebookEntryItemScoreTrend | Unset):  Default: 'new'.
        assessment_type (str | Unset):  Default: ''.
        result (NotebookEntryItemResultType0 | str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        attempt_count (int | Unset):  Default: 1.
        hints_used (int | Unset):  Default: 0.
        confidence (float | None | Unset):
        response_time (float | None | Unset):
        quality (float | None | Unset):
        is_correct (bool | Unset):  Default: False.
        resolved (bool | Unset):  Default: False.
        bookmarked (bool | Unset):  Default: False.
        followup_session_id (str | Unset):  Default: ''.
        ai_judgment (str | Unset):  Default: ''.
        categories (list[CategoryItem] | None | Unset):
        practice (None | NotebookEntryItemPracticeType0 | Unset):
    """

    id: int
    question: str
    created_at: float
    updated_at: float
    session_id: str | Unset = ""
    session_title: str | Unset = ""
    origin_type: NotebookEntryItemOriginType | Unset = "conversation"
    origin_ref: str | Unset = ""
    turn_id: str | Unset = ""
    question_id: str | Unset = ""
    question_type: str | Unset = ""
    options: Options | Unset = UNSET
    correct_answer: str | Unset = ""
    explanation: str | Unset = ""
    difficulty: str | Unset = ""
    user_answer: str | Unset = ""
    user_answer_images: list[AnswerImageItem] | Unset = UNSET
    source: NotebookEntryItemSource | Unset = "deep_question"
    material_id: str | Unset = ""
    material_title: str | Unset = ""
    section_id: str | Unset = ""
    section_title: str | Unset = ""
    score_trend: NotebookEntryItemScoreTrend | Unset = "new"
    assessment_type: str | Unset = ""
    result: NotebookEntryItemResultType0 | str | Unset = ""
    mastery_path_id: str | Unset = ""
    knowledge_point_id: str | Unset = ""
    attempt_count: int | Unset = 1
    hints_used: int | Unset = 0
    confidence: float | None | Unset = UNSET
    response_time: float | None | Unset = UNSET
    quality: float | None | Unset = UNSET
    is_correct: bool | Unset = False
    resolved: bool | Unset = False
    bookmarked: bool | Unset = False
    followup_session_id: str | Unset = ""
    ai_judgment: str | Unset = ""
    categories: list[CategoryItem] | None | Unset = UNSET
    practice: None | NotebookEntryItemPracticeType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.notebook_entry_item_practice_type_0 import NotebookEntryItemPracticeType0  # noqa: PLC0415

        id = self.id

        question = self.question

        created_at = self.created_at

        updated_at = self.updated_at

        session_id = self.session_id

        session_title = self.session_title

        origin_type: str | Unset = UNSET
        if not isinstance(self.origin_type, Unset):
            origin_type = self.origin_type

        origin_ref = self.origin_ref

        turn_id = self.turn_id

        question_id = self.question_id

        question_type = self.question_type

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        correct_answer = self.correct_answer

        explanation = self.explanation

        difficulty = self.difficulty

        user_answer = self.user_answer

        user_answer_images: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.user_answer_images, Unset):
            user_answer_images = []
            for user_answer_images_item_data in self.user_answer_images:
                user_answer_images_item = user_answer_images_item_data.to_dict()
                user_answer_images.append(user_answer_images_item)

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        material_id = self.material_id

        material_title = self.material_title

        section_id = self.section_id

        section_title = self.section_title

        score_trend: str | Unset = UNSET
        if not isinstance(self.score_trend, Unset):
            score_trend = self.score_trend

        assessment_type = self.assessment_type

        result: str | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, str):
            result = self.result
        else:
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

        is_correct = self.is_correct

        resolved = self.resolved

        bookmarked = self.bookmarked

        followup_session_id = self.followup_session_id

        ai_judgment = self.ai_judgment

        categories: list[dict[str, Any]] | None | Unset
        if isinstance(self.categories, Unset):
            categories = UNSET
        elif isinstance(self.categories, list):
            categories = []
            for categories_type_0_item_data in self.categories:
                categories_type_0_item = categories_type_0_item_data.to_dict()
                categories.append(categories_type_0_item)

        else:
            categories = self.categories

        practice: dict[str, Any] | None | Unset
        if isinstance(self.practice, Unset):
            practice = UNSET
        elif isinstance(self.practice, NotebookEntryItemPracticeType0):
            practice = self.practice.to_dict()
        else:
            practice = self.practice

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "question": question,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if session_title is not UNSET:
            field_dict["session_title"] = session_title
        if origin_type is not UNSET:
            field_dict["origin_type"] = origin_type
        if origin_ref is not UNSET:
            field_dict["origin_ref"] = origin_ref
        if turn_id is not UNSET:
            field_dict["turn_id"] = turn_id
        if question_id is not UNSET:
            field_dict["question_id"] = question_id
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
        if score_trend is not UNSET:
            field_dict["score_trend"] = score_trend
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
        if is_correct is not UNSET:
            field_dict["is_correct"] = is_correct
        if resolved is not UNSET:
            field_dict["resolved"] = resolved
        if bookmarked is not UNSET:
            field_dict["bookmarked"] = bookmarked
        if followup_session_id is not UNSET:
            field_dict["followup_session_id"] = followup_session_id
        if ai_judgment is not UNSET:
            field_dict["ai_judgment"] = ai_judgment
        if categories is not UNSET:
            field_dict["categories"] = categories
        if practice is not UNSET:
            field_dict["practice"] = practice

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.answer_image_item import AnswerImageItem  # noqa: PLC0415
        from ..models.category_item import CategoryItem  # noqa: PLC0415
        from ..models.notebook_entry_item_practice_type_0 import NotebookEntryItemPracticeType0  # noqa: PLC0415
        from ..models.options import Options  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        question = d.pop("question")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        session_id = d.pop("session_id", UNSET)

        session_title = d.pop("session_title", UNSET)

        _origin_type = d.pop("origin_type", UNSET)
        origin_type: NotebookEntryItemOriginType | Unset
        if isinstance(_origin_type, Unset):
            origin_type = UNSET
        else:
            origin_type = check_notebook_entry_item_origin_type(_origin_type)

        origin_ref = d.pop("origin_ref", UNSET)

        turn_id = d.pop("turn_id", UNSET)

        question_id = d.pop("question_id", UNSET)

        question_type = d.pop("question_type", UNSET)

        _options = d.pop("options", UNSET)
        options: Options | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = Options.from_dict(_options)

        correct_answer = d.pop("correct_answer", UNSET)

        explanation = d.pop("explanation", UNSET)

        difficulty = d.pop("difficulty", UNSET)

        user_answer = d.pop("user_answer", UNSET)

        _user_answer_images = d.pop("user_answer_images", UNSET)
        user_answer_images: list[AnswerImageItem] | Unset = UNSET
        if _user_answer_images is not UNSET:
            user_answer_images = []
            for user_answer_images_item_data in _user_answer_images:
                user_answer_images_item = AnswerImageItem.from_dict(user_answer_images_item_data)

                user_answer_images.append(user_answer_images_item)

        _source = d.pop("source", UNSET)
        source: NotebookEntryItemSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_notebook_entry_item_source(_source)

        material_id = d.pop("material_id", UNSET)

        material_title = d.pop("material_title", UNSET)

        section_id = d.pop("section_id", UNSET)

        section_title = d.pop("section_title", UNSET)

        _score_trend = d.pop("score_trend", UNSET)
        score_trend: NotebookEntryItemScoreTrend | Unset
        if isinstance(_score_trend, Unset):
            score_trend = UNSET
        else:
            score_trend = check_notebook_entry_item_score_trend(_score_trend)

        assessment_type = d.pop("assessment_type", UNSET)

        def _parse_result(data: object) -> NotebookEntryItemResultType0 | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                result_type_0 = check_notebook_entry_item_result_type_0(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(NotebookEntryItemResultType0 | str | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

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

        is_correct = d.pop("is_correct", UNSET)

        resolved = d.pop("resolved", UNSET)

        bookmarked = d.pop("bookmarked", UNSET)

        followup_session_id = d.pop("followup_session_id", UNSET)

        ai_judgment = d.pop("ai_judgment", UNSET)

        def _parse_categories(data: object) -> list[CategoryItem] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                categories_type_0 = []
                _categories_type_0 = data
                for categories_type_0_item_data in _categories_type_0:
                    categories_type_0_item = CategoryItem.from_dict(categories_type_0_item_data)

                    categories_type_0.append(categories_type_0_item)

                return categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[CategoryItem] | None | Unset, data)

        categories = _parse_categories(d.pop("categories", UNSET))

        def _parse_practice(data: object) -> None | NotebookEntryItemPracticeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                practice_type_0 = NotebookEntryItemPracticeType0.from_dict(data)

                return practice_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | NotebookEntryItemPracticeType0 | Unset, data)

        practice = _parse_practice(d.pop("practice", UNSET))

        notebook_entry_item = cls(
            id=id,
            question=question,
            created_at=created_at,
            updated_at=updated_at,
            session_id=session_id,
            session_title=session_title,
            origin_type=origin_type,
            origin_ref=origin_ref,
            turn_id=turn_id,
            question_id=question_id,
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
            score_trend=score_trend,
            assessment_type=assessment_type,
            result=result,
            mastery_path_id=mastery_path_id,
            knowledge_point_id=knowledge_point_id,
            attempt_count=attempt_count,
            hints_used=hints_used,
            confidence=confidence,
            response_time=response_time,
            quality=quality,
            is_correct=is_correct,
            resolved=resolved,
            bookmarked=bookmarked,
            followup_session_id=followup_session_id,
            ai_judgment=ai_judgment,
            categories=categories,
            practice=practice,
        )

        notebook_entry_item.additional_properties = d
        return notebook_entry_item

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
