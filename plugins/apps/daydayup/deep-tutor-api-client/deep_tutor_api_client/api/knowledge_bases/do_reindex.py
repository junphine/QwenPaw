from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_reindex_knowledge_base_api_knowledge_bases_kb_name_reindex_post import (
    BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.response_reindex_knowledge_base_api_knowledge_bases_kb_name_reindex_post import (
    ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    kb_name: str,
    *,
    body: BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset = UNSET,
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
        "url": "/api/knowledge-bases/{kb_name}/reindex".format(
            kb_name=quote(str(kb_name), safe=""),
        ),
        "cookies": cookies,
    }

    if not isinstance(body, Unset):
        _kwargs["data"] = body.to_dict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | None:
    if response.status_code == 200:
        response_200 = ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost]:
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
    body: BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost]:
    """Reindex Knowledge Base

     Re-index ``kb_name`` through its bound RAG provider.

    LlamaIndex keys versions by the selected embedding model. The other
    providers keep synthetic provider-keyed versions, so they should rebuild
    without requiring an embedding-signature precheck.

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost]
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
    body: BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | None:
    """Reindex Knowledge Base

     Re-index ``kb_name`` through its bound RAG provider.

    LlamaIndex keys versions by the selected embedding model. The other
    providers keep synthetic provider-keyed versions, so they should rebuild
    without requiring an embedding-signature precheck.

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost
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
    body: BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost]:
    """Reindex Knowledge Base

     Re-index ``kb_name`` through its bound RAG provider.

    LlamaIndex keys versions by the selected embedding model. The other
    providers keep synthetic provider-keyed versions, so they should rebuild
    without requiring an embedding-signature precheck.

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost]
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
    body: BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | None:
    """Reindex Knowledge Base

     Re-index ``kb_name`` through its bound RAG provider.

    LlamaIndex keys versions by the selected embedding model. The other
    providers keep synthetic provider-keyed versions, so they should rebuild
    without requiring an embedding-signature precheck.

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost
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
