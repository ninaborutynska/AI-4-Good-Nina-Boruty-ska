"""Incrementally analyse updated local CSVs; never starts or modifies the collector."""
from __future__ import annotations
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path
from filelock import FileLock, Timeout
from sentiment.core import read_rows, STATUS_COLUMNS
ROOT = Path(__file__).resolve().parent

def watch(source, interval=60, once=False):
    previous = ""
    with FileLock(str(ROOT / "data/local-monitor.lock"), timeout=0):
        while True:
            try:
                digest = hashlib.sha256(source.read_bytes()).hexdigest()
                if digest != previous:
                    result = subprocess.run([sys.executable, str(ROOT / "analyse_sentiment.py"), "--input", str(source),
                        "--revision", "3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7", "--retry-failed"], check=False)
                    statuses = read_rows(ROOT / "data/processing_status.csv", STATUS_COLUMNS)
                    failed = any(row["status"] == "inference_failed" for row in statuses.values())
                    if result.returncode == 0 and not failed: previous = digest
                    else: print("Analysis run did not finish; retrying on the next check.", flush=True)
            except (OSError, ValueError):
                print("Source CSV is unavailable; retrying on the next check.", flush=True)
            if once: return
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.interval < 30: raise SystemExit("Use a polling interval of at least 30 seconds")
    (ROOT / "data").mkdir(parents=True, exist_ok=True)
    try: watch(args.input, args.interval, args.once)
    except Timeout: raise SystemExit("Another local sentiment monitor is already running")
    except KeyboardInterrupt: print("Local sentiment monitor stopped; saved predictions are preserved.")
