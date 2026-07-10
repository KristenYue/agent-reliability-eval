# Agent regression and trajectory diagnostics extension

This branch extends the upstream MIT-licensed AgentEvals project with paired version regression
analysis. The upstream trajectory evaluators remain unchanged.

## Added capabilities

- compare baseline and candidate runs by paired `task_id`
- aggregate success rate, arbitrary numeric metrics and latency percentiles
- identify changed trajectories, new failures and resolved failures
- classify application-specific failure signals through adapters
- enforce configurable quality gates in local development or CI
- write a machine-readable JSON report and return a non-zero exit code on gate failure

## CLI

```powershell
python -m agentevals.regression_cli `
  --baseline baseline.json `
  --candidate candidate.json `
  --thresholds thresholds.json `
  --output regression_report.json
```

## Real integration result

The checked-in example compares 36 paired runs from the opinion-analysis Agent:

- baseline: character TF-IDF retrieval
- candidate: TF-IDF + BGE-small-zh-v1.5 reciprocal-rank fusion with relevance rejection
- success rate: unchanged at 100%
- mean per-task label accuracy: unchanged
- Agent contract pass rate: unchanged at 100%
- p95 latency in the latest local run: 112.6 ms -> 152.0 ms (1.35x)
- trajectory changes: 0
- new execution failures: 0
- candidate rejected low-confidence retrieval evidence in 29/36 tasks
- configured quality gate: passed

The report does not claim that fewer accepted documents automatically means better retrieval. It
records the behavior change for separate retrieval-quality evaluation. Latency values are local-run
measurements and can vary with model warm-up and machine load; the paired ratio is retained in the
machine-readable report.

## Test scope

The four new deterministic tests pass without external services. Upstream LLM-as-judge tests are
not run without an API key; they must not be reported as passing in that environment.
