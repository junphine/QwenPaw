from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_delete_chapter_api_books_book_id_chapters_chapter_id_delete import (
    ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    chapter_id: str,
    *,
    expected_revision: int | None | Unset = UNSET,
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

    json_expected_revision: int | None | Unset
    if isinstance(expected_revision, Unset):
        json_expected_revision = UNSET
    else:
        json_expected_revision = expected_revision
    params["expected_revision"] = json_expected_revision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/books/{book_id}/chapters/{chapter_id}".format(
            book_id=quote(str(book_id), safe=""),
            chapter_id=quote(str(chapter_id), safe=""),
        ),
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete | None:
    if response.status_code == 200:
        response_200 = ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    book_id: str,
    chapter_id: str,
    *,
    client: AuthenticatedClient | Client,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete]:
    """Delete Chapter

     Delete a chapter and only its pages; other compiled pages are untouched.

    Args:
        book_id (str):
        chapter_id (str):
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        chapter_id=chapter_id,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    book_id: str,
    chapter_id: str,
    *,
    client: AuthenticatedClient | Client,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete | None:
    """Delete Chapter

     Delete a chapter and only its pages; other compiled pages are untouched.

    Args:
        book_id (str):
        chapter_id (str):
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete
    """

    return sync_detailed(
        book_id=book_id,
        chapter_id=chapter_id,
        client=client,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    chapter_id: str,
    *,
    client: AuthenticatedClient | Client,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete]:
    """Delete Chapter

     Delete a chapter and only its pages; other compiled pages are untouched.

    Args:
        book_id (str):
        chapter_id (str):
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        chapter_id=chapter_id,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    chapter_id: str,
    *,
    client: AuthenticatedClient | Client,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete | None:
    """Delete Chapter

     Delete a chapter and only its pages; other compiled pages are untouched.

    Args:
        book_id (str):
        chapter_id (str):
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseDeleteChapterApiBooksBookIdChaptersChapterIdDelete
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            chapter_id=chapter_id,
            client=client,
            expected_revision=expected_revision,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
