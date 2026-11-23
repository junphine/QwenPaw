# -*- coding: utf-8 -*-
"""The typed output contract for AFD nodes.

Standard library only: this module is importable without the host package or
the web layer, which is what makes the contract testable in isolation and lets
the API serve it as the single source of truth for the designer.
"""

import copy
import json
import math
from dataclasses import dataclass
from typing import Any, List, Tuple

FIELD_TYPES: Tuple[str, ...] = (
    "string", "number", "integer", "boolean", "object", "array",
)


@dataclass(frozen=True)
class OutputField:
    name: str
    type: str
    required: bool = False
    default: Any = None
    description: str = ""


def _default_matches_type(value: Any, target: str) -> bool:
    if value is None:
        return True
    if target == "string":
        return isinstance(value, str)
    if target == "boolean":
        return isinstance(value, bool)
    if target == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if target == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if target == "object":
        return isinstance(value, dict)
    if target == "array":
        return isinstance(value, list)
    return False


def parse_output_schema(raw: Any) -> Tuple[List[OutputField], List[str]]:
    """Parse a declaration into fields plus declaration-level errors.

    Never raises: a malformed declaration is a graph error the publish gate
    reports, not an exception that takes down the request.
    """
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        return [], ["outputSchema 必须是字段声明数组"]
    if not raw:
        return [], []

    fields: List[OutputField] = []
    errors: List[str] = []
    seen: set = set()
    for index, row in enumerate(raw, start=1):
        if not isinstance(row, dict):
            errors.append(f"第 {index} 行字段声明必须是对象")
            continue
        name = str(row.get("name") or "").strip()
        if not name:
            errors.append(f"第 {index} 行字段名为空")
            continue
        if name in seen:
            errors.append(f"字段名「{name}」重复")
            continue
        target = str(row.get("type") or "").strip()
        if target not in FIELD_TYPES:
            errors.append(f"字段「{name}」的类型「{target or '未填写'}」不受支持")
            continue
        default = row.get("default")
        if not _default_matches_type(default, target):
            errors.append(f"字段「{name}」的默认值与类型「{target}」不符")
            continue
        seen.add(name)
        fields.append(OutputField(
            name=name,
            type=target,
            required=bool(row.get("required")),
            default=default,
            description=str(row.get("description") or ""),
        ))
    return fields, errors


def coerce_scalar(raw: Any, target: str) -> Tuple[Any, bool]:
    """Coerce one value to a declared type, Pydantic-lax style.

    Ambiguity is refused rather than guessed: ``"yes"`` is not a boolean and
    ``True`` is not a number. Guessing turns "the model broke the contract"
    into a plausible-looking wrong answer.
    """
    if target == "string":
        return (raw, True) if isinstance(raw, str) else (None, False)

    if target == "boolean":
        if isinstance(raw, bool):
            return raw, True
        if isinstance(raw, str) and raw.strip().lower() in ("true", "false"):
            return raw.strip().lower() == "true", True
        return None, False

    if target in ("number", "integer"):
        # bool is a subclass of int: check it first or `true` becomes 1.
        if isinstance(raw, bool):
            return None, False
        if isinstance(raw, str):
            try:
                number = float(raw.strip())
            except (TypeError, ValueError):
                return None, False
        elif isinstance(raw, (int, float)):
            number = raw
        else:
            return None, False
        # An int is always finite; math.isfinite() would raise OverflowError on
        # the arbitrary-precision ints json.loads can produce.
        if isinstance(number, float) and not math.isfinite(number):
            return None, False
        if target == "number":
            return number, True
        if isinstance(number, int):
            return number, True
        if float(number).is_integer():
            return int(number), True
        return None, False

    if target == "object":
        return (raw, True) if isinstance(raw, dict) else (None, False)
    if target == "array":
        return (raw, True) if isinstance(raw, list) else (None, False)
    return None, False


def validate_output(value: Any, fields: List[OutputField]) -> Tuple[Any, List[str]]:
    """Check one node output against its declaration.

    Returns ``(None, errors)`` on any violation so a failed node can never
    also publish a half-normalized dict into ``node_outputs``.
    """
    if not isinstance(value, dict):
        return None, ["输出不是 JSON 对象，无法按声明的字段校验"]

    result: dict = {}
    errors: List[str] = []
    for field in fields:
        if field.name not in value:
            if field.required:
                errors.append(f"缺少必填字段「{field.name}」（{field.type}）")
            elif field.default is not None:
                # The default belongs to the persisted config row; handing out
                # the same list twice lets one run corrupt the next.
                result[field.name] = copy.deepcopy(field.default)
            continue
        coerced, ok = coerce_scalar(value[field.name], field.type)
        if not ok:
            errors.append(
                f"字段「{field.name}」期望类型 {field.type}，实际值无法解析为该类型"
            )
            continue
        result[field.name] = coerced
    if errors:
        return None, errors
    return result, []


_FENCE = "```"


def _strip_code_fence(text: str) -> str:
    """Remove one wrapping Markdown fence, and nothing else.

    Only a block that both starts and ends with a fence qualifies. Regexing a
    JSON fragment out of prose, patching trailing commas or converting quotes
    would turn "the model broke the contract" into a silent guess.
    """
    stripped = text.strip()
    if not (stripped.startswith(_FENCE) and stripped.endswith(_FENCE)):
        return stripped
    inner = stripped[len(_FENCE):-len(_FENCE)]
    lines = inner.split("\n")
    first = lines[0].strip()
    if first and " " not in first and first.isalnum():
        lines = lines[1:]
    return "\n".join(lines).strip()


def parse_json_output(text: str) -> Tuple[Any, bool]:
    """Turn one raw agent answer into the object validate_output expects."""
    if not isinstance(text, str) or not text.strip():
        return None, False
    try:
        return json.loads(_strip_code_fence(text)), True
    except (ValueError, TypeError, RecursionError):
        return None, False


SYSTEM_VARIABLE_KEYS: Tuple[str, ...] = (
    "SYS_USER_ID", "USER_UID", "USER_NAME", "USER_LANG",
    "AGENT_ID", "CONVERSATION_ID", "REQUEST_ID"
)

#: The four names _lookup_node_output accepts for a scalar output. They all
#: resolve to the same string; advertising anything else hands the user a
#: dropdown entry the runtime can never resolve.
_SCALAR_ALIASES: Tuple[Tuple[str, str], ...] = (
    ("output", "string"), ("result", "string"),
    ("text", "string"), ("response", "string"),
)

NODE_OUTPUT_CONTRACT = {
    "start": (
        ("user_input", "string"),
        ("user_attachments", "array"),
        ("messages", "array"),
        ("messages_count", "integer"),
    ) + tuple((key, "string") for key in SYSTEM_VARIABLE_KEYS),
    "agent": _SCALAR_ALIASES,
    "tool": _SCALAR_ALIASES,
    "router": (
        ("output", "string"), ("selected_branch", "string"),
        ("branch_name", "string"), ("matched", "boolean"),
        ("routeType", "string"), ("routeReason", "string"),
    ),
    "ask": _SCALAR_ALIASES,
    "end": (),
}


def build_node_contract() -> dict:
    """The payload the designer consumes instead of guessing field names."""
    return {
        "fieldTypes": list(FIELD_TYPES),
        "systemVariables": list(SYSTEM_VARIABLE_KEYS),
        "nodeTypes": [
            {
                "type": node_type,
                "outputFields": [
                    {"name": name, "type": ftype} for name, ftype in fields
                ],
            }
            for node_type, fields in NODE_OUTPUT_CONTRACT.items()
        ],
    }