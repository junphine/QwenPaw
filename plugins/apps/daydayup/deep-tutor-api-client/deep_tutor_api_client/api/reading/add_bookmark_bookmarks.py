from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bookmark_info import BookmarkInfo
from ...models.bookmark_payload import BookmarkPayload
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    material_id: str,
    *,
    body: BookmarkPayload,
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
        "url": "/api/reading/materials/{material_id}/bookmarks".format(
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
) -> BookmarkInfo | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = BookmarkInfo.from_dict(response.json())

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
) -> Response[BookmarkInfo | HTTPValidationError]:
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
    body: BookmarkPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[BookmarkInfo | HTTPValidationError]:
    """Add Bookmark

     Keep one place. Bookmarking an already-kept locator returns that one.

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BookmarkPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BookmarkInfo | HTTPValidationError]
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
    body: BookmarkPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> BookmarkInfo | HTTPValidationError | None:
    """Add Bookmark

     Keep one place. Bookmarking an already-kept locator returns that one.

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BookmarkPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BookmarkInfo | HTTPValidationError
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
    body: BookmarkPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[BookmarkInfo | HTTPValidationError]:
    """Add Bookmark

     Keep one place. Bookmarking an already-kept locator returns that one.

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BookmarkPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BookmarkInfo | HTTPValidationError]
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
    body: BookmarkPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> BookmarkInfo | HTTPValidationError | None:
    """Add Bookmark

     Keep one place. Bookmarking an already-kept locator returns that one.

    Args:
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BookmarkPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BookmarkInfo | HTTPValidationError
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
