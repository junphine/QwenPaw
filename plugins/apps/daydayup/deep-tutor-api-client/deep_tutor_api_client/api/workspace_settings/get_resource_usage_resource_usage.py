from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_workspace_resource_usage_api_settings_workspace_resource_usage_get import (
    ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    kind: str,
    resource_id: str,
    skill_workspace: str | Unset = "",
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

    params["kind"] = kind

    params["resource_id"] = resource_id

    params["skill_workspace"] = skill_workspace

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/settings/workspace/resource-usage",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet | None:
    if response.status_code == 200:
        response_200 = ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    kind: str,
    resource_id: str,
    skill_workspace: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet]:
    """Workspace Resource Usage

    Args:
        kind (str):
        resource_id (str):
        skill_workspace (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet]
    """

    kwargs = _get_kwargs(
        kind=kind,
        resource_id=resource_id,
        skill_workspace=skill_workspace,
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
    kind: str,
    resource_id: str,
    skill_workspace: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet | None:
    """Workspace Resource Usage

    Args:
        kind (str):
        resource_id (str):
        skill_workspace (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet
    """

    return sync_detailed(
        client=client,
        kind=kind,
        resource_id=resource_id,
        skill_workspace=skill_workspace,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    kind: str,
    resource_id: str,
    skill_workspace: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet]:
    """Workspace Resource Usage

    Args:
        kind (str):
        resource_id (str):
        skill_workspace (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet]
    """

    kwargs = _get_kwargs(
        kind=kind,
        resource_id=resource_id,
        skill_workspace=skill_workspace,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    kind: str,
    resource_id: str,
    skill_workspace: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet | None:
    """Workspace Resource Usage

    Args:
        kind (str):
        resource_id (str):
        skill_workspace (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseWorkspaceResourceUsageApiSettingsWorkspaceResourceUsageGet
    """

    return (
        await asyncio_detailed(
            client=client,
            kind=kind,
            resource_id=resource_id,
            skill_workspace=skill_workspace,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
