from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_credential_create_request import DeviceCredentialCreateRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_issue_device_api_auth_devices_post import ResponseIssueDeviceApiAuthDevicesPost
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: DeviceCredentialCreateRequest,
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
        "url": "/api/auth/devices",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost | None:
    if response.status_code == 201:
        response_201 = ResponseIssueDeviceApiAuthDevicesPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceCredentialCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost]:
    """Issue Device

     Issue a revocable device credential for an ordinary local account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (DeviceCredentialCreateRequest): Admin payload for issuing a local ordinary-user
            device credential.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost]
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
    body: DeviceCredentialCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost | None:
    """Issue Device

     Issue a revocable device credential for an ordinary local account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (DeviceCredentialCreateRequest): Admin payload for issuing a local ordinary-user
            device credential.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost
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
    body: DeviceCredentialCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost]:
    """Issue Device

     Issue a revocable device credential for an ordinary local account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (DeviceCredentialCreateRequest): Admin payload for issuing a local ordinary-user
            device credential.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost]
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
    body: DeviceCredentialCreateRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost | None:
    """Issue Device

     Issue a revocable device credential for an ordinary local account.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (DeviceCredentialCreateRequest): Admin payload for issuing a local ordinary-user
            device credential.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseIssueDeviceApiAuthDevicesPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
