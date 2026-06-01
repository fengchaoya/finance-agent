"""Assemble the DeepAgent: model + tools + skills + subagents + filesystem backend + MCP.

This is where the course's "five core capabilities" come together:

- Planning: deepagents' built-in ``write_todos`` tool (auto-loaded, no config)
- Filesystem / memory carrier: ``FilesystemBackend``, virtual root anchored to this project
- Skills: each subdirectory of ``skills/`` that contains a ``SKILL.md``
- SubAgents: delegated through the built-in ``task`` tool
- External services (MCP): tools exposed by the servers configured in ``mcp.py``
"""

from __future__ import annotations

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from cufel_deepagent.config import PROJECT_ROOT, get_model
from cufel_deepagent.mcp.mcp import load_mcp_tools
from cufel_deepagent.tools.tools import TOOLS

# Default response language for the agent. Override per run with the CLI's
# --lang flag or the AGENT_LANG env var.
DEFAULT_LANG = "en"

# Maps a language setting to the response-language instruction injected into the
# system prompt. "auto" mirrors whatever language the user writes in.
LANG_DIRECTIVES = {
    "en": "Always respond in English.",
    "zh": "Always respond in Chinese (中文).",
    "auto": "Respond in the same language the user writes in.",
}

SYSTEM_PROMPT_TEMPLATE = """You are a financial-analysis DeepAgent, intended for learning and research.

You can:
- call tools (current time, company fundamentals, simulated quotes, ...) to gather data;
- for structured tasks, read the relevant Skill first, then follow its steps;
- write intermediate artifacts or final reports to files with write_file (your file
  root is this project's directory);
- delegate complex, self-contained subtasks to a subagent via the task tool.

{language_directive} Be concise and accurate: lead with the conclusion, then the
supporting evidence. Do not fabricate data.
"""


def build_system_prompt(lang: str = DEFAULT_LANG) -> str:
    """Render the system prompt for the given response language ('en'|'zh'|'auto')."""
    directive = LANG_DIRECTIVES.get(lang, LANG_DIRECTIVES[DEFAULT_LANG])
    return SYSTEM_PROMPT_TEMPLATE.format(language_directive=directive)


def _build_subagents(model):
    """Example subagent: a data analyst (demonstrates the SubAgent capability)."""
    return [
        {
            "name": "data-analyst",
            "description": (
                "Data-analysis subagent: gathers data with the available tools and "
                "compares/summarizes it. Delegate to it when several lookups need to "
                "be rolled up into a single conclusion."
            ),
            "system_prompt": (
                "You are a data-analysis assistant. Gather data with the available "
                "tools, do the necessary comparisons and calculations, and return a "
                "single clear conclusion (including the key numbers)."
            ),
            "model": model,
            "tools": list(TOOLS),
        }
    ]


async def build_agent(
    *,
    with_mcp: bool = True,
    require_key: bool = True,
    lang: str = DEFAULT_LANG,
):
    """Build and return the compiled DeepAgent graph.

    Args:
        with_mcp: Whether to load the MCP tools configured in mcp.py.
        require_key: Whether to raise when ``QWEN_API`` is missing (``--check`` passes False).
        lang: Response language — ``"en"`` (default), ``"zh"``, or ``"auto"``.
    """
    model = get_model(require_key=require_key)

    # Anchor the agent's "virtual filesystem" to the project root: read_file/
    # write_file/skills all resolve relative to it — so skills/ is readable while
    # reads and writes stay confined to the project directory.
    backend = FilesystemBackend(root_dir=str(PROJECT_ROOT), virtual_mode=True)

    tools = list(TOOLS)
    if with_mcp:
        tools += await load_mcp_tools()

    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=build_system_prompt(lang),
        skills=["skills"],  # load skills from <project>/skills/*/SKILL.md (progressive disclosure)
        subagents=_build_subagents(model),
        backend=backend,
    )
