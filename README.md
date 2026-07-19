# AgentEvals：Agent 可靠性回归评估工具

> 本仓库基于 MIT 许可证发布的上游项目 [LangChain AgentEvals](https://github.com/langchain-ai/agentevals)，保留了原项目的 Python、TypeScript 评估器与许可证，并在其基础上增加了成对 Agent 版本回归分析、应用轨迹适配器和可配置的 CI 质量门禁。

[English README](README_EN.md) · [扩展功能说明](PORTFOLIO_EXTENSION.md) · [上游归属与版本说明](FORK_NOTES.md) · [MIT License](LICENSE)

## 项目简介

Agent 应用拥有较高的流程自主性：它可以选择工具、改变执行路径，并根据中间结果继续推理。这种能力非常强大，但也意味着一次提示词、检索策略、模型或工具修改，可能在下游造成难以观察的行为变化。

本项目提供一套面向 Agent 的评估与回归分析工具，重点关注：

- Agent 最终任务是否成功；
- Agent 实际经过了哪些中间节点或工具调用；
- 新版本与基线版本相比是否出现指标下降；
- 延迟是否显著增加；
- 是否产生新的失败，或修复了旧失败；
- CI 是否应该因为质量门禁失败而阻止发布。

## 主要能力

### 上游 AgentEvals 能力

- 严格轨迹匹配；
- 无序轨迹匹配；
- 子集轨迹匹配；
- 超集轨迹匹配；
- 基于 LLM-as-a-Judge 的轨迹评估；
- LangGraph 图轨迹评估；
- Python 和 TypeScript 两套实现。

### 本仓库增加的能力

- 按 `task_id` 对齐基线版本和候选版本的运行记录；
- 对比成功率、任意数值指标和延迟分位数；
- 计算轨迹变化率；
- 找出新失败任务和已修复任务；
- 汇总应用相关的失败类型；
- 支持可配置的 CI 质量门禁；
- 生成机器可读的 JSON 回归报告；
- 质量门禁失败时返回非零退出码；
- 提供舆情分析 Agent 运行结果适配器。

## 项目结构

```text
agent-reliability-eval/
├─ python/
│  ├─ agentevals/
│  │  ├─ trajectory/              # 通用 Agent 轨迹评估
│  │  ├─ graph_trajectory/        # LangGraph 图轨迹评估
│  │  ├─ regression.py            # 成对版本回归分析
│  │  ├─ regression_cli.py        # 回归分析命令行入口
│  │  └─ trace_adapter.py         # 应用运行记录适配器
│  └─ tests/                       # Python 测试
├─ js/
│  ├─ src/                         # TypeScript 评估器
│  └─ package.json
├─ examples/
│  ├─ opinion_agent_thresholds.json
│  └─ opinion_agent_regression_report.json
├─ .github/workflows/              # 构建和集成测试
├─ PORTFOLIO_EXTENSION.md          # 新增能力说明
├─ FORK_NOTES.md                   # 上游归属和固定版本
├─ README_EN.md                    # 完整英文说明
└─ LICENSE                         # MIT 许可证
```

## 快速开始

### 安装 Python 包

如果只需要使用已发布的上游评估器：

```bash
pip install agentevals
```

如果需要运行本仓库增加的回归分析功能，建议从源码安装：

```powershell
cd python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

也可以使用 `uv`：

```powershell
cd python
uv sync
uv sync --group dev
```

### 安装 TypeScript 包

使用已发布的包：

```bash
npm install agentevals @langchain/core
```

从本仓库安装开发依赖：

```powershell
cd js
yarn install --immutable
```

## Agent 轨迹评估

轨迹表示 Agent 在执行任务时经历的中间步骤，例如：

```text
用户问题 → 检索 → 证据过滤 → 分类 → 输出
```

严格轨迹匹配适合要求步骤和顺序完全一致的场景；无序、子集和超集匹配则适合允许某些步骤变化的场景。完整的 Python 与 TypeScript API 示例请参考 [英文说明](README_EN.md)。

## 成对版本回归分析

回归分析模块比较同一组任务在两个 Agent 版本上的运行结果：

- `baseline`：基线版本；
- `candidate`：待评估的新版本。

系统使用 `task_id` 将两个版本的同一任务配对，再计算成功率、指标、延迟与轨迹差异。

### 通用输入格式

基线和候选 JSON 可以直接是记录数组，也可以使用 `records` 包装：

```json
{
  "records": [
    {
      "task_id": "task-001",
      "success": true,
      "trajectory": ["retrieve", "filter", "classify"],
      "metrics": {
        "label_accuracy": 1.0,
        "evidence_count": 3.0
      },
      "latency_ms": 125.4,
      "failures": []
    }
  ]
}
```

每条记录包含：

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | 字符串 | 用于配对两个版本的任务 ID |
| `success` | 布尔值 | 任务是否成功 |
| `trajectory` | 字符串数组 | Agent 的执行轨迹 |
| `metrics` | 数值字典 | 需要比较的业务指标 |
| `latency_ms` | 数值 | 执行延迟，单位为毫秒 |
| `failures` | 字符串数组 | 可选的失败类型 |

### 质量门禁配置

示例阈值文件：

```json
{
  "max_success_rate_drop": 0.0,
  "max_metric_drop": {
    "label_accuracy": 0.0,
    "agent_contract_pass_rate": 0.0
  },
  "max_p95_latency_increase_ratio": 1.0,
  "max_trajectory_change_rate": 0.0
}
```

字段含义：

- `max_success_rate_drop`：允许的最大成功率下降；
- `max_metric_drop`：各数值指标允许的最大下降；
- `max_p95_latency_increase_ratio`：允许的 P95 延迟增幅；
- `max_trajectory_change_rate`：允许发生轨迹变化的任务比例。

### 运行命令

安装本仓库 Python 包后，可以运行：

```powershell
python -m agentevals.regression_cli `
  --baseline baseline.json `
  --candidate candidate.json `
  --thresholds thresholds.json `
  --output regression_report.json
```

也可以使用安装后生成的命令：

```powershell
agent-regression `
  --baseline baseline.json `
  --candidate candidate.json `
  --thresholds thresholds.json `
  --output regression_report.json
```

门禁通过时程序返回退出码 `0`；门禁失败时返回退出码 `1`，因此可以直接接入 GitHub Actions 或其他 CI 系统。

## 回归报告内容

生成的 JSON 报告包括：

- 成功配对的任务数量；
- 基线与候选版本的成功率；
- 各数值指标的平均值和变化量；
- 平均、P50、P95 和最大延迟；
- P95 延迟比率；
- 轨迹发生变化的任务；
- 新失败任务；
- 已修复任务；
- 失败类型统计；
- 门禁是否通过；
- 违反的具体质量阈值。

## 舆情分析 Agent 适配器

`python/agentevals/trace_adapter.py` 可以把舆情分析 Agent 的任务结果转换为通用回归记录，并识别：

- 工具执行失败；
- 检索证据被拒绝；
- 需要人工复核；
- Agent 契约违规；
- 具体的契约检查失败项。

适配器同时提取：

- 标签准确率；
- 证据数量；
- Agent 契约通过率；
- 运行延迟；
- 执行轨迹。

## 已验证的集成示例

仓库中的示例对比了舆情分析 Agent 的 36 组成对任务：

- 基线：字符级 TF-IDF 检索；
- 候选：TF-IDF 与 BGE-small-zh-v1.5 的倒数排名融合，并增加相关性拒绝；
- 两个版本的任务成功率均为 100%；
- 平均标签准确率保持不变；
- Agent 契约通过率保持 100%；
- 最近一次本地运行的 P95 延迟从 112.6 ms 增加到 152.0 ms，约为 1.35 倍；
- 轨迹变化任务为 0；
- 新执行失败为 0；
- 候选版本在 36 个任务中的 29 个任务上拒绝了低置信度检索证据；
- 配置的质量门禁通过。

“接受的文档更少”不能直接证明检索质量更高。本项目只记录行为变化，检索质量仍需通过单独的相关性评估判断。延迟数据来自本地运行，也会受到模型预热和机器性能影响。

## 运行测试

### Python

运行全部 Python 测试：

```powershell
cd python
uv sync
uv sync --group dev
uv run pytest tests
```

只运行本仓库增加的确定性测试：

```powershell
cd python
uv run pytest tests/test_regression.py tests/test_trace_adapter.py
```

新增测试不需要访问外部服务。上游 LLM-as-a-Judge 测试需要相应 API Key；没有配置 API Key 时，不应宣称这些测试已经通过。

### TypeScript

```powershell
cd js
yarn install --immutable
yarn test
```

## CI 集成

仓库保留 GitHub Actions 工作流，用于：

- Python 测试；
- TypeScript 测试；
- TypeScript 构建；
- 按文件变化决定需要执行的工作流；
- 手动触发集成测试。

回归 CLI 采用标准退出码，因此也可以在自定义工作流中加入：

```yaml
- name: Agent 回归质量门禁
  run: |
    python -m agentevals.regression_cli \
      --baseline baseline.json \
      --candidate candidate.json \
      --thresholds thresholds.json \
      --output regression_report.json
```

## 上游归属与许可证

- 上游项目：[langchain-ai/agentevals](https://github.com/langchain-ai/agentevals)
- 固定的上游提交：`db42ec14993de1e123d7c527b79944baa3106d14`
- 许可证：MIT

本仓库没有重命名或宣称拥有上游评估器的原创权。原始版权和许可证文件均被保留，本项目只在其基础上增加独立的回归分析层。详细说明见 [FORK_NOTES.md](FORK_NOTES.md)。

## 相关项目

- [OpenEvals](https://github.com/langchain-ai/openevals)：更通用的评估工具；
- [LangGraph](https://github.com/langchain-ai/langgraph)：用于构建有状态 Agent 工作流；
- [LangSmith](https://www.langchain.com/langsmith)：Agent 调试、追踪和评估平台。
