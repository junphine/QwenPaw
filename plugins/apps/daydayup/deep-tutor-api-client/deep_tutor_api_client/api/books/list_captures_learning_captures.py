from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_list_learning_captures_api_books_book_id_learning_captures_get import (
    ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    *,
    status: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    cookies = {}
    if dt_token is not UNSET:
        cookies["dt_token"] = dt_token

    params: dict[str, Any] = {}

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/books/{book_id}/learning-captures".format(
            book_id=quote(str(book_id), safe=""),
        ),
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet | None:
    if response.status_code == 200:
        response_200 = ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet]:
    """List Learning Captures

    Args:
        book_id (str):
        status (None | str | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        status=status,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet | None:
    """List Learning Captures

    Args:
        book_id (str):
        status (None | str | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet
    """

    return sync_detailed(
        book_id=book_id,
        client=client,
        status=status,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet]:
    """List Learning Captures

    Args:
        book_id (str):
        status (None | str | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        status=status,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet | None:
    """List Learning Captures

    Args:
        book_id (str):
        status (None | str | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListLearningCapturesApiBooksBookIdLearningCapturesGet
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            client=client,
            status=status,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
