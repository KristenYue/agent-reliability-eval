from agentevals.regression import compare_run_sets, summarize_runs


def record(task_id, success=True, accuracy=1.0, latency=10.0, trajectory=None):
    return {
        "task_id": task_id,
        "success": success,
        "trajectory": trajectory or ["classify", "retrieve"],
        "metrics": {"accuracy": accuracy},
        "latency_ms": latency,
        "failures": [] if success else ["tool_error"],
    }


def test_compare_run_sets_detects_quality_and_latency_regressions():
    baseline = [record("a"), record("b")]
    candidate = [record("a", accuracy=0.7, latency=20), record("b", accuracy=0.7, latency=20)]

    report = compare_run_sets(
        baseline,
        candidate,
        {
            "max_metric_drop": {"accuracy": 0.1},
            "max_p95_latency_increase_ratio": 0.5,
        },
    )

    assert report["gate_passed"] is False
    assert {item["gate"] for item in report["violations"]} == {
        "metric:accuracy",
        "p95_latency",
    }


def test_compare_run_sets_reports_trajectory_changes_and_new_failures():
    baseline = [record("a"), record("b")]
    candidate = [record("a", trajectory=["classify"]), record("b", success=False)]

    report = compare_run_sets(baseline, candidate)

    assert report["changed_trajectory_tasks"] == ["a"]
    assert report["new_failure_tasks"] == ["b"]


def test_summarize_runs_counts_failure_taxonomy():
    records = [record("a"), record("b", success=False)]

    summary = summarize_runs(records)

    assert summary["success_rate"] == 0.5
    assert summary["failure_counts"] == {"tool_error": 1}
