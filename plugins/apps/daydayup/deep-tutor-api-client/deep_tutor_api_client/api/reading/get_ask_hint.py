from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_get_workspace_ask_hint_api_reading_workspaces_workspace_id_ask_hint_get import (
    ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    workspace_id: str,
    *,
    session_id: str | Unset = "",
    locator: int | None | Unset = UNSET,
    selection: str | Unset = "",
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

    params["session_id"] = session_id

    json_locator: int | None | Unset
    if isinstance(locator, Unset):
        json_locator = UNSET
    else:
        json_locator = locator
    params["locator"] = json_locator

    params["selection"] = selection

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/reading/workspaces/{workspace_id}/ask-hint".format(
            workspace_id=quote(str(workspace_id), safe=""),
        ),
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet | None:
    if response.status_code == 200:
        response_200 = ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    locator: int | None | Unset = UNSET,
    selection: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet]:
    """Get Workspace Ask Hint

     One question the learner could ask about their current reading context.

    Args:
        workspace_id (str):
        session_id (str | Unset):  Default: ''.
        locator (int | None | Unset):
        selection (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        locator=locator,
        selection=selection,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    workspace_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    locator: int | None | Unset = UNSET,
    selection: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet | None:
    """Get Workspace Ask Hint

     One question the learner could ask about their current reading context.

    Args:
        workspace_id (str):
        session_id (str | Unset):  Default: ''.
        locator (int | None | Unset):
        selection (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet
    """

    return sync_detailed(
        workspace_id=workspace_id,
        client=client,
        session_id=session_id,
        locator=locator,
        selection=selection,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    workspace_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    locator: int | None | Unset = UNSET,
    selection: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet]:
    """Get Workspace Ask Hint

     One question the learner could ask about their current reading context.

    Args:
        workspace_id (str):
        session_id (str | Unset):  Default: ''.
        locator (int | None | Unset):
        selection (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet]
    """

    kwargs = _get_kwargs(
        workspace_id=workspace_id,
        session_id=session_id,
        locator=locator,
        selection=selection,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    workspace_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    locator: int | None | Unset = UNSET,
    selection: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet | None:
    """Get Workspace Ask Hint

     One question the learner could ask about their current reading context.

    Args:
        workspace_id (str):
        session_id (str | Unset):  Default: ''.
        locator (int | None | Unset):
        selection (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseGetWorkspaceAskHintApiReadingWorkspacesWorkspaceIdAskHintGet
    """

    return (
        await asyncio_detailed(
            workspace_id=workspace_id,
            client=client,
            session_id=session_id,
            locator=locator,
            selection=selection,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
