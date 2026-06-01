# DeepAgent — 具备规划、技能、子智能体与 MCP 工具的自主智能体

[English](README.md) · **中文**

一个构建在 LangChain [`deepagents`](https://github.com/langchain-ai/deepagents) 与
LangGraph 之上的自主 **deep agent**。它能规划多步任务、在受限工作区内读写文件、
按需加载可复用的**技能(Skill)**、把子任务委派给专门的**子智能体(SubAgent)**，并通过
**MCP（Model Context Protocol）** 调用外部工具。项目自带一个轻量的金融主题——公司
信息查询、一个模拟行情的 MCP 服务器，以及一个"个股简报"技能——把各个能力端到端地
串起来，命令行还带有可持久化的对话记忆。

> 设计上与模型无关：任何 OpenAI 兼容端点都可接入。当前接的是阿里 **Qwen**
> （通过 DashScope）。

## 它展示了什么
- **基于 LangGraph 的智能体架构** —— 规划 / 工具调用循环，借助 `deepagents` harness 实现自动上下文摘要与递归控制。
- **渐进式披露的技能** —— 把 `SKILL.md` 放进 `skills/`，平时只暴露名称与简介，任务匹配时才按需读取完整指令。
- **子智能体委派** —— 内置 `task` 工具，为独立、上下文较重的子任务派生隔离的子智能体。
- **MCP 工具集成** —— 工具由独立进程经 stdio 提供，用 `langchain-mcp-adapters` 动态加载。
- **受限文件系统** —— 智能体的文件工具通过虚拟文件系统操作，限定在项目目录内。
- **持久化记忆** —— 对话序列化为 JSON，跨会话自动载入。
- **双语输出** —— `--lang en | zh | auto`。

## 架构

| 能力 | 实现 |
| --- | --- |
| 规划 | 内置 `write_todos` 待办循环 |
| 文件系统 / 记忆 | `FilesystemBackend(virtual_mode=True)`，根目录锚定到项目 |
| 技能 | `skills/<名字>/SKILL.md`（YAML frontmatter） |
| 子智能体 | `subagents=[...]`，经 `task` 工具委派 |
| 外部工具(MCP) | `mcp/mcp.py` 中注册的服务器 |
| 自定义工具 | `tools/tools.py` 里的 `@tool` 函数 |

```
deep-agent/
├── main.py                       # 命令行入口
├── pyproject.toml                # 依赖（uv 管理）
├── .env.example                  # 配置模板 → 复制成 .env
├── skills/
│   └── market-briefing/SKILL.md  # 示例技能：个股简报
├── memories/                     # 对话历史（带 -c 时写入；已 gitignore）
└── src/cufel_deepagent/
    ├── config.py                 # 环境变量 + 模型工厂（一处切换模型）
    ├── agent.py                  # 组装 模型 + 工具 + 技能 + 子智能体 + 后端 + MCP
    ├── cli.py                    # 命令行逻辑
    ├── tools/tools.py            # 自定义工具
    └── mcp/
        ├── mcp.py                # MCP 服务器注册表
        └── servers/stock_server.py  # 本地模拟行情 MCP 服务器
```

## 技术栈
LangGraph · langchain-deepagents · langchain-mcp-adapters · MCP · 阿里 Qwen（DashScope，OpenAI 兼容） · uv · Python 3.12

## 快速开始

```bash
uv sync                       # 安装依赖（按 uv.lock 还原）
cp .env.example .env          # 然后在 .env 里填 QWEN_API
uv run main.py --check        # 离线自检：工具 / MCP / 技能 / 装配
uv run main.py --run "给我出一份 AAPL 和 TSLA 的个股简报" --lang zh
uv run main.py -i -c demo     # 交互模式，带对话记忆
```

### 回答语言
默认英文。用 `--lang` 按次切换，或在 `.env` 里设 `AGENT_LANG`：

| 参数 | 效果 |
| --- | --- |
| `--lang en` | 英文（默认） |
| `--lang zh` | 中文 |
| `--lang auto` | 跟随用户使用的语言 |

## 它是怎么跑起来的
1. `config.get_model()` 构建一个指向 OpenAI 兼容端点（DashScope / Qwen）的 `ChatOpenAI` 客户端。
2. `agent.build_agent()` 把模型、工具、`skills/`、子智能体、MCP 工具和 `FilesystemBackend` 交给 `create_deep_agent()`，编译成一张 LangGraph 图。
3. `cli.py` 把每一轮作为 `HumanMessage` 传给 `agent.ainvoke()`；带 `-c` 时，完整消息历史会序列化到 `memories/<名字>.json` 并在下次运行时载入。

## 如何扩展
- **加工具** —— 在 `tools/tools.py` 写一个 `@tool` 函数并加入 `TOOLS`。
- **加技能** —— 新建 `skills/<名字>/SKILL.md`（frontmatter 的 `name` 必须等于目录名）。
- **加 MCP 服务器** —— 在 `mcp/mcp.py` 的 `MCP_SERVERS` 里加一项（stdio 或 HTTP）。

## 说明
- **演示数据为模拟** —— 公司基本面与行情均为示意数据，并非真实市场数据。
- **安全** —— `FilesystemBackend` 以 `virtual_mode=True` 运行，将文件访问限定在项目目录内。
