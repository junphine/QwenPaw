from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    partner_id: str,
    *,
    session_key: None | str | Unset = UNSET,
    session_id: None | str | Unset = UNSET,
    limit: int | Unset = 100,
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

    json_session_key: None | str | Unset
    if isinstance(session_key, Unset):
        json_session_key = UNSET
    else:
        json_session_key = session_key
    params["session_key"] = json_session_key

    json_session_id: None | str | Unset
    if isinstance(session_id, Unset):
        json_session_id = UNSET
    else:
        json_session_id = session_id
    params["session_id"] = json_session_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/partners/{partner_id}/history".format(
            partner_id=quote(str(partner_id), safe=""),
        ),
        "params": params,
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
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_key: None | str | Unset = UNSET,
    session_id: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Partner History

     Conversation history. Pass ``session_key`` for an exact key, or
    ``session_id`` for a web session (mapped through ``web_session_key``);
    with neither, all non-archived sessions are merged.

    Args:
        partner_id (str):
        session_key (None | str | Unset):
        session_id (None | str | Unset):
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        partner_id=partner_id,
        session_key=session_key,
        session_id=session_id,
        limit=limit,
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
    session_key: None | str | Unset = UNSET,
    session_id: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Partner History

     Conversation history. Pass ``session_key`` for an exact key, or
    ``session_id`` for a web session (mapped through ``web_session_key``);
    with neither, all non-archived sessions are merged.

    Args:
        partner_id (str):
        session_key (None | str | Unset):
        session_id (None | str | Unset):
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        partner_id=partner_id,
        client=client,
        session_key=session_key,
        session_id=session_id,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_key: None | str | Unset = UNSET,
    session_id: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Get Partner History

     Conversation history. Pass ``session_key`` for an exact key, or
    ``session_id`` for a web session (mapped through ``web_session_key``);
    with neither, all non-archived sessions are merged.

    Args:
        partner_id (str):
        session_key (None | str | Unset):
        session_id (None | str | Unset):
        limit (int | Unset):  Default: 100.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        partner_id=partner_id,
        session_key=session_key,
        session_id=session_id,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    partner_id: str,
    *,
    client: AuthenticatedClient | Client,
    session_key: None | str | Unset = UNSET,
    session_id: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Get Partner History

     Conversation history. Pass ``session_key`` for an exact key, or
    ``session_id`` for a web session (mapped through ``web_session_key``);
    with neither, all non-archived sessions are merged.

    Args:
        partner_id (str):
        session_key (None | str | Unset):
        session_id (None | str | Unset):
        limit (int | Unset):  Default: 100.
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
            partner_id=partner_id,
            client=client,
            session_key=session_key,
            session_id=session_id,
            limit=limit,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
