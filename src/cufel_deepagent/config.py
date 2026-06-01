"""Central configuration: environment variables, paths, and the LLM factory.

Switch the model in one place — just edit ``.env`` (mirroring the course
framework's design, where ``.env`` drives which Qwen model is used).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Project root: this file is src/cufel_deepagent/config.py, so go up three levels.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = PROJECT_ROOT / "skills"
MEMORIES_DIR = PROJECT_ROOT / "memories"

# Load .env from the project root (if present).
load_dotenv(PROJECT_ROOT / ".env")

QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
QWEN_API = os.getenv("QWEN_API")
QWEN_URL = os.getenv("QWEN_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")

# Default response language for the agent: "en" | "zh" | "auto" (None if unset).
# The CLI's --lang flag takes precedence over this.
AGENT_LANG = os.getenv("AGENT_LANG")

_PLACEHOLDER_KEY = "sk-placeholder-not-used"


def get_model(
    model: str | None = None,
    temperature: float = 0.0,
    *,
    require_key: bool = True,
) -> ChatOpenAI:
    """Build the chat model: Qwen via DashScope's OpenAI-compatible endpoint.

    Args:
        model: Override the default model name (defaults to ``QWEN_MODEL`` from .env).
        temperature: Sampling temperature.
        require_key: When True, raise if ``QWEN_API`` is missing. ``--check`` passes
            False so the wiring can be validated offline, without a key.
    """
    api_key = QWEN_API
    if not api_key:
        if require_key:
            raise RuntimeError(
                "QWEN_API is not set. Copy .env.example to .env and fill in your "
                "DashScope API key (QWEN_API=...)."
            )
        api_key = _PLACEHOLDER_KEY
    return ChatOpenAI(
        model=model or QWEN_MODEL,
        api_key=api_key,
        base_url=QWEN_URL,
        temperature=temperature,
    )
