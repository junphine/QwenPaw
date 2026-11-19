from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_reveal_render_file_files_workspace_items_workspace_id_workspace_item_id_reveal_post import (
    ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    workspace_item_id: str,
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
        "url": "/files/workspace-items/{workspace_id}/{workspace_item_id}/reveal".format(
            workspace_id=quote(str(workspace_id), safe=""),
            workspace_item_id=quote(str(workspace_item_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost | None:
    if response.status_code == 200:
        response_200 = ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost.from_dict(
            response.json()
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
) -> Response[HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    workspace_item_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost]:
    """Reveal Render File

     Select an artifact in the local desktop file manager.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    workspace_item_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost | None:
    """Reveal Render File

     Select an artifact in the local desktop file manager.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost
    """

    return sync_detailed(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    workspace_item_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost]:
    """Reveal Render File

     Select an artifact in the local desktop file manager.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    workspace_item_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost | None:
    """Reveal Render File

     Select an artifact in the local desktop file manager.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevealRenderFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRevealPost
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            workspace_item_id=workspace_item_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
