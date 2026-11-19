from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    kb_name: str,
    folder_path: str,
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
        "url": "/api/knowledge-bases/{kb_name}/folders/{folder_path}".format(
            kb_name=quote(str(kb_name), safe=""),
            folder_path=quote(str(folder_path), safe=""),
        ),
        "cookies": cookies,
    }

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
    kb_name: str,
    folder_path: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Delete Kb Folder

     Remove a whole folder and everything beneath it from a knowledge base.

    Deletes the folder, its files, and any nested subfolders. Like single-file
    deletion this works while the KB is in an *error* state, and connected
    (read-only) / legacy KBs are rejected. Vectors are not pruned here;
    ``was_indexed`` tells the caller whether a re-index is needed to purge the
    removed documents from retrieval.

    Args:
        kb_name (str):
        folder_path (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        folder_path=folder_path,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    kb_name: str,
    folder_path: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Delete Kb Folder

     Remove a whole folder and everything beneath it from a knowledge base.

    Deletes the folder, its files, and any nested subfolders. Like single-file
    deletion this works while the KB is in an *error* state, and connected
    (read-only) / legacy KBs are rejected. Vectors are not pruned here;
    ``was_indexed`` tells the caller whether a re-index is needed to purge the
    removed documents from retrieval.

    Args:
        kb_name (str):
        folder_path (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        kb_name=kb_name,
        folder_path=folder_path,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    kb_name: str,
    folder_path: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Delete Kb Folder

     Remove a whole folder and everything beneath it from a knowledge base.

    Deletes the folder, its files, and any nested subfolders. Like single-file
    deletion this works while the KB is in an *error* state, and connected
    (read-only) / legacy KBs are rejected. Vectors are not pruned here;
    ``was_indexed`` tells the caller whether a re-index is needed to purge the
    removed documents from retrieval.

    Args:
        kb_name (str):
        folder_path (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        folder_path=folder_path,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kb_name: str,
    folder_path: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Delete Kb Folder

     Remove a whole folder and everything beneath it from a knowledge base.

    Deletes the folder, its files, and any nested subfolders. Like single-file
    deletion this works while the KB is in an *error* state, and connected
    (read-only) / legacy KBs are rejected. Vectors are not pruned here;
    ``was_indexed`` tells the caller whether a re-index is needed to purge the
    removed documents from retrieval.

    Args:
        kb_name (str):
        folder_path (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            kb_name=kb_name,
            folder_path=folder_path,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
