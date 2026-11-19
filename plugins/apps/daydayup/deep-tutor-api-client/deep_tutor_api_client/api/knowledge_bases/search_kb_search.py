from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.knowledge_base_search_request import KnowledgeBaseSearchRequest
from ...models.response_search_knowledge_base_api_knowledge_bases_kb_name_search_post import (
    ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    kb_name: str,
    *,
    body: KnowledgeBaseSearchRequest,
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
        "url": "/api/knowledge-bases/{kb_name}/search".format(
            kb_name=quote(str(kb_name), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost | None:
    if response.status_code == 200:
        response_200 = ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost]:
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
    body: KnowledgeBaseSearchRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost]:
    """Search Knowledge Base

     Run a RAG query against a knowledge base.

    Open API mirroring :func:`deeptutor.tools.rag_tool.rag_search`. The KB is
    resolved through the current user's visibility rules (so ``AccessError``
    for a missing or unassigned KB surfaces as 403/404 via the global handler),
    then the query is delegated to the KB's bound retrieval pipeline. Returns
    the standard RAG envelope (``query``, ``answer``, ``content``, ``sources``,
    ``provider``) plus any pipeline extras (``query_rewrite``, ``warning``,
    ``error_type``, ``needs_reindex``).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KnowledgeBaseSearchRequest): Request body for the knowledge-base RAG search open
            API.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        body=body,
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
    body: KnowledgeBaseSearchRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost | None:
    """Search Knowledge Base

     Run a RAG query against a knowledge base.

    Open API mirroring :func:`deeptutor.tools.rag_tool.rag_search`. The KB is
    resolved through the current user's visibility rules (so ``AccessError``
    for a missing or unassigned KB surfaces as 403/404 via the global handler),
    then the query is delegated to the KB's bound retrieval pipeline. Returns
    the standard RAG envelope (``query``, ``answer``, ``content``, ``sources``,
    ``provider``) plus any pipeline extras (``query_rewrite``, ``warning``,
    ``error_type``, ``needs_reindex``).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KnowledgeBaseSearchRequest): Request body for the knowledge-base RAG search open
            API.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost
    """

    return sync_detailed(
        kb_name=kb_name,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseSearchRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost]:
    """Search Knowledge Base

     Run a RAG query against a knowledge base.

    Open API mirroring :func:`deeptutor.tools.rag_tool.rag_search`. The KB is
    resolved through the current user's visibility rules (so ``AccessError``
    for a missing or unassigned KB surfaces as 403/404 via the global handler),
    then the query is delegated to the KB's bound retrieval pipeline. Returns
    the standard RAG envelope (``query``, ``answer``, ``content``, ``sources``,
    ``provider``) plus any pipeline extras (``query_rewrite``, ``warning``,
    ``error_type``, ``needs_reindex``).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KnowledgeBaseSearchRequest): Request body for the knowledge-base RAG search open
            API.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: KnowledgeBaseSearchRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost | None:
    """Search Knowledge Base

     Run a RAG query against a knowledge base.

    Open API mirroring :func:`deeptutor.tools.rag_tool.rag_search`. The KB is
    resolved through the current user's visibility rules (so ``AccessError``
    for a missing or unassigned KB surfaces as 403/404 via the global handler),
    then the query is delegated to the KB's bound retrieval pipeline. Returns
    the standard RAG envelope (``query``, ``answer``, ``content``, ``sources``,
    ``provider``) plus any pipeline extras (``query_rewrite``, ``warning``,
    ``error_type``, ``needs_reindex``).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KnowledgeBaseSearchRequest): Request body for the knowledge-base RAG search open
            API.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseSearchKnowledgeBaseApiKnowledgeBasesKbNameSearchPost
    """

    return (
        await asyncio_detailed(
            kb_name=kb_name,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
