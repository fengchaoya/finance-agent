# cufel-deepagent（DeepAgent 等价复刻版）

[English](README.md) · **中文**

一个学习项目：在公开的
[`langchain-ai/deepagents`](https://github.com/langchain-ai/deepagents) 框架之上，
搭建一个具备「规划、文件系统/记忆、按需技能(Skill)、可委派子智能体(SubAgent)、
MCP 外部工具」的 deep agent。

对应课程「十讲十练 · 第4讲 DeepAgent」。这是一个**独立的新项目**（不是在第3讲
BOT 基础上改的）：第3讲讲的是 FunctionCall 范式，第4讲在 DeepAgent 范式下重建，
在普通函数调用之上引入五大能力。

> 课程自带的 `cufel-deepagent` 框架没有公开下载地址，所以本仓库用公开的
> `deepagents` 做了一个**功能等价**的实现，并刻意沿用课程的
> `src/cufel_deepagent/...` 目录结构，让教程步骤可以一一对应。

## 五大能力 ↔ 代码位置

| 能力 | 实现 |
| --- | --- |
| 规划 Planning | deepagents 内置 `write_todos`（自动加载） |
| 文件系统/记忆载体 | `FilesystemBackend(virtual_mode=True)`，虚拟根目录锚定到本项目 |
| 技能 Skill | `skills/<名字>/SKILL.md`（带 YAML frontmatter） |
| 子智能体 SubAgent | `agent.py` 里的 `subagents=[...]`，经内置 `task` 工具委派 |
| 外部服务 MCP | `src/cufel_deepagent/mcp/mcp.py` 配置服务器 |
| 工具 Tool | `src/cufel_deepagent/tools/tools.py` |

## 目录结构

```
deep-agent/
├── main.py                       # 入口（转发到 cufel_deepagent.cli）
├── pyproject.toml                # 依赖（uv 管理）
├── .env.example                  # 配置模板 → 复制成 .env 填 Key
├── skills/
│   └── market-briefing/SKILL.md  # 示例技能：个股速览简报
├── memories/                     # 对话历史（-c 时写到这里，已 gitignore）
└── src/cufel_deepagent/
    ├── config.py                 # 环境变量 + Qwen LLM 工厂（一处切换大模型）
    ├── agent.py                  # 组装 DeepAgent（模型+工具+技能+子智能体+后端+MCP）
    ├── cli.py                    # 命令行逻辑
    ├── tools/tools.py            # 自定义工具（Agent 的"手"）
    └── mcp/
        ├── mcp.py                # MCP 服务器配置（开关在这里）
        └── servers/stock_server.py  # 本地"模拟股市" MCP 示例
```

## 环境要求
- [uv](https://docs.astral.sh/uv/)（管理依赖与虚拟环境）
- Node.js（部分 MCP 服务器需要 `npx`；本项目自带的模拟 MCP 用纯 Python，可不依赖）
- Python 3.12（uv 会按 `.python-version` 自动准备）

## 快速开始

```bash
# 1. 安装依赖（按 uv.lock 还原环境）
uv sync

# 2. 准备配置：复制模板并填入你的 DashScope Key
cp .env.example .env        # 然后编辑 .env，填 QWEN_API

# 3.（可选）不联网自检：确认 工具/MCP/技能/装配 都正常
uv run main.py --check

# 4. 提问
uv run main.py --run "你有哪些能力？" --lang zh
uv run main.py --run "给我出一份 AAPL 和 600519 的个股速览" --lang zh

# 5. 交互模式（-c 会把对话记忆存到 memories/demo.json）
uv run main.py -i -c demo --lang zh
```

### 回答语言
智能体**默认用英文回答**。可用 `--lang` 覆盖，或在 `.env` 里设 `AGENT_LANG`：

```bash
uv run main.py --run "What can you do?"  --lang en     # 英文（默认）
uv run main.py --run "介绍一下你的能力"  --lang zh     # 中文
uv run main.py -i --lang auto                            # 跟随用户使用的语言
```

## 它是怎么跑起来的
1. `config.get_model()` 用 `langchain-openai` 的 `ChatOpenAI` 指向 DashScope 的
   OpenAI 兼容端点，调用 Qwen。
2. `agent.build_agent()` 把模型、工具、`skills/`、子智能体、MCP 工具和
   `FilesystemBackend` 交给 `create_deep_agent()` 组装成一张图。
3. `cli.py` 把你的问题作为 `HumanMessage` 传给 `agent.ainvoke()`；带 `-c` 时，
   完整对话会用 `messages_to_dict` 序列化到 `memories/<名字>.json`，下次自动载入。

## 跟着教程继续练
- **加工具**：在 `tools/tools.py` 写新的 `@tool` 函数，并加进 `TOOLS`。
- **加技能**：新建 `skills/<名字>/SKILL.md`（frontmatter 的 `name` 必须等于目录名）。
- **接 MCP**：在 `mcp/mcp.py` 的 `MCP_SERVERS` 里加一项（如练习题里的 World Bank 宏观 MCP）。

> 安全提示：`FilesystemBackend` 让智能体能读写文件，本项目已用 `virtual_mode=True`
> 把它限制在项目目录内；请勿把根目录设成 `/` 或你的家目录。
