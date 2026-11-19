from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.apply_book_edit_request import ApplyBookEditRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_apply_book_edit_api_books_book_id_edits_edit_id_apply_post import (
    ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    edit_id: str,
    *,
    body: ApplyBookEditRequest,
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
        "url": "/api/books/{book_id}/edits/{edit_id}/apply".format(
            book_id=quote(str(book_id), safe=""),
            edit_id=quote(str(edit_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost | None:
    if response.status_code == 200:
        response_200 = ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    book_id: str,
    edit_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApplyBookEditRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost]:
    """Apply Book Edit

    Args:
        book_id (str):
        edit_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApplyBookEditRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        edit_id=edit_id,
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
    edit_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApplyBookEditRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost | None:
    """Apply Book Edit

    Args:
        book_id (str):
        edit_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApplyBookEditRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost
    """

    return sync_detailed(
        book_id=book_id,
        edit_id=edit_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    edit_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApplyBookEditRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost]:
    """Apply Book Edit

    Args:
        book_id (str):
        edit_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApplyBookEditRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        edit_id=edit_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    edit_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApplyBookEditRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost | None:
    """Apply Book Edit

    Args:
        book_id (str):
        edit_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApplyBookEditRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseApplyBookEditApiBooksBookIdEditsEditIdApplyPost
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            edit_id=edit_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
