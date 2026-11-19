from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.add_chapter_request import AddChapterRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_add_chapter_api_books_book_id_chapters_post import ResponseAddChapterApiBooksBookIdChaptersPost
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    *,
    body: AddChapterRequest,
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
        "url": "/api/books/{book_id}/chapters".format(
            book_id=quote(str(book_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost | None:
    if response.status_code == 200:
        response_200 = ResponseAddChapterApiBooksBookIdChaptersPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost]:
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
    body: AddChapterRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost]:
    """Add Chapter

     Append an empty chapter shell after generation, without recompiling.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AddChapterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
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
    *,
    client: AuthenticatedClient | Client,
    body: AddChapterRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost | None:
    """Add Chapter

     Append an empty chapter shell after generation, without recompiling.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AddChapterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost
    """

    return sync_detailed(
        book_id=book_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddChapterRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost]:
    """Add Chapter

     Append an empty chapter shell after generation, without recompiling.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AddChapterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: AddChapterRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost | None:
    """Add Chapter

     Append an empty chapter shell after generation, without recompiling.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AddChapterRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAddChapterApiBooksBookIdChaptersPost
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
