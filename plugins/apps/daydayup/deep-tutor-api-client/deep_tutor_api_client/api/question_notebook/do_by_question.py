from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.do_by_question_origin_type import DoByQuestionOriginType
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    session_id: str | Unset = "",
    origin_type: DoByQuestionOriginType | Unset = "conversation",
    origin_ref: str | Unset = "",
    question_id: str,
    turn_id: None | str | Unset = UNSET,
    missing_ok: bool | Unset = False,
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

    params["session_id"] = session_id

    json_origin_type: str | Unset = UNSET
    if not isinstance(origin_type, Unset):
        json_origin_type = origin_type

    params["origin_type"] = json_origin_type

    params["origin_ref"] = origin_ref

    params["question_id"] = question_id

    json_turn_id: None | str | Unset
    if isinstance(turn_id, Unset):
        json_turn_id = UNSET
    else:
        json_turn_id = turn_id
    params["turn_id"] = json_turn_id

    params["missing_ok"] = missing_ok

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/question-notebook/entries/lookup/by-question",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> Any | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    origin_type: DoByQuestionOriginType | Unset = "conversation",
    origin_ref: str | Unset = "",
    question_id: str,
    turn_id: None | str | Unset = UNSET,
    missing_ok: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Lookup Entry

    Args:
        session_id (str | Unset):  Default: ''.
        origin_type (DoByQuestionOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        question_id (str):
        turn_id (None | str | Unset):
        missing_ok (bool | Unset): Return 204 No Content instead of 404 when the entry is absent —
            used by the quiz viewer to probe not-yet-saved questions without logging noisy 404s.
            Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        origin_type=origin_type,
        origin_ref=origin_ref,
        question_id=question_id,
        turn_id=turn_id,
        missing_ok=missing_ok,
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
    session_id: str | Unset = "",
    origin_type: DoByQuestionOriginType | Unset = "conversation",
    origin_ref: str | Unset = "",
    question_id: str,
    turn_id: None | str | Unset = UNSET,
    missing_ok: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Lookup Entry

    Args:
        session_id (str | Unset):  Default: ''.
        origin_type (DoByQuestionOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        question_id (str):
        turn_id (None | str | Unset):
        missing_ok (bool | Unset): Return 204 No Content instead of 404 when the entry is absent —
            used by the quiz viewer to probe not-yet-saved questions without logging noisy 404s.
            Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        session_id=session_id,
        origin_type=origin_type,
        origin_ref=origin_ref,
        question_id=question_id,
        turn_id=turn_id,
        missing_ok=missing_ok,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    origin_type: DoByQuestionOriginType | Unset = "conversation",
    origin_ref: str | Unset = "",
    question_id: str,
    turn_id: None | str | Unset = UNSET,
    missing_ok: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Lookup Entry

    Args:
        session_id (str | Unset):  Default: ''.
        origin_type (DoByQuestionOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        question_id (str):
        turn_id (None | str | Unset):
        missing_ok (bool | Unset): Return 204 No Content instead of 404 when the entry is absent —
            used by the quiz viewer to probe not-yet-saved questions without logging noisy 404s.
            Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        origin_type=origin_type,
        origin_ref=origin_ref,
        question_id=question_id,
        turn_id=turn_id,
        missing_ok=missing_ok,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    session_id: str | Unset = "",
    origin_type: DoByQuestionOriginType | Unset = "conversation",
    origin_ref: str | Unset = "",
    question_id: str,
    turn_id: None | str | Unset = UNSET,
    missing_ok: bool | Unset = False,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Lookup Entry

    Args:
        session_id (str | Unset):  Default: ''.
        origin_type (DoByQuestionOriginType | Unset):  Default: 'conversation'.
        origin_ref (str | Unset):  Default: ''.
        question_id (str):
        turn_id (None | str | Unset):
        missing_ok (bool | Unset): Return 204 No Content instead of 404 when the entry is absent —
            used by the quiz viewer to probe not-yet-saved questions without logging noisy 404s.
            Default: False.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            session_id=session_id,
            origin_type=origin_type,
            origin_ref=origin_ref,
            question_id=question_id,
            turn_id=turn_id,
            missing_ok=missing_ok,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
