"""Adapters from application traces to generic regression run records."""

from __future__ import annotations

from agentevals.regression import RunRecord


def from_opinion_agent_task(result: dict[str, object]) -> RunRecord:
    """Normalize one opinion-agent task result without importing that project."""
    reasons = [str(reason) for reason in result.get("review_reasons", [])]
    failed_contract_checks = [
        str(check) for check in result.get("failed_contract_checks", [])
    ]
    failures: list[str] = []
    if not result.get("execution_success", False):
        failures.append("tool_execution_error")
    if "no_retrieval_evidence" in reasons:
        failures.append("retrieval_rejected")
    if result.get("needs_review", False):
        failures.append("review_required")
    if result.get("agent_contract_passed") is False:
        failures.append("agent_contract_violation")
        failures.extend(f"contract:{check}" for check in failed_contract_checks)
    trajectory = [str(node) for node in result.get("trajectory", [])]
    metrics = {
        "label_accuracy": float(result.get("label_accuracy", 0.0)),
        "evidence_count": float(result.get("evidence_count", 0.0)),
    }
    if "agent_contract_passed" in result:
        metrics["agent_contract_pass_rate"] = float(
            bool(result["agent_contract_passed"])
        )
    return {
        "task_id": str(result["task_id"]),
        "success": bool(result.get("execution_success", False)),
        "trajectory": trajectory,
        "metrics": metrics,
        "latency_ms": float(result.get("latency_ms", 0.0)),
        "failures": failures,
    }
