"""Dominion MCP server — tool registration and server setup."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dominion")

# Tool modules are imported here to register their tools on the server.
from .tools import agent_lifecycle  # noqa: F401
from .tools import pipeline_tools  # noqa: F401
from .tools import data_read  # noqa: F401
from .tools import data_write  # noqa: F401
