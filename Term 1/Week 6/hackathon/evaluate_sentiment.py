"""Evaluate only genuine human labels; compare the transformer with VADER."""
from __future__ import annotations
import argparse
import json
import hashlib
from pathlib import Path
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiment.core import LABELS, atomic_csv, now, read_rows, RESULT_COLUMNS

BASE = Path(__file__).resolve().parent
MANUAL_COLUMNS = ["comment_id", "text", "manual_sentiment"]


def metrics(truth, predictions):
    matrix = [[0] * 3 for _ in LABELS]
    for actual, predicted in zip(truth, predictions):
        matrix[LABELS.index(actual)][LABELS.index(predicted)] += 1
    correct = sum(matrix[i][i] for i in range(3))
    return {"accuracy": correct / len(truth), "count": len(truth), "labels": LABELS, "confusion_matrix": matrix}


def evaluate(comments_path, results_path, labels_path):
    comments = read_rows(comments_path, ["comment_id", "text"])
    results = read_rows(results_path, RESULT_COLUMNS)
    labels = read_rows(labels_path, MANUAL_COLUMNS)
    if not labels:
        return {"status": "awaiting_manual_labels", "message": "No manually labelled real comments are available.", "manual_count": 0}
    valid = []
    excluded = []
    for identifier, row in labels.items():
        if not row["manual_sentiment"]:
            continue
        if row["manual_sentiment"] not in (*LABELS, "Not relevant"):
            raise ValueError("Manual labels must be Positive, Neutral, Negative, or Not relevant")
        if identifier not in comments or row["text"] != comments[identifier]["text"]:
            raise ValueError("Manual labels must refer to the unchanged text of real collected comments")
        if row["manual_sentiment"] == "Not relevant" or row.get("relevance", "").strip().lower() == "no":
            excluded.append(row)
        else:
            valid.append(row)
    matched = [row for row in valid if row["comment_id"] in results]
    if not valid:
        return {"status": "awaiting_manual_labels", "message": "No relevant comments have genuine manual sentiment labels yet.", "manual_count": 0, "excluded_irrelevant_count": len(excluded)}
    if not matched:
        return {"status": "awaiting_predictions", "message": "No manually labelled comments have transformer predictions yet.", "manual_count": len(valid)}
    baseline = SentimentIntensityAnalyzer()
    truth = [row["manual_sentiment"] for row in matched]
    transformer = [results[row["comment_id"]]["sentiment"] for row in matched]
    compound = [baseline.polarity_scores(row["text"])["compound"] for row in matched]
    vader = ["Positive" if value >= .05 else "Negative" if value <= -.05 else "Neutral" for value in compound]
    failures = [dict(comment_id=row["comment_id"], text=row["text"], actual=actual, predicted=predicted, explanation=row.get("notes", ""))
                for row, actual, predicted in zip(matched, truth, transformer) if actual != predicted]
    documented = sum(bool(row["explanation"].strip()) for row in failures)
    return dict(status="ready" if len(matched) >= 50 and documented >= 3 else "incomplete_evaluation",
                manual_labels_sha256=hashlib.sha256(labels_path.read_bytes()).hexdigest(),
                predictions_sha256=hashlib.sha256(results_path.read_bytes()).hexdigest(),
                manual_count=len(valid), evaluated_count=len(matched), unmatched_count=len(valid) - len(matched),
                excluded_irrelevant_count=len(excluded), total_labelled_count=len(valid) + len(excluded),
                transformer=metrics(truth, transformer), baseline=metrics(truth, vader),
                baseline_name="VADER 3.3.2 (compound thresholds ±0.05)", failures=failures,
                documented_failures=documented, evaluated_at=now(),
                models=sorted(set(results[row["comment_id"]]["model_version"] for row in matched)),
                message="Label sentiment toward autonomous driving. Not relevant comments are excluded. Requirement: at least 50 matched relevant manual labels and 3 human-documented classification failures. Names, timestamps, and notes are optional for labelling; failure explanations can be added after comparison.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", type=Path, default=BASE / "data/youtube_comments.csv")
    parser.add_argument("--results", type=Path, default=BASE / "data/sentiment_results.csv")
    parser.add_argument("--labels", type=Path, default=BASE / "data/manual_labels.csv")
    parser.add_argument("--output", type=Path, default=BASE / "data/evaluation.json")
    parser.add_argument("--prepare-labels", action="store_true", help="Create a blind 60-comment sample with EMPTY manual labels; refuses to overwrite")
    args = parser.parse_args()
    if args.prepare_labels:
        if args.labels.exists():
            raise SystemExit("Manual labels already exist; refusing to overwrite human work")
        source = pd.read_csv(args.comments, dtype=str, keep_default_na=False).drop_duplicates("comment_id")
        source = source[(source.comment_id.str.strip() != "") & (source.text.str.strip() != "")]
        sample = source.sample(n=min(60, len(source)), random_state=42)
        atomic_csv(args.labels, MANUAL_COLUMNS, ({"comment_id": row.comment_id, "text": row.text} for row in sample.itertuples()))
        print(f"Prepared {len(sample)} real comments with empty manual labels. Annotate independently before viewing predictions.")
    else:
        report = evaluate(args.comments, args.results, args.labels)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(args.output)
        print(json.dumps(report, indent=2, ensure_ascii=True))
