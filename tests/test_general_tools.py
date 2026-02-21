"""
Integration tests for tools/general_tools.py

Tests cover:
- get_config_value / write_config_value round-trip
- extract_conversation with dict-based messages
- extract_tool_messages / extract_first_tool_message_content
"""

import json
import os
import tempfile
import pytest

# Ensure project root is on sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ai_message(content, finish_reason="stop"):
    return {
        "content": content,
        "response_metadata": {"finish_reason": finish_reason},
        "additional_kwargs": {},
    }


def _make_tool_message(content, tool_call_id="call_1", name="get_price"):
    return {
        "content": content,
        "tool_call_id": tool_call_id,
        "name": name,
    }


# ---------------------------------------------------------------------------
# write_config_value / get_config_value
# ---------------------------------------------------------------------------

class TestConfigRoundTrip:
    def setup_method(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self._tmp.close()
        os.environ["RUNTIME_ENV_PATH"] = self._tmp.name
        # Remove stale cache so the module re-reads our env var
        import tools.general_tools as gt
        # Reload to pick up updated env var
        import importlib
        importlib.reload(gt)
        self.gt = gt

    def teardown_method(self):
        os.unlink(self._tmp.name)
        os.environ.pop("RUNTIME_ENV_PATH", None)

    def test_write_and_read_string(self):
        self.gt.write_config_value("SIGNATURE", "test-sig")
        assert self.gt.get_config_value("SIGNATURE") == "test-sig"

    def test_write_and_read_bool(self):
        self.gt.write_config_value("IF_TRADE", False)
        assert self.gt.get_config_value("IF_TRADE") is False

    def test_write_and_read_multiple_keys(self):
        self.gt.write_config_value("MARKET", "us")
        self.gt.write_config_value("LOG_PATH", "./data/agent_data")
        assert self.gt.get_config_value("MARKET") == "us"
        assert self.gt.get_config_value("LOG_PATH") == "./data/agent_data"

    def test_get_missing_key_returns_default(self):
        result = self.gt.get_config_value("NONEXISTENT_KEY", "default_val")
        assert result == "default_val"

    def test_file_persists_json(self):
        self.gt.write_config_value("FOO", "bar")
        with open(self._tmp.name) as f:
            data = json.load(f)
        assert data["FOO"] == "bar"


# ---------------------------------------------------------------------------
# extract_conversation
# ---------------------------------------------------------------------------

class TestExtractConversation:
    def setup_method(self):
        import tools.general_tools as gt
        self.gt = gt

    def test_final_returns_last_stop_message(self):
        conversation = {
            "messages": [
                _make_ai_message("first answer"),
                _make_ai_message("second answer"),
            ]
        }
        result = self.gt.extract_conversation(conversation, "final")
        assert result == "second answer"

    def test_final_skips_empty_content(self):
        conversation = {
            "messages": [
                _make_ai_message("good answer"),
                _make_ai_message(""),
            ]
        }
        result = self.gt.extract_conversation(conversation, "final")
        assert result == "good answer"

    def test_final_skips_tool_calls(self):
        conversation = {
            "messages": [
                _make_ai_message("final answer", finish_reason="stop"),
                {
                    "content": "",
                    "additional_kwargs": {"tool_calls": [{"id": "1", "function": {"name": "t"}}]},
                    "response_metadata": {"finish_reason": "tool_calls"},
                },
            ]
        }
        result = self.gt.extract_conversation(conversation, "final")
        assert result == "final answer"

    def test_all_returns_full_list(self):
        messages = [_make_ai_message("a"), _make_ai_message("b")]
        conversation = {"messages": messages}
        result = self.gt.extract_conversation(conversation, "all")
        assert result is messages

    def test_invalid_output_type_raises(self):
        with pytest.raises(ValueError):
            self.gt.extract_conversation({"messages": []}, "bad_type")

    def test_empty_conversation_final_returns_none(self):
        result = self.gt.extract_conversation({"messages": []}, "final")
        assert result is None


# ---------------------------------------------------------------------------
# extract_tool_messages / extract_first_tool_message_content
# ---------------------------------------------------------------------------

class TestExtractToolMessages:
    def setup_method(self):
        import tools.general_tools as gt
        self.gt = gt

    def test_extracts_tool_messages(self):
        conversation = {
            "messages": [
                _make_ai_message("thinking"),
                _make_tool_message("price data", tool_call_id="call_1"),
                _make_ai_message("final answer"),
            ]
        }
        tool_msgs = self.gt.extract_tool_messages(conversation)
        assert len(tool_msgs) == 1
        assert tool_msgs[0]["content"] == "price data"

    def test_no_tool_messages_returns_empty(self):
        conversation = {"messages": [_make_ai_message("answer")]}
        tool_msgs = self.gt.extract_tool_messages(conversation)
        assert tool_msgs == []

    def test_first_tool_message_content(self):
        conversation = {
            "messages": [
                _make_tool_message("first tool result", tool_call_id="call_1"),
                _make_tool_message("second tool result", tool_call_id="call_2"),
            ]
        }
        content = self.gt.extract_first_tool_message_content(conversation)
        assert content == "first tool result"

    def test_first_tool_message_content_none_when_absent(self):
        conversation = {"messages": [_make_ai_message("only AI")]}
        content = self.gt.extract_first_tool_message_content(conversation)
        assert content is None
