from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_upload_material_api_reading_materials_post import BodyUploadMaterialApiReadingMaterialsPost
from ...models.http_validation_error import HTTPValidationError
from ...models.material_detail import MaterialDetail
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: BodyUploadMaterialApiReadingMaterialsPost,
    reuse: bool | Unset = True,
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

    params["reuse"] = reuse

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/reading/materials",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | MaterialDetail | None:
    if response.status_code == 200:
        response_200 = MaterialDetail.from_dict(response.json())

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
) -> Response[HTTPValidationError | MaterialDetail]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadMaterialApiReadingMaterialsPost,
    reuse: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | MaterialDetail]:
    """Upload Material

     Ingest an uploaded document and return it ready to read.

    The upload is streamed to a temp file with a running size check, so an
    oversized file is rejected before it is fully buffered rather than after.

    Audio and video answer as soon as the file is stored and transcription is
    queued, the same shape as a URL import. Holding the request open for the
    length of a lecture meant no progress could reach the client, the browser
    or a proxy could time the upload out after the transcription had already
    been paid for, and nothing was left on disk to retry from.

    Args:
        reuse (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadMaterialApiReadingMaterialsPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MaterialDetail]
    """

    kwargs = _get_kwargs(
        body=body,
        reuse=reuse,
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
    body: BodyUploadMaterialApiReadingMaterialsPost,
    reuse: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | MaterialDetail | None:
    """Upload Material

     Ingest an uploaded document and return it ready to read.

    The upload is streamed to a temp file with a running size check, so an
    oversized file is rejected before it is fully buffered rather than after.

    Audio and video answer as soon as the file is stored and transcription is
    queued, the same shape as a URL import. Holding the request open for the
    length of a lecture meant no progress could reach the client, the browser
    or a proxy could time the upload out after the transcription had already
    been paid for, and nothing was left on disk to retry from.

    Args:
        reuse (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadMaterialApiReadingMaterialsPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MaterialDetail
    """

    return sync_detailed(
        client=client,
        body=body,
        reuse=reuse,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadMaterialApiReadingMaterialsPost,
    reuse: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | MaterialDetail]:
    """Upload Material

     Ingest an uploaded document and return it ready to read.

    The upload is streamed to a temp file with a running size check, so an
    oversized file is rejected before it is fully buffered rather than after.

    Audio and video answer as soon as the file is stored and transcription is
    queued, the same shape as a URL import. Holding the request open for the
    length of a lecture meant no progress could reach the client, the browser
    or a proxy could time the upload out after the transcription had already
    been paid for, and nothing was left on disk to retry from.

    Args:
        reuse (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadMaterialApiReadingMaterialsPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MaterialDetail]
    """

    kwargs = _get_kwargs(
        body=body,
        reuse=reuse,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadMaterialApiReadingMaterialsPost,
    reuse: bool | Unset = True,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | MaterialDetail | None:
    """Upload Material

     Ingest an uploaded document and return it ready to read.

    The upload is streamed to a temp file with a running size check, so an
    oversized file is rejected before it is fully buffered rather than after.

    Audio and video answer as soon as the file is stored and transcription is
    queued, the same shape as a URL import. Holding the request open for the
    length of a lecture meant no progress could reach the client, the browser
    or a proxy could time the upload out after the transcription had already
    been paid for, and nothing was left on disk to retry from.

    Args:
        reuse (bool | Unset):  Default: True.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadMaterialApiReadingMaterialsPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MaterialDetail
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            reuse=reuse,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
