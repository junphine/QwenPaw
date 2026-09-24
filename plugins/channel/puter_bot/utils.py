# -*- coding: utf-8 -*-
"""Puter channel utilities for file handling."""

import mimetypes
from pathlib import Path
from typing import Optional
import httpx
import aiohttp
import uuid
import logging
logger = logging.getLogger(__name__)

def sync_puter_login(imUrl,apiUrl,uuid,authCode):
    data = {"apiUrl": apiUrl, "uuid": uuid, "authCode": authCode,"device":"web"}
    response = httpx.post(
        imUrl+"/puter/login",
        json=data,
        timeout=10.0
    )
    return response.json()


async def download_file(
    url: str,
    media_dir: Path,
    filename: str,
) -> Optional[str]:
    """Download file from URL to media_dir, return local path."""
    media_dir.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status >= 400:
                    return None

                data = await resp.read()
                content_type = (
                    resp.headers.get("Content-Type", "").split(";")[0].strip()
                )

                # Determine extension
                ext = ""
                if content_type:
                    ext = mimetypes.guess_extension(content_type) or ""
                if not ext:
                    ext = Path(filename).suffix or ".bin"

                # Build safe filename
                safe_name = "".join(
                    c for c in filename if c.isalnum() or c in "-_."
                )
                if not safe_name:
                    safe_name = "file"

                # Ensure unique extension
                if not Path(safe_name).suffix and ext:
                    safe_name = f"{Path(safe_name).stem}{ext}"

                path = media_dir / safe_name
                path.write_bytes(data)
                return str(path)

        except Exception:
            return None


async def _download_puter_file(
        *,
        http: httpx.AsyncClient,
        url: str,
        file_id: str,
        media_dir: Path,
        filename_hint: str = "",
) -> Optional[str]:
    """Stream-download a Mattermost file to local media_dir; return path."""
    try:
        media_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(filename_hint).suffix if filename_hint else ""
        local_name = f"{uuid.uuid4().hex[:12]}{suffix or '.bin'}"
        local_path = media_dir / local_name
        async with http.stream("GET", url) as resp:
            if resp.status_code != 200:
                logger.warning(
                    "puter: download %s returned %s",
                    file_id,
                    resp.status_code,
                )
                return None
            with open(local_path, "wb") as fh:
                async for chunk in resp.aiter_bytes(65536):
                    fh.write(chunk)
        return str(local_path)
    except Exception:
        logger.exception("puter: download failed for file_id=%s", file_id)
        return None

