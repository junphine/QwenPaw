from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_get_reindex_config_api_knowledge_bases_kb_name_reindex_config_get import (
    ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    kb_name: str,
    *,
    embedding_model: str | Unset = "",
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

    params["embedding_model"] = embedding_model

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/knowledge-bases/{kb_name}/reindex-config".format(
            kb_name=quote(str(kb_name), safe=""),
        ),
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet | None:
    if response.status_code == 200:
        response_200 = ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    embedding_model: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet]:
    """Get Reindex Config

     Read selected embedding and current role defaults for rebuild confirmation.

    Args:
        kb_name (str):
        embedding_model (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        embedding_model=embedding_model,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    embedding_model: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet | None:
    """Get Reindex Config

     Read selected embedding and current role defaults for rebuild confirmation.

    Args:
        kb_name (str):
        embedding_model (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet
    """

    return sync_detailed(
        kb_name=kb_name,
        client=client,
        embedding_model=embedding_model,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    embedding_model: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet]:
    """Get Reindex Config

     Read selected embedding and current role defaults for rebuild confirmation.

    Args:
        kb_name (str):
        embedding_model (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        embedding_model=embedding_model,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    embedding_model: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet | None:
    """Get Reindex Config

     Read selected embedding and current role defaults for rebuild confirmation.

    Args:
        kb_name (str):
        embedding_model (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseGetReindexConfigApiKnowledgeBasesKbNameReindexConfigGet
    """

    return (
        await asyncio_detailed(
            kb_name=kb_name,
            client=client,
            embedding_model=embedding_model,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
