from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_list_server_folders_api_settings_workspace_folders_get import (
    ResponseListServerFoldersApiSettingsWorkspaceFoldersGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    path: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(authorization, Unset):
        headers["Authorization"] = authorization

    cookies = {}
    if dt_token is not UNSET:
        cookies["dt_token"] = dt_token

    params: dict[str, Any] = {}

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/settings/workspace/folders",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet | None:
    if response.status_code == 200:
        response_200 = ResponseListServerFoldersApiSettingsWorkspaceFoldersGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet]:
    """List Server Folders

     Return folders available to the authenticated workspace picker.

    Args:
        path (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet]
    """

    kwargs = _get_kwargs(
        path=path,
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
    path: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet | None:
    """List Server Folders

     Return folders available to the authenticated workspace picker.

    Args:
        path (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet
    """

    return sync_detailed(
        client=client,
        path=path,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet]:
    """List Server Folders

     Return folders available to the authenticated workspace picker.

    Args:
        path (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet]
    """

    kwargs = _get_kwargs(
        path=path,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet | None:
    """List Server Folders

     Return folders available to the authenticated workspace picker.

    Args:
        path (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListServerFoldersApiSettingsWorkspaceFoldersGet
    """

    return (
        await asyncio_detailed(
            client=client,
            path=path,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
