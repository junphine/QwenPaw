from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_estimate_basis_api_books_estimate_basis_get import ResponseEstimateBasisApiBooksEstimateBasisGet
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    depth: str | Unset = "standard",
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

    params["depth"] = depth

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/books/estimate-basis",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet | None:
    if response.status_code == 200:
        response_200 = ResponseEstimateBasisApiBooksEstimateBasisGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    depth: str | Unset = "standard",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet]:
    """Estimate Basis

     Per-chapter generation cost, keyed by content type.

    The spine editor sums this over whatever chapters currently exist, so the
    estimate stays live while the user edits without a request per keystroke —
    and stays honest, because the numbers come from the same templates the
    architect plans from.

    Args:
        depth (str | Unset):  Default: 'standard'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet]
    """

    kwargs = _get_kwargs(
        depth=depth,
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
    depth: str | Unset = "standard",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet | None:
    """Estimate Basis

     Per-chapter generation cost, keyed by content type.

    The spine editor sums this over whatever chapters currently exist, so the
    estimate stays live while the user edits without a request per keystroke —
    and stays honest, because the numbers come from the same templates the
    architect plans from.

    Args:
        depth (str | Unset):  Default: 'standard'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet
    """

    return sync_detailed(
        client=client,
        depth=depth,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    depth: str | Unset = "standard",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet]:
    """Estimate Basis

     Per-chapter generation cost, keyed by content type.

    The spine editor sums this over whatever chapters currently exist, so the
    estimate stays live while the user edits without a request per keystroke —
    and stays honest, because the numbers come from the same templates the
    architect plans from.

    Args:
        depth (str | Unset):  Default: 'standard'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet]
    """

    kwargs = _get_kwargs(
        depth=depth,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    depth: str | Unset = "standard",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet | None:
    """Estimate Basis

     Per-chapter generation cost, keyed by content type.

    The spine editor sums this over whatever chapters currently exist, so the
    estimate stays live while the user edits without a request per keystroke —
    and stays honest, because the numbers come from the same templates the
    architect plans from.

    Args:
        depth (str | Unset):  Default: 'standard'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseEstimateBasisApiBooksEstimateBasisGet
    """

    return (
        await asyncio_detailed(
            client=client,
            depth=depth,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
