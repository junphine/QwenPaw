from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_recover_workspace_migration_api_settings_workspace_data_operations_operation_id_recover_post import (
    ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    operation_id: str,
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
        "url": "/api/settings/workspace/data/operations/{operation_id}/recover".format(
            operation_id=quote(str(operation_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> (
    HTTPValidationError
    | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
    | None
):
    if response.status_code == 200:
        response_200 = (
            ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost.from_dict(
                response.json()
            )
        )

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
) -> Response[
    HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
]:
    """Recover Workspace Migration

    Args:
        operation_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
    | None
):
    """Recover Workspace Migration

    Args:
        operation_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
    """

    return sync_detailed(
        operation_id=operation_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
]:
    """Recover Workspace Migration

    Args:
        operation_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost]
    """

    kwargs = _get_kwargs(
        operation_id=operation_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    operation_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
    | None
):
    """Recover Workspace Migration

    Args:
        operation_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRecoverWorkspaceMigrationApiSettingsWorkspaceDataOperationsOperationIdRecoverPost
    """

    return (
        await asyncio_detailed(
            operation_id=operation_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
