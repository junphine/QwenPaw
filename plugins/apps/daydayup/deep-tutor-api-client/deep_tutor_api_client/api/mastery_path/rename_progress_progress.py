from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rename_path_request import RenamePathRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    *,
    body: RenamePathRequest,
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
        "url": "/api/mastery-paths/progress/{book_id}".format(
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
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Any | HTTPValidationError]:
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
    body: RenamePathRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Rename Progress

     Rename a path — the only edit that is the learner's rather than the tutor's.

    Guarded like every other path mutation so a rename cannot interleave with a
    tutoring turn's own commit, and emitted as an event so the activity feed
    records who called it what.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenamePathRequest): An empty name is a valid request: it restores the derived
            display name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    body: RenamePathRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Rename Progress

     Rename a path — the only edit that is the learner's rather than the tutor's.

    Guarded like every other path mutation so a rename cannot interleave with a
    tutoring turn's own commit, and emitted as an event so the activity feed
    records who called it what.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenamePathRequest): An empty name is a valid request: it restores the derived
            display name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
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
    body: RenamePathRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Rename Progress

     Rename a path — the only edit that is the learner's rather than the tutor's.

    Guarded like every other path mutation so a rename cannot interleave with a
    tutoring turn's own commit, and emitted as an event so the activity feed
    records who called it what.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenamePathRequest): An empty name is a valid request: it restores the derived
            display name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    body: RenamePathRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Rename Progress

     Rename a path — the only edit that is the learner's rather than the tutor's.

    Guarded like every other path mutation so a rename cannot interleave with a
    tutoring turn's own commit, and emitted as an event so the activity feed
    records who called it what.

    Args:
        book_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenamePathRequest): An empty name is a valid request: it restores the derived
            display name.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
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
