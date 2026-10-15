"""Run real inference into an isolated artifact directory and verify source preservation."""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyse_sentiment import parser, run
from sentiment.core import read_rows, RESULT_COLUMNS, STATUS_COLUMNS


def main():
    args = parser().parse_args()
    original = hashlib.sha256(args.input.read_bytes()).hexdigest()
    counts = run(args)
    unchanged = hashlib.sha256(args.input.read_bytes()).hexdigest() == original
    results = read_rows(args.output, RESULT_COLUMNS)
    statuses = read_rows(args.status, STATUS_COLUMNS)
    report = dict(counts=counts, total_predictions=len(results), total_statuses=len(statuses),
                  source_sha256=original, source_unchanged=unchanged,
                  source_commit=os.environ.get("SOURCE_COMMIT", "local"))
    (args.output.parent / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report), flush=True)
    if not unchanged or counts["failed"] or counts["malformed_input"]:
        raise SystemExit("Validation failed; inspect artifact checkpoints and validation.json")


if __name__ == "__main__":
    main()
