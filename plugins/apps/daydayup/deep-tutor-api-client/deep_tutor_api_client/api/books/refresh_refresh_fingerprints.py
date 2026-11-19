from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_refresh_fingerprints_api_books_book_id_refresh_fingerprints_post import (
    ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    book_id: str,
    *,
    force: bool | Unset = False,
    expected_revision: int | None | Unset = UNSET,
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

    params["force"] = force

    json_expected_revision: int | None | Unset
    if isinstance(expected_revision, Unset):
        json_expected_revision = UNSET
    else:
        json_expected_revision = expected_revision
    params["expected_revision"] = json_expected_revision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/books/{book_id}/refresh-fingerprints".format(
            book_id=quote(str(book_id), safe=""),
        ),
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost | None:
    if response.status_code == 200:
        response_200 = ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost]:
    """Refresh Fingerprints

     Mark the current KB state as seen.

    409s while pages the last drift flagged are still awaiting recompilation.
    ``force=true`` dismisses them anyway — stale detection over-marks on
    purpose when an anchor cannot be resolved, so the user needs a way out.

    Args:
        book_id (str):
        force (bool | Unset):  Default: False.
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        force=force,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost | None:
    """Refresh Fingerprints

     Mark the current KB state as seen.

    409s while pages the last drift flagged are still awaiting recompilation.
    ``force=true`` dismisses them anyway — stale detection over-marks on
    purpose when an anchor cannot be resolved, so the user needs a way out.

    Args:
        book_id (str):
        force (bool | Unset):  Default: False.
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost
    """

    return sync_detailed(
        book_id=book_id,
        client=client,
        force=force,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost]:
    """Refresh Fingerprints

     Mark the current KB state as seen.

    409s while pages the last drift flagged are still awaiting recompilation.
    ``force=true`` dismisses them anyway — stale detection over-marks on
    purpose when an anchor cannot be resolved, so the user needs a way out.

    Args:
        book_id (str):
        force (bool | Unset):  Default: False.
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost]
    """

    kwargs = _get_kwargs(
        book_id=book_id,
        force=force,
        expected_revision=expected_revision,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    book_id: str,
    *,
    client: AuthenticatedClient | Client,
    force: bool | Unset = False,
    expected_revision: int | None | Unset = UNSET,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost | None:
    """Refresh Fingerprints

     Mark the current KB state as seen.

    409s while pages the last drift flagged are still awaiting recompilation.
    ``force=true`` dismisses them anyway — stale detection over-marks on
    purpose when an anchor cannot be resolved, so the user needs a way out.

    Args:
        book_id (str):
        force (bool | Unset):  Default: False.
        expected_revision (int | None | Unset):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRefreshFingerprintsApiBooksBookIdRefreshFingerprintsPost
    """

    return (
        await asyncio_detailed(
            book_id=book_id,
            client=client,
            force=force,
            expected_revision=expected_revision,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
