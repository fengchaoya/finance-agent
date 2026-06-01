"""MCP configuration — register MCP servers and load their tools.

Mirrors the course design: flip a server on/off here, and the tools it exposes
are wired into the agent automatically.
"""

from __future__ import annotations

import logging
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

# Server name -> connection config.
# The local "stock" server is launched as a stdio subprocess using the current
# Python interpreter (the uv virtualenv), so no extra install is needed. Remove
# or comment out an entry to "turn it off".
MCP_SERVERS: dict[str, dict] = {
    "stock": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "cufel_deepagent.mcp.servers.stock_server"],
    },
    # Advanced example: connect an MCP exposed over HTTP (e.g. World Bank macro
    # data); enable as needed:
    # "worldbank": {
    #     "transport": "streamable_http",
    #     "url": "http://localhost:8000/mcp",
    # },
}


async def load_mcp_tools() -> list:
    """Load tools from all configured MCP servers (async).

    On failure, log a warning and return an empty list so the agent still starts
    when an MCP server is unavailable.
    """
    if not MCP_SERVERS:
        return []
    try:
        client = MultiServerMCPClient(MCP_SERVERS)
        return await client.get_tools()
    except Exception as exc:  # noqa: BLE001 - tolerate MCP being unavailable
        logger.warning("Failed to load MCP tools: %s", exc)
        return []
