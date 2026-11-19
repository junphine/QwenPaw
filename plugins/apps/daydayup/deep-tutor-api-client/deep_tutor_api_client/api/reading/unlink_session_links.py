from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_unlink_reading_session_api_reading_workspaces_workspace_id_sessions_session_id_links_target_session_id_delete import (
    ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    session_id: str,
    target_session_id: str,
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
        "url": "/api/reading/workspaces/{workspace_id}/sessions/{session_id}/links/{target_session_id}".format(
            workspace_id=quote(str(workspace_id), safe=""),
            session_id=quote(str(session_id), safe=""),
            target_session_id=quote(str(target_session_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> (
    HTTPValidationError
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
    | None
):
    if response.status_code == 200:
        response_200 = ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete.from_dict(
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
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    session_id: str,
    target_session_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
]:
    """Unlink Reading Session

    Args:
        workspace_id (str):
        session_id (str):
        target_session_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        target_session_id=target_session_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    session_id: str,
    target_session_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
    | None
):
    """Unlink Reading Session

    Args:
        workspace_id (str):
        session_id (str):
        target_session_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
    """

    return sync_detailed(
        workspace_id=workspace_id,
        session_id=session_id,
        target_session_id=target_session_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    session_id: str,
    target_session_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[
    HTTPValidationError
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
]:
    """Unlink Reading Session

    Args:
        workspace_id (str):
        session_id (str):
        target_session_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        target_session_id=target_session_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    session_id: str,
    target_session_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> (
    HTTPValidationError
    | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
    | None
):
    """Unlink Reading Session

    Args:
        workspace_id (str):
        session_id (str):
        target_session_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUnlinkReadingSessionApiReadingWorkspacesWorkspaceIdSessionsSessionIdLinksTargetSessionIdDelete
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            session_id=session_id,
            target_session_id=target_session_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
