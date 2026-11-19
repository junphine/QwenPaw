from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_update_persona_api_personas_name_put import ResponseUpdatePersonaApiPersonasNamePut
from ...models.update_persona_request import UpdatePersonaRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
    body: UpdatePersonaRequest,
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
        "method": "put",
        "url": "/api/personas/{name}".format(
            name=quote(str(name), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut | None:
    if response.status_code == 200:
        response_200 = ResponseUpdatePersonaApiPersonasNamePut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonaRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut]:
    """Update Persona

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdatePersonaRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonaRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut | None:
    """Update Persona

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdatePersonaRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut
    """

    return sync_detailed(
        name=name,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonaRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut]:
    """Update Persona

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdatePersonaRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonaRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut | None:
    """Update Persona

    Args:
        name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdatePersonaRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseUpdatePersonaApiPersonasNamePut
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
