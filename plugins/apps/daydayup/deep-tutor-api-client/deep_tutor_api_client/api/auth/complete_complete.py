from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_complete_session_handoff_api_auth_session_handoff_complete_post import (
    ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost,
)
from ...models.session_handoff_complete_request import SessionHandoffCompleteRequest
from ...types import Response


def _get_kwargs(
    *,
    body: SessionHandoffCompleteRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/auth/session-handoff/complete",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost | None:
    if response.status_code == 200:
        response_200 = ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCompleteRequest,
) -> Response[HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost]:
    """Complete Session Handoff

     Consume a ticket once and issue the normal HttpOnly session cookie.

    Args:
        body (SessionHandoffCompleteRequest): Public request that trades a JWE ticket for the
            normal cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCompleteRequest,
) -> HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost | None:
    """Complete Session Handoff

     Consume a ticket once and issue the normal HttpOnly session cookie.

    Args:
        body (SessionHandoffCompleteRequest): Public request that trades a JWE ticket for the
            normal cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCompleteRequest,
) -> Response[HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost]:
    """Complete Session Handoff

     Consume a ticket once and issue the normal HttpOnly session cookie.

    Args:
        body (SessionHandoffCompleteRequest): Public request that trades a JWE ticket for the
            normal cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SessionHandoffCompleteRequest,
) -> HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost | None:
    """Complete Session Handoff

     Consume a ticket once and issue the normal HttpOnly session cookie.

    Args:
        body (SessionHandoffCompleteRequest): Public request that trades a JWE ticket for the
            normal cookie.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseCompleteSessionHandoffApiAuthSessionHandoffCompletePost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
