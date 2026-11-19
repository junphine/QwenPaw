# -*- coding: utf-8 -*-
"""Tests for the extended node registry with metadata support (#8).

Covers: NodeTypeDef, PropertyField, register_node with metadata,
get_node_type_def, list_node_type_defs, and the new _REGISTRY structure.
"""

import pytest
from engine.registry import (
    NodeTypeDef,
    PropertyField,
    get_handler,
    get_node_type_def,
    list_node_type_defs,
    register_node,
    registered_types,
)


# ── PropertyField ───────────────────────────────────────────────────────────

class TestPropertyField:
    def test_defaults(self):
        pf = PropertyField(name="code", type="textarea", label="代码")
        assert pf.name == "code"
        assert pf.type == "textarea"
        assert pf.label == "代码"
        assert pf.required is False
        assert pf.default is None
        assert pf.description == ""
        assert pf.placeholder == ""
        assert pf.options == []
        assert pf.condition_field == ""
        assert pf.condition_value is None

    def test_full_init(self):
        pf = PropertyField(
            name="language",
            type="select",
            label="语言",
            required=True,
            default="python",
            description="选择编程语言",
            placeholder="python",
            options=[{"value": "python", "label": "Python"}, {"value": "js", "label": "JavaScript"}],
            condition_field="source",
            condition_value="code",
        )
        assert pf.required is True
        assert pf.default == "python"
        assert pf.options[0]["value"] == "python"


# ── NodeTypeDef ─────────────────────────────────────────────────────────────

class TestNodeTypeDef:
    def test_defaults(self):
        nt = NodeTypeDef(type_id="test", label="测试")
        assert nt.type_id == "test"
        assert nt.label == "测试"
        assert nt.description == ""
        assert nt.icon == "default"
        assert nt.color == "#6366F1"
        assert nt.bg_color == "#eef2ff"
        assert nt.border_color == "#6366F1"
        assert nt.properties == []
        assert nt.output_fields == []
        assert nt.supports_error_policy is False
        assert nt.supports_retry is False
        assert nt.custom_renderer is None

    def test_with_properties(self):
        nt = NodeTypeDef(
            type_id="code",
            label="Code",
            properties=[
                PropertyField(name="language", type="select", label="语言"),
                PropertyField(name="code", type="textarea", label="代码", required=True),
            ],
            supports_error_policy=True,
            supports_retry=True,
        )
        assert len(nt.properties) == 2
        assert nt.properties[0].name == "language"
        assert nt.properties[1].required is True
        assert nt.supports_error_policy is True


# ── Registry operations ─────────────────────────────────────────────────────

class TestRegistryMetadata:
    def test_register_node_with_metadata(self):
        """register_node accepts optional metadata and stores it."""
        meta = NodeTypeDef(type_id="test_agent", label="Agent")

        @register_node("test_agent", metadata=meta)
        async def handle_agent(ctx):
            pass

        assert get_handler("test_agent") is handle_agent
        assert get_node_type_def("test_agent") is meta

    def test_register_node_without_metadata(self):
        """Nodes without metadata are still callable, but get_node_type_def returns None."""

        @register_node("legacy")
        async def handle_legacy(ctx):
            pass

        assert get_handler("legacy") is handle_legacy
        assert get_node_type_def("legacy") is None

    def test_list_node_type_defs_returns_only_nodes_with_metadata(self):
        """list_node_type_defs skips nodes registered without metadata."""

        @register_node("with_meta", metadata=NodeTypeDef(type_id="with_meta", label="有元数据"))
        async def handle_with_meta(ctx):
            pass

        @register_node("without_meta")
        async def handle_without_meta(ctx):
            pass

        defs = list_node_type_defs()
        type_ids = [d.type_id for d in defs]
        assert "with_meta" in type_ids
        assert "without_meta" not in type_ids

    def test_registered_types_includes_all(self):
        """registered_types includes every registered type, with or without metadata."""
        before = len(registered_types())

        @register_node("all_types_test", metadata=NodeTypeDef(type_id="all_types_test", label="Test"))
        async def handle(ctx):
            pass

        assert "all_types_test" in registered_types()

    def test_get_node_type_def_returns_none_for_unknown(self):
        assert get_node_type_def("nonexistent") is None

    def test_multiple_properties_accessible(self):
        meta = NodeTypeDef(
            type_id="complex",
            label="复杂节点",
            properties=[
                PropertyField(name="name", type="text", label="名称"),
                PropertyField(name="count", type="number", label="数量", default=0),
            ],
            output_fields=[{"name": "result", "type": "string"}],
        )

        @register_node("complex", metadata=meta)
        async def handle(ctx):
            pass

        defn = get_node_type_def("complex")
        assert defn is not None
        assert defn.properties[0].type == "text"
        assert defn.properties[1].default == 0
        assert defn.output_fields[0]["name"] == "result"
