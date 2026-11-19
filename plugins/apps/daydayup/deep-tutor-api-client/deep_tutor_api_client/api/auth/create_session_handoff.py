from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_create_session_handoff_api_auth_session_handoff_post import (
    ResponseCreateSessionHandoffApiAuthSessionHandoffPost,
)
from ...models.session_handoff_create_request import SessionHandoffCreateRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SessionHandoffCreateRequest,
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
        "url": "/api/auth/session-handoff",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost | None:
    if response.status_code == 200:
        response_200 = ResponseCreateSessionHandoffApiAuthSessionHandoffPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost]:
    """Create Session Handoff

     Create a host-bound, one-time pairing code from the private origin.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (SessionHandoffCreateRequest): Private request that starts a one-time public handoff.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost | None:
    """Create Session Handoff

     Create a host-bound, one-time pairing code from the private origin.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (SessionHandoffCreateRequest): Private request that starts a one-time public handoff.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost]:
    """Create Session Handoff

     Create a host-bound, one-time pairing code from the private origin.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (SessionHandoffCreateRequest): Private request that starts a one-time public handoff.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost | None:
    """Create Session Handoff

     Create a host-bound, one-time pairing code from the private origin.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (SessionHandoffCreateRequest): Private request that starts a one-time public handoff.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseCreateSessionHandoffApiAuthSessionHandoffPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
