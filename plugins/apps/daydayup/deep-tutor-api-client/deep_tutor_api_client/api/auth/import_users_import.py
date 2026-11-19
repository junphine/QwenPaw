from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_admin_import_users_api_auth_users_import_post import BodyAdminImportUsersApiAuthUsersImportPost
from ...models.http_validation_error import HTTPValidationError
from ...models.response_admin_import_users_api_auth_users_import_post import (
    ResponseAdminImportUsersApiAuthUsersImportPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodyAdminImportUsersApiAuthUsersImportPost,
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
        "url": "/api/auth/users/import",
        "cookies": cookies,
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost | None:
    if response.status_code == 200:
        response_200 = ResponseAdminImportUsersApiAuthUsersImportPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BodyAdminImportUsersApiAuthUsersImportPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost]:
    """Admin Import Users

     Admin-only: provision ordinary users from a CSV file.

    The response is row-oriented so one invalid record does not erase the
    context of the valid records around it. Passwords are never returned.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyAdminImportUsersApiAuthUsersImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost]
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
    body: BodyAdminImportUsersApiAuthUsersImportPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost | None:
    """Admin Import Users

     Admin-only: provision ordinary users from a CSV file.

    The response is row-oriented so one invalid record does not erase the
    context of the valid records around it. Passwords are never returned.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyAdminImportUsersApiAuthUsersImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost
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
    body: BodyAdminImportUsersApiAuthUsersImportPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost]:
    """Admin Import Users

     Admin-only: provision ordinary users from a CSV file.

    The response is row-oriented so one invalid record does not erase the
    context of the valid records around it. Passwords are never returned.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyAdminImportUsersApiAuthUsersImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost]
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
    body: BodyAdminImportUsersApiAuthUsersImportPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost | None:
    """Admin Import Users

     Admin-only: provision ordinary users from a CSV file.

    The response is row-oriented so one invalid record does not erase the
    context of the valid records around it. Passwords are never returned.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyAdminImportUsersApiAuthUsersImportPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseAdminImportUsersApiAuthUsersImportPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
