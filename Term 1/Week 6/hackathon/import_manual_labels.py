"""Validate extracted Excel annotations before publishing the evaluation CSV."""
import argparse
import hashlib
import json
from pathlib import Path
from sentiment.core import LABELS, atomic_csv, now, read_rows

BASE = Path(__file__).resolve().parent

def import_labels(extracted, comments, output, overrides=None):
    payload = json.loads(extracted.read_text(encoding="utf-8"))
    source = read_rows(comments, ["comment_id", "text"])
    previous_rows = read_rows(output, ["comment_id", "text", "manual_sentiment"])
    records = []
    seen = set()
    for row in payload["rows"]:
        identifier = row["comment_id"]
        if not identifier or identifier in seen:
            raise ValueError("Missing or duplicate comment ID in the annotation file")
        seen.add(identifier)
        if identifier not in source or row["text"] != source[identifier]["text"]:
            raise ValueError("Annotation text/ID differs from the collected source; no labels were imported")
        label = row["manual_sentiment"].strip()
        if overrides and identifier in overrides:
            if label and label != overrides[identifier]:
                raise ValueError("A supplied completion conflicts with an existing workbook label")
            label = overrides[identifier]
        if label not in (*LABELS, "Not relevant", ""):
            raise ValueError(f"Unsupported annotation label for comment {identifier}")
        record = dict(comment_id=identifier, text=row["text"], manual_sentiment=label)
        previous = previous_rows.get(identifier, {})
        if previous.get("manual_sentiment") == label and previous.get("text") == row["text"] and previous.get("notes"):
            record["notes"] = previous["notes"]
        records.append(record)
    if overrides and not set(overrides).issubset(seen):
        raise ValueError("A completion refers to a comment outside the uploaded sample")
    if output.exists():
        previous = output.read_bytes()
        if any(row["manual_sentiment"] for row in previous_rows.values()):
            archive = output.parent / "annotation_history" / (hashlib.sha256(previous).hexdigest() + ".csv")
            archive.parent.mkdir(parents=True, exist_ok=True)
            if not archive.exists(): archive.write_bytes(previous)
    columns = ["comment_id", "text", "manual_sentiment"] + (["notes"] if any(row.get("notes") for row in records) else [])
    atomic_csv(output, columns, records)
    report = dict(imported_at=now(), workbook=payload["source"], sample_size=len(records),
        label_counts={label: sum(row["manual_sentiment"] == label for row in records) for label in (*LABELS,"Not relevant","")},
        manual_csv_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        supplied_completions=overrides or {},
        completion_source="Explicit human replies in the chat" if overrides else None)
    workbook_path = Path(payload["source"])
    if workbook_path.exists(): report["workbook_sha256"] = hashlib.sha256(workbook_path.read_bytes()).hexdigest()
    (output.parent / "manual_labels_import.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extracted", type=Path, required=True)
    parser.add_argument("--comments", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=BASE / "data/manual_labels.csv")
    parser.add_argument("--completions", type=Path)
    args = parser.parse_args()
    completions = json.loads(args.completions.read_text(encoding="utf-8")) if args.completions else None
    print(json.dumps(import_labels(args.extracted,args.comments,args.output,completions),indent=2))
