from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generated_output_cleanup_payload import GeneratedOutputCleanupPayload
from ...models.http_validation_error import HTTPValidationError
from ...models.response_remove_chat_output_file_files_workspace_items_workspace_id_workspace_item_id_remove_generated_output_post import (
    ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    workspace_item_id: str,
    *,
    body: GeneratedOutputCleanupPayload,
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
        "url": "/files/workspace-items/{workspace_id}/{workspace_item_id}/remove-generated-output".format(
            workspace_id=quote(str(workspace_id), safe=""),
            workspace_item_id=quote(str(workspace_item_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> (
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
    | None
):
    if response.status_code == 200:
        response_200 = ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost.from_dict(
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
) -> Response[
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
]:
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
    body: GeneratedOutputCleanupPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
]:
    """Remove Chat Output File

     Remove an unchanged workspace copy while retaining the chat snapshot.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (GeneratedOutputCleanupPayload): Bind deletion to the file details reviewed by the
            caller.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        body=body,
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
    body: GeneratedOutputCleanupPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
    | None
):
    """Remove Chat Output File

     Remove an unchanged workspace copy while retaining the chat snapshot.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (GeneratedOutputCleanupPayload): Bind deletion to the file details reviewed by the
            caller.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
    """

    return sync_detailed(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    workspace_item_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GeneratedOutputCleanupPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
]:
    """Remove Chat Output File

     Remove an unchanged workspace copy while retaining the chat snapshot.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (GeneratedOutputCleanupPayload): Bind deletion to the file details reviewed by the
            caller.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        workspace_item_id=workspace_item_id,
        body=body,
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
    body: GeneratedOutputCleanupPayload,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
    | None
):
    """Remove Chat Output File

     Remove an unchanged workspace copy while retaining the chat snapshot.

    Args:
        workspace_id (str):
        workspace_item_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (GeneratedOutputCleanupPayload): Bind deletion to the file details reviewed by the
            caller.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRemoveChatOutputFileFilesWorkspaceItemsWorkspaceIdWorkspaceItemIdRemoveGeneratedOutputPost
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            workspace_item_id=workspace_item_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
