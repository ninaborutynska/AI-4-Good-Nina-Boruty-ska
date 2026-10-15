"""Incremental local Hugging Face analysis. Never writes source comments or logs."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from filelock import FileLock, Timeout
from sentiment.core import Classifier, RESULT_COLUMNS, STATUS_COLUMNS, LABELS, atomic_csv, now, read_rows, text_hash, validate

BASE = Path(__file__).resolve().parent


def run(args, classifier_factory=Classifier):
    started = time.monotonic()
    if not args.input.is_file():
        raise FileNotFoundError(f"YouTube comments dataset not found: {args.input}")
    if args.input.resolve() in {args.output.resolve(), args.status.resolve()} or args.output.resolve() == args.status.resolve():
        raise ValueError("Input, predictions and processing status must be separate files")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(args.output) + ".lock", timeout=0):
        results = read_rows(args.output, RESULT_COLUMNS)
        statuses = read_rows(args.status, STATUS_COLUMNS)
        for row in results.values():
            if row["sentiment"] not in LABELS or not 0 <= float(row["confidence"]) <= 1:
                raise ValueError("Existing predictions contain invalid sentiment or confidence")
        model = None
        pending = []
        seen = set()
        counts = dict(successful=0, skipped=0, failed=0, duplicate_input=0, malformed_input=0)

        def checkpoint():
            atomic_csv(args.output, RESULT_COLUMNS, results.values())
            atomic_csv(args.status, STATUS_COLUMNS, statuses.values())

        def flush():
            nonlocal model
            if not pending:
                checkpoint()
                return
            if model is None:
                model = classifier_factory(args.cache_dir, args.revision, args.device, args.threads)
            # Split a failing batch recursively, isolating failures and reducing OOM pressure.
            def infer(batch):
                try:
                    predictions = model.predict([record["text"] for record in batch])
                    if len(predictions) != len(batch):
                        raise ValueError("Incomplete model batch")
                except Exception as error:
                    if len(batch) > 1:
                        mid = len(batch) // 2
                        infer(batch[:mid])
                        infer(batch[mid:])
                    else:
                        status = statuses[batch[0]["comment_id"]]
                        status.update(status="inference_failed", reason=f"Inference failed ({type(error).__name__}); use --retry-failed")
                        counts["failed"] += 1
                    return
                timestamp = now()
                for record, (label, score) in zip(batch, predictions):
                    identifier = record["comment_id"]
                    results[identifier] = dict(comment_id=identifier, sentiment=label, confidence=f"{score:.8f}",
                                               model_version=model.version, analysed_at=timestamp)
                    status = statuses[identifier]
                    flags = status["quality_flags"].split(";")
                    if score < .60:
                        flags.append("low_confidence")
                    if len(model.tokenizer.encode(record["text"], truncation=False)) > model.max_length:
                        flags.append("truncated")
                    status.update(status="analysed", reason="", quality_flags=";".join(flags), checked_at=timestamp)
                    counts["successful"] += 1
            infer(pending)
            pending.clear()
            checkpoint()
            print(json.dumps({**counts, "total_predictions": len(results), "elapsed_seconds": round(time.monotonic() - started, 2)}), flush=True)

        required = {"comment_id", "video_id", "text", "published_at", "collected_at"}
        headers = pd.read_csv(args.input, nrows=0).columns
        if not required.issubset(headers):
            raise ValueError(f"Missing source columns: {', '.join(sorted(required - set(headers)))}")
        with pd.read_csv(args.input, dtype=str, keep_default_na=False, chunksize=1000, on_bad_lines="warn") as reader:
            for chunk in reader:
                for record in chunk.to_dict("records"):
                    identifier = record["comment_id"].strip()
                    record["comment_id"] = identifier
                    if not identifier:
                        counts["malformed_input"] += 1
                        continue
                    if identifier in seen:
                        counts["duplicate_input"] += 1
                        continue
                    seen.add(identifier)
                    if identifier in results:
                        continue
                    digest = text_hash(record["text"])
                    previous = statuses.get(identifier, {})
                    if previous.get("text_hash") == digest and previous.get("status") in {"empty", "malformed", "unsupported_language", "inference_failed"} and not args.retry_failed:
                        continue
                    state, reason, language, flags = validate(record["text"])
                    if not record["video_id"].strip() or any(pd.isna(pd.to_datetime(record[field], utc=True, errors="coerce")) for field in ("published_at", "collected_at")):
                        state, reason = "malformed", "Missing video ID or invalid publication/collection timestamp"
                    statuses[identifier] = dict(comment_id=identifier, status=state, reason=reason, language=language,
                                                quality_flags=";".join(flags), text_hash=digest, checked_at=now())
                    if state != "eligible":
                        counts["skipped"] += 1
                        continue
                    pending.append(record)
                    if len(pending) >= args.batch_size:
                        flush()
                    if args.limit and counts["successful"] + counts["failed"] + len(pending) >= args.limit:
                        flush()
                        return counts
        flush()
        print(json.dumps({"finished": True, **counts, "total_predictions": len(results), "elapsed_seconds": round(time.monotonic() - started, 2)}), flush=True)
        return counts


def parser():
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--input", type=Path, default=BASE / "data/youtube_comments.csv")
    value.add_argument("--output", type=Path, default=BASE / "data/sentiment_results.csv")
    value.add_argument("--status", type=Path, default=BASE / "data/processing_status.csv")
    value.add_argument("--cache-dir", type=Path, default=BASE / ".model-cache")
    value.add_argument("--revision", default="main", help="Pin a model commit for reproducible inference")
    value.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    value.add_argument("--threads", type=int, default=4)
    value.add_argument("--batch-size", type=int, default=16)
    value.add_argument("--limit", type=int, default=0, help="Smoke-test only this many pending comments")
    value.add_argument("--retry-failed", action="store_true")
    return value


if __name__ == "__main__":
    arguments = parser().parse_args()
    if arguments.batch_size < 1 or arguments.threads < 1 or arguments.limit < 0:
        raise SystemExit("Batch size/threads must be positive and limit must be nonnegative")
    try:
        run(arguments)
    except Timeout:
        raise SystemExit("Another sentiment processing run owns the output lock")
    except (OSError, ValueError) as error:
        raise SystemExit(f"Sentiment processing stopped safely: {error}")
