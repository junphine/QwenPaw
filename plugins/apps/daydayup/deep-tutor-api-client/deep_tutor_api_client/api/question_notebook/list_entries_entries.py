from http import HTTPStatus
from typing import Any, Literal

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_entries_entries_source_type_0 import (
    ListEntriesEntriesSourceType0,
)
from ...models.notebook_entry_list_response import NotebookEntryListResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    category_id: int | None | Unset = UNSET,
    mistakes_only: bool | Unset = False,
    uncategorized: bool | Unset = False,
    bookmarked: bool | None | Unset = UNSET,
    is_correct: bool | None | Unset = UNSET,
    source: ListEntriesEntriesSourceType0 | Literal[""] | Unset = "",
    material_id: str | Unset = "",
    section_id: str | Unset = "",
    assessment_type: str | Unset = "",
    result: str | Unset = "",
    mastery_path_id: str | Unset = "",
    knowledge_point_id: str | Unset = "",
    resolved: bool | None | Unset = UNSET,
    score_trend: str | Unset = "",
    search: str | Unset = "",
    sort: str | Unset = "recent",
    limit: int | Unset = 50,
    offset: int | Unset = 0,
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

    json_category_id: int | None | Unset
    if isinstance(category_id, Unset):
        json_category_id = UNSET
    else:
        json_category_id = category_id
    params["category_id"] = json_category_id

    params["mistakes_only"] = mistakes_only

    params["uncategorized"] = uncategorized

    json_bookmarked: bool | None | Unset
    if isinstance(bookmarked, Unset):
        json_bookmarked = UNSET
    else:
        json_bookmarked = bookmarked
    params["bookmarked"] = json_bookmarked

    json_is_correct: bool | None | Unset
    if isinstance(is_correct, Unset):
        json_is_correct = UNSET
    else:
        json_is_correct = is_correct
    params["is_correct"] = json_is_correct

    json_source: Literal[""] | str | Unset
    if isinstance(source, Unset):
        json_source = UNSET
    elif isinstance(source, str):
        json_source = source
    else:
        json_source = source
    params["source"] = json_source

    params["material_id"] = material_id

    params["section_id"] = section_id

    params["assessment_type"] = assessment_type

    params["result"] = result

    params["mastery_path_id"] = mastery_path_id

    params["knowledge_point_id"] = knowledge_point_id

    json_resolved: bool | None | Unset
    if isinstance(resolved, Unset):
        json_resolved = UNSET
    else:
        json_resolved = resolved
    params["resolved"] = json_resolved

    params["score_trend"] = score_trend

    params["search"] = search

    params["sort"] = sort

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/question-notebook/entries",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | NotebookEntryListResponse | None:
    if response.status_code == 200:
        response_200 = NotebookEntryListResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | NotebookEntryListResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    category_id: int | None | Unset = UNSET,
    mistakes_only: bool | Unset = False,
    uncategorized: bool | Unset = False,
    bookmarked: bool | None | Unset = UNSET,
    is_correct: bool | None | Unset = UNSET,
    source: ListEntriesEntriesSourceType0 | Literal[""] | Unset = "",
    material_id: str | Unset = "",
    section_id: str | Unset = "",
    assessment_type: str | Unset = "",
    result: str | Unset = "",
    mastery_path_id: str | Unset = "",
    knowledge_point_id: str | Unset = "",
    resolved: bool | None | Unset = UNSET,
    score_trend: str | Unset = "",
    search: str | Unset = "",
    sort: str | Unset = "recent",
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NotebookEntryListResponse]:
    """List Entries

    Args:
        category_id (int | None | Unset):
        mistakes_only (bool | Unset):  Default: False.
        uncategorized (bool | Unset): Only entries filed under no category — the triage inbox.
            Ignored when category_id is set. Default: False.
        bookmarked (bool | None | Unset):
        is_correct (bool | None | Unset):
        source (ListEntriesEntriesSourceType0 | Literal[''] | Unset):  Default: ''.
        material_id (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        assessment_type (str | Unset):  Default: ''.
        result (str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        resolved (bool | None | Unset):
        score_trend (str | Unset):  Default: ''.
        search (str | Unset):  Default: ''.
        sort (str | Unset):  Default: 'recent'.
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NotebookEntryListResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        mistakes_only=mistakes_only,
        uncategorized=uncategorized,
        bookmarked=bookmarked,
        is_correct=is_correct,
        source=source,
        material_id=material_id,
        section_id=section_id,
        assessment_type=assessment_type,
        result=result,
        mastery_path_id=mastery_path_id,
        knowledge_point_id=knowledge_point_id,
        resolved=resolved,
        score_trend=score_trend,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
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
    category_id: int | None | Unset = UNSET,
    mistakes_only: bool | Unset = False,
    uncategorized: bool | Unset = False,
    bookmarked: bool | None | Unset = UNSET,
    is_correct: bool | None | Unset = UNSET,
    source: ListEntriesEntriesSourceType0 | Literal[""] | Unset = "",
    material_id: str | Unset = "",
    section_id: str | Unset = "",
    assessment_type: str | Unset = "",
    result: str | Unset = "",
    mastery_path_id: str | Unset = "",
    knowledge_point_id: str | Unset = "",
    resolved: bool | None | Unset = UNSET,
    score_trend: str | Unset = "",
    search: str | Unset = "",
    sort: str | Unset = "recent",
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | NotebookEntryListResponse | None:
    """List Entries

    Args:
        category_id (int | None | Unset):
        mistakes_only (bool | Unset):  Default: False.
        uncategorized (bool | Unset): Only entries filed under no category — the triage inbox.
            Ignored when category_id is set. Default: False.
        bookmarked (bool | None | Unset):
        is_correct (bool | None | Unset):
        source (ListEntriesEntriesSourceType0 | Literal[''] | Unset):  Default: ''.
        material_id (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        assessment_type (str | Unset):  Default: ''.
        result (str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        resolved (bool | None | Unset):
        score_trend (str | Unset):  Default: ''.
        search (str | Unset):  Default: ''.
        sort (str | Unset):  Default: 'recent'.
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NotebookEntryListResponse
    """

    return sync_detailed(
        client=client,
        category_id=category_id,
        mistakes_only=mistakes_only,
        uncategorized=uncategorized,
        bookmarked=bookmarked,
        is_correct=is_correct,
        source=source,
        material_id=material_id,
        section_id=section_id,
        assessment_type=assessment_type,
        result=result,
        mastery_path_id=mastery_path_id,
        knowledge_point_id=knowledge_point_id,
        resolved=resolved,
        score_trend=score_trend,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    category_id: int | None | Unset = UNSET,
    mistakes_only: bool | Unset = False,
    uncategorized: bool | Unset = False,
    bookmarked: bool | None | Unset = UNSET,
    is_correct: bool | None | Unset = UNSET,
    source: ListEntriesEntriesSourceType0 | Literal[""] | Unset = "",
    material_id: str | Unset = "",
    section_id: str | Unset = "",
    assessment_type: str | Unset = "",
    result: str | Unset = "",
    mastery_path_id: str | Unset = "",
    knowledge_point_id: str | Unset = "",
    resolved: bool | None | Unset = UNSET,
    score_trend: str | Unset = "",
    search: str | Unset = "",
    sort: str | Unset = "recent",
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | NotebookEntryListResponse]:
    """List Entries

    Args:
        category_id (int | None | Unset):
        mistakes_only (bool | Unset):  Default: False.
        uncategorized (bool | Unset): Only entries filed under no category — the triage inbox.
            Ignored when category_id is set. Default: False.
        bookmarked (bool | None | Unset):
        is_correct (bool | None | Unset):
        source (ListEntriesEntriesSourceType0 | Literal[''] | Unset):  Default: ''.
        material_id (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        assessment_type (str | Unset):  Default: ''.
        result (str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        resolved (bool | None | Unset):
        score_trend (str | Unset):  Default: ''.
        search (str | Unset):  Default: ''.
        sort (str | Unset):  Default: 'recent'.
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NotebookEntryListResponse]
    """

    kwargs = _get_kwargs(
        category_id=category_id,
        mistakes_only=mistakes_only,
        uncategorized=uncategorized,
        bookmarked=bookmarked,
        is_correct=is_correct,
        source=source,
        material_id=material_id,
        section_id=section_id,
        assessment_type=assessment_type,
        result=result,
        mastery_path_id=mastery_path_id,
        knowledge_point_id=knowledge_point_id,
        resolved=resolved,
        score_trend=score_trend,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    category_id: int | None | Unset = UNSET,
    mistakes_only: bool | Unset = False,
    uncategorized: bool | Unset = False,
    bookmarked: bool | None | Unset = UNSET,
    is_correct: bool | None | Unset = UNSET,
    source: ListEntriesEntriesSourceType0 | Literal[""] | Unset = "",
    material_id: str | Unset = "",
    section_id: str | Unset = "",
    assessment_type: str | Unset = "",
    result: str | Unset = "",
    mastery_path_id: str | Unset = "",
    knowledge_point_id: str | Unset = "",
    resolved: bool | None | Unset = UNSET,
    score_trend: str | Unset = "",
    search: str | Unset = "",
    sort: str | Unset = "recent",
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | NotebookEntryListResponse | None:
    """List Entries

    Args:
        category_id (int | None | Unset):
        mistakes_only (bool | Unset):  Default: False.
        uncategorized (bool | Unset): Only entries filed under no category — the triage inbox.
            Ignored when category_id is set. Default: False.
        bookmarked (bool | None | Unset):
        is_correct (bool | None | Unset):
        source (ListEntriesEntriesSourceType0 | Literal[''] | Unset):  Default: ''.
        material_id (str | Unset):  Default: ''.
        section_id (str | Unset):  Default: ''.
        assessment_type (str | Unset):  Default: ''.
        result (str | Unset):  Default: ''.
        mastery_path_id (str | Unset):  Default: ''.
        knowledge_point_id (str | Unset):  Default: ''.
        resolved (bool | None | Unset):
        score_trend (str | Unset):  Default: ''.
        search (str | Unset):  Default: ''.
        sort (str | Unset):  Default: 'recent'.
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NotebookEntryListResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            category_id=category_id,
            mistakes_only=mistakes_only,
            uncategorized=uncategorized,
            bookmarked=bookmarked,
            is_correct=is_correct,
            source=source,
            material_id=material_id,
            section_id=section_id,
            assessment_type=assessment_type,
            result=result,
            mastery_path_id=mastery_path_id,
            knowledge_point_id=knowledge_point_id,
            resolved=resolved,
            score_trend=score_trend,
            search=search,
            sort=sort,
            limit=limit,
            offset=offset,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
