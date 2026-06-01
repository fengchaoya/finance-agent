---
name: market-briefing
description: Produce a "single-stock snapshot" briefing. Use when the user asks for a quick fundamentals + quote overview of one or more stocks, or asks for a "briefing/snapshot".
---

# Single-Stock Briefing (Market Briefing)

## When to use
- The user says: "show me AAPL", "give me a Moutai snapshot", "compare AAPL and TSLA"
- You need to roll up "fundamentals + current (simulated) quote" into one structured briefing

## Steps
1. Use `get_company_overview` to fetch each stock's fundamentals (name, sector, P/E).
2. Use the MCP tool `get_stock_price` to fetch each stock's current (simulated) price and
   change; if you are unsure which symbols exist, call `list_symbols` first.
3. Use `get_current_time` to get the date, then assemble a Markdown briefing:

   ```
   ## Single-Stock Snapshot ({date})
   - **{name} ({symbol})** | sector: {sector} | P/E: {pe}
     - Price: {price} {currency} ({change_pct}%)
     - One-line take: ...
   ```
4. If the user asks to save it, use `write_file` to write `/briefings/{symbol}-{date}.md`.

## Notes
- Quotes are "simulated" data — always note "(simulated data, for learning only)" in the briefing.
- Do not invent financial metrics that were not provided; if missing, write "N/A".
