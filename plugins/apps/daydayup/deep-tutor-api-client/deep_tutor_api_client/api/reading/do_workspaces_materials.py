from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_remove_workspace_material_api_reading_workspaces_workspace_id_materials_material_id_delete import (
    ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    material_id: str,
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
        "method": "delete",
        "url": "/api/reading/workspaces/{workspace_id}/materials/{material_id}".format(
            workspace_id=quote(str(workspace_id), safe=""),
            material_id=quote(str(material_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> (
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete | None
):
    if response.status_code == 200:
        response_200 = (
            ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete.from_dict(
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
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete
]:
    """Remove Workspace Material

    Args:
        workspace_id (str):
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        material_id=material_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete | None
):
    """Remove Workspace Material

    Args:
        workspace_id (str):
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete
    """

    return sync_detailed(
        workspace_id=workspace_id,
        material_id=material_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete
]:
    """Remove Workspace Material

    Args:
        workspace_id (str):
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        material_id=material_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    material_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete | None
):
    """Remove Workspace Material

    Args:
        workspace_id (str):
        material_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRemoveWorkspaceMaterialApiReadingWorkspacesWorkspaceIdMaterialsMaterialIdDelete
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            material_id=material_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
