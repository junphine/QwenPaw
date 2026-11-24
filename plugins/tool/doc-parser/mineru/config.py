"""Resolved MinerU backend configuration.

This is the single read-side adapter between the persisted
``document_parsing.json`` settings (owned by :class:`RuntimeSettingsService`)
and the MinerU parser
backend in this package. ``load_mineru_settings`` returns the MinerU engine
slice of the v2 document-parsing structure, so this resolver stays unchanged in
shape. The parser code never touches the storage shape directly — it asks for a
:class:`MinerUConfig` and gets validated, ready-to-use values.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MUNERU_SERVER_URL = "http://8.145.35.112:8003"

from ..types import ParserError

# The MinerU cloud API rejects any single file above 200 pages, so the PDF
# auto-slicer must never emit a part larger than that even if a setting asks
# for it.
MAX_PAGES_PER_PART_CEILING = 200
DEFAULT_MAX_PAGES_PER_PART = 180


class MinerUError(ParserError):
    """Raised when a MinerU parse fails (local CLI missing, cloud API error,
    misconfiguration). Carries a user-facing message; the capability layer
    surfaces it as a stream error. The shared ParserError boundary lets batch
    consumers isolate this document instead of aborting the whole KB (#1982)."""

    def __init__(self, message: str, *, code: str | None = None, detail: str = "") -> None:
        super().__init__(message)
        #: Machine-readable reason when one is known (``LocalParseReason``
        #: values for local failures); ``None`` when the error is raised
        #: without a classification.
        self.code = code
        #: Bounded diagnostic excerpt backing the message; ``""`` when none.
        self.detail = detail


@dataclass(frozen=True)
class MinerUConfig:
    """Validated MinerU parsing configuration.

    ``mode`` is one of ``"local"`` / ``"cloud"``. The cloud branch additionally
    requires ``api_token``; the remaining fields are parsing knobs both
    backends understand (the local CLI ignores the ones it doesn't support).
    """

    mode: str = "local"
    api_base_url: str = DEFAULT_MUNERU_SERVER_URL
    api_token: str | list[str] = ""
    # Explicit path to a local MinerU executable; "" = auto-detect from PATH.
    local_cli_path: str = ""
    # Local-mode model weight download source + optional custom address
    # (HF_ENDPOINT mirror; "" = the source's official address).
    model_download_source: str = "huggingface"
    model_download_endpoint: str = ""
    model_version: str = "pipeline"
    language: str = "auto"
    enable_formula: bool = True
    enable_table: bool = True
    is_ocr: bool = False
    # Cloud-only opt-in; preserves all parser choices and the original PDF.
    normalize_tiny_scans: bool = False
    # When False (default), a local parse fails fast instead of letting the
    # MinerU CLI silently download multi-GB model weights on first run. The user
    # opts in explicitly (Settings → Document Parsing) or via the one-click
    # download button. Cloud mode ignores this (no local models).
    allow_local_model_download: bool = False
    # Cloud-mode PDF auto-slicing. PDFs longer than this many pages are split
    # into per-part PDFs, parsed one by one, and their artifacts merged back
    # into a single working dir (see ``cloud.parse_cloud``). Values above the
    # MinerU cloud ceiling are clamped in ``__post_init__``.
    max_pages_per_part: int = DEFAULT_MAX_PAGES_PER_PART

    def __post_init__(self) -> None:
        if self.max_pages_per_part > MAX_PAGES_PER_PART_CEILING:
            object.__setattr__(self, "max_pages_per_part", MAX_PAGES_PER_PART_CEILING)
        elif self.max_pages_per_part < 1:
            object.__setattr__(self, "max_pages_per_part", 1)

    @property
    def api_language(self) -> str | None:
        """API ``language`` hint. ``"auto"`` maps to ``None`` (let MinerU
        auto-detect) so callers can drop the field from the request body."""
        return None if self.language.lower() == "auto" else self.language

    @property
    def api_keys(self) -> list[str]:
        values = self.api_token if isinstance(self.api_token, list) else [self.api_token]
        return [key for value in values if (key := str(value).strip())]


def resolve_mineru_config() -> MinerUConfig:
    """Load the effective MinerU config from ``document_parsing.json`` (+ env overrides)."""
    from qwenpaw.plugins import get_tool_config
    settings = get_tool_config("mineru_parse") or {}
    return MinerUConfig(
        mode=str(settings.get("mode") or 'local'),
        api_base_url=str(settings.get("api_base_url") or DEFAULT_MUNERU_SERVER_URL),
        api_token=str(settings.get("api_token") or ""),
        local_cli_path=str(settings.get("local_cli_path") or ""),
        model_download_source=str(settings.get("model_download_source") or "huggingface"),
        model_download_endpoint=str(settings.get("model_download_endpoint") or ""),
        model_version=str(settings.get("model_version") or "pipeline"),
        language=str(settings.get("language") or "auto"),
        enable_formula=bool(settings.get("enable_formula", True)),
        enable_table=bool(settings.get("enable_table", True)),
        is_ocr=bool(settings.get("is_ocr", False)),
        normalize_tiny_scans=bool(settings.get("normalize_tiny_scans", False)),
        allow_local_model_download=bool(settings.get("allow_local_model_download", False)),
        max_pages_per_part=(
            DEFAULT_MAX_PAGES_PER_PART
            if settings.get("max_pages_per_part") is None
            else int(settings.get("max_pages_per_part"))  # type: ignore[arg-type]
        ),
    )


__all__ = [
    "DEFAULT_MAX_PAGES_PER_PART",
    "MAX_PAGES_PER_PART_CEILING",
    "MinerUConfig",
    "MinerUError",
    "resolve_mineru_config",
]
