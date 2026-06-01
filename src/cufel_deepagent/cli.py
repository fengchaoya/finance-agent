"""Command-line entry point: one-shot ask / interactive mode / conversation memory / self-check.

Usage (same style as the course):

    uv run main.py --run "What can you do?"   # one-shot
    uv run main.py -i                          # interactive
    uv run main.py -i -c demo                  # interactive + save chat to memories/demo.json
    uv run main.py --run "Introduce yourself" --lang zh   # force a Chinese reply
    uv run main.py --check                     # self-check: offline, no key, verifies wiring
"""

from __future__ import annotations

import argparse
import asyncio
import json

from langchain_core.messages import (
    HumanMessage,
    messages_from_dict,
    messages_to_dict,
)

from cufel_deepagent.agent import DEFAULT_LANG, build_agent
from cufel_deepagent.config import AGENT_LANG, MEMORIES_DIR, QWEN_MODEL


def _resolve_lang(args) -> str:
    """Response language precedence: --lang flag > AGENT_LANG env > default ('en')."""
    return args.lang or AGENT_LANG or DEFAULT_LANG


def _conv_path(name: str):
    return MEMORIES_DIR / f"{name}.json"


def load_history(name: str | None):
    """Load prior messages from memories/NAME.json (empty list if absent)."""
    if not name:
        return []
    path = _conv_path(name)
    if path.exists():
        return messages_from_dict(json.loads(path.read_text(encoding="utf-8")))
    return []


def save_history(name: str | None, messages) -> None:
    """Serialize the full conversation back to memories/NAME.json."""
    if not name:
        return
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    _conv_path(name).write_text(
        json.dumps(messages_to_dict(messages), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def message_text(msg) -> str:
    """Robustly extract a message's text content (works across langchain versions)."""
    text = getattr(msg, "text", None)
    if callable(text):
        text = text()
    if text:
        return text
    content = getattr(msg, "content", "")
    if isinstance(content, list):
        parts = []
        for part in content:
            parts.append(part.get("text", "") if isinstance(part, dict) else str(part))
        return "".join(parts)
    return content or ""


async def _ask(agent, history, user_input: str):
    """Append a user message, invoke the agent, and return the updated message list."""
    messages = list(history) + [HumanMessage(user_input)]
    result = await agent.ainvoke({"messages": messages})
    return result["messages"]


async def _run_once(args) -> None:
    agent = await build_agent(with_mcp=not args.no_mcp, lang=_resolve_lang(args))
    history = load_history(args.conversation)
    messages = await _ask(agent, history, args.run)
    print(message_text(messages[-1]))
    save_history(args.conversation, messages)


async def _interactive(args) -> None:
    lang = _resolve_lang(args)
    agent = await build_agent(with_mcp=not args.no_mcp, lang=lang)
    history = load_history(args.conversation)
    print(f"DeepAgent interactive mode (model: {QWEN_MODEL}, lang: {lang}). Type exit/quit to leave.")
    if args.conversation:
        print(
            f"Conversation memory: memories/{args.conversation}.json "
            f"(loaded {len(history)} prior messages)"
        )
    while True:
        try:
            user_input = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", ":q"}:
            break
        history = await _ask(agent, history, user_input)
        print(f"\nassistant > {message_text(history[-1])}")
        save_history(args.conversation, history)


async def _check(args) -> None:
    """Assembly self-check: needs no real API key and makes no LLM call."""
    from cufel_deepagent.config import SKILLS_DIR
    from cufel_deepagent.mcp.mcp import load_mcp_tools
    from cufel_deepagent.tools.tools import TOOLS

    print("Custom tools:", [t.name for t in TOOLS])
    mcp_tools = await load_mcp_tools()
    print(f"MCP tools ({len(mcp_tools)}):", [t.name for t in mcp_tools])
    skills = sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))
    print("Skills:", skills or "(none)")
    await build_agent(with_mcp=False, require_key=False)
    print("✅ Assembly check passed: create_deep_agent returned successfully.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cufel-deepagent",
        description="Cufel DeepAgent (equivalent reimplementation on langchain deepagents)",
    )
    parser.add_argument("-r", "--run", metavar="TEXT", help="ask once, then exit")
    parser.add_argument("-i", "--interactive", action="store_true", help="enter interactive mode")
    parser.add_argument(
        "-c", "--conversation", metavar="NAME",
        help="conversation name: read/write history at memories/NAME.json",
    )
    parser.add_argument(
        "--lang", choices=["en", "zh", "auto"], default=None,
        help="response language: en (default) | zh | auto (mirror the user). "
        "Overrides AGENT_LANG from .env.",
    )
    parser.add_argument("--no-mcp", action="store_true", help="do not load MCP tools this run")
    parser.add_argument("--check", action="store_true", help="assembly self-check (offline, no key)")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.check:
        asyncio.run(_check(args))
    elif args.run:
        asyncio.run(_run_once(args))
    elif args.interactive:
        asyncio.run(_interactive(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
