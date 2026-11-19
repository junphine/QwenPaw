from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    code: str | Unset = "",
    state: str | Unset = "",
    error: str | Unset = "",
    error_description: str | Unset = "",
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

    params["code"] = code

    params["state"] = state

    params["error"] = error

    params["error_description"] = error_description

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/space/mcp/oauth/callback",
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
    code: str | Unset = "",
    state: str | Unset = "",
    error: str | Unset = "",
    error_description: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Oauth Callback

     Where the authorization server sends the browser back.

    Deliberately **not** returning JSON: a person is looking at this, having just
    clicked Approve on somebody else's site. It answers with a small page that
    says what happened and closes itself.

    An unknown ``state`` completes nothing — see ``complete_authorization``.

    Args:
        code (str | Unset):  Default: ''.
        state (str | Unset):  Default: ''.
        error (str | Unset):  Default: ''.
        error_description (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
        error=error,
        error_description=error_description,
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
    code: str | Unset = "",
    state: str | Unset = "",
    error: str | Unset = "",
    error_description: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Oauth Callback

     Where the authorization server sends the browser back.

    Deliberately **not** returning JSON: a person is looking at this, having just
    clicked Approve on somebody else's site. It answers with a small page that
    says what happened and closes itself.

    An unknown ``state`` completes nothing — see ``complete_authorization``.

    Args:
        code (str | Unset):  Default: ''.
        state (str | Unset):  Default: ''.
        error (str | Unset):  Default: ''.
        error_description (str | Unset):  Default: ''.
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
        code=code,
        state=state,
        error=error,
        error_description=error_description,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = "",
    state: str | Unset = "",
    error: str | Unset = "",
    error_description: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Oauth Callback

     Where the authorization server sends the browser back.

    Deliberately **not** returning JSON: a person is looking at this, having just
    clicked Approve on somebody else's site. It answers with a small page that
    says what happened and closes itself.

    An unknown ``state`` completes nothing — see ``complete_authorization``.

    Args:
        code (str | Unset):  Default: ''.
        state (str | Unset):  Default: ''.
        error (str | Unset):  Default: ''.
        error_description (str | Unset):  Default: ''.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        code=code,
        state=state,
        error=error,
        error_description=error_description,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    code: str | Unset = "",
    state: str | Unset = "",
    error: str | Unset = "",
    error_description: str | Unset = "",
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Oauth Callback

     Where the authorization server sends the browser back.

    Deliberately **not** returning JSON: a person is looking at this, having just
    clicked Approve on somebody else's site. It answers with a small page that
    says what happened and closes itself.

    An unknown ``state`` completes nothing — see ``complete_authorization``.

    Args:
        code (str | Unset):  Default: ''.
        state (str | Unset):  Default: ''.
        error (str | Unset):  Default: ''.
        error_description (str | Unset):  Default: ''.
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
            code=code,
            state=state,
            error=error,
            error_description=error_description,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
