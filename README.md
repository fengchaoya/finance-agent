# DeepAgent — an autonomous agent with planning, skills, subagents & MCP tools

**English** · [中文](README.zh-CN.md)

An autonomous **deep agent** built on LangChain's
[`deepagents`](https://github.com/langchain-ai/deepagents) and LangGraph. It plans
multi-step tasks, reads and writes files in a sandboxed workspace, loads reusable
**skills** on demand, delegates to specialized **subagents**, and calls external
tools over **MCP** (Model Context Protocol). A lightweight finance theme — company
lookups, a simulated market-data MCP server, and a "market briefing" skill — wires
the pieces together end to end, and the CLI adds persistent conversation memory.

> Model-agnostic by design: any OpenAI-compatible endpoint works. This build is
> wired to Alibaba **Qwen** via DashScope.

## What it demonstrates
- **Agentic architecture on LangGraph** — a planning / tool-calling loop with automatic context summarization and recursion control, via the `deepagents` harness.
- **Skills with progressive disclosure** — drop a `SKILL.md` into `skills/`; the agent sees only its name and description until a task matches, then reads the full instructions on demand.
- **Subagent delegation** — a built-in `task` tool spawns isolated subagents for self-contained, context-heavy work.
- **MCP tool integration** — tools are served by a separate process over stdio and loaded dynamically with `langchain-mcp-adapters`.
- **Sandboxed filesystem** — the agent's file tools operate through a virtual filesystem confined to the project directory.
- **Persistent memory** — conversations serialize to JSON and reload across sessions.
- **Bilingual output** — `--lang en | zh | auto`.

## Architecture

| Capability | Implementation |
| --- | --- |
| Planning | built-in `write_todos` todo-list loop |
| Filesystem / memory | `FilesystemBackend(virtual_mode=True)`, rooted at the project |
| Skills | `skills/<name>/SKILL.md` (YAML frontmatter) |
| Subagents | `subagents=[...]`, invoked via the `task` tool |
| External tools (MCP) | servers registered in `mcp/mcp.py` |
| Custom tools | `@tool` functions in `tools/tools.py` |

```
deep-agent/
├── main.py                       # CLI entry point
├── pyproject.toml                # dependencies (managed by uv)
├── .env.example                  # config template → copy to .env
├── skills/
│   └── market-briefing/SKILL.md  # example skill: single-stock briefing
├── memories/                     # conversation history (with -c; gitignored)
└── src/cufel_deepagent/
    ├── config.py                 # env + model factory (swap models in one place)
    ├── agent.py                  # assembles model + tools + skills + subagents + backend + MCP
    ├── cli.py                    # command-line logic
    ├── tools/tools.py            # custom tools
    └── mcp/
        ├── mcp.py                # MCP server registry
        └── servers/stock_server.py  # local simulated market-data MCP server
```

## Tech stack
LangGraph · langchain-deepagents · langchain-mcp-adapters · MCP · Alibaba Qwen (DashScope, OpenAI-compatible) · uv · Python 3.12

## Quickstart

```bash
uv sync                       # install (restores from uv.lock)
cp .env.example .env          # then set QWEN_API in .env
uv run main.py --check        # offline self-check: tools / MCP / skills / assembly
uv run main.py --run "Give me a single-stock snapshot of AAPL and TSLA"
uv run main.py -i -c demo     # interactive, with conversation memory
```

### Response language
Defaults to English. Switch per run with `--lang`, or set `AGENT_LANG` in `.env`:

| Flag | Result |
| --- | --- |
| `--lang en` | English (default) |
| `--lang zh` | Chinese |
| `--lang auto` | mirror the user's language |

## How it works
1. `config.get_model()` builds a `ChatOpenAI` client pointed at an OpenAI-compatible endpoint (DashScope / Qwen).
2. `agent.build_agent()` passes the model, tools, `skills/`, subagents, MCP tools, and a `FilesystemBackend` to `create_deep_agent()`, which compiles a LangGraph graph.
3. `cli.py` sends each turn as a `HumanMessage` to `agent.ainvoke()`; with `-c`, the full message history is serialized to `memories/<name>.json` and reloaded next run.

## Extending it
- **Add a tool** — write a `@tool` function in `tools/tools.py` and add it to `TOOLS`.
- **Add a skill** — create `skills/<name>/SKILL.md` (frontmatter `name` must match the directory name).
- **Add an MCP server** — add an entry to `MCP_SERVERS` in `mcp/mcp.py` (stdio or HTTP).

## Notes
- **Demo data is simulated** — company fundamentals and quotes are illustrative, not real market data.
- **Security** — `FilesystemBackend` runs with `virtual_mode=True` to confine file access to the project directory.
