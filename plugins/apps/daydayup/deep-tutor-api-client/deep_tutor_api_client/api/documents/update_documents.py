from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_response import DocumentResponse
from ...models.http_validation_error import HTTPValidationError
from ...models.update_document_request import UpdateDocumentRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    doc_id: str,
    *,
    body: UpdateDocumentRequest,
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
        "url": "/api/documents/{doc_id}".format(
            doc_id=quote(str(doc_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> DocumentResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DocumentResponse.from_dict(response.json())

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
) -> Response[DocumentResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    doc_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDocumentRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[DocumentResponse | HTTPValidationError]:
    """Update Document

     Update a Co-Writer document (title and/or content).

    Args:
        doc_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        doc_id=doc_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    doc_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDocumentRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> DocumentResponse | HTTPValidationError | None:
    """Update Document

     Update a Co-Writer document (title and/or content).

    Args:
        doc_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentResponse | HTTPValidationError
    """

    return sync_detailed(
        doc_id=doc_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    doc_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDocumentRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[DocumentResponse | HTTPValidationError]:
    """Update Document

     Update a Co-Writer document (title and/or content).

    Args:
        doc_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        doc_id=doc_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    doc_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateDocumentRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> DocumentResponse | HTTPValidationError | None:
    """Update Document

     Update a Co-Writer document (title and/or content).

    Args:
        doc_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (UpdateDocumentRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            doc_id=doc_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
