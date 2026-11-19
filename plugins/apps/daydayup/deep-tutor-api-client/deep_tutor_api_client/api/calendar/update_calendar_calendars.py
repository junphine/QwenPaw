from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.calendar_response import CalendarResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.update_calendar import UpdateCalendar
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    body: UpdateCalendar,
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
        "method": "patch",
        "url": "/api/calendar/calendars/{id}".format(
            id=quote(str(id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> CalendarResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CalendarResponse.from_dict(response.json())

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
) -> Response[CalendarResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateCalendar,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[CalendarResponse | HTTPValidationError]:
    """Update Calendar

    Args:
        id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateCalendar):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CalendarResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateCalendar,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> CalendarResponse | HTTPValidationError | None:
    """Update Calendar

    Args:
        id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateCalendar):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CalendarResponse | HTTPValidationError
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateCalendar,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[CalendarResponse | HTTPValidationError]:
    """Update Calendar

    Args:
        id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateCalendar):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CalendarResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateCalendar,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> CalendarResponse | HTTPValidationError | None:
    """Update Calendar

    Args:
        id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateCalendar):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CalendarResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
