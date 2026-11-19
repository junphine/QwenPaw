from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.response_hub_catalog_api_skills_hub_catalog_get import ResponseHubCatalogApiSkillsHubCatalogGet
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    hub: str | Unset = "eduhub",
    q: str | Unset = "",
    limit: int | Unset = 50,
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

    params["hub"] = hub

    params["q"] = q

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/skills/hub/catalog",
        "params": params,
        "cookies": cookies,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet | None:
    if response.status_code == 200:
        response_200 = ResponseHubCatalogApiSkillsHubCatalogGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    hub: str | Unset = "eduhub",
    q: str | Unset = "",
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet]:
    """Hub Catalog

     Proxy a skill hub's public catalog for the in-app browser.

    The web "Import from EduHub" panel renders these rows in DeepTutor's own
    UI — no embedded iframe, no login — so users can browse, search, and
    one-click download skills. Returns ``web_url`` (the hub's site origin) so
    the panel can offer a "view on EduHub" link out.

    Args:
        hub (str | Unset):  Default: 'eduhub'.
        q (str | Unset):  Default: ''.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet]
    """

    kwargs = _get_kwargs(
        hub=hub,
        q=q,
        limit=limit,
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
    hub: str | Unset = "eduhub",
    q: str | Unset = "",
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet | None:
    """Hub Catalog

     Proxy a skill hub's public catalog for the in-app browser.

    The web "Import from EduHub" panel renders these rows in DeepTutor's own
    UI — no embedded iframe, no login — so users can browse, search, and
    one-click download skills. Returns ``web_url`` (the hub's site origin) so
    the panel can offer a "view on EduHub" link out.

    Args:
        hub (str | Unset):  Default: 'eduhub'.
        q (str | Unset):  Default: ''.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet
    """

    return sync_detailed(
        client=client,
        hub=hub,
        q=q,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    hub: str | Unset = "eduhub",
    q: str | Unset = "",
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet]:
    """Hub Catalog

     Proxy a skill hub's public catalog for the in-app browser.

    The web "Import from EduHub" panel renders these rows in DeepTutor's own
    UI — no embedded iframe, no login — so users can browse, search, and
    one-click download skills. Returns ``web_url`` (the hub's site origin) so
    the panel can offer a "view on EduHub" link out.

    Args:
        hub (str | Unset):  Default: 'eduhub'.
        q (str | Unset):  Default: ''.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet]
    """

    kwargs = _get_kwargs(
        hub=hub,
        q=q,
        limit=limit,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    hub: str | Unset = "eduhub",
    q: str | Unset = "",
    limit: int | Unset = 50,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet | None:
    """Hub Catalog

     Proxy a skill hub's public catalog for the in-app browser.

    The web "Import from EduHub" panel renders these rows in DeepTutor's own
    UI — no embedded iframe, no login — so users can browse, search, and
    one-click download skills. Returns ``web_url`` (the hub's site origin) so
    the panel can offer a "view on EduHub" link out.

    Args:
        hub (str | Unset):  Default: 'eduhub'.
        q (str | Unset):  Default: ''.
        limit (int | Unset):  Default: 50.
        authorization (None | str | Unset):
        dt_token (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseHubCatalogApiSkillsHubCatalogGet
    """

    return (
        await asyncio_detailed(
            client=client,
            hub=hub,
            q=q,
            limit=limit,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
