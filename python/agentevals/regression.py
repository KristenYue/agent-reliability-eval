"""Paired Agent-version regression analysis and CI quality gates."""

from __future__ import annotations

from collections.abc import Sequence
from statistics import mean
from typing import NotRequired, TypedDict
import math


class RunRecord(TypedDict):
    task_id: str
    success: bool
    trajectory: list[str]
    metrics: dict[str, float]
    latency_ms: float
    failures: NotRequired[list[str]]


class RegressionThresholds(TypedDict, total=False):
    max_success_rate_drop: float
    max_metric_drop: dict[str, float]
    max_p95_latency_increase_ratio: float
    max_trajectory_change_rate: float


def compare_run_sets(
    baseline: Sequence[RunRecord],
    candidate: Sequence[RunRecord],
    thresholds: RegressionThresholds | None = None,
) -> dict[str, object]:
    """Compare two paired run sets and return an auditable gate report."""
    thresholds = thresholds or {}
    baseline_by_id = _index_unique(baseline, "baseline")
    candidate_by_id = _index_unique(candidate, "candidate")
    task_ids = sorted(set(baseline_by_id) & set(candidate_by_id))
    if not task_ids:
        raise ValueError("Baseline and candidate have no overlapping task_id values")

    base = [baseline_by_id[task_id] for task_id in task_ids]
    cand = [candidate_by_id[task_id] for task_id in task_ids]
    base_summary = summarize_runs(base)
    candidate_summary = summarize_runs(cand)
    metric_names = sorted(
        set(base_summary["metric_means"]) & set(candidate_summary["metric_means"])
    )
    metric_deltas = {
        name: candidate_summary["metric_means"][name] - base_summary["metric_means"][name]
        for name in metric_names
    }
    changed_trajectories = [
        task_id
        for task_id in task_ids
        if baseline_by_id[task_id]["trajectory"] != candidate_by_id[task_id]["trajectory"]
    ]
    new_failures = [
        task_id
        for task_id in task_ids
        if baseline_by_id[task_id]["success"] and not candidate_by_id[task_id]["success"]
    ]
    resolved_failures = [
        task_id
        for task_id in task_ids
        if not baseline_by_id[task_id]["success"] and candidate_by_id[task_id]["success"]
    ]
    trajectory_change_rate = len(changed_trajectories) / len(task_ids)
    success_rate_drop = base_summary["success_rate"] - candidate_summary["success_rate"]
    latency_ratio = _safe_ratio(
        candidate_summary["latency_ms"]["p95"], base_summary["latency_ms"]["p95"]
    )

    violations: list[dict[str, object]] = []
    max_success_drop = thresholds.get("max_success_rate_drop", 0.0)
    if success_rate_drop > max_success_drop:
        violations.append(
            {
                "gate": "success_rate",
                "actual_drop": success_rate_drop,
                "allowed_drop": max_success_drop,
            }
        )
    for name, allowed_drop in thresholds.get("max_metric_drop", {}).items():
        if name not in metric_deltas:
            violations.append({"gate": f"metric:{name}", "error": "metric_missing"})
        elif -metric_deltas[name] > allowed_drop:
            violations.append(
                {
                    "gate": f"metric:{name}",
                    "actual_drop": -metric_deltas[name],
                    "allowed_drop": allowed_drop,
                }
            )
    max_latency_ratio = thresholds.get("max_p95_latency_increase_ratio")
    if max_latency_ratio is not None and latency_ratio > 1 + max_latency_ratio:
        violations.append(
            {
                "gate": "p95_latency",
                "actual_ratio": latency_ratio,
                "allowed_ratio": 1 + max_latency_ratio,
            }
        )
    max_trajectory_rate = thresholds.get("max_trajectory_change_rate")
    if max_trajectory_rate is not None and trajectory_change_rate > max_trajectory_rate:
        violations.append(
            {
                "gate": "trajectory_change_rate",
                "actual": trajectory_change_rate,
                "allowed": max_trajectory_rate,
            }
        )

    return {
        "paired_tasks": len(task_ids),
        "baseline": base_summary,
        "candidate": candidate_summary,
        "deltas": {
            "success_rate": candidate_summary["success_rate"] - base_summary["success_rate"],
            "metrics": metric_deltas,
            "p95_latency_ratio": latency_ratio,
            "trajectory_change_rate": trajectory_change_rate,
        },
        "changed_trajectory_tasks": changed_trajectories,
        "new_failure_tasks": new_failures,
        "resolved_failure_tasks": resolved_failures,
        "gate_passed": not violations,
        "violations": violations,
    }


def summarize_runs(records: Sequence[RunRecord]) -> dict[str, object]:
    if not records:
        raise ValueError("Cannot summarize an empty run set")
    metric_names = sorted(set.intersection(*(set(record["metrics"]) for record in records)))
    latencies = [float(record["latency_ms"]) for record in records]
    failure_counts: dict[str, int] = {}
    for record in records:
        for failure in record.get("failures", []):
            failure_counts[failure] = failure_counts.get(failure, 0) + 1
    return {
        "tasks": len(records),
        "success_rate": sum(bool(record["success"]) for record in records) / len(records),
        "metric_means": {
            name: mean(float(record["metrics"][name]) for record in records)
            for name in metric_names
        },
        "latency_ms": {
            "mean": mean(latencies),
            "p50": _percentile(latencies, 0.50),
            "p95": _percentile(latencies, 0.95),
            "max": max(latencies),
        },
        "failure_counts": failure_counts,
    }


def _index_unique(records: Sequence[RunRecord], name: str) -> dict[str, RunRecord]:
    indexed: dict[str, RunRecord] = {}
    for record in records:
        task_id = record["task_id"]
        if task_id in indexed:
            raise ValueError(f"Duplicate task_id in {name}: {task_id}")
        indexed[task_id] = record
    return indexed


def _percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(len(ordered) * q) - 1))
    return ordered[index]


def _safe_ratio(candidate: float, baseline: float) -> float:
    if baseline == 0:
        return 1.0 if candidate == 0 else math.inf
    return candidate / baseline
