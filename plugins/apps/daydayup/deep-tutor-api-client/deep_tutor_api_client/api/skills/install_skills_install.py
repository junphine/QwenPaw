from http import HTTPStatus
from typing import Any

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.install_skill_request import InstallSkillRequest
from ...models.response_install_skill_api_skills_install_post import ResponseInstallSkillApiSkillsInstallPost
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: InstallSkillRequest,
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
        "url": "/api/skills/install",
        "cookies": cookies,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx2.Response
) -> HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost | None:
    if response.status_code == 200:
        response_200 = ResponseInstallSkillApiSkillsInstallPost.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: InstallSkillRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost]:
    """Install Skill

     Import a hub skill (e.g. from EduHub) into the caller's own skill layer.

    Lands the package in the same per-user dir that ``/create`` writes to, so
    the imported skill shows up in this user's Skills list. The install gate
    (``suspicious`` verdict abort, safe extraction, ``always`` stripping)
    lives in :func:`deeptutor.services.skill.hub.install_from_hub`.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (InstallSkillRequest): Install a hub skill into the caller's own skill layer.

            ``ref`` is a ``<hub>:<slug>[@version]`` reference (the bare hub prefix
            defaults to ``eduhub``). The web "import from EduHub" flow always builds an
            ``eduhub:`` ref so a spoofed bridge message can't redirect the install to an
            arbitrary registry.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: InstallSkillRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost | None:
    """Install Skill

     Import a hub skill (e.g. from EduHub) into the caller's own skill layer.

    Lands the package in the same per-user dir that ``/create`` writes to, so
    the imported skill shows up in this user's Skills list. The install gate
    (``suspicious`` verdict abort, safe extraction, ``always`` stripping)
    lives in :func:`deeptutor.services.skill.hub.install_from_hub`.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (InstallSkillRequest): Install a hub skill into the caller's own skill layer.

            ``ref`` is a ``<hub>:<slug>[@version]`` reference (the bare hub prefix
            defaults to ``eduhub``). The web "import from EduHub" flow always builds an
            ``eduhub:`` ref so a spoofed bridge message can't redirect the install to an
            arbitrary registry.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost
    """

    return sync_detailed(
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: InstallSkillRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost]:
    """Install Skill

     Import a hub skill (e.g. from EduHub) into the caller's own skill layer.

    Lands the package in the same per-user dir that ``/create`` writes to, so
    the imported skill shows up in this user's Skills list. The install gate
    (``suspicious`` verdict abort, safe extraction, ``always`` stripping)
    lives in :func:`deeptutor.services.skill.hub.install_from_hub`.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (InstallSkillRequest): Install a hub skill into the caller's own skill layer.

            ``ref`` is a ``<hub>:<slug>[@version]`` reference (the bare hub prefix
            defaults to ``eduhub``). The web "import from EduHub" flow always builds an
            ``eduhub:`` ref so a spoofed bridge message can't redirect the install to an
            arbitrary registry.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost]
    """

    kwargs = _get_kwargs(
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: InstallSkillRequest,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost | None:
    """Install Skill

     Import a hub skill (e.g. from EduHub) into the caller's own skill layer.

    Lands the package in the same per-user dir that ``/create`` writes to, so
    the imported skill shows up in this user's Skills list. The install gate
    (``suspicious`` verdict abort, safe extraction, ``always`` stripping)
    lives in :func:`deeptutor.services.skill.hub.install_from_hub`.

    Args:
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (InstallSkillRequest): Install a hub skill into the caller's own skill layer.

            ``ref`` is a ``<hub>:<slug>[@version]`` reference (the bare hub prefix
            defaults to ``eduhub``). The web "import from EduHub" flow always builds an
            ``eduhub:`` ref so a spoofed bridge message can't redirect the install to an
            arbitrary registry.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResponseInstallSkillApiSkillsInstallPost
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
