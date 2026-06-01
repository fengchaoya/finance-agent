"""A minimal simulated stock-market MCP server (stdio transport).

Corresponds to the course's "MCP advanced: simulated stock-market MCP example".
Run standalone for debugging:

    uv run python -m cufel_deepagent.mcp.servers.stock_server

Normally you don't start it by hand — mcp.py launches it as a subprocess.
"""

from __future__ import annotations

import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stock-sim")

# Baseline (simulated) prices for a few symbols.
_BASE = {"AAPL": 195.0, "TSLA": 250.0, "BABA": 78.0, "NVDA": 1200.0, "600519": 1680.0}


@mcp.tool()
def get_stock_price(symbol: str) -> dict:
    """Return a simulated current price and intraday change for a stock symbol.

    Args:
        symbol: Stock symbol, e.g. 'AAPL', '600519'.
    """
    base = _BASE.get(symbol.upper()) or _BASE.get(symbol, 100.0)
    change_pct = round(random.uniform(-3.0, 3.0), 2)
    price = round(base * (1 + change_pct / 100), 2)
    return {
        "symbol": symbol.upper(),
        "price": price,
        "change_pct": change_pct,
        "currency": "CNY" if symbol.isdigit() else "USD",
        "note": "simulated data, for learning only",
    }


@mcp.tool()
def list_symbols() -> list[str]:
    """List the stock symbols this simulated market supports."""
    return list(_BASE)


if __name__ == "__main__":
    # Defaults to stdio transport, matching transport="stdio" in mcp.py.
    mcp.run()
