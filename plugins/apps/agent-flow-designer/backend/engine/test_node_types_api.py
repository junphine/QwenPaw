# -*- coding: utf-8 -*-
"""Tests for the /node-types API endpoint.

Covers: GET /node-types returns registered node type metadata.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# main.py imports register metadata for built-in nodes;  
# router is the APIRouter we mount on a temporary FastAPI app.
from main import router

# Build a standalone FastAPI app for testing so TestClient works.
_test_app = FastAPI()
_test_app.include_router(router, prefix="/api/agent-flow-designer")
client = TestClient(_test_app)


class TestNodeTypesApi:
    def test_get_node_types_returns_success(self):
        """GET /node-types returns 200 with success flag."""
        response = client.get("/api/agent-flow-designer/node-types")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_node_types_returns_list(self):
        """Response data is a non-empty list of node type metadata."""
        response = client.get("/api/agent-flow-designer/node-types")
        data = response.json()
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_each_item_has_required_fields(self):
        """Each node type metadata has the required fields."""
        response = client.get("/api/agent-flow-designer/node-types")
        data = response.json()
        for item in data["data"]:
            assert "type_id" in item
            assert "label" in item
            assert "description" in item
            assert "icon" in item
            assert "color" in item
            assert "bg_color" in item
            assert "border_color" in item
            assert "properties" in item
            assert "output_fields" in item
            assert "supports_error_policy" in item
            assert "supports_retry" in item

    def test_builtin_types_present(self):
        """Built-in types like 'agent', 'tool', 'router' are present."""
        response = client.get("/api/agent-flow-designer/node-types")
        data = response.json()
        type_ids = {item["type_id"] for item in data["data"]}
        assert "agent" in type_ids
        assert "tool" in type_ids
        assert "router" in type_ids

    def test_agent_has_properties(self):
        """Agent node type has properties describing its config panel."""
        response = client.get("/api/agent-flow-designer/node-types")
        data = response.json()
        agent = next((item for item in data["data"] if item["type_id"] == "agent"), None)
        assert agent is not None
        assert len(agent["properties"]) > 0
        prop_names = {p["name"] for p in agent["properties"]}
        assert "agentId" in prop_names or "outputSchema" in prop_names

    def test_property_field_has_all_keys(self):
        """Each property field exposes all expected keys."""
        response = client.get("/api/agent-flow-designer/node-types")
        data = response.json()
        for item in data["data"]:
            for prop in item["properties"]:
                assert "name" in prop
                assert "type" in prop
                assert "label" in prop
                assert "required" in prop
                assert "default" in prop
                assert "description" in prop
                assert "placeholder" in prop
                assert "options" in prop
