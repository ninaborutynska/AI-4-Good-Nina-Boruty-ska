"""Exercise genuine transformer inference incrementally on isolated synthetic fixtures."""
import json
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyse_sentiment import run, parser
from sentiment.core import Classifier, atomic_csv, read_rows, RESULT_COLUMNS
ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        columns = ["comment_id", "video_id", "text", "published_at", "collected_at"]
        records = [dict(comment_id=f"synthetic-test-{i}", video_id="test-only", text=text, published_at="2026-10-14T00:00:00Z", collected_at="2026-10-14T01:00:00Z") for i, text in enumerate([
            "I love this technology. Self-driving cars are wonderful!",
            "This is terrible and unsafe. I hate these dangerous cars.",
            "The video describes a self-driving car travelling along a road."
        ])]
        atomic_csv(folder / "source.csv", columns, records[:2])
        arguments = parser().parse_args(["--input", str(folder / "source.csv"), "--output", str(folder / "results.csv"), "--status", str(folder / "status.csv"), "--cache-dir", str(ROOT / ".model-cache"), "--batch-size", "2"])
        source_bytes = arguments.input.read_bytes()
        assert run(arguments)["successful"] == 2
        assert arguments.input.read_bytes() == source_bytes
        first = read_rows(arguments.output, RESULT_COLUMNS)
        assert len(first) == 2
        assert run(arguments)["successful"] == 0
        atomic_csv(folder / "source.csv", columns, records)
        assert run(arguments)["successful"] == 1
        results = read_rows(arguments.output, RESULT_COLUMNS)
        assert len(results) == 3 and all(results[key] == value for key, value in first.items())
        assert all(0 <= float(row["confidence"]) <= 1 for row in results.values())
        report = {"test_data": "Synthetic fixtures in a temporary directory, never research data", "incremental": "passed", "duplicate_prevention": "passed", "source_preservation": "passed", "test_predictions": 3, "models": sorted(set(row["model_version"] for row in results.values()))}
        (ROOT / "tests/real_pipeline_smoke_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
