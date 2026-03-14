"""Entry point for dominion-mcp binary."""

from .server import mcp


def main():
    """Start the Dominion MCP server (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
