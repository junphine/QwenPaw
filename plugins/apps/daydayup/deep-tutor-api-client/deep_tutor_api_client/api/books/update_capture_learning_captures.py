from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.learning_capture_update_request import LearningCaptureUpdateRequest
from ...models.response_update_learning_capture_api_books_book_id_learning_captures_capture_id_patch import (
    ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    capture_id: str,
    *,
    body: LearningCaptureUpdateRequest,
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
        "method": "patch",
        "url": "/api/books/{book_id}/learning-captures/{capture_id}".format(
            book_id=quote(str(book_id), safe=""),
            capture_id=quote(str(capture_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch | None:
    if response.status_code == 200:
        response_200 = ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch.from_dict(
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
) -> Response[HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    book_id: str,
    capture_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearningCaptureUpdateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch]:
    """Update Learning Capture

    Args:
        book_id (str):
        capture_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearningCaptureUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        capture_id=capture_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    book_id: str,
    capture_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearningCaptureUpdateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch | None:
    """Update Learning Capture

    Args:
        book_id (str):
        capture_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearningCaptureUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch
    """

    return sync_detailed(
        book_id=book_id,
        capture_id=capture_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    capture_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearningCaptureUpdateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch]:
    """Update Learning Capture

    Args:
        book_id (str):
        capture_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearningCaptureUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        capture_id=capture_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    capture_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearningCaptureUpdateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch | None:
    """Update Learning Capture

    Args:
        book_id (str):
        capture_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearningCaptureUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUpdateLearningCaptureApiBooksBookIdLearningCapturesCaptureIdPatch
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            capture_id=capture_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
