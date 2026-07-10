from agentevals.trace_adapter import from_opinion_agent_task


def test_opinion_agent_adapter_preserves_metrics_and_failure_reasons():
    record = from_opinion_agent_task(
        {
            "task_id": "event-1",
            "execution_success": True,
            "trajectory": ["sentiment_classifier", "evidence_retriever"],
            "label_accuracy": 0.5,
            "evidence_count": 0,
            "latency_ms": 42,
            "needs_review": True,
            "review_reasons": ["no_retrieval_evidence"],
            "agent_contract_passed": False,
            "failed_contract_checks": ["evidence_provenance_integrity"],
        }
    )

    assert record["metrics"]["label_accuracy"] == 0.5
    assert record["metrics"]["agent_contract_pass_rate"] == 0.0
    assert record["failures"] == [
        "retrieval_rejected",
        "review_required",
        "agent_contract_violation",
        "contract:evidence_provenance_integrity",
    ]
