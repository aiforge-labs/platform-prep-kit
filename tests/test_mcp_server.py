"""Tests for the MCP server tool registration and basic functionality."""

import pytest


class TestMCPToolRegistration:
    """Verify that all expected tools are registered on the FastMCP instance."""

    def test_mcp_instance_exists(self):
        from prep_agent.mcp_server import mcp
        assert mcp is not None
        assert mcp.name == "platform-prep-kit"

    def test_expected_tools_registered(self):
        from prep_agent.mcp_server import mcp

        # FastMCP stores tools internally; list them
        tool_names = set()
        for tool in mcp._tool_manager.list_tools():
            tool_names.add(tool.name)

        expected = {"get_today", "start_study", "take_quiz", "add_note", "get_progress", "get_fitment"}
        for name in expected:
            assert name in tool_names, f"Tool '{name}' not registered. Found: {tool_names}"

    def test_add_note_tool_works(self, tmp_path):
        """add_note should work even without a full workspace — it just needs a writable dir."""
        from prep_agent.core.knowledge import KnowledgeBase

        kb = KnowledgeBase(prep_dir=str(tmp_path))
        path = kb.add_note("Test Topic", "This is a test note.")
        assert path is not None
        assert (tmp_path / "knowledge").exists()


class TestMCPCommand:
    def test_mcp_cmd_registered(self):
        """The mcp command should be discoverable in the CLI."""
        from prep_agent.cli import prep
        commands = list(prep.commands.keys())
        assert "mcp" in commands
