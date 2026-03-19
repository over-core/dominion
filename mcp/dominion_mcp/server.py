"""Dominion MCP server — tool registration and server setup."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dominion")

# Tool modules are imported here to register their tools on the server.
# v0.3.0: 11 tools across 4 modules (3 setup + 2 submit + 5 progress + 1 knowledge)
from .tools import setup  # noqa: F401  (start_phase, prepare_step, prepare_task)
from .tools import submit  # noqa: F401  (submit_work, signal_blocker)
from .tools import progress  # noqa: F401  (get_progress, quality_gate, assess_complexity, advance_step, save_decision)
from .tools import knowledge  # noqa: F401  (save_knowledge)
