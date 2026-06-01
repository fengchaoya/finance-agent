# cufel-deepagent (DeepAgent — equivalent reimplementation)

**English** · [中文](README.zh-CN.md)

A learning project that builds a **deep agent** — an LLM agent with planning, a
filesystem/memory, on-demand **skills**, delegatable **subagents**, and **MCP**
(Model Context Protocol) tools — on top of the public
[`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents) framework.

It corresponds to Lecture 4 ("DeepAgent") of the CUFEL course. This is a
**standalone project**, not an extension of the Lecture 3 bot: Lecture 3 covers
the FunctionCall paradigm; Lecture 4 rebuilds under the DeepAgent paradigm,
adding five capabilities on top of plain function-calling.

> The course's own `cufel-deepagent` framework isn't publicly downloadable, so
> this repo is a functionally equivalent implementation on public `deepagents`,
> deliberately structured to mirror the course's `src/cufel_deepagent/...` layout
> so the exercises map one-to-one.

## The five capabilities ↔ where they live

| Capability | Implementation |
| --- | --- |
| Planning | deepagents' built-in `write_todos` (auto-loaded) |
| Filesystem / memory carrier | `FilesystemBackend(virtual_mode=True)`, virtual root anchored to the project |
| Skill | `skills/<name>/SKILL.md` (with YAML frontmatter) |
| SubAgent | `subagents=[...]` in `agent.py`, invoked via the built-in `task` tool |
| External services (MCP) | `src/cufel_deepagent/mcp/mcp.py` |
| Tool | `src/cufel_deepagent/tools/tools.py` |

## Project layout

```
deep-agent/
├── main.py                       # entry point (forwards to cufel_deepagent.cli)
├── pyproject.toml                # dependencies (managed by uv)
├── .env.example                  # config template → copy to .env and fill your key
├── skills/
│   └── market-briefing/SKILL.md  # example skill: single-stock briefing
├── memories/                     # conversation history (written with -c; gitignored)
└── src/cufel_deepagent/
    ├── config.py                 # env vars + Qwen LLM factory (swap models in one place)
    ├── agent.py                  # assembles the DeepAgent (model+tools+skills+subagents+backend+MCP)
    ├── cli.py                    # command-line logic
    ├── tools/tools.py            # custom tools (the agent's "hands")
    └── mcp/
        ├── mcp.py                # MCP server config (toggle servers here)
        └── servers/stock_server.py  # local "simulated stock market" MCP example
```

## Requirements
- [uv](https://docs.astral.sh/uv/) (dependency & virtualenv manager)
- Node.js (some MCP servers need `npx`; the bundled simulated MCP is pure Python, so it's optional)
- Python 3.12 (uv provisions it automatically from `.python-version`)

## Quickstart

```bash
# 1. Install dependencies (restores the environment from uv.lock)
uv sync

# 2. Configure: copy the template and fill in your DashScope key
cp .env.example .env        # then edit .env and set QWEN_API

# 3. (optional) Offline self-check: verifies tools / MCP / skills / assembly
uv run main.py --check

# 4. Ask
uv run main.py --run "What can you do?"
uv run main.py --run "Give me a single-stock snapshot of AAPL and 600519"

# 5. Interactive mode (-c persists the conversation to memories/demo.json)
uv run main.py -i -c demo
```

### Response language
The agent replies in **English** by default. Override per run with `--lang`, or set
`AGENT_LANG` in `.env`:

```bash
uv run main.py --run "What can you do?"      --lang en    # English (default)
uv run main.py --run "Summarize your tools"  --lang zh    # force a Chinese reply
uv run main.py -i --lang auto                             # mirror the user's language
```

## How it works
1. `config.get_model()` uses `langchain-openai`'s `ChatOpenAI`, pointed at
   DashScope's OpenAI-compatible endpoint, to call Qwen.
2. `agent.build_agent()` hands the model, tools, `skills/`, subagents, MCP tools,
   and a `FilesystemBackend` to `create_deep_agent()`, which compiles a graph.
3. `cli.py` sends your question as a `HumanMessage` to `agent.ainvoke()`; with
   `-c`, the full conversation is serialized to `memories/<name>.json` via
   `messages_to_dict` and reloaded next time.

## Continuing the course
- **Add a tool**: write a new `@tool` function in `tools/tools.py` and add it to `TOOLS`.
- **Add a skill**: create `skills/<name>/SKILL.md` (frontmatter `name` must equal the directory name).
- **Add an MCP server**: add an entry to `MCP_SERVERS` in `mcp/mcp.py` (e.g. the World Bank macro MCP from the exercises).

> Security note: `FilesystemBackend` lets the agent read and write files; this
> project uses `virtual_mode=True` to confine it to the project directory. Don't
> set the root to `/` or your home directory.
