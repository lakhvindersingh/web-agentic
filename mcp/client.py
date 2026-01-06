"""MCP client for connecting to MCP servers."""
from typing import List, Optional
from langchain_core.tools import BaseTool, StructuredTool
import asyncio

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the MCP server (for HTTP-based servers)
        """
        self.server_url = server_url or "http://localhost:8000"
        self.session: Optional[ClientSession] = None
        self._connected = False
    
    async def connect(self):
        """Connect to the MCP server."""
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not available. Install with: pip install mcp"
            )
        
        if self._connected:
            return
        
        # For HTTP-based MCP servers
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/health")
                if response.status_code == 200:
                    self._connected = True
        except Exception as e:
            print(f"Warning: Could not connect to MCP server at {self.server_url}: {e}")
            self._connected = False
    
    async def get_tools(self) -> List[dict]:
        """
        Get available tools from MCP server.
        
        Returns:
            List of tool definitions from MCP server
        """
        if not self._connected:
            await self.connect()
        
        if not self._connected:
            return []
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/tools")
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"Warning: Could not fetch tools from MCP server: {e}")
        
        return []
    
    async def close(self):
        """Close the MCP connection."""
        self._connected = False
        self.session = None


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def _get_mcp_client() -> Optional[MCPClient]:
    """Get or create MCP client instance."""
    global _mcp_client
    
    if not MCP_AVAILABLE:
        return None
    
    from config import Config
    
    if not Config.MCP_ENABLED:
        return None
    
    if _mcp_client is None:
        _mcp_client = MCPClient(Config.MCP_SERVER_URL)
    
    return _mcp_client


def get_mcp_tools() -> List[BaseTool]:
    """
    Get tools from MCP server and convert to LangChain tools.
    
    Returns:
        List of LangChain tools from MCP server
    """
    if not MCP_AVAILABLE:
        return []
    
    client = _get_mcp_client()
    if not client:
        return []
    
    try:
        # Run async function in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a new one
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, client.get_tools())
                tool_defs = future.result(timeout=5)
        else:
            tool_defs = loop.run_until_complete(client.get_tools())
    except Exception as e:
        print(f"Warning: Error fetching MCP tools: {e}")
        return []
    
    # Convert MCP tool definitions to LangChain tools
    tools = []
    for tool_def in tool_defs:
        try:
            # Create a StructuredTool from MCP tool definition
            def tool_func(**kwargs):
                # This would actually call the MCP server to execute the tool
                return f"MCP tool {tool_def.get('name', 'unknown')} called with {kwargs}"
            
            langchain_tool = StructuredTool.from_function(
                func=tool_func,
                name=tool_def.get("name", "mcp_tool"),
                description=tool_def.get("description", ""),
                args_schema=None,  # Could parse from tool_def schema
            )
            tools.append(langchain_tool)
        except Exception as e:
            print(f"Warning: Could not convert MCP tool {tool_def.get('name')}: {e}")
    
    return tools

