from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.quiz_answers_payload import QuizAnswersPayload
from ...models.response_submit_quiz_answers_api_reading_materials_material_id_extensions_quiz_answers_post import (
    ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    material_id: str,
    *,
    body: QuizAnswersPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    cookies = {}
    if dt_token is not UNSET:
        cookies["dt_token"] = dt_token

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/reading/materials/{material_id}/extensions/quiz/answers".format(
            material_id=quote(str(material_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost | None:
    if response.status_code == 200:
        response_200 = ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Response[HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: QuizAnswersPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost]:
    """Submit Quiz Answers

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (QuizAnswersPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost]
    """

    kwargs = _get_kwargs(
        material_id=material_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: QuizAnswersPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost | None:
    """Submit Quiz Answers

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (QuizAnswersPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost
    """

    return sync_detailed(
        material_id=material_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: QuizAnswersPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost]:
    """Submit Quiz Answers

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (QuizAnswersPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost]
    """

    kwargs = _get_kwargs(
        material_id=material_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: QuizAnswersPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost | None:
    """Submit Quiz Answers

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (QuizAnswersPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSubmitQuizAnswersApiReadingMaterialsMaterialIdExtensionsQuizAnswersPost
    """

    return (
        await asyncio_detailed(
            material_id=material_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
