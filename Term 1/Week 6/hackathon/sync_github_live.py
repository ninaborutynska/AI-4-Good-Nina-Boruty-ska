"""Read-only GitHub-to-dashboard bridge. Never runs or modifies the collector."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import zipfile

import requests
from filelock import FileLock
from sentiment.core import now, read_rows, RESULT_COLUMNS, STATUS_COLUMNS

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / "runtime/live"
API = "https://api.github.com/repos/LuukAalders/Hackathons"


class SyncError(Exception):
    pass


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def token():
    direct = os.environ.get("GITHUB_TOKEN", "").strip()
    if direct:
        return direct
    configured = os.environ.get("GITHUB_TOKEN_FILE")
    config = LIVE / "credentials.json"
    if not configured and config.exists():
        configured = json.loads(config.read_text(encoding="utf-8")).get("token_file")
    path = Path(configured) if configured else LIVE / "github-token"
    if not path.is_file():
        raise SyncError("Connect GitHub on the Connection page to enable live updates.")
    value = path.read_text(encoding="utf-8-sig").strip()
    # Accept either a plain token or a local dotenv file without returning its contents.
    for line in value.splitlines():
        if line.startswith(("GITHUB_TOKEN=", "GH_TOKEN=")):
            value = line.split("=", 1)[1].strip().strip("\"'")
            break
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise SyncError("The local token file is empty or has an unsupported format.")
    return value


class GitHub:
    def __init__(self, access_token):
        self.session = requests.Session()
        self.session.headers.update(Authorization=f"Bearer {access_token}", Accept="application/vnd.github+json",
                                    **{"X-GitHub-Api-Version": "2022-11-28"})

    def get(self, route, raw=False, optional=False):
        response = self.session.get(API + route, timeout=(10, 45),
                                    headers={"Accept": "application/vnd.github.raw+json" if raw else "application/vnd.github+json"})
        if optional and response.status_code == 404:
            return None
        if not response.ok:
            if response.status_code == 401:
                raise SyncError("GitHub authentication failed. Replace the token on the Connection page.")
            if response.status_code in (403, 404):
                raise SyncError("GitHub access failed. The token needs Contents: Read and Actions: Read for Hackathons, or its request allowance may be exhausted.")
            raise SyncError("GitHub is temporarily unavailable. Updates will retry automatically.")
        return response.content if raw else response.json()

    def source(self, commit, name, optional=False):
        return self.get(f"/contents/Hackathon%206/data/{name}?ref={commit}", raw=True, optional=optional)


def unpack_artifact(payload, expected_digest):
    if expected_digest and expected_digest != "sha256:" + hashlib.sha256(payload).hexdigest():
        raise SyncError("The downloaded sentiment artifact failed its integrity check.")
    files = {}
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if sum(item.file_size for item in archive.infolist()) > 25_000_000:
            raise SyncError("The sentiment artifact exceeds the supported size.")
        for item in archive.infolist():
            name = Path(item.filename).name
            if name in {"sentiment_results.csv", "processing_status.csv", "validation.json"}:
                if name in files:
                    raise SyncError("The sentiment artifact contains ambiguous files.")
                files[name] = archive.read(item)
    if len(files) != 3:
        raise SyncError("The sentiment artifact is missing its results or validation report.")
    report = json.loads(files["validation.json"])
    if not report.get("source_unchanged") or report.get("counts", {}).get("failed") != 0:
        raise SyncError("The sentiment artifact did not pass source preservation and inference checks.")
    if not re.fullmatch(r"[a-f0-9]{40}", report.get("source_commit", "")):
        raise SyncError("The sentiment artifact has no valid source commit.")
    return files, report


def sync_once(client, live=LIVE, labels_path=None):
    live.mkdir(parents=True, exist_ok=True)
    manifest_path = live / "current.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    commit = client.get("/commits/main")["sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise SyncError("GitHub returned an invalid source commit.")
    runs = client.get("/actions/workflows/sentiment.yml/runs?branch=main&status=success&per_page=1")["workflow_runs"]
    if not runs:
        raise SyncError("Waiting for the first successful GitHub sentiment analysis.")
    run = runs[0]
    if run.get("head_repository", {}).get("full_name") != "LuukAalders/Hackathons" or run.get("head_branch") != "main":
        raise SyncError("The sentiment workflow source could not be verified.")
    artifacts = client.get(f"/actions/runs/{run['id']}/artifacts")["artifacts"]
    candidates = [item for item in artifacts if not item["expired"] and item["name"].startswith(f"sentiment-checkpoints-{run['id']}-")]
    if not candidates:
        raise SyncError("The latest sentiment artifact is unavailable. Waiting for the next completed analysis.")
    artifact = max(candidates, key=lambda item: item["id"])
    labels_path = labels_path or ROOT / "data/manual_labels.csv"
    labels = labels_path.read_bytes() if labels_path.exists() else None
    labels_hash = hashlib.sha256(labels or b"").hexdigest()
    if old and old["commit"] == commit and old["artifact_id"] == artifact["id"] and old.get("labels_sha256") == labels_hash:
        return old
    snapshots = live / "snapshots"
    snapshots.mkdir(exist_ok=True)
    target = Path(tempfile.mkdtemp(prefix=commit[:12] + "-", dir=snapshots))
    if old and old["commit"] == commit:
        comments = (Path(old["data_directory"]) / "youtube_comments.csv").read_bytes()
        for name in ("youtube_comments.csv", "collection_log.csv", "monitoring_started.txt"):
            previous = Path(old["data_directory"]) / name
            if previous.exists():
                shutil.copyfile(previous, target / name)
    else:
        comments = client.source(commit, "youtube_comments.csv")
        (target / "youtube_comments.csv").write_bytes(comments)
        for name in ("collection_log.csv", "monitoring_started.txt"):
            content = client.source(commit, name, optional=True)
            if content is not None:
                (target / name).write_bytes(content)
    if old and old["artifact_id"] == artifact["id"]:
        for name in ("sentiment_results.csv", "processing_status.csv", "validation.json"):
            shutil.copyfile(Path(old["data_directory"]) / name, target / name)
    else:
        files, report = unpack_artifact(client.get(f"/actions/artifacts/{artifact['id']}/zip", raw=True), artifact.get("digest"))
        analysed_source = comments if report["source_commit"] == commit else client.source(report["source_commit"], "youtube_comments.csv")
        if hashlib.sha256(analysed_source).hexdigest() != report["source_sha256"]:
            raise SyncError("The sentiment results do not match their recorded source dataset.")
        for name, content in files.items():
            (target / name).write_bytes(content)
        predictions = read_rows(target / "sentiment_results.csv", RESULT_COLUMNS)
        statuses = read_rows(target / "processing_status.csv", STATUS_COLUMNS)
        analysed_ids = {row["comment_id"].strip() for row in csv.DictReader(io.StringIO(analysed_source.decode("utf-8-sig")))}
        if len(predictions) != report["total_predictions"] or len(statuses) != report["total_statuses"] or not set(predictions).issubset(analysed_ids):
            raise SyncError("The sentiment artifact record counts or comment IDs are inconsistent.")
        if any(row["sentiment"] not in {"Positive", "Neutral", "Negative"} or not math.isfinite(float(row["confidence"])) or not 0 <= float(row["confidence"]) <= 1 for row in predictions.values()):
            raise SyncError("The sentiment artifact contains invalid predictions.")
    # Preserve genuine local human labels and refresh their comparison against current predictions.
    if labels:
        (target / "manual_labels.csv").write_bytes(labels)
        from evaluate_sentiment import evaluate
        report = evaluate(target / "youtube_comments.csv", target / "sentiment_results.csv", target / "manual_labels.csv")
        (target / "evaluation.json").write_text(json.dumps(report), encoding="utf-8")
    manifest = dict(commit=commit, artifact_id=artifact["id"], analysis_run_id=run["id"],
                    data_directory=str(target.resolve()), labels_sha256=labels_hash, synced_at=now())
    # Publish only when every file and the evaluation are complete. Readers keep using the previous generation.
    atomic_json(manifest_path, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    LIVE.mkdir(parents=True, exist_ok=True)
    with FileLock(str(LIVE / "sync.lock"), timeout=0):
        while True:
            try:
                manifest = sync_once(GitHub(token()))
                status = dict(ok=True, checked_at=now(), commit=manifest["commit"], artifact_id=manifest["artifact_id"])
            except SyncError as error:
                status = dict(ok=False, checked_at=now(), error=str(error))
            except Exception:
                status = dict(ok=False, checked_at=now(), error="Live GitHub synchronization failed. The last complete snapshot is preserved; retrying automatically.")
            atomic_json(LIVE / "status.json", status)
            print(json.dumps(status), flush=True)
            if args.once:
                return 0 if status["ok"] else 1
            time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
