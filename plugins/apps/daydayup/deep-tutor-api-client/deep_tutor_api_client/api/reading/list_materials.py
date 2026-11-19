from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_materials_filter import ListMaterialsFilter
from ...models.list_materials_status_type_0 import ListMaterialsStatusType0
from ...models.response_list_library_materials_api_reading_library_materials_get import (
    ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str | Unset = "",
    status: ListMaterialsStatusType0 | None | Unset = UNSET,
    filter_: ListMaterialsFilter | Unset = "all",
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

    params["search"] = search

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, str):
        json_status = status
    else:
        json_status = status
    params["status"] = json_status

    json_filter_: str | Unset = UNSET
    if not isinstance(filter_, Unset):
        json_filter_ = filter_

    params["filter"] = json_filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/reading/library/materials",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet | None:
    if response.status_code == 200:
        response_200 = ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    status: ListMaterialsStatusType0 | None | Unset = UNSET,
    filter_: ListMaterialsFilter | Unset = "all",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet]:
    """List Library Materials

     Every material the owner has, with the collections holding each one.

    Membership travels with the row because the library view exists to answer
    "where is this used, and what did I upload that is used nowhere" — a
    question the client cannot ask one material at a time.

    Args:
        search (str | Unset):  Default: ''.
        status (ListMaterialsStatusType0 | None | Unset):
        filter_ (ListMaterialsFilter | Unset):  Default: 'all'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet]
    """

    kwargs = _get_kwargs(
        search=search,
        status=status,
        filter_=filter_,
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
    search: str | Unset = "",
    status: ListMaterialsStatusType0 | None | Unset = UNSET,
    filter_: ListMaterialsFilter | Unset = "all",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet | None:
    """List Library Materials

     Every material the owner has, with the collections holding each one.

    Membership travels with the row because the library view exists to answer
    "where is this used, and what did I upload that is used nowhere" — a
    question the client cannot ask one material at a time.

    Args:
        search (str | Unset):  Default: ''.
        status (ListMaterialsStatusType0 | None | Unset):
        filter_ (ListMaterialsFilter | Unset):  Default: 'all'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet
    """

    return sync_detailed(
        client=client,
        search=search,
        status=status,
        filter_=filter_,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    status: ListMaterialsStatusType0 | None | Unset = UNSET,
    filter_: ListMaterialsFilter | Unset = "all",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet]:
    """List Library Materials

     Every material the owner has, with the collections holding each one.

    Membership travels with the row because the library view exists to answer
    "where is this used, and what did I upload that is used nowhere" — a
    question the client cannot ask one material at a time.

    Args:
        search (str | Unset):  Default: ''.
        status (ListMaterialsStatusType0 | None | Unset):
        filter_ (ListMaterialsFilter | Unset):  Default: 'all'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet]
    """

    kwargs = _get_kwargs(
        search=search,
        status=status,
        filter_=filter_,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = "",
    status: ListMaterialsStatusType0 | None | Unset = UNSET,
    filter_: ListMaterialsFilter | Unset = "all",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet | None:
    """List Library Materials

     Every material the owner has, with the collections holding each one.

    Membership travels with the row because the library view exists to answer
    "where is this used, and what did I upload that is used nowhere" — a
    question the client cannot ask one material at a time.

    Args:
        search (str | Unset):  Default: ''.
        status (ListMaterialsStatusType0 | None | Unset):
        filter_ (ListMaterialsFilter | Unset):  Default: 'all'.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseListLibraryMaterialsApiReadingLibraryMaterialsGet
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            status=status,
            filter_=filter_,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
