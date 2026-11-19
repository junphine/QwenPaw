from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.review_settings_request import ReviewSettingsRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    path_id: str,
    *,
    body: ReviewSettingsRequest,
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
        "url": "/api/mastery-paths/topics/{path_id}/review-settings".format(
            path_id=quote(str(path_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

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
    path_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ReviewSettingsRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Review Settings

    Args:
        path_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ReviewSettingsRequest): A per-path recall target; higher values schedule shorter
            intervals.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        path_id=path_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    path_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ReviewSettingsRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Review Settings

    Args:
        path_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ReviewSettingsRequest): A per-path recall target; higher values schedule shorter
            intervals.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        path_id=path_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    path_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ReviewSettingsRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Update Review Settings

    Args:
        path_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ReviewSettingsRequest): A per-path recall target; higher values schedule shorter
            intervals.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        path_id=path_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    path_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ReviewSettingsRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Update Review Settings

    Args:
        path_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ReviewSettingsRequest): A per-path recall target; higher values schedule shorter
            intervals.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            path_id=path_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
