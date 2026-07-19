# AgentEvals：Agent 可靠性回归评估工具

本项目用于评估大语言模型 Agent 在版本更新、提示词调整、工具变更和工作流重构前后的可靠性变化。仓库在上游 AgentEvals 的轨迹评估能力之上，增加了成对版本回归分析、应用轨迹适配器、命令行报告与可配置质量门禁，适合作为 Agent 工程测试和作品集项目。

## 主要能力

- 对 Agent 的工具调用轨迹进行严格、子集、超集和无序匹配。
- 使用 LLM 作为裁判评估复杂轨迹。
- 比较基线版本与候选版本，识别退化、改善和不稳定样本。
- 从 OpenAI Agents、LangGraph 等运行记录中提取统一轨迹。
- 生成 JSON 和 Markdown 回归报告。
- 通过阈值配置决定 CI 是否通过，阻止明显退化的版本合并。
- 同时提供 Python 与 TypeScript 实现。

## 项目结构

```text
agent-reliability-eval/
├─ python/                 # Python 包、测试与回归分析命令行工具
├─ js/                     # TypeScript 包、测试与构建配置
├─ examples/               # 可直接运行的示例
├─ scripts/                # 演示和辅助脚本
├─ static/                 # 文档静态资源
├─ .github/workflows/      # 构建、离线测试和发布流程
├─ PORTFOLIO_EXTENSION.md  # 本仓库新增功能说明
├─ FORK_NOTES.md           # 上游来源与修改记录
└─ LICENSE                 # MIT 许可证
```

## Python 快速开始

建议使用 Python 3.10 或 3.11。在仓库根目录打开 PowerShell：

```powershell
cd python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest -q
```

运行回归分析命令：

```powershell
agent-regression --help
```

Python 包的接口和更多示例见 [`python/README.md`](python/README.md)。

## TypeScript 快速开始

需要 Node.js 22。项目使用 Corepack 管理 Yarn 3.5.1：

```powershell
cd js
corepack enable
corepack prepare yarn@3.5.1 --activate
yarn install --immutable
yarn build
yarn test
```

TypeScript 包的详细接口见 [`js/README.md`](js/README.md)。

## 回归分析示例

一个典型流程包括：

1. 准备同一批评测样本的基线版本和候选版本运行记录。
2. 使用适配器将记录转换为统一轨迹格式。
3. 运行成对比较，统计退化率、改善率和失败样本。
4. 生成 Markdown 或 JSON 报告。
5. 根据允许退化率等阈值决定质量门禁是否通过。

仓库中的 [`examples`](examples) 提供了可执行样例；新增扩展的设计和范围见 [`PORTFOLIO_EXTENSION.md`](PORTFOLIO_EXTENSION.md)。

## 自动化测试

GitHub Actions 默认运行不依赖外部服务的 Python 与 JavaScript 测试。需要真实 OpenAI 或 LangSmith 凭据的在线测试不会在普通推送中执行，避免公开仓库因为缺少 Secrets 而失败。

如需运行在线测试，请先在仓库 Secrets 中配置：

- `OPENAI_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_ENDPOINT`（可选）

然后在 GitHub Actions 页面手动运行 `Integration Tests CI`，勾选 `run-online-tests`。

## 安全说明

- 不要把 API Key 写入源码、测试或 README。
- 本地环境变量文件应保持在 `.gitignore` 中。
- 公开测试默认使用离线用例；只有手动触发时才调用外部模型。

## 上游归属与许可证

本仓库基于 LangChain 团队维护的 AgentEvals 项目进行扩展。上游来源、固定提交和本仓库新增范围记录在 [`FORK_NOTES.md`](FORK_NOTES.md) 与 [`PORTFOLIO_EXTENSION.md`](PORTFOLIO_EXTENSION.md) 中。

项目遵循 [MIT License](LICENSE)。保留原作者的版权和许可证声明，不代表本仓库作者独立创作了全部上游代码。
