from typing import Literal

BodyImportPreviewApiQuestionNotebookPracticeImportPreviewPostTarget = Literal["bank", "mistakes"]

BODY_IMPORT_PREVIEW_API_QUESTION_NOTEBOOK_PRACTICE_IMPORT_PREVIEW_POST_TARGET_VALUES: set[
    BodyImportPreviewApiQuestionNotebookPracticeImportPreviewPostTarget
] = {
    "bank",
    "mistakes",
}


def check_body_import_preview_api_question_notebook_practice_import_preview_post_target(
    value: str,
) -> BodyImportPreviewApiQuestionNotebookPracticeImportPreviewPostTarget:
    if value in BODY_IMPORT_PREVIEW_API_QUESTION_NOTEBOOK_PRACTICE_IMPORT_PREVIEW_POST_TARGET_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {BODY_IMPORT_PREVIEW_API_QUESTION_NOTEBOOK_PRACTICE_IMPORT_PREVIEW_POST_TARGET_VALUES!r}"
    )
