"""Docling engine config (read-side adapter over the v2 settings slice)."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_DOCLING_SERVER_URL = "http://localhost:5001"


@dataclass(frozen=True)
class DoclingConfig:
    """Validated Docling configuration.

    ``mode`` is ``"local"`` (the ``docling`` package runs in-process) or
    ``"remote"`` (a Docling Serve HTTP server does the conversion). Remote adds
    ``api_base_url`` and an optional ``api_token`` sent as ``X-Api-Key``. The
    remaining fields are parsing knobs the local converter ignores where it
    doesn't support them.
    """

    mode: str = "remote"
    api_base_url: str = DEFAULT_DOCLING_SERVER_URL
    api_token: str = ""
    do_ocr: bool = False
    do_table_structure: bool = True
    do_formula_enrichment: bool = False
    do_picture_classification: bool = False
    do_picture_description: bool = False
    allow_local_model_download: bool = False


def resolve_docling_config() -> DoclingConfig:
    from qwenpaw.plugins import get_tool_config
    slice_ = get_tool_config("docling_parse") or {}
    return DoclingConfig(
        mode=str(slice_.get("mode") or "remote"),
        api_base_url=str(slice_.get("api_base_url") or DEFAULT_DOCLING_SERVER_URL).rstrip("/"),
        api_token=str(slice_.get("api_token") or ""),
        do_ocr=bool(slice_.get("do_ocr", False)),
        do_table_structure=bool(slice_.get("do_table_structure", True)),
        do_formula_enrichment=bool(slice_.get("do_formula_enrichment", False)),
        do_picture_classification=bool(slice_.get("do_picture_classification", False)),
        do_picture_description=bool(slice_.get("do_picture_description", False)),
        allow_local_model_download=bool(slice_.get("allow_local_model_download", False)),
    )


__all__ = ["DoclingConfig", "resolve_docling_config"]
