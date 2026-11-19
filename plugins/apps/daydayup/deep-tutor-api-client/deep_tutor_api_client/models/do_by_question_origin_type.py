from typing import Literal

DoByQuestionOriginType = Literal["conversation", "document_analysis", "external_import"]

DO_BY_QUESTION_ORIGIN_TYPE_VALUES: set[DoByQuestionOriginType] = {
    "conversation",
    "document_analysis",
    "external_import",
}


def check_do_by_question_origin_type(value: str) -> DoByQuestionOriginType:
    if value in DO_BY_QUESTION_ORIGIN_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DO_BY_QUESTION_ORIGIN_TYPE_VALUES!r}")
