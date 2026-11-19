from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx2

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.body_upload_files_api_knowledge_bases_kb_name_upload_post import (
    BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    kb_name: str,
    *,
    body: BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
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
        "url": "/api/knowledge-bases/{kb_name}/upload".format(
            kb_name=quote(str(kb_name), safe=""),
        ),
        "cookies": cookies,
    }

    _kwargs["files"] = body.to_multipart()

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
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Upload Files

     Upload files to a knowledge base and process them in background.

    ``dest_subdir`` places the whole batch under that folder inside the KB.
    A browser folder pick reports each file's path relative to the chosen
    directory, so the directory's own ancestors never reach the server; this
    is how a caller adding one subtree at a time re-attaches it where it
    belongs instead of piling every batch at the root (#866).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadFilesApiKnowledgeBasesKbNameUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Upload Files

     Upload files to a knowledge base and process them in background.

    ``dest_subdir`` places the whole batch under that folder inside the KB.
    A browser folder pick reports each file's path relative to the chosen
    directory, so the directory's own ancestors never reach the server; this
    is how a caller adding one subtree at a time re-attaches it where it
    belongs instead of piling every batch at the root (#866).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadFilesApiKnowledgeBasesKbNameUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        kb_name=kb_name,
        client=client,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    ).parsed


async def asyncio_detailed(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Response[Any | HTTPValidationError]:
    """Upload Files

     Upload files to a knowledge base and process them in background.

    ``dest_subdir`` places the whole batch under that folder inside the KB.
    A browser folder pick reports each file's path relative to the chosen
    directory, so the directory's own ancestors never reach the server; this
    is how a caller adding one subtree at a time re-attaches it where it
    belongs instead of piling every batch at the root (#866).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadFilesApiKnowledgeBasesKbNameUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        kb_name=kb_name,
        body=body,
        authorization=authorization,
        dt_token=dt_token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    kb_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: BodyUploadFilesApiKnowledgeBasesKbNameUploadPost,
    authorization: None | str | Unset = UNSET,
    dt_token: None | str | Unset = UNSET,
) -> Any | HTTPValidationError | None:
    """Upload Files

     Upload files to a knowledge base and process them in background.

    ``dest_subdir`` places the whole batch under that folder inside the KB.
    A browser folder pick reports each file's path relative to the chosen
    directory, so the directory's own ancestors never reach the server; this
    is how a caller adding one subtree at a time re-attaches it where it
    belongs instead of piling every batch at the root (#866).

    Args:
        kb_name (str):
        authorization (None | str | Unset):
        dt_token (None | str | Unset):
        body (BodyUploadFilesApiKnowledgeBasesKbNameUploadPost):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            kb_name=kb_name,
            client=client,
            body=body,
            authorization=authorization,
            dt_token=dt_token,
        )
    ).parsed
