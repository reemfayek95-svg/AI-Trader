"""
Integration tests for configuration loading (main.py / configs/).

Tests cover:
- load_config reads and validates the default JSON config
- load_config raises SystemExit for missing files
- Configuration structure (required keys, types)
- get_agent_class registry lookup
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

class TestLoadConfig:
    """Tests for main.load_config."""

    @pytest.fixture(autouse=True)
    def _import_main(self):
        import importlib
        import main as m
        importlib.reload(m)
        self.load_config = m.load_config
        self.get_agent_class = m.get_agent_class

    def test_loads_default_config(self):
        default_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "configs",
            "default_config.json",
        )
        config = self.load_config(default_path)
        assert isinstance(config, dict)

    def test_default_config_has_required_keys(self):
        default_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "configs",
            "default_config.json",
        )
        config = self.load_config(default_path)
        for key in ("agent_type", "market", "date_range", "models", "agent_config"):
            assert key in config, f"Missing required key: {key}"

    def test_date_range_keys(self):
        default_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "configs",
            "default_config.json",
        )
        config = self.load_config(default_path)
        assert "init_date" in config["date_range"]
        assert "end_date" in config["date_range"]

    def test_missing_file_exits(self):
        with pytest.raises(SystemExit):
            self.load_config("/nonexistent/path/config.json")

    def test_invalid_json_exits(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("{ invalid json }")
            tmp_path = f.name
        try:
            with pytest.raises(SystemExit):
                self.load_config(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_custom_config_roundtrip(self):
        cfg = {
            "agent_type": "BaseAgent",
            "market": "us",
            "date_range": {"init_date": "2025-01-01", "end_date": "2025-01-31"},
            "models": [
                {
                    "name": "test-model",
                    "basemodel": "openai/gpt-4",
                    "signature": "gpt-4-test",
                    "enabled": True,
                }
            ],
            "agent_config": {
                "max_steps": 10,
                "max_retries": 3,
                "base_delay": 0.5,
                "initial_cash": 10000.0,
                "verbose": False,
            },
            "log_config": {"log_path": "./data/agent_data"},
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(cfg, f)
            tmp_path = f.name
        try:
            loaded = self.load_config(tmp_path)
            assert loaded["agent_type"] == "BaseAgent"
            assert loaded["agent_config"]["max_steps"] == 10
            assert loaded["models"][0]["signature"] == "gpt-4-test"
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# get_agent_class registry
# ---------------------------------------------------------------------------

class TestGetAgentClass:
    @pytest.fixture(autouse=True)
    def _import_main(self):
        import main as m
        self.get_agent_class = m.get_agent_class
        self.AGENT_REGISTRY = m.AGENT_REGISTRY

    def test_registry_has_base_agent(self):
        assert "BaseAgent" in self.AGENT_REGISTRY

    def test_registry_has_all_expected_types(self):
        expected = [
            "BaseAgent",
            "BaseAgent_Hour",
            "BaseAgentAStock",
            "BaseAgentAStock_Hour",
            "BaseAgentCrypto",
        ]
        for agent_type in expected:
            assert agent_type in self.AGENT_REGISTRY, f"Missing agent type: {agent_type}"

    def test_unsupported_agent_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported agent type"):
            self.get_agent_class("NonExistentAgentType")
