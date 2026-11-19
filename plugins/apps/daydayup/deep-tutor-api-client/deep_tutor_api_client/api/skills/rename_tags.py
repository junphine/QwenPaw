from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.rename_tag_request import RenameTagRequest
from ...models.response_rename_tag_api_skills_tags_tag_put import ResponseRenameTagApiSkillsTagsTagPut
from ...types import UNSET, Response, Unset


def _get_kwargs(
    tag: str,
    *,
    body: RenameTagRequest,
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
        "url": "/api/skills/tags/{tag}".format(
            tag=quote(str(tag), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut | None:
    if response.status_code == 200:
        response_200 = ResponseRenameTagApiSkillsTagsTagPut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tag: str,
    *,
    client: AuthenticatedClient | Client,
    body: RenameTagRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut]:
    """Rename Tag

    Args:
        tag (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenameTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut]
    """

    kwargs = _get_kwargs(
        tag=tag,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tag: str,
    *,
    client: AuthenticatedClient | Client,
    body: RenameTagRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut | None:
    """Rename Tag

    Args:
        tag (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenameTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut
    """

    return sync_detailed(
        tag=tag,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    tag: str,
    *,
    client: AuthenticatedClient | Client,
    body: RenameTagRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut]:
    """Rename Tag

    Args:
        tag (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenameTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut]
    """

    kwargs = _get_kwargs(
        tag=tag,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tag: str,
    *,
    client: AuthenticatedClient | Client,
    body: RenameTagRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut | None:
    """Rename Tag

    Args:
        tag (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (RenameTagRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseRenameTagApiSkillsTagsTagPut
    """

    return (
        await asyncio_detailed(
            tag=tag,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
