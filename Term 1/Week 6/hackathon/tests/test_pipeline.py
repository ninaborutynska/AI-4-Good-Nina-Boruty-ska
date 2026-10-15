"""Offline correctness tests use synthetic fixtures in temporary directories only."""
import argparse
import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyse_sentiment import run, parser
from evaluate_sentiment import evaluate, metrics
from sentiment.core import atomic_csv, read_rows, RESULT_COLUMNS, STATUS_COLUMNS, validate
from filelock import FileLock, Timeout

SOURCE_COLUMNS = ["comment_id", "video_id", "text", "published_at", "collected_at"]
class FakeTokenizer:
    def encode(self, text, **kwargs): return text.split()
class FakeClassifier:
    version = "synthetic-test-double-not-a-model"
    tokenizer = FakeTokenizer()
    max_length = 512
    def __init__(self, *args): pass
    def predict(self, texts):
        if any("FAIL" in text for text in texts): raise RuntimeError("Synthetic test failure")
        return [("Neutral", .7) for text in texts]

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.args = parser().parse_args(["--input", str(self.root / "input.csv"), "--output", str(self.root / "results.csv"), "--status", str(self.root / "status.csv"), "--batch-size", "2"])
    def tearDown(self): self.directory.cleanup()
    def write(self, records):
        atomic_csv(self.args.input, SOURCE_COLUMNS, [dict(comment_id=identifier, text=text, video_id="test", published_at="2026-10-14T00:00:00Z", collected_at="2026-10-14T01:00:00Z") for identifier, text in records])
    def test_incremental_unique_and_input_preserved(self):
        self.write([("one", "This is a synthetic English comment for an offline test."), ("one", "duplicate"), ("empty", "")])
        original = self.args.input.read_bytes()
        result = run(self.args, FakeClassifier)
        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["duplicate_input"], 1)
        self.assertEqual(self.args.input.read_bytes(), original)
        def forbidden(*args): raise AssertionError("No model should load for already processed comments")
        result = run(self.args, forbidden)
        self.assertEqual(result["successful"], 0)
        self.write([("one", "This is a synthetic English comment for an offline test."), ("two", "A new synthetic English comment has now arrived for testing.")])
        self.assertEqual(run(self.args, FakeClassifier)["successful"], 1)
        self.assertEqual(len(read_rows(self.args.output, RESULT_COLUMNS)), 2)
    def test_failed_batch_isolated_and_explicit_retry(self):
        self.write([("one", "This is a synthetic English comment for an offline test."), ("two", "This synthetic English comment must FAIL for the failure isolation test.")])
        self.assertEqual(run(self.args, FakeClassifier)["failed"], 1)
        self.assertEqual(len(read_rows(self.args.output, RESULT_COLUMNS)), 1)
        self.assertEqual(read_rows(self.args.status, STATUS_COLUMNS)["two"]["status"], "inference_failed")
        self.assertEqual(run(self.args, FakeClassifier)["failed"], 0)
        self.args.retry_failed = True
        self.assertEqual(run(self.args, FakeClassifier)["failed"], 1)
    def test_interruption_retains_prior_checkpoint(self):
        self.args.batch_size = 1
        self.write([("one", "This is a synthetic English comment for an offline test."), ("two", "Another English comment used only as a synthetic test fixture.")])
        class InterruptClassifier(FakeClassifier):
            calls = 0
            def predict(instance, texts):
                instance.calls += 1
                if instance.calls == 2: raise KeyboardInterrupt()
                return super().predict(texts)
        with self.assertRaises(KeyboardInterrupt): run(self.args, InterruptClassifier)
        self.assertEqual(len(read_rows(self.args.output, RESULT_COLUMNS)), 1)
        self.assertEqual(run(self.args, FakeClassifier)["successful"], 1)
        self.assertEqual(len(read_rows(self.args.output, RESULT_COLUMNS)), 2)
    def test_output_lock(self):
        self.write([])
        with FileLock(str(self.args.output) + ".lock"):
            with self.assertRaises(Timeout): run(self.args, FakeClassifier)
    def test_source_cannot_be_output(self):
        self.write([])
        self.args.output = self.args.input
        with self.assertRaises(ValueError): run(self.args, FakeClassifier)
    def test_duplicate_results_are_rejected(self):
        self.write([])
        row = dict(comment_id="duplicate", sentiment="Neutral", confidence=.7, model_version="test", analysed_at="2026-10-14T00:00:00Z")
        atomic_csv(self.args.output, RESULT_COLUMNS, [row, row])
        with self.assertRaises(ValueError): run(self.args, FakeClassifier)
    def test_malformed_metadata_and_empty_are_flagged(self):
        atomic_csv(self.args.input, SOURCE_COLUMNS, [dict(comment_id="one", text="A synthetic comment with invalid publication metadata.", video_id="test", published_at="invalid", collected_at="invalid")])
        self.assertEqual(run(self.args, FakeClassifier)["skipped"], 1)
        self.assertEqual(read_rows(self.args.status, STATUS_COLUMNS)["one"]["status"], "malformed")
        self.assertEqual(validate("")[0], "empty")
    def test_language_checks(self):
        self.assertEqual(validate("Dit is een Nederlandse reactie over de toekomst van zelfrijdende auto's en veiligheid op de openbare weg.")[0], "unsupported_language")
        self.assertEqual(validate("Great!")[0], "eligible")
        self.assertIn("short_text_language_uncertain", validate("Great!")[3])
    def test_metrics_rows_are_truth_columns_are_predictions(self):
        result = metrics(["Positive", "Negative", "Neutral"], ["Negative", "Negative", "Positive"])
        self.assertAlmostEqual(result["accuracy"], 1/3)
        self.assertEqual(result["confusion_matrix"], [[1,0,0],[0,0,1],[1,0,0]])
    def test_no_ground_truth_means_no_accuracy(self):
        self.write([("one", "A synthetic English test fixture, not actual research data.")])
        run(self.args, FakeClassifier)
        report = evaluate(self.args.input, self.args.output, self.root / "absent-labels.csv")
        self.assertEqual(report["status"], "awaiting_manual_labels")
        self.assertNotIn("transformer", report)
    def test_minimal_manual_labels_need_no_annotator_or_timestamp(self):
        self.write([("one", "A synthetic English test fixture, not actual research data."), ("two", "Another synthetic English test fixture for an unrelated topic.")])
        run(self.args, FakeClassifier)
        source = read_rows(self.args.input, SOURCE_COLUMNS)
        path = self.root / "labels.csv"
        atomic_csv(path, ["comment_id", "text", "manual_sentiment"], [
            dict(comment_id="one", text=source["one"]["text"], manual_sentiment="Positive"),
            dict(comment_id="two", text=source["two"]["text"], manual_sentiment="Not relevant")])
        report = evaluate(self.args.input, self.args.output, path)
        self.assertEqual(report["manual_count"], 1)
        self.assertEqual(report["excluded_irrelevant_count"], 1)
        self.assertEqual(report["evaluated_count"], 1)
        self.assertEqual(report["failures"][0]["explanation"], "")

if __name__ == "__main__": unittest.main()
