from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.practice_question import PracticeQuestion
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    timezone: str | Unset = "UTC",
    category_id: int | None | Unset = UNSET,
    limit: int | Unset = 20,
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

    params["timezone"] = timezone

    json_category_id: int | None | Unset
    if isinstance(category_id, Unset):
        json_category_id = UNSET
    else:
        json_category_id = category_id
    params["category_id"] = json_category_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/question-notebook/practice/queue",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | list[PracticeQuestion] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PracticeQuestion.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[PracticeQuestion]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    timezone: str | Unset = "UTC",
    category_id: int | None | Unset = UNSET,
    limit: int | Unset = 20,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[PracticeQuestion]]:
    """Queue

    Args:
        timezone (str | Unset):  Default: 'UTC'.
        category_id (int | None | Unset):
        limit (int | Unset):  Default: 20.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[PracticeQuestion]]
    """

    kwargs = _get_kwargs(
        timezone=timezone,
        category_id=category_id,
        limit=limit,
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
    timezone: str | Unset = "UTC",
    category_id: int | None | Unset = UNSET,
    limit: int | Unset = 20,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | list[PracticeQuestion] | None:
    """Queue

    Args:
        timezone (str | Unset):  Default: 'UTC'.
        category_id (int | None | Unset):
        limit (int | Unset):  Default: 20.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[PracticeQuestion]
    """

    return sync_detailed(
        client=client,
        timezone=timezone,
        category_id=category_id,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    timezone: str | Unset = "UTC",
    category_id: int | None | Unset = UNSET,
    limit: int | Unset = 20,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | list[PracticeQuestion]]:
    """Queue

    Args:
        timezone (str | Unset):  Default: 'UTC'.
        category_id (int | None | Unset):
        limit (int | Unset):  Default: 20.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[PracticeQuestion]]
    """

    kwargs = _get_kwargs(
        timezone=timezone,
        category_id=category_id,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    timezone: str | Unset = "UTC",
    category_id: int | None | Unset = UNSET,
    limit: int | Unset = 20,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | list[PracticeQuestion] | None:
    """Queue

    Args:
        timezone (str | Unset):  Default: 'UTC'.
        category_id (int | None | Unset):
        limit (int | Unset):  Default: 20.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[PracticeQuestion]
    """

    return (
        await asyncio_detailed(
            client=client,
            timezone=timezone,
            category_id=category_id,
            limit=limit,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
