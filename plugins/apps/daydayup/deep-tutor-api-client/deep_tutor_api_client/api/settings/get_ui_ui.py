from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/settings/ui",
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Get Ui Settings

     Return the pre-session UI preferences: theme and the two languages.

    Public by design, which is why it is a narrow projection rather than the
    saved ``ui`` blob. The app shell — and the statically prerendered auth
    pages, which have no session at all — adopt the persisted languages here
    during bootstrap. Theme rides along so those pages can paint in the right
    one instead of flashing.

    Everything else under ``ui`` (sidebar_nav_order, enabled_optional_tools,
    chat_response_timeout, …) describes what the deployment has turned on, so
    it stays behind auth: read it from the ``ui`` key of GET /settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any]:
    """Get Ui Settings

     Return the pre-session UI preferences: theme and the two languages.

    Public by design, which is why it is a narrow projection rather than the
    saved ``ui`` blob. The app shell — and the statically prerendered auth
    pages, which have no session at all — adopt the persisted languages here
    during bootstrap. Theme rides along so those pages can paint in the right
    one instead of flashing.

    Everything else under ``ui`` (sidebar_nav_order, enabled_optional_tools,
    chat_response_timeout, …) describes what the deployment has turned on, so
    it stays behind auth: read it from the ``ui`` key of GET /settings.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
