from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.enabled_payload import EnabledPayload
from ...models.http_validation_error import HTTPValidationError
from ...models.response_set_enabled_api_space_cli_apps_apps_app_id_enabled_put import (
    ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    app_id: str,
    *,
    body: EnabledPayload,
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
        "url": "/api/space/cli-apps/apps/{app_id}/enabled".format(
            app_id=quote(str(app_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut | None:
    if response.status_code == 200:
        response_200 = ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    app_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EnabledPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut]:
    """Set Enabled

     Switch one app on or off for the calling account.

    Refused for an app the caller has not been granted: the preference file must
    not become a way to record interest in something the grant denies, because a
    later grant would then silently switch it on.

    Args:
        app_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (EnabledPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    app_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EnabledPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut | None:
    """Set Enabled

     Switch one app on or off for the calling account.

    Refused for an app the caller has not been granted: the preference file must
    not become a way to record interest in something the grant denies, because a
    later grant would then silently switch it on.

    Args:
        app_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (EnabledPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut
    """

    return sync_detailed(
        app_id=app_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    app_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EnabledPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut]:
    """Set Enabled

     Switch one app on or off for the calling account.

    Refused for an app the caller has not been granted: the preference file must
    not become a way to record interest in something the grant denies, because a
    later grant would then silently switch it on.

    Args:
        app_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (EnabledPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut]
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    app_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: EnabledPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut | None:
    """Set Enabled

     Switch one app on or off for the calling account.

    Refused for an app the caller has not been granted: the preference file must
    not become a way to record interest in something the grant denies, because a
    later grant would then silently switch it on.

    Args:
        app_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (EnabledPayload):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSetEnabledApiSpaceCliAppsAppsAppIdEnabledPut
    """

    return (
        await asyncio_detailed(
            app_id=app_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
