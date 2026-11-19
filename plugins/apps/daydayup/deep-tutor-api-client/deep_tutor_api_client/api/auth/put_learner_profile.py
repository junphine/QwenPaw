from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.learner_profile_request import LearnerProfileRequest
from ...models.response_put_learner_profile_api_auth_users_username_learner_profile_put import (
    ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    username: str,
    *,
    body: LearnerProfileRequest,
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
        "url": "/api/auth/users/{username}/learner-profile".format(
            username=quote(str(username), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut | None:
    if response.status_code == 200:
        response_200 = ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    username: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearnerProfileRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut]:
    """Put Learner Profile

    Args:
        username (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearnerProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    username: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearnerProfileRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut | None:
    """Put Learner Profile

    Args:
        username (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearnerProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut
    """

    return sync_detailed(
        username=username,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    username: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearnerProfileRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut]:
    """Put Learner Profile

    Args:
        username (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearnerProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut]
    """

    kwargs = _get_kwargs(
        username=username,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    username: str,
    *,
    client: AuthenticatedClient | Client,
    body: LearnerProfileRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut | None:
    """Put Learner Profile

    Args:
        username (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (LearnerProfileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponsePutLearnerProfileApiAuthUsersUsernameLearnerProfilePut
    """

    return (
        await asyncio_detailed(
            username=username,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
