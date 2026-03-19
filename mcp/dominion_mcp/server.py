"""Dominion MCP server — tool registration and server setup."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dominion")

# Tool modules are imported here to register their tools on the server.
# v0.3.0: 11 tools across 4 modules (setup, submit, progress, knowledge)
# Modules will be imported as they are implemented.
