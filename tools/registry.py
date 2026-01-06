"""Tool registry for managing all available tools."""
from typing import List
from langchain_core.tools import BaseTool

from tools.builtin import get_builtin_tools
from config import Config


def get_all_tools() -> List[BaseTool]:
    """
    Get all available tools (built-in + MCP tools if enabled).
    
    Returns:
        List of all available tools
    """
    tools = []
    
    # Add built-in tools
    tools.extend(get_builtin_tools())
    
    # Add MCP tools if enabled
    if Config.MCP_ENABLED:
        try:
            from mcp.client import get_mcp_tools
            mcp_tools = get_mcp_tools()
            tools.extend(mcp_tools)
        except Exception as e:
            # Log error but don't fail - continue with built-in tools only
            print(f"Warning: Could not load MCP tools: {e}")
    
    return tools

