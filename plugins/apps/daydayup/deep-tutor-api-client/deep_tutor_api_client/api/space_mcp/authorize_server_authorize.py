from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_authorize_server_api_space_mcp_servers_name_authorize_post import (
    ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
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
        "url": "/api/space/mcp/servers/{name}/authorize".format(
            name=quote(str(name), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost | None:
    if response.status_code == 200:
        response_200 = ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost]:
    """Authorize Server

     Begin an OAuth consent for one of the caller's servers.

    Returns the URL to send the person to. This is the **only** place a flow may
    start: a background reconnect has nobody in front of it, so it reports
    ``needs_auth`` and waits for someone to click.

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost]
    """

    kwargs = _get_kwargs(
        name=name,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost | None:
    """Authorize Server

     Begin an OAuth consent for one of the caller's servers.

    Returns the URL to send the person to. This is the **only** place a flow may
    start: a background reconnect has nobody in front of it, so it reports
    ``needs_auth`` and waits for someone to click.

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost
    """

    return sync_detailed(
        name=name,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost]:
    """Authorize Server

     Begin an OAuth consent for one of the caller's servers.

    Returns the URL to send the person to. This is the **only** place a flow may
    start: a background reconnect has nobody in front of it, so it reports
    ``needs_auth`` and waits for someone to click.

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost]
    """

    kwargs = _get_kwargs(
        name=name,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost | None:
    """Authorize Server

     Begin an OAuth consent for one of the caller's servers.

    Returns the URL to send the person to. This is the **only** place a flow may
    start: a background reconnect has nobody in front of it, so it reports
    ``needs_auth`` and waits for someone to click.

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAuthorizeServerApiSpaceMcpServersNameAuthorizePost
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
