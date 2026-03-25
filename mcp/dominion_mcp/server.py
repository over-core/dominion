"""Dominion MCP server — tool registration and server setup."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dominion")

# Tool modules are imported here to register their tools on the server.
# v0.5.0: 20 tools across 6 modules (3 setup + 2 submit + 6 progress + 1 knowledge + 4 monitoring + 4 objective)
from .tools import setup  # noqa: F401  (start_phase, prepare_step, prepare_task)
from .tools import submit  # noqa: F401  (submit_work, signal_blocker)
from .tools import progress  # noqa: F401  (get_progress, quality_gate, assess_complexity, advance_step, save_decision)
from .tools import knowledge  # noqa: F401  (save_knowledge)
from .tools import monitoring  # noqa: F401  (get_feed, register_agent, check_agent_health, check_pipeline_ready)
from .tools import objective  # noqa: F401  (create_objective, link_phase_to_objective, get_objective, complete_objective)
