from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_list_guardian_relationships_api_multi_user_guardians_get import (
    ResponseListGuardianRelationshipsApiMultiUserGuardiansGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    include_revoked: bool | Unset = False,
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

    params["include_revoked"] = include_revoked

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/multi-user/guardians",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet | None:
    if response.status_code == 200:
        response_200 = ResponseListGuardianRelationshipsApiMultiUserGuardiansGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_revoked: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet]:
    """List Guardian Relationships

    Args:
        include_revoked (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet]
    """

    kwargs = _get_kwargs(
        include_revoked=include_revoked,
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
    include_revoked: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet | None:
    """List Guardian Relationships

    Args:
        include_revoked (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet
    """

    return sync_detailed(
        client=client,
        include_revoked=include_revoked,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_revoked: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet]:
    """List Guardian Relationships

    Args:
        include_revoked (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet]
    """

    kwargs = _get_kwargs(
        include_revoked=include_revoked,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    include_revoked: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet | None:
    """List Guardian Relationships

    Args:
        include_revoked (bool | Unset):  Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListGuardianRelationshipsApiMultiUserGuardiansGet
    """

    return (
        await asyncio_detailed(
            client=client,
            include_revoked=include_revoked,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
