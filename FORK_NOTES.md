# Portfolio extension notes

- Upstream: https://github.com/langchain-ai/agentevals
- Upstream commit: `db42ec14993de1e123d7c527b79944baa3106d14`
- License: MIT; original copyright and license files are preserved.

## Upstream capabilities retained

- strict, unordered, subset and superset trajectory matching
- LLM-as-judge trajectory evaluation
- LangGraph trajectory evaluators

## Added in this branch

- paired baseline/candidate Agent run comparison
- success, metric, latency and trajectory-change deltas
- configurable CI quality gates
- new/resolved failure reporting
- failure taxonomy aggregation
- adapter for the opinion-analysis Agent task report
- Agent-contract pass-rate gates and contract-failure taxonomy through that adapter
- JSON CLI suitable for local regression tests or CI

The new code does not rename or claim authorship of upstream evaluators. It adds a separate
regression-analysis layer on top of them.
