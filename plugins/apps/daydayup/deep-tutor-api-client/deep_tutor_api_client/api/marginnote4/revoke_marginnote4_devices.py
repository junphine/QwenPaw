from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_revoke_device_api_marginnote_4_devices_device_id_delete import (
    ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    device_id: str,
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
        "url": "/api/marginnote4/devices/{device_id}".format(
            device_id=quote(str(device_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete | None:
    if response.status_code == 200:
        response_200 = ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    device_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete]:
    """Revoke Device

     Revoke a paired device.

    Args:
        device_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    device_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete | None:
    """Revoke Device

     Revoke a paired device.

    Args:
        device_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete
    """

    return sync_detailed(
        device_id=device_id,
        client=client,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    device_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete]:
    """Revoke Device

     Revoke a paired device.

    Args:
        device_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    device_id: str,
    *,
    client: AuthenticatedClient | Client,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete | None:
    """Revoke Device

     Revoke a paired device.

    Args:
        device_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRevokeDeviceApiMarginnote4DevicesDeviceIdDelete
    """

    return (
        await asyncio_detailed(
            device_id=device_id,
            client=client,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
