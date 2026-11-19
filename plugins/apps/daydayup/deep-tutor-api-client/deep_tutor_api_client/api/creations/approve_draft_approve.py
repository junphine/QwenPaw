from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.approve_creation_request import ApproveCreationRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.response_approve_creation_draft_api_creations_drafts_draft_id_approve_post import (
    ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    draft_id: str,
    *,
    body: ApproveCreationRequest,
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
        "url": "/api/creations/drafts/{draft_id}/approve".format(
            draft_id=quote(str(draft_id), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost | None:
    if response.status_code == 200:
        response_200 = ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    draft_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveCreationRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost]:
    """Approve Creation Draft

    Args:
        draft_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApproveCreationRequest): Editable fields accepted by the explicit draft-approval
            step.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost]
    """

    kwargs = _get_kwargs(
        draft_id=draft_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    draft_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveCreationRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost | None:
    """Approve Creation Draft

    Args:
        draft_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApproveCreationRequest): Editable fields accepted by the explicit draft-approval
            step.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost
    """

    return sync_detailed(
        draft_id=draft_id,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    draft_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveCreationRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost]:
    """Approve Creation Draft

    Args:
        draft_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApproveCreationRequest): Editable fields accepted by the explicit draft-approval
            step.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost]
    """

    kwargs = _get_kwargs(
        draft_id=draft_id,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    draft_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveCreationRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost | None:
    """Approve Creation Draft

    Args:
        draft_id (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (ApproveCreationRequest): Editable fields accepted by the explicit draft-approval
            step.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseApproveCreationDraftApiCreationsDraftsDraftIdApprovePost
    """

    return (
        await asyncio_detailed(
            draft_id=draft_id,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
