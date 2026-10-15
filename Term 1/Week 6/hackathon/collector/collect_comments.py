import os
import csv
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from googleapiclient.discovery import build

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DATA.mkdir(parents=True, exist_ok=True)

COMMENTS_FILE = DATA / "youtube_comments.csv"
LOG_FILE = DATA / "collection_log.csv"
START_FILE = DATA / "monitoring_started.txt"
VIDEOS_FILE = Path(__file__).resolve().parent / "video_ids.csv"

COLUMNS = [
    "comment_id",
    "video_id",
    "text",
    "published_at",
    "collected_at"
]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def main():
    api_key = os.environ["YOUTUBE_API_KEY"]
    youtube = build(
        "youtube", "v3",
        developerKey=api_key
    )

    now = utc_now()

    # Save start time only once
    if START_FILE.exists():
        started = pd.Timestamp(
            START_FILE.read_text().strip()
        )
    else:
        started = pd.Timestamp(now)
        START_FILE.write_text(now)

    # Read selected videos
    video_ids = (
        pd.read_csv(VIDEOS_FILE)["video_id"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()[:20]
    )

    if not video_ids:
        raise ValueError("No video IDs found")

    # Load existing dataset
    if COMMENTS_FILE.exists():
        old = pd.read_csv(
            COMMENTS_FILE, dtype=str
        )
    else:
        old = pd.DataFrame(columns=COLUMNS)

    for column in COLUMNS:
        if column not in old.columns:
            old[column] = pd.NA

    known = set(
        old["comment_id"].dropna()
    )

    new_rows = []
    successful = 0
    failed = 0

    for video_id in video_ids:
        try:
            page_token = None

            # Check up to 3 pages per video
            for page in range(3):
                params = {
                    "part": "snippet",
                    "videoId": video_id,
                    "maxResults": 100,
                    "order": "time",
                    "textFormat": "plainText"
                }

                if page_token:
                    params["pageToken"] = page_token

                response = (
                    youtube.commentThreads()
                    .list(**params)
                    .execute()
                )

                for item in response.get("items", []):
                    comment = item["snippet"][
                        "topLevelComment"
                    ]

                    comment_id = comment["id"]

                    if comment_id in known:
                        continue

                    known.add(comment_id)

                    new_rows.append({
                        "comment_id": comment_id,
                        "video_id": video_id,
                        "text": comment["snippet"][
                            "textDisplay"
                        ],
                        "published_at": comment["snippet"][
                            "publishedAt"
                        ],
                        "collected_at": now
                    })

                page_token = response.get(
                    "nextPageToken"
                )

                if not page_token:
                    break

            successful += 1

        except Exception as error:
            failed += 1
            print(f"Error for {video_id}: {error}")

    if successful == 0:
        raise RuntimeError(
            "All YouTube requests failed"
        )

    new = pd.DataFrame(
        new_rows, columns=COLUMNS
    )

    combined = pd.concat(
        [old, new],
        ignore_index=True
    ).drop_duplicates(
        subset="comment_id",
        keep="first"
    )

    combined.to_csv(
        COMMENTS_FILE, index=False
    )

    # Count comments published after start
    published = pd.to_datetime(
        combined["published_at"],
        utc=True,
        errors="coerce"
    )

    collected = pd.to_datetime(
        combined["collected_at"],
        utc=True,
        errors="coerce"
    )

    live = (
        (published >= started)
        & (collected >= started)
    ).sum()

    # Append monitoring log
    with LOG_FILE.open(
        "a", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow([
                "checked_at",
                "successful_videos",
                "failed_videos",
                "new_items",
                "total_items",
                "live_items"
            ])

        writer.writerow([
            now,
            successful,
            failed,
            len(new),
            len(combined),
            int(live)
        ])

    print("Monitoring started:", started)
    print("Last check:", now)
    print("Videos checked:", successful)
    print("Failed videos:", failed)
    print("New comments:", len(new))
    print("Total comments:", len(combined))
    print("Live-period comments:", live)

if __name__ == "__main__":
    main()
