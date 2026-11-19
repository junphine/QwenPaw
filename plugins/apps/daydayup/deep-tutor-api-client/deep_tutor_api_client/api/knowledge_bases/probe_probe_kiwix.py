from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.kiwix_connection_request import KiwixConnectionRequest
from ...models.response_probe_kiwix_route_api_knowledge_bases_probe_kiwix_post import (
    ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: KiwixConnectionRequest,
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
        "url": "/api/knowledge-bases/probe-kiwix",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost | None:
    if response.status_code == 200:
        response_200 = ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: KiwixConnectionRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost]:
    """Probe Kiwix Route

     Verify that one archive is readable without copying its ZIM file.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KiwixConnectionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: KiwixConnectionRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost | None:
    """Probe Kiwix Route

     Verify that one archive is readable without copying its ZIM file.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KiwixConnectionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: KiwixConnectionRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost]:
    """Probe Kiwix Route

     Verify that one archive is readable without copying its ZIM file.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KiwixConnectionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: KiwixConnectionRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost | None:
    """Probe Kiwix Route

     Verify that one archive is readable without copying its ZIM file.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (KiwixConnectionRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseProbeKiwixRouteApiKnowledgeBasesProbeKiwixPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
