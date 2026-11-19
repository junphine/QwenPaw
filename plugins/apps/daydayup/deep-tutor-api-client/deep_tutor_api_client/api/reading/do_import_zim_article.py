from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_import_zim_article_api_reading_library_import_zim_article_post import (
    ResponseImportZimArticleApiReadingLibraryImportZimArticlePost,
)
from ...models.zim_article_import_request import ZimArticleImportRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ZimArticleImportRequest,
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
        "url": "/api/reading/library/import-zim-article",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost | None:
    if response.status_code == 200:
        response_200 = ResponseImportZimArticleApiReadingLibraryImportZimArticlePost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ZimArticleImportRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost]:
    """Import Zim Article

     Open one selected Kiwix article in Immersive Reading.

    Only its bounded text snapshot enters the reading store.  The ZIM archive
    stays on the existing kiwix-serve instance, without bulk extraction.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ZimArticleImportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost]
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
    body: ZimArticleImportRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost | None:
    """Import Zim Article

     Open one selected Kiwix article in Immersive Reading.

    Only its bounded text snapshot enters the reading store.  The ZIM archive
    stays on the existing kiwix-serve instance, without bulk extraction.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ZimArticleImportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost
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
    body: ZimArticleImportRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost]:
    """Import Zim Article

     Open one selected Kiwix article in Immersive Reading.

    Only its bounded text snapshot enters the reading store.  The ZIM archive
    stays on the existing kiwix-serve instance, without bulk extraction.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ZimArticleImportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost]
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
    body: ZimArticleImportRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost | None:
    """Import Zim Article

     Open one selected Kiwix article in Immersive Reading.

    Only its bounded text snapshot enters the reading store.  The ZIM archive
    stays on the existing kiwix-serve instance, without bulk extraction.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ZimArticleImportRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseImportZimArticleApiReadingLibraryImportZimArticlePost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
