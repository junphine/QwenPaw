from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_revoke_guardian_relationship_api_multi_user_guardians_relationship_id_delete import (
    ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    relationship_id: str,
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
        "url": "/api/multi-user/guardians/{relationship_id}".format(
            relationship_id=quote(str(relationship_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete | None:
    if response.status_code == 200:
        response_200 = ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete.from_dict(
            response.json()
        )

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
) -> Response[HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    relationship_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete]:
    """Revoke Guardian Relationship

    Args:
        relationship_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete]
    """

    kwargs = _get_kwargs(
        relationship_id=relationship_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    relationship_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete | None:
    """Revoke Guardian Relationship

    Args:
        relationship_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete
    """

    return sync_detailed(
        relationship_id=relationship_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    relationship_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete]:
    """Revoke Guardian Relationship

    Args:
        relationship_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete]
    """

    kwargs = _get_kwargs(
        relationship_id=relationship_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    relationship_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete | None:
    """Revoke Guardian Relationship

    Args:
        relationship_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevokeGuardianRelationshipApiMultiUserGuardiansRelationshipIdDelete
    """

    return (
        await asyncio_detailed(
            relationship_id=relationship_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
