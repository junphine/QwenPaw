from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.miner_u_settings_update import MinerUSettingsUpdate
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: MinerUSettingsUpdate,
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
        "url": "/api/settings/mineru/test",
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
    body: MinerUSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Test Mineru Connection

     Validate the active backend. ``mode == "local"`` checks the CLI install
    (PATH probe + ``--version``); cloud mode validates the token against the
    live MinerU API (no parse quota consumed). Tests the draft form values so
    the user can verify before saving; falls back to the stored token when the
    secret field is untouched.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (MinerUSettingsUpdate): MinerU document-parsing backend settings.

            ``api_token`` is tri-state: ``None`` keeps the stored token (the UI sends
            None when the user didn't edit the secret field), ``""`` clears it, and a
            non-empty string or string array replaces it. The GET payload never echoes
            the raw token.

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
    body: MinerUSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Test Mineru Connection

     Validate the active backend. ``mode == "local"`` checks the CLI install
    (PATH probe + ``--version``); cloud mode validates the token against the
    live MinerU API (no parse quota consumed). Tests the draft form values so
    the user can verify before saving; falls back to the stored token when the
    secret field is untouched.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (MinerUSettingsUpdate): MinerU document-parsing backend settings.

            ``api_token`` is tri-state: ``None`` keeps the stored token (the UI sends
            None when the user didn't edit the secret field), ``""`` clears it, and a
            non-empty string or string array replaces it. The GET payload never echoes
            the raw token.

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
    body: MinerUSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Test Mineru Connection

     Validate the active backend. ``mode == "local"`` checks the CLI install
    (PATH probe + ``--version``); cloud mode validates the token against the
    live MinerU API (no parse quota consumed). Tests the draft form values so
    the user can verify before saving; falls back to the stored token when the
    secret field is untouched.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (MinerUSettingsUpdate): MinerU document-parsing backend settings.

            ``api_token`` is tri-state: ``None`` keeps the stored token (the UI sends
            None when the user didn't edit the secret field), ``""`` clears it, and a
            non-empty string or string array replaces it. The GET payload never echoes
            the raw token.

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
    body: MinerUSettingsUpdate,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Test Mineru Connection

     Validate the active backend. ``mode == "local"`` checks the CLI install
    (PATH probe + ``--version``); cloud mode validates the token against the
    live MinerU API (no parse quota consumed). Tests the draft form values so
    the user can verify before saving; falls back to the stored token when the
    secret field is untouched.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (MinerUSettingsUpdate): MinerU document-parsing backend settings.

            ``api_token`` is tri-state: ``None`` keeps the stored token (the UI sends
            None when the user didn't edit the secret field), ``""`` clears it, and a
            non-empty string or string array replaces it. The GET payload never echoes
            the raw token.

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
