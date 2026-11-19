from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_starter_settings_update import ChatStarterSettingsUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ChatStarterSettingsUpdate,
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
        "method": "put",
        "url": "/api/settings/chat-starters",
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
    *,
    client: AuthenticatedClient | Client,
    body: ChatStarterSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Chat Starter Settings

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatStarterSettingsUpdate): How much recent activity shapes the home screen's
            starting points, and
            whether the chat composer offers a predicted next line.

            Bounds mirror ``starter_settings.TRACE_COUNT_RANGE`` so the API rejects
            loudly what the file layer would silently clamp. ``ask_hint_enabled`` left
            out (``None``) keeps the stored value, so a client that only knows
            ``trace_count`` cannot switch the hint back on by accident.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    body: ChatStarterSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Chat Starter Settings

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatStarterSettingsUpdate): How much recent activity shapes the home screen's
            starting points, and
            whether the chat composer offers a predicted next line.

            Bounds mirror ``starter_settings.TRACE_COUNT_RANGE`` so the API rejects
            loudly what the file layer would silently clamp. ``ask_hint_enabled`` left
            out (``None``) keeps the stored value, so a client that only knows
            ``trace_count`` cannot switch the hint back on by accident.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
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
    body: ChatStarterSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Chat Starter Settings

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatStarterSettingsUpdate): How much recent activity shapes the home screen's
            starting points, and
            whether the chat composer offers a predicted next line.

            Bounds mirror ``starter_settings.TRACE_COUNT_RANGE`` so the API rejects
            loudly what the file layer would silently clamp. ``ask_hint_enabled`` left
            out (``None``) keeps the stored value, so a client that only knows
            ``trace_count`` cannot switch the hint back on by accident.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
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
    body: ChatStarterSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Chat Starter Settings

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatStarterSettingsUpdate): How much recent activity shapes the home screen's
            starting points, and
            whether the chat composer offers a predicted next line.

            Bounds mirror ``starter_settings.TRACE_COUNT_RANGE`` so the API rejects
            loudly what the file layer would silently clamp. ``ask_hint_enabled`` left
            out (``None``) keeps the stored value, so a client that only knows
            ``trace_count`` cannot switch the hint back on by accident.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
