from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.chat_message_request import ChatMessageRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_partner_chat_http_api_partners_partner_id_chat_post import (
    ResponsePartnerChatHttpApiPartnersPartnerIdChatPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    partner_id: str,
    *,
    body: ChatMessageRequest,
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
        "url": "/api/partners/{partner_id}/chat".format(
            partner_id=quote(str(partner_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost | None:
    if response.status_code == 200:
        response_200 = ResponsePartnerChatHttpApiPartnersPartnerIdChatPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatMessageRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost]:
    """Partner Chat Http

     Send one HTTP message to a partner with persistent session context.

    Args:
        partner_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost]
    """

    kwargs = _get_kwargs(
        partner_id=partner_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatMessageRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost | None:
    """Partner Chat Http

     Send one HTTP message to a partner with persistent session context.

    Args:
        partner_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost
    """

    return sync_detailed(
        partner_id=partner_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatMessageRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost]:
    """Partner Chat Http

     Send one HTTP message to a partner with persistent session context.

    Args:
        partner_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost]
    """

    kwargs = _get_kwargs(
        partner_id=partner_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ChatMessageRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost | None:
    """Partner Chat Http

     Send one HTTP message to a partner with persistent session context.

    Args:
        partner_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ChatMessageRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponsePartnerChatHttpApiPartnersPartnerIdChatPost
    """

    return (
        await asyncio_detailed(
            partner_id=partner_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
