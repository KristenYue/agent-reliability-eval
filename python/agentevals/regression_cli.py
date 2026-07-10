"""Command-line interface for paired Agent regression gates."""

from argparse import ArgumentParser
from pathlib import Path
import json

from agentevals.regression import compare_run_sets
from agentevals.trace_adapter import from_opinion_agent_task


def main() -> int:
    parser = ArgumentParser(description="Compare baseline and candidate Agent run records")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--thresholds", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    baseline = _load_records(args.baseline)
    candidate = _load_records(args.candidate)
    thresholds = json.loads(args.thresholds.read_text(encoding="utf-8")) if args.thresholds else {}
    report = compare_run_sets(baseline, candidate, thresholds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"gate_passed": report["gate_passed"], "violations": report["violations"]}, indent=2))
    return 0 if report["gate_passed"] else 1


def _load_records(path: Path) -> list[dict[str, object]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict):
        value = value.get("records", value.get("task_results"))
    if not isinstance(value, list):
        raise ValueError(f"Expected a JSON list or records/task_results wrapper: {path}")
    if value and isinstance(value[0], dict) and "execution_success" in value[0]:
        value = [from_opinion_agent_task(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
