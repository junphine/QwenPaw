from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.admin_create_user_request import AdminCreateUserRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_admin_create_user_api_auth_users_post import ResponseAdminCreateUserApiAuthUsersPost
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: AdminCreateUserRequest,
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
        "url": "/api/auth/users",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost | None:
    if response.status_code == 201:
        response_201 = ResponseAdminCreateUserApiAuthUsersPost.from_dict(response.json())

        return response_201

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Response[HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: AdminCreateUserRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost]:
    """Admin Create User

     Admin-only: create one ordinary user account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AdminCreateUserRequest): Admin user-creation payload.

            A preset configures an ordinary account; it never becomes a third role.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost]
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
    body: AdminCreateUserRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost | None:
    """Admin Create User

     Admin-only: create one ordinary user account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AdminCreateUserRequest): Admin user-creation payload.

            A preset configures an ordinary account; it never becomes a third role.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost
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
    body: AdminCreateUserRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost]:
    """Admin Create User

     Admin-only: create one ordinary user account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AdminCreateUserRequest): Admin user-creation payload.

            A preset configures an ordinary account; it never becomes a third role.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost]
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
    body: AdminCreateUserRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost | None:
    """Admin Create User

     Admin-only: create one ordinary user account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (AdminCreateUserRequest): Admin user-creation payload.

            A preset configures an ordinary account; it never becomes a third role.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAdminCreateUserApiAuthUsersPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
