"""Custom tools — the agent's "hands". Add your own @tool functions here.

Each function decorated with ``@tool`` is exposed to the model as a tool; the
function's docstring is the description the model sees, so state clearly what it
does and what its arguments are.
"""

from __future__ import annotations

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Return the current local date and time as an ISO-8601 string."""
    return datetime.now().isoformat(timespec="seconds")


# A small built-in "company database" standing in for a real fundamentals API
# (demo data, runs offline).
_COMPANY_DB = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "pe": 31.2},
    "TSLA": {"name": "Tesla, Inc.", "sector": "Automotive", "pe": 58.7},
    "BABA": {"name": "Alibaba Group", "sector": "E-commerce", "pe": 14.5},
    "600519": {"name": "Kweichow Moutai", "sector": "Spirits", "pe": 28.9},
}


@tool
def get_company_overview(ticker: str) -> str:
    """Look up a quick fundamentals overview for a stock ticker (demo data).

    Args:
        ticker: Stock symbol, e.g. 'AAPL' or '600519'.
    """
    info = _COMPANY_DB.get(ticker.upper()) or _COMPANY_DB.get(ticker)
    if not info:
        return f"No data for '{ticker}'. Known tickers: {', '.join(_COMPANY_DB)}."
    return (
        f"{info['name']} ({ticker}) — sector: {info['sector']}, "
        f"trailing P/E: {info['pe']}."
    )


# Custom tools the main agent can use directly.
TOOLS = [get_current_time, get_company_overview]
